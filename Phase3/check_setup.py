#!/usr/bin/env python3
"""Setup verification script for Phase 3."""

import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists and has required keys."""
    env_path = Path(".env")
    if not env_path.exists():
        return False, ".env file not found"

    required_keys = [
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "DEEPGRAM_API_KEY",
        "ELEVENLABS_API_KEY",
        "OPENAI_API_KEY",
        "TWILIO_ACCOUNT_SID",  # New for Phase 3
        "TWILIO_AUTH_TOKEN",  # New for Phase 3
        "TWILIO_PHONE_NUMBER",  # New for Phase 3
    ]

    env_content = env_path.read_text()
    missing = []

    for key in required_keys:
        if key not in env_content or f"{key}=your_" in env_content:
            missing.append(key)

    if missing:
        return False, f"Missing or placeholder: {', '.join(missing)}"

    return True, "All required keys present"


def check_python_version():
    """Check Python version is 3.11+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        return False, f"Python 3.11+ required. You have {version.major}.{version.minor}"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"


def check_dependencies():
    """Check if key dependencies are installed."""
    try:
        import livekit  # noqa
        import deepgram  # noqa
        import elevenlabs  # noqa
        import openai  # noqa
        import twilio  # noqa
        import fastapi  # noqa
        from google.oauth2 import service_account  # noqa

        return True, "Core dependencies installed"
    except ImportError as e:
        return False, f"Missing: {e}. Run: pip install -r requirements.txt"


def check_config():
    """Try to load config."""
    try:
        from agent.config import config  # noqa

        return True, "Configuration loads successfully"
    except Exception as e:
        return False, f"Config error: {e}"


def check_calendar_credentials():
    """Check if Google Calendar credentials exist."""
    creds_path = Path("credentials/google-calendar-service-account.json")

    if not creds_path.exists():
        return False, "Google Calendar credentials not found"

    try:
        import json

        with open(creds_path) as f:
            data = json.load(f)

        if data.get("type") != "service_account":
            return False, "Not a service account key"

        return True, f"Service account: {data.get('client_email', 'unknown')}"

    except Exception as e:
        return False, f"Error: {e}"


def check_twilio():
    """Check Twilio configuration."""
    try:
        from agent.config import config
        from twilio.rest import Client

        if not config.twilio_account_sid or "your_" in config.twilio_account_sid:
            return False, "Twilio Account SID not configured"

        if not config.twilio_auth_token or "your_" in config.twilio_auth_token:
            return False, "Twilio Auth Token not configured"

        # Try to initialize client (won't make API call)
        client = Client(config.twilio_account_sid, config.twilio_auth_token)

        return True, f"Twilio configured (SID: {config.twilio_account_sid[:10]}...)"

    except Exception as e:
        return False, f"Twilio error: {e}"


def main():
    """Run all checks."""
    print("🚛 Phase 3: Twilio Integration - Setup Check\n")

    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Google Calendar", check_calendar_credentials),
        ("Twilio Setup", check_twilio),
    ]

    all_passed = True

    for name, check_func in checks:
        passed, message = check_func()
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {message}")

        if not passed:
            all_passed = False

    print()

    if all_passed:
        print("🎉 All checks passed! Phase 3 ready to run:")
        print()
        print("Start services:")
        print("  Terminal 1: python -m api.server")
        print("  Terminal 2: python -m agent.main")
        print()
        print("Test call:")
        print('  curl -X POST http://localhost:8000/api/calls/initiate \\')
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"driver_id":"TEST","driver_name":"Test",')
        print('         "driver_phone":"+1234567890","truck_number":"T-1",')
        print('         "call_purpose":"test"}\'')
        print()
        print("NEW in Phase 3:")
        print("  ✨ Real outbound phone calls")
        print("  ✨ SMS confirmations")
        print("  ✨ Voicemail detection")
        return 0
    else:
        print("⚠️  Setup incomplete. Fix issues above.")
        print()
        print("For Twilio setup: See TWILIO_SETUP.md")
        print("For Google Calendar: See ../Phase2/GOOGLE_CALENDAR_SETUP.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
