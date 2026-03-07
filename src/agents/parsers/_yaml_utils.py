"""Shared YAML extraction and parsing utilities for L4 agent parsers."""

from __future__ import annotations

import re
from typing import Any

import yaml


def extract_yaml_block(text: str) -> str:
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


def parse_yaml(content: str) -> dict[str, Any]:
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
