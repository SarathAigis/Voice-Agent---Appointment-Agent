"""Webhook handlers for Twilio events."""

import structlog
from fastapi import APIRouter, Form, Request
from typing import Optional

from agent.telephony import CallStatus, get_caller, get_voicemail_detector, get_sms_service
from agent.config import config

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/calls", tags=["webhooks"])


@router.post("/status")
async def call_status_webhook(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Duration: Optional[str] = Form(None),
    AnsweredBy: Optional[str] = Form(None),
):
    """
    Webhook handler for Twilio call status updates.

    Args:
        CallSid: Twilio call SID
        CallStatus: Current call status
        From: Caller phone number
        To: Callee phone number
        Duration: Call duration (if completed)
        AnsweredBy: Answering machine detection result

    Returns:
        Success response
    """
    logger.info(
        "twilio_status_webhook",
        call_sid=CallSid,
        status=CallStatus,
        answered_by=AnsweredBy,
    )

    caller = get_caller()
    call_record = caller.get_call_record(CallSid)

    if not call_record:
        logger.warning("webhook_call_not_found", call_sid=CallSid)
        return {"status": "ok"}

    # Map Twilio status to our CallStatus enum
    status_map = {
        "queued": CallStatus.INITIATED,
        "initiated": CallStatus.INITIATED,
        "ringing": CallStatus.RINGING,
        "in-progress": CallStatus.IN_PROGRESS,
        "completed": CallStatus.COMPLETED,
        "busy": CallStatus.BUSY,
        "no-answer": CallStatus.NO_ANSWER,
        "canceled": CallStatus.CANCELED,
        "failed": CallStatus.FAILED,
    }

    new_status = status_map.get(CallStatus.lower(), CallStatus.FAILED)

    # Handle voicemail detection
    if AnsweredBy and AnsweredBy != "human":
        vm_detector = get_voicemail_detector()
        if vm_detector.is_voicemail(AnsweredBy):
            new_status = CallStatus.VOICEMAIL
            caller.update_call_status(
                CallSid,
                new_status,
                voicemail_detected=True,
            )

            # Handle voicemail
            vm_detector.handle_voicemail(
                call_sid=CallSid,
                driver_name=call_record.request.driver_name,
                driver_phone=call_record.request.driver_phone,
                call_purpose=call_record.request.call_purpose,
            )

            logger.info("voicemail_handled", call_sid=CallSid)
            return {"status": "ok"}

    # Update call status
    if new_status == CallStatus.IN_PROGRESS:
        caller.update_call_status(CallSid, new_status, answered=True)
    elif new_status in [CallStatus.COMPLETED, CallStatus.FAILED]:
        if Duration:
            caller.update_call_status(CallSid, new_status, duration_seconds=int(Duration))
        else:
            caller.update_call_status(CallSid, new_status)

        # Send SMS followup if call failed
        if new_status == CallStatus.FAILED or (new_status == CallStatus.NO_ANSWER and call_record):
            sms_service = get_sms_service()
            sms_service.send_failed_call_followup(
                phone=call_record.request.driver_phone,
                driver_name=call_record.request.driver_name,
                reason=call_record.request.call_purpose,
            )
    else:
        caller.update_call_status(CallSid, new_status)

    return {"status": "ok"}


@router.post("/recording")
async def recording_webhook(request: Request):
    """
    Webhook handler for call recording completion.

    Args:
        request: FastAPI request object

    Returns:
        Success response
    """
    form = await request.form()
    call_sid = form.get("CallSid")
    recording_url = form.get("RecordingUrl")

    logger.info(
        "recording_webhook",
        call_sid=call_sid,
        recording_url=recording_url,
    )

    # Store recording URL in call record if needed
    # This would be used in Phase 5+ for observability

    return {"status": "ok"}


@router.post("/events")
async def events_webhook(request: Request):
    """
    Webhook handler for real-time call events from Twilio streams.

    Args:
        request: FastAPI request object

    Returns:
        Success response
    """
    body = await request.json()
    event_type = body.get("event")

    logger.info(
        "twilio_event",
        event_type=event_type,
        data=body,
    )

    # Handle different event types
    # This can be used for more granular call monitoring

    return {"status": "ok"}
