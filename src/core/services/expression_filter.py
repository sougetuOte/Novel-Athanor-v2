"""Expression filter.

禁止キーワードの検出とテキスト安全性チェック。
仕様: docs/specs/novel-generator-v2/04_ai-information-control.md Section 5
"""

from dataclasses import dataclass, field


@dataclass
class KeywordViolation:
    """キーワード違反.

    Attributes:
        keyword: 検出された禁止キーワード
        positions: キーワードが出現した位置（0-indexed）のリスト
        context: キーワード周辺のコンテキスト（前後20文字程度）
    """

    keyword: str
    positions: list[int] = field(default_factory=list)
    context: str = ""

    def __str__(self) -> str:
        """文字列表現."""
        pos_str = ", ".join(str(p) for p in self.positions)
        return f"KeywordViolation('{self.keyword}' at positions [{pos_str}])"


@dataclass
class SafetyCheckResult:
    """安全性チェック結果.

    Attributes:
        is_safe: 安全かどうか
        violations: 検出された違反のリスト
        summary: サマリーメッセージ
    """

    is_safe: bool
    violations: list[KeywordViolation] = field(default_factory=list)
    summary: str = ""


def check_forbidden_keywords(
    text: str,
    forbidden_keywords: list[str],
    context_chars: int = 20,
) -> list[KeywordViolation]:
    """テキスト内の禁止キーワードをチェックする.

    Args:
        text: チェック対象のテキスト
        forbidden_keywords: 禁止キーワードのリスト
        context_chars: コンテキストとして抽出する前後の文字数

    Returns:
        検出された違反のリスト
    """
    if text is None:
        return []

    violations: list[KeywordViolation] = []

    for keyword in forbidden_keywords:
        if not keyword:
            continue

        positions = _find_all_positions(text, keyword)
        if positions:
            context = _extract_context(text, positions[0], keyword, context_chars)
            violations.append(
                KeywordViolation(
                    keyword=keyword,
                    positions=positions,
                    context=context,
                )
            )

    return violations


def _find_all_positions(text: str, keyword: str) -> list[int]:
    """テキスト内のキーワード出現位置を全て検索する.

    Args:
        text: 検索対象テキスト
        keyword: 検索キーワード

    Returns:
        出現位置（0-indexed）のリスト
    """
    positions: list[int] = []
    start = 0

    while True:
        pos = text.find(keyword, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1

    return positions


def _extract_context(
    text: str,
    position: int,
    keyword: str,
    context_chars: int,
) -> str:
    """キーワード周辺のコンテキストを抽出する.

    Args:
        text: 元テキスト
        position: キーワードの位置
        keyword: キーワード
        context_chars: 前後に抽出する文字数

    Returns:
        コンテキスト文字列（前後に ... を付加）
    """
    start = max(0, position - context_chars)
    end = min(len(text), position + len(keyword) + context_chars)

    context = text[start:end]

    # 前後に省略記号を追加
    if start > 0:
        context = "..." + context
    if end < len(text):
        context = context + "..."

    return context


def check_text_safety(
    text: str,
    forbidden_keywords: list[str],
) -> SafetyCheckResult:
    """テキストの安全性をチェックする.

    Args:
        text: チェック対象テキスト
        forbidden_keywords: 禁止キーワードリスト

    Returns:
        安全性チェック結果
    """
    violations = check_forbidden_keywords(text, forbidden_keywords)

    if not violations:
        return SafetyCheckResult(
            is_safe=True,
            violations=[],
            summary="No violations found.",
        )

    # サマリーメッセージを生成
    keyword_list = ", ".join(v.keyword for v in violations)
    summary = f"Found {len(violations)} violation(s): {keyword_list}"

    return SafetyCheckResult(
        is_safe=False,
        violations=violations,
        summary=summary,
    )
