"""
Reasonix Provider — writes prompt+input files for CLI execution.

The Reasonix provider does NOT make API calls.
Instead, it prepares structured .prompt files that can be:
  - Executed manually via Reasonix CLI
  - Queued for batch execution
  - Audited before running

This is the DEFAULT provider for the Knowledge Compiler.
"""

import os
from datetime import datetime
from . import Provider, ProviderConfig, GenerationResult


class ReasonixProvider(Provider):
    """
    Writes prompt+input pairs as .prompt files for Reasonix CLI execution.
    
    These files contain:
      - The system prompt (from prompts/{stage}.md)
      - The input text (from the chunk/extraction file)
      - Metadata for tracking
    """

    def __init__(self, config: ProviderConfig):
        self._config = config
        self._prompt_dir = None  # set by build system

    @property
    def name(self) -> str:
        return "reasonix"

    @property
    def model_name(self) -> str:
        return self._config.model

    def generate(self, prompt: str, input_text: str, system_hint: str = "") -> GenerationResult:
        """
        Write a .prompt file instead of calling an API.
        Returns a GenerationResult with the file path as output.
        """
        file_id = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{abs(hash(input_text[:50])) % 10000:04d}'
        filename = f"{file_id}.prompt"
        
        if self._prompt_dir:
            filepath = os.path.join(self._prompt_dir, filename)
        else:
            filepath = filename

        content = f"""# Knowledge Compiler — Prompt File
# Provider: reasonix
# Model: {self._config.model}
# Created: {datetime.now().isoformat()}

## System Prompt
{system_hint or prompt}

## Task
{prompt}

## Input
{input_text}

## Instructions
Run this file with Reasonix CLI or copy the prompt to your preferred model.
Output should be written to the file specified in the task.
"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return GenerationResult(
            success=True,
            output=f"Prompt file written: {filepath}",
            provider="reasonix",
            model=self._config.model,
            error=None,
        )

    def estimate_cost(self, input_chars: int, output_chars: int) -> float:
        """Reasonix usage is not metered per-call in the same way.
        Return 0 and log approximate token count for monitoring."""
        return 0.0

    def set_prompt_dir(self, path: str):
        """Set the directory where .prompt files will be written."""
        self._prompt_dir = path
        os.makedirs(path, exist_ok=True)
