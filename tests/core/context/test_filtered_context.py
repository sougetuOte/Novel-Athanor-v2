"""Tests for FilteredContext data class."""


from src.core.context.filtered_context import FilteredContext


class TestFilteredContextCreation:
    """Test FilteredContext instance creation."""

    def test_create_empty_context(self):
        """空のコンテキストを生成できる."""
        ctx = FilteredContext()
        assert ctx.plot_l1 is None
        assert ctx.plot_l2 is None
        assert ctx.plot_l3 is None
        assert ctx.summary_l1 is None
        assert ctx.summary_l2 is None
        assert ctx.summary_l3 is None
        assert ctx.characters == {}
        assert ctx.world_settings == {}
        assert ctx.style_guide is None
        assert ctx.scene_id == ""
        assert ctx.current_phase is None
        assert ctx.warnings == []

    def test_create_with_all_fields(self):
        """全フィールドを指定して生成できる."""
        ctx = FilteredContext(
            plot_l1="Theme: Redemption",
            plot_l2="Chapter goal: Hero confronts past",
            plot_l3="Scene: Flashback sequence",
            summary_l1="Overall summary",
            summary_l2="Chapter summary",
            summary_l3="Recent summary",
            characters={"Alice": "Protagonist details"},
            world_settings={"Magic": "Magic system rules"},
            style_guide="Third person limited",
            scene_id="ep010/seq_01",
            current_phase="arc_1_reveal",
            warnings=["Some data was stale"],
        )
        assert ctx.plot_l1 == "Theme: Redemption"
        assert ctx.characters["Alice"] == "Protagonist details"
        assert ctx.world_settings["Magic"] == "Magic system rules"
        assert len(ctx.warnings) == 1


class TestFilteredContextHasPlot:
    """Test has_plot() method."""

    def test_has_plot_with_l1_only(self):
        """plot_l1 のみで has_plot() は True."""
        ctx = FilteredContext(plot_l1="Theme")
        assert ctx.has_plot() is True

    def test_has_plot_with_l2_only(self):
        """plot_l2 のみで has_plot() は True."""
        ctx = FilteredContext(plot_l2="Chapter goal")
        assert ctx.has_plot() is True

    def test_has_plot_with_l3_only(self):
        """plot_l3 のみで has_plot() は True."""
        ctx = FilteredContext(plot_l3="Scene")
        assert ctx.has_plot() is True

    def test_has_plot_false_when_empty(self):
        """プロット情報がない場合は False."""
        ctx = FilteredContext()
        assert ctx.has_plot() is False


class TestFilteredContextHasSummary:
    """Test has_summary() method."""

    def test_has_summary_with_l1_only(self):
        """summary_l1 のみで has_summary() は True."""
        ctx = FilteredContext(summary_l1="Overall")
        assert ctx.has_summary() is True

    def test_has_summary_with_l3_only(self):
        """summary_l3 のみで has_summary() は True."""
        ctx = FilteredContext(summary_l3="Recent")
        assert ctx.has_summary() is True

    def test_has_summary_false_when_empty(self):
        """サマリ情報がない場合は False."""
        ctx = FilteredContext()
        assert ctx.has_summary() is False


class TestFilteredContextCharacters:
    """Test character-related methods."""

    def test_get_character_names_empty(self):
        """キャラクターがない場合は空リスト."""
        ctx = FilteredContext()
        assert ctx.get_character_names() == []

    def test_get_character_names_with_characters(self):
        """キャラクター名のリストを取得."""
        ctx = FilteredContext(
            characters={
                "Alice": "Protagonist",
                "Bob": "Antagonist",
                "Charlie": "Support",
            }
        )
        names = ctx.get_character_names()
        assert len(names) == 3
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names


class TestFilteredContextWarnings:
    """Test warning-related methods."""

    def test_add_warning(self):
        """警告を追加できる."""
        ctx = FilteredContext()
        ctx.add_warning("Warning 1")
        ctx.add_warning("Warning 2")
        assert len(ctx.warnings) == 2
        assert "Warning 1" in ctx.warnings
        assert "Warning 2" in ctx.warnings

    def test_initial_warnings_preserved(self):
        """初期警告に追加できる."""
        ctx = FilteredContext(warnings=["Initial warning"])
        ctx.add_warning("New warning")
        assert len(ctx.warnings) == 2


