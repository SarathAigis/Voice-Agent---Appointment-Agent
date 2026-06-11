#!/bin/bash

# Setup script for Phase 2 - Appointment Agent with GPT-4o

set -e

echo "🚛 Setting up Phase 2: LLM Integration + Google Calendar..."

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

# Create credentials directory
if [ ! -d "credentials" ]; then
    echo "Creating credentials directory..."
    mkdir credentials
    echo "✅ Credentials directory created"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env with your API keys:"
    echo "   - LIVEKIT_API_KEY & LIVEKIT_API_SECRET"
    echo "   - DEEPGRAM_API_KEY"
    echo "   - ELEVENLABS_API_KEY"
    echo "   - OPENAI_API_KEY (NEW for Phase 2)"
    echo ""
    echo "📝 And add Google Calendar credentials:"
    echo "   - Place service account JSON in ./credentials/"
    echo "   - Update GOOGLE_CALENDAR_CREDENTIALS_PATH in .env"
    echo ""
else
    echo "✅ .env file exists"
fi

# Check for Google Calendar credentials
if [ ! -f "credentials/google-calendar-service-account.json" ]; then
    echo ""
    echo "⚠️  Google Calendar credentials not found"
    echo "📝 To set up Google Calendar:"
    echo "   1. Go to https://console.cloud.google.com"
    echo "   2. Create a new project (or select existing)"
    echo "   3. Enable Google Calendar API"
    echo "   4. Create a Service Account"
    echo "   5. Download JSON key and save as:"
    echo "      ./credentials/google-calendar-service-account.json"
    echo ""
else
    echo "✅ Google Calendar credentials found"
fi

echo ""
echo "🎉 Phase 2 setup complete!"
echo ""
echo "New features in Phase 2:"
echo "  ✨ GPT-4o conversational agent"
echo "  ✨ Google Calendar integration"
echo "  ✨ Real appointment scheduling"
echo "  ✨ Multi-turn conversations"
echo ""
echo "Next steps:"
echo "  1. Edit .env with API keys (including OPENAI_API_KEY)"
echo "  2. Add Google Calendar credentials"
echo "  3. Activate virtualenv: source venv/bin/activate"
echo "  4. Run agent: python -m agent.main"
echo "  5. Test at: https://agents-playground.livekit.io"
