"""Tests for style_agent.py formatter.

Tests the format_style_analysis_context() function that formats
episode texts and existing StyleGuide into a prompt for the Style Agent.
"""

from __future__ import annotations

import pytest

from src.agents.prompts.style_agent import format_style_analysis_context
from src.core.models.style import POVType, StyleGuide, TenseType


class TestFormatStyleAnalysisContext:
    """Tests for format_style_analysis_context()."""

    def test_single_episode_text_appears_in_output(self) -> None:
        """Single episode text should appear in the output."""
        episodes = ["これは最初のエピソードです。"]
        result = format_style_analysis_context(episodes)

        assert "## 分析対象テキスト" in result
        assert "これは最初のエピソードです。" in result

    def test_multiple_episodes_numbered(self) -> None:
        """Multiple episodes should be numbered."""
        episodes = [
            "第一のエピソード",
            "第二のエピソード",
            "第三のエピソード",
        ]
        result = format_style_analysis_context(episodes)

        assert "### エピソード 1" in result
        assert "第一のエピソード" in result
        assert "### エピソード 2" in result
        assert "第二のエピソード" in result
        assert "### エピソード 3" in result
        assert "第三のエピソード" in result

    def test_no_existing_guide_section_when_none(self) -> None:
        """Should not include existing guide section when existing_guide is None."""
        episodes = ["テキスト"]
        result = format_style_analysis_context(episodes, existing_guide=None)

        assert "## 既存スタイルガイド" not in result

    def test_existing_guide_pov_and_tense_appear(self) -> None:
        """Existing StyleGuide POV and tense should appear in output."""
        episodes = ["テキスト"]
        guide = StyleGuide(
            work="Sample Work",
            pov=POVType.THIRD_PERSON_LIMITED,
            tense=TenseType.PAST,
        )
        result = format_style_analysis_context(episodes, existing_guide=guide)

        assert "## 既存スタイルガイド" in result
        assert "third_person_limited" in result
        assert "past" in result

    def test_existing_guide_style_characteristics(self) -> None:
        """Existing StyleGuide characteristics should appear."""
        episodes = ["テキスト"]
        guide = StyleGuide(
            work="Sample Work",
            pov=POVType.FIRST_PERSON,
            tense=TenseType.PRESENT,
            style_characteristics=["簡潔な文体", "内省的な語り"],
        )
        result = format_style_analysis_context(episodes, existing_guide=guide)

        assert "簡潔な文体" in result
        assert "内省的な語り" in result

    def test_existing_guide_avoid_expressions(self) -> None:
        """Existing StyleGuide avoid_expressions should appear."""
        episodes = ["テキスト"]
        guide = StyleGuide(
            work="Sample Work",
            pov=POVType.FIRST_PERSON,
            tense=TenseType.PRESENT,
            avoid_expressions=["〜のような", "とても"],
        )
        result = format_style_analysis_context(episodes, existing_guide=guide)

        assert "〜のような" in result
        assert "とても" in result

    def test_empty_episodes_raises_error(self) -> None:
        """Empty episode list should raise ValueError."""
        with pytest.raises(ValueError, match="episode_texts cannot be empty"):
            format_style_analysis_context([])

    def test_sections_separated_by_separator(self) -> None:
        """Sections should be separated by --- separator."""
        episodes = ["エピソード1"]
        guide = StyleGuide(
            work="Sample",
            pov=POVType.FIRST_PERSON,
            tense=TenseType.PAST,
        )
        result = format_style_analysis_context(episodes, existing_guide=guide)

        # Should have separator between analysis text section and existing guide section
        assert "\n\n---\n\n" in result
