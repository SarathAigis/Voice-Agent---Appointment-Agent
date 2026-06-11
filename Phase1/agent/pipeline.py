"""Voice pipeline orchestration using LiveKit Agents SDK."""

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
from livekit.plugins import deepgram, elevenlabs, silero

from .config import config

logger = structlog.get_logger(__name__)


async def create_voice_pipeline(ctx: JobContext) -> VoicePipelineAgent:
    """
    Create and configure the voice pipeline agent.

    Phase 1: Simple echo/canned response agent for audio pipeline validation.
    Phase 2+: Will be replaced with LLM-powered conversational agent.
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

    # Phase 1: Simple function-based LLM for testing
    # This will be replaced with Claude/GPT-4o in Phase 2
    @llm.ai_callable()
    async def simple_response(ctx: llm.FunctionCallContext):
        """
        Simple echo response for Phase 1 testing.
        In Phase 2, this will be replaced with actual LLM conversation.
        """
        user_message = ctx.messages[-1].content if ctx.messages else ""
        logger.info("received_user_message", message=user_message)

        # Phase 1: Echo back with a canned response
        response = f"I heard you say: {user_message}. This is a test of the voice pipeline."

        return response

    # Create simple LLM for Phase 1 (will be replaced in Phase 2)
    simple_llm = llm.FunctionLLM()

    # Create the voice pipeline agent
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(
            min_speech_duration=config.vad_min_speech_duration,
            min_silence_duration=config.vad_silence_duration,
            # Aggressive thresholds for noisy truck environments
            activation_threshold=config.vad_energy_threshold,
            deactivation_threshold=config.vad_energy_threshold * 0.8,
        ),
        stt=stt,
        llm=simple_llm,
        tts=tts,
        # Allow interruption (barge-in) - critical for natural conversation
        allow_interruptions=True,
        # Minimum time before allowing interruption (ms)
        min_endpointing_delay=200,
    )

    # Start the pipeline
    agent.start(ctx.room)

    logger.info(
        "voice_pipeline_created",
        room=ctx.room.name,
        participant=ctx.room.local_participant.identity,
    )

    # Phase 1: Simple greeting
    await agent.say("Hello, this is a test of the voice pipeline. Please say something.")

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

    # Create and start the voice pipeline
    agent = await create_voice_pipeline(ctx)

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
