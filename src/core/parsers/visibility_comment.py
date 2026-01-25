"""Visibility comment parser.

Markdown 内の <!-- ai_visibility: N --> コメントをパースする。
仕様: docs/specs/novel-generator-v2/04_ai-information-control.md Section 3.2
"""

import re
from dataclasses import dataclass

from src.core.models.ai_visibility import AIVisibilityLevel

# <!-- ai_visibility: N --> パターン（空白許容）
VISIBILITY_COMMENT_PATTERN = re.compile(
    r"<!--\s*ai_visibility:\s*(\S+)\s*-->",
    re.IGNORECASE,
)

# Markdown セクションヘッダーパターン
SECTION_HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


@dataclass
class VisibilityMarker:
    """可視性マーカー.

    Attributes:
        level: AI可視性レベル
        line_number: コメントの行番号（1-indexed）
        section_name: 関連するセクション名（オプション）
    """

    level: AIVisibilityLevel
    line_number: int
    section_name: str | None = None


def parse_visibility_comments(content: str) -> list[VisibilityMarker]:
    """コンテンツ内の可視性コメントをパースする.

    Args:
        content: パース対象のMarkdownコンテンツ

    Returns:
        検出された可視性マーカーのリスト

    Raises:
        ValueError: 無効な可視性レベルが指定された場合
    """
    markers: list[VisibilityMarker] = []
    lines = content.split("\n")

    for i, line in enumerate(lines):
        match = VISIBILITY_COMMENT_PATTERN.search(line)
        if match:
            level_str = match.group(1)
            level = _parse_level(level_str, i + 1)
            markers.append(
                VisibilityMarker(
                    level=level,
                    line_number=i + 1,  # 1-indexed
                )
            )

    return markers


def _parse_level(level_str: str, line_number: int) -> AIVisibilityLevel:
    """レベル文字列をパースする.

    Args:
        level_str: レベルを表す文字列
        line_number: エラーメッセージ用の行番号

    Returns:
        AIVisibilityLevel

    Raises:
        ValueError: 無効なレベルの場合
    """
    try:
        level_int = int(level_str)
    except ValueError as err:
        raise ValueError(
            f"Invalid visibility level '{level_str}' at line {line_number}. "
            f"Expected 0-3."
        ) from err

    if level_int < 0 or level_int > 3:
        raise ValueError(
            f"Invalid visibility level {level_int} at line {line_number}. "
            f"Expected 0-3."
        )

    return AIVisibilityLevel(level_int)


def extract_section_visibility(
    content: str,
    default_level: AIVisibilityLevel = AIVisibilityLevel.USE,
) -> dict[str, AIVisibilityLevel]:
    """各セクションの可視性レベルを抽出する.

    可視性コメントは、直前のセクションに適用される。
    コメントがないセクションにはデフォルトレベルが適用される。

    Args:
        content: Markdownコンテンツ
        default_level: デフォルトの可視性レベル

    Returns:
        セクション名 → 可視性レベルの辞書
    """
    sections: dict[str, AIVisibilityLevel] = {}
    lines = content.split("\n")

    current_section: str | None = None

    for i, line in enumerate(lines):
        # セクションヘッダーを検出
        header_match = SECTION_HEADER_PATTERN.match(line)
        if header_match:
            section_name = header_match.group(2).strip()
            current_section = section_name
            # デフォルトレベルを設定（後で上書きされる可能性あり）
            sections[section_name] = default_level
            continue

        # 可視性コメントを検出
        visibility_match = VISIBILITY_COMMENT_PATTERN.search(line)
        if visibility_match and current_section:
            level_str = visibility_match.group(1)
            try:
                level = _parse_level(level_str, i + 1)
                sections[current_section] = level
            except ValueError:
                # パースエラーの場合はデフォルトを維持
                pass

    return sections
