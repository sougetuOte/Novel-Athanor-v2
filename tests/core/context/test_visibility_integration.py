"""Integration tests for visibility system.

Tests the complete flow:
FilteredContext -> VisibilityFilteringService -> HintCollector
"""

import time

import pytest

from src.core.context.filtered_context import FilteredContext
from src.core.context.foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from src.core.context.hint_collector import HintCollector
from src.core.context.visibility_context import VisibilityAwareContext
from src.core.context.visibility_filtering import VisibilityFilteringService
from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.services.visibility_controller import VisibilityController


# --- Test Fixtures ---


@pytest.fixture
def visibility_controller() -> VisibilityController:
    """Create a visibility controller with forbidden keywords."""
    return VisibilityController(
        default_level=AIVisibilityLevel.USE,
        forbidden_keywords=["絶対秘密", "禁句"],
    )


@pytest.fixture
def sample_context() -> FilteredContext:
    """Create sample context with visibility comments.

    Uses ai_visibility: 0 (HIDDEN), 1 (AWARE), 2 (KNOW), 3 (USE)
    """
    return FilteredContext(
        scene_id="ep010",
        current_phase="arc_1",
        plot_l1="復讐と赦しの物語",
        plot_l2="主人公の決意",
        plot_l3="対決前夜",
        summary_l1="これまでの物語",
        characters={
            # HIDDEN section - should be completely excluded
            "黒幕": """# 黒幕
## 基本情報
物語の敵役。

## 正体
<!-- ai_visibility: 0 -->
実は主人公の兄である。
""",
            # AWARE section - should generate hint, content excluded
            "アイラ": """# アイラ
## 基本情報
謎の少女。

## 秘密
<!-- ai_visibility: 1 -->
実は王族の血を引いている。
""",
            # All visible (USE level default)
            "主人公": """# 主人公
## 基本情報
復讐を誓う戦士。

## 詳細
師匠の仇を追っている。
""",
        },
        world_settings={
            # HIDDEN setting
            "禁忌の力": """# 禁忌の力
## 基本情報
使ってはならない力。

## 真実
<!-- ai_visibility: 0 -->
世界を滅ぼす可能性がある。
""",
            # AWARE setting
            "古代王国": """# 古代王国
## 基本情報
かつて栄えた王国。

## 秘密
<!-- ai_visibility: 1 -->
滅亡の真因は内部の裏切り。
""",
            # All visible
            "魔法体系": """# 魔法体系
## 基本情報
この世界の魔法。

## 詳細
元素を操る力。
""",
        },
    )


@pytest.fixture
def sample_instructions() -> ForeshadowInstructions:
    """Create sample foreshadowing instructions."""
    instructions = ForeshadowInstructions()
    instructions.add_instruction(
        ForeshadowInstruction(
            foreshadowing_id="FS-010-royal",
            action=InstructionAction.PLANT,
            forbidden_expressions=["王族", "血筋"],
            note="王族の血筋を匂わせる",
            subtlety_target=4,
        )
    )
    instructions.add_instruction(
        ForeshadowInstruction(
            foreshadowing_id="FS-005-magic",
            action=InstructionAction.HINT,
            note="禁忌の魔法の存在を示唆",
            subtlety_target=8,
        )
    )
    return instructions


# --- Integration Tests ---


class TestVisibilityIntegrationCompleteFlow:
    """Tests for complete visibility filtering flow."""

    def test_complete_flow_filtering_and_hints(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
    ):
        """Complete flow: context -> filter -> hints."""
        # Setup
        filtering_service = VisibilityFilteringService(visibility_controller)
        hint_collector = HintCollector()

        # 1. Filter context
        visibility_context = filtering_service.filter_context(sample_context)

        # Verify: HIDDEN sections are excluded
        assert "実は主人公の兄" not in visibility_context.filtered_characters.get(
            "黒幕", ""
        )
        assert "世界を滅ぼす可能性" not in visibility_context.filtered_world_settings.get(
            "禁忌の力", ""
        )

        # Verify: AWARE sections generate hints
        assert len(visibility_context.hints) >= 2  # アイラ and 古代王国

        # Verify: USE sections are fully included
        hero_info = visibility_context.filtered_characters.get("主人公", "")
        assert "復讐を誓う戦士" in hero_info
        assert "師匠の仇" in hero_info

        # 2. Collect hints
        hints = hint_collector.collect_all(visibility_context=visibility_context)

        # Verify hints exist
        assert len(hints.hints) >= 2

    def test_flow_with_foreshadowing(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
        sample_instructions: ForeshadowInstructions,
    ):
        """Complete flow with foreshadowing instructions."""
        filtering_service = VisibilityFilteringService(visibility_controller)
        hint_collector = HintCollector()

        # Filter context
        visibility_context = filtering_service.filter_context(sample_context)

        # Collect hints from both visibility and foreshadowing
        hints = hint_collector.collect_all(
            visibility_context=visibility_context,
            foreshadow_instructions=sample_instructions,
        )

        # Verify: hints from both sources
        visibility_hints = [h for h in hints.hints if h.source.value == "visibility"]
        foreshadow_hints = [h for h in hints.hints if h.source.value == "foreshadowing"]

        assert len(visibility_hints) >= 2  # From AWARE sections
        assert len(foreshadow_hints) == 1  # Only HINT action (FS-005-magic)


