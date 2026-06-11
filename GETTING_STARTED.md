# Getting Started - Complete Guide

Welcome! This guide will take you from zero to a working voice agent in ~30 minutes.

## 🎯 What You'll Build

A voice agent that can:
- Have natural conversations using GPT-4o
- Check appointment availability in Google Calendar
- Book, list, and cancel appointments
- Work in noisy environments (truck cabin)
- All via voice interaction

## 📍 Where You Are

Your project is organized by phases:
- **Phase1/** - Basic voice pipeline (VAD, STT, TTS)
- **Phase2/** - LLM + Google Calendar (←  START HERE)
- **Phase3-6/** - Coming later (Twilio, RAG, Dashboard)

**We recommend starting with Phase 2** because it includes all Phase 1 capabilities plus real scheduling.

## 🚀 Quick Start (Phase 2)

### Step 1: Prerequisites (10 min)

You need 5 API keys:

#### 1. LiveKit (Audio Transport)
- Go to [cloud.livekit.io](https://cloud.livekit.io)
- Sign up (free tier)
- Create a project
- Copy: WebSocket URL, API Key, API Secret

#### 2. Deepgram (Speech-to-Text)
- Go to [console.deepgram.com](https://console.deepgram.com/signup)
- Sign up (12,000 min/month free)
- Create API key
- Copy it

#### 3. ElevenLabs (Text-to-Speech)
- Go to [elevenlabs.io](https://elevenlabs.io)
- Sign up (10,000 chars/month free)
- Profile → API Keys → Create
- Copy it

#### 4. OpenAI (GPT-4o)
- Go to [platform.openai.com](https://platform.openai.com)
- Sign up
- Create API key
- Copy it (starts with `sk-`)

#### 5. Google Calendar (Appointment Storage)
This one is more involved. We have a [complete guide](Phase2/GOOGLE_CALENDAR_SETUP.md).

**Quick version:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create project → Enable Calendar API
3. Create Service Account → Download JSON key
4. Share your Google Calendar with the service account email

**Full guide**: [Phase2/GOOGLE_CALENDAR_SETUP.md](Phase2/GOOGLE_CALENDAR_SETUP.md)

### Step 2: Setup (5 min)

```bash
# Navigate to Phase 2
cd "Appointment Agent/Phase2"

# Run automated setup
./setup.sh

# This will:
# - Create virtual environment
# - Install dependencies
# - Create .env template
# - Create credentials directory
```

### Step 3: Configure (5 min)

Edit `.env` file:

```bash
# LiveKit
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxx
LIVEKIT_API_SECRET=xxxxx

# Deepgram
DEEPGRAM_API_KEY=xxxxx

# ElevenLabs
ELEVENLABS_API_KEY=xxxxx

# OpenAI (NEW)
OPENAI_API_KEY=sk-proj-xxxxx

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/google-calendar-service-account.json
GOOGLE_CALENDAR_ID=primary
```

Place your Google service account JSON:
```bash
mv ~/Downloads/your-service-account-*.json Phase2/credentials/google-calendar-service-account.json
```

### Step 4: Verify (1 min)

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
✅ Google Calendar Credentials: Found service account: xxx@xxx.iam.gserviceaccount.com

🎉 All checks passed!
```

### Step 5: Run (1 min)

```bash
python -m agent.main
```

Expected output:
```
INFO     starting_phase2_agent 
         livekit_url=wss://...
         llm_model=gpt-4o
INFO     Worker registered
INFO     Waiting for room...
```

### Step 6: Test (10 min)

1. Open [agents-playground.livekit.io](https://agents-playground.livekit.io)
2. Enter your LiveKit URL and API key
3. Click "Connect"
4. Allow microphone access

You should hear: "Hi Mike, this is the scheduling assistant..."

**Try this conversation:**

```
You: "Hi"
Agent: "Hi Mike, am I speaking with Mike?"
You: "Yes"
Agent: "Great! How can I help you today?"
You: "I need to book a delivery appointment"
Agent: "Sure! Which facility and what date?"
You: "Denver warehouse, next Thursday"
Agent: [checks calendar] "I have 10am, 2pm, or 4pm available"
You: "2pm works"
Agent: [books] "Done! Booked for Thursday at 2pm. You'll get a text."
```

**Verify**: Open Google Calendar - you should see the appointment!

## ✅ Validation Checklist

Test these scenarios:

### Basic Flow
- [ ] Agent greets you
- [ ] You can book an appointment
- [ ] Appointment appears in Google Calendar
- [ ] Agent remembers context (your name, etc.)
- [ ] Response time feels natural (<2.5s)

### Edge Cases
- [ ] No available slots → agent offers alternatives
- [ ] Unclear request → agent asks for clarification
- [ ] Interrupt agent → it stops and listens

### Calendar Integration
- [ ] `check_availability` finds real slots
- [ ] Booked appointments have correct time/details
- [ ] Can list your upcoming appointments
- [ ] Can cancel an appointment

## 🐛 Common Issues

### "Connection refused"
**Problem**: Can't connect to LiveKit

**Fix**:
- Check `LIVEKIT_URL` in `.env` is correct
- Verify it starts with `wss://` (not `ws://` for cloud)
- Test: Visit the URL in browser - should show "404 page not found" (that's OK)

### "Invalid credentials" (OpenAI)
**Problem**: OpenAI API key rejected

**Fix**:
- Verify key starts with `sk-`
- Check for typos or extra spaces
- Ensure you have API credits in OpenAI account

### "Google Calendar credentials not found"
**Problem**: Can't find service account JSON

**Fix**:
```bash
# Check if file exists
ls -l Phase2/credentials/google-calendar-service-account.json

# If missing, find the downloaded file
ls -l ~/Downloads/*service*.json

# Move it
mv ~/Downloads/your-file.json Phase2/credentials/google-calendar-service-account.json
```

### "Permission denied" (Calendar)
**Problem**: Can't access Google Calendar

**Fix**:
1. Open Google Calendar
2. Settings → Share with specific people
3. Add the service account email (from JSON file: `client_email`)
4. Set permission to "Make changes to events"
5. Click "Send"

### "Agent doesn't respond"
**Problem**: Agent not hearing you

**Fix**:
- Check microphone permissions in browser
- Verify microphone is working (test in browser settings)
- Try speaking louder/clearer
- Check agent logs for "speech_ended" messages

### High latency (>5 seconds)
**Problem**: Slow responses

**Fix**:
- Check internet speed (speedtest.net)
- Try `gpt-4o-mini` instead (faster, slightly less capable)
  - Edit `Phase2/agent/config.py`: `llm_model: str = "gpt-4o-mini"`
- Use LiveKit cloud region closest to you

## 📖 Next Steps

### Learn More
- [Phase 2 README](Phase2/README.md) - Complete Phase 2 documentation
- [Google Calendar Setup](Phase2/GOOGLE_CALENDAR_SETUP.md) - Detailed calendar guide
- [Tactical Design](tactical-design.md) - Overall implementation plan

### Customize
Edit `Phase2/agent/prompts/system.py` to change:
- Agent personality
- Response style
- Appointment types
- Conversation flow

Edit `Phase2/agent/config.py` to adjust:
- Business hours (default: 8am-6pm)
- Appointment duration (default: 30 min)
- LLM temperature, max tokens

### Move to Production

Once Phase 2 works:
- **Phase 3**: Real phone calls via Twilio (not just Playground)
- **Phase 4**: RAG for policy retrieval, fallback system
- **Phase 5**: Langfuse observability, metrics
- **Phase 6**: Web dashboard for dispatchers

## 💡 Tips

1. **Start Simple**: Book one appointment before testing edge cases
2. **Check Calendar**: Verify every booking actually appears
3. **Use Dev Tools**: Check browser console for errors
4. **Monitor Logs**: Watch agent terminal output for insights
5. **Be Patient**: First run may be slow as models load

## 🎉 Success!

If you completed a full booking conversation and the appointment appeared in Google Calendar, you've successfully built a working voice agent!

**What you've built:**
- ✅ Real-time voice conversation
- ✅ Natural language understanding (GPT-4o)
- ✅ Google Calendar integration
- ✅ Multi-turn context retention
- ✅ Noise-robust audio pipeline

**Next**: Test edge cases, customize prompts, move to Phase 3 for phone integration.

## 🆘 Need Help?

1. **Setup Issues**: [Phase2/README.md](Phase2/README.md) → Troubleshooting
2. **Calendar Issues**: [GOOGLE_CALENDAR_SETUP.md](Phase2/GOOGLE_CALENDAR_SETUP.md)
3. **Architecture Questions**: [Phase1/ARCHITECTURE.md](Phase1/ARCHITECTURE.md)
4. **Overall Plan**: [tactical-design.md](tactical-design.md)

---

**Current**: Phase 2 (LLM + Calendar)  
**Next**: Phase 3 (Twilio Phone Integration)  
**Goal**: Complete voice agent for truck driver appointment scheduling
