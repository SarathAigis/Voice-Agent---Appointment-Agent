# System Architecture

## Overview

Voice agent for truck driver appointment scheduling, optimized for high-noise environments (road, engine, CB radio). Designed for outbound calls with natural conversation flow.

---

## Phase 1: Voice Pipeline (Current)

```
┌─────────────────────────────────────────────────────────────┐
│                        Phase 1 Flow                          │
└─────────────────────────────────────────────────────────────┘

  User Microphone
       │
       ▼
┌──────────────┐
│   LiveKit    │  ← WebRTC Transport
│   Browser    │    (Playground or Custom Client)
└──────┬───────┘
       │ Audio Stream (WebRTC)
       ▼
┌──────────────┐
│   LiveKit    │  ← Real-time Media Server
│    Server    │    (Cloud or Self-hosted)
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│              Voice Pipeline Agent (Python)                │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  1. Silero VAD (Voice Activity Detection)         │  │
│  │     • Detects speech start/end                     │  │
│  │     • Tuned for noise: 700ms silence, 0.5 thresh  │  │
│  │     • Prevents false triggers                      │  │
│  └────────────┬───────────────────────────────────────┘  │
│               ▼                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  2. Deepgram STT (Speech-to-Text)                 │  │
│  │     • Model: nova-2 (noise-robust)                │  │
│  │     • Streaming transcription                      │  │
│  │     • Confidence scoring                           │  │
│  └────────────┬───────────────────────────────────────┘  │
│               ▼                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  3. Simple Response Logic (Phase 1)               │  │
│  │     • Echo back user message                       │  │
│  │     • (Replaced with LLM in Phase 2)              │  │
│  └────────────┬───────────────────────────────────────┘  │
│               ▼                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  4. ElevenLabs TTS (Text-to-Speech)               │  │
│  │     • Model: eleven_turbo_v2                      │  │
│  │     • Voice: Rachel (professional female)         │  │
│  │     • Streaming audio generation                   │  │
│  └────────────┬───────────────────────────────────────┘  │
│               │                                           │
└───────────────┼───────────────────────────────────────────┘
                ▼
        LiveKit Server
                │
                ▼
        User Speaker
```

---

## Complete Architecture (All Phases)

```
┌────────────────────────────────────────────────────────────────┐
│                      Full System (Phase 6)                      │
└────────────────────────────────────────────────────────────────┘

                            ┌──────────────┐
                            │   Trigger    │
                            │ (API/Cron)   │
                            └──────┬───────┘
                                   │
                                   ▼
                       ┌───────────────────────┐
                       │   Twilio Outbound     │  Phase 3
                       │      Call API         │
                       └───────────┬───────────┘
                                   │
                       Phone Call  │
                                   ▼
                       ┌───────────────────────┐
                       │  Driver's Phone       │
                       │  (Truck Cabin Noise)  │
                       └───────────┬───────────┘
                                   │
                           PSTN    │
                                   ▼
                       ┌───────────────────────┐
                       │   Twilio SIP Trunk    │  Phase 3
                       └───────────┬───────────┘
                                   │
                                   ▼
                       ┌───────────────────────┐
                       │   LiveKit Server      │
                       │   (Media Transport)   │
                       └───────────┬───────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│  Voice Agent   │      │   Dispatcher   │      │   Dashboard    │
│   (Python)     │      │  (Warm Trans.) │      │   (Next.js)    │
└───────┬────────┘      └────────────────┘      └────────────────┘
        │                                              Phase 6
        │
        │  ┌──────────────────────────────────────────────┐
        └─▶│         Voice Pipeline                        │
           │                                               │
           │  Silero VAD → Deepgram STT → LLM → 11Labs TTS │
           └───────────────────┬───────────────────────────┘
                               │
                               ▼
           ┌────────────────────────────────────────────────┐
           │              LLM Agent (Phase 2)               │
           │                                                │
           │  Claude Sonnet or GPT-4o                       │
           │  • Conversation orchestration                  │
           │  • Intent recognition                          │
           │  • Tool calling                                │
           │  • Context management                          │
           └──────┬─────────────────────────────────────────┘
                  │
                  │ Tool Calls
                  │
    ┌─────────────┼─────────────┬─────────────┬────────────┐
    ▼             ▼             ▼             ▼            ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
│Google  │  │   RAG    │  │ Escalate │  │ Callback │  │  SMS   │
│Calendar│  │ Policies │  │  Human   │  │  Queue   │  │Fallback│
└────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘
  Phase 2     Phase 4       Phase 4       Phase 4      Phase 3

                               │
                               ▼
                    ┌─────────────────────┐
                    │  Langfuse Tracing   │  Phase 5
                    │  • Latency metrics  │
                    │  • Cost tracking    │
                    │  • Quality scores   │
                    └─────────────────────┘
```

