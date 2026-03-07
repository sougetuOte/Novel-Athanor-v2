"""Quality Agent prompt formatter.

This module provides functions for formatting ContextBuildResult into
prompt text for the Quality Agent. The Quality Agent needs:
1. The draft text to evaluate
2. Scene requirements (what was requested)
3. Context information (characters, style guide, plot) as evaluation criteria
"""

from src.agents.models.scene_requirements import SceneRequirements
from src.agents.prompts._common import (
    add_character_section,
    add_plot_section,
    add_style_guide_section,
    add_summary_section,
    add_world_setting_section,
    select_context,
)
from src.agents.prompts.ghost_writer import format_scene_requirements
from src.core.context import ContextBuildResult


def format_quality_context(
    result: ContextBuildResult,
    draft_text: str,
    requirements: SceneRequirements,
) -> str:
    """Format ContextBuildResult + draft into Quality Agent prompt text.

    Args:
        result: Context build result from L3.
        draft_text: The draft text to be evaluated.
        requirements: Scene requirements for context.

    Returns:
        Formatted prompt text for Quality Agent.
    """
    ctx = select_context(result)
    sections: list[str] = []

    _add_draft_section(sections, draft_text)
    _add_requirements_section(sections, requirements)
    add_plot_section(sections, ctx)
    add_summary_section(sections, ctx)
    add_character_section(sections, ctx)
    add_world_setting_section(sections, ctx)
    add_style_guide_section(sections, ctx)

    return "\n\n---\n\n".join(sections)


def _add_draft_section(sections: list[str], draft_text: str) -> None:
    """Add the draft text section."""
    sections.append(f"## 評価対象テキスト\n\n{draft_text}")


def _add_requirements_section(
    sections: list[str], requirements: SceneRequirements
) -> None:
    """Add scene requirements section."""
    sections.append(format_scene_requirements(requirements))
