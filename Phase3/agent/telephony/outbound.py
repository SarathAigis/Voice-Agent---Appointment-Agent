"""Twilio outbound calling functionality."""

import structlog
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from ..config import config

logger = structlog.get_logger(__name__)


class CallStatus(str, Enum):
    """Call status enumeration."""

    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    CANCELED = "canceled"
    VOICEMAIL = "voicemail"


class CallRequest(BaseModel):
    """Request to initiate an outbound call."""

    driver_id: str
    driver_name: str
    driver_phone: str
    truck_number: str
    call_purpose: str
    appointment_id: Optional[str] = None
    context: dict = {}


class CallRecord(BaseModel):
    """Record of a call."""

    call_sid: str
    request: CallRequest
    status: CallStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    answered: bool = False
    voicemail_detected: bool = False
    livekit_room_name: Optional[str] = None


class OutboundCaller:
    """Handles outbound calling via Twilio."""

    def __init__(self):
        """Initialize Twilio client."""
        self.client = Client(config.twilio_account_sid, config.twilio_auth_token)
        self.active_calls: dict[str, CallRecord] = {}

    def initiate_call(self, request: CallRequest) -> CallRecord:
        """
        Initiate an outbound call to a driver.

        Args:
            request: Call request details

        Returns:
            CallRecord with call details

        Raises:
            TwilioRestException: If call fails to initiate
        """
        logger.info(
            "initiating_outbound_call",
            driver=request.driver_name,
            phone=request.driver_phone,
            purpose=request.call_purpose,
        )

        # Create unique room name for this call
        room_name = f"call-{request.driver_id}-{int(datetime.now().timestamp())}"

        # Build TwiML URL that will connect to LiveKit
        # In production, this would be your API server endpoint
        twiml_url = f"http://{config.api_host}:{config.api_port}/api/calls/twiml/{room_name}"

        # Status callback URL for call events
        status_callback = f"http://{config.api_host}:{config.api_port}/api/calls/status"

        try:
            # Initiate the call
            call = self.client.calls.create(
                to=request.driver_phone,
                from_=config.twilio_phone_number,
                url=twiml_url,
                status_callback=status_callback,
                status_callback_event=["initiated", "ringing", "answered", "completed"],
                status_callback_method="POST",
                timeout=config.call_timeout_seconds,
                # Enable answering machine detection if configured
                machine_detection="DetectMessageEnd" if config.enable_voicemail_detection else "Enable",
                machine_detection_timeout=5,
                machine_detection_speech_threshold=2400,
                machine_detection_speech_end_threshold=1200,
                machine_detection_silence_timeout=5000,
            )

            # Create call record
            call_record = CallRecord(
                call_sid=call.sid,
                request=request,
                status=CallStatus.INITIATED,
                start_time=datetime.now(),
                livekit_room_name=room_name,
            )

            # Store active call
            self.active_calls[call.sid] = call_record

            logger.info(
                "call_initiated",
                call_sid=call.sid,
                room_name=room_name,
                driver=request.driver_name,
            )

            return call_record

        except TwilioRestException as e:
            logger.error(
                "call_initiation_failed",
                error=str(e),
                driver=request.driver_name,
                phone=request.driver_phone,
            )
            raise

    def update_call_status(self, call_sid: str, status: CallStatus, **kwargs) -> None:
        """
        Update the status of an active call.

        Args:
            call_sid: Twilio call SID
            status: New call status
            **kwargs: Additional fields to update
        """
        if call_sid not in self.active_calls:
            logger.warning("call_not_found", call_sid=call_sid)
            return

        call_record = self.active_calls[call_sid]
        call_record.status = status

        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(call_record, key):
                setattr(call_record, key, value)

        # If call ended, set end time and duration
        if status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.NO_ANSWER, CallStatus.BUSY]:
            if not call_record.end_time:
                call_record.end_time = datetime.now()
                duration = (call_record.end_time - call_record.start_time).seconds
                call_record.duration_seconds = duration

        logger.info(
            "call_status_updated",
            call_sid=call_sid,
            status=status.value,
            driver=call_record.request.driver_name,
        )

    def hangup_call(self, call_sid: str) -> bool:
        """
        Hangup an active call.

        Args:
            call_sid: Twilio call SID

        Returns:
            True if successful, False otherwise
        """
        try:
            call = self.client.calls(call_sid).update(status="completed")

            self.update_call_status(call_sid, CallStatus.COMPLETED)

            logger.info("call_hung_up", call_sid=call_sid)
            return True

        except TwilioRestException as e:
            logger.error("hangup_failed", call_sid=call_sid, error=str(e))
            return False

    def get_call_record(self, call_sid: str) -> Optional[CallRecord]:
        """
        Get call record by SID.

        Args:
            call_sid: Twilio call SID

        Returns:
            CallRecord if found, None otherwise
        """
        return self.active_calls.get(call_sid)

    def cleanup_call(self, call_sid: str) -> None:
        """
        Remove call from active calls.

        Args:
            call_sid: Twilio call SID
        """
        if call_sid in self.active_calls:
            del self.active_calls[call_sid]
            logger.info("call_cleaned_up", call_sid=call_sid)


# Global caller instance
_caller = None


def get_caller() -> OutboundCaller:
    """Get or create the global outbound caller instance."""
    global _caller
    if _caller is None:
        _caller = OutboundCaller()
    return _caller
