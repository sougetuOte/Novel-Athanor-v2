"""Tests for YAML frontmatter parser."""

import pytest

from src.core.parsers.frontmatter import ParseError, parse_frontmatter


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
