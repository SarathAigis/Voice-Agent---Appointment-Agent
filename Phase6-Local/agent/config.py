"""Configuration for local voice agent."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LiveKit
    livekit_url: str = "ws://localhost:7880"
    livekit_api_key: str = "devkey"
    livekit_api_secret: str = "secret"

    # Local Whisper STT
    whisper_model: str = "base"  # tiny, base, small, medium, large
    whisper_device: str = "cpu"  # cpu or cuda

    # Local TTS (Coqui)
    tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC"
    tts_device: str = "cpu"

    # Local LLM (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # VAD Configuration
    vad_min_speech_duration: int = 250
    vad_silence_duration: int = 700
    vad_energy_threshold: float = 0.5

    # Appointment defaults
    default_appointment_duration_minutes: int = 30
    business_hours_start: int = 8
    business_hours_end: int = 18


# Global config instance
config = Config()
