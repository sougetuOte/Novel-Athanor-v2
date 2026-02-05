"""Plot context collector for L3 context building.

This module provides PlotCollector which gathers plot information
(L1/L2/L3) from the vault for scene generation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ..lazy_loader import FileLazyLoader, LoadPriority
from ..scene_identifier import SceneIdentifier

if TYPE_CHECKING:
    from src.core.repositories.plot import PlotRepository


@dataclass
class PlotContext:
    """Plot context data.

    Attributes:
        l1_theme: L1 theme (overall direction)
        l2_chapter: L2 chapter goal
        l3_scene: L3 scene structure
    """

    l1_theme: str | None = None
    l2_chapter: str | None = None
    l3_scene: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convert to dictionary format.

        Returns:
            Dictionary with plot_l1, plot_l2, plot_l3 keys.
        """
        return {
            "plot_l1": self.l1_theme,
            "plot_l2": self.l2_chapter,
            "plot_l3": self.l3_scene,
        }


class PlotCollector:
    """Plot context collector.

    Collects L1/L2/L3 plot information from vault.

    Supports both file-based and repository-based collection for backward compatibility.

    Attributes:
        vault_root: Vault root path
        loader: Lazy loader for file loading
        repository: Optional PlotRepository for structured data access
    """

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
        repository: "PlotRepository | None" = None,
    ) -> None:
        """Initialize PlotCollector.

        Args:
            vault_root: Root path of the vault
            loader: Lazy loader for file loading
            repository: Optional PlotRepository for structured access
        """
        self.vault_root = vault_root
        self.loader = loader
        self.repository = repository

    def _load_file(self, path: str, priority: LoadPriority) -> str | None:
        """Load a file and extract data if successful.

        This helper method encapsulates the common pattern of loading a file
        and returning its data or None. This abstraction allows future
        enhancements (logging, error handling) to be made in one place.

        Args:
            path: File path relative to vault_root
            priority: Load priority (REQUIRED or OPTIONAL)

        Returns:
            File content if load succeeded, None otherwise.
        """
        result = self.loader.load(path, priority)
        return result.data if result.success else None

    def collect(self, scene: SceneIdentifier) -> PlotContext:
        """Collect plot context.

        Args:
            scene: Scene identifier

        Returns:
            Collected plot context
        """
        return PlotContext(
            l1_theme=self._collect_l1(),
            l2_chapter=self._collect_l2(scene),
            l3_scene=self._collect_l3(scene),
        )

    def _collect_l1(self) -> str | None:
        """Collect L1 plot (theme).

        Uses repository if available, otherwise falls back to file-based loading.

        Path (file-based): _plot/l1_theme.md
        Priority: OPTIONAL (continue without it)

        Returns:
            L1 theme content, or None if not available.
        """
        if self.repository:
            try:
                plot = self.repository.read("L1")
                return plot.content or None
            except Exception:
                # Fall back to file-based if repository fails
                pass

        return self._load_file("_plot/l1_theme.md", LoadPriority.OPTIONAL)

    def _collect_l2(self, scene: SceneIdentifier) -> str | None:
        """Collect L2 plot (chapter goal).

        Uses repository if available and chapter info can be resolved.

        Path (file-based): _plot/l2_{chapter_id}.md
        Priority: OPTIONAL

        Args:
            scene: Scene identifier

        Returns:
            L2 chapter goal content, or None if not available.
        """
        if not scene.chapter_id:
            return None

        # Repository-based collection for L2 would require mapping chapter_id
        # to chapter_number and chapter_name, which is not straightforward.
        # For now, use file-based approach for backward compatibility.

        path = f"_plot/l2_{scene.chapter_id}.md"
        return self._load_file(path, LoadPriority.OPTIONAL)

    def _collect_l3(self, scene: SceneIdentifier) -> str | None:
        """Collect L3 plot (scene structure).

        Uses repository if available and scene info can be resolved.

        Path (file-based): _plot/l3_{episode_id}.md
        Priority: REQUIRED (essential for scene writing)

        Args:
            scene: Scene identifier

        Returns:
            L3 scene structure content, or None if not available.
        """
        # Repository-based collection for L3 would require mapping episode_id
        # to chapter_number, chapter_name, and sequence_number.
        # This mapping is not available in the current SceneIdentifier.
        # For now, use file-based approach for backward compatibility.

        path = f"_plot/l3_{scene.episode_id}.md"
        return self._load_file(path, LoadPriority.REQUIRED)

    def collect_as_string(self, scene: SceneIdentifier) -> str | None:
        """ContextCollector protocol method.

        Collects all plot contexts and returns them as an integrated string.

        Args:
            scene: Scene identifier

        Returns:
            Integrated plot string, or None if no contexts available.
        """
        context = self.collect(scene)

        parts = []
        if context.l1_theme:
            parts.append(f"## テーマ（L1）\n{context.l1_theme}")
        if context.l2_chapter:
            parts.append(f"## 章目標（L2）\n{context.l2_chapter}")
        if context.l3_scene:
            parts.append(f"## シーン構成（L3）\n{context.l3_scene}")

        if not parts:
            return None

        return "\n\n".join(parts)