class TestVisibilityIntegrationHiddenBehavior:
    """Tests for HIDDEN visibility behavior."""

    def test_hidden_sections_excluded(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
    ):
        """HIDDEN sections are completely excluded from output."""
        service = VisibilityFilteringService(visibility_controller)
        result = service.filter_context(sample_context)

        # Character: 黒幕's 正体 section (HIDDEN)
        kuromaku_info = result.filtered_characters.get("黒幕", "")
        assert "主人公の兄" not in kuromaku_info

        # World: 禁忌の力's 真実 section (HIDDEN)
        kinki_info = result.filtered_world_settings.get("禁忌の力", "")
        assert "世界を滅ぼす" not in kinki_info

    def test_hidden_does_not_generate_hints(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
    ):
        """HIDDEN sections do not generate hints (only AWARE does)."""
        service = VisibilityFilteringService(visibility_controller)
        result = service.filter_context(sample_context)

        # Hints should not mention HIDDEN content
        for hint in result.hints:
            assert "主人公の兄" not in hint.hint_text
            assert "世界を滅ぼす" not in hint.hint_text


class TestVisibilityIntegrationAwareBehavior:
    """Tests for AWARE visibility behavior."""

    def test_aware_sections_generate_hints(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
    ):
        """AWARE sections generate hints."""
        service = VisibilityFilteringService(visibility_controller)
        result = service.filter_context(sample_context)

        # Should have hints for AWARE sections
        assert len(result.hints) >= 2

        # Hints should mention the existence of hidden info
        hint_texts = " ".join(h.hint_text for h in result.hints)
        assert "非公開" in hint_texts or "秘密" in hint_texts

    def test_aware_sections_content_excluded(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
    ):
        """AWARE sections have their content excluded."""
        service = VisibilityFilteringService(visibility_controller)
        result = service.filter_context(sample_context)

        # アイラ's 秘密 section (AWARE) - content should be excluded
        aira_info = result.filtered_characters.get("アイラ", "")
        assert "王族の血" not in aira_info

        # 古代王国's 秘密 section (AWARE) - content should be excluded
        kingdom_info = result.filtered_world_settings.get("古代王国", "")
        assert "内部の裏切り" not in kingdom_info


class TestVisibilityIntegrationUseBehavior:
    """Tests for USE visibility behavior."""

    def test_use_sections_fully_included(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
    ):
        """USE (default) sections are fully included."""
        service = VisibilityFilteringService(visibility_controller)
        result = service.filter_context(sample_context)

        # 主人公 has no visibility restrictions
        hero_info = result.filtered_characters.get("主人公", "")
        assert "復讐を誓う戦士" in hero_info
        assert "師匠の仇" in hero_info

        # 魔法体系 has no visibility restrictions
        magic_info = result.filtered_world_settings.get("魔法体系", "")
        assert "元素を操る力" in magic_info


class TestVisibilityIntegrationForbiddenKeywords:
    """Tests for forbidden keywords handling."""

    def test_forbidden_keywords_collected(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
    ):
        """Forbidden keywords from controller are collected."""
        service = VisibilityFilteringService(visibility_controller)
        result = service.filter_context(sample_context)

        # Controller was initialized with forbidden keywords
        assert "絶対秘密" in result.forbidden_keywords
        assert "禁句" in result.forbidden_keywords


class TestVisibilityIntegrationPromptFormat:
    """Tests for prompt formatting."""

    def test_format_for_prompt(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
        sample_instructions: ForeshadowInstructions,
    ):
        """Hints can be formatted for prompt."""
        service = VisibilityFilteringService(visibility_controller)
        hint_collector = HintCollector()

        visibility_context = service.filter_context(sample_context)
        hints = hint_collector.collect_all(
            visibility_context=visibility_context,
            foreshadow_instructions=sample_instructions,
        )

        prompt_text = hint_collector.format_for_prompt(hints)

        # Should have formatted output
        assert "執筆時のヒント" in prompt_text
        assert "匂わせてください" in prompt_text


class TestVisibilityIntegrationPerformance:
    """Performance tests."""

    def test_performance_within_limit(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
        sample_instructions: ForeshadowInstructions,
    ):
        """Complete flow finishes within 100ms."""
        service = VisibilityFilteringService(visibility_controller)
        hint_collector = HintCollector()

        start = time.time()

        visibility_context = service.filter_context(sample_context)
        hints = hint_collector.collect_all(
            visibility_context=visibility_context,
            foreshadow_instructions=sample_instructions,
        )
        _ = hint_collector.format_for_prompt(hints)

        elapsed = time.time() - start

        assert elapsed < 0.1  # 100ms


class TestVisibilityIntegrationGhostWriterOutput:
    """Tests for Ghost Writer context output."""

    def test_to_ghost_writer_context(
        self,
        visibility_controller: VisibilityController,
        sample_context: FilteredContext,
    ):
        """VisibilityAwareContext can generate Ghost Writer context."""
        service = VisibilityFilteringService(visibility_controller)
        result = service.filter_context(sample_context)

        gw_context = result.to_ghost_writer_context()

        # Should have basic context fields
        assert "plot_theme" in gw_context
        assert gw_context["plot_theme"] == "復讐と赦しの物語"

        # Should have excluded count metadata
        assert "_excluded_count" in gw_context

        # Should have visibility level metadata
        assert "_visibility_level" in gw_context
