"""Summary context collector for L3 context building.

This module collects summary information (L1/L2/L3) from the vault.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ..lazy_loader import FileLazyLoader, LoadPriority
from ..scene_identifier import SceneIdentifier

if TYPE_CHECKING:
    from src.core.repositories.summary import SummaryRepository


@dataclass
class SummaryContext:
    """Summary context.

    Attributes:
        l1_overall: L1 overall summary.
        l2_chapter: L2 chapter summary.
        l3_recent: L3 recent scene summary.
    """

    l1_overall: str | None = None
    l2_chapter: str | None = None
    l3_recent: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Convert to dictionary format.

        Returns:
            Dictionary with summary_l1, summary_l2, summary_l3 keys.
        """
        return {
            "summary_l1": self.l1_overall,
            "summary_l2": self.l2_chapter,
            "summary_l3": self.l3_recent,
        }


class SummaryCollector:
    """Summary context collector.

    Collects L1/L2/L3 summaries from vault.
    Summaries are supplementary information, so failures are tolerated.

    Supports both file-based and repository-based collection for backward compatibility.

    Attributes:
        vault_root: Vault root path.
        loader: Lazy loader for file loading.
        repository: Optional SummaryRepository for structured data access.
    """

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
        repository: "SummaryRepository | None" = None,
    ):
        """Initialize SummaryCollector.

        Args:
            vault_root: Vault root path.
            loader: Lazy loader instance.
            repository: Optional SummaryRepository for structured access.
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
            path: File path relative to vault_root.
            priority: Load priority (REQUIRED or OPTIONAL).

        Returns:
            File content if load succeeded, None otherwise.
        """
        result = self.loader.load(path, priority)
        return result.data if result.success else None

    def collect(self, scene: SceneIdentifier) -> SummaryContext:
        """Collect summary context.

        Args:
            scene: Scene identifier.

        Returns:
            Collected summary context.
        """
        return SummaryContext(
            l1_overall=self._collect_l1(),
            l2_chapter=self._collect_l2(scene),
            l3_recent=self._collect_l3(scene),
        )

    def _collect_l1(self) -> str | None:
        """Collect L1 summary (overall).

        Uses repository if available, otherwise falls back to file-based loading.

        Path (file-based): _summary/l1_overall.md
        Priority: OPTIONAL

        Returns:
            L1 overall summary content, or None if not available.
        """
        if self.repository:
            try:
                summary = self.repository.read("L1")
                return summary.content or None
            except Exception:
                # Fall back to file-based if repository fails
                pass

        return self._load_file("_summary/l1_overall.md", LoadPriority.OPTIONAL)

    def _collect_l2(self, scene: SceneIdentifier) -> str | None:
        """Collect L2 summary (chapter).

        Uses repository if available and chapter info can be resolved.

        Path (file-based): _summary/l2_{chapter_id}.md
        Priority: OPTIONAL

        Args:
            scene: Scene identifier.

        Returns:
            L2 chapter summary content, or None if not available.
        """
        if not scene.chapter_id:
            return None

        # Repository-based collection for L2 would require mapping chapter_id
        # to chapter_number and chapter_name, which is not straightforward.
        # For now, use file-based approach for backward compatibility.

        path = f"_summary/l2_{scene.chapter_id}.md"
        return self._load_file(path, LoadPriority.OPTIONAL)

    def _collect_l3(self, scene: SceneIdentifier) -> str | None:
        """Collect L3 summary (recent scene).

        Retrieves summary of the previous episode.
        Uses repository if available and scene info can be resolved.

        Path (file-based): _summary/l3_{previous_episode_id}.md
        Priority: OPTIONAL

        Args:
            scene: Scene identifier.

        Returns:
            L3 recent scene summary content, or None if not available.
        """
        previous_episode_id = self._get_previous_episode_id(scene.episode_id)
        if not previous_episode_id:
            return None

        # Repository-based collection for L3 would require mapping episode_id
        # to chapter_number, chapter_name, and sequence_number.
        # This mapping is not available in the current SceneIdentifier.
        # For now, use file-based approach for backward compatibility.

        path = f"_summary/l3_{previous_episode_id}.md"
        return self._load_file(path, LoadPriority.OPTIONAL)

    def _get_previous_episode_id(self, episode_id: str) -> str | None:
        """Get previous episode ID.

        Example: "ep010" -> "ep009"

        Args:
            episode_id: Current episode ID.

        Returns:
            Previous episode ID, or None if first episode.
        """
        # Match formats like "ep010", "episode010", or "010"
        match = re.match(r"(ep|episode)?(\d+)", episode_id, re.IGNORECASE)
        if not match:
            return None

        prefix = match.group(1) or ""
        num = int(match.group(2))

        if num <= 1:
            return None

        return f"{prefix}{num - 1:03d}"

    def collect_as_string(self, scene: SceneIdentifier) -> str | None:
        """ContextCollector protocol-compliant method.

        Integrates all summaries into a single string.

        Args:
            scene: Scene identifier.

        Returns:
            Integrated summary string, or None if no summaries.
        """
        context = self.collect(scene)

        parts = []
        if context.l1_overall:
            parts.append(f"## 全体要約（L1）\n{context.l1_overall}")
        if context.l2_chapter:
            parts.append(f"## 章要約（L2）\n{context.l2_chapter}")
        if context.l3_recent:
            parts.append(f"## 直近シーン要約（L3）\n{context.l3_recent}")

        if not parts:
            return None

        return "\n\n".join(parts)
