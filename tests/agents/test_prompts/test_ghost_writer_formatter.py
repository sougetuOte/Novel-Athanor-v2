"""Tests for Ghost Writer prompt formatter."""

from src.agents.models.scene_requirements import SceneRequirements
from src.agents.prompts.ghost_writer import (
    format_scene_requirements,
    format_writing_context,
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


class TestFormatSceneRequirements:
    """Tests for format_scene_requirements helper."""

    def test_minimal_requirements(self) -> None:
        """Test minimal scene requirements formatting."""
        requirements = SceneRequirements(episode_id="ep010")
        result = format_scene_requirements(requirements)

        assert "## シーン要件" in result
        assert "episode_id: ep010" in result
        assert "word_count: 3000" in result
        assert "pov: 三人称限定視点" in result

    def test_full_requirements(self) -> None:
        """Test full scene requirements formatting."""
        requirements = SceneRequirements(
            episode_id="ep010",
            sequence_id="seq01",
            chapter_id="ch01",
            current_phase="起",
            word_count=5000,
            pov="一人称",
            mood="緊張感",
            special_instructions="伏線を強調すること",
        )
        result = format_scene_requirements(requirements)

        assert "episode_id: ep010" in result
        assert "sequence_id: seq01" in result
        assert "chapter_id: ch01" in result
        assert "current_phase: 起" in result
        assert "word_count: 5000" in result
        assert "pov: 一人称" in result
        assert "mood: 緊張感" in result
        assert "special_instructions: 伏線を強調すること" in result

    def test_optional_fields_none(self) -> None:
        """Test optional fields when None."""
        requirements = SceneRequirements(
            episode_id="ep010", sequence_id=None, mood=None
        )
        result = format_scene_requirements(requirements)

        assert "episode_id: ep010" in result
        assert "sequence_id" not in result or "sequence_id: None" not in result
        assert "mood" not in result or "mood: None" not in result


class TestFormatWritingContext:
    """Tests for format_writing_context formatter."""

    def test_full_context(self) -> None:
        """Test formatting with all fields populated."""
        ctx = FilteredContext(
            plot_l1="Theme: Redemption",
            plot_l2="Chapter: First encounter",
            plot_l3="Scene: Meeting at tavern",
            summary_l1="Overall: A journey begins",
            summary_l2="Chapter summary: Introduction",
            summary_l3="Previous scene: Arrival at town",
            characters={"Alice": "Protagonist, age 25", "Bob": "Guide, age 40"},
            world_settings={
                "Magic System": "Rule-based magic",
                "Geography": "Northern continent",
            },
            style_guide="Use simple sentences.",
            scene_id="ep010/seq01",
            current_phase="起",
        )

        instructions = ForeshadowInstructions()
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.PLANT,
                note="First mention of the artifact",
            )
        )

        result_obj = ContextBuildResult(
            context=ctx,
            visibility_context=None,
            foreshadow_instructions=instructions,
            forbidden_keywords=["royal blood", "princess"],
            hints=HintCollection(),
        )

        requirements = SceneRequirements(episode_id="ep010", word_count=3000)
        result = format_writing_context(result_obj, requirements)

        # Check plot sections
        assert "## プロット情報" in result
        assert "### L1 (全体)" in result
        assert "Theme: Redemption" in result
        assert "### L2 (章)" in result
        assert "Chapter: First encounter" in result
        assert "### L3 (シーン)" in result
        assert "Scene: Meeting at tavern" in result

        # Check summary sections
        assert "## サマリ情報" in result
        assert "### 全体サマリ" in result
        assert "A journey begins" in result
        assert "### 章サマリ" in result
        assert "Introduction" in result
        assert "### 直近シーン" in result
        assert "Arrival at town" in result

        # Check characters
        assert "## キャラクター" in result
        assert "### Alice" in result
        assert "Protagonist, age 25" in result
        assert "### Bob" in result
        assert "Guide, age 40" in result

        # Check world settings
        assert "## 世界観設定" in result
        assert "### Magic System" in result
        assert "Rule-based magic" in result
        assert "### Geography" in result
        assert "Northern continent" in result

        # Check style guide
        assert "## スタイルガイド" in result
        assert "Use simple sentences." in result

        # Check foreshadowing instructions
        assert "## 伏線指示" in result
        assert "FS-001" in result
        assert "plant" in result.lower()
        assert "First mention of the artifact" in result

        # Check forbidden keywords
        assert "## 禁止キーワード" in result
        assert "絶対に使用しないこと" in result
        assert "royal blood" in result
        assert "princess" in result

        # Check scene requirements
        assert "## シーン要件" in result
        assert "episode_id: ep010" in result
        assert "word_count: 3000" in result

        # Check section separators
        assert "\n\n---\n\n" in result

    def test_minimal_context(self) -> None:
        """Test formatting with minimal fields."""
        ctx = FilteredContext(plot_l1="Theme: Minimal test")

        result_obj = ContextBuildResult(
            context=ctx,
            visibility_context=None,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=[],
            hints=HintCollection(),
        )

        requirements = SceneRequirements(episode_id="ep010")
        result = format_writing_context(result_obj, requirements)

        # Check that plot section exists
        assert "## プロット情報" in result
        assert "Theme: Minimal test" in result

        # Check that empty sections are not included
        assert "## キャラクター" not in result
        assert "## 世界観設定" not in result
        assert "## スタイルガイド" not in result
        assert "## 伏線指示" not in result
        assert "## 禁止キーワード" not in result

        # Check that scene requirements exist
        assert "## シーン要件" in result

    def test_visibility_context_priority(self) -> None:
        """Test that visibility_context.base_context is used when present."""
        base_ctx = FilteredContext(plot_l1="Base plot")
        visibility_ctx_filtered = FilteredContext(plot_l1="Visibility filtered plot")

        visibility_context = VisibilityAwareContext(
            base_context=visibility_ctx_filtered,
            current_visibility_level=AIVisibilityLevel.USE,
        )

        result_obj = ContextBuildResult(
            context=base_ctx,
            visibility_context=visibility_context,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=[],
            hints=HintCollection(),
        )

        requirements = SceneRequirements(episode_id="ep010")
        result = format_writing_context(result_obj, requirements)

        # Should use visibility_context.base_context, not result.context
        assert "Visibility filtered plot" in result
        assert "Base plot" not in result

    def test_active_instructions_only(self) -> None:
        """Test that only active instructions (action != NONE) are included."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.PLANT,
                note="Should appear",
            )
        )
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-002",
                action=InstructionAction.NONE,
                note="Should not appear",
            )
        )
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-003",
                action=InstructionAction.REINFORCE,
                note="Should also appear",
            )
        )

        ctx = FilteredContext(plot_l1="Test")
        result_obj = ContextBuildResult(
            context=ctx,
            visibility_context=None,
            foreshadow_instructions=instructions,
            forbidden_keywords=[],
            hints=HintCollection(),
        )

        requirements = SceneRequirements(episode_id="ep010")
        result = format_writing_context(result_obj, requirements)

        assert "FS-001" in result
        assert "Should appear" in result
        assert "FS-003" in result
        assert "Should also appear" in result
        assert "FS-002" not in result
        assert "Should not appear" not in result

    def test_forbidden_keywords_list(self) -> None:
        """Test forbidden keywords formatting."""
        ctx = FilteredContext(plot_l1="Test")
        result_obj = ContextBuildResult(
            context=ctx,
            visibility_context=None,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=["秘密", "隠された", "真実"],
            hints=HintCollection(),
        )

        requirements = SceneRequirements(episode_id="ep010")
        result = format_writing_context(result_obj, requirements)

        assert "## 禁止キーワード" in result
        assert "絶対に使用しないこと" in result
        assert "- 秘密" in result
        assert "- 隠された" in result
        assert "- 真実" in result

    def test_empty_foreshadowing_not_included(self) -> None:
        """Test that empty foreshadowing section is not included."""
        ctx = FilteredContext(plot_l1="Test")
        result_obj = ContextBuildResult(
            context=ctx,
            visibility_context=None,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=[],
            hints=HintCollection(),
        )

        requirements = SceneRequirements(episode_id="ep010")
        result = format_writing_context(result_obj, requirements)

        assert "## 伏線指示" not in result

    def test_section_separator(self) -> None:
        """Test that sections are separated by '\\n\\n---\\n\\n'."""
        ctx = FilteredContext(
            plot_l1="Test plot",
            characters={"Alice": "Test character"},
            style_guide="Test style",
        )

        result_obj = ContextBuildResult(
            context=ctx,
            visibility_context=None,
            foreshadow_instructions=ForeshadowInstructions(),
            forbidden_keywords=["test"],
            hints=HintCollection(),
        )

        requirements = SceneRequirements(episode_id="ep010")
        result = format_writing_context(result_obj, requirements)

        # Count separators
        separator_count = result.count("\n\n---\n\n")
        # Should have separators between: plot, character, style, forbidden, requirements
        # That's 4 separators
        assert separator_count == 4

    def test_instruction_action_value(self) -> None:
        """Test that InstructionAction.value is used correctly."""
        instructions = ForeshadowInstructions()
        instructions.add_instruction(
            ForeshadowInstruction(
                foreshadowing_id="FS-001",
                action=InstructionAction.HINT,
                note="Test hint",
            )
        )

        ctx = FilteredContext(plot_l1="Test")
        result_obj = ContextBuildResult(
            context=ctx,
            visibility_context=None,
            foreshadow_instructions=instructions,
            forbidden_keywords=[],
            hints=HintCollection(),
        )

        requirements = SceneRequirements(episode_id="ep010")
        result = format_writing_context(result_obj, requirements)

        # Should use action.value (lowercase)
        assert "hint" in result.lower()
        assert "FS-001" in result
