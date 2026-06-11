"""SMS messaging functionality via Twilio."""

import structlog
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from ..config import config

logger = structlog.get_logger(__name__)


class SMSMessage(BaseModel):
    """SMS message details."""

    to: str
    body: str
    from_: Optional[str] = None


class SMSService:
    """Handles SMS messaging via Twilio."""

    def __init__(self):
        """Initialize Twilio SMS client."""
        self.client = Client(config.twilio_account_sid, config.twilio_auth_token)
        self.from_number = config.sms_from_number or config.twilio_phone_number

    def send_appointment_confirmation(
        self,
        phone: str,
        driver_name: str,
        appointment_type: str,
        facility: str,
        date: str,
        time: str,
    ) -> bool:
        """
        Send appointment confirmation SMS.

        Args:
            phone: Driver's phone number
            driver_name: Driver's name
            appointment_type: Type of appointment
            facility: Facility name
            date: Appointment date (human readable)
            time: Appointment time (human readable)

        Returns:
            True if sent successfully, False otherwise
        """
        message_body = (
            f"Hi {driver_name}, your {appointment_type} appointment is confirmed:\n"
            f"📍 {facility}\n"
            f"📅 {date} at {time}\n"
            f"Reply HELP for assistance or CANCEL to cancel."
        )

        return self.send_sms(phone, message_body)

    def send_reschedule_confirmation(
        self,
        phone: str,
        driver_name: str,
        old_date: str,
        old_time: str,
        new_date: str,
        new_time: str,
        facility: str,
    ) -> bool:
        """
        Send reschedule confirmation SMS.

        Args:
            phone: Driver's phone number
            driver_name: Driver's name
            old_date: Original date
            old_time: Original time
            new_date: New date
            new_time: New time
            facility: Facility name

        Returns:
            True if sent successfully
        """
        message_body = (
            f"Hi {driver_name}, your appointment has been rescheduled:\n"
            f"From: {old_date} at {old_time}\n"
            f"To: {new_date} at {new_time}\n"
            f"📍 {facility}"
        )

        return self.send_sms(phone, message_body)

    def send_cancellation_confirmation(
        self,
        phone: str,
        driver_name: str,
        appointment_type: str,
        date: str,
        time: str,
    ) -> bool:
        """
        Send cancellation confirmation SMS.

        Args:
            phone: Driver's phone number
            driver_name: Driver's name
            appointment_type: Type of appointment
            date: Appointment date
            time: Appointment time

        Returns:
            True if sent successfully
        """
        message_body = (
            f"Hi {driver_name}, your {appointment_type} appointment on {date} at {time} "
            f"has been cancelled. Call us to reschedule: {self.from_number}"
        )

        return self.send_sms(phone, message_body)

    def send_voicemail_followup(
        self,
        phone: str,
        driver_name: str,
        reason: str,
    ) -> bool:
        """
        Send SMS after voicemail is detected.

        Args:
            phone: Driver's phone number
            driver_name: Driver's name
            reason: Reason for the call

        Returns:
            True if sent successfully
        """
        message_body = (
            f"Hi {driver_name}, we tried calling you about {reason}. "
            f"Please call us back at {self.from_number} or reply to this message."
        )

        return self.send_sms(phone, message_body)

    def send_failed_call_followup(
        self,
        phone: str,
        driver_name: str,
        reason: str,
    ) -> bool:
        """
        Send SMS after call fails to connect.

        Args:
            phone: Driver's phone number
            driver_name: Driver's name
            reason: Reason for the call

        Returns:
            True if sent successfully
        """
        message_body = (
            f"Hi {driver_name}, we couldn't reach you about {reason}. "
            f"Please call us at {self.from_number} to discuss."
        )

        return self.send_sms(phone, message_body)

    def send_sms(self, to: str, body: str) -> bool:
        """
        Send an SMS message.

        Args:
            to: Recipient phone number
            body: Message body

        Returns:
            True if sent successfully, False otherwise
        """
        if not config.twilio_enable_sms:
            logger.info("sms_disabled", to=to)
            return False

        try:
            message = self.client.messages.create(
                to=to,
                from_=self.from_number,
                body=body,
            )

            logger.info(
                "sms_sent",
                to=to,
                message_sid=message.sid,
                status=message.status,
            )

            return True

        except TwilioRestException as e:
            logger.error(
                "sms_send_failed",
                to=to,
                error=str(e),
            )
            return False


# Global SMS service instance
_sms_service = None


def get_sms_service() -> SMSService:
    """Get or create the global SMS service instance."""
    global _sms_service
    if _sms_service is None:
        _sms_service = SMSService()
    return _sms_service
