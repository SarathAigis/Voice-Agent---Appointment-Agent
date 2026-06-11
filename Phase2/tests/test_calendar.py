"""Tests for Google Calendar integration."""

import pytest
from datetime import datetime, timedelta
from agent.tools.calendar import CalendarTool
from agent.tools.schemas import AppointmentType, AvailabilityRequest, BookingRequest


@pytest.fixture
def calendar_tool():
    """Create a calendar tool instance."""
    return CalendarTool()


def test_check_availability_mock(calendar_tool):
    """Test availability checking (works without calendar credentials)."""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    request = AvailabilityRequest(
        date=tomorrow,
        facility="Test Warehouse",
        appointment_type=AppointmentType.DELIVERY,
        duration_minutes=30,
    )

    slots = calendar_tool.check_availability(
        date=request.date,
        facility=request.facility,
        appointment_type=request.appointment_type,
        duration_minutes=request.duration_minutes,
    )

    # Should return mock slots even without credentials
    assert len(slots) > 0
    assert all(slot.facility == "Test Warehouse" for slot in slots)


def test_book_appointment_mock(calendar_tool):
    """Test appointment booking (mock mode without credentials)."""
    start_time = datetime.now() + timedelta(days=1, hours=2)

    request = BookingRequest(
        driver_id="TEST-001",
        driver_name="Test Driver",
        truck_number="T-TEST",
        appointment_type=AppointmentType.DELIVERY,
        facility="Test Warehouse",
        start_time=start_time.isoformat(),
        duration_minutes=30,
        notes="Test appointment",
    )

    appointment = calendar_tool.book_appointment(
        driver_id=request.driver_id,
        driver_name=request.driver_name,
        truck_number=request.truck_number,
        appointment_type=request.appointment_type,
        facility=request.facility,
        start_time=request.start_time,
        duration_minutes=request.duration_minutes,
        notes=request.notes,
    )

    assert appointment.driver_id == "TEST-001"
    assert appointment.driver_name == "Test Driver"
    assert appointment.appointment_type == AppointmentType.DELIVERY
    assert appointment.facility == "Test Warehouse"


def test_appointment_type_enum():
    """Test appointment type enumeration."""
    assert AppointmentType.DELIVERY.value == "delivery"
    assert AppointmentType.MAINTENANCE.value == "maintenance"
    assert AppointmentType.COMPLIANCE.value == "compliance"

    # Test case-insensitive parsing
    assert AppointmentType("delivery") == AppointmentType.DELIVERY
    assert AppointmentType("DELIVERY") == AppointmentType.DELIVERY
