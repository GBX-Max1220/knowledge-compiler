"""
Knowledge Compiler — Provider Interface

All LLM providers implement this interface.
The build system selects a provider via compiler.yaml.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderConfig:
    """Configuration for a single provider."""
    name: str           # "reasonix" | "openai" | "claude" | "openrouter"
    model: str          # model identifier
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    max_retries: int = 3
    timeout_sec: int = 120


@dataclass
class GenerationResult:
    """Result from a provider generation call."""
    success: bool
    output: str                 # generated text / YAML
    provider: str               # which provider was used
    model: str                  # which model was used
    input_tokens: int = 0
    output_tokens: int = 0
    cost_estimate: float = 0.0  # estimated cost in USD
    error: Optional[str] = None


class Provider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, input_text: str, system_hint: str = "") -> GenerationResult:
        """Run a prompt against input text and return structured output."""
        ...

    @abstractmethod
    def estimate_cost(self, input_chars: int, output_chars: int) -> float:
        """Estimate API cost for a given input/output size."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...
