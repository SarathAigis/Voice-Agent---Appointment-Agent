```markdown
# Phase 2: LLM Integration + Google Calendar

Voice agent with GPT-4o conversational intelligence and real appointment scheduling via Google Calendar.

## 🎯 What's New in Phase 2

### Conversational Intelligence
- **GPT-4o** - Natural multi-turn conversations
- Context retention across conversation
- Intent recognition and handling
- Natural language understanding

### Google Calendar Integration
- Real appointment booking
- Availability checking
- Rescheduling and cancellation
- Appointment listing

### Tool Calling
- `check_availability` - Find available time slots
- `book_appointment` - Create appointments
- `list_appointments` - Show upcoming appointments
- `cancel_appointment` - Cancel bookings

## 📋 Prerequisites

Everything from Phase 1, plus:

1. **OpenAI API Key**
   - Sign up at [platform.openai.com](https://platform.openai.com)
   - Create an API key
   - Model: GPT-4o

2. **Google Calendar Setup**
   - Google Cloud project
   - Calendar API enabled
   - Service account with Calendar access
   - Downloaded JSON credentials

## 🚀 Quick Start

### 1. Setup

```bash
cd Phase2
./setup.sh
```

### 2. Configure API Keys

Edit `.env`:
```bash
# All Phase 1 keys (LiveKit, Deepgram, ElevenLabs)
# ...

# NEW: OpenAI for GPT-4o
OPENAI_API_KEY=sk-proj-...

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/google-calendar-service-account.json
GOOGLE_CALENDAR_ID=primary
```

### 3. Google Calendar Setup

**Create Service Account:**

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable Google Calendar API:
   - APIs & Services → Library
   - Search "Google Calendar API"
   - Click "Enable"

4. Create Service Account:
   - APIs & Services → Credentials
   - Create Credentials → Service Account
   - Fill in details, click "Create"
   - Skip optional steps, click "Done"

5. Create Key:
   - Click on the service account you just created
   - Keys tab → Add Key → Create New Key
   - Choose JSON format
   - Download and save as `credentials/google-calendar-service-account.json`

6. Share Calendar:
   - Open Google Calendar
   - Find the calendar you want to use
   - Settings → Share with specific people
   - Add the service account email (from JSON file)
   - Grant "Make changes to events" permission

### 4. Run

```bash
source venv/bin/activate
python -m agent.main
```

### 5. Test

Visit [agents-playground.livekit.io](https://agents-playground.livekit.io) and try:

**Test Conversation Flow:**
```
You: "Hi"
Agent: "Hi Mike, this is the scheduling assistant. Am I speaking with Mike?"
You: "Yes"
Agent: "Great! How can I help you today?"
You: "I need to book a delivery appointment"
Agent: "Sure! Which facility and what date works for you?"
You: "Denver warehouse, next Thursday"
Agent: [checks availability] "I have availability at: 10:00 AM, 2:00 PM or 4:00 PM"
You: "2pm works"
Agent: [books appointment] "Done! I've booked your delivery at Denver warehouse for Thursday at 2:00 PM. You'll get a text confirmation."
```

## 🧪 Phase 2 Validation Checklist

### Conversational Intelligence
- [ ] Agent maintains context across multiple turns
- [ ] Natural responses (not robotic or scripted)
- [ ] Understands variations ("next Thursday" vs "Thursday" vs "2024-06-13")
- [ ] Asks clarifying questions when needed
- [ ] Handles interruptions gracefully

### Google Calendar Integration
- [ ] Check availability returns real calendar slots
- [ ] Book appointment creates event in Google Calendar
- [ ] Event has correct details (time, facility, driver info)
- [ ] List appointments shows upcoming bookings
- [ ] Cancel appointment removes event from calendar

### Tool Calling
- [ ] Agent uses tools appropriately (doesn't try to guess availability)
- [ ] Tool calls complete within <2s
- [ ] Error handling works (graceful degradation if calendar unavailable)
- [ ] Agent confirms before booking

### Latency
- [ ] End-to-end response (with tool call): <2.5s
- [ ] Simple response (no tool call): <1.5s
- [ ] Tool execution: <1s

### Edge Cases
- [ ] No available slots → agent offers alternatives
- [ ] Ambiguous request → agent clarifies
- [ ] Out-of-scope question → agent redirects politely
- [ ] Driver changes mind → agent adapts

## 🏗️ Architecture

```
User Speech
    ↓
