"""Policy document indexer for RAG system."""

import structlog
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI

from ..config import config

logger = structlog.get_logger(__name__)


class PolicyIndexer:
    """Indexes policy documents into vector database for retrieval."""

    def __init__(self):
        """Initialize the policy indexer."""
        self.openai_client = OpenAI(api_key=config.openai_api_key)

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=config.vector_db_path,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="scheduling_policies",
            metadata={"description": "Scheduling policies and procedures"}
        )

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            List of embedding floats
        """
        try:
            response = self.openai_client.embeddings.create(
                model=config.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("embedding_failed", error=str(e))
            raise

    def chunk_document(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split document into overlapping chunks.

        Args:
            text: Document text
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)

                if break_point > chunk_size // 2:
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def index_document(self, file_path: Path, document_id: str = None) -> int:
        """
        Index a single policy document.

        Args:
            file_path: Path to document file
            document_id: Optional document ID (uses filename if not provided)

        Returns:
            Number of chunks indexed
        """
        if document_id is None:
            document_id = file_path.stem

        logger.info("indexing_document", file=file_path.name, doc_id=document_id)

        try:
            # Read document
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Chunk document
            chunks = self.chunk_document(content)

            # Generate embeddings and add to collection
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                embedding = self.embed_text(chunk)

                self.collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        "document_id": document_id,
                        "chunk_index": i,
                        "source_file": file_path.name,
                    }]
                )

            logger.info(
                "document_indexed",
                doc_id=document_id,
                chunks=len(chunks)
            )

            return len(chunks)

        except Exception as e:
            logger.error("indexing_failed", file=file_path.name, error=str(e))
            raise

    def index_directory(self, directory_path: Path) -> Dict[str, int]:
        """
        Index all policy documents in a directory.

        Args:
            directory_path: Path to directory containing policy files

        Returns:
            Dictionary mapping document IDs to chunk counts
        """
        logger.info("indexing_directory", path=str(directory_path))

        results = {}

        # Find all markdown files
        for file_path in directory_path.glob("*.md"):
            try:
                num_chunks = self.index_document(file_path)
                results[file_path.stem] = num_chunks
            except Exception as e:
                logger.error("document_indexing_failed", file=file_path.name, error=str(e))

        total_chunks = sum(results.values())
        logger.info(
            "directory_indexed",
            documents=len(results),
            total_chunks=total_chunks
        )

        return results

    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            self.chroma_client.delete_collection("scheduling_policies")
            self.collection = self.chroma_client.create_collection(
                name="scheduling_policies",
                metadata={"description": "Scheduling policies and procedures"}
            )
            logger.info("collection_cleared")
        except Exception as e:
            logger.error("clear_failed", error=str(e))

    def get_collection_stats(self) -> Dict:
        """Get statistics about the indexed collection."""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name,
        }


def initialize_rag_system(policies_dir: Path = None) -> PolicyIndexer:
    """
    Initialize RAG system by indexing policy documents.

    Args:
        policies_dir: Path to policies directory (defaults to ./data/policies)

    Returns:
        Initialized PolicyIndexer
    """
    if policies_dir is None:
        policies_dir = Path("./data/policies")

    indexer = PolicyIndexer()

    if policies_dir.exists():
        logger.info("initializing_rag_system", policies_dir=str(policies_dir))
        indexer.index_directory(policies_dir)
    else:
        logger.warning("policies_directory_not_found", path=str(policies_dir))

    return indexer
