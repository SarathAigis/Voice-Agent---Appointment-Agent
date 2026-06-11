"""Voice pipeline with GPT-4o LLM, Google Calendar, and Twilio integration."""

import structlog
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, elevenlabs, openai, silero

from .config import config
from .prompts.system import SCHEDULING_AGENT_SYSTEM_PROMPT
from .tools import calendar
from .telephony import get_sms_service

logger = structlog.get_logger(__name__)


class AppointmentContext:
    """Track appointment context during the conversation."""

    def __init__(self):
        self.driver_id: str | None = None
        self.driver_name: str | None = None
        self.driver_phone: str | None = None
        self.truck_number: str | None = None
        self.verified: bool = False
        self.current_appointment_id: str | None = None
        self.call_purpose: str | None = None
        self.call_sid: str | None = None


async def create_voice_pipeline(
    ctx: JobContext, call_context: AppointmentContext
) -> VoicePipelineAgent:
    """
    Create and configure the voice pipeline agent with GPT-4o and Twilio integration.

    Args:
        ctx: LiveKit job context
        call_context: Appointment context for this call

    Returns:
        Configured voice pipeline agent
    """

    # Initialize STT (Speech-to-Text) with Deepgram
    stt = deepgram.STT(
        model=config.deepgram_model,
        language=config.deepgram_language,
        smart_format=config.deepgram_smart_format,
        interim_results=config.deepgram_interim_results,
        endpointing=config.deepgram_endpointing,
        utterance_end_ms=config.deepgram_utterance_end_ms,
    )

    # Initialize TTS (Text-to-Speech) with ElevenLabs
    tts = elevenlabs.TTS(
        model_id=config.elevenlabs_model,
        voice_id=config.elevenlabs_voice_id,
        stability=config.elevenlabs_stability,
        similarity_boost=config.elevenlabs_similarity_boost,
    )

    # Initialize GPT-4o LLM
    gpt4o_llm = openai.LLM(
        model=config.llm_model,
        temperature=config.llm_temperature,
    )

    # Setup chat context
    initial_context = llm.ChatContext()
    initial_context.messages.append(
        llm.ChatMessage(
            role="system",
            content=SCHEDULING_AGENT_SYSTEM_PROMPT,
        )
    )

    # Add call context
    if call_context.driver_name and call_context.call_purpose:
        context_msg = f"You are calling {call_context.driver_name} (Truck: {call_context.truck_number or 'Unknown'}, Phone: {call_context.driver_phone}) regarding: {call_context.call_purpose}"
        initial_context.messages.append(
            llm.ChatMessage(
                role="system",
                content=context_msg,
            )
        )

    # Create the voice pipeline agent with GPT-4o
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(
            min_speech_duration=config.vad_min_speech_duration,
            min_silence_duration=config.vad_silence_duration,
            activation_threshold=config.vad_energy_threshold,
            deactivation_threshold=config.vad_energy_threshold * 0.8,
        ),
        stt=stt,
        llm=gpt4o_llm,
        tts=tts,
        chat_ctx=initial_context,
        allow_interruptions=True,
        min_endpointing_delay=200,
        fnc_ctx=llm.FunctionContext(),
    )

    # Get SMS service for confirmations
    sms_service = get_sms_service()

    # Register calendar tools (same as Phase 2)
    @agent.function("check_availability")
    async def check_availability_tool(
        date: str,
        facility: str,
        appointment_type: str,
        duration_minutes: int = 30,
    ):
        """Check available time slots for appointments."""
        from .tools.schemas import AppointmentType, AvailabilityRequest

        logger.info("checking_availability", date=date, facility=facility)

        try:
            apt_type = AppointmentType(appointment_type.lower())
            request = AvailabilityRequest(
                date=date,
                facility=facility,
                appointment_type=apt_type,
                duration_minutes=duration_minutes,
            )

            slots = calendar.check_availability(request)

            if not slots:
                return "No available slots found for that date. Would you like to try a different date?"

            slot_descriptions = []
            for slot in slots[:3]:
                time_str = slot.start_time.strftime("%I:%M %p")
                slot_descriptions.append(f"{time_str}")

            return f"I have availability at: {', '.join(slot_descriptions[:-1]) + ' or ' + slot_descriptions[-1] if len(slot_descriptions) > 1 else slot_descriptions[0]}"

        except Exception as e:
            logger.error("availability_check_failed", error=str(e))
            return "I'm having trouble checking availability right now."

    @agent.function("book_appointment")
    async def book_appointment_tool(
        appointment_type: str,
        facility: str,
        start_time: str,
        duration_minutes: int = 30,
        notes: str = "",
    ):
        """Book a new appointment."""
        from .tools.schemas import AppointmentType, BookingRequest
        from datetime import datetime

        logger.info("booking_appointment", driver=call_context.driver_name, facility=facility)

        try:
            if not call_context.driver_id or not call_context.driver_name:
                return "I need to verify your information first."

            apt_type = AppointmentType(appointment_type.lower())
            request = BookingRequest(
                driver_id=call_context.driver_id,
                driver_name=call_context.driver_name,
                truck_number=call_context.truck_number or "Unknown",
                appointment_type=apt_type,
                facility=facility,
                start_time=start_time,
                duration_minutes=duration_minutes,
                notes=notes,
            )

            appointment = calendar.book_appointment(request)
            call_context.current_appointment_id = appointment.id

            # Send SMS confirmation
            date_str = appointment.start_time.strftime("%A, %B %d")
            time_str = appointment.start_time.strftime("%I:%M %p")

            if call_context.driver_phone and config.twilio_enable_sms:
                sms_service.send_appointment_confirmation(
                    phone=call_context.driver_phone,
                    driver_name=call_context.driver_name,
                    appointment_type=appointment_type,
                    facility=facility,
                    date=date_str,
                    time=time_str,
                )

            return f"Done! I've booked your {appointment_type} at {facility} for {date_str} at {time_str}. You'll get a text confirmation."

        except Exception as e:
            logger.error("booking_failed", error=str(e))
            return "I wasn't able to book that appointment."

    @agent.function("list_appointments")
    async def list_appointments_tool(days_ahead: int = 30):
        """List upcoming appointments for the driver."""
        logger.info("listing_appointments", driver=call_context.driver_name)

        try:
            if not call_context.driver_id:
                return "I need to verify your identity first."

            appointments = calendar.list_appointments(call_context.driver_id, days_ahead)

            if not appointments:
                return "You don't have any upcoming appointments."

            apt_list = []
            for apt in appointments[:3]:
                date_str = apt.start_time.strftime("%A, %B %d")
                time_str = apt.start_time.strftime("%I:%M %p")
                apt_list.append(
                    f"{apt.appointment_type.value} at {apt.facility} on {date_str} at {time_str}"
                )

            if len(appointments) > 3:
                apt_list.append(f"and {len(appointments) - 3} more")

            return "Your upcoming appointments: " + "; ".join(apt_list)

        except Exception as e:
            logger.error("list_appointments_failed", error=str(e))
            return "I'm having trouble accessing your appointments."

    @agent.function("cancel_appointment")
    async def cancel_appointment_tool(appointment_id: str, reason: str = ""):
        """Cancel an appointment."""
        from .tools.schemas import CancelRequest

        logger.info("canceling_appointment", appointment_id=appointment_id)

        try:
            request = CancelRequest(appointment_id=appointment_id, reason=reason)
            success = calendar.cancel_appointment(request)

            if success:
                # Send SMS confirmation
                if call_context.driver_phone and config.twilio_enable_sms:
                    sms_service.send_cancellation_confirmation(
                        phone=call_context.driver_phone,
                        driver_name=call_context.driver_name or "there",
                        appointment_type="appointment",
                        date="the scheduled",
                        time="time",
                    )

                return "Your appointment has been cancelled. You'll get a text confirmation."
            else:
                return "I wasn't able to cancel that appointment."

        except Exception as e:
            logger.error("cancel_failed", error=str(e))
            return "I had trouble cancelling that."

    # Start the pipeline
    agent.start(ctx.room)

    logger.info(
        "voice_pipeline_created_phase3",
        room=ctx.room.name,
        driver=call_context.driver_name,
        call_sid=call_context.call_sid,
    )

    # Initial greeting
    if call_context.driver_name:
        greeting = f"Hi {call_context.driver_name}, this is the scheduling assistant. Am I speaking with {call_context.driver_name}?"
    else:
        greeting = "Hi, this is the scheduling assistant. Can I get your name?"

    await agent.say(greeting)

    return agent


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the LiveKit agent with Twilio integration.
    This is called when a call connects via Twilio.
    """
    logger.info(
        "agent_started_phase3",
        room=ctx.room.name,
        participants=len(ctx.room.remote_participants),
    )

    # Wait for a participant to join
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Log participant connection
    participant = await ctx.wait_for_participant()
    logger.info(
        "participant_connected",
        participant_identity=participant.identity,
        participant_sid=participant.sid,
    )

    # Create call context
    # In production, this would be populated from the API call that triggered this
    # For now, parse from room name or metadata
    call_context = AppointmentContext()

    # Extract call context from room metadata if available
    room_metadata = ctx.room.metadata
    if room_metadata:
        import json

        try:
            metadata = json.loads(room_metadata)
            call_context.driver_id = metadata.get("driver_id")
            call_context.driver_name = metadata.get("driver_name")
            call_context.driver_phone = metadata.get("driver_phone")
            call_context.truck_number = metadata.get("truck_number")
            call_context.call_purpose = metadata.get("call_purpose")
            call_context.call_sid = metadata.get("call_sid")
        except json.JSONDecodeError:
            logger.warning("invalid_room_metadata", metadata=room_metadata)

    # Fallback to test data if no metadata
    if not call_context.driver_name:
        call_context.driver_id = "DRV-TEST-001"
        call_context.driver_name = "Mike"
        call_context.driver_phone = "+1234567890"
        call_context.truck_number = "T-4521"
        call_context.call_purpose = "appointment scheduling"

    # Create and start the voice pipeline
    agent = await create_voice_pipeline(ctx, call_context)

    # Keep the agent running until the room closes
    await agent.join()

    # Cleanup after call ends
    logger.info(
        "call_ended",
        room=ctx.room.name,
        driver=call_context.driver_name,
        call_sid=call_context.call_sid,
    )


if __name__ == "__main__":
    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ]
    )

    # Run the agent with LiveKit CLI
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=config.livekit_api_key,
            api_secret=config.livekit_api_secret,
            ws_url=config.livekit_url,
        )
    )
