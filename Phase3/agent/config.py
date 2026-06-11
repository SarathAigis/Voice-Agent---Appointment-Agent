"""Configuration management for Phase 3 voice agent."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # LiveKit
    livekit_url: str = "wss://localhost:7880"
    livekit_api_key: str
    livekit_api_secret: str

    # Deepgram STT
    deepgram_api_key: str

    # ElevenLabs TTS
    elevenlabs_api_key: str

    # VAD Configuration
    vad_min_speech_duration: int = 250
    vad_silence_duration: int = 700
    vad_energy_threshold: float = 0.5

    # STT Configuration
    deepgram_model: str = "nova-2"
    deepgram_language: str = "en"
    deepgram_smart_format: bool = True
    deepgram_interim_results: bool = True
    deepgram_endpointing: int = 500
    deepgram_utterance_end_ms: int = 1500

    # TTS Configuration
    elevenlabs_model: str = "eleven_turbo_v2"
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_stability: float = 0.5
    elevenlabs_similarity_boost: float = 0.75

    # LLM Configuration
    openai_api_key: str
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 500

    # Google Calendar
    google_calendar_credentials_path: str = "./credentials/google-calendar-service-account.json"
    google_calendar_id: str = "primary"

    # Appointment defaults
    default_appointment_duration_minutes: int = 30
    business_hours_start: int = 8
    business_hours_end: int = 18

    # Twilio Configuration (Phase 3)
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # Twilio SIP
    twilio_sip_domain: str | None = None
    twilio_sip_username: str | None = None
    twilio_sip_password: str | None = None

    # SMS Configuration
    twilio_enable_sms: bool = True
    sms_from_number: str | None = None

    # Call Configuration
    enable_voicemail_detection: bool = True
    voicemail_message: str = "Hi, this is the scheduling assistant. Please call us back at your convenience or check your text messages."
    max_call_duration_seconds: int = 300
    call_timeout_seconds: int = 30

    # API Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-this-in-production"

    # Database
    database_url: str = "sqlite:///./data/appointments.db"

    # Langfuse (Phase 5+)
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"


# Global config instance
config = Config()
