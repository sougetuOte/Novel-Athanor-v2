"""Phase filter protocol for L3 context building.

This module defines the PhaseFilter protocol and related exceptions for
filtering entities (characters, world settings) based on the current
narrative phase.
"""

from typing import Protocol, TypeVar

from src.core.models.character import Character
from src.core.models.world_setting import WorldSetting

T = TypeVar("T")


class PhaseFilterError(Exception):
    """Base exception for phase filtering errors."""


class InvalidPhaseError(PhaseFilterError):
    """Raised when an invalid phase is specified."""


class PhaseFilter(Protocol[T]):
    """Protocol for filtering entities by narrative phase.

    Characters and world settings contain information that becomes available
    at different points in the story (phases). This protocol defines the
    interface for filtering such entities to return only the information
    appropriate for the current phase.

    The phase filtering logic typically works as follows:
    - Each entity has phase-specific information
    - When filtering by a phase, all information up to and including that
      phase should be returned
    - Information from future phases should be excluded to prevent spoilers

    Example implementation:
        class CharacterPhaseFilter:
            def __init__(self, phase_order: list[str]):
                self.phase_order = phase_order

            def filter_by_phase(self, character: Character, phase: str) -> Character:
                if phase not in self.phase_order:
                    raise InvalidPhaseError(f"Unknown phase: {phase}")

                # Get all phases up to current
                phase_idx = self.phase_order.index(phase)
                applicable = self.phase_order[:phase_idx + 1]

                # Filter character data
                return character.filter_phases(applicable)

            def get_available_phases(self, character: Character) -> list[str]:
                return [p for p in self.phase_order if character.has_phase(p)]

    Type Parameters:
        T: The type of entity being filtered (e.g., Character, WorldSetting).
    """

    def filter_by_phase(self, entity: T, phase: str) -> T:
        """Filter entity to include only phase-appropriate information.

        Args:
            entity: The entity to filter.
            phase: The current narrative phase.

        Returns:
            A filtered version of the entity containing only information
            appropriate for the specified phase.

        Raises:
            InvalidPhaseError: If the specified phase is not valid.
        """
        ...

    def get_available_phases(self, entity: T) -> list[str]:
        """Get the list of phases available in an entity.

        Args:
            entity: The entity to examine.

        Returns:
            List of phase names that have data in this entity.
        """
        ...


class CharacterPhaseFilter:
    """Phase filter for Character entities.

    Filters character information based on the current narrative phase,
    hiding future phases to prevent spoilers in AI context.
    """

    def __init__(self, phase_order: list[str]):
        """Initialize filter with phase progression order.

        Args:
            phase_order: Ordered list of phase names (e.g., ["initial", "arc_1", "finale"]).
        """
        self.phase_order = phase_order

    def filter_by_phase(self, entity: Character, phase: str) -> Character:
        """Filter character to include only phase-appropriate information.

        Args:
            entity: The character to filter.
            phase: The current narrative phase.

        Returns:
            A new Character instance with only phases up to and including
            the specified phase.

        Raises:
            InvalidPhaseError: If the specified phase is not in phase_order.
        """
        if phase not in self.phase_order:
            raise InvalidPhaseError(
                f"Unknown phase: {phase}. Available: {self.phase_order}"
            )

        # Get index of current phase
        phase_idx = self.phase_order.index(phase)
        # All phases up to and including current
        applicable_phases = set(self.phase_order[: phase_idx + 1])

        # Filter phases
        filtered_phases = [p for p in entity.phases if p.name in applicable_phases]

        return Character(
            type=entity.type,
            name=entity.name,
            phases=filtered_phases,
            current_phase=entity.current_phase,
            ai_visibility=entity.ai_visibility,
            sections=entity.sections,
            created=entity.created,
            updated=entity.updated,
            tags=entity.tags,
        )

    def get_available_phases(self, entity: Character) -> list[str]:
        """Get phases that exist in the character.

        Args:
            entity: The character to examine.

        Returns:
            List of phase names from phase_order that exist in the character.
        """
        char_phases = {p.name for p in entity.phases}
        return [p for p in self.phase_order if p in char_phases]

    def to_context_string(self, entity: Character, phase: str) -> str:
        """Convert filtered character to context string for AI.

        Args:
            entity: The character to convert.
            phase: The current narrative phase.

        Returns:
            Markdown-formatted string representation.
        """
        filtered = self.filter_by_phase(entity, phase)

        lines = [f"# {filtered.name}"]

        # Add sections
        for section_name, content in filtered.sections.items():
            lines.append(f"\n## {section_name}")
            lines.append(content)

        # Add phase information
        if filtered.phases:
            lines.append("\n## Phases")
            for p in filtered.phases:
                lines.append(f"- {p.name}: episodes {p.episodes}")

        return "\n".join(lines)


class WorldSettingPhaseFilter:
    """Phase filter for WorldSetting entities.

    Filters world setting information based on the current narrative phase.
    """

    def __init__(self, phase_order: list[str]):
        """Initialize filter with phase progression order.

        Args:
            phase_order: Ordered list of phase names.
        """
        self.phase_order = phase_order

    def filter_by_phase(self, entity: WorldSetting, phase: str) -> WorldSetting:
        """Filter world setting to include only phase-appropriate information.

        Args:
            entity: The world setting to filter.
            phase: The current narrative phase.

        Returns:
            A new WorldSetting instance with filtered phases.

        Raises:
            InvalidPhaseError: If the specified phase is not in phase_order.
        """
        if phase not in self.phase_order:
            raise InvalidPhaseError(
                f"Unknown phase: {phase}. Available: {self.phase_order}"
            )

        phase_idx = self.phase_order.index(phase)
        applicable_phases = set(self.phase_order[: phase_idx + 1])

        filtered_phases = [p for p in entity.phases if p.name in applicable_phases]

        return WorldSetting(
            type=entity.type,
            name=entity.name,
            category=entity.category,
            phases=filtered_phases,
            current_phase=entity.current_phase,
            ai_visibility=entity.ai_visibility,
            sections=entity.sections,
            created=entity.created,
            updated=entity.updated,
            tags=entity.tags,
        )

    def get_available_phases(self, entity: WorldSetting) -> list[str]:
        """Get phases that exist in the world setting.

        Args:
            entity: The world setting to examine.

        Returns:
            List of phase names from phase_order that exist in the world setting.
        """
        setting_phases = {p.name for p in entity.phases}
        return [p for p in self.phase_order if p in setting_phases]

    def to_context_string(self, entity: WorldSetting, phase: str) -> str:
        """Convert filtered world setting to context string for AI.

        Args:
            entity: The world setting to convert.
            phase: The current narrative phase.

        Returns:
            Markdown-formatted string representation.
        """
        filtered = self.filter_by_phase(entity, phase)

        lines = [f"# {filtered.name}", f"Category: {filtered.category}"]

        for section_name, content in filtered.sections.items():
            lines.append(f"\n## {section_name}")
            lines.append(content)

        if filtered.phases:
            lines.append("\n## Phases")
            for p in filtered.phases:
                lines.append(f"- {p.name}: episodes {p.episodes}")

        return "\n".join(lines)
