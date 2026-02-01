"""Tests for StyleGuideCollector (L3-4-2e)."""

import pytest
from pathlib import Path
from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.lazy_loader import FileLazyLoader
from src.core.context.collectors.style_guide_collector import (
    StyleGuideCollector,
    StyleGuideContext,
)


@pytest.fixture
def vault_root(tmp_path: Path) -> Path:
    """Create vault root with style guides."""
    vault = tmp_path / "vault"
    vault.mkdir()

    # Create _style_guides directory
    style_dir = vault / "_style_guides"
    style_dir.mkdir()

    # Default style guide
    default_guide = style_dir / "default.md"
    default_guide.write_text(
        "# デフォルトスタイルガイド\n\n- 三人称限定視点\n- 過去形で記述",
        encoding="utf-8"
    )

    # Episode-specific override
    episodes_dir = style_dir / "episodes"
    episodes_dir.mkdir()
    ep010_guide = episodes_dir / "ep010.md"
    ep010_guide.write_text(
        "# エピソード010スタイル\n\n- 現在形で記述",
        encoding="utf-8"
    )

    # Chapter-specific override
    chapters_dir = style_dir / "chapters"
    chapters_dir.mkdir()
    chapter01_guide = chapters_dir / "chapter01.md"
    chapter01_guide.write_text(
        "# 章01スタイル\n\n- 一人称視点",
        encoding="utf-8"
    )

    return vault


@pytest.fixture
def loader(vault_root: Path) -> FileLazyLoader:
    """Create FileLazyLoader."""
    return FileLazyLoader(vault_root=vault_root, cache_ttl_seconds=300.0)


@pytest.fixture
def collector(vault_root: Path, loader: FileLazyLoader) -> StyleGuideCollector:
    """Create StyleGuideCollector."""
    return StyleGuideCollector(vault_root=vault_root, loader=loader)


class TestStyleGuideContext:
    """Test StyleGuideContext dataclass."""

    def test_merged_default_only(self):
        """Test merged property with default guide only."""
        context = StyleGuideContext(
            default_guide="# Default\n\n- Rule 1",
            scene_override=None,
        )
        assert context.merged == "# Default\n\n- Rule 1"

    def test_merged_override_only(self):
        """Test merged property with override only."""
        context = StyleGuideContext(
            default_guide=None,
            scene_override="# Override\n\n- Rule 2",
        )
        assert context.merged == "# Override\n\n- Rule 2"

    def test_merged_both(self):
        """Test merged property with both default and override."""
        context = StyleGuideContext(
            default_guide="# Default\n\n- Rule 1",
            scene_override="# Override\n\n- Rule 2",
        )
        expected = (
            "# Default\n\n- Rule 1\n\n"
            "---\n\n"
            "## シーン固有スタイル\n"
            "# Override\n\n- Rule 2"
        )
        assert context.merged == expected

    def test_merged_none(self):
        """Test merged property with no guides."""
        context = StyleGuideContext()
        assert context.merged is None


class TestStyleGuideCollector:
    """Test StyleGuideCollector."""

    def test_collect_default_only(self, collector: StyleGuideCollector):
        """Test collect() with default guide only (no override)."""
        # Scene with no specific style guide
        scene = SceneIdentifier(episode_id="ep999")

        context = collector.collect(scene)

        assert context.default_guide is not None
        assert "デフォルトスタイルガイド" in context.default_guide
        assert context.scene_override is None

    def test_collect_episode_specific(self, collector: StyleGuideCollector):
        """Test collect() with episode-specific override."""
        scene = SceneIdentifier(episode_id="ep010")

        context = collector.collect(scene)

        assert context.default_guide is not None
        assert context.scene_override is not None
        assert "エピソード010スタイル" in context.scene_override

    def test_collect_chapter_specific(self, collector: StyleGuideCollector):
        """Test collect() with chapter-specific override."""
        scene = SceneIdentifier(episode_id="ep999", chapter_id="chapter01")

        context = collector.collect(scene)

        assert context.default_guide is not None
        assert context.scene_override is not None
        assert "章01スタイル" in context.scene_override

    def test_collect_episode_priority_over_chapter(
        self, collector: StyleGuideCollector, vault_root: Path
    ):
        """Test collect() prioritizes episode over chapter when both exist."""
        # Create episode guide for same scene
        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        context = collector.collect(scene)

        # Episode should take priority
        assert context.scene_override is not None
        assert "エピソード010スタイル" in context.scene_override
        assert "章01スタイル" not in context.scene_override

    def test_collect_default_exists(self, collector: StyleGuideCollector):
        """Test _collect_default() when default.md exists."""
        result = collector._collect_default()

        assert result is not None
        assert "デフォルトスタイルガイド" in result

    def test_collect_default_missing(self, tmp_path: Path):
        """Test _collect_default() when default.md is missing."""
        # Empty vault
        vault = tmp_path / "empty_vault"
        vault.mkdir()
        (vault / "_style_guides").mkdir()

        loader = FileLazyLoader(vault_root=vault, cache_ttl_seconds=300.0)
        collector = StyleGuideCollector(vault_root=vault, loader=loader)

        result = collector._collect_default()

        # Should return None for missing REQUIRED file
        assert result is None

    def test_collect_as_string_protocol(self, collector: StyleGuideCollector):
        """Test collect_as_string() conforms to ContextCollector protocol."""
        scene = SceneIdentifier(episode_id="ep010")

        result = collector.collect_as_string(scene)

        assert result is not None
        assert isinstance(result, str)
        # Should include both default and episode override
        assert "デフォルトスタイルガイド" in result
        assert "エピソード010スタイル" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_vault(self, tmp_path: Path):
        """Test with completely empty vault."""
        vault = tmp_path / "empty"
        vault.mkdir()

        loader = FileLazyLoader(vault_root=vault, cache_ttl_seconds=300.0)
        collector = StyleGuideCollector(vault_root=vault, loader=loader)

        scene = SceneIdentifier(episode_id="ep001")
        context = collector.collect(scene)

        assert context.default_guide is None
        assert context.scene_override is None
        assert context.merged is None

    def test_collect_as_string_returns_none_when_no_data(self, tmp_path: Path):
        """Test collect_as_string() returns None when no style guides exist."""
        vault = tmp_path / "empty"
        vault.mkdir()

        loader = FileLazyLoader(vault_root=vault, cache_ttl_seconds=300.0)
        collector = StyleGuideCollector(vault_root=vault, loader=loader)

        scene = SceneIdentifier(episode_id="ep001")
        result = collector.collect_as_string(scene)

        assert result is None
