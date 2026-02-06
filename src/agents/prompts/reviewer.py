"""Reviewer prompt formatter.

This module provides functions for formatting ContextBuildResult into
prompt text for the Reviewer agent. The Reviewer needs:
1. The draft text to review
2. Forbidden keywords to check against
3. Foreshadowing constraints (forbidden_expressions per instruction)
4. Visibility constraints (excluded sections, visibility-level forbidden keywords)
"""

from src.core.context import ContextBuildResult


def format_review_context(
    result: ContextBuildResult,
    draft_text: str,
) -> str:
    """Format ContextBuildResult + draft into Reviewer prompt text.

    Args:
        result: Context build result from L3.
        draft_text: The draft text to be reviewed.

    Returns:
        Formatted prompt text for Reviewer agent.
    """
    sections: list[str] = []

    _add_draft_section(sections, draft_text)
    _add_forbidden_keywords_section(sections, result)
    _add_foreshadowing_constraints_section(sections, result)
    _add_visibility_constraints_section(sections, result)

    return "\n\n---\n\n".join(sections)


def _add_draft_section(sections: list[str], draft_text: str) -> None:
    """Add the draft text section."""
    sections.append(f"## レビュー対象テキスト\n\n{draft_text}")


def _add_forbidden_keywords_section(
    sections: list[str], result: ContextBuildResult
) -> None:
    """Add forbidden keywords section if keywords exist."""
    if not result.forbidden_keywords:
        return

    lines = [f"- {kw}" for kw in result.forbidden_keywords]
    sections.append(
        "## 禁止キーワード（テキスト内に含まれていないか確認すること）\n"
        + "\n".join(lines)
    )


def _add_foreshadowing_constraints_section(
    sections: list[str], result: ContextBuildResult
) -> None:
    """Add foreshadowing constraints section if forbidden_expressions exist."""
    constraints: list[str] = []

    for instr in result.foreshadow_instructions.instructions:
        if not instr.forbidden_expressions:
            continue
        expr_list = ", ".join(instr.forbidden_expressions)
        constraints.append(f"- {instr.foreshadowing_id}: 禁止表現 [{expr_list}]")

    if not constraints:
        return

    sections.append("## 伏線制約\n" + "\n".join(constraints))


def _add_visibility_constraints_section(
    sections: list[str], result: ContextBuildResult
) -> None:
    """Add visibility constraints section if excluded sections or keywords exist."""
    if result.visibility_context is None:
        return

    vis = result.visibility_context
    has_excluded = bool(vis.excluded_sections)
    has_vis_keywords = bool(vis.forbidden_keywords)

    if not has_excluded and not has_vis_keywords:
        return

    lines: list[str] = []

    if has_excluded:
        lines.append("### 除外セクション（これらの内容に言及してはならない）")
        for section in vis.excluded_sections:
            lines.append(f"- {section}")

    if has_vis_keywords:
        if lines:
            lines.append("")
        lines.append("### 可視性禁止キーワード")
        for kw in vis.forbidden_keywords:
            lines.append(f"- {kw}")

    sections.append("## 可視性制約\n" + "\n".join(lines))
