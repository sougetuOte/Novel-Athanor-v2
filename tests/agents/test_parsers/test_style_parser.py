"""Tests for style_parser.py.

Tests the parsing of LLM output containing StyleGuide and StyleProfile
YAML blocks into structured Pydantic models.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.agents.parsers.style_parser import (
    parse_style_guide_output,
    parse_style_profile_output,
)
from src.core.models.style import (
    POVType,
    StyleGuide,
    StyleProfile,
    TenseType,
)


class TestParseStyleGuideOutput:
    """Tests for parse_style_guide_output()."""

    def test_parse_complete_style_guide(self) -> None:
        """Parse a complete StyleGuide YAML with all fields."""
        text = """
Here is the style guide analysis:

```yaml
work: "Sample Novel"
pov: third_person_limited
tense: past
style_characteristics:
  - "簡潔な文体"
  - "内省的な語り"
dialogue:
  quote_style: "「」"
  inner_thought_style: "（）"
  speaker_attribution: "after"
description_tendencies:
  - "五感を活用した描写"
  - "比喩の多用"
avoid_expressions:
  - "〜のような"
  - "とても"
notes: "追加メモ"
```

Analysis complete.
"""
        result = parse_style_guide_output(text)

        assert isinstance(result, StyleGuide)
        assert result.work == "Sample Novel"
        assert result.pov == POVType.THIRD_PERSON_LIMITED
        assert result.tense == TenseType.PAST
        assert result.style_characteristics == ["簡潔な文体", "内省的な語り"]
        assert result.dialogue is not None
        assert result.dialogue.quote_style == "「」"
        assert result.dialogue.inner_thought_style == "（）"
        assert result.dialogue.speaker_attribution == "after"
        assert result.description_tendencies == ["五感を活用した描写", "比喩の多用"]
        assert result.avoid_expressions == ["〜のような", "とても"]
        assert result.notes == "追加メモ"

    def test_parse_minimal_style_guide(self) -> None:
        """Parse a minimal StyleGuide YAML with only required fields."""
        text = """
```yaml
work: "Minimal Work"
pov: first_person
tense: present
```
"""
        result = parse_style_guide_output(text)

        assert result.work == "Minimal Work"
        assert result.pov == POVType.FIRST_PERSON
        assert result.tense == TenseType.PRESENT
        assert result.style_characteristics == []
        assert result.dialogue is None
        assert result.description_tendencies == []
        assert result.avoid_expressions == []
        assert result.notes is None

    def test_parse_with_dialogue_field(self) -> None:
        """Parse StyleGuide with dialogue field present."""
        text = """
```yaml
work: "Dialogue Test"
pov: third_person
tense: past
dialogue:
  quote_style: "『』"
  inner_thought_style: null
```
"""
        result = parse_style_guide_output(text)

        assert result.dialogue is not None
        assert result.dialogue.quote_style == "『』"
        assert result.dialogue.inner_thought_style is None

    def test_no_yaml_block_raises_error(self) -> None:
        """Raise ValueError if no YAML block is found."""
        text = "Just some plain text without YAML."

        with pytest.raises(ValueError, match="No YAML code block found"):
            parse_style_guide_output(text)

    def test_invalid_pov_raises_error(self) -> None:
        """Raise ValueError if pov field has an invalid value."""
        text = """
```yaml
work: "Invalid POV"
pov: second_person
tense: past
```
"""
        with pytest.raises(ValueError):
            parse_style_guide_output(text)

    def test_missing_required_field_raises_error(self) -> None:
        """Raise ValueError if required field 'work' is missing."""
        text = """
```yaml
pov: first_person
tense: past
```
"""
        with pytest.raises(ValueError):
            parse_style_guide_output(text)


class TestParseStyleProfileOutput:
    """Tests for parse_style_profile_output()."""

    def test_parse_complete_style_profile(self) -> None:
        """Parse a complete StyleProfile YAML with all fields."""
        text = """
Analysis result:

```yaml
work: "Sample Novel"
avg_sentence_length: 25.3
dialogue_ratio: 0.35
ttr: 0.45
pos_ratios:
  noun: 0.30
  verb: 0.20
  adjective: 0.15
frequent_words:
  - "彼"
  - "言う"
  - "思う"
sample_episodes:
  - 1
  - 2
  - 3
analyzed_at: 2026-02-06
```

Done.
"""
        result = parse_style_profile_output(text)

        assert isinstance(result, StyleProfile)
        assert result.work == "Sample Novel"
        assert result.avg_sentence_length == 25.3
        assert result.dialogue_ratio == 0.35
        assert result.ttr == 0.45
        assert result.pos_ratios == {"noun": 0.30, "verb": 0.20, "adjective": 0.15}
        assert result.frequent_words == ["彼", "言う", "思う"]
        assert result.sample_episodes == [1, 2, 3]
        assert result.analyzed_at == date(2026, 2, 6)

    def test_parse_minimal_style_profile(self) -> None:
        """Parse a minimal StyleProfile YAML with only required fields."""
        text = """
```yaml
work: "Minimal Profile"
```
"""
        result = parse_style_profile_output(text)

        assert result.work == "Minimal Profile"
        assert result.avg_sentence_length is None
        assert result.dialogue_ratio is None
        assert result.ttr is None
        assert result.pos_ratios == {}
        assert result.frequent_words == []
        assert result.sample_episodes == []
        assert result.analyzed_at is None

    def test_no_yaml_block_raises_error(self) -> None:
        """Raise ValueError if no YAML block is found."""
        text = "No code block here."

        with pytest.raises(ValueError, match="No YAML code block found"):
            parse_style_profile_output(text)

    def test_missing_work_field_raises_error(self) -> None:
        """Raise ValueError if required field 'work' is missing."""
        text = """
```yaml
avg_sentence_length: 20.0
ttr: 0.4
```
"""
        with pytest.raises(ValueError):
            parse_style_profile_output(text)
