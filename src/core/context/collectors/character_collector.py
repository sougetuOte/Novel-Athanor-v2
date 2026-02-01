"""Character context collector for L3 context building.

This module provides functionality to collect character information
for a given scene, applying phase filtering.
"""

from dataclasses import dataclass, field
from pathlib import Path

from ...models.character import Character
from ...parsers.frontmatter import ParseError, parse_frontmatter
from ..lazy_loader import FileLazyLoader, LoadPriority
from ..phase_filter import CharacterPhaseFilter
from ..scene_identifier import SceneIdentifier
from ..scene_resolver import SceneResolver


@dataclass
class CharacterContext:
    """Character context result.

    Attributes:
        characters: Map of character name to filtered setting text.
        warnings: List of warnings during collection.
    """

    characters: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def get_names(self) -> list[str]:
        """Get list of character names.

        Returns:
            List of character names in order.
        """
        return list(self.characters.keys())

    def get_character(self, name: str) -> str | None:
        """Get character setting by name.

        Args:
            name: Character name.

        Returns:
            Character setting text, or None if not found.
        """
        return self.characters.get(name)


class CharacterCollector:
    """Character context collector.

    Collects character information for a scene, applying phase filtering
    to hide future information from AI context.

    Attributes:
        vault_root: Vault root directory.
        loader: Lazy loader for file loading.
        resolver: Scene resolver for identifying character files.
        phase_filter: Phase filter for filtering character information.
    """

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
        resolver: SceneResolver,
        phase_filter: CharacterPhaseFilter,
    ):
        """Initialize CharacterCollector.

        Args:
            vault_root: Vault root directory.
            loader: Lazy loader instance.
            resolver: Scene resolver instance.
            phase_filter: Character phase filter instance.
        """
        self.vault_root = vault_root
        self.loader = loader
        self.resolver = resolver
        self.phase_filter = phase_filter

    def collect(self, scene: SceneIdentifier) -> CharacterContext:
        """Collect character context for a scene.

        1. Load episode and plot_l3 files to get content.
        2. Identify character files using resolver.
        3. Load and parse each character file.
        4. Apply phase filter to character data.
        5. Convert to context string.

        Args:
            scene: Scene identifier.

        Returns:
            CharacterContext with collected characters and warnings.
        """
        context = CharacterContext()

        # Load source files and identify characters
        episode_content = self._load_file_content(
            self.resolver.resolve_episode_path(scene)
        )
        _, _, plot_l3_path = self.resolver.resolve_plot_paths(scene)
        plot_l3_content = self._load_file_content(plot_l3_path)

        character_paths = self.resolver.identify_characters(
            scene, episode_content, plot_l3_content
        )

        # Collect each character
        for path in character_paths:
            self._collect_single_character(scene, path, context)

        return context

    def _load_file_content(self, path: Path | None) -> str | None:
        """Load file content with optional priority.

        Args:
            path: File path, or None if file doesn't exist.

        Returns:
            File content, or None if loading failed or path is None.
        """
        if not path:
            return None

        rel_path = str(path.relative_to(self.vault_root))
        result = self.loader.load(rel_path, LoadPriority.OPTIONAL)
        if result.success and result.data:
            return result.data
        return None

    def _collect_single_character(
        self, scene: SceneIdentifier, path: Path, context: CharacterContext
    ) -> None:
        """Collect a single character and add to context.

        Args:
            scene: Scene identifier.
            path: Character file path.
            context: Context to update.
        """
        try:
            # Load file
            rel_path = str(path.relative_to(self.vault_root))
            result = self.loader.load(rel_path, LoadPriority.REQUIRED)
            if not result.success or not result.data:
                context.warnings.append(f"キャラクター読み込み失敗: {path}")
                return

            # Parse character
            character = self._parse_character(path, result.data)
            if not character:
                context.warnings.append(f"キャラクターパース失敗: {path}")
                return

            # Apply phase filter and add to context
            filtered_str = self._apply_phase_filter(character, scene.current_phase)
            context.characters[character.name] = filtered_str

        except Exception as e:
            context.warnings.append(f"キャラクター処理エラー: {path}: {e}")

    def _apply_phase_filter(
        self, character: Character, current_phase: str | None
    ) -> str:
        """Apply phase filter to character.

        Args:
            character: Character to filter.
            current_phase: Current phase, or None for no filtering.

        Returns:
            Filtered character string.
        """
        if current_phase:
            return self.phase_filter.to_context_string(character, current_phase)
        else:
            # No phase specified, return all information
            return self._character_to_string(character)

    def _parse_character(self, path: Path, content: str) -> Character | None:
        """Parse character from file content.

        Args:
            path: File path (for error reporting).
            content: File content.

        Returns:
            Parsed Character, or None if parsing failed.
        """
        try:
            frontmatter, _body = parse_frontmatter(content)
            # Character model doesn't have a body field (uses sections instead)
            return Character(**frontmatter)
        except (ParseError, Exception):
            # Return None on any parsing error
            return None

    def _character_to_string(self, character: Character) -> str:
        """Convert character to string without phase filtering.

        Args:
            character: Character instance.

        Returns:
            Markdown-formatted string.
        """
        lines = [f"# {character.name}"]

        # Add sections
        for section_name, content in character.sections.items():
            lines.append(f"\n## {section_name}")
            lines.append(content)

        # Add phase information
        if character.phases:
            lines.append("\n## Phases")
            for p in character.phases:
                lines.append(f"- {p.name}: episodes {p.episodes}")

        return "\n".join(lines)

    def collect_as_string(self, scene: SceneIdentifier) -> str | None:
        """Collect context as integrated string (ContextCollector protocol).

        Args:
            scene: Scene identifier.

        Returns:
            Integrated character context string, or None if no characters.
        """
        context = self.collect(scene)

        if not context.characters:
            return None

        parts = [
            f"## {name}\n{info}" for name, info in context.characters.items()
        ]

        return "\n\n---\n\n".join(parts)
