"""Local Speech-to-Text using Whisper."""

import asyncio
import structlog
from typing import AsyncIterator
import numpy as np
from faster_whisper import WhisperModel

from .config import config

logger = structlog.get_logger(__name__)


class LocalWhisperSTT:
    """Local STT using faster-whisper."""

    def __init__(self):
        """Initialize Whisper model."""
        logger.info(
            "loading_whisper_model",
            model=config.whisper_model,
            device=config.whisper_device,
        )

        self.model = WhisperModel(
            config.whisper_model,
            device=config.whisper_device,
            compute_type="int8" if config.whisper_device == "cpu" else "float16",
        )

        logger.info("whisper_model_loaded")

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[str]:
        """
        Transcribe streaming audio.

        Args:
            audio_stream: Async iterator of audio bytes (16kHz, 16-bit PCM)

        Yields:
            Transcribed text segments
        """
        audio_buffer = []
        buffer_duration = 0  # seconds

        async for audio_chunk in audio_stream:
            # Convert bytes to numpy array
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            audio_float = audio_data.astype(np.float32) / 32768.0

            audio_buffer.append(audio_float)
            buffer_duration += len(audio_data) / 16000

            # Process when we have ~2 seconds of audio
            if buffer_duration >= 2.0:
                combined_audio = np.concatenate(audio_buffer)

                # Run transcription in thread pool (Whisper is blocking)
                segments, info = await asyncio.to_thread(
                    self.model.transcribe, combined_audio, language="en", beam_size=5
                )

                # Yield transcribed text
                for segment in segments:
                    text = segment.text.strip()
                    if text:
                        logger.info(
                            "transcription",
                            text=text,
                            confidence=segment.avg_logprob,
                        )
                        yield text

                # Reset buffer
                audio_buffer = []
                buffer_duration = 0

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe audio array synchronously.

        Args:
            audio: NumPy array of audio (16kHz, float32)

        Returns:
            Transcribed text
        """
        segments, info = self.model.transcribe(audio, language="en", beam_size=5)

        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())

        result = " ".join(text_parts).strip()

        logger.info(
            "transcription_complete",
            text=result,
            language=info.language,
            probability=info.language_probability,
        )

        return result
