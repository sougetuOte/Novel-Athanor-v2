"""Markdown body extractor.

Markdown ファイルから本文を抽出し、セクション単位で分割する。
"""

import re
from dataclasses import dataclass

from src.core.parsers.frontmatter import parse_frontmatter


@dataclass
class Section:
    """Markdown セクションを表すデータクラス."""

    title: str
    level: int  # 1-6
    content: str
    start_line: int
    end_line: int


def extract_body(content: str) -> str:
    """Markdown コンテンツから本文（frontmatter 以降）を抽出する.

    Args:
        content: Markdown ファイルの内容

    Returns:
        frontmatter を除いた本文
    """
    _, body = parse_frontmatter(content)
    return body


def extract_sections(body: str) -> list[Section]:
    """Markdown 本文をセクション単位で分割する.

    Args:
        body: frontmatter を除いた Markdown 本文

    Returns:
        Section のリスト
    """
    if not body.strip():
        return []

    # 見出しパターン: # から始まる行
    header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    matches = list(header_pattern.finditer(body))

    if not matches:
        return []

    sections: list[Section] = []

    for i, match in enumerate(matches):
        level = len(match.group(1))
        title = match.group(2).strip()

        # 開始行を計算
        start_pos = match.start()
        start_line = body[:start_pos].count("\n")

        # 終了位置を決定
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(body)

        # セクションの内容を抽出（見出し行を除く）
        content_start = match.end()
        content = body[content_start:end_pos].strip()

        # 終了行を計算
        end_line = body[:end_pos].count("\n")

        sections.append(
            Section(
                title=title,
                level=level,
                content=content,
                start_line=start_line,
                end_line=end_line,
            )
        )

    return sections
