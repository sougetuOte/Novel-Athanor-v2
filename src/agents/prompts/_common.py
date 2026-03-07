"""Common helper functions shared across L4 agent prompt formatters.

These functions build prompt sections from a FilteredContext. They are
used by ghost_writer.py, quality.py, and potentially other formatters.
"""

from src.core.context import ContextBuildResult, FilteredContext


def select_context(result: ContextBuildResult) -> FilteredContext:
    """Select the appropriate context from result.

    Returns visibility-filtered context if available, otherwise base context.

    Args:
        result: Context build result from L3.

    Returns:
        Visibility-filtered context if available, otherwise base context.
    """
    if result.visibility_context is not None:
        return result.visibility_context.base_context
    return result.context


def add_plot_section(sections: list[str], ctx: FilteredContext) -> None:
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


def add_summary_section(sections: list[str], ctx: FilteredContext) -> None:
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


def add_character_section(sections: list[str], ctx: FilteredContext) -> None:
    """Add character information section if characters exist."""
    if not ctx.characters:
        return

    subsections = [f"### {name}\n{info}" for name, info in ctx.characters.items()]
    sections.append("## キャラクター\n\n" + "\n\n".join(subsections))


def add_world_setting_section(sections: list[str], ctx: FilteredContext) -> None:
    """Add world setting information section if settings exist."""
    if not ctx.world_settings:
        return

    subsections = [f"### {name}\n{info}" for name, info in ctx.world_settings.items()]
    sections.append("## 世界観設定\n\n" + "\n\n".join(subsections))


def add_style_guide_section(sections: list[str], ctx: FilteredContext) -> None:
    """Add style guide section if content exists."""
    if ctx.style_guide:
        sections.append(f"## スタイルガイド\n{ctx.style_guide}")
