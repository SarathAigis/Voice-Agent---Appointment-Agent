"""Langfuse tracing for conversation monitoring."""

import structlog
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from functools import wraps
import time

from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe

from ..config import config

logger = structlog.get_logger(__name__)


class LangfuseTracer:
    """Manages Langfuse tracing for conversations."""

    def __init__(self):
        """Initialize Langfuse client."""
        if config.langfuse_enabled:
            self.client = Langfuse(
                public_key=config.langfuse_public_key,
                secret_key=config.langfuse_secret_key,
                host=config.langfuse_host,
            )
            logger.info("langfuse_initialized", host=config.langfuse_host)
        else:
            self.client = None
            logger.info("langfuse_disabled")

        self.active_traces: Dict[str, Any] = {}

    def start_conversation_trace(
        self,
        call_id: str,
        driver_id: str,
        driver_name: str,
        call_purpose: str,
        metadata: Dict = None,
    ) -> Optional[Any]:
        """
        Start a new conversation trace.

        Args:
            call_id: Unique call identifier
            driver_id: Driver ID
            driver_name: Driver name
            call_purpose: Purpose of the call
            metadata: Additional metadata

        Returns:
            Trace object or None if disabled
        """
        if not self.client:
            return None

        try:
            trace = self.client.trace(
                name=f"call_{call_id}",
                user_id=driver_id,
                session_id=call_id,
                metadata={
                    "driver_name": driver_name,
                    "call_purpose": call_purpose,
                    "start_time": datetime.now().isoformat(),
                    **(metadata or {}),
                },
                tags=["voice_call", "appointment_scheduling"],
            )

            self.active_traces[call_id] = trace

            logger.info(
                "conversation_trace_started",
                call_id=call_id,
                driver=driver_name,
            )

            return trace

        except Exception as e:
            logger.error("trace_start_failed", call_id=call_id, error=str(e))
            return None

    def log_stt_event(
        self,
        call_id: str,
        transcript: str,
        confidence: float,
        duration_ms: int,
        metadata: Dict = None,
    ):
        """
        Log a speech-to-text event.

        Args:
            call_id: Call identifier
            transcript: Transcribed text
            confidence: Confidence score
            duration_ms: Audio duration
            metadata: Additional metadata
        """
        if not self.client or call_id not in self.active_traces:
            return

        try:
            trace = self.active_traces[call_id]

            trace.span(
                name="stt_transcription",
                metadata={
                    "transcript": transcript,
                    "confidence": confidence,
                    "duration_ms": duration_ms,
                    "model": config.deepgram_model,
                    **(metadata or {}),
                },
            )

        except Exception as e:
            logger.error("stt_log_failed", call_id=call_id, error=str(e))

    def log_llm_call(
        self,
        call_id: str,
        prompt: str,
        response: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        metadata: Dict = None,
    ):
        """
        Log an LLM API call.

        Args:
            call_id: Call identifier
            prompt: Input prompt
            response: Model response
            model: Model name
            input_tokens: Input token count
            output_tokens: Output token count
            latency_ms: Latency in milliseconds
            metadata: Additional metadata
        """
        if not self.client or call_id not in self.active_traces:
            return

        try:
            trace = self.active_traces[call_id]

            # Calculate cost
            input_cost = (input_tokens / 1000) * config.cost_gpt4o_input_per_1k
            output_cost = (output_tokens / 1000) * config.cost_gpt4o_output_per_1k
            total_cost = input_cost + output_cost

            trace.generation(
                name="llm_response",
                model=model,
                input=prompt,
                output=response,
                usage={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens,
                },
                metadata={
                    "latency_ms": latency_ms,
                    "cost_usd": total_cost,
                    **(metadata or {}),
                },
            )

        except Exception as e:
            logger.error("llm_log_failed", call_id=call_id, error=str(e))

    def log_tool_call(
        self,
        call_id: str,
        tool_name: str,
        input_args: Dict,
        output: Any,
        success: bool,
        latency_ms: int,
        metadata: Dict = None,
    ):
        """
        Log a tool/function call.

        Args:
            call_id: Call identifier
            tool_name: Name of the tool
            input_args: Tool input arguments
            output: Tool output
            success: Whether tool call succeeded
            latency_ms: Latency in milliseconds
            metadata: Additional metadata
        """
        if not self.client or call_id not in self.active_traces:
            return

        try:
            trace = self.active_traces[call_id]

            trace.span(
                name=f"tool_{tool_name}",
                metadata={
                    "tool": tool_name,
                    "input": input_args,
                    "output": str(output),
                    "success": success,
                    "latency_ms": latency_ms,
                    **(metadata or {}),
                },
                level="DEFAULT" if success else "ERROR",
            )

        except Exception as e:
            logger.error("tool_log_failed", call_id=call_id, error=str(e))

    def log_tts_event(
        self,
        call_id: str,
        text: str,
        char_count: int,
        duration_ms: int,
        metadata: Dict = None,
    ):
        """
        Log a text-to-speech event.

        Args:
            call_id: Call identifier
            text: Text being synthesized
            char_count: Character count
            duration_ms: Generation duration
            metadata: Additional metadata
        """
        if not self.client or call_id not in self.active_traces:
            return

        try:
            trace = self.active_traces[call_id]

            # Calculate cost
            cost = (char_count / 1000) * config.cost_elevenlabs_per_1k_chars

            trace.span(
                name="tts_synthesis",
                metadata={
                    "text": text,
                    "char_count": char_count,
                    "duration_ms": duration_ms,
                    "model": config.elevenlabs_model,
                    "cost_usd": cost,
                    **(metadata or {}),
                },
            )

        except Exception as e:
            logger.error("tts_log_failed", call_id=call_id, error=str(e))

    def log_fallback_event(
        self,
        call_id: str,
        trigger: str,
        from_state: str,
        to_state: str,
        reason: str = None,
    ):
        """
        Log a fallback state transition.

        Args:
            call_id: Call identifier
            trigger: What triggered the fallback
            from_state: Previous state
            to_state: New state
            reason: Reason for fallback
        """
        if not self.client or call_id not in self.active_traces:
            return

        try:
            trace = self.active_traces[call_id]

            trace.event(
                name="fallback_transition",
                metadata={
                    "trigger": trigger,
                    "from_state": from_state,
                    "to_state": to_state,
                    "reason": reason,
                },
            )

        except Exception as e:
            logger.error("fallback_log_failed", call_id=call_id, error=str(e))

    def end_conversation_trace(
        self,
        call_id: str,
        outcome: str,
        duration_seconds: int,
        total_cost: float = None,
        metadata: Dict = None,
    ):
        """
        End a conversation trace.

        Args:
            call_id: Call identifier
            outcome: Call outcome (completed, failed, escalated, etc.)
            duration_seconds: Total call duration
            total_cost: Total cost in USD
            metadata: Additional metadata
        """
        if not self.client or call_id not in self.active_traces:
            return

        try:
            trace = self.active_traces[call_id]

            trace.update(
                output={"outcome": outcome},
                metadata={
                    "end_time": datetime.now().isoformat(),
                    "duration_seconds": duration_seconds,
                    "total_cost_usd": total_cost,
                    "outcome": outcome,
                    **(metadata or {}),
                },
            )

            # Remove from active traces
            del self.active_traces[call_id]

            logger.info(
                "conversation_trace_ended",
                call_id=call_id,
                outcome=outcome,
                duration=duration_seconds,
            )

        except Exception as e:
            logger.error("trace_end_failed", call_id=call_id, error=str(e))

    def flush(self):
        """Flush any pending traces to Langfuse."""
        if self.client:
            try:
                self.client.flush()
                logger.info("langfuse_flushed")
            except Exception as e:
                logger.error("flush_failed", error=str(e))


