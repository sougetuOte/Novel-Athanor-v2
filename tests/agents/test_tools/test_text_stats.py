"""Tests for text statistics utility."""

from src.agents.tools.text_stats import (
    avg_sentence_length,
    compute_text_stats,
    dialogue_ratio,
    frequent_words,
    ttr,
)

# --- avg_sentence_length ---


class TestAvgSentenceLength:
    """Tests for avg_sentence_length()."""

    def test_basic_sentences(self) -> None:
        """Count characters per sentence."""
        text = "これは文です。もう一つの文です。"
        result = avg_sentence_length(text)
        # "これは文です" = 6 chars, "もう一つの文です" = 8 chars -> avg 7.0
        assert result == 7.0

    def test_mixed_delimiters(self) -> None:
        """Should handle multiple sentence delimiters."""
        text = "質問です？感嘆です！終わり。"
        result = avg_sentence_length(text)
        # "質問です" = 4, "感嘆です" = 4, "終わり" = 3 -> avg ~3.67
        assert abs(result - 3.67) < 0.1

    def test_empty_text(self) -> None:
        """Empty text should return 0."""
        assert avg_sentence_length("") == 0.0

    def test_no_delimiter(self) -> None:
        """Text with no delimiter is treated as one sentence."""
        text = "区切りのないテキスト"
        result = avg_sentence_length(text)
        assert result == 10.0

    def test_trailing_spaces(self) -> None:
        """Should strip whitespace from sentences."""
        text = "  文一。  文二。  "
        result = avg_sentence_length(text)
        assert result == 2.0  # "文一" = 2, "文二" = 2


# --- dialogue_ratio ---


class TestDialogueRatio:
    """Tests for dialogue_ratio()."""

    def test_no_dialogue(self) -> None:
        """Text without dialogue returns 0."""
        text = "地の文だけの文章です。会話はありません。"
        assert dialogue_ratio(text) == 0.0

    def test_all_dialogue(self) -> None:
        """Text that is entirely dialogue returns high ratio."""
        text = "「すべて会話です」"
        # 7 dialogue chars / 9 total chars (brackets excluded from dialogue count)
        result = dialogue_ratio(text)
        assert result > 0.7

    def test_mixed(self) -> None:
        """Mixed text returns ratio between 0 and 1."""
        text = "太郎は言った。「こんにちは」花子は微笑んだ。"
        result = dialogue_ratio(text)
        # "こんにちは" = 5 chars dialogue, total ~22 chars
        assert 0.0 < result < 1.0

    def test_empty_text(self) -> None:
        """Empty text returns 0."""
        assert dialogue_ratio("") == 0.0

    def test_nested_brackets(self) -> None:
        """Should handle multiple dialogue segments."""
        text = "「一つ目」と「二つ目」"
        result = dialogue_ratio(text)
        assert result > 0.5

    def test_custom_brackets(self) -> None:
        """Should handle inner thought brackets."""
        text = "太郎は思った。（本当だろうか）"
        result = dialogue_ratio(text, brackets=["（）"])
        assert result > 0.0


# --- ttr ---


class TestTTR:
    """Tests for Type-Token Ratio."""

    def test_all_unique(self) -> None:
        """All unique words should give TTR = 1.0."""
        # Using space-separated tokens for simplicity
        text = "これ は テスト です"
        result = ttr(text)
        assert result == 1.0

    def test_all_same(self) -> None:
        """All same words should give TTR approaching 1/N."""
        text = "テスト テスト テスト テスト"
        result = ttr(text)
        assert result == 0.25

    def test_empty_text(self) -> None:
        """Empty text returns 0."""
        assert ttr("") == 0.0

    def test_japanese_characters(self) -> None:
        """Should split Japanese text by character when no spaces."""
        text = "ああいい"
        result = ttr(text)
        # Characters: あ, あ, い, い -> 2 types, 4 tokens -> 0.5
        assert result == 0.5


# --- frequent_words ---


class TestFrequentWords:
    """Tests for frequent_words()."""

    def test_basic_frequency(self) -> None:
        """Should return words sorted by frequency."""
        text = "犬 猫 犬 犬 猫 鳥"
        result = frequent_words(text, top_n=3)
        assert result[0] == "犬"
        assert result[1] == "猫"

    def test_top_n_limit(self) -> None:
        """Should respect top_n limit."""
        text = "a b c d e f g"
        result = frequent_words(text, top_n=3)
        assert len(result) == 3

    def test_empty_text(self) -> None:
        """Empty text returns empty list."""
        assert frequent_words("", top_n=5) == []

    def test_japanese_characters(self) -> None:
        """Should work with character-level tokenization for Japanese."""
        text = "ああいいああ"
        result = frequent_words(text, top_n=2)
        assert "あ" in result


# --- compute_text_stats ---


class TestComputeTextStats:
    """Tests for compute_text_stats() aggregate function."""

    def test_returns_dict(self) -> None:
        """Should return a dict with all stats."""
        text = "太郎は言った。「こんにちは」"
        result = compute_text_stats(text)

        assert "avg_sentence_length" in result
        assert "dialogue_ratio" in result
        assert "ttr" in result
        assert "frequent_words" in result

    def test_values_are_reasonable(self) -> None:
        """All values should be in expected ranges."""
        text = "これはテストです。もう一文。「会話です」"
        result = compute_text_stats(text)

        assert result["avg_sentence_length"] > 0
        assert 0.0 <= result["dialogue_ratio"] <= 1.0
        assert 0.0 <= result["ttr"] <= 1.0
        assert isinstance(result["frequent_words"], list)
