"""Escalation handler for transferring to human dispatchers."""

import structlog
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..config import config
from ..telephony import get_sms_service

logger = structlog.get_logger(__name__)


class EscalationRequest(BaseModel):
    """Request to escalate to human dispatcher."""

    call_id: str
    driver_id: str
    driver_name: str
    driver_phone: str
    reason: str
    call_context: dict = {}
    timestamp: datetime = datetime.now()


class EscalationHandler:
    """Handles escalation to human dispatchers."""

    def __init__(self):
        """Initialize escalation handler."""
        self.sms_service = get_sms_service()
        self.pending_escalations: dict[str, EscalationRequest] = {}

    def is_dispatcher_available(self) -> bool:
        """
        Check if dispatcher is available based on business hours.

        Returns:
            True if dispatcher available
        """
        now = datetime.now()
        hour = now.hour

        available = (
            config.dispatcher_available_hours_start <= hour < config.dispatcher_available_hours_end
        )

        logger.info(
            "dispatcher_availability_check",
            hour=hour,
            available=available,
        )

        return available

    def escalate(
        self,
        call_id: str,
        driver_id: str,
        driver_name: str,
        driver_phone: str,
        reason: str,
        call_context: dict = None,
    ) -> str:
        """
        Escalate call to human dispatcher.

        Args:
            call_id: Call identifier
            driver_id: Driver ID
            driver_name: Driver name
            driver_phone: Driver phone number
            reason: Reason for escalation
            call_context: Additional context

        Returns:
            Escalation message to tell driver
        """
        logger.info(
            "escalating_to_human",
            call_id=call_id,
            driver=driver_name,
            reason=reason,
        )

        # Create escalation request
        request = EscalationRequest(
            call_id=call_id,
            driver_id=driver_id,
            driver_name=driver_name,
            driver_phone=driver_phone,
            reason=reason,
            call_context=call_context or {},
        )

        self.pending_escalations[call_id] = request

        # Check if warm transfer is possible
        if config.warm_transfer_enabled and self.is_dispatcher_available():
            return self._warm_transfer(request)
        else:
            return self._schedule_callback(request)

    def _warm_transfer(self, request: EscalationRequest) -> str:
        """
        Initiate warm transfer to dispatcher.

        Args:
            request: Escalation request

        Returns:
            Message to driver
        """
        logger.info(
            "warm_transfer_initiated",
            call_id=request.call_id,
            driver=request.driver_name,
        )

        # In a real implementation, this would:
        # 1. Add dispatcher to LiveKit room
        # 2. Send context to dispatcher via separate channel
        # 3. Introduce parties
        # 4. Agent leaves room

        # For now, simulate with message
        message = (
            f"Let me connect you with one of our dispatchers who can help. "
            f"Please hold for just a moment."
        )

        # Send SMS with context in case transfer fails
        self.sms_service.send_sms(
            to=request.driver_phone,
            body=(
                f"Hi {request.driver_name}, we're connecting you with a dispatcher. "
                f"If disconnected, please call {config.escalation_phone_number or 'us back'}."
            ),
        )

        return message

    def _schedule_callback(self, request: EscalationRequest) -> str:
        """
        Schedule callback when dispatcher not available.

        Args:
            request: Escalation request

        Returns:
            Message to driver
        """
        logger.info(
            "callback_scheduled",
            call_id=request.call_id,
            driver=request.driver_name,
        )

        # Send SMS with callback details
        callback_time = "within the next hour"
        if not self.is_dispatcher_available():
            callback_time = f"at {config.dispatcher_available_hours_start}am when our office opens"

        self.sms_service.send_sms(
            to=request.driver_phone,
            body=(
                f"Hi {request.driver_name}, a dispatcher will call you back {callback_time}. "
                f"Reason: {request.reason}. "
                f"Or call us at {config.escalation_phone_number or 'our main number'}."
            ),
        )

        message = (
            f"I understand this needs more attention. A dispatcher will call you back {callback_time}. "
            f"You'll also get a text message with our callback number."
        )

        return message

    def get_escalation(self, call_id: str) -> Optional[EscalationRequest]:
        """Get escalation request by call ID."""
        return self.pending_escalations.get(call_id)

    def resolve_escalation(self, call_id: str):
        """Mark escalation as resolved."""
        if call_id in self.pending_escalations:
            del self.pending_escalations[call_id]
            logger.info("escalation_resolved", call_id=call_id)


# Global escalation handler instance
_escalation_handler = None


def get_escalation_handler() -> EscalationHandler:
    """Get or create the global escalation handler instance."""
    global _escalation_handler
    if _escalation_handler is None:
        _escalation_handler = EscalationHandler()
    return _escalation_handler
