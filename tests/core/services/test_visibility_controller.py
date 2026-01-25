"""Tests for visibility controller.

セクション単位可視性判定とフィルタリング機能のテスト。
"""

import pytest

from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.services.visibility_controller import (
    FilteredContext,
    VisibilityController,
    filter_content_by_visibility,
)


class TestFilterContentByVisibility:
    """filter_content_by_visibility 関数のテスト."""

    def test_filter_hidden_section(self) -> None:
        """Level 0 (HIDDEN) のセクションを除外する."""
        content = """## 基本情報
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

    def test_filter_use_section(self) -> None:
        """Level 3 (USE) のセクションは制限なし."""
        content = """## 公開設定
<!-- ai_visibility: 3 -->
自由に使える情報
"""
        result = filter_content_by_visibility(content)

        assert "自由に使える情報" in result.content
        assert result.excluded_sections == []

    def test_default_is_use(self) -> None:
        """デフォルトは Level 3 (USE)."""
        content = """## セクション
可視性コメントなし
"""
        result = filter_content_by_visibility(content)

        assert "可視性コメントなし" in result.content

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

    def test_filter_with_custom_default(self) -> None:
        """カスタムデフォルトレベルを設定できる."""
        controller = VisibilityController(
            default_level=AIVisibilityLevel.HIDDEN
        )
        content = "## セクション\n内容"

        result = controller.filter(content)

        # デフォルトが HIDDEN なので除外される
        assert "内容" not in result.content

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

        content = "## セクション\n内容"
        result = controller.filter(content)

        assert "このキャラには秘密があります" in result.hints


class TestFilteredContext:
    """FilteredContext データクラスのテスト."""

    def test_create_context(self) -> None:
        """コンテキストを作成できる."""
        ctx = FilteredContext(
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
        ctx = FilteredContext(
            content="全て公開",
            hints=[],
            forbidden_keywords=[],
            excluded_sections=[],
        )

        assert ctx.has_restrictions is False

    def test_is_restricted_with_exclusions(self) -> None:
        """除外ありは制限あり."""
        ctx = FilteredContext(
            content="一部公開",
            hints=["ヒント"],
            forbidden_keywords=["禁止"],
            excluded_sections=["秘密"],
        )

        assert ctx.has_restrictions is True

    def test_summary(self) -> None:
        """サマリーを取得できる."""
        ctx = FilteredContext(
            content="内容",
            hints=["ヒント"],
            forbidden_keywords=["禁止1", "禁止2"],
            excluded_sections=["除外"],
        )

        summary = ctx.get_summary()
        assert "1" in summary  # 除外セクション数
        assert "2" in summary  # 禁止キーワード数
