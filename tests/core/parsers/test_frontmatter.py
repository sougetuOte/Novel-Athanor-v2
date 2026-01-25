"""Tests for YAML frontmatter parser."""

import pytest

from src.core.parsers.frontmatter import (
    ParseError,
    ParseResult,
    parse_frontmatter,
    parse_frontmatter_with_fallback,
)


class TestParseFrontmatter:
    """parse_frontmatter 関数のテスト."""

    def test_parse_valid_frontmatter(self) -> None:
        """正常な frontmatter を解析できる."""
        content = """---
type: episode
title: "エピソード1"
episode_number: 1
---

# 本文
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter["type"] == "episode"
        assert frontmatter["title"] == "エピソード1"
        assert frontmatter["episode_number"] == 1
        assert "# 本文" in body

    def test_parse_frontmatter_with_list(self) -> None:
        """リストを含む frontmatter を解析できる."""
        content = """---
tags:
  - main_character
  - hero
---

本文
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter["tags"] == ["main_character", "hero"]
        assert "本文" in body

    def test_parse_no_frontmatter(self) -> None:
        """frontmatter がない場合は空辞書を返す."""
        content = "# タイトル\n\n本文です。"

        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert "# タイトル" in body

    def test_parse_empty_frontmatter(self) -> None:
        """空の frontmatter を解析できる."""
        content = """---
---

本文
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert "本文" in body

    def test_parse_invalid_yaml_raises_error(self) -> None:
        """不正な YAML の場合は ParseError を発生させる."""
        content = """---
invalid: yaml: syntax: error
  bad indentation
---

本文
"""
        with pytest.raises(ParseError):
            parse_frontmatter(content)

    def test_parse_frontmatter_preserves_body(self) -> None:
        """本文が正確に保持される."""
        content = """---
title: test
---

## セクション1

段落1。

## セクション2

段落2。
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter["title"] == "test"
        assert "## セクション1" in body
        assert "## セクション2" in body
        assert "段落1。" in body
        assert "段落2。" in body

    def test_parse_empty_content(self) -> None:
        """空の内容を解析できる."""
        frontmatter, body = parse_frontmatter("")

        assert frontmatter == {}
        assert body == ""

    def test_parse_nested_yaml(self) -> None:
        """ネストした YAML を解析できる."""
        content = """---
character:
  name: "太郎"
  attributes:
    strength: 10
    intelligence: 8
---

本文
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter["character"]["name"] == "太郎"
        assert frontmatter["character"]["attributes"]["strength"] == 10


class TestParseFrontmatterWithFallback:
    """parse_frontmatter_with_fallback 関数のテスト."""

    def test_fallback_returns_structured_on_success(self) -> None:
        """正常パース時は structured タイプを返す."""
        content = """---
type: episode
title: "テスト"
---

本文です。
"""
        result = parse_frontmatter_with_fallback(content)

        assert result.result_type == "structured"
        assert result.frontmatter is not None
        assert result.frontmatter["type"] == "episode"
        assert "本文です。" in result.body  # type: ignore[operator]
        assert result.error is None

    def test_fallback_returns_raw_on_invalid_yaml(self) -> None:
        """不正な YAML の場合は raw_text タイプを返す."""
        content = """---
invalid: yaml: syntax: error
  bad indentation
---

本文です。
"""
        result = parse_frontmatter_with_fallback(content)

        assert result.result_type == "raw_text"
        assert result.raw_content == content
        assert result.error is not None
        assert "Invalid YAML" in result.error

    def test_fallback_preserves_content_on_error(self) -> None:
        """エラー時も元のコンテンツを保持する."""
        content = "壊れた: データ: ここ\n本文"
        result = parse_frontmatter_with_fallback(content)

        # frontmatter がない場合は正常扱い
        assert result.result_type == "structured"
        assert result.frontmatter == {}

    def test_fallback_handles_empty_content(self) -> None:
        """空のコンテンツを処理できる."""
        result = parse_frontmatter_with_fallback("")

        assert result.result_type == "structured"
        assert result.frontmatter == {}
        assert result.body == ""


class TestParseResult:
    """ParseResult データクラスのテスト."""

    def test_create_structured_result(self) -> None:
        """structured タイプの結果を作成できる."""
        result = ParseResult(
            result_type="structured",
            frontmatter={"title": "test"},
            body="本文",
        )

        assert result.result_type == "structured"
        assert result.frontmatter == {"title": "test"}
        assert result.body == "本文"
        assert result.raw_content is None
        assert result.error is None

    def test_create_raw_text_result(self) -> None:
        """raw_text タイプの結果を作成できる."""
        result = ParseResult(
            result_type="raw_text",
            raw_content="生テキスト",
            error="パースエラー",
        )

        assert result.result_type == "raw_text"
        assert result.raw_content == "生テキスト"
        assert result.error == "パースエラー"
        assert result.frontmatter is None
        assert result.body is None
