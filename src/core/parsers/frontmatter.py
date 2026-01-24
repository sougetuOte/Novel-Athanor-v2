"""YAML frontmatter parser.

Markdown ファイルの YAML frontmatter を解析するパーサー。
"""

from typing import Any

import frontmatter
import yaml


class ParseError(Exception):
    """frontmatter の解析に失敗した場合の例外."""

    pass


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