---

## Component Details

### Phase 1: Voice Pipeline

| Component | Technology | Purpose | Configuration |
|-----------|-----------|---------|---------------|
| **VAD** | Silero VAD | Detect speech start/end in noisy env | 700ms silence, 0.5 threshold |
| **STT** | Deepgram Nova-2 | Speech-to-text transcription | Streaming, smart format |
| **TTS** | ElevenLabs Turbo v2 | Natural voice synthesis | Rachel voice, low latency |
| **Transport** | LiveKit | WebRTC media server | Cloud or self-hosted |

### Phase 2: LLM + Tools (Not Yet Implemented)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Claude Sonnet / GPT-4o | Conversation orchestration |
| **Calendar** | Google Calendar API | Appointment CRUD |
| **Context** | In-memory | Multi-turn conversation state |

### Phase 3: Telephony (Not Yet Implemented)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Outbound** | Twilio Voice API | Initiate calls to drivers |
| **SIP Trunk** | Twilio + LiveKit | PSTN ↔ WebRTC bridge |
| **SMS** | Twilio Messaging | Confirmations + fallback |
| **AMD** | Twilio Answering Machine Detection | Voicemail vs. human |

### Phase 4: Intelligence (Not Yet Implemented)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **RAG** | ChromaDB / pgvector | Policy retrieval |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic search |
| **Fallback** | State machine | Tiered escalation |

### Phase 5: Observability (Not Yet Implemented)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Tracing** | Langfuse | Full conversation traces |
| **Metrics** | Langfuse | Latency, cost, quality |

### Phase 6: Dashboard (Not Yet Implemented)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Next.js | Dispatcher UI |
| **Real-time** | WebSocket | Live call monitoring |
| **API** | FastAPI | Backend endpoints |

---

## Data Flow (Phase 1)

```
1. User speaks → Microphone captures audio
2. Audio → Browser → LiveKit (WebRTC)
3. LiveKit → Agent receives audio stream
4. Silero VAD detects speech boundaries
5. Audio chunk → Deepgram API (streaming)
6. Deepgram returns transcript text
7. Simple logic generates response text
8. Response text → ElevenLabs API
9. ElevenLabs returns audio stream
10. Audio → LiveKit → Browser → Speaker
```

**Latency Breakdown (Target):**
- VAD detection: ~100ms
- STT transcription: ~300-500ms
- LLM response (Phase 2): ~400-800ms
- TTS generation: ~200-400ms
- **Total: <1.5s** (Phase 1: <1s since no LLM)

---

## Data Flow (Phase 2+ - Future)

```
1. [Same as Phase 1 through STT]
2. Transcript → LLM Agent (Claude/GPT-4o)
3. LLM may call tools:
   - check_availability() → Google Calendar API
   - book_appointment() → Google Calendar API
   - query_policies() → RAG system (Phase 4)
   - escalate_to_human() → Warm transfer (Phase 4)
4. LLM generates response text
5. [Same as Phase 1 from TTS onward]
```

---

## Noise Handling Strategy

### Problem
Truck cabin environment:
- Engine noise: 70-85 dB
- Road noise: 75-90 dB
- CB radio: intermittent
- Wind noise: varies

### Solution

**1. VAD Tuning**
- Longer silence duration (700ms vs. default 400ms)
- Higher activation threshold (0.5 vs. default 0.3)
- Prevents false triggers from background noise

