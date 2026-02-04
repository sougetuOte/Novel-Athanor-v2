"""Shared fixtures for context builder tests."""

import pytest

from src.core.context.context_builder import ContextBuilder
from src.core.context.scene_identifier import SceneIdentifier


@pytest.fixture
def scene():
    """Standard test scene identifier."""
    return SceneIdentifier(
        episode_id="ep010", sequence_id="seq_01", current_phase="initial"
    )


@pytest.fixture
def builder(tmp_path):
    """Create a ContextBuilder with empty vault."""
    return ContextBuilder(vault_root=tmp_path)
