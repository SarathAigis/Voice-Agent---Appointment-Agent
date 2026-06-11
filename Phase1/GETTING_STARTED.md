# Getting Started - Quick Guide

## 🎯 Phase 1 Goal

Build a working voice pipeline that can:
- Listen to you speak via LiveKit
- Transcribe your speech with Deepgram
- Echo your message back via ElevenLabs TTS
- Handle noisy environments (truck cabin simulation)

**No phone calls yet** - just testing the audio pipeline foundation.

## 📋 Prerequisites (5 minutes)

### 1. Get LiveKit Access

**Option A: LiveKit Cloud** (Recommended - fastest)
1. Go to [cloud.livekit.io](https://cloud.livekit.io)
2. Sign up (free)
3. Create a new project
4. Copy your:
   - WebSocket URL (e.g., `wss://your-project.livekit.cloud`)
   - API Key
   - API Secret

**Option B: Self-Hosted**
```bash
docker run -d \
  --name livekit \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  livekit/livekit-server \
  --dev
```
URL will be: `ws://localhost:7880`

### 2. Get Deepgram API Key
1. Go to [console.deepgram.com/signup](https://console.deepgram.com/signup)
2. Sign up (free tier: 12,000 min/month)
3. Create an API key
4. Copy it

### 3. Get ElevenLabs API Key
1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Sign up (free tier: 10,000 chars/month)
3. Go to Profile → API Keys
4. Create and copy key

## 🚀 Setup (2 minutes)

```bash
# 1. Navigate to project
cd "/Users/sarathchandra/Desktop/AI Personal Projects/Bootstrapped Applications/Voice Agents/Appointment Agent"

# 2. Run setup
./setup.sh

# 3. Edit .env with your keys
nano .env  # or use your favorite editor
```

Your `.env` should look like:
```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxx

DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxx

ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxx
```

## ✅ Verify Setup

```bash
source venv/bin/activate
python check_setup.py
```

You should see:
```
✅ Python Version: Python 3.11.x
✅ Environment File: All required keys present
✅ Dependencies: Core dependencies installed
✅ Configuration: Configuration loads successfully

🎉 All checks passed!
```

## 🎙️ Run the Agent

```bash
source venv/bin/activate
python -m agent.main
```

Expected output:
```
INFO     starting_agent livekit_url=wss://...
INFO     Worker registered
INFO     Waiting for room...
```

## 🧪 Test It

### Open LiveKit Playground

1. Go to [agents-playground.livekit.io](https://agents-playground.livekit.io)
2. Enter your LiveKit URL and API Key
3. Click **"Connect"**
4. Allow microphone access

### Test Flow

1. **Agent greets you**: You should hear "Hello, this is a test of the voice pipeline. Please say something."

2. **Speak clearly**: Say "Hello, my name is [Your Name]"
   - You should see your speech transcribed on screen
   - Agent will respond: "I heard you say: [your message]. This is a test of the voice pipeline."

3. **Test noise handling**:
   - Open YouTube: search "truck cabin noise"
   - Play it on another device or speaker
   - Speak while noise is playing
   - Agent should still transcribe reasonably well

4. **Test interruption**:
   - Let agent start speaking
   - Interrupt by speaking
   - Agent should stop immediately and listen

## 📊 Validation Checklist

Mark each as you test:

**Basic Tests:**
- [ ] Agent connects and greets you
- [ ] Your speech is transcribed accurately (>95% in quiet)
- [ ] Agent echoes your message via TTS
- [ ] Response latency < 1.5 seconds

**Noise Tests:**
- [ ] Transcription still works with background noise (>80%)
- [ ] Agent doesn't respond to pure noise (no false triggers)

**Interaction Tests:**
- [ ] You can interrupt the agent (barge-in works)
- [ ] Multiple back-and-forth exchanges work

## 🐛 Common Issues

### "Connection refused"
- Check `LIVEKIT_URL` is correct
- Verify LiveKit server is running
- For LiveKit Cloud, URL must start with `wss://`

### "Invalid credentials"
- Check for typos in `.env`
- Ensure no extra spaces or quotes around keys
- Verify keys are active (not expired/deleted)

### "Poor audio quality"
- Check your microphone permissions
- Try a different browser (Chrome recommended)
- Check internet connection speed

### "Agent doesn't hear me"
- Verify microphone is working in browser
- Check volume levels
- Try adjusting VAD threshold in `agent/config.py`:
  ```python
  vad_energy_threshold: float = 0.4  # Lower = more sensitive
  ```

### "Too much latency"
- Use LiveKit Cloud region closest to you
- Check internet speed (speedtest.net)
- Verify using `eleven_turbo_v2` model

## 📝 Next Steps

Once all validation tests pass:

1. ✅ Mark Phase 1 complete
2. 🗣️ Ready for Phase 2: LLM Integration
   - Add Claude/GPT-4o conversational intelligence
   - Integrate Google Calendar
   - Real appointment scheduling logic

## 🆘 Need Help?

1. Check [PHASE1.md](./PHASE1.md) for detailed troubleshooting
2. Review [tactical-design.md](./tactical-design.md) for architecture details
3. Check LiveKit docs: [docs.livekit.io](https://docs.livekit.io)

---

**Ready?** Run `./setup.sh` and let's test your voice pipeline!
