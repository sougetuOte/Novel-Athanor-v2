"""Tests for scene resolver."""

import pytest
from pathlib import Path

from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.scene_resolver import ResolvedPaths, SceneResolver


class TestResolvedPaths:
    """Test ResolvedPaths data class."""

    def test_create_empty(self) -> None:
        """Create empty ResolvedPaths."""
        paths = ResolvedPaths()
        assert paths.episode is None
        assert paths.plot_l1 is None
        assert paths.plot_l2 is None
        assert paths.plot_l3 is None
        assert paths.summary_l1 is None
        assert paths.summary_l2 is None
        assert paths.summary_l3 is None
        assert paths.style_guide is None

    def test_create_with_values(self) -> None:
        """Create ResolvedPaths with values."""
        paths = ResolvedPaths(
            episode=Path("episodes/010.md"),
            plot_l1=Path("_plot/l1_theme.md"),
            plot_l2=Path("_plot/l2_ch01.md"),
            summary_l1=Path("_summary/l1_overall.md"),
            style_guide=Path("_style_guides/default.md"),
        )
        assert paths.episode == Path("episodes/010.md")
        assert paths.plot_l1 == Path("_plot/l1_theme.md")
        assert paths.plot_l2 == Path("_plot/l2_ch01.md")
        assert paths.summary_l1 == Path("_summary/l1_overall.md")
        assert paths.style_guide == Path("_style_guides/default.md")


