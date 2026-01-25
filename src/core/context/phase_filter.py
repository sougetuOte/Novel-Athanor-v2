"""Phase filter protocol for L3 context building.

This module defines the PhaseFilter protocol and related exceptions for
filtering entities (characters, world settings) based on the current
narrative phase.
"""

from typing import Protocol, TypeVar

T = TypeVar("T")


class PhaseFilterError(Exception):
    """Base exception for phase filtering errors."""

    pass


class InvalidPhaseError(PhaseFilterError):
    """Raised when an invalid phase is specified."""

    pass


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
