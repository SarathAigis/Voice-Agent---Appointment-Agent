"""Tests for telephony functionality."""

import pytest
from agent.telephony.outbound import CallRequest, CallStatus, OutboundCaller
from agent.telephony.sms import SMSService
from agent.telephony.voicemail import VoicemailDetector


@pytest.fixture
def call_request():
    """Create a test call request."""
    return CallRequest(
        driver_id="TEST-001",
        driver_name="Test Driver",
        driver_phone="+15551234567",
        truck_number="T-TEST",
        call_purpose="test call",
    )


def test_call_request_creation(call_request):
    """Test call request model."""
    assert call_request.driver_id == "TEST-001"
    assert call_request.driver_name == "Test Driver"
    assert call_request.driver_phone == "+15551234567"
    assert call_request.truck_number == "T-TEST"


def test_call_status_enum():
    """Test call status enumeration."""
    assert CallStatus.INITIATED.value == "initiated"
    assert CallStatus.IN_PROGRESS.value == "in-progress"
    assert CallStatus.COMPLETED.value == "completed"
    assert CallStatus.VOICEMAIL.value == "voicemail"


def test_voicemail_detection():
    """Test voicemail detection logic."""
    detector = VoicemailDetector()

    # Test voicemail detection
    assert detector.is_voicemail("machine_start") is True
    assert detector.is_voicemail("machine_end_beep") is True
    assert detector.is_voicemail("machine_end_silence") is True

    # Test human detection
    assert detector.is_voicemail("human") is False
    assert detector.is_voicemail("unknown") is False


def test_sms_service_initialization():
    """Test SMS service initialization."""
    sms_service = SMSService()
    assert sms_service.client is not None
    assert sms_service.from_number is not None
