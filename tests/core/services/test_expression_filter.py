"""Tests for expression filter.

禁止キーワードマッチャーのテスト。
"""


from src.core.services.expression_filter import (
    KeywordViolation,
    check_forbidden_keywords,
    check_text_safety,
)


class TestCheckForbiddenKeywords:
    """check_forbidden_keywords 関数のテスト."""

    def test_detect_single_keyword(self) -> None:
        """単一のキーワードを検出できる."""
        text = "彼女は王族の血筋だった。"
        forbidden = ["王族"]

        violations = check_forbidden_keywords(text, forbidden)

        assert len(violations) == 1
        assert violations[0].keyword == "王族"
        assert 3 in violations[0].positions

    def test_detect_multiple_keywords(self) -> None:
        """複数のキーワードを検出できる."""
        text = "王族の血筋を持つ高貴な存在。"
        forbidden = ["王族", "血筋", "高貴"]

        violations = check_forbidden_keywords(text, forbidden)

        assert len(violations) == 3
        keywords = {v.keyword for v in violations}
        assert keywords == {"王族", "血筋", "高貴"}

    def test_detect_multiple_occurrences(self) -> None:
        """同じキーワードの複数出現を検出できる."""
        text = "王族は王族らしく、王族として振る舞う。"
        forbidden = ["王族"]

        violations = check_forbidden_keywords(text, forbidden)

        assert len(violations) == 1
        assert len(violations[0].positions) == 3

    def test_no_violations(self) -> None:
        """違反がない場合は空リストを返す."""
        text = "彼女は普通の村娘だった。"
        forbidden = ["王族", "血筋"]

        violations = check_forbidden_keywords(text, forbidden)

        assert violations == []

    def test_empty_forbidden_list(self) -> None:
        """禁止リストが空の場合は空リストを返す."""
        text = "何でも書いてよい。"
        forbidden: list[str] = []

        violations = check_forbidden_keywords(text, forbidden)

        assert violations == []

    def test_case_sensitive(self) -> None:
        """大文字小文字を区別する."""
        text = "The KING is here."
        forbidden = ["king"]

        violations = check_forbidden_keywords(text, forbidden)

        assert violations == []

    def test_context_extraction(self) -> None:
        """違反箇所の前後コンテキストを抽出できる."""
        text = "長い文章の中で王族という単語が出てくる。"
        forbidden = ["王族"]

        violations = check_forbidden_keywords(text, forbidden)

        assert len(violations) == 1
        assert "王族" in violations[0].context
        # コンテキストには前後の文字が含まれる
        assert len(violations[0].context) > len("王族")

    def test_none_text_returns_empty(self) -> None:
        """None のテキストは空リストを返す."""
        violations = check_forbidden_keywords(None, ["王族"])  # type: ignore
        assert violations == []


class TestCheckTextSafety:
    """check_text_safety 関数のテスト."""

    def test_safe_text(self) -> None:
        """安全なテキストを判定できる."""
        text = "彼女は村で育った。"
        forbidden = ["王族", "魔王"]

        result = check_text_safety(text, forbidden)

        assert result.is_safe is True
        assert result.violations == []

    def test_unsafe_text(self) -> None:
        """危険なテキストを判定できる."""
        text = "彼女は実は王族だった。"
        forbidden = ["王族"]

        result = check_text_safety(text, forbidden)

        assert result.is_safe is False
        assert len(result.violations) == 1

    def test_summary_message(self) -> None:
        """サマリーメッセージを生成できる."""
        text = "王族の血筋。"
        forbidden = ["王族", "血筋"]

        result = check_text_safety(text, forbidden)

        assert "2" in result.summary  # 2件の違反
        assert "王族" in result.summary or "血筋" in result.summary


class TestKeywordViolation:
    """KeywordViolation データクラスのテスト."""

    def test_create_violation(self) -> None:
        """違反オブジェクトを作成できる."""
        violation = KeywordViolation(
            keyword="王族",
            positions=[5, 20],
            context="...は王族の...",
        )

        assert violation.keyword == "王族"
        assert violation.positions == [5, 20]
        assert violation.context == "...は王族の..."

    def test_violation_str(self) -> None:
        """文字列表現を取得できる."""
        violation = KeywordViolation(
            keyword="王族",
            positions=[5],
            context="王族",
        )

        str_repr = str(violation)
        assert "王族" in str_repr
