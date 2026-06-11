"""Tests for configuration management."""

import pytest
from agent.config import Config


def test_config_defaults():
    """Test that configuration has sensible defaults."""
    # These will use defaults from config.py since we don't have a real .env in tests
    assert Config.model_config["env_file"] == ".env"


def test_vad_thresholds():
    """Test VAD configuration for noisy environments."""
    config = Config(
        livekit_api_key="test",
        livekit_api_secret="test",
        deepgram_api_key="test",
        elevenlabs_api_key="test",
    )

    # Tuned for truck cabin noise
    assert config.vad_silence_duration == 700  # ms
    assert config.vad_energy_threshold == 0.5
    assert config.vad_min_speech_duration == 250  # ms


def test_deepgram_settings():
    """Test Deepgram STT configuration."""
    config = Config(
        livekit_api_key="test",
        livekit_api_secret="test",
        deepgram_api_key="test",
        elevenlabs_api_key="test",
    )

    assert config.deepgram_model == "nova-2"
    assert config.deepgram_language == "en"
    assert config.deepgram_smart_format is True
    assert config.deepgram_interim_results is True


def test_elevenlabs_settings():
    """Test ElevenLabs TTS configuration."""
    config = Config(
        livekit_api_key="test",
        livekit_api_secret="test",
        deepgram_api_key="test",
        elevenlabs_api_key="test",
    )

    assert config.elevenlabs_model == "eleven_turbo_v2"
    assert 0.0 <= config.elevenlabs_stability <= 1.0
    assert 0.0 <= config.elevenlabs_similarity_boost <= 1.0
