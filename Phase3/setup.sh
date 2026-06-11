#!/bin/bash

# Setup script for Phase 3 - Twilio Integration

set -e

echo "🚛 Setting up Phase 3: Twilio Phone Integration..."

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

# Create necessary directories
mkdir -p data credentials

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env with your API keys:"
    echo "   Phase 1-2 keys:"
    echo "   - LIVEKIT_API_KEY & LIVEKIT_API_SECRET"
    echo "   - DEEPGRAM_API_KEY"
    echo "   - ELEVENLABS_API_KEY"
    echo "   - OPENAI_API_KEY"
    echo ""
    echo "   NEW Phase 3 keys:"
    echo "   - TWILIO_ACCOUNT_SID"
    echo "   - TWILIO_AUTH_TOKEN"
    echo "   - TWILIO_PHONE_NUMBER"
    echo ""
    echo "📝 And add Google Calendar credentials:"
    echo "   - Place service account JSON in ./credentials/"
    echo ""
else
    echo "✅ .env file exists"
fi

# Check for Google Calendar credentials
if [ ! -f "credentials/google-calendar-service-account.json" ]; then
    echo ""
    echo "⚠️  Google Calendar credentials not found"
    echo "   Copy from Phase 2 or follow Google Calendar setup guide"
    echo ""
fi

echo ""
echo "🎉 Phase 3 setup complete!"
echo ""
echo "NEW in Phase 3:"
echo "  ✨ Real outbound phone calls via Twilio"
echo "  ✨ SMS confirmations and fallback"
echo "  ✨ Voicemail detection"
echo "  ✨ Call lifecycle management"
echo "  ✨ API server for call initiation"
echo ""
echo "Next steps:"
echo "  1. Sign up for Twilio: https://www.twilio.com/try-twilio"
echo "  2. Get a phone number with voice capabilities"
echo "  3. Edit .env with Twilio credentials"
echo "  4. Copy Google Calendar credentials from Phase 2"
echo "  5. Run API server: python -m api.server"
echo "  6. Run agent: python -m agent.main"
echo "  7. Test with real phone call!"
