"""Policy retrieval for answering questions."""

import structlog
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI

from ..config import config

logger = structlog.get_logger(__name__)


class PolicyRetriever:
    """Retrieves relevant policy information based on queries."""

    def __init__(self):
        """Initialize the policy retriever."""
        self.openai_client = OpenAI(api_key=config.openai_api_key)

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=config.vector_db_path,
            settings=Settings(anonymized_telemetry=False)
        )

        try:
            self.collection = self.chroma_client.get_collection("scheduling_policies")
        except Exception:
            logger.warning("policy_collection_not_found")
            # Create empty collection
            self.collection = self.chroma_client.create_collection(
                name="scheduling_policies",
                metadata={"description": "Scheduling policies and procedures"}
            )

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for search query.

        Args:
            query: Search query text

        Returns:
            Query embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model=config.embedding_model,
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("query_embedding_failed", error=str(e))
            raise

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Dict]:
        """
        Retrieve relevant policy chunks for a query.

        Args:
            query: Search query
            top_k: Number of results to return (defaults to config)
            similarity_threshold: Minimum similarity score (defaults to config)

        Returns:
            List of result dictionaries with 'text', 'score', and 'metadata'
        """
        if top_k is None:
            top_k = config.rag_top_k

        if similarity_threshold is None:
            similarity_threshold = config.rag_similarity_threshold

        logger.info("retrieving_policies", query=query, top_k=top_k)

        try:
            # Generate query embedding
            query_embedding = self.embed_query(query)

            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

            # Format results
            formatted_results = []

            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    # ChromaDB returns distances, convert to similarity
                    distance = results['distances'][0][i]
                    similarity = 1 - distance  # Cosine similarity

                    if similarity >= similarity_threshold:
                        formatted_results.append({
                            'text': doc,
                            'score': similarity,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        })

            logger.info(
                "policies_retrieved",
                query=query,
                results=len(formatted_results)
            )

            return formatted_results

        except Exception as e:
            logger.error("retrieval_failed", query=query, error=str(e))
            return []

    def format_context(self, results: List[Dict], max_length: int = 1500) -> str:
        """
        Format retrieval results into context string for LLM.

        Args:
            results: List of retrieval results
            max_length: Maximum context length in characters

        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant policy information found."

        context_parts = []
        current_length = 0

        for i, result in enumerate(results, 1):
            text = result['text'].strip()
            source = result['metadata'].get('source_file', 'unknown')
            score = result['score']

            part = f"[Policy {i} - {source} (relevance: {score:.2f})]:\n{text}\n"

            if current_length + len(part) > max_length:
                break

            context_parts.append(part)
            current_length += len(part)

        context = "\n".join(context_parts)

        return f"Relevant policy information:\n\n{context}"


# Global retriever instance
_retriever = None


def get_retriever() -> PolicyRetriever:
    """Get or create the global policy retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = PolicyRetriever()
    return _retriever


def query_policies(query: str, top_k: int = 3) -> str:
    """
    Query policies and return formatted context.

    This is the main function exposed to the LLM agent.

    Args:
        query: Question about policies
        top_k: Number of results

    Returns:
        Formatted context string
    """
    retriever = get_retriever()
    results = retriever.retrieve(query, top_k=top_k)
    return retriever.format_context(results)
