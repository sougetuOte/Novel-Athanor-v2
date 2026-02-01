"""Tests for VisibilityAwareContext data classes."""

import pytest

from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.context.filtered_context import FilteredContext
from src.core.context.visibility_context import (
    VisibilityHint,
    VisibilityAwareContext,
)


class TestVisibilityHint:
    """Test VisibilityHint data class."""

    def test_create_basic(self):
        """基本的なヒント生成."""
        hint = VisibilityHint(
            category="character",
            entity_id="alice.secret",
            hint_text="There seems to be something hidden about Alice.",
            level=AIVisibilityLevel.AWARE,
        )
        assert hint.category == "character"
        assert hint.entity_id == "alice.secret"
        assert hint.source_section == "character.alice.secret"  # backward compat
        assert hint.hint_text == "There seems to be something hidden about Alice."
        assert hint.level == AIVisibilityLevel.AWARE

    def test_create_with_know_level(self):
        """KNOW レベルのヒント."""
        hint = VisibilityHint(
            category="world",
            entity_id="kingdom.history",
            hint_text="The kingdom has a complicated history involving royal succession.",
            level=AIVisibilityLevel.KNOW,
        )
        assert hint.level == AIVisibilityLevel.KNOW

    def test_create_with_different_levels(self):
        """各可視性レベルでヒント生成可能."""
        for level in [AIVisibilityLevel.HIDDEN, AIVisibilityLevel.AWARE,
                      AIVisibilityLevel.KNOW, AIVisibilityLevel.USE]:
            hint = VisibilityHint(
                category="test",
                entity_id="item",
                hint_text="test hint",
                level=level,
            )
            assert hint.level == level


class TestVisibilityAwareContextCreation:
    """Test VisibilityAwareContext instance creation."""

    def test_create_minimal(self):
        """最小限のパラメータで生成."""
        base = FilteredContext()
        ctx = VisibilityAwareContext(base_context=base)
        assert ctx.base_context is base
        assert ctx.hints == []
        assert ctx.excluded_sections == []
        assert ctx.current_visibility_level == AIVisibilityLevel.USE
        assert ctx.forbidden_keywords == []

    def test_create_with_all_fields(self):
        """全フィールドを指定して生成."""
        base = FilteredContext(
            plot_l1="Theme: Redemption",
            scene_id="ep001/seq_01",
        )
        hint = VisibilityHint(
            category="character",
            entity_id="bob",
            hint_text="Bob seems nervous.",
            level=AIVisibilityLevel.AWARE,
        )
        ctx = VisibilityAwareContext(
            base_context=base,
            hints=[hint],
            excluded_sections=["character.secret_villain", "world.magic_system"],
            current_visibility_level=AIVisibilityLevel.KNOW,
            forbidden_keywords=["royal", "princess"],
        )
        assert ctx.base_context.plot_l1 == "Theme: Redemption"
        assert len(ctx.hints) == 1
        assert len(ctx.excluded_sections) == 2
        assert ctx.current_visibility_level == AIVisibilityLevel.KNOW
        assert len(ctx.forbidden_keywords) == 2


class TestVisibilityAwareContextGetHintsByLevel:
    """Test get_hints_by_level() method."""

    def test_get_hints_by_level_single_match(self):
        """単一レベルのヒント取得."""
        hints = [
            VisibilityHint(category="section", entity_id="sec1", hint_text="hint1", level=AIVisibilityLevel.AWARE),
            VisibilityHint(category="section", entity_id="sec2", hint_text="hint2", level=AIVisibilityLevel.KNOW),
            VisibilityHint(category="section", entity_id="sec3", hint_text="hint3", level=AIVisibilityLevel.AWARE),
        ]
        ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            hints=hints,
        )
        aware_hints = ctx.get_hints_by_level(AIVisibilityLevel.AWARE)
        assert len(aware_hints) == 2
        assert all(h.level == AIVisibilityLevel.AWARE for h in aware_hints)

    def test_get_hints_by_level_no_match(self):
        """マッチなしの場合は空リスト."""
        hints = [
            VisibilityHint(category="section", entity_id="sec1", hint_text="hint1", level=AIVisibilityLevel.AWARE),
        ]
        ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            hints=hints,
        )
        know_hints = ctx.get_hints_by_level(AIVisibilityLevel.KNOW)
        assert know_hints == []

    def test_get_hints_by_level_empty_hints(self):
        """ヒントリストが空の場合."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        result = ctx.get_hints_by_level(AIVisibilityLevel.AWARE)
        assert result == []


class TestVisibilityAwareContextHasHints:
    """Test has_hints() method."""

    def test_has_hints_true(self):
        """ヒントが存在する場合 True."""
        hint = VisibilityHint(category="section", entity_id="sec1", hint_text="hint1", level=AIVisibilityLevel.AWARE)
        ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            hints=[hint],
        )
        assert ctx.has_hints() is True

    def test_has_hints_false(self):
        """ヒントがない場合 False."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        assert ctx.has_hints() is False


