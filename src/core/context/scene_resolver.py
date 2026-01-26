"""Scene resolver for L3 context building.

This module provides functionality to resolve file paths
from SceneIdentifier within the vault structure.
"""

from dataclasses import dataclass
from pathlib import Path

from .scene_identifier import SceneIdentifier


@dataclass
class ResolvedPaths:
    """Resolved file paths for a scene.

    Contains all file paths related to a specific scene,
    resolved from the vault directory structure.

    Attributes:
        episode: Path to the episode file.
        plot_l1: Path to L1 plot file (theme/overall direction).
        plot_l2: Path to L2 plot file (chapter objective).
        plot_l3: Path to L3 plot file (scene composition).
        summary_l1: Path to L1 summary file.
        summary_l2: Path to L2 summary file.
        summary_l3: Path to L3 summary file.
        style_guide: Path to style guide file.
    """

    episode: Path | None = None
    plot_l1: Path | None = None
    plot_l2: Path | None = None
    plot_l3: Path | None = None
    summary_l1: Path | None = None
    summary_l2: Path | None = None
    summary_l3: Path | None = None
    style_guide: Path | None = None


class SceneResolver:
    """Resolves scene identifiers to file paths.

    Maps SceneIdentifier to actual file paths within the vault structure.
    This class handles the logic of finding relevant files for a given scene
    across different directories (_plot, _summary, episodes, etc.).

    Attributes:
        vault_root: Root directory of the vault.
    """

    def __init__(self, vault_root: Path) -> None:
        """Initialize SceneResolver.

        Args:
            vault_root: Path to the vault root directory.
        """
        self.vault_root = vault_root

    def resolve_all(self, scene: SceneIdentifier) -> ResolvedPaths:
        """Resolve all related paths for a scene.

        Args:
            scene: Scene identifier.

        Returns:
            ResolvedPaths containing all resolved file paths.
        """
        plot_l1, plot_l2, plot_l3 = self.resolve_plot_paths(scene)
        summary_l1, summary_l2, summary_l3 = self.resolve_summary_paths(scene)

        return ResolvedPaths(
            episode=self.resolve_episode_path(scene),
            plot_l1=plot_l1,
            plot_l2=plot_l2,
            plot_l3=plot_l3,
            summary_l1=summary_l1,
            summary_l2=summary_l2,
            summary_l3=summary_l3,
            style_guide=self.resolve_style_guide_path(),
        )

    def resolve_episode_path(self, scene: SceneIdentifier) -> Path | None:
        """Resolve episode file path.

        Searches in the following order:
        1. episodes/{chapter_id}/{episode_id}.md (if chapter_id exists)
        2. episodes/{episode_id}.md (flat structure)

        Args:
            scene: Scene identifier.

        Returns:
            Path to episode file if exists, None otherwise.
        """
        # Try with chapter subdirectory first
        if scene.chapter_id:
            path = (
                self.vault_root
                / "episodes"
                / scene.chapter_id
                / f"{scene.episode_id}.md"
            )
            if path.exists():
                return path

        # Try flat structure
        path = self.vault_root / "episodes" / f"{scene.episode_id}.md"
        return path if path.exists() else None

    def resolve_plot_paths(
        self, scene: SceneIdentifier
    ) -> tuple[Path | None, Path | None, Path | None]:
        """Resolve plot paths (L1, L2, L3).

        L1: l1_theme.md (theme, overall direction)
        L2: l2_{chapter_id}.md (chapter objective)
        L3: l3_{episode_id}.md (scene composition)

        Args:
            scene: Scene identifier.

        Returns:
            Tuple of (L1 path, L2 path, L3 path). Each can be None if not found.
        """
        plot_dir = self.vault_root / "_plot"

        l1 = plot_dir / "l1_theme.md"
        l2 = plot_dir / f"l2_{scene.chapter_id}.md" if scene.chapter_id else None
        l3 = plot_dir / f"l3_{scene.episode_id}.md"

        return (
            l1 if l1.exists() else None,
            l2 if l2 and l2.exists() else None,
            l3 if l3.exists() else None,
        )

    def resolve_summary_paths(
        self, scene: SceneIdentifier
    ) -> tuple[Path | None, Path | None, Path | None]:
        """Resolve summary paths (L1, L2, L3).

        L1: l1_overall.md (overall summary)
        L2: l2_{chapter_id}.md (chapter summary)
        L3: l3_{episode_id}.md (episode summary)

        Args:
            scene: Scene identifier.

        Returns:
            Tuple of (L1 path, L2 path, L3 path). Each can be None if not found.
        """
        summary_dir = self.vault_root / "_summary"

        l1 = summary_dir / "l1_overall.md"
        l2 = summary_dir / f"l2_{scene.chapter_id}.md" if scene.chapter_id else None
        l3 = summary_dir / f"l3_{scene.episode_id}.md"

        return (
            l1 if l1.exists() else None,
            l2 if l2 and l2.exists() else None,
            l3 if l3.exists() else None,
        )

    def resolve_style_guide_path(self) -> Path | None:
        """Resolve style guide path.

        Returns:
            Path to style guide file if exists, None otherwise.
        """
        path = self.vault_root / "_style_guides" / "default.md"
        return path if path.exists() else None
