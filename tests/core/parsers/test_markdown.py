"""Tests for Markdown body extractor."""


from src.core.parsers.markdown import Section, extract_body, extract_sections


class TestExtractBody:
    """extract_body 関数のテスト."""

    def test_extract_body_from_content_with_frontmatter(self) -> None:
        """frontmatter 付きコンテンツから本文を抽出."""
        content = """---
title: test
---

# 本文タイトル

段落。
"""
        body = extract_body(content)

        assert "# 本文タイトル" in body
        assert "段落。" in body
        assert "---" not in body
        assert "title: test" not in body

    def test_extract_body_without_frontmatter(self) -> None:
        """frontmatter なしのコンテンツはそのまま返す."""
        content = "# タイトル\n\n本文です。"

        body = extract_body(content)

        assert body == content


class TestExtractSections:
    """extract_sections 関数のテスト."""

    def test_extract_single_section(self) -> None:
        """単一セクションを抽出できる."""
        body = """# メインタイトル

導入文です。
"""
        sections = extract_sections(body)

        assert len(sections) == 1
        assert sections[0].title == "メインタイトル"
        assert sections[0].level == 1
        assert "導入文です。" in sections[0].content

    def test_extract_multiple_sections(self) -> None:
        """複数セクションを抽出できる."""
        body = """# メインタイトル

導入文

## セクション1

セクション1の内容

## セクション2

セクション2の内容
"""
        sections = extract_sections(body)

        assert len(sections) == 3
        assert sections[0].title == "メインタイトル"
        assert sections[0].level == 1
        assert sections[1].title == "セクション1"
        assert sections[1].level == 2
        assert sections[2].title == "セクション2"
        assert sections[2].level == 2

    def test_extract_nested_sections(self) -> None:
        """ネストしたセクションを抽出できる."""
        body = """# レベル1

## レベル2

### レベル3

内容
"""
        sections = extract_sections(body)

        assert len(sections) == 3
        assert sections[0].level == 1
        assert sections[1].level == 2
        assert sections[2].level == 3

    def test_extract_sections_empty_body(self) -> None:
        """空の本文は空リストを返す."""
        sections = extract_sections("")

        assert sections == []

    def test_extract_sections_no_headers(self) -> None:
        """見出しがない場合は空リストを返す."""
        body = "これは見出しのない\n普通のテキストです。"

        sections = extract_sections(body)

        assert sections == []

    def test_section_has_line_numbers(self) -> None:
        """セクションに行番号情報が含まれる."""
        body = """# タイトル

内容
"""
        sections = extract_sections(body)

        assert sections[0].start_line >= 0
        assert sections[0].end_line >= sections[0].start_line


class TestSection:
    """Section dataclass のテスト."""

    def test_section_creation(self) -> None:
        """Section を正しく作成できる."""
        section = Section(
            title="テストタイトル",
            level=2,
            content="テスト内容",
            start_line=0,
            end_line=3,
        )

        assert section.title == "テストタイトル"
        assert section.level == 2
        assert section.content == "テスト内容"
        assert section.start_line == 0
        assert section.end_line == 3