**2. STT Selection**
- Deepgram Nova-2: trained on noisy audio
- Smart formatting reduces transcription errors

**3. Confirmation Strategy**
- Agent repeats back critical info
- "So that's Thursday at 2pm - correct?"
- Allows error correction

**4. Fallback System (Phase 4)**
- Low confidence → repeat question
- Still unclear → SMS fallback
- Driver frustrated → human transfer

---

## Security Considerations

### Phase 1
- API keys in `.env` (not committed)
- No sensitive data stored yet

### Future Phases
- Google Calendar: Service account (no OAuth)
- Driver identity: Phone number + verbal verification
- Call recordings: Encrypted at rest
- Credentials: Environment variables + secrets manager

---

## Scalability

### Phase 1 (Current)
- Single agent process
- 1 concurrent call per agent instance
- Suitable for: Testing, POC

### Production (Phase 6)
- Multiple agent workers
- LiveKit Cloud auto-scales
- 50-500 calls/day target
- Horizontal scaling via Kubernetes (future)

---

## Cost Estimates

### Phase 1 Testing (per call)

| Service | Usage | Cost |
|---------|-------|------|
| LiveKit Cloud | 5 min audio | ~$0.01 |
| Deepgram STT | 5 min @ $0.0043/min | $0.02 |
| ElevenLabs TTS | 500 chars @ $0.03/1K | $0.015 |
| **Total** | | **~$0.045/call** |

### Production (Phase 6, per call)

Add:
- LLM (Claude): ~2K tokens @ $0.003/1K = $0.006
- Twilio outbound: 5 min @ $0.013/min = $0.065
- SMS confirmation: 1 SMS @ $0.0075 = $0.0075

**Total: ~$0.12-0.15/call**

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| End-to-end latency | <1.5s | TBD (needs testing) |
| STT accuracy (quiet) | >95% | TBD |
| STT accuracy (noisy) | >80% | TBD |
| Uptime | 99.5% | N/A (POC) |
| Concurrent calls | 50-500/day | 1 (dev) |

---

## Technology Choices

### Why LiveKit?
- Native Python Agents SDK
- Low-latency WebRTC transport
- Built-in voice pipeline abstractions
- SIP trunk support for Phase 3

### Why Deepgram?
- Best-in-class noise handling
- Low latency streaming
- Smart formatting (punctuation, capitalization)
- Generous free tier

### Why ElevenLabs?
- Most natural-sounding voices
- Turbo v2 model: <300ms latency
- Streaming support
- Conversational tone

### Why Claude Sonnet? (Phase 2)
- Excellent tool calling
- Long context (200K+)
- Fast inference
- Strong following of system prompts

### Alternative: GPT-4o
- Faster inference in some regions
- Similar tool calling quality
- Will benchmark both in Phase 2

---

## File Organization

```
agent/
├── main.py              # Entrypoint, CLI runner
├── pipeline.py          # Voice pipeline orchestration
├── config.py            # Configuration management
├── tools/               # Tool definitions (Phase 2+)
│   ├── calendar.py      # Google Calendar integration
│   ├── rag.py           # Policy retrieval
│   └── escalation.py    # Fallback handlers
├── prompts/             # LLM system prompts (Phase 2+)
│   └── system.py
├── telephony/           # Twilio integration (Phase 3+)
│   ├── outbound.py
│   ├── sip_trunk.py
│   └── sms.py
├── rag/                 # RAG system (Phase 4+)
│   ├── indexer.py
│   └── retriever.py
└── observability/       # Langfuse tracing (Phase 5+)
    └── tracer.py
```

---

## Next Steps

1. **Phase 1 Validation** (Current)
   - Test voice pipeline end-to-end
   - Measure latency and accuracy
   - Tune VAD for optimal performance

2. **Phase 2 Prep**
   - Get Claude API key
   - Set up Google Calendar service account
   - Write system prompt for scheduling agent

3. **Future Phases**
   - See [tactical-design.md](./tactical-design.md) for detailed plan

---

**Questions?** Check [GETTING_STARTED.md](./GETTING_STARTED.md) for setup or [PHASE1.md](./PHASE1.md) for testing.
