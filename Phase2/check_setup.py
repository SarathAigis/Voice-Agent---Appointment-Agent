#!/usr/bin/env python3
"""Setup verification script for Phase 2."""

import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists and has required keys."""
    env_path = Path(".env")
    if not env_path.exists():
        return False, ".env file not found. Copy from .env.example and fill in your API keys."

    required_keys = [
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "DEEPGRAM_API_KEY",
        "ELEVENLABS_API_KEY",
        "OPENAI_API_KEY",  # New for Phase 2
    ]

    env_content = env_path.read_text()
    missing = []

    for key in required_keys:
        if key not in env_content or f"{key}=your_" in env_content:
            missing.append(key)

    if missing:
        return False, f"Missing or placeholder values for: {', '.join(missing)}"

    return True, "All required keys present"


def check_python_version():
    """Check Python version is 3.11+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        return (
            False,
            f"Python 3.11+ required. You have {version.major}.{version.minor}.{version.micro}",
        )
    return True, f"Python {version.major}.{version.minor}.{version.micro}"


def check_dependencies():
    """Check if key dependencies are installed."""
    try:
        import livekit  # noqa
        import deepgram  # noqa
        import elevenlabs  # noqa
        import openai  # noqa
        import structlog  # noqa
        from google.oauth2 import service_account  # noqa

        return True, "Core dependencies installed"
    except ImportError as e:
        return False, f"Missing dependencies: {e}. Run: pip install -r requirements.txt"


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
        return (
            False,
            "Google Calendar credentials not found. See GOOGLE_CALENDAR_SETUP.md",
        )

    # Try to parse JSON
    try:
        import json

        with open(creds_path) as f:
            data = json.load(f)

        if data.get("type") != "service_account":
            return False, "Credentials file is not a service account key"

        return True, f"Found service account: {data.get('client_email', 'unknown')}"

    except json.JSONDecodeError:
        return False, "Credentials file is not valid JSON"
    except Exception as e:
        return False, f"Error reading credentials: {e}"


def main():
    """Run all checks."""
    print("🚛 Appointment Agent Phase 2 - Setup Check\n")

    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Google Calendar Credentials", check_calendar_credentials),
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
        print("🎉 All checks passed! Phase 2 ready to run:")
        print("   python -m agent.main")
        print()
        print("Test at: https://agents-playground.livekit.io")
        print()
        print("New in Phase 2:")
        print("  ✨ GPT-4o conversational agent")
        print("  ✨ Google Calendar integration")
        print("  ✨ Real appointment scheduling")
        return 0
    else:
        print("⚠️  Setup incomplete. Fix the issues above and try again.")
        print()
        print("For Google Calendar setup, see:")
        print("  📖 GOOGLE_CALENDAR_SETUP.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
