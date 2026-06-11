# Tactical Design — Voice Agent Implementation

## Implementation Philosophy

Each phase is a self-contained unit with a **validation gate** at the end. We do NOT move to the next phase until the current phase passes its validation criteria. This ensures we build on solid foundations and catch integration issues early.

---

## Phase 1: Basic Voice Pipeline (LiveKit + Silero + Deepgram + ElevenLabs)

### Goal
Get audio flowing end-to-end: microphone in → STT → hardcoded response → TTS → speaker out. No LLM, no Twilio, no scheduling logic. Just prove the audio pipeline works.

### What We Build

```
Local microphone / SIP test call
    → LiveKit Room (local dev server)
        → Silero VAD (detect speech start/end)
            → Deepgram STT (streaming transcription)
                → Static response logic (echo or canned replies)
                    → ElevenLabs TTS (generate speech)
                        → LiveKit → Speaker output
```

### Implementation Details

**Project Structure:**
```
appointment-agent/
├── agent/
│   ├── __init__.py
│   ├── main.py              # LiveKit agent entrypoint
│   ├── pipeline.py          # Voice pipeline orchestration
│   └── config.py            # API keys, model configs
├── requirements.txt
├── .env.example
└── livekit-agent.toml       # LiveKit agent config
```

**Key Files:**

1. `agent/main.py` — LiveKit Agents SDK entrypoint
   - Register the agent with LiveKit
   - Configure Silero VAD (energy_threshold tuned for noise)
   - Wire Deepgram STT (model: nova-2, language: en, smart_format: true)
   - Wire ElevenLabs TTS (model: eleven_turbo_v2, voice: conversational male/female)

2. `agent/pipeline.py` — Pipeline orchestration
   - VoicePipelineAgent from livekit-agents
   - VAD settings: `min_speech_duration=250ms`, `silence_duration=700ms` (tuned for noisy env)
   - Deepgram settings: `interim_results=true`, `endpointing=500ms`, `utterance_end_ms=1500`

3. `agent/config.py` — Configuration
   - Load from .env: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
   - DEEPGRAM_API_KEY, ELEVENLABS_API_KEY
   - VAD thresholds as configurable params

**Dependencies:**
```
livekit-agents>=0.8
livekit-plugins-silero>=0.6
livekit-plugins-deepgram>=0.6
livekit-plugins-elevenlabs>=0.7
python-dotenv
```

### Validation Gate — Phase 1

| # | Test | Pass Criteria |
|---|------|---------------|
| 1 | Start agent, connect via LiveKit Playground | Agent connects, shows "listening" state |
| 2 | Speak a sentence clearly | Deepgram transcribes with >95% accuracy |
| 3 | Speak with background noise (play road noise from speaker) | Silero VAD correctly detects speech boundaries, Deepgram still transcribes >80% |
| 4 | Agent responds with TTS | ElevenLabs audio plays back clearly, < 1s latency from end of speech to TTS start |
| 5 | Rapid speech / interruption | Barge-in works — TTS stops when driver speaks |
| 6 | Silence (no speech for 10s) | No false triggers from background noise |

