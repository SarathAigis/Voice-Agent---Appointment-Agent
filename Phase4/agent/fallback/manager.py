"""Fallback state machine and manager."""

import structlog
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from ..config import config

logger = structlog.get_logger(__name__)


class FallbackState(str, Enum):
    """Fallback states in the tiered system."""

    NORMAL = "normal"
    LOW_CONFIDENCE = "low_confidence"
    RETRY = "retry"
    SMS_FALLBACK = "sms_fallback"
    CALLBACK_SCHEDULED = "callback_scheduled"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    FAILED = "failed"


class FallbackTrigger(str, Enum):
    """Events that can trigger fallback state changes."""

    LOW_CONFIDENCE_STT = "low_confidence_stt"
    REPEATED_FAILURE = "repeated_failure"
    DRIVER_CONFUSED = "driver_confused"
    DRIVER_FRUSTRATED = "driver_frustrated"
    DRIVER_REQUEST_HUMAN = "driver_request_human"
    NO_AVAILABLE_SLOTS = "no_available_slots"
    TOOL_CALL_FAILED = "tool_call_failed"
    MAX_RETRIES_REACHED = "max_retries_reached"
    DRIVER_REQUEST_CALLBACK = "driver_request_callback"


class FallbackContext(BaseModel):
    """Context for a fallback situation."""

    state: FallbackState = FallbackState.NORMAL
    retry_count: int = 0
    low_confidence_count: int = 0
    last_trigger: Optional[FallbackTrigger] = None
    last_trigger_time: Optional[datetime] = None
    callback_requested_time: Optional[datetime] = None
    escalation_reason: Optional[str] = None


class FallbackManager:
    """Manages the tiered fallback system."""

    def __init__(self):
        """Initialize fallback manager."""
        self.contexts: dict[str, FallbackContext] = {}

    def get_context(self, call_id: str) -> FallbackContext:
        """
        Get or create fallback context for a call.

        Args:
            call_id: Unique call identifier

        Returns:
            FallbackContext for this call
        """
        if call_id not in self.contexts:
            self.contexts[call_id] = FallbackContext()
        return self.contexts[call_id]

    def handle_trigger(
        self,
        call_id: str,
        trigger: FallbackTrigger,
        context_data: dict = None
    ) -> FallbackState:
        """
        Handle a fallback trigger and update state.

        Args:
            call_id: Call identifier
            trigger: What triggered the fallback
            context_data: Additional context information

        Returns:
            New fallback state
        """
        context = self.get_context(call_id)
        previous_state = context.state

        logger.info(
            "fallback_trigger",
            call_id=call_id,
            trigger=trigger.value,
            current_state=previous_state.value,
        )

        # Update trigger info
        context.last_trigger = trigger
        context.last_trigger_time = datetime.now()

        # State transition logic
        if trigger == FallbackTrigger.DRIVER_REQUEST_HUMAN:
            # Immediate escalation when driver explicitly requests
            context.state = FallbackState.ESCALATE_TO_HUMAN
            context.escalation_reason = "Driver requested human assistance"

        elif trigger == FallbackTrigger.DRIVER_FRUSTRATED:
            # Escalate frustrated drivers immediately
            context.state = FallbackState.ESCALATE_TO_HUMAN
            context.escalation_reason = "Driver appears frustrated"

        elif trigger == FallbackTrigger.DRIVER_REQUEST_CALLBACK:
            # Schedule callback
            context.state = FallbackState.CALLBACK_SCHEDULED
            context.callback_requested_time = datetime.now()

        elif trigger == FallbackTrigger.LOW_CONFIDENCE_STT:
            # Track low confidence attempts
            context.low_confidence_count += 1

            if context.low_confidence_count >= config.max_retry_attempts:
                # Too many low confidence → SMS fallback
                context.state = FallbackState.SMS_FALLBACK
            else:
                # Try rephrasing
                context.state = FallbackState.RETRY

        elif trigger in [
            FallbackTrigger.REPEATED_FAILURE,
            FallbackTrigger.DRIVER_CONFUSED,
        ]:
            # Increment retry counter
            context.retry_count += 1

            if context.retry_count >= config.max_retry_attempts:
                # Max retries → escalate
                context.state = FallbackState.ESCALATE_TO_HUMAN
                context.escalation_reason = f"Max retries reached ({trigger.value})"
            else:
                # Try SMS fallback first
                context.state = FallbackState.SMS_FALLBACK

        elif trigger == FallbackTrigger.NO_AVAILABLE_SLOTS:
            # Offer alternatives or callback
            if config.callback_queue_enabled:
                context.state = FallbackState.CALLBACK_SCHEDULED
            else:
                context.state = FallbackState.SMS_FALLBACK

        elif trigger == FallbackTrigger.TOOL_CALL_FAILED:
            # Tool failure → retry or escalate
            context.retry_count += 1

            if context.retry_count >= 2:
                context.state = FallbackState.ESCALATE_TO_HUMAN
                context.escalation_reason = "Tool call failure"
            else:
                context.state = FallbackState.RETRY

        elif trigger == FallbackTrigger.MAX_RETRIES_REACHED:
            # Final fallback
            context.state = FallbackState.ESCALATE_TO_HUMAN
            context.escalation_reason = "Maximum retry attempts exceeded"

        logger.info(
            "fallback_state_changed",
            call_id=call_id,
            from_state=previous_state.value,
            to_state=context.state.value,
            trigger=trigger.value,
        )

        return context.state

    def should_retry(self, call_id: str) -> bool:
        """
        Check if agent should retry current operation.

        Args:
            call_id: Call identifier

        Returns:
            True if should retry
        """
        context = self.get_context(call_id)
        return (
            context.state in [FallbackState.NORMAL, FallbackState.RETRY]
            and context.retry_count < config.max_retry_attempts
        )

    def should_send_sms(self, call_id: str) -> bool:
        """
        Check if should send SMS fallback.

        Args:
            call_id: Call identifier

        Returns:
            True if should send SMS
        """
        context = self.get_context(call_id)
        return context.state == FallbackState.SMS_FALLBACK

    def should_escalate(self, call_id: str) -> bool:
        """
        Check if should escalate to human.

        Args:
            call_id: Call identifier

        Returns:
            True if should escalate
        """
        context = self.get_context(call_id)
        return context.state == FallbackState.ESCALATE_TO_HUMAN

    def get_escalation_reason(self, call_id: str) -> Optional[str]:
        """Get reason for escalation."""
        context = self.get_context(call_id)
        return context.escalation_reason

    def reset_context(self, call_id: str):
        """Reset fallback context for a call."""
        if call_id in self.contexts:
            del self.contexts[call_id]
            logger.info("fallback_context_reset", call_id=call_id)


# Global fallback manager instance
_fallback_manager = None


def get_fallback_manager() -> FallbackManager:
    """Get or create the global fallback manager instance."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = FallbackManager()
    return _fallback_manager
