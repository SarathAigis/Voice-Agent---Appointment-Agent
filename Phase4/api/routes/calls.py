"""API routes for call initiation and management."""

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from agent.telephony import CallRequest, CallStatus, get_caller
from agent.config import config

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/calls", tags=["calls"])


class InitiateCallRequest(BaseModel):
    """Request body for initiating a call."""

    driver_id: str
    driver_name: str
    driver_phone: str
    truck_number: str
    call_purpose: str
    appointment_id: str | None = None
    context: dict = {}


class InitiateCallResponse(BaseModel):
    """Response for call initiation."""

    call_sid: str
    status: str
    room_name: str
    message: str


@router.post("/initiate", response_model=InitiateCallResponse)
async def initiate_call(request: InitiateCallRequest):
    """
    Initiate an outbound call to a driver.

    Args:
        request: Call initiation request

    Returns:
        Call details including SID and room name
    """
    logger.info(
        "api_call_initiate_request",
        driver=request.driver_name,
        phone=request.driver_phone,
    )

    try:
        caller = get_caller()

        call_request = CallRequest(
            driver_id=request.driver_id,
            driver_name=request.driver_name,
            driver_phone=request.driver_phone,
            truck_number=request.truck_number,
            call_purpose=request.call_purpose,
            appointment_id=request.appointment_id,
            context=request.context,
        )

        call_record = caller.initiate_call(call_request)

        return InitiateCallResponse(
            call_sid=call_record.call_sid,
            status=call_record.status.value,
            room_name=call_record.livekit_room_name or "",
            message=f"Call initiated to {request.driver_name}",
        )

    except Exception as e:
        logger.error("call_initiation_api_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{call_sid}")
async def get_call_status(call_sid: str):
    """
    Get the status of a call.

    Args:
        call_sid: Twilio call SID

    Returns:
        Call status details
    """
    caller = get_caller()
    call_record = caller.get_call_record(call_sid)

    if not call_record:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "call_sid": call_record.call_sid,
        "status": call_record.status.value,
        "driver_name": call_record.request.driver_name,
        "answered": call_record.answered,
        "voicemail_detected": call_record.voicemail_detected,
        "duration_seconds": call_record.duration_seconds,
        "start_time": call_record.start_time.isoformat(),
        "end_time": call_record.end_time.isoformat() if call_record.end_time else None,
    }


@router.post("/hangup/{call_sid}")
async def hangup_call(call_sid: str):
    """
    Hangup an active call.

    Args:
        call_sid: Twilio call SID

    Returns:
        Success message
    """
    caller = get_caller()
    success = caller.hangup_call(call_sid)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to hangup call")

    return {"message": "Call hung up successfully", "call_sid": call_sid}


@router.get("/twiml/{room_name}")
async def get_twiml(room_name: str):
    """
    Generate TwiML to connect call to LiveKit room.

    This endpoint is called by Twilio when the call is answered.

    Args:
        room_name: LiveKit room name

    Returns:
        TwiML XML response
    """
    # Generate LiveKit token for this call
    # In production, you'd create a proper token with room access

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{config.livekit_url.replace('wss://', '').replace('ws://', '')}/stream">
            <Parameter name="room" value="{room_name}" />
        </Stream>
    </Connect>
</Response>"""

    logger.info("twiml_generated", room_name=room_name)

    return Response(content=twiml, media_type="application/xml")
