"""Voice pipeline with GPT-4o LLM and Google Calendar integration."""

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

logger = structlog.get_logger(__name__)


class AppointmentContext:
    """Track appointment context during the conversation."""

    def __init__(self):
        self.driver_id: str | None = None
        self.driver_name: str | None = None
        self.truck_number: str | None = None
        self.verified: bool = False
        self.current_appointment_id: str | None = None
        self.call_purpose: str | None = None


async def create_voice_pipeline(ctx: JobContext, call_context: AppointmentContext) -> VoicePipelineAgent:
    """
    Create and configure the voice pipeline agent with GPT-4o.

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

    # Define tools for the LLM
    # Note: We'll use function calling to handle tool execution
    initial_context = llm.ChatContext()
    initial_context.messages.append(
        llm.ChatMessage(
            role="system",
            content=SCHEDULING_AGENT_SYSTEM_PROMPT,
        )
    )

    # Add initial call context if available
    if call_context.driver_name and call_context.call_purpose:
        context_msg = f"You are calling {call_context.driver_name} (Truck: {call_context.truck_number or 'Unknown'}) regarding: {call_context.call_purpose}"
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
        # Allow interruption (barge-in) - critical for natural conversation
        allow_interruptions=True,
        # Minimum time before allowing interruption (ms)
        min_endpointing_delay=200,
        # Function calling for tools
        fnc_ctx=llm.FunctionContext(),
    )

    # Register calendar tools with the agent
    @agent.function("check_availability")
    async def check_availability_tool(
        date: str,
        facility: str,
        appointment_type: str,
        duration_minutes: int = 30,
    ):
        """
        Check available time slots for appointments.

        Args:
            date: Date in YYYY-MM-DD format
            facility: Facility name (e.g., "Denver Warehouse")
            appointment_type: Type of appointment - "delivery", "maintenance", or "compliance"
            duration_minutes: Appointment duration in minutes (default 30)
        """
        from .tools.schemas import AppointmentType, AvailabilityRequest

        logger.info(
            "checking_availability",
            date=date,
            facility=facility,
            type=appointment_type,
        )

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

            # Format slots for voice output
            slot_descriptions = []
            for i, slot in enumerate(slots[:3], 1):  # Max 3 options
                time_str = slot.start_time.strftime("%I:%M %p")
                slot_descriptions.append(f"{time_str}")

            return f"I have availability at: {', '.join(slot_descriptions[:-1]) + ' or ' + slot_descriptions[-1] if len(slot_descriptions) > 1 else slot_descriptions[0]}"

        except Exception as e:
            logger.error("availability_check_failed", error=str(e))
            return "I'm having trouble checking availability right now. Can I help you with something else?"

    @agent.function("book_appointment")
    async def book_appointment_tool(
        appointment_type: str,
        facility: str,
        start_time: str,
        duration_minutes: int = 30,
        notes: str = "",
    ):
        """
        Book a new appointment.

        Args:
            appointment_type: Type of appointment - "delivery", "maintenance", or "compliance"
            facility: Facility name
            start_time: Start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
            duration_minutes: Duration in minutes (default 30)
            notes: Additional notes
        """
        from .tools.schemas import AppointmentType, BookingRequest

        logger.info(
            "booking_appointment",
            driver=call_context.driver_name,
            facility=facility,
            time=start_time,
        )

        try:
            # Use context information
            if not call_context.driver_id or not call_context.driver_name:
                return "I need to verify your information first. Can you confirm your name and truck number?"

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

            # Store for potential rescheduling/cancellation
            call_context.current_appointment_id = appointment.id

            # Format confirmation for voice
            date_str = appointment.start_time.strftime("%A, %B %d")
            time_str = appointment.start_time.strftime("%I:%M %p")

            return f"Done! I've booked your {appointment_type} at {facility} for {date_str} at {time_str}. You'll get a text confirmation."

        except Exception as e:
            logger.error("booking_failed", error=str(e))
            return "I wasn't able to book that appointment. Can you try a different time?"

    @agent.function("list_appointments")
    async def list_appointments_tool(days_ahead: int = 30):
        """
        List upcoming appointments for the driver.

        Args:
            days_ahead: Number of days to look ahead (default 30)
        """
        logger.info("listing_appointments", driver=call_context.driver_name)

        try:
            if not call_context.driver_id:
                return "I need to verify your identity first. Can you tell me your truck number?"

            appointments = calendar.list_appointments(call_context.driver_id, days_ahead)

            if not appointments:
                return "You don't have any upcoming appointments in the next 30 days."

            # Format for voice (max 3 to avoid overwhelming)
            apt_list = []
            for apt in appointments[:3]:
                date_str = apt.start_time.strftime("%A, %B %d")
                time_str = apt.start_time.strftime("%I:%M %p")
                apt_list.append(f"{apt.appointment_type.value} at {apt.facility} on {date_str} at {time_str}")

            if len(appointments) > 3:
                apt_list.append(f"and {len(appointments) - 3} more")

            return "Your upcoming appointments are: " + "; ".join(apt_list)

        except Exception as e:
            logger.error("list_appointments_failed", error=str(e))
            return "I'm having trouble accessing your appointments right now."

    @agent.function("cancel_appointment")
    async def cancel_appointment_tool(appointment_id: str, reason: str = ""):
        """
        Cancel an appointment.

        Args:
            appointment_id: ID of the appointment to cancel
            reason: Reason for cancellation
        """
        from .tools.schemas import CancelRequest

        logger.info("canceling_appointment", appointment_id=appointment_id)

        try:
            request = CancelRequest(appointment_id=appointment_id, reason=reason)
            success = calendar.cancel_appointment(request)

            if success:
                return "Your appointment has been cancelled. You'll get a text confirmation."
            else:
                return "I wasn't able to cancel that appointment. Let me transfer you to a dispatcher."

        except Exception as e:
            logger.error("cancel_failed", error=str(e))
            return "I had trouble cancelling that. Can you try again or would you like to speak with someone?"

    # Start the pipeline
    agent.start(ctx.room)

    logger.info(
        "voice_pipeline_created",
        room=ctx.room.name,
        driver=call_context.driver_name,
        model=config.llm_model,
    )

    # Initial greeting
    if call_context.driver_name:
        greeting = f"Hi {call_context.driver_name}, this is the scheduling assistant. Am I speaking with {call_context.driver_name}?"
    else:
        greeting = "Hi, this is the scheduling assistant. Can I get your name and truck number?"

    await agent.say(greeting)

    return agent


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the LiveKit agent.
    This is called when a participant joins a room.
    """
    logger.info(
        "agent_started",
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
    # In Phase 3+, this will be populated from the trigger that initiated the call
    call_context = AppointmentContext()

    # For Phase 2 testing via Playground, use test data
    call_context.driver_id = "DRV-TEST-001"
    call_context.driver_name = "Mike"
    call_context.truck_number = "T-4521"
    call_context.call_purpose = "appointment scheduling"
    call_context.verified = False

    # Create and start the voice pipeline
    agent = await create_voice_pipeline(ctx, call_context)

    # Keep the agent running until the room closes
    await agent.join()


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
