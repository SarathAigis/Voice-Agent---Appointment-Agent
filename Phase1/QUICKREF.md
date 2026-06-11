# Quick Reference Card

## 🚀 Commands

```bash
# Setup
./setup.sh

# Verify setup
python check_setup.py

# Run agent
source venv/bin/activate
python -m agent.main

# Run tests
pytest

# Format code
black agent/
ruff check agent/
```

## 🔑 API Keys Needed (Phase 1)

| Service | Purpose | Sign Up | Free Tier |
|---------|---------|---------|-----------|
| LiveKit | Audio transport | [cloud.livekit.io](https://cloud.livekit.io) | ✅ Yes |
| Deepgram | Speech-to-Text | [console.deepgram.com](https://console.deepgram.com) | 12K min/mo |
| ElevenLabs | Text-to-Speech | [elevenlabs.io](https://elevenlabs.io) | 10K chars/mo |

## 📁 Project Structure

```
appointment-agent/
├── agent/
│   ├── main.py              # Entrypoint
│   ├── pipeline.py          # Voice pipeline (VAD → STT → LLM → TTS)
│   ├── config.py            # Configuration & settings
│   └── tools/               # Tool calling (Phase 2+)
├── tests/                   # Unit tests
├── .env                     # Your API keys (create from .env.example)
├── requirements.txt         # Python dependencies
├── setup.sh                 # Setup automation
├── check_setup.py           # Verify installation
├── GETTING_STARTED.md       # Detailed setup guide
└── PHASE1.md               # Phase 1 testing guide
```

## 🧪 Testing URL

[LiveKit Agents Playground](https://agents-playground.livekit.io)

## 🎯 Phase 1 Validation

- [ ] Agent connects to LiveKit
- [ ] Greeting plays via TTS
- [ ] Clear speech transcribed (>95%)
- [ ] Noisy speech transcribed (>80%)
- [ ] Response latency <1.5s
- [ ] Barge-in/interruption works
- [ ] No false triggers from noise

## ⚙️ Key Configuration

**File**: `agent/config.py`

```python
# Tune for noisy environments
vad_silence_duration: int = 700  # ms
vad_energy_threshold: float = 0.5

# Deepgram model
deepgram_model: str = "nova-2"

# ElevenLabs model
elevenlabs_model: str = "eleven_turbo_v2"
```

## 🔍 Debugging

```bash
# Verbose logging
LIVEKIT_LOG_LEVEL=debug python -m agent.main

# Check config loads
python -c "from agent.config import config; print(config.livekit_url)"

# Test imports
python -c "import livekit; import deepgram; import elevenlabs; print('OK')"
```

## 📊 What's Working (Phase 1)

✅ LiveKit room connection  
✅ Silero VAD (voice activity detection)  
✅ Deepgram STT (speech-to-text)  
✅ ElevenLabs TTS (text-to-speech)  
✅ Simple echo/response logic  
✅ Barge-in support  
✅ Noise-tuned VAD settings  

## 🔜 Coming Next (Phase 2)

- Claude/GPT-4o LLM integration
- Google Calendar tool calling
- Real appointment scheduling
- Multi-turn conversations

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check `LIVEKIT_URL` in `.env` |
| Invalid credentials | Verify API keys, no extra spaces |
| Poor transcription | Adjust VAD threshold in `config.py` |
| High latency | Use closer LiveKit region |
| False triggers | Increase `vad_energy_threshold` |

## 📚 Documentation

- [README.md](./README.md) - Project overview
- [GETTING_STARTED.md](./GETTING_STARTED.md) - Setup walkthrough
- [PHASE1.md](./PHASE1.md) - Phase 1 testing guide
- [tactical-design.md](./tactical-design.md) - Full implementation plan
- [plan.md](./plan.md) - Scope document

---

**Current Phase**: 1 of 6 (Voice Pipeline)  
**Next Milestone**: LLM Integration + Google Calendar
