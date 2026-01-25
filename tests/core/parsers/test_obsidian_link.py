"""Tests for Obsidian link parser."""

import pytest

from src.core.parsers.obsidian_link import ObsidianLink, extract_links, parse_link


class TestParseLink:
    """parse_link 関数のテスト."""

    def test_parse_simple_link(self) -> None:
        """シンプルなリンクを解析できる."""
        link = parse_link("[[キャラ名]]")
        assert link.target == "キャラ名"
        assert link.display is None
        assert link.heading is None
        assert link.block_id is None

    def test_parse_link_with_alias(self) -> None:
        """エイリアス付きリンクを解析できる."""
        link = parse_link("[[filename|表示テキスト]]")
        assert link.target == "filename"
        assert link.display == "表示テキスト"

    def test_parse_link_with_path(self) -> None:
        """パス付きリンクを解析できる."""
        link = parse_link("[[path/to/filename]]")
        assert link.target == "path/to/filename"

    def test_parse_link_with_heading(self) -> None:
        """見出しへのリンクを解析できる."""
        link = parse_link("[[filename#見出し]]")
        assert link.target == "filename"
        assert link.heading == "見出し"

    def test_parse_link_with_block_id(self) -> None:
        """ブロックIDへのリンクを解析できる."""
        link = parse_link("[[filename#^block-123]]")
        assert link.target == "filename"
        assert link.block_id == "block-123"

    def test_parse_link_with_heading_and_alias(self) -> None:
        """見出しとエイリアス付きリンクを解析できる."""
        link = parse_link("[[filename#見出し|表示テキスト]]")
        assert link.target == "filename"
        assert link.heading == "見出し"
        assert link.display == "表示テキスト"

    def test_parse_link_with_path_heading_alias(self) -> None:
        """パス、見出し、エイリアス付きリンクを解析できる."""
        link = parse_link("[[path/to/file#heading|alias]]")
        assert link.target == "path/to/file"
        assert link.heading == "heading"
        assert link.display == "alias"

    def test_parse_invalid_link_returns_none(self) -> None:
        """無効なリンクは None を返す."""
        assert parse_link("not a link") is None
        assert parse_link("[single bracket]") is None
        assert parse_link("[[unclosed") is None

    def test_parse_empty_link(self) -> None:
        """空のリンクは None を返す."""
        assert parse_link("[[]]") is None


class TestExtractLinks:
    """extract_links 関数のテスト."""

    def test_extract_single_link(self) -> None:
        """1つのリンクを抽出できる."""
        text = "これは [[キャラ名]] へのリンクです。"
        links = extract_links(text)
        assert len(links) == 1
        assert links[0].target == "キャラ名"

    def test_extract_multiple_links(self) -> None:
        """複数のリンクを抽出できる."""
        text = """
## 登場キャラクター

- [[キャラ名1]]
- [[キャラ名2]]
- [[キャラ名3]]
"""
        links = extract_links(text)
        assert len(links) == 3
        assert links[0].target == "キャラ名1"
        assert links[1].target == "キャラ名2"
        assert links[2].target == "キャラ名3"

    def test_extract_links_with_various_formats(self) -> None:
        """様々なフォーマットのリンクを抽出できる."""
        text = """
- [[simple]]
- [[path/to/file]]
- [[with alias|表示名]]
- [[with heading#見出し]]
"""
        links = extract_links(text)
        assert len(links) == 4

    def test_extract_no_links(self) -> None:
        """リンクがない場合は空リストを返す."""
        text = "リンクのないテキストです。"
        links = extract_links(text)
        assert links == []

    def test_extract_links_preserves_order(self) -> None:
        """リンクの出現順を保持する."""
        text = "[[first]] と [[second]] と [[third]]"
        links = extract_links(text)
        assert len(links) == 3
        assert links[0].target == "first"
        assert links[1].target == "second"
        assert links[2].target == "third"


class TestObsidianLink:
    """ObsidianLink データクラスのテスト."""

    def test_create_link(self) -> None:
        """リンクを作成できる."""
        link = ObsidianLink(
            target="filename",
            display="表示名",
            heading="見出し",
        )
        assert link.target == "filename"
        assert link.display == "表示名"
        assert link.heading == "見出し"
        assert link.block_id is None

    def test_link_defaults(self) -> None:
        """デフォルト値が設定される."""
        link = ObsidianLink(target="filename")
        assert link.display is None
        assert link.heading is None
        assert link.block_id is None

    def test_link_to_markdown(self) -> None:
        """Markdown リンク形式に変換できる."""
        link = ObsidianLink(target="filename")
        assert link.to_markdown() == "[[filename]]"

        link_with_alias = ObsidianLink(target="filename", display="表示名")
        assert link_with_alias.to_markdown() == "[[filename|表示名]]"

        link_with_heading = ObsidianLink(target="filename", heading="見出し")
        assert link_with_heading.to_markdown() == "[[filename#見出し]]"

        link_with_block = ObsidianLink(target="filename", block_id="abc123")
        assert link_with_block.to_markdown() == "[[filename#^abc123]]"

    def test_link_display_text(self) -> None:
        """表示テキストを取得できる."""
        link = ObsidianLink(target="filename")
        assert link.display_text == "filename"

        link_with_alias = ObsidianLink(target="filename", display="表示名")
        assert link_with_alias.display_text == "表示名"

    def test_link_filename(self) -> None:
        """ファイル名部分を取得できる."""
        link = ObsidianLink(target="path/to/filename")
        assert link.filename == "filename"

        link_simple = ObsidianLink(target="filename")
        assert link_simple.filename == "filename"
