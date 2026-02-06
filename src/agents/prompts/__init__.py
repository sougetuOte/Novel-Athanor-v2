"""L4 Agent prompt formatters.

This module provides formatters for converting ContextBuildResult into
prompt text for various L4 agents.
"""

from .ghost_writer import format_scene_requirements, format_writing_context
from .quality import format_quality_context
from .reviewer import format_review_context
from .style_agent import format_style_analysis_context

__all__ = [
    "format_quality_context",
    "format_review_context",
    "format_scene_requirements",
    "format_style_analysis_context",
    "format_writing_context",
]