Silero VAD → Deepgram STT
    ↓
GPT-4o LLM
    ├→ Tool: check_availability → Google Calendar API
    ├→ Tool: book_appointment → Google Calendar API
    ├→ Tool: list_appointments → Google Calendar API
    └→ Tool: cancel_appointment → Google Calendar API
    ↓
Response Text
    ↓
ElevenLabs TTS → Audio Output
```

## 📂 File Structure

```
Phase2/
├── agent/
│   ├── __init__.py
│   ├── main.py              # Entrypoint
│   ├── config.py            # Configuration (now with GPT-4o)
│   ├── pipeline.py          # Voice pipeline with tool calling
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── calendar.py      # Google Calendar integration
│   │   └── schemas.py       # Data models
│   └── prompts/
│       ├── __init__.py
│       └── system.py        # System prompt for scheduling
├── credentials/             # Google service account JSON
├── tests/
├── .env                     # Your API keys
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🔧 Configuration

Key settings in `agent/config.py`:

```python
# LLM
llm_model: str = "gpt-4o"
llm_temperature: float = 0.7
llm_max_tokens: int = 500  # Keep voice responses concise

# Calendar
google_calendar_credentials_path: str = "./credentials/..."
google_calendar_id: str = "primary"

# Appointments
default_appointment_duration_minutes: int = 30
business_hours_start: int = 8  # 8 AM
business_hours_end: int = 18   # 6 PM
```

## 🐛 Troubleshooting

### Google Calendar Issues

**"Credentials not found"**
```bash
# Check file exists
ls -l credentials/google-calendar-service-account.json

# Check path in .env
cat .env | grep GOOGLE_CALENDAR_CREDENTIALS_PATH
```

**"Permission denied" when booking**
- Verify you shared the calendar with the service account email
- Check the service account has "Make changes to events" permission

**"No available slots" (but calendar is empty)**
- Check `business_hours_start` and `business_hours_end` in config
- Ensure requested date is not in the past
- Verify timezone settings

### GPT-4o Issues

**High latency (>3s per response)**
- Check OpenAI API status
- Consider using `gpt-4o-mini` for faster responses (trade-off: slightly less capable)
- Verify `llm_max_tokens` is set to 500 or less

**Tool calling not working**
- Check agent logs for tool call attempts
- Verify function names match exactly
- Ensure function descriptions are clear

**Agent doesn't understand requests**
- Review system prompt in `agent/prompts/system.py`
- Test with simpler, more direct phrases
- Check conversation history isn't getting too long

### Calendar Mock Mode

If you don't have Google Calendar set up yet, the agent will use mock data:
- Returns predefined time slots (10am, 2pm, 4pm)
- Simulates booking (doesn't actually create events)
- Logs indicate "mock_appointment_booked"

This lets you test the conversation flow before connecting real calendar.

## 📊 What to Observe

During Phase 2 testing:

1. **Conversation Quality**
   - Does the agent sound natural?
   - Does it ask appropriate follow-up questions?
   - Can it handle multi-step scheduling?

2. **Tool Usage**
   - When does the agent call tools vs. respond directly?
   - Are tool calls successful?
   - Does it handle tool errors gracefully?

3. **Context Retention**
   - Does it remember driver name throughout?
   - Can it reference previously mentioned details?
   - Does context stay relevant across turns?

4. **Performance**
   - Total latency including tool calls
   - Google Calendar API response time
   - GPT-4o inference time

## ✅ Phase 2 Complete When

- [ ] Full booking conversation completes successfully
- [ ] Appointments appear in Google Calendar
- [ ] Multi-turn conversations work naturally
- [ ] Tool calling is reliable (<5% failure rate)
- [ ] End-to-end latency <2.5s (including tool calls)
- [ ] Agent handles at least 3 edge cases gracefully

## 🔜 Next: Phase 3

Once Phase 2 validates, we add:
- **Twilio** - Real outbound phone calls (not just Playground)
- **SIP Trunk** - Connect phone network to LiveKit
- **SMS** - Send confirmation texts
- **Voicemail Detection** - Handle when calls go to voicemail

---

**Current**: Phase 2 - LLM + Calendar  
**Next**: Phase 3 - Twilio + Phone Integration
```
