"""Configuration management for the voice agent."""

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
    livekit_api_key: str
    livekit_api_secret: str

    # Deepgram STT
    deepgram_api_key: str

    # ElevenLabs TTS
    elevenlabs_api_key: str

    # VAD Configuration (Silero)
    vad_min_speech_duration: int = 250  # ms
    vad_silence_duration: int = 700  # ms - tuned for noisy environments
    vad_energy_threshold: float = 0.5  # 0.0-1.0, higher = less sensitive

    # STT Configuration (Deepgram)
    deepgram_model: str = "nova-2"
    deepgram_language: str = "en"
    deepgram_smart_format: bool = True
    deepgram_interim_results: bool = True
    deepgram_endpointing: int = 500  # ms
    deepgram_utterance_end_ms: int = 1500  # ms

    # TTS Configuration (ElevenLabs)
    elevenlabs_model: str = "eleven_turbo_v2"
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional female
    elevenlabs_stability: float = 0.5
    elevenlabs_similarity_boost: float = 0.75

    # LLM Configuration (Phase 2+)
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    llm_provider: str = "anthropic"  # anthropic or openai
    llm_model: str = "claude-sonnet-4-20250514"  # or gpt-4o

    # Google Calendar (Phase 2+)
    google_calendar_credentials_path: str = "./credentials/google-calendar-service-account.json"

    # Twilio (Phase 3+)
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None

    # Langfuse (Phase 5+)
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    # Database (Phase 4+)
    database_url: str | None = None


# Global config instance
config = Config()
