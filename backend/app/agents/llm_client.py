"""Shared LLM client for all agents."""

import asyncio
import logging
import re
import time
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResult:
    content: str
    tokens: int
    execution_time_ms: float


def sanitize_input(text: str) -> str:
    """Basic prompt injection protection."""
    cleaned = re.sub(r"(?i)(ignore previous|system:|assistant:|<\|)", "", text)
    return cleaned[:8000]


class LLMClient:
    async def complete(self, prompt: str, system: str = "") -> LLMResult:
        start = time.perf_counter()
        safe_prompt = sanitize_input(prompt)
        safe_system = sanitize_input(system)

        has_openai = bool(settings.openai_api_key and not settings.openai_api_key.startswith("sk-..."))
        has_anthropic = bool(settings.anthropic_api_key and not settings.anthropic_api_key.startswith("sk-ant-..."))

        try:
            if settings.ai_provider == "anthropic" and has_anthropic:
                result = await asyncio.wait_for(
                    self._call_anthropic(safe_system, safe_prompt),
                    timeout=settings.llm_timeout_seconds,
                )
            elif has_openai:
                result = await asyncio.wait_for(
                    self._call_openai(safe_system, safe_prompt),
                    timeout=settings.llm_timeout_seconds,
                )
            else:
                result = self._mock_response(safe_prompt)
        except asyncio.TimeoutError:
            logger.warning(
                "LLM call timed out, using mock response",
                extra={"timeout_s": settings.llm_timeout_seconds},
            )
            result = self._mock_response(safe_prompt)
        except Exception as exc:
            logger.warning("LLM call failed, using mock response", extra={"error": str(exc)})
            result = self._mock_response(safe_prompt)

        result.execution_time_ms = round((time.perf_counter() - start) * 1000, 2)
        return result

    async def _call_openai(self, system: str, prompt: str) -> LLMResult:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.3,
        )
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else len(content.split())
        return LLMResult(content=content, tokens=tokens, execution_time_ms=0)

    async def _call_anthropic(self, system: str, prompt: str) -> LLMResult:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            system=system or "You are a helpful sales AI agent.",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text if response.content else ""
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return LLMResult(content=content, tokens=tokens, execution_time_ms=0)

    def _mock_response(self, prompt: str) -> LLMResult:
        """Deterministic fallback when no API key is configured."""
        logger.warning("No LLM API key configured — using mock response")
        if "score" in prompt.lower() or "lead" in prompt.lower():
            content = '{"lead_score": 85, "summary": "Strong lead with verified company profile."}'
        elif "qualif" in prompt.lower():
            content = '{"qualified": true, "confidence_score": 0.92, "summary": "Lead meets qualification criteria."}'
        elif "requirement" in prompt.lower():
            content = '{"requirements": "Standard ambulance configuration with medical equipment.", "summary": "Requirements captured."}'
        elif "pric" in prompt.lower() or "bom" in prompt.lower():
            content = '{"summary": "Quotation generated with standard pricing."}'
        elif "order" in prompt.lower():
            content = '{"summary": "Order created and sent to ERP."}'
        elif "deliver" in prompt.lower():
            content = '{"summary": "Delivery plan scheduled."}'
        else:
            content = '{"summary": "Agent execution completed successfully."}'
        return LLMResult(content=content, tokens=100, execution_time_ms=0)
