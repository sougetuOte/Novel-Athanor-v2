"""Tests for quality prompt formatter."""

from src.agents.models.scene_requirements import SceneRequirements
from src.agents.prompts.quality import format_quality_context
from src.core.context import (
    ContextBuildResult,
    FilteredContext,
    ForeshadowInstructions,
)


def _make_filtered_context(**kwargs) -> FilteredContext:
    """Create a FilteredContext with defaults."""
    defaults = {
        "plot_l1": "",
        "plot_l2": "",
        "plot_l3": "",
        "summary_l1": "",
        "summary_l2": "",
        "summary_l3": "",
        "characters": {},
        "world_settings": {},
        "style_guide": "",
    }
    defaults.update(kwargs)
    return FilteredContext(**defaults)


def _make_result(ctx: FilteredContext | None = None) -> ContextBuildResult:
    """Create a ContextBuildResult with defaults."""
    if ctx is None:
        ctx = _make_filtered_context()
    return ContextBuildResult(
        context=ctx,
        visibility_context=None,
        foreshadow_instructions=ForeshadowInstructions(instructions=[]),
        forbidden_keywords=[],
        hints=[],
    )


def _make_requirements(**kwargs) -> SceneRequirements:
    """Create SceneRequirements with defaults."""
    defaults = {"episode_id": "ep001", "word_count": 3000, "pov": "三人称限定視点"}
    defaults.update(kwargs)
    return SceneRequirements(**defaults)


class TestFormatQualityContext:
    """Tests for format_quality_context()."""

    def test_includes_draft_text(self) -> None:
        """Draft text must appear in the output."""
        result = _make_result()
        reqs = _make_requirements()
        draft = "これはテスト用ドラフトです。"

        output = format_quality_context(result, draft, reqs)

        assert "これはテスト用ドラフトです。" in output

    def test_includes_draft_section_header(self) -> None:
        """Draft section must have a proper header."""
        result = _make_result()
        reqs = _make_requirements()

        output = format_quality_context(result, "テスト", reqs)

        assert "## 評価対象テキスト" in output

    def test_includes_scene_requirements(self) -> None:
        """Scene requirements must be included."""
        result = _make_result()
        reqs = _make_requirements(episode_id="ep010", word_count=5000)

        output = format_quality_context(result, "テスト", reqs)

        assert "ep010" in output
        assert "5000" in output

    def test_includes_character_info(self) -> None:
        """Character info should be included for character consistency evaluation."""
        ctx = _make_filtered_context(
            characters={"太郎": "勇敢な少年", "花子": "知的な少女"}
        )
        result = _make_result(ctx)
        reqs = _make_requirements()

        output = format_quality_context(result, "テスト", reqs)

        assert "太郎" in output
        assert "花子" in output

    def test_includes_style_guide(self) -> None:
        """Style guide should be included for style evaluation."""
        ctx = _make_filtered_context(style_guide="文語調、敬体")
        result = _make_result(ctx)
        reqs = _make_requirements()

        output = format_quality_context(result, "テスト", reqs)

        assert "文語調、敬体" in output

    def test_includes_plot_info(self) -> None:
        """Plot info should be included for coherence evaluation."""
        ctx = _make_filtered_context(plot_l3="主人公が敵と対峙する")
        result = _make_result(ctx)
        reqs = _make_requirements()

        output = format_quality_context(result, "テスト", reqs)

        assert "主人公が敵と対峙する" in output

    def test_excludes_empty_sections(self) -> None:
        """Empty sections should not appear in the output."""
        result = _make_result()
        reqs = _make_requirements()

        output = format_quality_context(result, "テスト", reqs)

        assert "## キャラクター" not in output
        assert "## 世界観設定" not in output
        assert "## スタイルガイド" not in output
        assert "## プロット情報" not in output

    def test_sections_separated_by_divider(self) -> None:
        """Sections should be separated by ---."""
        ctx = _make_filtered_context(style_guide="常体")
        result = _make_result(ctx)
        reqs = _make_requirements()

        output = format_quality_context(result, "テスト", reqs)

        assert "\n\n---\n\n" in output

    def test_includes_summary_info(self) -> None:
        """Summary info should be included for continuity evaluation."""
        ctx = _make_filtered_context(summary_l3="前のシーンで主人公が旅立った")
        result = _make_result(ctx)
        reqs = _make_requirements()

        output = format_quality_context(result, "テスト", reqs)

        assert "前のシーンで主人公が旅立った" in output

    def test_full_context_includes_all_sections(self) -> None:
        """A fully-populated context should include all relevant sections."""
        ctx = _make_filtered_context(
            plot_l3="決戦シーン",
            summary_l3="前回の続き",
            characters={"太郎": "主人公"},
            world_settings={"魔法": "火と水の二属性"},
            style_guide="常体、簡潔",
        )
        result = _make_result(ctx)
        reqs = _make_requirements()

        output = format_quality_context(result, "ドラフト本文", reqs)

        assert "## 評価対象テキスト" in output
        assert "## シーン要件" in output
        assert "## プロット情報" in output
        assert "## サマリ情報" in output
        assert "## キャラクター" in output
        assert "## 世界観設定" in output
        assert "## スタイルガイド" in output