class TestVisibilityAwareContextCountExcluded:
    """Test count_excluded() method."""

    def test_count_excluded_empty(self):
        """除外なしの場合 0."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        assert ctx.count_excluded() == 0

    def test_count_excluded_with_sections(self):
        """除外セクションのカウント."""
        ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            excluded_sections=["sec1", "sec2", "sec3"],
        )
        assert ctx.count_excluded() == 3


class TestVisibilityAwareContextAddHint:
    """Test add_hint() method."""

    def test_add_hint_to_empty(self):
        """空リストにヒント追加."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        hint = VisibilityHint(category="section", entity_id="sec1", hint_text="hint1", level=AIVisibilityLevel.AWARE)
        ctx.add_hint(hint)
        assert len(ctx.hints) == 1
        assert ctx.hints[0].source_section == "section.sec1"

    def test_add_multiple_hints(self):
        """複数ヒント追加."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        ctx.add_hint(VisibilityHint(category="section", entity_id="sec1", hint_text="hint1", level=AIVisibilityLevel.AWARE))
        ctx.add_hint(VisibilityHint(category="section", entity_id="sec2", hint_text="hint2", level=AIVisibilityLevel.KNOW))
        assert len(ctx.hints) == 2


class TestVisibilityAwareContextAddExcludedSection:
    """Test add_excluded_section() method."""

    def test_add_excluded_section_to_empty(self):
        """空リストに除外セクション追加."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        ctx.add_excluded_section("character.villain")
        assert "character.villain" in ctx.excluded_sections

    def test_add_excluded_section_no_duplicate(self):
        """重複するセクションは追加されない."""
        ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            excluded_sections=["character.villain"],
        )
        ctx.add_excluded_section("character.villain")
        assert ctx.excluded_sections.count("character.villain") == 1

    def test_add_different_excluded_sections(self):
        """異なるセクションは追加される."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        ctx.add_excluded_section("sec1")
        ctx.add_excluded_section("sec2")
        assert len(ctx.excluded_sections) == 2


class TestVisibilityAwareContextMergeForbiddenKeywords:
    """Test merge_forbidden_keywords() method."""

    def test_merge_to_empty(self):
        """空リストにマージ."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        ctx.merge_forbidden_keywords(["royal", "princess"])
        assert "royal" in ctx.forbidden_keywords
        assert "princess" in ctx.forbidden_keywords

    def test_merge_with_existing(self):
        """既存のキーワードとマージ."""
        ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            forbidden_keywords=["royal"],
        )
        ctx.merge_forbidden_keywords(["princess", "queen"])
        assert len(ctx.forbidden_keywords) == 3
        assert "royal" in ctx.forbidden_keywords
        assert "princess" in ctx.forbidden_keywords
        assert "queen" in ctx.forbidden_keywords

    def test_merge_deduplicates(self):
        """重複キーワードは除去."""
        ctx = VisibilityAwareContext(
            base_context=FilteredContext(),
            forbidden_keywords=["royal", "princess"],
        )
        ctx.merge_forbidden_keywords(["royal", "queen"])
        assert ctx.forbidden_keywords.count("royal") == 1

    def test_merge_returns_sorted(self):
        """結果はソートされる."""
        ctx = VisibilityAwareContext(base_context=FilteredContext())
        ctx.merge_forbidden_keywords(["zebra", "apple", "middle"])
        assert ctx.forbidden_keywords == ["apple", "middle", "zebra"]


