"""Google Calendar integration for appointment management."""

import os
from datetime import datetime, timedelta
from typing import List, Optional

import structlog
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import config
from .schemas import (
    Appointment,
    AppointmentType,
    AvailabilityRequest,
    BookingRequest,
    CancelRequest,
    RescheduleRequest,
    TimeSlot,
)

logger = structlog.get_logger(__name__)


class CalendarTool:
    """Google Calendar API wrapper for appointment management."""

    def __init__(self):
        """Initialize the calendar service."""
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Calendar API service with credentials."""
        try:
            if not os.path.exists(config.google_calendar_credentials_path):
                logger.warning(
                    "google_calendar_credentials_not_found",
                    path=config.google_calendar_credentials_path,
                )
                return

            credentials = service_account.Credentials.from_service_account_file(
                config.google_calendar_credentials_path,
                scopes=["https://www.googleapis.com/auth/calendar"],
            )

            self.service = build("calendar", "v3", credentials=credentials)
            logger.info("google_calendar_initialized")

        except Exception as e:
            logger.error("google_calendar_init_failed", error=str(e))
            self.service = None

    def _format_event_id(self, driver_id: str, timestamp: datetime) -> str:
        """Generate a consistent event ID."""
        ts = timestamp.strftime("%Y%m%d%H%M")
        return f"appt_{driver_id}_{ts}".replace("-", "").lower()

    def check_availability(
        self, date: str, facility: str, appointment_type: AppointmentType, duration_minutes: int = 30
    ) -> List[TimeSlot]:
        """
        Check available time slots for a given date and facility.

        Args:
            date: Date in YYYY-MM-DD format
            facility: Facility name
            appointment_type: Type of appointment
            duration_minutes: Duration of appointment

        Returns:
            List of available time slots
        """
        if not self.service:
            logger.warning("calendar_service_not_initialized")
            # Return mock slots for testing without calendar
            return self._mock_availability(date, facility, duration_minutes)

        try:
            # Parse the date
            target_date = datetime.fromisoformat(date)

            # Define business hours
            time_min = target_date.replace(
                hour=config.business_hours_start, minute=0, second=0, microsecond=0
            )
            time_max = target_date.replace(
                hour=config.business_hours_end, minute=0, second=0, microsecond=0
            )

            # Get existing events
            events_result = (
                self.service.events()
                .list(
                    calendarId=config.google_calendar_id,
                    timeMin=time_min.isoformat() + "Z",
                    timeMax=time_max.isoformat() + "Z",
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            # Find gaps between events
            available_slots = []
            current_time = time_min

            for event in events:
                event_start = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                event_start = event_start.replace(tzinfo=None)

                # If there's a gap before this event
                if (event_start - current_time).seconds >= duration_minutes * 60:
                    available_slots.append(
                        TimeSlot(
                            start_time=current_time,
                            end_time=current_time + timedelta(minutes=duration_minutes),
                            facility=facility,
                        )
                    )

                # Move current_time to after this event
                event_end = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
                current_time = max(current_time, event_end.replace(tzinfo=None))

            # Check if there's time remaining at the end of the day
            if (time_max - current_time).seconds >= duration_minutes * 60:
                available_slots.append(
                    TimeSlot(
                        start_time=current_time,
                        end_time=current_time + timedelta(minutes=duration_minutes),
                        facility=facility,
                    )
                )

            logger.info(
                "availability_checked",
                date=date,
                facility=facility,
                slots_found=len(available_slots),
            )

            # Return max 5 slots to avoid overwhelming the driver
            return available_slots[:5]

        except HttpError as e:
            logger.error("calendar_api_error", error=str(e))
            return self._mock_availability(date, facility, duration_minutes)

    def _mock_availability(self, date: str, facility: str, duration_minutes: int) -> List[TimeSlot]:
        """Return mock availability for testing without calendar access."""
        target_date = datetime.fromisoformat(date)
        slots = []

        # Generate 3 mock slots: 10am, 2pm, 4pm
        for hour in [10, 14, 16]:
            start = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            slots.append(
                TimeSlot(
                    start_time=start,
                    end_time=start + timedelta(minutes=duration_minutes),
                    facility=facility,
                )
            )

        return slots

    def book_appointment(
        self,
        driver_id: str,
        driver_name: str,
        truck_number: str,
        appointment_type: AppointmentType,
        facility: str,
        start_time: str,
        duration_minutes: int = 30,
        notes: Optional[str] = None,
    ) -> Appointment:
        """
        Book a new appointment.

        Args:
            driver_id: Unique driver identifier
            driver_name: Driver's name
            truck_number: Truck number
            appointment_type: Type of appointment
            facility: Facility name
            start_time: Start time in ISO 8601 format
            duration_minutes: Duration in minutes
            notes: Optional notes

        Returns:
            Created appointment
        """
        start_dt = datetime.fromisoformat(start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        event = {
            "summary": f"{appointment_type.value.title()} - {driver_name}",
            "location": facility,
            "description": f"Driver: {driver_name}\nTruck: {truck_number}\nType: {appointment_type.value}\n{notes or ''}",
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Denver"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "America/Denver"},
            "attendees": [],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "sms", "minutes": 60},  # 1 hour before
                ],
            },
        }

        if self.service:
            try:
                created_event = (
                    self.service.events()
                    .insert(calendarId=config.google_calendar_id, body=event)
                    .execute()
                )

                appointment_id = created_event["id"]
                logger.info(
                    "appointment_booked",
                    appointment_id=appointment_id,
                    driver=driver_name,
                    facility=facility,
                    time=start_time,
                )

            except HttpError as e:
                logger.error("booking_failed", error=str(e))
                appointment_id = self._format_event_id(driver_id, start_dt)
        else:
            appointment_id = self._format_event_id(driver_id, start_dt)
            logger.info("mock_appointment_booked", appointment_id=appointment_id)

        return Appointment(
            id=appointment_id,
            driver_id=driver_id,
            driver_name=driver_name,
            truck_number=truck_number,
            appointment_type=appointment_type,
            facility=facility,
            start_time=start_dt,
            end_time=end_dt,
            notes=notes,
            confirmed=True,
        )

    def reschedule_appointment(
        self, appointment_id: str, new_start_time: str, reason: Optional[str] = None
    ) -> bool:
        """
        Reschedule an existing appointment.

        Args:
            appointment_id: Appointment ID to reschedule
            new_start_time: New start time in ISO 8601 format
            reason: Reason for rescheduling

        Returns:
            True if successful
        """
        if not self.service:
            logger.info("mock_appointment_rescheduled", appointment_id=appointment_id)
            return True

        try:
            # Get the existing event
            event = (
                self.service.events()
                .get(calendarId=config.google_calendar_id, eventId=appointment_id)
                .execute()
            )

            # Calculate duration
            start_dt = datetime.fromisoformat(new_start_time)
            original_start = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
            original_end = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
            duration = original_end - original_start

            # Update times
            event["start"]["dateTime"] = start_dt.isoformat()
            event["end"]["dateTime"] = (start_dt + duration).isoformat()

            # Add reason to description
            if reason:
                event["description"] = f"{event.get('description', '')}\nRescheduled: {reason}"

            # Update the event
            self.service.events().update(
                calendarId=config.google_calendar_id, eventId=appointment_id, body=event
            ).execute()

            logger.info("appointment_rescheduled", appointment_id=appointment_id)
            return True

        except HttpError as e:
            logger.error("reschedule_failed", error=str(e))
            return False

    def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel an appointment.

        Args:
            appointment_id: Appointment ID to cancel
            reason: Reason for cancellation

        Returns:
            True if successful
        """
        if not self.service:
            logger.info("mock_appointment_cancelled", appointment_id=appointment_id)
            return True

        try:
            self.service.events().delete(
                calendarId=config.google_calendar_id, eventId=appointment_id
            ).execute()

            logger.info("appointment_cancelled", appointment_id=appointment_id, reason=reason)
            return True

        except HttpError as e:
            logger.error("cancel_failed", error=str(e))
            return False

    def list_appointments(self, driver_id: str, days_ahead: int = 30) -> List[Appointment]:
        """
        List upcoming appointments for a driver.

        Args:
            driver_id: Driver ID
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming appointments
        """
        if not self.service:
            logger.info("mock_appointments_listed", driver_id=driver_id)
            return []

        try:
            time_min = datetime.now()
            time_max = time_min + timedelta(days=days_ahead)

            events_result = (
                self.service.events()
                .list(
                    calendarId=config.google_calendar_id,
                    timeMin=time_min.isoformat() + "Z",
                    timeMax=time_max.isoformat() + "Z",
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            # Filter events for this driver (by checking description)
            appointments = []
            for event in events:
                description = event.get("description", "")
                if driver_id in description:
                    start_dt = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))

                    # Parse appointment type from description
                    appointment_type = AppointmentType.DELIVERY  # default
                    if "maintenance" in description.lower():
                        appointment_type = AppointmentType.MAINTENANCE
                    elif "compliance" in description.lower():
                        appointment_type = AppointmentType.COMPLIANCE

                    appointments.append(
                        Appointment(
                            id=event["id"],
                            driver_id=driver_id,
                            driver_name=event["summary"].split(" - ")[-1],
                            appointment_type=appointment_type,
                            facility=event.get("location", "Unknown"),
                            start_time=start_dt.replace(tzinfo=None),
                            end_time=end_dt.replace(tzinfo=None),
                            confirmed=True,
                        )
                    )

            logger.info("appointments_listed", driver_id=driver_id, count=len(appointments))
            return appointments

        except HttpError as e:
            logger.error("list_appointments_failed", error=str(e))
            return []


