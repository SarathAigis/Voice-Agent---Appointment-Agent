"""Voicemail detection and handling."""

import structlog
from typing import Optional

from ..config import config
from .sms import get_sms_service

logger = structlog.get_logger(__name__)


class VoicemailDetector:
    """Handles voicemail detection and appropriate responses."""

    def __init__(self):
        """Initialize voicemail detector."""
        self.sms_service = get_sms_service()

    def handle_voicemail(
        self,
        call_sid: str,
        driver_name: str,
        driver_phone: str,
        call_purpose: str,
    ) -> bool:
        """
        Handle when voicemail is detected.

        Actions:
        1. Leave voicemail message
        2. Send SMS followup
        3. Log the event

        Args:
            call_sid: Twilio call SID
            driver_name: Driver's name
            driver_phone: Driver's phone number
            call_purpose: Purpose of the call

        Returns:
            True if handled successfully
        """
        logger.info(
            "voicemail_detected",
            call_sid=call_sid,
            driver=driver_name,
        )

        # Send SMS followup
        sms_sent = self.sms_service.send_voicemail_followup(
            phone=driver_phone,
            driver_name=driver_name,
            reason=call_purpose,
        )

        if sms_sent:
            logger.info(
                "voicemail_followup_sent",
                call_sid=call_sid,
                driver=driver_name,
            )

        return sms_sent

    def get_voicemail_message(self) -> str:
        """
        Get the voicemail message to leave.

        Returns:
            Voicemail message text
        """
        return config.voicemail_message

    def is_voicemail(self, answering_machine_detection: str) -> bool:
        """
        Determine if call went to voicemail based on AMD result.

        Args:
            answering_machine_detection: AMD result from Twilio
                - "human" = Human answered
                - "machine_start" = Machine detected, message starting
                - "machine_end_beep" = Machine detected, beep occurred
                - "machine_end_silence" = Machine detected, silence after message
                - "machine_end_other" = Machine detected, other end signal
                - "fax" = Fax machine detected
                - "unknown" = Could not determine

        Returns:
            True if voicemail, False otherwise
        """
        voicemail_indicators = [
            "machine_start",
            "machine_end_beep",
            "machine_end_silence",
            "machine_end_other",
        ]

        is_vm = answering_machine_detection in voicemail_indicators

        logger.info(
            "voicemail_detection_result",
            amd_result=answering_machine_detection,
            is_voicemail=is_vm,
        )

        return is_vm


# Global voicemail detector instance
_detector = None


def get_voicemail_detector() -> VoicemailDetector:
    """Get or create the global voicemail detector instance."""
    global _detector
    if _detector is None:
        _detector = VoicemailDetector()
    return _detector
