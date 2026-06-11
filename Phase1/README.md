# Voice Agent for Truck Driver Appointment Scheduling

A voice-first AI agent designed for truck drivers to manage appointments (delivery slots, maintenance, compliance) via natural phone conversations. Built to handle high-noise environments (road, engine, CB radio).

## Project Status

**Current Phase:** Phase 1 - Basic Voice Pipeline ✅ (In Progress)

See [plan.md](./plan.md) for the full scope and [tactical-design.md](./tactical-design.md) for implementation details.

## Architecture

```
Twilio (Phone) → LiveKit (WebRTC) → Silero VAD → Deepgram STT 
    → LLM Agent → ElevenLabs TTS → LiveKit → Twilio → Driver
```

## Phase 1: Voice Pipeline Setup

### Prerequisites

Before you start, you need:

1. **LiveKit Server**
   - Option A: [LiveKit Cloud](https://cloud.livekit.io) (easiest)
   - Option B: [Self-hosted](https://docs.livekit.io/realtime/self-hosting/)
   
2. **API Keys**
   - [Deepgram](https://deepgram.com) - Speech-to-Text
   - [ElevenLabs](https://elevenlabs.io) - Text-to-Speech

### Installation

1. **Clone and setup**
   ```bash
   cd "/path/to/Appointment Agent"
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the agent**
   ```bash
   python -m agent.main
   ```

### Testing Phase 1

Use [LiveKit Agents Playground](https://agents-playground.livekit.io):

1. Connect to your LiveKit server
2. Join a room
3. The agent should greet you
4. Speak clearly - it will echo your message back
5. Test with background noise (play truck sounds from YouTube)

### Phase 1 Validation Checklist

- [ ] Agent connects to LiveKit successfully
- [ ] Deepgram transcribes clear speech (>95% accuracy)
- [ ] Agent responds with TTS (<1.5s latency)
- [ ] Barge-in works (interrupting stops TTS)
- [ ] Works with background noise (>80% accuracy)
- [ ] No false triggers from silence

## Project Structure

```
appointment-agent/
├── agent/
│   ├── __init__.py
│   ├── main.py           # Entrypoint
│   ├── pipeline.py       # Voice pipeline orchestration
│   ├── config.py         # Configuration
│   ├── tools/            # Tool calling (Phase 2+)
│   └── prompts/          # LLM prompts (Phase 2+)
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Development

### Running in development mode

```bash
# Activate virtualenv
source venv/bin/activate

# Run with debug logging
LIVEKIT_LOG_LEVEL=debug python -m agent.main
```

### Code formatting

```bash
black agent/
ruff check agent/
```

## Troubleshooting

### "No module named 'livekit'"

Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Connection refused" to LiveKit

- Check your `LIVEKIT_URL` in `.env`
- Verify LiveKit server is running
- For LiveKit Cloud, URL should be `wss://your-instance.livekit.cloud`

### High latency or choppy audio

- Check your internet connection
- Try a different Deepgram model: `nova-2-general` → `nova-2-phonecall`
- Adjust VAD thresholds in `config.py`

### Poor transcription accuracy in noise

Current VAD settings are tuned for noisy environments. If too aggressive:
- Increase `vad_energy_threshold` (default 0.5 → 0.6)
- Increase `vad_silence_duration` (default 700ms → 900ms)

## Next Phases

- **Phase 2**: LLM integration (Claude/GPT-4o) + Google Calendar tool calling
- **Phase 3**: Twilio phone integration + SMS
- **Phase 4**: RAG + conflict resolution + fallback system
- **Phase 5**: Langfuse observability
- **Phase 6**: Dispatcher dashboard

## License

MIT
