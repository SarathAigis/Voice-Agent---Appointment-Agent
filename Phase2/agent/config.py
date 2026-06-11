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

    # LLM Configuration (Phase 2)
    openai_api_key: str
    llm_model: str = "gpt-4o"  # GPT-4o for Phase 2
    llm_temperature: float = 0.7
    llm_max_tokens: int = 500  # Keep responses concise for voice

    # Google Calendar (Phase 2)
    google_calendar_credentials_path: str = "./credentials/google-calendar-service-account.json"
    google_calendar_id: str = "primary"

    # Appointment defaults
    default_appointment_duration_minutes: int = 30
    business_hours_start: int = 8  # 8 AM
    business_hours_end: int = 18  # 6 PM

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
