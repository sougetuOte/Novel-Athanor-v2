"""Visibility controller.

セクション単位の可視性判定とフィルタリング機能。
仕様: docs/specs/novel-generator-v2/04_ai-information-control.md Section 4
"""

from dataclasses import dataclass, field

from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.parsers.visibility_comment import (
    SECTION_HEADER_PATTERN,
    VISIBILITY_COMMENT_PATTERN,
    extract_section_visibility,
)


@dataclass
class FilteredContext:
    """フィルタ済みコンテキスト.

    Attributes:
        content: フィルタ済みコンテンツ
        hints: Level 1/2 用のヒント（「〜に秘密があります」等）
        forbidden_keywords: 禁止キーワードリスト
        excluded_sections: 除外されたセクション名リスト
    """

    content: str
    hints: list[str] = field(default_factory=list)
    forbidden_keywords: list[str] = field(default_factory=list)
    excluded_sections: list[str] = field(default_factory=list)

    @property
    def has_restrictions(self) -> bool:
        """制限があるかどうか."""
        return bool(
            self.hints or self.forbidden_keywords or self.excluded_sections
        )

    def get_summary(self) -> str:
        """サマリーを取得する."""
        parts = []
        if self.excluded_sections:
            parts.append(f"Excluded: {len(self.excluded_sections)} section(s)")
        if self.forbidden_keywords:
            parts.append(f"Forbidden: {len(self.forbidden_keywords)} keyword(s)")
        if self.hints:
            parts.append(f"Hints: {len(self.hints)}")
        return ", ".join(parts) if parts else "No restrictions"


class VisibilityController:
    """可視性コントローラ.

    コンテンツの可視性をレベルに基づいてフィルタリングする。
    """

    def __init__(
        self,
        default_level: AIVisibilityLevel = AIVisibilityLevel.USE,
        forbidden_keywords: list[str] | None = None,
    ) -> None:
        """初期化.

        Args:
            default_level: デフォルトの可視性レベル
            forbidden_keywords: グローバル禁止キーワードリスト
        """
        self.default_level = default_level
        self.forbidden_keywords = forbidden_keywords or []
        self._global_hints: list[str] = []

    def add_hint(self, hint: str) -> None:
        """グローバルヒントを追加する.

        Args:
            hint: ヒントメッセージ
        """
        self._global_hints.append(hint)

    def filter(self, content: str) -> FilteredContext:
        """コンテンツをフィルタリングする.

        Args:
            content: フィルタ対象のMarkdownコンテンツ

        Returns:
            フィルタ済みコンテキスト
        """
        return filter_content_by_visibility(
            content,
            default_level=self.default_level,
            forbidden_keywords=self.forbidden_keywords,
            global_hints=self._global_hints,
        )


def filter_content_by_visibility(
    content: str,
    default_level: AIVisibilityLevel = AIVisibilityLevel.USE,
    forbidden_keywords: list[str] | None = None,
    global_hints: list[str] | None = None,
) -> FilteredContext:
    """可視性レベルに基づいてコンテンツをフィルタリングする.

    Args:
        content: フィルタ対象のMarkdownコンテンツ
        default_level: デフォルトの可視性レベル
        forbidden_keywords: 禁止キーワードリスト
        global_hints: グローバルヒントリスト

    Returns:
        フィルタ済みコンテキスト
    """
    forbidden_keywords = forbidden_keywords or []
    hints = list(global_hints) if global_hints else []
    excluded_sections: list[str] = []

    # セクション別の可視性を取得
    section_visibility = extract_section_visibility(content, default_level)

    # セクションごとにフィルタリング
    filtered_lines: list[str] = []
    lines = content.split("\n")

    current_level = default_level
    skip_until_next_section = False

    for line in lines:
        # セクションヘッダーを検出
        header_match = SECTION_HEADER_PATTERN.match(line)
        if header_match:
            section_name = header_match.group(2).strip()
            current_level = section_visibility.get(section_name, default_level)

            # レベルに応じた処理
            if current_level == AIVisibilityLevel.HIDDEN:
                # Level 0: 完全除外
                skip_until_next_section = True
                excluded_sections.append(section_name)
                continue
            elif current_level == AIVisibilityLevel.AWARE:
                # Level 1: ヒントのみ
                skip_until_next_section = True
                hints.append(f"{section_name}には非公開の情報があります（内容不明）")
                continue
            else:
                # Level 2, 3: コンテンツを含める
                skip_until_next_section = False
                filtered_lines.append(line)
                continue

        # 可視性コメント行はスキップ（出力に含めない）
        if VISIBILITY_COMMENT_PATTERN.search(line):
            continue

        # スキップ中ならスキップ
        if skip_until_next_section:
            continue

        # 通常の行を追加
        filtered_lines.append(line)

    # Level 2 の禁止キーワードを収集
    result_forbidden = list(forbidden_keywords)

    return FilteredContext(
        content="\n".join(filtered_lines),
        hints=hints,
        forbidden_keywords=result_forbidden,
        excluded_sections=excluded_sections,
    )
