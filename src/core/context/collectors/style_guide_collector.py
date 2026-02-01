"""StyleGuide context collector (L3-4-2e).

This module provides the StyleGuideCollector class for collecting
style guide context from the vault.
"""

from dataclasses import dataclass
from pathlib import Path

from ..lazy_loader import FileLazyLoader, LoadPriority
from ..scene_identifier import SceneIdentifier


@dataclass
class StyleGuideContext:
    """Style guide context.

    Attributes:
        default_guide: Default style guide.
        scene_override: Scene-specific override.
    """

    default_guide: str | None = None
    scene_override: str | None = None

    @property
    def merged(self) -> str | None:
        """Merged style guide.

        scene_override takes priority if present, otherwise default_guide.

        Returns:
            Merged style guide string or None.
        """
        if self.scene_override:
            if self.default_guide:
                return (
                    f"{self.default_guide}\n\n"
                    f"---\n\n"
                    f"## シーン固有スタイル\n"
                    f"{self.scene_override}"
                )
            return self.scene_override
        return self.default_guide


class StyleGuideCollector:
    """Style guide context collector.

    Collects style guides from vault.
    Style guides are required context.

    Attributes:
        vault_root: Vault root path.
        loader: Lazy loader.
    """

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
    ):
        """Initialize StyleGuideCollector.

        Args:
            vault_root: Vault root path.
            loader: Lazy loader for file access.
        """
        self.vault_root = vault_root
        self.loader = loader

    def _load_file(self, path: str, priority: LoadPriority) -> str | None:
        """Load a file and extract data if successful.

        Args:
            path: File path relative to vault_root.
            priority: Load priority (REQUIRED or OPTIONAL).

        Returns:
            File content if load succeeded, None otherwise.
        """
        result = self.loader.load(path, priority)
        return result.data if result.success else None

    def collect(self, scene: SceneIdentifier) -> StyleGuideContext:
        """Collect style guide.

        Args:
            scene: Scene identifier.

        Returns:
            Collected style guide context.
        """
        return StyleGuideContext(
            default_guide=self._collect_default(),
            scene_override=self._collect_scene_override(scene),
        )

    def _collect_default(self) -> str | None:
        """Collect default style guide.

        Path: _style_guides/default.md
        Priority: REQUIRED

        Returns:
            Default style guide content or None.
        """
        return self._load_file("_style_guides/default.md", LoadPriority.REQUIRED)

    def _collect_scene_override(
        self, scene: SceneIdentifier
    ) -> str | None:
        """Collect scene-specific style override.

        Path priority:
        1. _style_guides/episodes/{episode_id}.md (OPTIONAL)
        2. _style_guides/chapters/{chapter_id}.md (OPTIONAL)

        Args:
            scene: Scene identifier.

        Returns:
            Scene-specific style guide or None.
        """
        # Episode-specific override
        episode_path = f"_style_guides/episodes/{scene.episode_id}.md"
        content = self._load_file(episode_path, LoadPriority.OPTIONAL)
        if content:
            return content

        # Chapter-specific override
        if scene.chapter_id:
            chapter_path = f"_style_guides/chapters/{scene.chapter_id}.md"
            content = self._load_file(chapter_path, LoadPriority.OPTIONAL)
            if content:
                return content

        return None

    def collect_as_string(self, scene: SceneIdentifier) -> str | None:
        """Collect style guide as string (ContextCollector protocol).

        Returns merged style guide.

        Args:
            scene: Scene identifier.

        Returns:
            Style guide string or None.
        """
        context = self.collect(scene)
        return context.merged
