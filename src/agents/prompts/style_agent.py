"""Style Agent prompt formatter.

This module provides functions for formatting episode texts and existing
StyleGuide into prompt text for the Style Agent.
"""

from src.core.models.style import StyleGuide


def format_style_analysis_context(
    episode_texts: list[str],
    existing_guide: StyleGuide | None = None,
) -> str:
    """Format episode texts and existing StyleGuide into Style Agent prompt text.

    Args:
        episode_texts: List of episode texts to analyze.
        existing_guide: Existing StyleGuide if available (for differential update).

    Returns:
        Formatted prompt text for Style Agent.

    Raises:
        ValueError: If episode_texts is empty.
    """
    if not episode_texts:
        raise ValueError("episode_texts cannot be empty")

    sections: list[str] = []

    _add_analysis_text_section(sections, episode_texts)
    _add_existing_guide_section(sections, existing_guide)

    return "\n\n---\n\n".join(sections)


def _add_analysis_text_section(sections: list[str], episode_texts: list[str]) -> None:
    """Add the analysis target text section."""
    lines = ["## 分析対象テキスト", ""]

    for i, text in enumerate(episode_texts, start=1):
        lines.append(f"### エピソード {i}")
        lines.append("")
        lines.append(text)
        lines.append("")

    sections.append("\n".join(lines).rstrip())


def _add_existing_guide_section(
    sections: list[str], existing_guide: StyleGuide | None
) -> None:
    """Add existing StyleGuide section if it exists."""
    if existing_guide is None:
        return

    lines = ["## 既存スタイルガイド", ""]
    lines.append(f"- POV: {existing_guide.pov.value}")
    lines.append(f"- 時制: {existing_guide.tense.value}")

    if existing_guide.style_characteristics:
        lines.append("- スタイル特徴:")
        for char in existing_guide.style_characteristics:
            lines.append(f"  - {char}")

    if existing_guide.description_tendencies:
        lines.append("- 描写傾向:")
        for tendency in existing_guide.description_tendencies:
            lines.append(f"  - {tendency}")

    if existing_guide.avoid_expressions:
        lines.append("- 避けるべき表現:")
        for expr in existing_guide.avoid_expressions:
            lines.append(f"  - {expr}")

    if existing_guide.notes:
        lines.append(f"- 注記: {existing_guide.notes}")

    sections.append("\n".join(lines))
