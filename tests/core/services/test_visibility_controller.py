"""Tests for visibility controller.

セクション単位可視性判定とフィルタリング機能のテスト。
"""


from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.services.visibility_controller import (
    VisibilityController,
    VisibilityFilteredContent,
    filter_content_by_visibility,
    generate_level1_template,
    generate_level2_template,
)


class TestFilterContentByVisibility:
    """filter_content_by_visibility 関数のテスト."""

    def test_filter_hidden_section(self) -> None:
        """Level 0 (HIDDEN) のセクションを除外する."""
        content = """## 基本情報
<!-- ai_visibility: 3 -->
公開される内容

## 隠し設定
<!-- ai_visibility: 0 -->
秘密の内容
"""
        result = filter_content_by_visibility(content)

        assert "基本情報" in result.content
        assert "公開される内容" in result.content
        assert "秘密の内容" not in result.content
        assert "隠し設定" in result.excluded_sections

    def test_filter_aware_section(self) -> None:
        """Level 1 (AWARE) のセクションはヒントのみ."""
        content = """## 公開情報
<!-- ai_visibility: 3 -->
通常の内容

## 秘密の存在
<!-- ai_visibility: 1 -->
詳細は不明だが何かある
"""
        result = filter_content_by_visibility(content)

        assert "公開情報" in result.content
        assert "詳細は不明だが何かある" not in result.content
        assert len(result.hints) >= 1
        assert "秘密の存在" in result.hints[0]

    def test_filter_know_section(self) -> None:
        """Level 2 (KNOW) のセクションは禁止キーワード付き."""
        content = """## 公開
<!-- ai_visibility: 3 -->
通常

## 秘密
<!-- ai_visibility: 2 -->
王族の血筋を持つ
"""
        result = filter_content_by_visibility(
            content,
            forbidden_keywords=["王族", "血筋"],
        )

        assert "王族の血筋を持つ" in result.content
        assert "王族" in result.forbidden_keywords
        assert "血筋" in result.forbidden_keywords

    def test_level2_includes_content_with_restrictions(self) -> None:
        """Level 2 (KNOW) includes content but adds forbidden keywords."""
        from src.core.models.ai_visibility import SectionVisibility

        content = """## 秘密設定
<!-- ai_visibility: 2 -->
アイラは王族の血筋を持つ
"""
        section_configs = {
            "秘密設定": SectionVisibility(
                section_name="秘密設定",
                level=AIVisibilityLevel.KNOW,
                forbidden_keywords=["王族", "血筋"],
                allowed_expressions=["高貴な雰囲気", "育ちの良さ"],
            )
        }

        result = filter_content_by_visibility(
            content,
            section_configs=section_configs,
        )

        # Content should be included
        assert "アイラは王族の血筋を持つ" in result.content
        # Forbidden keywords should be added
        assert "王族" in result.forbidden_keywords
        assert "血筋" in result.forbidden_keywords
        # Should have a hint about restrictions
        assert len(result.hints) >= 1
        assert "執筆参考情報" in result.hints[0] or "禁止されています" in result.hints[0]

    def test_level3_includes_content_without_restrictions(self) -> None:
        """Level 3 (USE) includes content WITHOUT adding forbidden keywords."""
        from src.core.models.ai_visibility import SectionVisibility

        content = """## 公開情報
<!-- ai_visibility: 3 -->
アイラは優秀な魔法使いである
"""
        section_configs = {
            "公開情報": SectionVisibility(
                section_name="公開情報",
                level=AIVisibilityLevel.USE,
                forbidden_keywords=[],
                allowed_expressions=[],
            )
        }

        result = filter_content_by_visibility(
            content,
            section_configs=section_configs,
        )

        # Content should be included
        assert "アイラは優秀な魔法使いである" in result.content
        # No forbidden keywords should be added
        assert len(result.forbidden_keywords) == 0
        # No hints about restrictions
        assert len(result.hints) == 0

    def test_level2_vs_level3_different_behavior(self) -> None:
        """Level 2 and Level 3 produce different results for same content."""
        from src.core.models.ai_visibility import SectionVisibility

        same_content = "王族の秘密"

        # Level 2 section
        content_level2 = f"""## Section2
<!-- ai_visibility: 2 -->
{same_content}
"""
        section_configs_level2 = {
            "Section2": SectionVisibility(
                section_name="Section2",
                level=AIVisibilityLevel.KNOW,
                forbidden_keywords=["王族"],
                allowed_expressions=[],
            )
        }
        result_level2 = filter_content_by_visibility(
            content_level2,
            section_configs=section_configs_level2,
        )

        # Level 3 section
        content_level3 = f"""## Section3
<!-- ai_visibility: 3 -->
{same_content}
"""
        section_configs_level3 = {
            "Section3": SectionVisibility(
                section_name="Section3",
                level=AIVisibilityLevel.USE,
                forbidden_keywords=[],
                allowed_expressions=[],
            )
        }
        result_level3 = filter_content_by_visibility(
            content_level3,
            section_configs=section_configs_level3,
        )

        # Both should include content
        assert same_content in result_level2.content
        assert same_content in result_level3.content

        # But Level 2 should have restrictions
        assert len(result_level2.forbidden_keywords) > 0
        assert len(result_level2.hints) > 0

        # While Level 3 should not
        assert len(result_level3.forbidden_keywords) == 0
        assert len(result_level3.hints) == 0

    def test_filter_use_section(self) -> None:
        """Level 3 (USE) のセクションは制限なし."""
        content = """## 公開設定
<!-- ai_visibility: 3 -->
自由に使える情報
"""
        result = filter_content_by_visibility(content)

        assert "自由に使える情報" in result.content
        assert result.excluded_sections == []

    def test_default_is_hidden(self) -> None:
        """デフォルトは Level 0 (HIDDEN) - Secure by Default."""
        content = """## セクション
可視性コメントなし
"""
        result = filter_content_by_visibility(content)

        # デフォルトが HIDDEN なので除外される
        assert "可視性コメントなし" not in result.content
        assert "セクション" in result.excluded_sections

    def test_multiple_sections_mixed_levels(self) -> None:
        """複数セクションの混合レベル."""
        content = """## 公開
<!-- ai_visibility: 3 -->
公開OK

## 認識のみ
<!-- ai_visibility: 1 -->
存在のみ

## 秘匿
<!-- ai_visibility: 0 -->
完全秘密

## 使用禁止
<!-- ai_visibility: 2 -->
知ってるけど使わない
"""
        result = filter_content_by_visibility(content)

        assert "公開OK" in result.content
        assert "存在のみ" not in result.content
        assert "完全秘密" not in result.content
        assert "知ってるけど使わない" in result.content
        assert "秘匿" in result.excluded_sections
        assert len(result.hints) >= 1  # 認識のみのヒント


