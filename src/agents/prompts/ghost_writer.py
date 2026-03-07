"""Ghost Writer prompt formatter.

This module provides functions for formatting ContextBuildResult into
prompt text for the Ghost Writer agent.
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
from src.core.context import ContextBuildResult


def format_scene_requirements(requirements: SceneRequirements) -> str:
    """Format SceneRequirements into Markdown text.

    Args:
        requirements: Scene requirements to format.

    Returns:
        Formatted Markdown text.
    """
    lines = ["## シーン要件", ""]
    lines.append(f"- episode_id: {requirements.episode_id}")

    if requirements.sequence_id is not None:
        lines.append(f"- sequence_id: {requirements.sequence_id}")
    if requirements.chapter_id is not None:
        lines.append(f"- chapter_id: {requirements.chapter_id}")
    if requirements.current_phase is not None:
        lines.append(f"- current_phase: {requirements.current_phase}")

    lines.append(f"- word_count: {requirements.word_count}")
    lines.append(f"- pov: {requirements.pov}")

    if requirements.mood is not None:
        lines.append(f"- mood: {requirements.mood}")
    if requirements.special_instructions is not None:
        lines.append(f"- special_instructions: {requirements.special_instructions}")

    return "\n".join(lines)


def format_writing_context(
    result: ContextBuildResult,
    requirements: SceneRequirements,
) -> str:
    """Format ContextBuildResult into Ghost Writer prompt text.

    Args:
        result: Context build result from L3.
        requirements: Scene requirements for the Ghost Writer.

    Returns:
        Formatted prompt text for Ghost Writer agent.
    """
    ctx = select_context(result)
    sections: list[str] = []

    # Build each section only if content is available
    add_plot_section(sections, ctx)
    add_summary_section(sections, ctx)
    add_character_section(sections, ctx)
    add_world_setting_section(sections, ctx)
    add_style_guide_section(sections, ctx)
    _add_foreshadowing_section(sections, result)
    _add_forbidden_keywords_section(sections, result)
    _add_requirements_section(sections, requirements)

    return "\n\n---\n\n".join(sections)


def _add_foreshadowing_section(
    sections: list[str], result: ContextBuildResult
) -> None:
    """Add foreshadowing instructions section if active instructions exist."""
    active_instructions = result.foreshadow_instructions.get_active_instructions()
    if not active_instructions:
        return

    lines = []
    for instr in active_instructions:
        note = instr.note if instr.note else "(指示なし)"
        lines.append(f"- {instr.foreshadowing_id}: {instr.action.value} — {note}")

    sections.append("## 伏線指示\n" + "\n".join(lines))


def _add_forbidden_keywords_section(
    sections: list[str], result: ContextBuildResult
) -> None:
    """Add forbidden keywords section if keywords exist."""
    if not result.forbidden_keywords:
        return

    lines = [f"- {kw}" for kw in result.forbidden_keywords]
    sections.append("## 禁止キーワード（絶対に使用しないこと）\n" + "\n".join(lines))


def _add_requirements_section(
    sections: list[str], requirements: SceneRequirements
) -> None:
    """Add scene requirements section."""
    sections.append(format_scene_requirements(requirements))