# Global calendar instance
_calendar = None


def get_calendar() -> CalendarTool:
    """Get or create the global calendar instance."""
    global _calendar
    if _calendar is None:
        _calendar = CalendarTool()
    return _calendar


# Tool functions that will be exposed to the LLM


def check_availability(request: AvailabilityRequest) -> List[TimeSlot]:
    """Check available appointment slots."""
    calendar = get_calendar()
    return calendar.check_availability(
        date=request.date,
        facility=request.facility,
        appointment_type=request.appointment_type,
        duration_minutes=request.duration_minutes,
    )


def book_appointment(request: BookingRequest) -> Appointment:
    """Book a new appointment."""
    calendar = get_calendar()
    return calendar.book_appointment(
        driver_id=request.driver_id,
        driver_name=request.driver_name,
        truck_number=request.truck_number,
        appointment_type=request.appointment_type,
        facility=request.facility,
        start_time=request.start_time,
        duration_minutes=request.duration_minutes,
        notes=request.notes,
    )


def reschedule_appointment(request: RescheduleRequest) -> bool:
    """Reschedule an existing appointment."""
    calendar = get_calendar()
    return calendar.reschedule_appointment(
        appointment_id=request.appointment_id,
        new_start_time=request.new_start_time,
        reason=request.reason,
    )


def cancel_appointment(request: CancelRequest) -> bool:
    """Cancel an appointment."""
    calendar = get_calendar()
    return calendar.cancel_appointment(
        appointment_id=request.appointment_id, reason=request.reason
    )


def list_appointments(driver_id: str, days_ahead: int = 30) -> List[Appointment]:
    """List upcoming appointments for a driver."""
    calendar = get_calendar()
    return calendar.list_appointments(driver_id=driver_id, days_ahead=days_ahead)
