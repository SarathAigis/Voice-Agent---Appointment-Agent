"""Local Text-to-Speech using Coqui TTS."""

import asyncio
import structlog
import numpy as np
from TTS.api import TTS

from .config import config

logger = structlog.get_logger(__name__)


class LocalTTS:
    """Local TTS using Coqui TTS."""

    def __init__(self):
        """Initialize Coqui TTS model."""
        logger.info(
            "loading_tts_model",
            model=config.tts_model,
            device=config.tts_device,
        )

        self.tts = TTS(config.tts_model).to(config.tts_device)

        logger.info("tts_model_loaded")

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize

        Returns:
            Audio bytes (16kHz, 16-bit PCM)
        """
        logger.info("synthesizing_speech", text=text, chars=len(text))

        # Run TTS in thread pool (blocking operation)
        wav = await asyncio.to_thread(self.tts.tts, text)

        # Convert to numpy array if not already
        if not isinstance(wav, np.ndarray):
            wav = np.array(wav)

        # Convert float [-1, 1] to int16
        audio_int16 = (wav * 32767).astype(np.int16)

        # Convert to bytes
        audio_bytes = audio_int16.tobytes()

        logger.info(
            "speech_synthesized",
            duration_samples=len(audio_int16),
            duration_seconds=len(audio_int16) / 22050,  # Coqui default is 22kHz
        )

        return audio_bytes

    async def synthesize_stream(self, text: str):
        """
        Synthesize speech with streaming output.

        Args:
            text: Text to synthesize

        Yields:
            Audio chunks as bytes
        """
        # For POC, Coqui doesn't support streaming well
        # So we generate full audio and chunk it
        audio_bytes = await self.synthesize(text)

        # Chunk into ~100ms pieces for "streaming"
        chunk_size = 16000 * 2 // 10  # 100ms at 16kHz, 16-bit

        for i in range(0, len(audio_bytes), chunk_size):
            yield audio_bytes[i : i + chunk_size]
            await asyncio.sleep(0.01)  # Small delay for natural streaming