class TestSceneResolver:
    """Test SceneResolver class."""

    @pytest.fixture
    def vault_root(self, tmp_path: Path) -> Path:
        """Create test vault structure."""
        work = tmp_path / "test_work"
        (work / "episodes").mkdir(parents=True)
        (work / "_plot").mkdir()
        (work / "_summary").mkdir()
        (work / "_style_guides").mkdir()

        # Create test files
        (work / "episodes" / "010.md").write_text("Episode 10")
        (work / "_plot" / "l1_theme.md").write_text("Theme")
        (work / "_plot" / "l2_ch01.md").write_text("Chapter 1")
        (work / "_summary" / "l1_overall.md").write_text("Overall")
        (work / "_style_guides" / "default.md").write_text("Style")

        return work

    @pytest.fixture
    def resolver(self, vault_root: Path) -> SceneResolver:
        """Create SceneResolver instance."""
        return SceneResolver(vault_root)

    # Episode path resolution tests
    def test_resolve_episode_path_exists(self, resolver: SceneResolver) -> None:
        """Resolve existing episode path."""
        scene = SceneIdentifier(episode_id="010")
        path = resolver.resolve_episode_path(scene)
        assert path is not None
        assert path.name == "010.md"
        assert path.exists()

    def test_resolve_episode_path_not_exists(self, resolver: SceneResolver) -> None:
        """Resolve non-existing episode path."""
        scene = SceneIdentifier(episode_id="999")
        path = resolver.resolve_episode_path(scene)
        assert path is None

    def test_resolve_episode_path_with_chapter_subdirectory(
        self, vault_root: Path
    ) -> None:
        """Resolve episode in chapter subdirectory."""
        # Create chapter subdirectory structure
        (vault_root / "episodes" / "ch01").mkdir()
        (vault_root / "episodes" / "ch01" / "010.md").write_text("Episode 10 in ch01")

        resolver = SceneResolver(vault_root)
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        path = resolver.resolve_episode_path(scene)

        assert path is not None
        assert path == vault_root / "episodes" / "ch01" / "010.md"
        assert path.exists()

    # Plot paths resolution tests
    def test_resolve_plot_paths(self, resolver: SceneResolver) -> None:
        """Resolve plot paths."""
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        l1, l2, l3 = resolver.resolve_plot_paths(scene)

        assert l1 is not None  # l1_theme.md exists
        assert l1.name == "l1_theme.md"
        assert l2 is not None  # l2_ch01.md exists
        assert l2.name == "l2_ch01.md"
        assert l3 is None  # l3_010.md does not exist

    def test_resolve_plot_paths_without_chapter(self, resolver: SceneResolver) -> None:
        """Resolve plot paths without chapter ID."""
        scene = SceneIdentifier(episode_id="010")
        l1, l2, l3 = resolver.resolve_plot_paths(scene)

        assert l1 is not None
        assert l2 is None  # No chapter_id, so l2 should be None
        assert l3 is None

    def test_resolve_plot_paths_with_l3_exists(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Resolve plot paths when L3 plot exists."""
        # Create L3 plot file
        (vault_root / "_plot" / "l3_010.md").write_text("L3 plot for episode 010")

        scene = SceneIdentifier(episode_id="010")
        l1, l2, l3 = resolver.resolve_plot_paths(scene)

        assert l1 is not None
        assert l3 is not None
        assert l3.name == "l3_010.md"

    # Summary paths resolution tests
    def test_resolve_summary_paths(self, resolver: SceneResolver) -> None:
        """Resolve summary paths."""
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        l1, l2, l3 = resolver.resolve_summary_paths(scene)

        assert l1 is not None  # l1_overall.md exists
        assert l1.name == "l1_overall.md"
        assert l2 is None  # l2_ch01.md does not exist
        assert l3 is None  # l3_010.md does not exist

    def test_resolve_summary_paths_without_chapter(
        self, resolver: SceneResolver
    ) -> None:
        """Resolve summary paths without chapter ID."""
        scene = SceneIdentifier(episode_id="010")
        l1, l2, l3 = resolver.resolve_summary_paths(scene)

        assert l1 is not None
        assert l2 is None
        assert l3 is None

    def test_resolve_summary_paths_all_exist(
        self, resolver: SceneResolver, vault_root: Path
    ) -> None:
        """Resolve summary paths when all levels exist."""
        # Create L2 and L3 summary files
        (vault_root / "_summary" / "l2_ch01.md").write_text("Chapter 1 summary")
        (vault_root / "_summary" / "l3_010.md").write_text("Episode 010 summary")

        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        l1, l2, l3 = resolver.resolve_summary_paths(scene)

        assert l1 is not None
        assert l2 is not None
        assert l2.name == "l2_ch01.md"
        assert l3 is not None
        assert l3.name == "l3_010.md"

    # Style guide path resolution tests
    def test_resolve_style_guide_path(self, resolver: SceneResolver) -> None:
        """Resolve style guide path."""
        path = resolver.resolve_style_guide_path()
        assert path is not None
        assert path.name == "default.md"
        assert path.exists()

    def test_resolve_style_guide_path_not_exists(self, vault_root: Path) -> None:
        """Resolve style guide path when it does not exist."""
        # Remove style guide file
        (vault_root / "_style_guides" / "default.md").unlink()

        resolver = SceneResolver(vault_root)
        path = resolver.resolve_style_guide_path()
        assert path is None

    # resolve_all tests
    def test_resolve_all(self, resolver: SceneResolver) -> None:
        """Resolve all paths for a scene."""
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        paths = resolver.resolve_all(scene)

        assert isinstance(paths, ResolvedPaths)
        assert paths.episode is not None
        assert paths.plot_l1 is not None
        assert paths.plot_l2 is not None
        assert paths.summary_l1 is not None
        assert paths.style_guide is not None

    def test_resolve_all_minimal(self, vault_root: Path) -> None:
        """Resolve all paths with minimal files."""
        # Create minimal vault
        minimal_vault = vault_root / "minimal"
        minimal_vault.mkdir()
        (minimal_vault / "episodes").mkdir()
        (minimal_vault / "_plot").mkdir()
        (minimal_vault / "_summary").mkdir()
        (minimal_vault / "_style_guides").mkdir()

        # Only create episode file
        (minimal_vault / "episodes" / "001.md").write_text("Episode 1")

        resolver = SceneResolver(minimal_vault)
        scene = SceneIdentifier(episode_id="001")
        paths = resolver.resolve_all(scene)

        assert paths.episode is not None
        assert paths.plot_l1 is None
        assert paths.plot_l2 is None
        assert paths.plot_l3 is None
        assert paths.summary_l1 is None
        assert paths.style_guide is None

    def test_resolve_all_comprehensive(self, vault_root: Path) -> None:
        """Resolve all paths when all files exist."""
        # Create all possible files
        (vault_root / "_plot" / "l2_ch01.md").write_text("L2 plot")
        (vault_root / "_plot" / "l3_010.md").write_text("L3 plot")
        (vault_root / "_summary" / "l2_ch01.md").write_text("L2 summary")
        (vault_root / "_summary" / "l3_010.md").write_text("L3 summary")

        resolver = SceneResolver(vault_root)
        scene = SceneIdentifier(episode_id="010", chapter_id="ch01")
        paths = resolver.resolve_all(scene)

        assert paths.episode is not None
        assert paths.plot_l1 is not None
        assert paths.plot_l2 is not None
        assert paths.plot_l3 is not None
        assert paths.summary_l1 is not None
        assert paths.summary_l2 is not None
        assert paths.summary_l3 is not None
        assert paths.style_guide is not None
