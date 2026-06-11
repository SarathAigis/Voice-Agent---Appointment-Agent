# Local Voice Agent Setup - Zero API Costs

This version runs completely locally with no API dependencies (except optional Google Calendar).

## Prerequisites

- Python 3.11+
- Docker (for LiveKit)
- ~4GB free RAM
- ~2GB disk space (for models)

## Quick Start

### Step 1: Install Ollama (Local LLM)

**macOS:**
```bash
brew install ollama

# Start Ollama server
ollama serve

# In another terminal, pull the model
ollama pull llama3.1:8b
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.1:8b
```

**Verify:**
```bash
curl http://localhost:11434/api/tags
# Should show llama3.1:8b in the list
```

### Step 2: Start LiveKit Server

```bash
cd Phase6-Local

# Start LiveKit in Docker
docker-compose up -d

# Verify it's running
curl http://localhost:7880
```

### Step 3: Install Python Dependencies

```bash
cd Phase6-Local

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (this will take ~5 minutes)
pip install -r requirements.txt

# Download Whisper model (first time only)
python -c "import whisper; whisper.load_model('base')"

# Download TTS model (first time only)
python -c "from TTS.api import TTS; TTS('tts_models/en/ljspeech/tacotron2-DDC')"
```

### Step 4: Configure Environment

```bash
# Create .env file
cp .env.example .env

# No need to edit - defaults work for local setup!
# But you can customize model sizes:
# - WHISPER_MODEL=tiny|base|small|medium|large
# - OLLAMA_MODEL=llama3.1:8b|llama3.1:70b|mistral
```

### Step 5: Run the Agent

```bash
# Activate environment
source venv/bin/activate

# Run the voice agent
python -m agent.main
```

You should see:
```
INFO     whisper_model_loaded
INFO     tts_model_loaded
INFO     ollama_client_initialized
INFO     agent_started
```

### Step 6: Test It!

Open LiveKit Agents Playground:
https://agents-playground.livekit.io

**Connect with:**
- URL: `ws://localhost:7880`
- API Key: `devkey`
- API Secret: `secret`

**Allow microphone access** and start talking!

Try:
- "Hi, I need to schedule a delivery"
- "What times are available on Thursday?"
- "Can I book 2pm?"

---

## Model Selection Guide

### Whisper Models (STT)

| Model | Size | Speed | Quality | RAM |
|-------|------|-------|---------|-----|
| tiny | 39MB | Very fast | Poor | 1GB |
| base | 74MB | Fast | Good | 1GB |
| small | 244MB | Medium | Better | 2GB |
| medium | 769MB | Slow | Great | 5GB |
| large | 1.5GB | Very slow | Best | 10GB |

**Recommendation:** `base` for development, `small` for production

### Ollama Models (LLM)

| Model | Size | Speed | Quality | RAM |
|-------|------|-------|---------|-----|
| llama3.1:8b | 4.7GB | Fast | Good | 8GB |
| mistral:7b | 4.1GB | Fast | Good | 8GB |
| phi3:mini | 2.3GB | Very fast | OK | 4GB |
| llama3.1:70b | 40GB | Slow | Excellent | 64GB |

**Recommendation:** `llama3.1:8b` for most use cases

### TTS Models (Coqui)

Default model works well. For faster synthesis:
```python
TTS_MODEL=tts_models/en/ljspeech/fast_pitch
```

---

## Performance Expectations

**On a typical laptop (M1 Mac / i7 + 16GB RAM):**

| Component | Latency |
|-----------|---------|
| VAD | ~10ms |
| Whisper (base) | ~300ms |
| Ollama (llama3.1:8b) | ~500-800ms |
| Coqui TTS | ~400ms |
| **Total** | **~1.2-1.5s** |

**Not as fast as cloud** (cloud is ~800ms), but acceptable for testing!

---

## Cost Comparison

| Setup | Cost per Call | Quality |
|-------|--------------|---------|
| **Phase6-Local** | $0.00 | Good |
| Phase6 Cloud | $0.10 | Excellent |

**Local is free but:**
- Slower (1.5s vs 0.8s latency)
- Needs powerful hardware
- Voice quality is decent but not as natural

---

## Troubleshooting

### "Whisper model not found"
```bash
python -c "import whisper; whisper.load_model('base')"
```

### "Connection refused to Ollama"
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### "LiveKit connection failed"
```bash
# Check Docker container
docker ps | grep livekit

# Restart if needed
docker-compose restart
```

### "Out of memory" error
- Use smaller models: `WHISPER_MODEL=tiny`, `OLLAMA_MODEL=phi3:mini`
- Close other applications
- Increase Docker memory limit

### Slow response times
- Use smaller Whisper model (`tiny` or `base`)
- Use faster Ollama model (`phi3:mini` or `mistral:7b`)
- Add GPU support if available:
  ```bash
  # In .env
  WHISPER_DEVICE=cuda
  TTS_DEVICE=cuda
  ```

### Poor transcription quality
- Increase Whisper model size (`small` or `medium`)
- Adjust VAD thresholds in .env:
  ```bash
  VAD_ENERGY_THRESHOLD=0.6  # Less sensitive
  VAD_SILENCE_DURATION=900   # Wait longer
  ```

---

## Upgrading to Cloud (When Ready)

When you're ready to move to production with better quality/speed:

1. Keep Phase6-Local for development
2. Use Phase6 for production with cloud APIs
3. Best of both worlds: develop locally, deploy to cloud

---

## Next Steps

1. **Test the basic pipeline** - Verify audio flows correctly
2. **Tune for noise** - Play truck cabin sounds while testing
3. **Add appointment logic** - Connect to your actual scheduling system
4. **Benchmark latency** - Measure each component
5. **Optimize models** - Find the right quality/speed balance
6. **Add phone calls** - When ready, add Twilio for real calls

---

## Hardware Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Disk: 10GB free

**Recommended:**
- CPU: 8+ cores
- RAM: 16GB
- Disk: 20GB
- GPU: Optional but speeds up 10x

---

**Everything runs on your laptop. Zero API costs. Full privacy.** 🚀

See `QUICKSTART-LOCAL.md` for a step-by-step walkthrough of your first local test.
