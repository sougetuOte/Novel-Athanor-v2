"""YAML frontmatter parser.

Markdown ファイルの YAML frontmatter を解析するパーサー。
"""

from dataclasses import dataclass
from typing import Any

import frontmatter
import yaml


class ParseError(Exception):
    """frontmatter の解析に失敗した場合の例外."""

    pass


@dataclass
class ParseResult:
    """パース結果を表すデータクラス.

    Attributes:
        result_type: "structured" (正常パース) または "raw_text" (フォールバック)
        frontmatter: パースされた frontmatter 辞書 (structured の場合)
        body: パースされた本文 (structured の場合)
        raw_content: 生のコンテンツ (raw_text の場合)
        error: エラーメッセージ (raw_text の場合)
    """

    result_type: str  # "structured" | "raw_text"
    frontmatter: dict[str, Any] | None = None
    body: str | None = None
    raw_content: str | None = None
    error: str | None = None


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Markdown コンテンツから frontmatter と本文を抽出する.

    Args:
        content: Markdown ファイルの内容

    Returns:
        (frontmatter辞書, 本文) のタプル

    Raises:
        ParseError: YAML の解析に失敗した場合
    """
    try:
        post = frontmatter.loads(content)
        return dict(post.metadata), post.content
    except yaml.YAMLError as e:
        raise ParseError(f"Invalid YAML in frontmatter: {e}") from e


def parse_frontmatter_with_fallback(content: str) -> ParseResult:
    """パース失敗時に生テキストでフォールバックする.

    仕様書 03_data-model.md Section 7.2 に基づく実装。
    パースに失敗した場合でも、生のテキストとしてコンテキストに含められるよう
    フォールバック処理を行う。

    Args:
        content: Markdown ファイルの内容

    Returns:
        ParseResult: パース結果（structured または raw_text）
    """
    try:
        fm, body = parse_frontmatter(content)
        return ParseResult(
            result_type="structured",
            frontmatter=fm,
            body=body,
        )
    except ParseError as e:
        return ParseResult(
            result_type="raw_text",
            raw_content=content,
            error=str(e),
        )
