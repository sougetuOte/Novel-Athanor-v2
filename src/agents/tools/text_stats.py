"""Text statistics utility for Style Agent.

Provides purely algorithmic (no LLM) text analysis functions:
- Average sentence length
- Dialogue ratio
- Type-Token Ratio (TTR)
- Frequent words

These are used to populate StyleProfile quantitative fields.
"""

from __future__ import annotations

import re
from collections import Counter

# Sentence delimiters for Japanese text
_SENTENCE_DELIMITERS = re.compile(r"[。！？!?]+")

# Default dialogue bracket pairs
_DEFAULT_BRACKETS = ["「」", "『』"]


def avg_sentence_length(text: str) -> float:
    """Calculate average sentence length in characters.

    Splits text by sentence-ending punctuation (。！？!?) and returns
    the mean character count per sentence.

    Args:
        text: Input text.

    Returns:
        Average characters per sentence. 0.0 for empty text.
    """
    text = text.strip()
    if not text:
        return 0.0

    parts = _SENTENCE_DELIMITERS.split(text)
    sentences = [s.strip() for s in parts if s.strip()]

    if not sentences:
        return 0.0

    return sum(len(s) for s in sentences) / len(sentences)


def dialogue_ratio(
    text: str, brackets: list[str] | None = None
) -> float:
    """Calculate the ratio of dialogue characters to total characters.

    Counts characters inside bracket pairs (default: 「」『』) relative
    to the total text length.

    Args:
        text: Input text.
        brackets: List of bracket pair strings (e.g. ["「」", "（）"]).

    Returns:
        Ratio 0.0-1.0. 0.0 for empty text.
    """
    text = text.strip()
    if not text:
        return 0.0

    if brackets is None:
        brackets = _DEFAULT_BRACKETS

    dialogue_chars = 0
    for pair in brackets:
        open_br, close_br = pair[0], pair[1]
        pattern = re.compile(re.escape(open_br) + r"(.*?)" + re.escape(close_br))
        for m in pattern.finditer(text):
            dialogue_chars += len(m.group(1))

    total = len(text)
    if total == 0:
        return 0.0

    return dialogue_chars / total


def ttr(text: str) -> float:
    """Calculate Type-Token Ratio.

    For text with spaces, splits by whitespace. For text without spaces
    (Japanese), splits by character.

    Args:
        text: Input text.

    Returns:
        TTR value 0.0-1.0. 0.0 for empty text.
    """
    text = text.strip()
    if not text:
        return 0.0

    if " " in text:
        tokens = text.split()
    else:
        tokens = list(text)

    if not tokens:
        return 0.0

    types = set(tokens)
    return len(types) / len(tokens)


def frequent_words(text: str, top_n: int = 20) -> list[str]:
    """Extract most frequent words/characters.

    For text with spaces, splits by whitespace. For text without spaces
    (Japanese), splits by character.

    Args:
        text: Input text.
        top_n: Number of top items to return.

    Returns:
        List of most frequent tokens, ordered by frequency.
    """
    text = text.strip()
    if not text:
        return []

    if " " in text:
        tokens = text.split()
    else:
        tokens = list(text)

    counter = Counter(tokens)
    return [word for word, _ in counter.most_common(top_n)]


def compute_text_stats(text: str) -> dict[str, object]:
    """Compute all text statistics at once.

    Args:
        text: Input text.

    Returns:
        Dictionary with keys: avg_sentence_length, dialogue_ratio, ttr,
        frequent_words.
    """
    return {
        "avg_sentence_length": avg_sentence_length(text),
        "dialogue_ratio": dialogue_ratio(text),
        "ttr": ttr(text),
        "frequent_words": frequent_words(text),
    }
