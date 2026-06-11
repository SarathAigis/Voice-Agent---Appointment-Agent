# Phase 3: Twilio Phone Integration

Real outbound phone calls! Your voice agent can now call truck drivers on their actual phones, not just via LiveKit Playground.

## 🎯 What's New in Phase 3

### Real Phone Calls
- **Twilio Outbound Calling** - Call real phone numbers
- **PSTN to LiveKit Bridge** - Connect phone network to your agent
- **Call Lifecycle Management** - Track initiated → ringing → answered → completed

### SMS Integration
- **Appointment Confirmations** - Text after successful booking
- **Voicemail Fallback** - SMS when call goes to voicemail
- **Failed Call Followup** - SMS when can't reach driver

### Voicemail Handling
- **Automatic Detection** - Twilio AMD (Answering Machine Detection)
- **Leave Message** - Play pre-recorded voicemail message
- **SMS Followup** - Send text with callback number

### API Server
- **FastAPI Backend** - RESTful API for triggering calls
- **Webhook Handlers** - Receive Twilio call events
- **Call Status Tracking** - Monitor active calls

## 📋 Prerequisites

Everything from Phase 1-2, plus:

### 1. Twilio Account

**Sign Up:**
1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up (free trial gives $15 credit)
3. Verify your email and phone

**Get Phone Number:**
1. Console → Phone Numbers → Buy a Number
2. Select a number with **Voice** capability
3. SMS capability optional but recommended
4. Cost: ~$1-2/month

**Get Credentials:**
1. Console → Account → API keys & tokens
2. Copy:
   - Account SID (starts with `AC`)
   - Auth Token (click "show" to reveal)

### 2. Expose API Server (Development)

For Twilio webhooks to reach your local machine:

**Option A: ngrok (Recommended)**
```bash
# Install ngrok
brew install ngrok  # Mac
# or download from ngrok.com

# Run ngrok
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Twilio Dev Phone**
- Use Twilio's test credentials
- Calls won't reach real phones but you can test the flow

**Production**: Deploy to a server with public IP/domain

## 🚀 Quick Start

### Step 1: Setup

```bash
cd Phase3
./setup.sh
```

### Step 2: Configure

Edit `.env`:
```bash
# All Phase 1-2 keys...

# NEW: Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# SMS (uses same number by default)
TWILIO_ENABLE_SMS=true

# API Server
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 3: Copy Google Calendar Credentials

```bash
# From Phase 2
cp ../Phase2/credentials/google-calendar-service-account.json ./credentials/
```

### Step 4: Start Services

**Terminal 1 - API Server:**
```bash
source venv/bin/activate
python -m api.server
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Voice Agent:**
```bash
source venv/bin/activate
python -m agent.main
```

You should see:
```
INFO     starting_phase3_agent
INFO     Worker registered
```

### Step 5: Make a Test Call

**Option A: API Request**
```bash
curl -X POST http://localhost:8000/api/calls/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "driver_id": "DRV-001",
    "driver_name": "Mike",
    "driver_phone": "+1YOUR_PHONE_NUMBER",
    "truck_number": "T-4521",
    "call_purpose": "appointment confirmation"
  }'
```

**Option B: Python Script**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/calls/initiate",
    json={
        "driver_id": "DRV-001",
        "driver_name": "Mike",
        "driver_phone": "+1YOUR_PHONE_NUMBER",
        "truck_number": "T-4521",
        "call_purpose": "appointment scheduling",
    }
)

print(response.json())
```

**Your phone should ring!** 📞

### Step 6: Have a Conversation

```
Agent: "Hi Mike, this is the scheduling assistant. Am I speaking with Mike?"
You: "Yes"
Agent: "Great! How can I help you today?"
You: "Book a delivery for Thursday"
Agent: [checks calendar] "I have 10am, 2pm, or 4pm"
You: "2pm"
Agent: [books] "Done! You'll get a text confirmation."
[SMS arrives with appointment details]
```

## 🏗️ Architecture

```
Your API Request
    ↓
FastAPI Server (/api/calls/initiate)
    ↓
Twilio REST API (create call)
    ↓
Twilio dials driver's phone
    ↓
Driver answers
    ↓
Twilio calls webhook (/api/calls/twiml/{room})
    ↓
TwiML connects to LiveKit Room
    ↓
LiveKit Agent joins room
    ↓
[Voice conversation with GPT-4o + Calendar tools]
    ↓
Agent books appointment
    ↓
Twilio SMS API sends confirmation
    ↓
Call ends
```

## 📂 File Structure

```
Phase3/
├── agent/
│   ├── main.py              # Agent entrypoint
│   ├── pipeline.py          # Voice pipeline (Phase 2 + SMS)
│   ├── config.py            # Configuration (+ Twilio settings)
│   ├── telephony/           # NEW
│   │   ├── outbound.py      # Twilio call initiation
│   │   ├── sms.py           # SMS messaging
│   │   └── voicemail.py     # Voicemail detection
│   ├── tools/               # From Phase 2
│   └── prompts/             # From Phase 2
│
├── api/                     # NEW
│   ├── server.py            # FastAPI server
│   └── routes/
│       ├── calls.py         # Call management endpoints
│       └── webhooks.py      # Twilio webhook handlers
│
├── data/                    # SQLite database (auto-created)
├── credentials/             # Google Calendar credentials
├── tests/
├── .env
├── requirements.txt
└── README.md
```

## 🧪 Testing

### Test 1: Basic Outbound Call

1. Use your own phone number
2. Initiate call via API
3. Answer and have conversation
4. Verify SMS confirmation arrives

### Test 2: Voicemail Detection