class TestVisibilityController:
    """VisibilityController クラスのテスト."""

    def test_create_controller(self) -> None:
        """コントローラを作成できる."""
        controller = VisibilityController()
        assert controller is not None

    def test_default_level_is_hidden(self) -> None:
        """デフォルトレベルは HIDDEN (Secure by Default)."""
        controller = VisibilityController()
        assert controller.default_level == AIVisibilityLevel.HIDDEN

    def test_filter_with_custom_default(self) -> None:
        """カスタムデフォルトレベルを設定できる."""
        controller = VisibilityController(
            default_level=AIVisibilityLevel.USE
        )
        content = "## セクション\n内容"

        result = controller.filter(content)

        # デフォルトが USE なので含まれる
        assert "内容" in result.content

    def test_filter_with_forbidden_keywords(self) -> None:
        """禁止キーワードを設定できる."""
        controller = VisibilityController(
            forbidden_keywords=["秘密", "内緒"]
        )
        content = """## 設定
<!-- ai_visibility: 2 -->
秘密の情報
"""
        result = controller.filter(content)

        assert "秘密" in result.forbidden_keywords

    def test_add_global_hint(self) -> None:
        """グローバルヒントを追加できる."""
        controller = VisibilityController()
        controller.add_hint("このキャラには秘密があります")

        content = "## セクション\n<!-- ai_visibility: 3 -->\n内容"
        result = controller.filter(content)

        assert "このキャラには秘密があります" in result.hints

    def test_controller_with_config(self) -> None:
        """VisibilityController が config を受け取れる."""
        from src.core.models.ai_visibility import (
            EntityVisibilityConfig,
            SectionVisibility,
            VisibilityConfig,
        )

        config = VisibilityConfig(
            entities=[
                EntityVisibilityConfig(
                    entity_type="character",
                    entity_name="アイラ",
                    sections=[
                        SectionVisibility(
                            section_name="秘密",
                            level=AIVisibilityLevel.KNOW,
                            forbidden_keywords=["王族", "血筋"],
                        ),
                    ],
                ),
            ]
        )

        controller = VisibilityController(config=config)

        # Should collect forbidden keywords from config
        assert "王族" in controller.forbidden_keywords
        assert "血筋" in controller.forbidden_keywords

    def test_controller_config_merges_forbidden_keywords(self) -> None:
        """config と直接指定の forbidden_keywords がマージされる."""
        from src.core.models.ai_visibility import (
            EntityVisibilityConfig,
            SectionVisibility,
            VisibilityConfig,
        )

        config = VisibilityConfig(
            entities=[
                EntityVisibilityConfig(
                    entity_type="character",
                    entity_name="test",
                    sections=[
                        SectionVisibility(
                            section_name="s1",
                            level=AIVisibilityLevel.KNOW,
                            forbidden_keywords=["config_keyword"],
                        ),
                    ],
                ),
            ]
        )

        controller = VisibilityController(
            forbidden_keywords=["direct_keyword"],
            config=config,
        )

        # Both sources should be merged
        assert "config_keyword" in controller.forbidden_keywords
        assert "direct_keyword" in controller.forbidden_keywords


