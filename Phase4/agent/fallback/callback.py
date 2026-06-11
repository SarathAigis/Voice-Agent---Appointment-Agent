"""Callback queue management."""

import structlog
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from ..config import config
from ..telephony import get_sms_service

logger = structlog.get_logger(__name__)


class CallbackRequest(BaseModel):
    """Request for a callback."""

    request_id: str
    driver_id: str
    driver_name: str
    driver_phone: str
    reason: str
    requested_time: datetime
    preferred_time: Optional[datetime] = None
    call_context: dict = {}
    completed: bool = False


class CallbackQueue:
    """Manages callback requests."""

    def __init__(self):
        """Initialize callback queue."""
        self.queue: dict[str, CallbackRequest] = {}
        self.sms_service = get_sms_service()

    def schedule_callback(
        self,
        call_id: str,
        driver_id: str,
        driver_name: str,
        driver_phone: str,
        reason: str,
        preferred_time: Optional[datetime] = None,
        call_context: dict = None,
    ) -> str:
        """
        Schedule a callback for the driver.

        Args:
            call_id: Current call ID
            driver_id: Driver ID
            driver_name: Driver name
            driver_phone: Driver phone number
            reason: Reason for callback
            preferred_time: When driver prefers callback
            call_context: Additional context

        Returns:
            Confirmation message for driver
        """
        logger.info(
            "callback_scheduled",
            call_id=call_id,
            driver=driver_name,
            preferred_time=preferred_time,
        )

        # Create callback request
        request = CallbackRequest(
            request_id=call_id,
            driver_id=driver_id,
            driver_name=driver_name,
            driver_phone=driver_phone,
            reason=reason,
            requested_time=datetime.now(),
            preferred_time=preferred_time,
            call_context=call_context or {},
        )

        self.queue[call_id] = request

        # Determine callback time
        if preferred_time:
            time_str = preferred_time.strftime("%I:%M %p")
        else:
            # Default: within 1 hour during business hours
            callback_time = datetime.now() + timedelta(hours=1)
            time_str = callback_time.strftime("%I:%M %p")

        # Send SMS confirmation
        self.sms_service.send_sms(
            to=driver_phone,
            body=(
                f"Hi {driver_name}, we'll call you back around {time_str} regarding {reason}. "
                f"Reply with a better time if needed, or call us at {config.twilio_phone_number}."
            ),
        )

        message = (
            f"Got it, {driver_name}. We'll call you back around {time_str}. "
            f"You'll get a text confirmation with our number."
        )

        return message

    def get_pending_callbacks(self) -> List[CallbackRequest]:
        """
        Get all pending callback requests.

        Returns:
            List of pending callbacks sorted by requested time
        """
        pending = [cb for cb in self.queue.values() if not cb.completed]
        pending.sort(key=lambda x: x.requested_time)
        return pending

    def get_due_callbacks(self) -> List[CallbackRequest]:
        """
        Get callbacks that are due now.

        Returns:
            List of callbacks due for processing
        """
        now = datetime.now()
        due = []

        for callback in self.get_pending_callbacks():
            if callback.preferred_time and callback.preferred_time <= now:
                due.append(callback)
            elif (now - callback.requested_time).total_seconds() > 3600:
                # Over 1 hour since request
                due.append(callback)

        return due

    def complete_callback(self, request_id: str):
        """
        Mark callback as completed.

        Args:
            request_id: Callback request ID
        """
        if request_id in self.queue:
            self.queue[request_id].completed = True
            logger.info("callback_completed", request_id=request_id)

    def cancel_callback(self, request_id: str, reason: str = None):
        """
        Cancel a callback request.

        Args:
            request_id: Callback request ID
            reason: Reason for cancellation
        """
        if request_id in self.queue:
            callback = self.queue[request_id]

            # Send cancellation SMS
            self.sms_service.send_sms(
                to=callback.driver_phone,
                body=(
                    f"Hi {callback.driver_name}, your scheduled callback has been cancelled. "
                    f"{reason or 'Please call us if you still need assistance.'}"
                ),
            )

            del self.queue[request_id]
            logger.info("callback_cancelled", request_id=request_id, reason=reason)


# Global callback queue instance
_callback_queue = None


def get_callback_queue() -> CallbackQueue:
    """Get or create the global callback queue instance."""
    global _callback_queue
    if _callback_queue is None:
        _callback_queue = CallbackQueue()
    return _callback_queue
