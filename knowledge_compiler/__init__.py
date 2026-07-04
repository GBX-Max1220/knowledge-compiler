"""
Knowledge Compiler — typed, validated, machine-readable knowledge objects.

Transforms expert textbooks into deterministic, agent-accessible knowledge bases.
"""

from .skill import Skill, UnknownObjectError

__version__ = "0.1.0"
__all__ = ["Skill", "UnknownObjectError"]
