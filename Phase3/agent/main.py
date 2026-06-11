"""Main entrypoint for Phase 3 voice agent with Twilio."""

import structlog

from .pipeline import entrypoint
from livekit.agents import WorkerOptions, cli
from .config import config


def main():
    """Run the voice agent."""

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )

    logger = structlog.get_logger(__name__)
    logger.info(
        "starting_phase3_agent",
        livekit_url=config.livekit_url,
        llm_model=config.llm_model,
        twilio_enabled=bool(config.twilio_account_sid),
    )

    # Run the LiveKit agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=config.livekit_api_key,
            api_secret=config.livekit_api_secret,
            ws_url=config.livekit_url,
        )
    )


if __name__ == "__main__":
    main()
