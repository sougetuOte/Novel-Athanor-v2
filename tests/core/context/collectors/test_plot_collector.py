"""Tests for PlotCollector.

Tests the collection of plot contexts (L1/L2/L3) from vault files.
"""

import pytest
from pathlib import Path
from src.core.context.collectors.plot_collector import PlotCollector, PlotContext
from src.core.context.lazy_loader import FileLazyLoader
from src.core.context.scene_identifier import SceneIdentifier


class TestPlotContext:
    """Tests for PlotContext data class."""

    def test_to_dict(self):
        """Test to_dict() conversion."""
        # Arrange
        context = PlotContext(
            l1_theme="Main theme",
            l2_chapter="Chapter goal",
            l3_scene="Scene structure",
        )

        # Act
        result = context.to_dict()

        # Assert
        assert result == {
            "plot_l1": "Main theme",
            "plot_l2": "Chapter goal",
            "plot_l3": "Scene structure",
        }

    def test_to_dict_partial(self):
        """Test to_dict() with partial data."""
        # Arrange
        context = PlotContext(l1_theme="Theme only")

        # Act
        result = context.to_dict()

        # Assert
        assert result == {
            "plot_l1": "Theme only",
            "plot_l2": None,
            "plot_l3": None,
        }


class TestPlotCollector:
    """Tests for PlotCollector."""

    @pytest.fixture
    def vault_root(self, tmp_path: Path) -> Path:
        """Create a temporary vault directory."""
        vault = tmp_path / "vault"
        vault.mkdir()
        return vault

    @pytest.fixture
    def loader(self, vault_root: Path) -> FileLazyLoader:
        """Create a FileLazyLoader instance."""
        return FileLazyLoader(vault_root)

    @pytest.fixture
    def collector(self, vault_root: Path, loader: FileLazyLoader) -> PlotCollector:
        """Create a PlotCollector instance."""
        return PlotCollector(vault_root, loader)

    def test_collect_all_exist(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test collect() when all L1/L2/L3 exist."""
        # Arrange
        plot_dir = vault_root / "_plot"
        plot_dir.mkdir()

        (plot_dir / "l1_theme.md").write_text("Overall theme", encoding="utf-8")
        (plot_dir / "l2_chapter01.md").write_text("Chapter 1 goal", encoding="utf-8")
        (plot_dir / "l3_ep010.md").write_text("Scene structure", encoding="utf-8")

        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect(scene)

        # Assert
        assert result.l1_theme == "Overall theme"
        assert result.l2_chapter == "Chapter 1 goal"
        assert result.l3_scene == "Scene structure"

    def test_collect_l1_only(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test collect() when only L1 exists."""
        # Arrange
        plot_dir = vault_root / "_plot"
        plot_dir.mkdir()

        (plot_dir / "l1_theme.md").write_text("Overall theme", encoding="utf-8")

        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect(scene)

        # Assert
        assert result.l1_theme == "Overall theme"
        assert result.l2_chapter is None
        assert result.l3_scene is None

    def test_collect_l3_only(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test collect() when only L3 exists."""
        # Arrange
        plot_dir = vault_root / "_plot"
        plot_dir.mkdir()

        (plot_dir / "l3_ep010.md").write_text("Scene structure", encoding="utf-8")

        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect(scene)

        # Assert
        assert result.l1_theme is None
        assert result.l2_chapter is None
        assert result.l3_scene == "Scene structure"

    def test_collect_l1_theme(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test _collect_l1() - theme collection."""
        # Arrange
        plot_dir = vault_root / "_plot"
        plot_dir.mkdir()

        (plot_dir / "l1_theme.md").write_text("Main theme", encoding="utf-8")

        # Act
        result = collector._collect_l1()

        # Assert
        assert result == "Main theme"

    def test_collect_l2_no_chapter_id(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test _collect_l2() when chapter_id is None."""
        # Arrange
        scene = SceneIdentifier(episode_id="ep010")

        # Act
        result = collector._collect_l2(scene)

        # Assert
        assert result is None

    def test_collect_l3_exists(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test _collect_l3() when L3 file exists."""
        # Arrange
        plot_dir = vault_root / "_plot"
        plot_dir.mkdir()

        (plot_dir / "l3_ep010.md").write_text("Scene structure", encoding="utf-8")

        scene = SceneIdentifier(episode_id="ep010")

        # Act
        result = collector._collect_l3(scene)

        # Assert
        assert result == "Scene structure"

    def test_collect_l3_missing_graceful(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test _collect_l3() when L3 file is missing (REQUIRED but graceful)."""
        # Arrange
        scene = SceneIdentifier(episode_id="ep010")

        # Act
        result = collector._collect_l3(scene)

        # Assert
        # Should return None gracefully despite REQUIRED priority
        assert result is None

    def test_collect_as_string_full(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test collect_as_string() with all contexts."""
        # Arrange
        plot_dir = vault_root / "_plot"
        plot_dir.mkdir()

        (plot_dir / "l1_theme.md").write_text("Overall theme", encoding="utf-8")
        (plot_dir / "l2_chapter01.md").write_text("Chapter goal", encoding="utf-8")
        (plot_dir / "l3_ep010.md").write_text("Scene structure", encoding="utf-8")

        scene = SceneIdentifier(episode_id="ep010", chapter_id="chapter01")

        # Act
        result = collector.collect_as_string(scene)

        # Assert
        assert result is not None
        assert "## テーマ（L1）" in result
        assert "Overall theme" in result
        assert "## 章目標（L2）" in result
        assert "Chapter goal" in result
        assert "## シーン構成（L3）" in result
        assert "Scene structure" in result

    def test_collect_as_string_none_available(
        self, vault_root: Path, collector: PlotCollector
    ):
        """Test collect_as_string() when no contexts are available."""
        # Arrange
        scene = SceneIdentifier(episode_id="ep010")

        # Act
        result = collector.collect_as_string(scene)

        # Assert
        assert result is None