1. Don't answer the call
2. Let it go to voicemail
3. Verify voicemail message plays
4. Verify SMS fallback arrives

### Test 3: Failed Call

1. Use an invalid number
2. Initiate call
3. Verify SMS fallback is sent

### Test 4: Full Booking Flow

1. Call with real appointment intent
2. Complete booking conversation
3. Check Google Calendar for appointment
4. Verify SMS confirmation

## 📊 API Endpoints

### POST /api/calls/initiate
Initiate an outbound call.

**Request:**
```json
{
  "driver_id": "DRV-001",
  "driver_name": "Mike Johnson",
  "driver_phone": "+15551234567",
  "truck_number": "T-4521",
  "call_purpose": "appointment confirmation",
  "appointment_id": "apt-123",
  "context": {}
}
```

**Response:**
```json
{
  "call_sid": "CAxxxxx",
  "status": "initiated",
  "room_name": "call-DRV-001-1234567890",
  "message": "Call initiated to Mike Johnson"
}
```

### GET /api/calls/status/{call_sid}
Get call status.

**Response:**
```json
{
  "call_sid": "CAxxxxx",
  "status": "completed",
  "driver_name": "Mike Johnson",
  "answered": true,
  "voicemail_detected": false,
  "duration_seconds": 145,
  "start_time": "2024-06-11T10:30:00",
  "end_time": "2024-06-11T10:32:25"
}
```

### POST /api/calls/hangup/{call_sid}
Hangup an active call.

### POST /api/calls/status (Webhook)
Twilio calls this when call status changes.

### GET /api/calls/twiml/{room_name}
Returns TwiML to connect call to LiveKit.

## 🔧 Configuration

### Call Settings

```python
# .env or agent/config.py

# Voicemail Detection
ENABLE_VOICEMAIL_DETECTION=true
VOICEMAIL_MESSAGE="Hi, this is the scheduling assistant..."

# Call Limits
MAX_CALL_DURATION_SECONDS=300  # 5 minutes
CALL_TIMEOUT_SECONDS=30        # Ring timeout

# SMS
TWILIO_ENABLE_SMS=true
SMS_FROM_NUMBER=+1234567890    # Optional, uses TWILIO_PHONE_NUMBER by default
```

### Twilio Webhook Configuration

In Twilio Console:
1. Phone Numbers → Your Number → Voice & Fax
2. "A CALL COMES IN" → Webhook → `https://your-domain.com/api/calls/twiml/{room}`
3. "STATUS CALLBACK URL" → `https://your-domain.com/api/calls/status`
4. Save

## 🐛 Troubleshooting

### Call Not Connecting

**Symptom**: API returns success but phone doesn't ring

**Fixes**:
- Verify phone number format: `+1234567890` (E.164 format)
- Check Twilio account status (trial vs. paid)
- Trial accounts can only call verified numbers
- Check Twilio console → Monitor → Logs for errors

### Voicemail Detection Not Working

**Symptom**: Voicemail not detected, agent talks to recording

**Fixes**:
- Ensure `ENABLE_VOICEMAIL_DETECTION=true`
- AMD takes 5-7 seconds to detect
- May not work on all carriers
- Check logs for `AnsweredBy` field in webhook

### SMS Not Sending

**Symptom**: Appointments booked but no SMS

**Fixes**:
- Verify `TWILIO_ENABLE_SMS=true`
- Check phone number has SMS capability
- Trial accounts require verified recipient numbers
- Check Twilio logs for SMS send errors

### Webhook Not Receiving Events

**Symptom**: Calls work but status not updating

**Fixes**:
- Verify ngrok/public URL is accessible
- Check Twilio webhook configuration
- Use `https://` (not `http://`) for Twilio webhooks
- Test endpoint: `curl https://your-url.com/api/calls/status`

### "ngrok not found"

**Fix**:
```bash
brew install ngrok  # Mac
# or
snap install ngrok  # Linux
# or download from ngrok.com
```

### Poor Audio Quality

**Symptom**: Choppy or unclear audio on phone

**Fixes**:
- Check internet connection speed
- Use LiveKit Cloud (not self-hosted) for better routing
- Verify Deepgram settings (Phase 2)
- Test with different phone/carrier

## 💰 Costs (Phase 3)

| Service | Usage | Cost |
|---------|-------|------|
| Twilio Voice | Outbound call (USA) | $0.013/min |
| Twilio SMS | Per message | $0.0075/msg |
| Phone Number | Monthly | $1-2/mo |
| **Total per 5-min call** | | **~$0.08** |

Plus Phase 1-2 costs (LiveKit, Deepgram, ElevenLabs, GPT-4o) = ~$0.05

**Total Phase 3 call cost: ~$0.13-0.15**

## ✅ Phase 3 Validation Checklist

- [ ] API server starts successfully
- [ ] Voice agent starts successfully
- [ ] Outbound call initiates via API
- [ ] Your phone rings
- [ ] You can have a full conversation
- [ ] Appointments book correctly
- [ ] SMS confirmation arrives
- [ ] Voicemail detection works (let call go to VM)
- [ ] SMS fallback arrives after voicemail
- [ ] Call status tracked correctly

## 🔜 Next: Phase 4

Once Phase 3 validates:
- **RAG** - Policy retrieval from vector DB
- **Conflict Resolution** - Smart slot proposals
- **Tiered Fallback** - SMS → callback → human transfer
- **Warm Transfer** - Escalate to live dispatcher

---

**Current**: Phase 3 (Twilio + Phone Calls)  
**Next**: Phase 4 (RAG + Fallback System)  
**Progress**: 50% Complete (3 of 6 phases)
