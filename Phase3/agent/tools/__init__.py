"""Tool definitions for the scheduling agent."""

from .calendar import (
    CalendarTool,
    check_availability,
    book_appointment,
    reschedule_appointment,
    cancel_appointment,
    list_appointments,
)
from .schemas import (
    AppointmentType,
    TimeSlot,
    Appointment,
    AvailabilityRequest,
    BookingRequest,
    RescheduleRequest,
    CancelRequest,
)

__all__ = [
    "CalendarTool",
    "check_availability",
    "book_appointment",
    "reschedule_appointment",
    "cancel_appointment",
    "list_appointments",
    "AppointmentType",
    "TimeSlot",
    "Appointment",
    "AvailabilityRequest",
    "BookingRequest",
    "RescheduleRequest",
    "CancelRequest",
]
