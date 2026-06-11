# Phase 1: Basic Voice Pipeline - Implementation Guide

## ✅ What We've Built

The foundational voice pipeline connecting:
- **Silero VAD** - Voice activity detection (tuned for noisy environments)
- **Deepgram STT** - Speech-to-text transcription
- **ElevenLabs TTS** - Text-to-speech synthesis
- **LiveKit** - Real-time audio transport

## 🚀 Getting Started

### 1. Prerequisites

You need API keys from:

- **LiveKit** (choose one):
  - [LiveKit Cloud](https://cloud.livekit.io) - fastest, free tier available
  - [Self-hosted](https://docs.livekit.io/realtime/self-hosting/) - more control

- **Deepgram**: [Sign up](https://console.deepgram.com/signup)
  - Free tier: 12,000 minutes of transcription
  - Model: Nova-2 (best for noisy audio)

- **ElevenLabs**: [Sign up](https://elevenlabs.io)
  - Free tier: 10,000 characters/month
  - Model: Turbo v2 (low latency)

### 2. Installation

```bash
# Navigate to project
cd "/Users/sarathchandra/Desktop/AI Personal Projects/Bootstrapped Applications/Voice Agents/Appointment Agent"

# Run setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

Edit `.env` file:

```bash
# LiveKit
LIVEKIT_URL=wss://your-instance.livekit.cloud  # Or ws://localhost:7880
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Deepgram
DEEPGRAM_API_KEY=your_deepgram_key

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### 4. Run the Agent

```bash
source venv/bin/activate
python -m agent.main
```

You should see:
```
INFO     starting_agent livekit_url=wss://... deepgram_model=nova-2
INFO     Worker registered room=...
```

## 🧪 Testing

### Option 1: LiveKit Agents Playground (Recommended)

1. Go to [agents-playground.livekit.io](https://agents-playground.livekit.io)
2. Enter your LiveKit URL and API key
3. Click "Connect"
4. The agent will greet you: "Hello, this is a test of the voice pipeline."
5. Speak clearly - it will echo your message back

### Option 2: Custom Client

If you have a LiveKit client app:
```bash
# Connect to your LiveKit room
# Agent will automatically join when you connect
```

## 📋 Validation Checklist

Test each scenario and check it off:

### Basic Functionality
- [ ] **Agent connects**: Agent starts and registers with LiveKit
- [ ] **Greeting plays**: You hear the greeting via TTS
- [ ] **Clear speech**: Say "Hello, how are you?" - transcribed >95% accurately
- [ ] **Echo response**: Agent repeats what you said with TTS
- [ ] **Latency**: Response starts within 1.5 seconds of you finishing speaking

### Noise Handling
- [ ] **Background noise**: Play [truck cabin noise](https://www.youtube.com/watch?v=bKkz2kixx8Y) from YouTube
  - Speech still transcribed >80% accurately
  - VAD correctly detects when you're speaking vs. background noise
- [ ] **No false triggers**: Agent doesn't respond to pure background noise (10s of silence)

### Interruption Handling
- [ ] **Barge-in works**: Speak while agent is talking - TTS stops immediately
- [ ] **Continues after interruption**: Agent processes your interruption correctly

### Edge Cases
- [ ] **Very short utterance**: Say "Yes" - should transcribe correctly
- [ ] **Long utterance**: Speak for 10+ seconds continuously
- [ ] **Multiple rapid utterances**: Say "Hello" pause 1s "How are you" - both processed

## 🔧 Troubleshooting

### Agent won't start

**Error**: `Connection refused`
- Check `LIVEKIT_URL` is correct
- Verify LiveKit server is running
- For LiveKit Cloud, URL must start with `wss://`

**Error**: `Invalid API key`
- Double-check `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` in `.env`
- Ensure no extra spaces or quotes

### Poor transcription quality

**Symptom**: Many words wrong or missing

Try these adjustments in `agent/config.py`:

```python
# Less aggressive VAD (if cutting off words)
vad_silence_duration: int = 900  # Increase from 700ms

# Different Deepgram model
deepgram_model: str = "nova-2-phonecall"  # Better for phone-like audio
```

### High latency (>2 seconds)

**Check**:
1. Internet connection speed (run `speedtest-cli`)
2. LiveKit server location (use closer region if Cloud)
3. ElevenLabs model (ensure using `eleven_turbo_v2`, not standard)

**Log latency breakdown**:
```bash
LIVEKIT_LOG_LEVEL=debug python -m agent.main
# Look for timing between "speech_ended" and "tts_started"
```

### TTS sounds robotic or cuts off

Adjust in `agent/config.py`:
```python
# More stable voice (less expressive but clearer)
elevenlabs_stability: float = 0.7  # Increase from 0.5

# Try different voice
elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)
# Or: "EXAVITQu4vr4xnSDxMaL"  # Bella - warm, friendly
```

### Background noise causes false triggers

**Symptom**: Agent responds to background sounds

Make VAD less sensitive in `agent/config.py`:
```python
vad_energy_threshold: float = 0.6  # Increase from 0.5 (higher = less sensitive)
```

## 📊 What to Observe

During testing, note:
- **STT accuracy** in quiet vs. noisy conditions
- **Latency** from your speech ending to TTS starting
- **VAD behavior** - does it correctly detect speech start/end?
- **Audio quality** - clear, natural, appropriate volume?
- **Interruption responsiveness** - instant barge-in or delayed?

## ✅ Phase 1 Complete Criteria

Phase 1 is ready for Phase 2 when:

1. ✅ Agent reliably connects and greets you
2. ✅ Clear speech transcribed >95% accurately
3. ✅ Noisy speech transcribed >80% accurately
4. ✅ End-to-end latency <1.5s (clean audio) or <2.5s (noisy)
5. ✅ Barge-in/interruption works smoothly
6. ✅ No false triggers from 10s of background noise

## 🔜 Next: Phase 2

Once Phase 1 validation passes, we'll add:
- Claude/GPT-4o conversational agent
- Google Calendar integration
- Real appointment scheduling logic
- Context retention across turns

---

**Questions or issues?** Open an issue or check the [tactical-design.md](./tactical-design.md) for detailed architecture.
