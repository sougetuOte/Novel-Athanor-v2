"""Style result parser.

This module parses LLM output text containing YAML blocks into
structured StyleGuide and StyleProfile models.

Expected LLM output format for StyleGuide:
    ```yaml
    work: "作品名"
    pov: third_person_limited | first_person | ...
    tense: past | present
    style_characteristics:
      - "簡潔な文体"
      - "内省的な語り"
    dialogue:
      quote_style: "「」"
      inner_thought_style: "（）"
      speaker_attribution: "after"
    description_tendencies:
      - "五感を活用した描写"
    avoid_expressions:
      - "〜のような"
    notes: "追加メモ"
    ```

Expected LLM output format for StyleProfile:
    ```yaml
    work: "作品名"
    avg_sentence_length: 25.3
    dialogue_ratio: 0.35
    ttr: 0.45
    pos_ratios:
      noun: 0.30
      verb: 0.20
    frequent_words:
      - "彼"
      - "言う"
    sample_episodes:
      - 1
      - 2
    analyzed_at: 2026-02-06
    ```
"""

from __future__ import annotations

import re
from typing import Any

import yaml

from src.core.models.style import DialogueStyle, StyleGuide, StyleProfile


def parse_style_guide_output(text: str) -> StyleGuide:
    """Parse LLM style guide output text into a StyleGuide.

    Extracts the first YAML code block from the text and parses it
    into a structured StyleGuide.

    Args:
        text: Raw LLM output containing a YAML code block.

    Returns:
        Parsed StyleGuide.

    Raises:
        ValueError: If no YAML block is found, YAML is malformed,
                    or required fields are missing/invalid.
    """
    yaml_content = _extract_yaml_block(text)
    data = _parse_yaml(yaml_content)
    return _build_style_guide(data)


def parse_style_profile_output(text: str) -> StyleProfile:
    """Parse LLM style profile output text into a StyleProfile.

    Extracts the first YAML code block from the text and parses it
    into a structured StyleProfile.

    Args:
        text: Raw LLM output containing a YAML code block.

    Returns:
        Parsed StyleProfile.

    Raises:
        ValueError: If no YAML block is found, YAML is malformed,
                    or required fields are missing/invalid.
    """
    yaml_content = _extract_yaml_block(text)
    data = _parse_yaml(yaml_content)
    return _build_style_profile(data)


def _extract_yaml_block(text: str) -> str:
    """Extract YAML content from a fenced code block.

    Args:
        text: Text potentially containing a ```yaml ... ``` block.

    Returns:
        The YAML content string.

    Raises:
        ValueError: If no YAML block is found.
    """
    pattern = r"```yaml\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match is None:
        msg = "No YAML code block found in the output."
        raise ValueError(msg)
    return match.group(1)


def _parse_yaml(content: str) -> dict[str, Any]:
    """Parse YAML string into a dictionary.

    Args:
        content: YAML string.

    Returns:
        Parsed dictionary.

    Raises:
        ValueError: If YAML parsing fails or result is not a dict.
    """
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        msg = f"Failed to parse YAML: {e}"
        raise ValueError(msg) from e

    if not isinstance(data, dict):
        msg = f"Expected YAML dict, got {type(data).__name__}"
        raise ValueError(msg)

    return data


def _build_style_guide(data: dict[str, Any]) -> StyleGuide:
    """Build StyleGuide from parsed YAML data.

    Args:
        data: Parsed YAML dictionary.

    Returns:
        StyleGuide instance.

    Raises:
        ValueError: If required fields are missing or invalid.
    """
    if "work" not in data:
        msg = "Missing required field: 'work'"
        raise ValueError(msg)
    if "pov" not in data:
        msg = "Missing required field: 'pov'"
        raise ValueError(msg)
    if "tense" not in data:
        msg = "Missing required field: 'tense'"
        raise ValueError(msg)

    dialogue = None
    if "dialogue" in data and data["dialogue"] is not None:
        dialogue = DialogueStyle(**data["dialogue"])

    return StyleGuide(
        work=data["work"],
        pov=data["pov"],
        tense=data["tense"],
        style_characteristics=data.get("style_characteristics") or [],
        dialogue=dialogue,
        description_tendencies=data.get("description_tendencies") or [],
        avoid_expressions=data.get("avoid_expressions") or [],
        notes=data.get("notes"),
        created=data.get("created"),
        updated=data.get("updated"),
    )


def _build_style_profile(data: dict[str, Any]) -> StyleProfile:
    """Build StyleProfile from parsed YAML data.

    Args:
        data: Parsed YAML dictionary.

    Returns:
        StyleProfile instance.

    Raises:
        ValueError: If required fields are missing or invalid.
    """
    if "work" not in data:
        msg = "Missing required field: 'work'"
        raise ValueError(msg)

    return StyleProfile(
        work=data["work"],
        avg_sentence_length=data.get("avg_sentence_length"),
        dialogue_ratio=data.get("dialogue_ratio"),
        ttr=data.get("ttr"),
        pos_ratios=data.get("pos_ratios") or {},
        frequent_words=data.get("frequent_words") or [],
        sample_episodes=data.get("sample_episodes") or [],
        analyzed_at=data.get("analyzed_at"),
    )
