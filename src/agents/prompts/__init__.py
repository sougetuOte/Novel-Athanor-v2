"""L4 Agent prompt formatters.

This module provides formatters for converting ContextBuildResult into
prompt text for various L4 agents.
"""

from .ghost_writer import format_scene_requirements, format_writing_context
from .reviewer import format_review_context

__all__ = [
    "format_review_context",
    "format_scene_requirements",
    "format_writing_context",
]
