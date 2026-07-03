"""
OpenAI Provider — calls OpenAI API directly.

Used when --auto flag is passed to the build command.
Requires OPENAI_API_KEY environment variable or Config entry.
"""

import os
import json
from . import Provider, ProviderConfig, GenerationResult


# Try to import openai; fail gracefully if not installed
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# Approximate pricing per 1K tokens (as of 2025)
PRICING = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "default": {"input": 0.003, "output": 0.015},
}


class OpenAIProvider(Provider):
    """Calls OpenAI API for extraction and generation."""

    def __init__(self, config: ProviderConfig):
        self._config = config
        api_key = config.api_key or os.environ.get("OPENAI_API_KEY", "")
        if HAS_OPENAI:
            self._client = openai.OpenAI(api_key=api_key)
        self._has_client = HAS_OPENAI and bool(api_key)

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._config.model

    def generate(self, prompt: str, input_text: str, system_hint: str = "") -> GenerationResult:
        if not self._has_client:
            return GenerationResult(
                success=False,
                output="",
                provider="openai",
                model=self._config.model,
                error="OpenAI client not available. Install: pip install openai, set OPENAI_API_KEY",
            )

        messages = []
        if system_hint:
            messages.append({"role": "system", "content": system_hint})
        messages.append({"role": "user", "content": f"{prompt}\n\n{input_text}"})

        try:
            response = self._client.chat.completions.create(
                model=self._config.model,
                messages=messages,
                temperature=0.0,  # deterministic for extraction
            )
            result = response.choices[0].message.content
            usage = response.usage

            return GenerationResult(
                success=True,
                output=result or "",
                provider="openai",
                model=self._config.model,
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                cost_estimate=self.estimate_cost(
                    usage.prompt_tokens if usage else 0,
                    usage.completion_tokens if usage else 0,
                ),
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                output="",
                provider="openai",
                model=self._config.model,
                error=str(e),
            )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = PRICING.get(self._config.model, PRICING["default"])
        return (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
