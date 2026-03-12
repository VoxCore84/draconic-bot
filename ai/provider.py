"""LLM provider abstraction — Gemini implementation via google-genai SDK."""

from __future__ import annotations

import abc
import asyncio
import json
import logging
import time

from ai.schemas import AIResult, CostEstimate, ModelTier, ProviderHealth, RouteType
from ai.settings import (
    AI_RESPONSE_TIMEOUT_SECONDS,
    AI_ROUTE_COMPLEX_MODEL,
    AI_ROUTE_DEFAULT_MODEL,
    AI_ROUTE_PRO_MODEL,
)

log = logging.getLogger(__name__)


def _extract_json(text: str) -> dict | None:
    """Robustly extract JSON from model response.

    Handles: raw JSON, markdown-wrapped JSON, truncated JSON.
    """
    if not text:
        return None

    # Strip markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        # Remove ```json or ``` wrapper
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    # Try direct parse first
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Find first { and try to parse from there
    idx = text.find("{")
    if idx < 0:
        return None
    text = text[idx:]

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    # Truncated JSON recovery: try to extract answer_markdown field
    import re
    md_match = re.search(r'"answer_markdown"\s*:\s*"((?:[^"\\]|\\.)*)', text)
    if md_match:
        answer = md_match.group(1)
        # Unescape JSON string escapes
        answer = answer.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")

        # Try to extract other fields
        conf_match = re.search(r'"confidence"\s*:\s*([\d.]+)', text)
        route_match = re.search(r'"route"\s*:\s*"(\w+)"', text)
        staff_match = re.search(r'"needs_staff"\s*:\s*(true|false)', text)
        kb_match = re.search(r'"used_kb_sections"\s*:\s*\[(.*?)\]', text)

        return {
            "route": route_match.group(1) if route_match else None,
            "confidence": float(conf_match.group(1)) if conf_match else 0.7,
            "needs_staff": staff_match.group(1) == "true" if staff_match else False,
            "answer_markdown": answer,
            "follow_up_question": "",
            "used_kb_sections": json.loads(f"[{kb_match.group(1)}]") if kb_match else [],
            "safety_flags": [],
        }

    return None


# Approximate pricing per million tokens (Gemini 2.5, as of spec date)
_PRICING = {
    "gemini-2.5-flash-lite": {"input": 0.075, "output": 0.30},
    "gemini-2.5-flash":      {"input": 0.15,  "output": 0.60},
    "gemini-2.5-pro":        {"input": 1.25,  "output": 10.00},
}


def _model_name_for_tier(tier: ModelTier) -> str:
    return {
        ModelTier.FLASH_LITE: AI_ROUTE_DEFAULT_MODEL,
        ModelTier.FLASH: AI_ROUTE_COMPLEX_MODEL,
        ModelTier.PRO: AI_ROUTE_PRO_MODEL,
    }[tier]


class LLMProvider(abc.ABC):
    """Abstract LLM provider interface."""

    @abc.abstractmethod
    async def generate(
        self,
        route_type: RouteType,
        model_tier: ModelTier,
        system_prompt: str,
        user_prompt: str,
        conversation_context: list[dict] | None = None,
        max_output_tokens: int = 300,
    ) -> AIResult:
        ...

    @abc.abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int, model_tier: ModelTier) -> CostEstimate:
        ...

    @abc.abstractmethod
    async def healthcheck(self) -> ProviderHealth:
        ...


class GeminiProvider(LLMProvider):
    """Google Gemini provider via google-genai SDK."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client()
        return self._client

    async def generate(
        self,
        route_type: RouteType,
        model_tier: ModelTier,
        system_prompt: str,
        user_prompt: str,
        conversation_context: list[dict] | None = None,
        max_output_tokens: int = 300,
    ) -> AIResult:
        model_name = _model_name_for_tier(model_tier)
        client = self._get_client()

        from google.genai import types

        # Build contents: conversation context + current user message
        contents = []
        if conversation_context:
            for turn in conversation_context:
                contents.append(types.Content(
                    role=turn["role"],
                    parts=[types.Part.from_text(text=turn["content"])],
                ))
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_prompt)],
        ))

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_output_tokens,
            temperature=0.3,
            response_mime_type="application/json",
        )

        start = time.monotonic()
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.models.generate_content,
                    model=model_name,
                    contents=contents,
                    config=config,
                ),
                timeout=AI_RESPONSE_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            return AIResult(
                route=route_type,
                confidence=0.0,
                needs_staff=True,
                answer_markdown="",
                model_used=model_name,
                error="Gemini request timed out",
            )
        except Exception as e:
            log.exception("Gemini API error")
            return AIResult(
                route=route_type,
                confidence=0.0,
                needs_staff=True,
                answer_markdown="",
                model_used=model_name,
                error=str(e),
            )

        latency_ms = int((time.monotonic() - start) * 1000)

        # Parse usage metadata
        input_tokens = 0
        output_tokens = 0
        if response.usage_metadata:
            input_tokens = response.usage_metadata.prompt_token_count or 0
            output_tokens = response.usage_metadata.candidates_token_count or 0

        # Extract text
        raw_text = ""
        if response.candidates and response.candidates[0].content.parts:
            raw_text = response.candidates[0].content.parts[0].text or ""

        # Parse structured JSON response
        parsed = _extract_json(raw_text)
        if parsed is None:
            # If Gemini didn't return valid JSON, treat the raw text as the answer
            return AIResult(
                route=route_type,
                confidence=0.5,
                needs_staff=False,
                answer_markdown=raw_text[:2000],
                model_used=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
            )

        # Use detected route for frustration/log_summary (our heuristics are more
        # reliable than the model's route label for these types)
        model_route = parsed.get("route", route_type.value)
        if route_type in (RouteType.FRUSTRATION, RouteType.LOG_SUMMARY):
            final_route = route_type
        else:
            try:
                final_route = RouteType(model_route)
            except ValueError:
                final_route = route_type

        return AIResult(
            route=final_route,
            confidence=float(parsed.get("confidence", 0.5)),
            needs_staff=bool(parsed.get("needs_staff", False)),
            answer_markdown=str(parsed.get("answer_markdown", ""))[:2000],
            follow_up_question=str(parsed.get("follow_up_question", "")),
            used_kb_sections=parsed.get("used_kb_sections", []),
            safety_flags=parsed.get("safety_flags", []),
            model_used=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int, model_tier: ModelTier) -> CostEstimate:
        model_name = _model_name_for_tier(model_tier)
        pricing = _PRICING.get(model_name, {"input": 0.15, "output": 0.60})
        cost = (input_tokens / 1_000_000 * pricing["input"]) + (output_tokens / 1_000_000 * pricing["output"])
        return CostEstimate(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model_name,
            estimated_usd=cost,
        )

    async def healthcheck(self) -> ProviderHealth:
        start = time.monotonic()
        try:
            client = self._get_client()
            # Quick model list check
            await asyncio.to_thread(lambda: list(client.models.list(config={"page_size": 1})))
            latency = int((time.monotonic() - start) * 1000)
            return ProviderHealth(available=True, latency_ms=latency)
        except Exception as e:
            latency = int((time.monotonic() - start) * 1000)
            return ProviderHealth(available=False, latency_ms=latency, error=str(e))
