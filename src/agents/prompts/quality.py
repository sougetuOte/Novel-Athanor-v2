"""Quality Agent prompt formatter.

This module provides functions for formatting ContextBuildResult into
prompt text for the Quality Agent. The Quality Agent needs:
1. The draft text to evaluate
2. Scene requirements (what was requested)
3. Context information (characters, style guide, plot) as evaluation criteria
"""

from src.agents.models.scene_requirements import SceneRequirements
from src.agents.prompts.ghost_writer import format_scene_requirements
from src.core.context import ContextBuildResult, FilteredContext


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
    ctx = _select_context(result)
    sections: list[str] = []

    _add_draft_section(sections, draft_text)
    _add_requirements_section(sections, requirements)
    _add_plot_section(sections, ctx)
    _add_summary_section(sections, ctx)
    _add_character_section(sections, ctx)
    _add_world_setting_section(sections, ctx)
    _add_style_guide_section(sections, ctx)

    return "\n\n---\n\n".join(sections)


def _select_context(result: ContextBuildResult) -> FilteredContext:
    """Select the appropriate context from result."""
    if result.visibility_context is not None:
        return result.visibility_context.base_context
    return result.context


def _add_draft_section(sections: list[str], draft_text: str) -> None:
    """Add the draft text section."""
    sections.append(f"## 評価対象テキスト\n\n{draft_text}")


def _add_requirements_section(
    sections: list[str], requirements: SceneRequirements
) -> None:
    """Add scene requirements section."""
    sections.append(format_scene_requirements(requirements))


def _add_plot_section(sections: list[str], ctx: FilteredContext) -> None:
    """Add plot information section if content exists."""
    subsections = []
    if ctx.plot_l1:
        subsections.append(f"### L1 (全体)\n{ctx.plot_l1}")
    if ctx.plot_l2:
        subsections.append(f"### L2 (章)\n{ctx.plot_l2}")
    if ctx.plot_l3:
        subsections.append(f"### L3 (シーン)\n{ctx.plot_l3}")

    if subsections:
        sections.append("## プロット情報\n\n" + "\n\n".join(subsections))


def _add_summary_section(sections: list[str], ctx: FilteredContext) -> None:
    """Add summary information section if content exists."""
    subsections = []
    if ctx.summary_l1:
        subsections.append(f"### 全体サマリ\n{ctx.summary_l1}")
    if ctx.summary_l2:
        subsections.append(f"### 章サマリ\n{ctx.summary_l2}")
    if ctx.summary_l3:
        subsections.append(f"### 直近シーン\n{ctx.summary_l3}")

    if subsections:
        sections.append("## サマリ情報\n\n" + "\n\n".join(subsections))


def _add_character_section(sections: list[str], ctx: FilteredContext) -> None:
    """Add character information section if characters exist."""
    if not ctx.characters:
        return
    subsections = [f"### {name}\n{info}" for name, info in ctx.characters.items()]
    sections.append("## キャラクター\n\n" + "\n\n".join(subsections))


def _add_world_setting_section(sections: list[str], ctx: FilteredContext) -> None:
    """Add world setting information section if settings exist."""
    if not ctx.world_settings:
        return
    subsections = [f"### {name}\n{info}" for name, info in ctx.world_settings.items()]
    sections.append("## 世界観設定\n\n" + "\n\n".join(subsections))


def _add_style_guide_section(sections: list[str], ctx: FilteredContext) -> None:
    """Add style guide section if content exists."""
    if ctx.style_guide:
        sections.append(f"## スタイルガイド\n{ctx.style_guide}")