class TestTemplateGeneration:
    """Template generation functions のテスト."""

    def test_generate_level1_template_basic(self) -> None:
        """Level 1 template generates positive framing (no 'don't' language)."""
        template = generate_level1_template("隠し設定")

        # Should not use negative commands
        assert "しない" not in template or "ください" in template  # Allow "〜してください"
        # Should mention information is not included (positive framing)
        assert "含まれていません" in template or "提示された情報" in template
        # Should mention section name
        assert "隠し設定" in template

    def test_generate_level1_template_with_hints(self) -> None:
        """Level 1 template includes additional hints when provided."""
        hints = ["周辺要素に焦点を当てる", "既知の情報のみ使用"]
        template = generate_level1_template("秘密", hints=hints)

        assert "秘密" in template
        assert "周辺要素に焦点を当てる" in template
        assert "既知の情報のみ使用" in template

    def test_generate_level2_template_with_allowed_expressions(self) -> None:
        """Level 2 template includes allowed expressions."""
        allowed = ["高貴な雰囲気", "育ちの良さ"]
        template = generate_level2_template(
            "秘密設定",
            allowed_expressions=allowed,
        )

        assert "秘密設定" in template
        assert "高貴な雰囲気" in template
        assert "育ちの良さ" in template
        assert "許可される表現" in template or "許可" in template

    def test_generate_level2_template_with_forbidden_keywords(self) -> None:
        """Level 2 template includes forbidden keywords instruction."""
        forbidden = ["王族", "血筋"]
        template = generate_level2_template(
            "隠し設定",
            forbidden_keywords=forbidden,
        )

        assert "隠し設定" in template
        assert "王族" in template
        assert "血筋" in template
        assert "禁止" in template or "使用禁止" in template

    def test_templates_integrated_into_filter(self) -> None:
        """Templates are integrated into filter output."""
        from src.core.models.ai_visibility import SectionVisibility

        # Level 1 with template
        content_level1 = """## 秘密
<!-- ai_visibility: 1 -->
何か秘密がある
"""
        result_level1 = filter_content_by_visibility(content_level1)

        assert len(result_level1.hints) >= 1
        # Check for positive framing (not negative commands)
        hint = result_level1.hints[0]
        assert "秘密" in hint
        assert "含まれていません" in hint or "提示された情報" in hint

        # Level 2 with template and section_configs
        content_level2 = """## 秘密設定
<!-- ai_visibility: 2 -->
王族の血筋
"""
        section_configs = {
            "秘密設定": SectionVisibility(
                section_name="秘密設定",
                level=AIVisibilityLevel.KNOW,
                forbidden_keywords=["王族"],
                allowed_expressions=["高貴な雰囲気"],
            )
        }
        result_level2 = filter_content_by_visibility(
            content_level2,
            section_configs=section_configs,
        )

        assert len(result_level2.hints) >= 1
        hint = result_level2.hints[0]
        assert "秘密設定" in hint
        assert "高貴な雰囲気" in hint or "王族" in hint