# Global tracer instance
_tracer = None


def get_tracer() -> LangfuseTracer:
    """Get or create the global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = LangfuseTracer()
    return _tracer


# Decorators for easy tracing


def traced_function(func_name: str = None):
    """
    Decorator to trace a function execution.

    Args:
        func_name: Optional name for the span (uses function name if not provided)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = func_name or func.__name__
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                latency_ms = int((time.time() - start_time) * 1000)

                # Log to tracer if call_id is available
                if "call_id" in kwargs:
                    tracer = get_tracer()
                    tracer.log_tool_call(
                        call_id=kwargs["call_id"],
                        tool_name=name,
                        input_args={k: v for k, v in kwargs.items() if k != "call_id"},
                        output=result,
                        success=True,
                        latency_ms=latency_ms,
                    )

                return result

            except Exception as e:
                latency_ms = int((time.time() - start_time) * 1000)

                if "call_id" in kwargs:
                    tracer = get_tracer()
                    tracer.log_tool_call(
                        call_id=kwargs["call_id"],
                        tool_name=name,
                        input_args={k: v for k, v in kwargs.items() if k != "call_id"},
                        output=str(e),
                        success=False,
                        latency_ms=latency_ms,
                    )

                raise

        return wrapper

    return decorator


def traced_llm_call(func: Callable) -> Callable:
    """Decorator to trace LLM calls."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Implementation would wrap LLM call and log tokens/latency
        return func(*args, **kwargs)

    return wrapper


def traced_tool_call(tool_name: str):
    """Decorator to trace tool calls."""
    return traced_function(tool_name)
