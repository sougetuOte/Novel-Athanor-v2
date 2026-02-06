"""Tests for Reviewer prompt formatter."""

from src.agents.prompts.reviewer import (
    format_review_context,
)
from src.core.context import (
    ContextBuildResult,
    FilteredContext,
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
    VisibilityAwareContext,
)
from src.core.context.hint_collector import HintCollection
from src.core.models.ai_visibility import AIVisibilityLevel


def _make_result(
    *,
    ctx: FilteredContext | None = None,
    forbidden_keywords: list[str] | None = None,
    visibility_context: VisibilityAwareContext | None = None,
    foreshadow_instructions: ForeshadowInstructions | None = None,
) -> ContextBuildResult:
    """Helper to build ContextBuildResult with defaults."""
    return ContextBuildResult(
        context=ctx or FilteredContext(),
        visibility_context=visibility_context,
        foreshadow_instructions=foreshadow_instructions or ForeshadowInstructions(),
        forbidden_keywords=forbidden_keywords or [],
        hints=HintCollection(),
    )


class TestFormatReviewContext:
    """Tests for format_review_context formatter."""

    def test_includes_draft_text(self) -> None:
        """Draft text is included in the output."""
        result = _make_result(ctx=FilteredContext(plot_l1="Plot"))
        output = format_review_context(
            result=result,
            draft_text="これはドラフトテキストです。",
        )
        assert "## レビュー対象テキスト" in output
        assert "これはドラフトテキストです。" in output

    def test_includes_forbidden_keywords(self) -> None:
        """Forbidden keywords section is present when keywords exist."""
        result = _make_result(forbidden_keywords=["王族", "血筋", "高貴"])
        output = format_review_context(
            result=result,
            draft_text="ドラフト",
        )
        assert "## 禁止キーワード" in output
        assert "- 王族" in output
        assert "- 血筋" in output
        assert "- 高貴" in output

    def test_no_forbidden_keywords_section_when_empty(self) -> None:
        """Forbidden keywords section is omitted when list is empty."""
        result = _make_result(forbidden_keywords=[])
        output = format_review_context(
            result=result,
            draft_text="ドラフト",
        )
        assert "## 禁止キーワード" not in output

    def test_includes_foreshadowing_constraints(self) -> None:
        """Foreshadowing forbidden_expressions are included as review constraints."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.PLANT,
                note="伏線を埋め込む",
                forbidden_expressions=["真実", "正体"],
            )
        )
        result = _make_result(foreshadow_instructions=instructions)
        output = format_review_context(
            result=result,
            draft_text="ドラフト",
        )
        assert "## 伏線制約" in output
        assert "FS-001" in output
        assert "真実" in output
        assert "正体" in output

    def test_no_foreshadowing_section_when_no_constraints(self) -> None:
        """Foreshadowing section is omitted when no forbidden_expressions exist."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.PLANT,
                note="伏線を埋め込む",
            )
        )
        result = _make_result(foreshadow_instructions=instructions)
        output = format_review_context(
            result=result,
            draft_text="ドラフト",
        )
        # No forbidden_expressions → no section
        assert "## 伏線制約" not in output

    def test_includes_secret_context_from_visibility(self) -> None:
        """Secret content from visibility context is included for review."""
        base_ctx = FilteredContext(
            characters={"アイラ": "フィルタ済みキャラ情報"},
        )
        vis_ctx = VisibilityAwareContext(
            base_context=base_ctx,
            current_visibility_level=AIVisibilityLevel.USE,
            excluded_sections=["character.闇の王"],
            forbidden_keywords=["王族", "血筋"],
        )
        result = _make_result(
            ctx=FilteredContext(characters={"アイラ": "完全キャラ情報"}),
            visibility_context=vis_ctx,
        )
        output = format_review_context(
            result=result,
            draft_text="ドラフト",
        )
        assert "## 可視性制約" in output
        assert "character.闇の王" in output

    def test_no_visibility_section_when_no_constraints(self) -> None:
        """Visibility section is omitted when no excluded sections/keywords."""
        vis_ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            current_visibility_level=AIVisibilityLevel.USE,
        )
        result = _make_result(visibility_context=vis_ctx)
        output = format_review_context(
            result=result,
            draft_text="ドラフト",
        )
        assert "## 可視性制約" not in output

    def test_section_separator(self) -> None:
        """Sections are separated by '\\n\\n---\\n\\n'."""
        result = _make_result(forbidden_keywords=["秘密"])
        output = format_review_context(
            result=result,
            draft_text="ドラフト",
        )
        assert "\n\n---\n\n" in output

    def test_draft_text_section_comes_first(self) -> None:
        """Draft text section appears before other sections."""
        result = _make_result(forbidden_keywords=["秘密"])
        output = format_review_context(
            result=result,
            draft_text="ドラフト",
        )
        draft_pos = output.index("## レビュー対象テキスト")
        keyword_pos = output.index("## 禁止キーワード")
        assert draft_pos < keyword_pos

    def test_full_context_all_sections(self) -> None:
        """Test with all sections populated."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.REINFORCE,
                note="強化",
                forbidden_expressions=["真の姿"],
            )
        )

        vis_ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            current_visibility_level=AIVisibilityLevel.USE,
            excluded_sections=["character.黒幕"],
            forbidden_keywords=["正体"],
        )

        result = _make_result(
            forbidden_keywords=["王族", "血筋"],
            foreshadow_instructions=instructions,
            visibility_context=vis_ctx,
        )
        output = format_review_context(
            result=result,
            draft_text="テストドラフト",
        )

        # All 4 sections present
        assert "## レビュー対象テキスト" in output
        assert "## 禁止キーワード" in output
        assert "## 伏線制約" in output
        assert "## 可視性制約" in output
        # Separators between 4 sections = 3 separators
        assert output.count("\n\n---\n\n") == 3
