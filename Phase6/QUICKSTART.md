# Quick Start - Make Your First Call

## Prerequisites Checklist

Before starting, get these API keys (free tiers available):

- [ ] **Twilio** - Phone calls + SMS
  - Sign up: https://www.twilio.com/try-twilio
  - Get: Account SID, Auth Token, Phone Number
  
- [ ] **LiveKit** - Audio transport
  - Sign up: https://cloud.livekit.io
  - Get: URL, API Key, API Secret
  
- [ ] **Deepgram** - Speech-to-Text
  - Sign up: https://console.deepgram.com
  - Get: API Key
  
- [ ] **ElevenLabs** - Text-to-Speech
  - Sign up: https://elevenlabs.io
  - Get: API Key
  
- [ ] **OpenAI** - GPT-4o
  - Sign up: https://platform.openai.com
  - Get: API Key
  
- [ ] **Google Calendar** (Optional for first test)
  - Can test without this initially

## Step 1: Setup Environment (5 minutes)

```bash
cd Phase6

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

## Step 2: Configure API Keys

Edit `Phase6/.env` with your keys:

```bash
# Required for phone calls
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Required for voice pipeline
LIVEKIT_URL=wss://your-instance.livekit.cloud
LIVEKIT_API_KEY=APIxxxxx
LIVEKIT_API_SECRET=xxxxxx

DEEPGRAM_API_KEY=xxxxxx
ELEVENLABS_API_KEY=xxxxxx
OPENAI_API_KEY=sk-proj-xxxxxx

# Optional for first test (can add later)
# GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/google-calendar-service-account.json
```

## Step 3: Start the Services

You need **2 terminals**:

### Terminal 1: API Server
```bash
cd Phase6
source venv/bin/activate
python -m api.server
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Terminal 2: Voice Agent
```bash
cd Phase6
source venv/bin/activate
python -m agent.main
```

You should see:
```
INFO     starting_phase3_agent
INFO     Worker registered
```

## Step 4: Make a Test Call! 📞

### Terminal 3: Trigger the Call
```bash
cd Phase6

# Replace with YOUR phone number
curl -X POST http://localhost:8000/api/calls/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "driver_id": "DRV-TEST-001",
    "driver_name": "Test Driver",
    "driver_phone": "+1YOUR_PHONE_NUMBER",
    "truck_number": "T-001",
    "call_purpose": "appointment scheduling test"
  }'
```

**Your phone should ring!** 📱

## What to Expect

1. **Phone rings** - Your phone will show the Twilio number
2. **Agent greets you** - "Hi Test Driver, this is the scheduling assistant..."
3. **Have a conversation** - Try:
   - "Hi, I need to schedule a delivery"
   - "What times are available?"
   - "Can I book for Thursday at 2pm?"
4. **Agent responds naturally** - GPT-4o understands and responds
5. **SMS confirmation** (if configured) - Get a text with details

## Troubleshooting

### Phone doesn't ring
```bash
# Check Twilio account status
curl https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID.json \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN | jq .status

# Should return "active"
```

**Trial account?** You can only call verified numbers. Add your number at:
https://console.twilio.com/us1/develop/phone-numbers/manage/verified

### API server error
```bash
# Check if running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### Voice agent not connecting
```bash
# Check LiveKit credentials
# Verify URL format: wss://xxx.livekit.cloud (not ws://)
```

### Poor audio quality
- Background noise is expected (it's designed for it!)
- The agent has noise-robust settings
- Try from a quieter location first to verify it works

## Test Without Phone (Optional)

Use LiveKit Playground for testing without Twilio:

```bash
# Just run the voice agent (skip API server)
cd Phase6
source venv/bin/activate
python -m agent.main

# Open browser to:
# https://agents-playground.livekit.io

# Connect with your LiveKit credentials
# Test the conversation without phone call costs
```

## Next Steps

Once your test call works:

1. **Add Google Calendar** - For real appointment booking
   - Follow: Phase2/GOOGLE_CALENDAR_SETUP.md
   
2. **Test in noise** - Play truck cabin noise while calling
   - YouTube: "truck cabin noise 10 hours"
   
3. **Test edge cases**:
   - Let it go to voicemail
   - Interrupt the agent
   - Ask for something it can't do
   
4. **View the dashboard** (optional):
   ```bash
   cd Phase6/dashboard
   npm install
   npm run dev
   # Open http://localhost:3000
   ```

## Cost Per Test Call

- Twilio Voice: ~$0.065 (5 min)
- Deepgram STT: ~$0.02
- ElevenLabs TTS: ~$0.015
- GPT-4o: ~$0.005
- **Total: ~$0.10 per test call**

## Quick Command Reference

```bash
# Check all services are ready
curl http://localhost:8000/health          # API server
ps aux | grep "agent.main"                 # Voice agent

# View recent calls
curl http://localhost:8000/api/dashboard/recent-calls | jq

# Stop everything
# Ctrl+C in both terminal windows

# Check logs
tail -f logs/*.log  # If you configured logging
```

## Need Help?

- **Twilio issues**: Phase3/TWILIO_SETUP.md
- **Calendar setup**: Phase2/GOOGLE_CALENDAR_SETUP.md
- **General setup**: Phase6/README.md
- **Architecture**: Phase1/ARCHITECTURE.md

---

**Ready to make your first call?** Start with Step 1! 🚀
