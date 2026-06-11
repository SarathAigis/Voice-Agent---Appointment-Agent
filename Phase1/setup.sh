#!/bin/bash

# Setup script for Appointment Agent

set -e

echo "🚛 Setting up Appointment Scheduling Voice Agent..."

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

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env with your API keys:"
    echo "   - LIVEKIT_API_KEY & LIVEKIT_API_SECRET"
    echo "   - DEEPGRAM_API_KEY"
    echo "   - ELEVENLABS_API_KEY"
    echo ""
    echo "Then run: source venv/bin/activate && python -m agent.main"
else
    echo "✅ .env file exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Activate virtualenv: source venv/bin/activate"
echo "  3. Run agent: python -m agent.main"
echo "  4. Test at: https://agents-playground.livekit.io"
