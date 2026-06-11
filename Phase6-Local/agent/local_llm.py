"""Local LLM integration using Ollama."""

import structlog
import httpx
import json
from typing import List, Dict, Any

from .config import config

logger = structlog.get_logger(__name__)


class LocalLLM:
    """Local LLM client for Ollama."""

    def __init__(self):
        """Initialize Ollama client."""
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model

        logger.info(
            "ollama_client_initialized",
            base_url=self.base_url,
            model=self.model,
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Send a chat request to Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional tool definitions
            temperature: Sampling temperature

        Returns:
            Response dict with 'content' and optional 'tool_calls'
        """
        logger.info("llm_request", messages_count=len(messages))

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )

            response.raise_for_status()
            result = response.json()

            message = result.get("message", {})
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            logger.info(
                "llm_response",
                content_length=len(content),
                tool_calls_count=len(tool_calls),
            )

            return {
                "content": content,
                "tool_calls": tool_calls,
            }

    def build_system_prompt(self) -> str:
        """Build system prompt for appointment scheduling."""
        return """You are a professional scheduling assistant calling truck drivers to manage their appointments.

CONTEXT:
- Driver is likely on the road (keep it brief)
- Background noise expected (engine, road, CB radio)
- Driver may need to interrupt to focus on driving

YOUR STYLE:
- Friendly but efficient
- Responses under 2 sentences
- One question at a time
- Confirm by repeating back key details
- Use simple, clear language

APPOINTMENT TYPES:
- Delivery slots (pickup/dropoff at warehouses)
- Maintenance (truck service)
- Compliance (DOT inspections, medical)

AVAILABLE TOOLS:
- check_availability: Find open time slots
- book_appointment: Create new appointment
- reschedule_appointment: Change existing appointment
- cancel_appointment: Cancel appointment

CONVERSATION RULES:
- Always confirm appointment details by repeating them
- Offer max 3 time slot options (don't overwhelm)
- If driver can't hear you, offer SMS fallback
- If driver seems frustrated, offer callback from human dispatcher
- End with "Safe travels" or similar

Remember: This is a VOICE call. Be conversational, not robotic."""
