"""Scene resolver for L3 context building.

This module provides functionality to resolve file paths
from SceneIdentifier within the vault structure.
"""

import copy
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .scene_identifier import SceneIdentifier

# Default reference patterns (used when no config file exists)
DEFAULT_REFERENCE_PATTERNS: dict[str, Any] = {
    "character_patterns": {
        "wikilinks": [
            {
                "pattern": r"\[\[characters/([^\]|]+)(?:\|[^\]]+)?\]\]",
                "description": "Full character wikilink",
            },
            {
                "pattern": r"\[\[([^\]/|]+)(?:\|[^\]]+)?\]\]",
                "exclude_prefixes": ["world", "_", "episodes"],
                "description": "Short wikilink (assumes characters/)",
            },
        ],
        "yaml": [
            {
                "pattern": r"^characters:\s*\n((?:\s+-\s*.+\n?)+)",
                "description": "YAML characters list",
            },
        ],
        "list_headers": [
            "登場人物",
            "登場キャラクター",
        ],
    },
    "world_patterns": {
        "wikilinks": [
            {
                "pattern": r"\[\[world/([^\]|]+)(?:\|[^\]]+)?\]\]",
                "description": "World setting wikilink",
            },
        ],
        "yaml": [
            {
                "pattern": r"^world_settings:\s*\n((?:\s+-\s*.+\n?)+)",
                "description": "YAML world_settings list",
            },
        ],
        "list_headers": [
            "関連設定",
            "世界観設定",
        ],
    },
}


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
        self._patterns_cache: dict[str, Any] | None = None

    def get_reference_patterns(
        self, force_reload: bool = False
    ) -> dict[str, Any]:
        """Get reference patterns from config or defaults.

        Loads patterns from _settings/reference_patterns.yaml if exists,
        otherwise returns default patterns.

        Args:
            force_reload: Force reload from file, bypassing cache.

        Returns:
            Dictionary of reference patterns.
        """
        if self._patterns_cache is not None and not force_reload:
            return self._patterns_cache

        config_path = self.vault_root / "_settings" / "reference_patterns.yaml"

        if config_path.exists():
            try:
                content = config_path.read_text(encoding="utf-8")
                loaded = yaml.safe_load(content)
                if isinstance(loaded, dict):
                    self._patterns_cache = self._merge_patterns(loaded)
                    return self._patterns_cache
            except yaml.YAMLError:
                # Invalid YAML, fall back to defaults
                pass

        self._patterns_cache = DEFAULT_REFERENCE_PATTERNS.copy()
        return self._patterns_cache

    def _merge_patterns(self, loaded: dict[str, Any]) -> dict[str, Any]:
        """Merge loaded patterns with defaults.

        Args:
            loaded: Loaded configuration from file.

        Returns:
            Merged configuration with defaults as fallback.
        """
        result = copy.deepcopy(DEFAULT_REFERENCE_PATTERNS)

        for key in ["character_patterns", "world_patterns"]:
            if key in loaded:
                if key not in result:
                    result[key] = {}
                for subkey, value in loaded[key].items():
                    result[key][subkey] = value

        return result

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

    # --- Character identification methods (L3-1-1c) ---

    def identify_characters(
        self,
        scene: SceneIdentifier,
        episode_content: str | None = None,
        plot_l3_content: str | None = None,
    ) -> list[Path]:
        """Identify character files related to a scene.

        Args:
            scene: Scene identifier.
            episode_content: Episode content (pre-loaded).
            plot_l3_content: L3 plot content (pre-loaded).

        Returns:
            List of paths to character files.
        """
        references: set[str] = set()

        if episode_content:
            refs = self._extract_character_references(episode_content)
            references.update(refs)

        if plot_l3_content:
            refs = self._extract_character_references(plot_l3_content)
            references.update(refs)

        # Resolve to paths
        paths: list[Path] = []
        for ref in references:
            path = self._resolve_character_path(ref)
            if path and path not in paths:
                paths.append(path)

        return paths

    def _extract_character_references(self, content: str) -> list[str]:
        """Extract character references from content.

        Recognizes the following formats:
        - [[characters/name]] or [[characters/name|alias]]
        - [[name]] (assumes characters/)
        - YAML frontmatter: characters: [name1, name2]
        - List format: 登場人物: name1, name2

        Args:
            content: Text content to search.

        Returns:
            List of character names.
        """
        references: list[str] = []
        references.extend(self._extract_wikilink_characters(content))
        references.extend(self._extract_yaml_characters(content))
        references.extend(self._extract_list_characters(content))
        return self._deduplicate_references(references)

    def _extract_wikilink_characters(self, content: str) -> list[str]:
        """Extract character refs from wikilinks [[characters/name]] or [[name]]."""
        refs: list[str] = []
        # Pattern: [[characters/name]] or [[characters/name|alias]]
        # Matches: characters/ followed by name, optional |alias, then ]]
        pattern_full = r'\[\[characters/([^\]|]+)(?:\|[^\]]+)?\]\]'
        refs.extend(re.findall(pattern_full, content))

        # Pattern: [[name]] short form (excludes known directory prefixes)
        # Matches: [[ followed by name without /, optional |alias, then ]]
        pattern_short = r'\[\[([^\]/|]+)(?:\|[^\]]+)?\]\]'
        for match in re.findall(pattern_short, content):
            if not match.startswith(('world', '_', 'episodes')):
                refs.append(match)
        return refs

    def _extract_yaml_characters(self, content: str) -> list[str]:
        """Extract character refs from YAML frontmatter characters list."""
        # Pattern: characters: followed by newline and list items (- name)
        pattern = r'^characters:\s*\n((?:\s+-\s*.+\n?)+)'
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            items = re.findall(r'-\s*(.+)', match.group(1))
            return [item.strip() for item in items]
        return []

    def _extract_list_characters(self, content: str) -> list[str]:
        """Extract character refs from configured list headers.

        Uses list_headers from character_patterns configuration.
        """
        patterns = self.get_reference_patterns()
        list_headers = patterns.get("character_patterns", {}).get(
            "list_headers", ["登場人物", "登場キャラクター"]
        )

        refs: list[str] = []
        for header in list_headers:
            # Pattern: header, then : or newline, then list items
            pattern = rf'(?:{re.escape(header)})(?:\s*[:：]\s*|\s*\n)((?:\s*[-・]\s*.+\n?)+)'
            match = re.search(pattern, content)
            if match:
                items = re.findall(r'[-・]\s*(.+)', match.group(1))
                # Pattern to strip wikilink: [[characters/name|alias]] or [[name]]
                wikilink_strip = r'\[\[(?:characters/)?([^\]|]+)(?:\|[^\]]+)?\]\]'
                for item in items:
                    clean = re.sub(wikilink_strip, r'\1', item)
                    refs.append(clean.strip())

        return refs

    def _deduplicate_references(self, references: list[str]) -> list[str]:
        """Deduplicate reference list while preserving order."""
        seen: set[str] = set()
        unique: list[str] = []
        for ref in references:
            if ref and ref not in seen:
                seen.add(ref)
                unique.append(ref)
        return unique

    def _resolve_character_path(self, character_name: str) -> Path | None:
        """Resolve character name to file path.

        Path format: vault/characters/{character_name}.md

        Args:
            character_name: Character name.

        Returns:
            File path if exists, None otherwise.
        """
        char_dir = self.vault_root / "characters"
        if not char_dir.exists():
            return None

        path = char_dir / f"{character_name}.md"
        return path if path.exists() else None

    def list_all_characters(self) -> list[Path]:
        """List all character files in vault.

        Returns:
            All .md files under characters/.
        """
        char_dir = self.vault_root / "characters"
        if not char_dir.exists():
            return []

        return list(char_dir.glob("*.md"))

    # --- World setting identification methods (L3-1-1d) ---

    def identify_world_settings(
        self,
        scene: SceneIdentifier,
        episode_content: str | None = None,
        plot_l3_content: str | None = None,
    ) -> list[Path]:
        """Identify world setting files related to a scene.

        Args:
            scene: Scene identifier.
            episode_content: Episode content (pre-loaded).
            plot_l3_content: L3 plot content (pre-loaded).

        Returns:
            List of paths to world setting files.
        """
        references: set[str] = set()

        if episode_content:
            refs = self._extract_world_references(episode_content)
            references.update(refs)

        if plot_l3_content:
            refs = self._extract_world_references(plot_l3_content)
            references.update(refs)

        # Resolve to paths
        paths: list[Path] = []
        for ref in references:
            path = self._resolve_world_setting_path(ref)
            if path and path not in paths:
                paths.append(path)

        return paths

    def _extract_world_references(self, content: str) -> list[str]:
        """Extract world setting references from content.

        Uses patterns from world_patterns configuration.

        Args:
            content: Text content to search.

        Returns:
            List of setting names (may include path like "地理/王都").
        """
        references: list[str] = []

        # Pattern 1: [[world/path]] or [[world/path|alias]]
        pattern1 = r'\[\[world/([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(pattern1, content)
        references.extend(matches)

        # Pattern 2: YAML frontmatter world_settings list
        yaml_pattern = r'^world_settings:\s*\n((?:\s+-\s*.+\n?)+)'
        yaml_match = re.search(yaml_pattern, content, re.MULTILINE)
        if yaml_match:
            items = re.findall(r'-\s*(.+)', yaml_match.group(1))
            references.extend([item.strip() for item in items])

        # Pattern 3: List format from config
        patterns = self.get_reference_patterns()
        list_headers = patterns.get("world_patterns", {}).get(
            "list_headers", ["関連設定", "世界観設定"]
        )

        for header in list_headers:
            list_pattern = rf'(?:{re.escape(header)})(?:\s*[:：]\s*|\s*\n)((?:\s*[-・]\s*.+\n?)+)'
            list_match = re.search(list_pattern, content)
            if list_match:
                items = re.findall(r'[-・]\s*(.+)', list_match.group(1))
                for item in items:
                    # Remove wikilink formatting if present
                    clean = re.sub(
                        r'\[\[(?:world/)?([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', item
                    )
                    references.append(clean.strip())

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for ref in references:
            if ref and ref not in seen:
                seen.add(ref)
                unique.append(ref)

        return unique

    def _resolve_world_setting_path(self, setting_name: str) -> Path | None:
        """Resolve setting name to file path.

        Path formats:
        - vault/world/{setting_name}.md
        - vault/world/{category}/{setting_name}.md

        Args:
            setting_name: Setting name (may include path like "地理/王都").

        Returns:
            File path if exists, None otherwise.
        """
        world_dir = self.vault_root / "world"
        if not world_dir.exists():
            return None

        # Try direct path first (e.g., "地理/王都")
        if "/" in setting_name:
            path = world_dir / f"{setting_name}.md"
            if path.exists():
                return path

        # Try top-level
        path = world_dir / f"{setting_name}.md"
        if path.exists():
            return path

        # Search in subdirectories
        for subdir in world_dir.iterdir():
            if subdir.is_dir():
                path = subdir / f"{setting_name}.md"
                if path.exists():
                    return path

        return None

    def list_all_world_settings(self) -> list[Path]:
        """List all world setting files recursively.

        Returns:
            All .md files under world/ (recursive).
        """
        world_dir = self.vault_root / "world"
        if not world_dir.exists():
            return []

        return list(world_dir.rglob("*.md"))
