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


class RecursionLimitError(Exception):
    """再帰深度制限を超えた場合の例外."""

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


def _validate_depth(data: Any, current_depth: int, max_depth: int) -> None:
    """データ構造の深度を検証する.

    Args:
        data: 検証対象データ
        current_depth: 現在の深度
        max_depth: 最大深度

    Raises:
        RecursionLimitError: 深度制限を超えた場合
    """
    if current_depth > max_depth:
        raise RecursionLimitError(
            f"YAML構造の深度制限（{max_depth}）を超えました。"
            f"循環参照の可能性があります。"
        )

    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, (dict, list)):
                _validate_depth(value, current_depth + 1, max_depth)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                _validate_depth(item, current_depth + 1, max_depth)


def parse_with_depth_limit(content: str, max_depth: int = 10) -> tuple[dict[str, Any], str]:
    """深度制限付きで frontmatter をパースする.

    仕様書 03_data-model.md Section 7.1 に基づく実装。
    YAML 構造の深いネストによる循環参照を防止する。

    Args:
        content: Markdown ファイルの内容
        max_depth: YAML構造の最大深度（デフォルト: 10）

    Returns:
        (frontmatter辞書, 本文) のタプル

    Raises:
        ParseError: YAML の解析に失敗した場合
        RecursionLimitError: 深度制限を超えた場合
    """
    frontmatter_dict, body = parse_frontmatter(content)

    # 深度検証
    _validate_depth(frontmatter_dict, current_depth=0, max_depth=max_depth)

    return frontmatter_dict, body
