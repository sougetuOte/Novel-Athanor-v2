"""Visibility controller.

セクション単位の可視性判定とフィルタリング機能。
仕様: docs/specs/novel-generator-v2/04_ai-information-control.md Section 4
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.core.models.ai_visibility import (
    AIVisibilityLevel,
    SectionVisibility,
    VisibilityConfig,
)
from src.core.parsers.visibility_comment import (
    SECTION_HEADER_PATTERN,
    VISIBILITY_COMMENT_PATTERN,
    extract_section_visibility,
)


def generate_level1_template(
    section_name: str,
    hints: list[str] | None = None,
) -> str:
    """Generate Level 1 (AWARE) avoidance template.

    Uses positive framing instead of "don't mention X" to avoid Pink Elephant Paradox.

    Args:
        section_name: セクション名
        hints: 追加のヒント（オプション）

    Returns:
        Level 1用のプロンプト指示文（ポジティブフレーミング）

    Example:
        >>> generate_level1_template("隠し設定")
        '隠し設定に関する一部の情報は、現在のコンテキストには含まれていません。...'
    """
    base_template = (
        f"{section_name}に関する一部の情報は、現在のコンテキストには含まれていません。\n"
        "提示された情報のみに基づいて描写してください。"
    )

    if hints:
        hints_text = "\n".join(f"- {hint}" for hint in hints)
        return f"{base_template}\n\n参考情報:\n{hints_text}"

    return base_template


def generate_level2_template(
    section_name: str,
    allowed_expressions: list[str] | None = None,
    forbidden_keywords: list[str] | None = None,
) -> str:
    """Generate Level 2 (KNOW) template.

    Returns instructions for AI on how to handle known-but-restricted content.
    Uses positive framing with allowed expressions.

    Args:
        section_name: セクション名
        allowed_expressions: AIが使用可能な暗示表現リスト
        forbidden_keywords: 禁止キーワードリスト

    Returns:
        Level 2用のプロンプト指示文

    Example:
        >>> generate_level2_template("秘密設定", ["高貴な雰囲気"], ["王族"])
        '【秘密設定: 執筆参考情報（文章への直接使用禁止）】...'
    """
    template_parts = [
        f"【{section_name}: 執筆参考情報（文章への直接使用禁止）】",
        "以下の情報は物語の暗示や緊張感の構築に活用できますが、",
        "明示的に述べることは禁止されています。",
    ]

    if allowed_expressions:
        expr_list = "\n".join(f"  - {expr}" for expr in allowed_expressions)
        template_parts.append(f"\n許可される表現パターン:\n{expr_list}")

    if forbidden_keywords:
        keywords_text = "、".join(forbidden_keywords)
        template_parts.append(f"\n使用禁止キーワード: {keywords_text}")

    return "\n".join(template_parts)


@dataclass
class VisibilityFilteredContent:
    """L2 フィルタ済みコンテンツ (旧 FilteredContext).

    Attributes:
        content: フィルタ済みコンテンツ
        hints: Level 1/2 用のヒント（「〜に秘密があります」等）
        forbidden_keywords: 禁止キーワードリスト
        excluded_sections: 除外されたセクション名リスト

    Note:
        L3 の FilteredContext (src.core.context.filtered_context) とは異なるクラス。
        このクラスは L2 の可視性フィルタリング結果を保持する。
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
        default_level: AIVisibilityLevel = AIVisibilityLevel.HIDDEN,
        forbidden_keywords: list[str] | None = None,
        config: VisibilityConfig | None = None,
    ) -> None:
        """初期化.

        Args:
            default_level: デフォルトの可視性レベル
            forbidden_keywords: グローバル禁止キーワードリスト
            config: 可視性設定（指定時は設定から禁止キーワードを収集）
        """
        self.default_level = default_level
        self.config = config
        # Collect forbidden keywords from config if provided
        if config:
            config_keywords = config.collect_forbidden_keywords()
            self.forbidden_keywords = list(set((forbidden_keywords or []) + config_keywords))
        else:
            self.forbidden_keywords = forbidden_keywords or []
        self._global_hints: list[str] = []

    def add_hint(self, hint: str) -> None:
        """グローバルヒントを追加する.

        Args:
            hint: ヒントメッセージ
        """
        self._global_hints.append(hint)

    def filter(self, content: str) -> VisibilityFilteredContent:
        """コンテンツをフィルタリングする.

        Args:
            content: フィルタ対象のMarkdownコンテンツ

        Returns:
            フィルタ済みコンテンツ
        """
        return filter_content_by_visibility(
            content,
            default_level=self.default_level,
            forbidden_keywords=self.forbidden_keywords,
            global_hints=self._global_hints,
        )


def filter_content_by_visibility(
    content: str,
    default_level: AIVisibilityLevel = AIVisibilityLevel.HIDDEN,
    forbidden_keywords: list[str] | None = None,
    global_hints: list[str] | None = None,
    section_configs: dict[str, SectionVisibility] | None = None,
) -> VisibilityFilteredContent:
    """可視性レベルに基づいてコンテンツをフィルタリングする.

    Args:
        content: フィルタ対象のMarkdownコンテンツ
        default_level: デフォルトの可視性レベル
        forbidden_keywords: 禁止キーワードリスト
        global_hints: グローバルヒントリスト
        section_configs: セクション別の詳細設定（forbidden_keywords, allowed_expressions含む）

    Returns:
        フィルタ済みコンテンツ
    """
    forbidden_keywords = forbidden_keywords or []
    hints = list(global_hints) if global_hints else []
    excluded_sections: list[str] = []
    section_configs = section_configs or {}

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
                # Level 1: ヒントのみ（ポジティブフレーミング）
                skip_until_next_section = True
                # Use template for positive framing
                level1_hint = generate_level1_template(section_name)
                hints.append(level1_hint)
                continue
            elif current_level == AIVisibilityLevel.KNOW:
                # Level 2: コンテンツを含めるが制限付き
                skip_until_next_section = False
                filtered_lines.append(line)
                # セクションの制限情報を追加
                section_config = section_configs.get(section_name)
                if section_config:
                    # 禁止キーワードを追加
                    if section_config.forbidden_keywords:
                        forbidden_keywords.extend(section_config.forbidden_keywords)
                    # Use template for Level 2 instructions
                    level2_hint = generate_level2_template(
                        section_name,
                        allowed_expressions=section_config.allowed_expressions,
                        forbidden_keywords=section_config.forbidden_keywords,
                    )
                    hints.append(level2_hint)
                else:
                    # section_configがない場合もテンプレートを使用
                    level2_hint = generate_level2_template(section_name)
                    hints.append(level2_hint)
                continue
            else:
                # Level 3 (USE): コンテンツを含める（制限なし）
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

    # 禁止キーワードを収集（重複削除）
    result_forbidden = list(set(forbidden_keywords))

    return VisibilityFilteredContent(
        content="\n".join(filtered_lines),
        hints=hints,
        forbidden_keywords=result_forbidden,
        excluded_sections=excluded_sections,
    )