class TestVisibilityAwareContextToGhostWriterContext:
    """Test to_ghost_writer_context() method."""

    def test_basic_conversion(self):
        """基本的な変換."""
        base = FilteredContext(
            plot_l1="Theme: Adventure",
            scene_id="ep001/seq_01",
        )
        ctx = VisibilityAwareContext(
            base_context=base,
            current_visibility_level=AIVisibilityLevel.USE,
        )
        result = ctx.to_ghost_writer_context()
        assert result["plot_theme"] == "Theme: Adventure"
        assert result["_visibility_level"] == 3  # USE = 3
        assert result["_excluded_count"] == 0

    def test_conversion_with_hints(self):
        """ヒント付きの変換."""
        base = FilteredContext()
        ctx = VisibilityAwareContext(
            base_context=base,
            hints=[
                VisibilityHint(category="section", entity_id="sec1", hint_text="Hint about secret", level=AIVisibilityLevel.AWARE),
                VisibilityHint(category="section", entity_id="sec2", hint_text="Another hint", level=AIVisibilityLevel.KNOW),
            ],
        )
        result = ctx.to_ghost_writer_context()
        assert "foreshadow_hints" in result
        assert "Hint about secret" in result["foreshadow_hints"]
        assert "Another hint" in result["foreshadow_hints"]

    def test_conversion_with_excluded_sections(self):
        """除外セクション付きの変換."""
        base = FilteredContext()
        ctx = VisibilityAwareContext(
            base_context=base,
            excluded_sections=["sec1", "sec2", "sec3"],
        )
        result = ctx.to_ghost_writer_context()
        assert result["_excluded_count"] == 3

    def test_conversion_no_hints_no_foreshadow_key(self):
        """ヒントなしの場合 foreshadow_hints キーなし."""
        base = FilteredContext()
        ctx = VisibilityAwareContext(base_context=base)
        result = ctx.to_ghost_writer_context()
        assert "foreshadow_hints" not in result

    def test_conversion_includes_base_context_fields(self):
        """base_context のフィールドが含まれる."""
        base = FilteredContext(
            plot_l1="Theme",
            plot_l2="Chapter goal",
            summary_l1="Overall summary",
            characters={"Alice": "Protagonist"},
            world_settings={"Kingdom": "Fantasy realm"},
            style_guide="Write elegantly",
        )
        ctx = VisibilityAwareContext(base_context=base)
        result = ctx.to_ghost_writer_context()
        assert result["plot_theme"] == "Theme"
        assert result["plot_chapter"] == "Chapter goal"
        assert result["summary_overall"] == "Overall summary"
        assert result["character_Alice"] == "Protagonist"
        assert result["world_Kingdom"] == "Fantasy realm"
        assert result["style_guide"] == "Write elegantly"


class TestVisibilityAwareContextIntegration:
    """Integration tests for VisibilityAwareContext."""

    def test_full_workflow(self):
        """完全なワークフローテスト."""
        # 1. Base context 作成
        base = FilteredContext(
            plot_l1="Theme: Hidden royalty",
            plot_l2="Chapter: First encounter",
            characters={"Alice": "Village girl with mysterious past"},
            scene_id="ep005/seq_02",
            current_phase="arc_1",
        )

        # 2. VisibilityAwareContext 作成
        ctx = VisibilityAwareContext(
            base_context=base,
            current_visibility_level=AIVisibilityLevel.KNOW,
        )

        # 3. ヒント追加
        ctx.add_hint(VisibilityHint(
            category="character",
            entity_id="alice.royal_blood",
            hint_text="Alice carries herself with unexpected grace.",
            level=AIVisibilityLevel.AWARE,
        ))
        ctx.add_hint(VisibilityHint(
            category="world",
            entity_id="kingdom.succession",
            hint_text="The kingdom's succession rules are complex.",
            level=AIVisibilityLevel.KNOW,
        ))

        # 4. 除外セクション追加
        ctx.add_excluded_section("character.alice.true_identity")
        ctx.add_excluded_section("world.kingdom.secret_heir")

        # 5. 禁止キーワードマージ
        ctx.merge_forbidden_keywords(["princess", "heir", "royal blood"])

        # 検証
        assert ctx.has_hints() is True
        assert len(ctx.get_hints_by_level(AIVisibilityLevel.AWARE)) == 1
        assert len(ctx.get_hints_by_level(AIVisibilityLevel.KNOW)) == 1
        assert ctx.count_excluded() == 2
        assert "princess" in ctx.forbidden_keywords

        # Ghost Writer コンテキスト生成
        gw_ctx = ctx.to_ghost_writer_context()
        assert "plot_theme" in gw_ctx
        assert "foreshadow_hints" in gw_ctx
        assert gw_ctx["_excluded_count"] == 2
        assert gw_ctx["_visibility_level"] == 2  # KNOW = 2

