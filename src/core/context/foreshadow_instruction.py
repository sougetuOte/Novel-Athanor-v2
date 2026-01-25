"""Foreshadowing instruction data classes for L3 context building.

This module defines data classes for representing foreshadowing instructions
that guide the Ghost Writer on how to handle foreshadowing elements in each scene.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class InstructionAction(Enum):
    """Action type for foreshadowing instructions.

    Specifies what action the Ghost Writer should take regarding a
    specific foreshadowing element in the current scene.

    Attributes:
        PLANT: First-time placement of a foreshadowing element.
        REINFORCE: Strengthen an existing foreshadowing element.
        HINT: Provide a subtle hint about the foreshadowing.
        NONE: Do not touch this foreshadowing in this scene.
    """

    PLANT = "plant"
    REINFORCE = "reinforce"
    HINT = "hint"
    NONE = "none"


@dataclass
class ForeshadowInstruction:
    """Individual foreshadowing instruction.

    Specifies how a particular foreshadowing element should be handled
    in the current scene.

    Attributes:
        foreshadowing_id: Unique identifier for the foreshadowing (e.g., "FS-001").
        action: The action to take for this foreshadowing.
        allowed_expressions: List of expressions that CAN be used.
        forbidden_expressions: List of expressions that MUST NOT be used.
        note: Natural language notes for additional guidance.
        subtlety_target: Target subtlety level (1-10, lower = more obvious).

    Raises:
        ValueError: If subtlety_target is not in range 1-10.

    Examples:
        >>> inst = ForeshadowInstruction(
        ...     foreshadowing_id="FS-001",
        ...     action=InstructionAction.PLANT,
        ...     allowed_expressions=["a familiar glint in her eyes"],
        ...     forbidden_expressions=["royal blood", "princess"],
        ...     subtlety_target=7,
        ... )
    """

    foreshadowing_id: str
    action: InstructionAction
    allowed_expressions: list[str] = field(default_factory=list)
    forbidden_expressions: list[str] = field(default_factory=list)
    note: Optional[str] = None
    subtlety_target: int = 5

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not 1 <= self.subtlety_target <= 10:
            raise ValueError(
                f"subtlety_target must be 1-10, got {self.subtlety_target}"
            )

    def should_act(self) -> bool:
        """Check if any action is needed for this foreshadowing.

        Returns:
            True if action is not NONE.
        """
        return self.action != InstructionAction.NONE

    def is_planting(self) -> bool:
        """Check if this is a first-time planting action.

        Returns:
            True if action is PLANT.
        """
        return self.action == InstructionAction.PLANT


@dataclass
class ForeshadowInstructions:
    """Container for all foreshadowing instructions for a scene.

    Groups multiple foreshadowing instructions together with global
    forbidden keywords that apply across all foreshadowing elements.

    Attributes:
        instructions: List of individual foreshadowing instructions.
        global_forbidden_keywords: Keywords forbidden globally (not tied to
            specific foreshadowing elements).

    Examples:
        >>> instructions = ForeshadowInstructions()
        >>> instructions.add_instruction(ForeshadowInstruction(
        ...     foreshadowing_id="FS-001",
        ...     action=InstructionAction.PLANT,
        ... ))
        >>> instructions.add_global_forbidden("royal blood")
        >>> forbidden = instructions.get_all_forbidden()
    """

    instructions: list[ForeshadowInstruction] = field(default_factory=list)
    global_forbidden_keywords: list[str] = field(default_factory=list)

    def get_all_forbidden(self) -> list[str]:
        """Get all forbidden keywords (deduplicated and sorted).

        Combines global forbidden keywords with forbidden expressions
        from all individual instructions.

        Returns:
            Sorted list of unique forbidden keywords.
        """
        result = set(self.global_forbidden_keywords)
        for inst in self.instructions:
            result.update(inst.forbidden_expressions)
        return sorted(result)

    def get_active_instructions(self) -> list[ForeshadowInstruction]:
        """Get only instructions that require action.

        Filters out instructions with NONE action.

        Returns:
            List of instructions where should_act() is True.
        """
        return [inst for inst in self.instructions if inst.should_act()]

    def add_instruction(self, instruction: ForeshadowInstruction) -> None:
        """Add an instruction to the collection.

        Args:
            instruction: The instruction to add.
        """
        self.instructions.append(instruction)

    def add_global_forbidden(self, keyword: str) -> None:
        """Add a global forbidden keyword.

        Duplicates are ignored.

        Args:
            keyword: The keyword to forbid globally.
        """
        if keyword not in self.global_forbidden_keywords:
            self.global_forbidden_keywords.append(keyword)

    def count_by_action(self) -> dict[InstructionAction, int]:
        """Count instructions grouped by action type.

        Returns:
            Dictionary mapping action types to their counts.
        """
        counts: dict[InstructionAction, int] = {}
        for inst in self.instructions:
            counts[inst.action] = counts.get(inst.action, 0) + 1
        return counts