class TestFilteredContextToPromptDict:
    """Test to_prompt_dict() method."""

    def test_empty_context_to_dict(self):
        """空コンテキストは空辞書を返す."""
        ctx = FilteredContext()
        d = ctx.to_prompt_dict()
        assert d == {}

    def test_plot_fields_in_dict(self):
        """プロットフィールドが辞書に含まれる."""
        ctx = FilteredContext(
            plot_l1="Theme",
            plot_l2="Chapter",
            plot_l3="Scene",
        )
        d = ctx.to_prompt_dict()
        assert d["plot_theme"] == "Theme"
        assert d["plot_chapter"] == "Chapter"
        assert d["plot_scene"] == "Scene"

    def test_summary_fields_in_dict(self):
        """サマリフィールドが辞書に含まれる."""
        ctx = FilteredContext(
            summary_l1="Overall",
            summary_l2="Chapter",
            summary_l3="Recent",
        )
        d = ctx.to_prompt_dict()
        assert d["summary_overall"] == "Overall"
        assert d["summary_chapter"] == "Chapter"
        assert d["summary_recent"] == "Recent"

    def test_characters_in_dict(self):
        """キャラクター情報が辞書に含まれる."""
        ctx = FilteredContext(
            characters={"Alice": "Details", "Bob": "Info"}
        )
        d = ctx.to_prompt_dict()
        assert d["character_Alice"] == "Details"
        assert d["character_Bob"] == "Info"

    def test_world_settings_in_dict(self):
        """世界観設定が辞書に含まれる."""
        ctx = FilteredContext(
            world_settings={"Magic": "Rules", "Technology": "Limits"}
        )
        d = ctx.to_prompt_dict()
        assert d["world_Magic"] == "Rules"
        assert d["world_Technology"] == "Limits"

    def test_style_guide_in_dict(self):
        """スタイルガイドが辞書に含まれる."""
        ctx = FilteredContext(style_guide="Third person limited")
        d = ctx.to_prompt_dict()
        assert d["style_guide"] == "Third person limited"

    def test_none_fields_excluded(self):
        """None のフィールドは辞書に含まれない."""
        ctx = FilteredContext(plot_l1="Theme")  # Only plot_l1
        d = ctx.to_prompt_dict()
        assert "plot_theme" in d
        assert "plot_chapter" not in d
        assert "plot_scene" not in d


class TestFilteredContextMerge:
    """Test merge() method."""

    def test_merge_empty_contexts(self):
        """空コンテキスト同士のマージ."""
        ctx1 = FilteredContext()
        ctx2 = FilteredContext()
        merged = ctx1.merge(ctx2)
        assert merged.plot_l1 is None
        assert merged.characters == {}

    def test_merge_preserves_self_values(self):
        """self の値が優先される."""
        ctx1 = FilteredContext(plot_l1="Original")
        ctx2 = FilteredContext(plot_l1="Other")
        merged = ctx1.merge(ctx2)
        assert merged.plot_l1 == "Original"

    def test_merge_fills_none_values(self):
        """self が None の場合は other の値を使用."""
        ctx1 = FilteredContext(plot_l1="Theme")
        ctx2 = FilteredContext(plot_l2="Chapter")
        merged = ctx1.merge(ctx2)
        assert merged.plot_l1 == "Theme"
        assert merged.plot_l2 == "Chapter"

    def test_merge_combines_characters(self):
        """キャラクター辞書をマージ."""
        ctx1 = FilteredContext(characters={"Alice": "A"})
        ctx2 = FilteredContext(characters={"Bob": "B"})
        merged = ctx1.merge(ctx2)
        assert "Alice" in merged.characters
        assert "Bob" in merged.characters

    def test_merge_combines_world_settings(self):
        """世界観設定辞書をマージ."""
        ctx1 = FilteredContext(world_settings={"Magic": "Rules"})
        ctx2 = FilteredContext(world_settings={"Tech": "Limits"})
        merged = ctx1.merge(ctx2)
        assert "Magic" in merged.world_settings
        assert "Tech" in merged.world_settings

    def test_merge_combines_warnings(self):
        """警告リストを結合."""
        ctx1 = FilteredContext(warnings=["W1"])
        ctx2 = FilteredContext(warnings=["W2"])
        merged = ctx1.merge(ctx2)
        assert "W1" in merged.warnings
        assert "W2" in merged.warnings
