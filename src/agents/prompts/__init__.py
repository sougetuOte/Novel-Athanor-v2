"""L4 Agent prompt formatters.

This module provides formatters for converting ContextBuildResult into
prompt text for various L4 agents.
"""

from .ghost_writer import format_scene_requirements, format_writing_context

__all__ = [
    "format_scene_requirements",
    "format_writing_context",
]
