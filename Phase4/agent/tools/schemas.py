"""Data schemas for appointment scheduling."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AppointmentType(str, Enum):
    """Types of appointments."""

    DELIVERY = "delivery"
    MAINTENANCE = "maintenance"
    COMPLIANCE = "compliance"


class TimeSlot(BaseModel):
    """An available time slot."""

    start_time: datetime
    end_time: datetime
    facility: str

    def __str__(self):
        """Format for voice output."""
        time_str = self.start_time.strftime("%A at %I:%M %p")
        return f"{time_str} at {self.facility}"


class Appointment(BaseModel):
    """A scheduled appointment."""

    id: str
    driver_id: str
    driver_name: str
    appointment_type: AppointmentType
    facility: str
    start_time: datetime
    end_time: datetime
    truck_number: Optional[str] = None
    notes: Optional[str] = None
    confirmed: bool = False

    def __str__(self):
        """Format for voice output."""
        date_str = self.start_time.strftime("%A, %B %d")
        time_str = self.start_time.strftime("%I:%M %p")
        return f"{self.appointment_type.value} at {self.facility} on {date_str} at {time_str}"


class AvailabilityRequest(BaseModel):
    """Request to check appointment availability."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    facility: str = Field(..., description="Facility name")
    appointment_type: AppointmentType = Field(..., description="Type of appointment")
    duration_minutes: int = Field(default=30, description="Appointment duration")


class BookingRequest(BaseModel):
    """Request to book an appointment."""

    driver_id: str = Field(..., description="Driver ID")
    driver_name: str = Field(..., description="Driver name")
    truck_number: str = Field(..., description="Truck number")
    appointment_type: AppointmentType = Field(..., description="Type of appointment")
    facility: str = Field(..., description="Facility name")
    start_time: str = Field(..., description="Start time in ISO 8601 format")
    duration_minutes: int = Field(default=30, description="Appointment duration")
    notes: Optional[str] = Field(None, description="Additional notes")


class RescheduleRequest(BaseModel):
    """Request to reschedule an appointment."""

    appointment_id: str = Field(..., description="Appointment ID to reschedule")
    new_start_time: str = Field(..., description="New start time in ISO 8601 format")
    reason: Optional[str] = Field(None, description="Reason for rescheduling")


class CancelRequest(BaseModel):
    """Request to cancel an appointment."""

    appointment_id: str = Field(..., description="Appointment ID to cancel")
    reason: Optional[str] = Field(None, description="Reason for cancellation")
