# Voice Agent for Truck Driver Appointment Scheduling — Scope Document

## Context

Truck drivers need to manage multiple appointment types (delivery/dock slots, maintenance, compliance) while on the road in noisy environments. The current process requires manual calls or app interaction — both impractical while driving. This voice agent will proactively call drivers to schedule, confirm, and reschedule appointments via natural conversation, handling background noise (road, CB radio, wind) gracefully.

---

## Problem Statement

- Drivers miss or mismanage appointments because they can't interact with scheduling tools while driving
- Background noise on calls (engine, highway, radio) causes ASR failures and frustration
- Current scheduling workflows require too many steps for a hands-free interaction
- No intelligent fallback when automated systems fail in noisy conditions

---

## System Architecture

### Core Pipeline

```
Twilio (outbound calls)
    → LiveKit (real-time audio transport + room management)
        → Silero VAD (voice activity detection — critical for noisy environments)
            → Deepgram (STT with noise-robust models)
                → LLM Agent (Claude/GPT-4o — conversation + tool calling)
                    → ElevenLabs (TTS — natural, human-like voice)
                        → LiveKit → Twilio → Driver
```

### Component Responsibilities

| Component | Role | Why This Choice |
|-----------|------|-----------------|
| **Twilio** | Outbound calling, phone number management, SMS fallback | Industry standard telephony, reliable outbound dialing |
| **LiveKit** | Real-time audio transport, WebRTC rooms, agent orchestration | Low-latency media server, native Python agent framework |
| **Silero VAD** | Voice activity detection, endpointing | Lightweight, fast, works well with noisy audio — critical for trucking environment |
| **Deepgram** | Speech-to-text | Best-in-class noise handling, low latency streaming, punctuation/formatting |
| **LLM (Claude/GPT-4o)** | Conversation orchestration, intent recognition, tool calling | Tool calling for scheduling, natural conversation flow |
| **ElevenLabs** | Text-to-speech | Most natural-sounding voices, low latency streaming, conversational tone |
| **Langfuse** | Observability, tracing, analytics | Full conversation traces, latency monitoring, cost tracking |
| **Google Calendar** | Appointment backend | Integration for scheduling, availability checking, conflict detection |

---

## Functional Scope (POC — 4 weeks)

### Week 1-2: Core Voice Pipeline

1. **Outbound Call Initiation**
   - Twilio outbound call triggered by scheduling system
   - Call connects to LiveKit room with agent
   - Graceful handling of voicemail/no-answer

2. **Noise-Robust Audio Processing**
   - Silero VAD tuned for high-noise environments (aggressive endpointing thresholds)
   - Deepgram STT with enhanced noise cancellation model
   - Confidence-based repeat/clarification ("I didn't catch that — could you repeat the date?")

3. **Driver Identity Verification**
   - System knows who it's calling (outbound)
   - Verbal verification: "Hi, am I speaking with [Name]? Can you confirm your truck number?"
   - Fallback to DOB or company ID if name match fails

4. **Appointment Scheduling Conversation**
   - Natural, concise dialogue (drivers are busy)
   - Support flows:
     - New appointment booking
     - Appointment confirmation/reminder
     - Rescheduling
     - Cancellation
   - Multiple appointment types: delivery slots, maintenance, compliance

### Week 2-3: Intelligence Layer

5. **LLM Agent with Tool Calling**
   - Google Calendar integration (check availability, create/update/delete events)
   - RAG over scheduling rules/policies (facility hours, booking windows, cancellation policies)
   - Conflict resolution logic:
     1. Propose alternative slots
     2. Offer waitlist placement
     3. Escalate to human dispatcher

6. **Conversation Design for Truck Drivers**
   - Short, direct utterances (no verbose explanations)
   - Confirmation by repetition ("So that's Thursday at 2pm at the Denver facility — correct?")
   - Graceful interruption handling (driver may need to respond to road events)
   - Barge-in support (driver can interrupt the agent mid-sentence)

7. **Tiered Fallback System**
   - Level 1: Repeat/rephrase on low confidence ASR
   - Level 2: SMS follow-up with appointment details/link
   - Level 3: Schedule callback from human dispatcher
   - Level 4: Live warm transfer to dispatcher

### Week 3-4: Observability & Admin

8. **Langfuse Integration**
   - Full conversation trace (STT text, LLM reasoning, TTS output)
   - Latency tracking per component (STT → LLM → TTS)
   - Cost per call tracking
   - Conversation quality metrics (completion rate, fallback rate, repeat rate)