**How to test:** Use LiveKit Playground (https://agents-playground.livekit.io) connected to your local LiveKit server. Play truck cabin noise from YouTube on a nearby speaker while testing.

---

## Phase 2: LLM Integration (Conversation Agent + Basic Tool Calling)

### Goal
Replace static responses with an LLM that can hold a natural scheduling conversation. Add Google Calendar tool calling. No Twilio yet — still testing via LiveKit Playground.

### What We Build

```
LiveKit Room
    → Silero VAD → Deepgram STT
        → LLM Agent (Claude/GPT-4o with system prompt + tools)
            → Tool: check_availability(date, facility)
            → Tool: book_appointment(driver_id, datetime, facility, type)
            → Tool: reschedule_appointment(appointment_id, new_datetime)
            → Tool: cancel_appointment(appointment_id)
        → ElevenLabs TTS
    → LiveKit → Speaker
```

### Implementation Details

**New/Modified Files:**
```
appointment-agent/
├── agent/
│   ├── main.py              # Updated: wire LLM into pipeline
│   ├── pipeline.py          # Updated: add LLM agent
│   ├── llm_agent.py         # NEW: LLM config, system prompt, tool definitions
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── calendar.py      # Google Calendar CRUD operations
│   │   └── schemas.py       # Tool input/output schemas
│   ├── prompts/
│   │   └── system.py        # System prompt for scheduling agent
│   └── config.py            # Updated: add LLM + Calendar config
├── requirements.txt         # Updated
└── .env.example             # Updated
```

**Key Design Decisions:**

1. **System Prompt Design** — Optimized for truck drivers:
   - Persona: Professional, friendly dispatcher assistant
   - Constraints: Keep responses under 2 sentences. Use simple language. Always confirm with repetition.
   - Behavior: Never ask more than one question at a time. Offer max 3 options.
   - Context: You're calling [Driver Name] about [Appointment Type]. Driver is likely driving.

2. **Tool Definitions:**
   ```python
   check_availability(date: str, facility: str, appointment_type: str) -> list[TimeSlot]
   book_appointment(driver_id: str, datetime: str, facility: str, type: str) -> Confirmation
   reschedule_appointment(appointment_id: str, new_datetime: str) -> Confirmation
   cancel_appointment(appointment_id: str, reason: str) -> Confirmation
   get_driver_appointments(driver_id: str) -> list[Appointment]
   ```

3. **Google Calendar Integration:**
   - Service account auth (no OAuth flow needed for POC)
   - Each facility = separate calendar
   - Appointment = calendar event with structured description (driver_id, type, truck_number)
   - Availability = find free slots in calendar within business hours

4. **LLM Selection:**
   - Primary: Claude Sonnet (best latency/quality for tool calling)
   - Fallback: GPT-4o-mini (if Claude latency exceeds threshold)
   - Measure both during this phase, pick winner for Phase 3+

### Validation Gate — Phase 2

| # | Test | Pass Criteria |
|---|------|---------------|
| 1 | Ask to book an appointment | Agent asks relevant questions (when, where, what type), books via Calendar API |
| 2 | Ask to reschedule | Agent finds existing appointment, proposes alternatives, confirms new slot |
| 3 | Request unavailable slot | Agent gracefully proposes alternatives (not error/crash) |
| 4 | Interrupt agent mid-sentence | Agent stops talking, listens, adapts response |
| 5 | Say something off-topic | Agent redirects to scheduling without being rude |
| 6 | Verify in Google Calendar | Booked appointments appear correctly in calendar with all metadata |
| 7 | Measure latency | End-to-end (speech end → TTS start) < 2s including tool call |
| 8 | 5-turn conversation | Agent maintains context across turns without confusion |

**How to test:** LiveKit Playground. Have a test Google Calendar set up. Run through the happy path call flow from the scope doc, then try edge cases.

---

## Phase 3: Twilio Integration (Real Phone Calls)

### Goal
Connect Twilio for outbound calls. Agent can now call a real phone number, have the scheduling conversation, and send SMS confirmation.

### What We Build

```
Trigger (API call / cron)
    → Twilio outbound call to driver's phone
        → Twilio SIP trunk → LiveKit Room
            → [Full voice pipeline from Phase 1+2]
        → Post-call: SMS confirmation via Twilio
```

### Implementation Details

**New/Modified Files:**
```
appointment-agent/
├── agent/
│   ├── main.py              # Updated: handle SIP participant events
│   ├── telephony/
│   │   ├── __init__.py
│   │   ├── outbound.py      # Twilio outbound call initiation
│   │   ├── sip_trunk.py     # LiveKit SIP trunk configuration
│   │   ├── sms.py           # SMS confirmation/fallback
│   │   └── voicemail.py     # Voicemail detection + message
│   ├── call_manager.py      # NEW: Call lifecycle management
│   └── config.py            # Updated: Twilio config
├── api/
│   ├── __init__.py
│   ├── server.py            # FastAPI server for triggering calls
│   └── routes/
│       ├── calls.py         # POST /calls/initiate, GET /calls/{id}/status
│       └── webhooks.py      # Twilio status webhooks
├── requirements.txt         # Updated
└── .env.example             # Updated
```

**Key Design Decisions:**

1. **LiveKit SIP Trunk** — Bridge between Twilio and LiveKit:
   - Configure LiveKit SIP trunk to accept Twilio PSTN calls
   - Outbound: API triggers Twilio call → connects to LiveKit room → agent joins room
   - Use LiveKit's SIP participant events to detect call answered/voicemail/no-answer

2. **Call Lifecycle:**
   ```
   INITIATED → RINGING → ANSWERED → IN_PROGRESS → COMPLETED/FAILED/ESCALATED
   ```
   - Track state transitions
   - Handle: no-answer (retry later), voicemail (leave message + SMS), busy (callback)

3. **Voicemail Detection:**
   - Use Twilio's AMD (Answering Machine Detection)
   - If voicemail: play brief message via TTS, send SMS with details
   - If human: proceed with agent conversation

4. **SMS Confirmation:**
   - After successful booking: send confirmation with date, time, facility, address
   - After failed call: send SMS with callback number or booking link
   - Template-based with driver name and appointment details

5. **Outbound Call API:**
   ```
   POST /calls/initiate
   {
     "driver_id": "DRV-123",
     "driver_phone": "+1555...",
     "driver_name": "Mike Johnson",
     "truck_number": "T-4521",
     "call_purpose": "reschedule",
     "appointment_id": "APT-456",
     "context": { ... }
   }
   ```

### Validation Gate — Phase 3

| # | Test | Pass Criteria |
|---|------|---------------|
| 1 | Trigger outbound call to personal phone | Phone rings, caller ID shows company number |
| 2 | Answer call, complete scheduling conversation | Full happy path works over real phone |
| 3 | Let call go to voicemail | Agent detects voicemail, leaves message, sends SMS |
| 4 | Test with road noise (in car / play truck noise) | Conversation completes despite noise |
| 5 | Hang up mid-conversation | System detects drop, logs incomplete call |
| 6 | Receive SMS confirmation after booking | SMS arrives within 10s with correct details |
| 7 | Call quality assessment | Audio is clear both directions, no echo, no cutting out |
| 8 | Trigger call via API endpoint | POST request successfully initiates call |

**How to test:** Use your personal phone. Drive around or play truck cabin noise. Test from different signal strengths (strong LTE vs spotty). Have a friend test to get a second perspective on voice quality.

---

## Phase 4: RAG + Conflict Resolution + Fallback System

### Goal
Add the intelligence layer: RAG over scheduling policies, smart conflict resolution, and the tiered fallback system (SMS → callback → human transfer).

### What We Build

```
LLM Agent
    → Tool: query_policies(question) → RAG retrieval
    → Tool: check_conflicts(driver_id, proposed_time) → conflict analysis
    → Tool: escalate_to_human(reason, context) → warm transfer
    → Tool: schedule_callback(driver_id, preferred_time) → callback queue
    → Tool: send_sms_fallback(driver_id, message) → SMS with details
```

### Implementation Details

**New/Modified Files:**
```
appointment-agent/
├── agent/
│   ├── tools/
│   │   ├── rag.py           # NEW: RAG query tool
│   │   ├── escalation.py    # NEW: Fallback/escalation tools
│   │   └── calendar.py      # Updated: conflict detection
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── indexer.py       # Index policy documents
│   │   ├── retriever.py     # Semantic search over policies
│   │   └── documents/       # Source policy docs (markdown)
│   ├── fallback/
│   │   ├── __init__.py
│   │   ├── manager.py       # Fallback state machine
│   │   ├── sms.py           # SMS fallback handler
│   │   ├── callback.py      # Callback scheduling
│   │   └── transfer.py      # Warm transfer to human
│   └── prompts/
│       └── system.py        # Updated: add policy awareness + fallback instructions
├── data/
│   └── policies/            # Scheduling policy documents
│       ├── facility_hours.md
│       ├── booking_rules.md
│       ├── cancellation_policy.md
│       └── driver_eligibility.md
```

**Key Design Decisions:**

1. **RAG Implementation:**
   - Embeddings: OpenAI text-embedding-3-small (cost effective, good quality)
   - Vector store: pgvector (PostgreSQL extension) or ChromaDB for POC
   - Chunk size: 500 tokens with 100 token overlap
   - Retrieval: top-3 chunks, similarity threshold > 0.7
   - Documents: scheduling policies, facility info, FAQ

2. **Conflict Resolution Logic:**
   ```
   IF requested_slot is available:
       book immediately
   ELIF alternative_slots exist within ±2 hours:
       propose up to 3 alternatives
   ELIF alternative_slots exist on same day:
       propose day alternatives
   ELIF waitlist is available:
       offer waitlist placement
   ELSE:
       escalate to human dispatcher
   ```

3. **Tiered Fallback State Machine:**
   ```
   NORMAL → LOW_CONFIDENCE → SMS_FALLBACK → CALLBACK → HUMAN_TRANSFER
   
   Triggers:
   - 3 consecutive low-confidence ASR results → SMS_FALLBACK
   - Driver says "I can't hear you" / "what?" 3x → SMS_FALLBACK
   - Driver says "talk to someone" / "real person" → HUMAN_TRANSFER
   - Driver says "call me back" → CALLBACK
   - Agent can't resolve after 2 conflict rounds → HUMAN_TRANSFER
   ```

4. **Warm Transfer:**
   - Add human dispatcher to LiveKit room
   - Agent provides context summary to dispatcher (via text sidebar)
   - Agent stays briefly to introduce: "I'm connecting you with [Dispatcher]. They have all the details."
   - Then agent leaves room

### Validation Gate — Phase 4

| # | Test | Pass Criteria |
|---|------|---------------|
| 1 | Ask about facility hours | Agent retrieves correct info from RAG, answers naturally |
| 2 | Ask about cancellation policy | Agent cites policy accurately |
| 3 | Request slot that's taken | Agent proposes alternatives smoothly |
| 4 | All alternatives rejected | Agent offers waitlist, then escalation |
| 5 | Simulate noisy environment (3 failed ASR) | Agent triggers SMS fallback gracefully |
| 6 | Say "let me talk to a real person" | Warm transfer initiates (or simulated for POC) |
| 7 | Say "call me back in an hour" | Callback scheduled, confirmation given |
| 8 | Complex scheduling conflict | Agent resolves without confusing the driver |

**How to test:** Prepare test policy documents. Simulate conflicts by pre-booking calendar slots. Test fallback triggers by mumbling or playing loud noise. Verify SMS arrives for fallback scenarios.

---

## Phase 5: Langfuse Observability

### Goal
Full conversation tracing, latency monitoring, cost tracking, and quality metrics for every call.

### What We Build

```
Every call generates:
    → Langfuse Trace (full conversation lifecycle)
        → Span: call_setup (Twilio → LiveKit connection time)
        → Span: each turn
            → Generation: STT (Deepgram result + confidence + latency)
            → Generation: LLM (prompt + completion + tool calls + latency + cost)
            → Generation: TTS (text input + audio duration + latency)
        → Span: call_outcome (success/escalated/failed + reason)
    → Scores: completion_rate, escalation_rate, driver_sentiment, noise_level
```

### Implementation Details

**New/Modified Files:**
```
appointment-agent/
├── agent/
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── tracer.py        # Langfuse trace/span management
│   │   ├── metrics.py       # Custom metrics computation
│   │   └── decorators.py    # @traced decorator for tool calls
│   ├── pipeline.py          # Updated: instrument each stage
│   └── config.py            # Updated: Langfuse config
```

**Key Metrics to Track:**

| Metric | How | Why |
|--------|-----|-----|
| STT latency | Time from speech end to transcript available | Pipeline bottleneck detection |
| LLM latency | Time from prompt sent to completion received | Model selection decisions |
| TTS latency | Time from text sent to first audio byte | User experience |
| End-to-end latency | Speech end → TTS audio starts playing | Primary UX metric |
| ASR confidence | Deepgram confidence score per utterance | Noise impact measurement |
| Tool call success rate | Calendar API success/failure | Integration health |
| Conversation turns | Turns per successful booking | Efficiency tracking |
| Escalation rate | % of calls needing human | Agent quality |
| Call completion rate | % of calls achieving stated goal | Overall success |
| Cost per call | LLM tokens + STT minutes + TTS characters | Unit economics |

### Validation Gate — Phase 5

| # | Test | Pass Criteria |
|---|------|---------------|
| 1 | Complete a call, check Langfuse dashboard | Full trace visible with all spans |
| 2 | Verify latency measurements | Each component latency captured accurately |
| 3 | Check cost tracking | Token/character/minute costs logged per call |
| 4 | Trigger escalation, verify trace | Escalation reason and context captured |
| 5 | Run 10 test calls | Aggregate metrics visible (avg latency, success rate) |
| 6 | Filter traces by outcome | Can find failed/escalated calls quickly |

**How to test:** Run several calls of varying quality (clean audio, noisy, escalation, success). Verify all data appears in Langfuse. Build a simple Langfuse dashboard view.

---

## Phase 6: Dispatcher Dashboard

### Goal
Web UI for dispatchers to monitor live calls, review transcripts, override appointments, and view analytics.

### What We Build

```
Next.js Dashboard
├── Live Calls View (real-time active calls with status)
├── Call History (transcripts, audio playback, outcomes)
├── Appointment Override (manual reschedule/cancel/book)
├── Analytics (completion rate, escalation rate, avg call duration)
└── Driver Lookup (search driver, see their call history)
```

### Implementation Details

**Project Structure:**
```
appointment-agent/
├── dashboard/
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Dashboard home (live calls)
│   │   │   ├── calls/
│   │   │   │   ├── page.tsx          # Call history list
│   │   │   │   └── [id]/page.tsx     # Single call detail (transcript + audio)
│   │   │   ├── appointments/
│   │   │   │   └── page.tsx          # Appointment management
│   │   │   ├── analytics/
│   │   │   │   └── page.tsx          # Metrics dashboard
│   │   │   └── drivers/
│   │   │       └── [id]/page.tsx     # Driver profile + history
│   │   ├── components/
│   │   │   ├── LiveCallCard.tsx      # Real-time call status card
│   │   │   ├── TranscriptViewer.tsx  # Turn-by-turn transcript
│   │   │   ├── AudioPlayer.tsx       # Call audio playback
│   │   │   └── MetricsChart.tsx      # Analytics charts
│   │   └── lib/
│   │       ├── api.ts               # Backend API client
│   │       └── websocket.ts         # Real-time call updates
│   └── tailwind.config.js
├── api/
│   ├── routes/
│   │   ├── dashboard.py             # Dashboard-specific endpoints
│   │   └── websocket.py             # WebSocket for live updates
```

**Key Features:**

1. **Live Calls View:**
   - WebSocket connection for real-time updates
   - Card per active call: driver name, duration, current state, sentiment indicator
   - "Listen in" button (join LiveKit room as observer)
   - "Take over" button (warm transfer to dispatcher)

2. **Call History:**
   - Filterable by: date, outcome, driver, duration, escalation
   - Each call shows: transcript, audio, tool calls made, Langfuse trace link
   - Export capability (CSV)

3. **Appointment Override:**
   - Search appointments by driver/date/facility
   - Manual book/reschedule/cancel with reason
   - Triggers outbound call to confirm with driver (optional)

4. **Analytics:**
   - Daily/weekly call volume
   - Success/escalation/failure rates
   - Average call duration and turns
   - Top failure reasons
   - Cost per call trend

### Validation Gate — Phase 6

| # | Test | Pass Criteria |
|---|------|---------------|
| 1 | Start a call, see it appear in Live Calls | Real-time card appears within 2s |
| 2 | Call completes, appears in history | Transcript and outcome visible |
| 3 | Play back call audio | Audio player works, synced with transcript |
| 4 | Override an appointment | Calendar updated, change reflected in dashboard |
| 5 | View analytics after 10+ calls | Charts render with accurate data |
| 6 | "Take over" a live call | Dispatcher joins, agent introduces and exits |
| 7 | Filter call history | Filters work correctly (date, outcome, driver) |

**How to test:** Run the dashboard locally. Trigger several test calls. Verify real-time updates. Test override flows against Google Calendar. Have someone else use the dashboard while you make test calls.

---

## Phase-by-Phase Summary

| Phase | Duration | Depends On | Key Risk |
|-------|----------|-----------|----------|
| 1: Voice Pipeline | 3-4 days | API keys for LiveKit, Deepgram, ElevenLabs | VAD tuning for noise |
| 2: LLM + Tools | 3-4 days | Phase 1 + Google Calendar service account | Latency budget (LLM + tool call) |
| 3: Twilio | 3-4 days | Phase 2 + Twilio account + SIP trunk setup | Audio quality over PSTN |
| 4: RAG + Fallback | 4-5 days | Phase 3 + policy documents + vector DB | Retrieval relevance |
| 5: Langfuse | 2-3 days | Phase 4 + Langfuse account | Instrumentation overhead on latency |
| 6: Dashboard | 5-6 days | Phase 5 (needs data to display) | Real-time WebSocket reliability |

**Total: ~22-26 working days (4 weeks with buffer)**

---

## Prerequisites (Before Phase 1)

- [ ] LiveKit Cloud account or self-hosted server
- [ ] Deepgram API key
- [ ] ElevenLabs API key
- [ ] Google Cloud project with Calendar API enabled + service account
- [ ] Twilio account with phone number + SIP trunk capability
- [ ] Langfuse account (cloud or self-hosted)
- [ ] Python 3.11+ environment
- [ ] Node.js 18+ (for dashboard)
- [ ] PostgreSQL (for call records + vector storage)
