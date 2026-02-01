"""Forbidden keyword collector for L3 context building.

This module collects forbidden keywords from multiple sources:
1. Foreshadowing instructions (forbidden_expressions)
2. AI visibility settings (visibility.yaml)
3. Global forbidden list (forbidden_keywords.txt)
"""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .foreshadow_instruction import ForeshadowInstructions
from .lazy_loader import FileLazyLoader, LoadPriority
from .scene_identifier import SceneIdentifier


@dataclass
class ForbiddenKeywordResult:
    """Forbidden keyword collection result.

    Attributes:
        keywords: Merged forbidden keywords list (sorted, deduplicated).
        sources: Keyword sources for debugging {source_name: keywords}.
    """

    keywords: list[str] = field(default_factory=list)
    sources: dict[str, list[str]] = field(default_factory=dict)

    def add_from_source(self, source: str, keywords: list[str]) -> None:
        """Add keywords from a source.

        Args:
            source: Source name (e.g., "foreshadowing", "visibility", "global").
            keywords: Keywords from this source.
        """
        self.sources[source] = keywords

    def finalize(self) -> None:
        """Deduplicate and sort all keywords."""
        all_keywords: set[str] = set()
        for kw_list in self.sources.values():
            all_keywords.update(kw_list)
        self.keywords = sorted(all_keywords)


class ForbiddenKeywordCollector:
    """Collects forbidden keywords from multiple sources.

    This class gathers forbidden keywords from:
    1. Foreshadowing instructions (forbidden_expressions from each instruction)
    2. AI visibility settings (global_forbidden_keywords from visibility.yaml)
    3. Global forbidden list (forbidden_keywords.txt)

    Attributes:
        vault_root: Vault root path.
        loader: Lazy loader for file access.
    """

    # File paths relative to vault root
    _VISIBILITY_FILE = "_ai_control/visibility.yaml"
    _FORBIDDEN_FILE = "_ai_control/forbidden_keywords.txt"

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
    ) -> None:
        """Initialize ForbiddenKeywordCollector.

        Args:
            vault_root: Vault root path.
            loader: Lazy loader for file access.
        """
        self.vault_root = vault_root
        self.loader = loader

    def collect(
        self,
        scene: SceneIdentifier,
        foreshadow_instructions: ForeshadowInstructions | None = None,
    ) -> ForbiddenKeywordResult:
        """Collect forbidden keywords from all sources.

        Args:
            scene: Scene identifier.
            foreshadow_instructions: Foreshadowing instructions (optional).

        Returns:
            Collection result with merged keywords and source info.
        """
        result = ForbiddenKeywordResult()

        # 1. From foreshadowing instructions
        if foreshadow_instructions:
            fs_keywords = foreshadow_instructions.get_all_forbidden()
            if fs_keywords:
                result.add_from_source("foreshadowing", fs_keywords)

        # 2. From visibility.yaml
        visibility_keywords = self._collect_from_visibility()
        if visibility_keywords:
            result.add_from_source("visibility", visibility_keywords)

        # 3. From forbidden_keywords.txt
        global_keywords = self._collect_from_global()
        if global_keywords:
            result.add_from_source("global", global_keywords)

        result.finalize()
        return result

    def collect_as_list(
        self,
        scene: SceneIdentifier,
        foreshadow_instructions: ForeshadowInstructions | None = None,
    ) -> list[str]:
        """Collect forbidden keywords as simple list.

        Args:
            scene: Scene identifier.
            foreshadow_instructions: Foreshadowing instructions (optional).

        Returns:
            Sorted, deduplicated list of forbidden keywords.
        """
        result = self.collect(scene, foreshadow_instructions)
        return result.keywords

    def _collect_from_visibility(self) -> list[str]:
        """Collect from visibility.yaml.

        Returns:
            List of forbidden keywords from visibility settings.
        """
        load_result = self.loader.load(self._VISIBILITY_FILE, LoadPriority.OPTIONAL)
        if not load_result.success or not load_result.data:
            return []

        try:
            data = yaml.safe_load(load_result.data)
            if data and isinstance(data, dict):
                keywords = data.get("global_forbidden_keywords", [])
                if isinstance(keywords, list):
                    return [str(k) for k in keywords if k]
        except yaml.YAMLError:
            pass

        return []

    def _collect_from_global(self) -> list[str]:
        """Collect from forbidden_keywords.txt.

        Returns:
            List of forbidden keywords from global list.
        """
        load_result = self.loader.load(self._FORBIDDEN_FILE, LoadPriority.OPTIONAL)
        if not load_result.success or not load_result.data:
            return []

        # Parse line by line, skip comments and empty lines
        keywords: list[str] = []
        for line in load_result.data.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                keywords.append(line)

        return keywords