9. **Dispatcher Dashboard**
   - Real-time active call monitoring
   - Transcript review with audio playback
   - Manual appointment override
   - Call outcome analytics (completed, escalated, failed)
   - Driver sentiment indicators

---

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| End-to-end latency (driver speaks → agent responds) | < 1.5 seconds |
| Call capacity | 50-500 concurrent calls/day |
| ASR accuracy in noisy environment | > 85% WER |
| Successful appointment completion rate | > 70% without escalation |
| Uptime | 99.5% during business hours |

---

## RAG Knowledge Base (POC Scope)

- Facility hours and booking windows
- Appointment type rules (lead time, cancellation policies)
- Driver eligibility constraints
- Rescheduling policies
- Common FAQ (what to bring, where to go, contact numbers)

Storage: Vector DB (e.g., Pinecone or pgvector) with embeddings, queried via tool call from the LLM agent.

---

## Call Flow (Happy Path)

```
1. System triggers outbound call via Twilio
2. Twilio connects → LiveKit room created with agent
3. Agent: "Hi, this is [Company] calling for [Driver Name]. Am I speaking with [Name]?"
4. Driver confirms identity (truck number verification)
5. Agent: "I'm calling about your delivery appointment at [Facility] on [Date]. Does that still work for you?"
6. Driver: "Nah, I'm running behind. Can we push it to Thursday?"
7. Agent checks Google Calendar availability via tool call
8. Agent: "Thursday I have 10am or 2pm open at Denver. Which works better?"
9. Driver: "2pm"
10. Agent books slot, confirms: "Done — Thursday 2pm at Denver. You'll get a text confirmation. Anything else?"
11. Driver: "Nope, thanks"
12. Agent: "Safe travels. Bye."
13. SMS confirmation sent via Twilio
```

---

## Edge Cases to Handle

| Scenario | Handling |
|----------|----------|
| Driver can't hear (tunnel, loud noise) | Pause, ask "Can you hear me?", retry 2x, then SMS fallback |
| Voicemail reached | Leave brief message + send SMS |
| Driver says "call back later" | Schedule callback, confirm time |
| Multiple schedule conflicts | Present max 3 options, don't overwhelm |
| Driver asks out-of-scope question | Acknowledge, redirect to scheduling, offer dispatcher transfer |
| Call drops mid-conversation | Callback within 2 minutes, resume context |
| Driver is agitated/frustrated | Acknowledge frustration, offer human transfer immediately |

---

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Telephony | Twilio (outbound calls + SMS) |
| Media Transport | LiveKit (WebRTC rooms, agent framework) |
| VAD | Silero (noise-robust voice activity detection) |
| STT | Deepgram (Nova-2, streaming, enhanced noise model) |
| LLM | Claude or GPT-4o (selected per latency/quality benchmarks) |
| TTS | ElevenLabs (Turbo v2, conversational voice) |
| Scheduling Backend | Google Calendar API |
| RAG | Vector DB + embeddings (scheduling policies) |
| Observability | Langfuse (traces, metrics, cost) |
| Admin Dashboard | Next.js or similar (call monitoring, transcripts, overrides) |
| Language | Python (LiveKit Agents SDK) |

---

## Out of Scope (POC)

- Multi-language support (English only)
- Inbound calls (outbound only for POC)
- Custom TMS/ERP integrations (Google Calendar only)
- Mobile app for drivers
- Automated quality scoring / LLM-as-judge
- Load testing beyond 500 calls/day

---

## Success Criteria (POC)

1. Complete an end-to-end outbound call that books an appointment in Google Calendar
2. Handle at least 3 noise scenarios without breaking conversation flow
3. Successfully execute tiered fallback (SMS → callback → human transfer)
4. Full Langfuse trace visibility for every call
5. Dispatcher dashboard shows live calls and allows override
6. < 1.5s average response latency in quiet conditions, < 2.5s in noisy conditions

---

## Deliverables

1. **LiveKit Agent** — Python service handling voice pipeline orchestration
2. **LLM Agent Logic** — Conversation management, tool calling, scheduling flows
3. **RAG Service** — Policy/rules retrieval for contextual answers
4. **Twilio Integration** — Outbound calling, SMS fallback, callback scheduling
5. **Dispatcher Dashboard** — Web UI for monitoring and overrides
6. **Langfuse Setup** — Full observability pipeline
7. **Documentation** — Setup guide, conversation flow diagrams, deployment instructions