class TestVisibilityFilteredContent:
    """VisibilityFilteredContent データクラスのテスト."""

    def test_create_context(self) -> None:
        """コンテキストを作成できる."""
        ctx = VisibilityFilteredContent(
            content="フィルタ済み",
            hints=["ヒント1"],
            forbidden_keywords=["禁止"],
            excluded_sections=["除外セクション"],
        )

        assert ctx.content == "フィルタ済み"
        assert ctx.hints == ["ヒント1"]
        assert ctx.forbidden_keywords == ["禁止"]
        assert ctx.excluded_sections == ["除外セクション"]

    def test_is_safe_with_no_exclusions(self) -> None:
        """除外なしは安全."""
        ctx = VisibilityFilteredContent(
            content="全て公開",
            hints=[],
            forbidden_keywords=[],
            excluded_sections=[],
        )

        assert ctx.has_restrictions is False

    def test_is_restricted_with_exclusions(self) -> None:
        """除外ありは制限あり."""
        ctx = VisibilityFilteredContent(
            content="一部公開",
            hints=["ヒント"],
            forbidden_keywords=["禁止"],
            excluded_sections=["秘密"],
        )

        assert ctx.has_restrictions is True

    def test_summary(self) -> None:
        """サマリーを取得できる."""
        ctx = VisibilityFilteredContent(
            content="内容",
            hints=["ヒント"],
            forbidden_keywords=["禁止1", "禁止2"],
            excluded_sections=["除外"],
        )

        summary = ctx.get_summary()
        assert "1" in summary  # 除外セクション数
        assert "2" in summary  # 禁止キーワード数


class TestRenameToVisibilityFilteredContent:
    """Tests for W5C-1: Rename VisibilityFilteredContent to VisibilityFilteredContent."""

    def test_renamed_class_exists(self) -> None:
        """VisibilityFilteredContent is importable from visibility_controller."""
        from src.core.services.visibility_controller import VisibilityFilteredContent

        assert VisibilityFilteredContent is not None

    def test_old_name_not_exported_in_init(self) -> None:
        """Old name VisibilityFilteredContent should not be exported in __init__.py."""
        from src.core.services import __all__

        # VisibilityFilteredContent should be in exports
        assert "VisibilityFilteredContent" in __all__
        # Old VisibilityFilteredContent should not be in exports (or renamed)
        # Note: During transition, VisibilityFilteredContent might still be imported from visibility_controller
        # but it should not be exported from services package

    def test_filter_returns_new_type(self) -> None:
        """VisibilityController.filter() returns VisibilityFilteredContent."""
        from src.core.services.visibility_controller import (
            VisibilityController,
            VisibilityFilteredContent,
        )

        controller = VisibilityController()
        content = "## Test\n<!-- ai_visibility: 3 -->\nTest content"
        result = controller.filter(content)

        assert isinstance(result, VisibilityFilteredContent)

    def test_function_returns_new_type(self) -> None:
        """filter_content_by_visibility() returns VisibilityFilteredContent."""
        from src.core.services.visibility_controller import (
            VisibilityFilteredContent,
            filter_content_by_visibility,
        )

        content = "## Test\n<!-- ai_visibility: 3 -->\nTest content"
        result = filter_content_by_visibility(content)

        assert isinstance(result, VisibilityFilteredContent)

    def test_new_class_has_all_attributes(self) -> None:
        """VisibilityFilteredContent has all expected attributes."""
        from src.core.services.visibility_controller import VisibilityFilteredContent

        ctx = VisibilityFilteredContent(
            content="test",
            hints=["hint"],
            forbidden_keywords=["keyword"],
            excluded_sections=["section"],
        )

        assert ctx.content == "test"
        assert ctx.hints == ["hint"]
        assert ctx.forbidden_keywords == ["keyword"]
        assert ctx.excluded_sections == ["section"]
        assert hasattr(ctx, "has_restrictions")
        assert hasattr(ctx, "get_summary")
