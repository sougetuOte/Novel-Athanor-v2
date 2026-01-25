"""Tests for visibility comment parser.

HTMLコメント `<!-- ai_visibility: N -->` のパーステスト。
"""

import pytest

from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.parsers.visibility_comment import (
    VisibilityMarker,
    parse_visibility_comments,
    extract_section_visibility,
)


class TestParseVisibilityComments:
    """parse_visibility_comments 関数のテスト."""

    def test_parse_single_comment(self) -> None:
        """単一のコメントをパースできる."""
        content = "## Section\n<!-- ai_visibility: 0 -->\nContent here"
        markers = parse_visibility_comments(content)

        assert len(markers) == 1
        assert markers[0].level == AIVisibilityLevel.HIDDEN
        assert markers[0].line_number == 2

    def test_parse_multiple_comments(self) -> None:
        """複数のコメントをパースできる."""
        content = """## Section 1
<!-- ai_visibility: 0 -->
Hidden content

## Section 2
<!-- ai_visibility: 3 -->
Visible content
"""
        markers = parse_visibility_comments(content)

        assert len(markers) == 2
        assert markers[0].level == AIVisibilityLevel.HIDDEN
        assert markers[1].level == AIVisibilityLevel.USE

    def test_parse_all_levels(self) -> None:
        """全レベル（0-3）をパースできる."""
        for level in range(4):
            content = f"<!-- ai_visibility: {level} -->"
            markers = parse_visibility_comments(content)

            assert len(markers) == 1
            assert markers[0].level == AIVisibilityLevel(level)

    def test_parse_with_whitespace(self) -> None:
        """空白を含むコメントをパースできる."""
        content = "<!--  ai_visibility:  2  -->"
        markers = parse_visibility_comments(content)

        assert len(markers) == 1
        assert markers[0].level == AIVisibilityLevel.KNOW

    def test_parse_no_comments(self) -> None:
        """コメントがない場合は空リストを返す."""
        content = "## Section\nNo visibility comments here"
        markers = parse_visibility_comments(content)

        assert markers == []

    def test_invalid_level_raises_error(self) -> None:
        """無効なレベル（5）はエラーを発生させる."""
        content = "<!-- ai_visibility: 5 -->"

        with pytest.raises(ValueError, match="Invalid visibility level"):
            parse_visibility_comments(content)

    def test_non_numeric_level_raises_error(self) -> None:
        """数値以外のレベルはエラーを発生させる."""
        content = "<!-- ai_visibility: abc -->"

        with pytest.raises(ValueError, match="Invalid visibility level"):
            parse_visibility_comments(content)

    def test_negative_level_raises_error(self) -> None:
        """負のレベルはエラーを発生させる."""
        content = "<!-- ai_visibility: -1 -->"

        with pytest.raises(ValueError, match="Invalid visibility level"):
            parse_visibility_comments(content)


class TestExtractSectionVisibility:
    """extract_section_visibility 関数のテスト."""

    def test_extract_section_with_visibility(self) -> None:
        """セクションの可視性を抽出できる."""
        content = """## 基本情報
公開される内容

## 隠し設定
<!-- ai_visibility: 0 -->
秘密の内容
"""
        sections = extract_section_visibility(content)

        assert "基本情報" in sections
        assert sections["基本情報"] == AIVisibilityLevel.USE  # default
        assert "隠し設定" in sections
        assert sections["隠し設定"] == AIVisibilityLevel.HIDDEN

    def test_default_visibility(self) -> None:
        """デフォルト可視性を指定できる."""
        content = """## Section
Content
"""
        sections = extract_section_visibility(
            content, default_level=AIVisibilityLevel.KNOW
        )

        assert sections["Section"] == AIVisibilityLevel.KNOW

    def test_nested_sections(self) -> None:
        """ネストしたセクションを処理できる."""
        content = """## Parent
<!-- ai_visibility: 2 -->

### Child
内容
"""
        sections = extract_section_visibility(content)

        assert sections["Parent"] == AIVisibilityLevel.KNOW

    def test_visibility_applies_to_preceding_section(self) -> None:
        """可視性コメントは直前のセクションに適用される."""
        content = """## Section A
Content A

## Section B
<!-- ai_visibility: 1 -->
Content B

## Section C
Content C
"""
        sections = extract_section_visibility(content)

        assert sections["Section A"] == AIVisibilityLevel.USE
        assert sections["Section B"] == AIVisibilityLevel.AWARE
        assert sections["Section C"] == AIVisibilityLevel.USE


class TestVisibilityMarker:
    """VisibilityMarker データクラスのテスト."""

    def test_create_marker(self) -> None:
        """マーカーを作成できる."""
        marker = VisibilityMarker(
            level=AIVisibilityLevel.HIDDEN,
            line_number=10,
        )

        assert marker.level == AIVisibilityLevel.HIDDEN
        assert marker.line_number == 10

    def test_marker_with_section_name(self) -> None:
        """セクション名付きマーカーを作成できる."""
        marker = VisibilityMarker(
            level=AIVisibilityLevel.KNOW,
            line_number=5,
            section_name="隠し設定",
        )

        assert marker.section_name == "隠し設定"
