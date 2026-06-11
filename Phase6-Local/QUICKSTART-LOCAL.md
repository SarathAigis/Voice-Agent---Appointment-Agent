# Quick Start - Local Voice Agent (5 Minutes)

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python3 --version

# Check Docker
docker --version

# Check free RAM
free -h  # Linux
vm_stat | grep free  # macOS
```

## 1. Install Ollama (1 minute)

```bash
# macOS
brew install ollama

# Linux  
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve &

# Pull model (wait ~2 minutes for download)
ollama pull llama3.1:8b
```

## 2. Start LiveKit (30 seconds)

```bash
cd Phase6-Local
docker-compose up -d

# Verify
docker ps | grep livekit
```

## 3. Install Dependencies (3 minutes)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Test It! (30 seconds)

```bash
python -m agent.main
```

Open: https://agents-playground.livekit.io

Connect with:
- URL: `ws://localhost:7880`
- Key: `devkey`  
- Secret: `secret`

**Talk to it!** 🎤

## Troubleshooting

### "Ollama not found"
```bash
# Check it's running
curl http://localhost:11434/api/tags
```

### "Port 7880 in use"
```bash
# Kill any existing LiveKit
docker-compose down
docker-compose up -d
```

### "Out of memory"
Use smaller models in `.env`:
```
WHISPER_MODEL=tiny
OLLAMA_MODEL=phi3:mini
```

**Total cost: $0** ✅
