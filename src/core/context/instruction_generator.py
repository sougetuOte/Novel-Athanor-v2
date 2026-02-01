"""Instruction generator protocol and implementation for L3 context building.

This module defines the protocol for generating foreshadowing
instructions based on scene context and foreshadowing data,
as well as the concrete implementation.
"""

from typing import Any, Protocol

from src.core.models.foreshadowing import Foreshadowing
from src.core.repositories.foreshadowing import ForeshadowingRepository

from .foreshadow_instruction import (
    ForeshadowInstruction,
    ForeshadowInstructions,
    InstructionAction,
)
from .foreshadowing_identifier import ForeshadowingIdentifier, IdentifiedForeshadowing
from .scene_identifier import SceneIdentifier


class InstructionGenerator(Protocol):
    """Protocol for generating foreshadowing instructions.

    Implementations analyze foreshadowing data and scene context
    to generate appropriate instructions for the Ghost Writer.
    """

    def generate(
        self,
        scene: SceneIdentifier,
        foreshadowings: list[dict[str, Any]],
    ) -> ForeshadowInstructions:
        """Generate foreshadowing instructions for a scene.

        Args:
            scene: The scene identifier.
            foreshadowings: List of foreshadowing data from L2 ForeshadowingManager.

        Returns:
            Generated ForeshadowInstructions.
        """
        ...

    def determine_action(
        self,
        foreshadowing: dict[str, Any],
        scene: SceneIdentifier,
    ) -> InstructionAction:
        """Determine the action for a foreshadowing element.

        Based on the foreshadowing status and scene relationship,
        determines the appropriate action (PLANT/REINFORCE/HINT/NONE).

        Decision logic:
        - registered + plant_scene matches -> PLANT
        - planted + in reinforce_scenes -> REINFORCE
        - planted + otherwise -> HINT or NONE
        - revealed -> NONE

        Args:
            foreshadowing: Foreshadowing data dict.
            scene: The scene identifier.

        Returns:
            The determined InstructionAction.
        """
        ...

    def collect_forbidden_keywords(
        self,
        instructions: ForeshadowInstructions,
    ) -> list[str]:
        """Collect all forbidden keywords from instructions.

        Args:
            instructions: The foreshadowing instructions.

        Returns:
            Deduplicated list of forbidden keywords.
        """
        ...


class InstructionGeneratorImpl:
    """Concrete implementation of InstructionGenerator.

    Generates foreshadowing instructions by using ForeshadowingIdentifier
    to find relevant foreshadowing elements and creating appropriate
    instructions for each.

    Attributes:
        repository: Foreshadowing repository for data access.
        identifier: Foreshadowing identifier for scene analysis.
    """

    def __init__(
        self,
        repository: ForeshadowingRepository,
        identifier: ForeshadowingIdentifier,
    ) -> None:
        """Initialize InstructionGeneratorImpl.

        Args:
            repository: Foreshadowing repository instance.
            identifier: Foreshadowing identifier instance.
        """
        self.repository = repository
        self.identifier = identifier

    def generate(
        self,
        scene: SceneIdentifier,
        appearing_characters: list[str] | None = None,
    ) -> ForeshadowInstructions:
        """Generate foreshadowing instructions for a scene.

        Args:
            scene: The scene identifier.
            appearing_characters: Characters appearing in the scene.

        Returns:
            Generated ForeshadowInstructions.
        """
        instructions = ForeshadowInstructions()

        # Identify relevant foreshadowing elements
        identified = self.identifier.identify(scene, appearing_characters)

        # Generate instruction for each identified element
        for item in identified:
            instruction = self._generate_instruction(item)
            instructions.add_instruction(instruction)

        return instructions

    def _generate_instruction(
        self,
        identified: IdentifiedForeshadowing,
    ) -> ForeshadowInstruction:
        """Generate a single instruction from identified foreshadowing.

        Args:
            identified: Identified foreshadowing element.

        Returns:
            Generated instruction.
        """
        # Get full foreshadowing data
        fs = self.repository.read(identified.foreshadowing_id)

        # Generate instruction based on action
        if identified.suggested_action == InstructionAction.PLANT:
            return self._generate_plant_instruction(fs)
        elif identified.suggested_action == InstructionAction.REINFORCE:
            return self._generate_reinforce_instruction(fs)
        elif identified.suggested_action == InstructionAction.HINT:
            return self._generate_hint_instruction(fs)
        else:
            return self._generate_none_instruction(fs)

    def _generate_plant_instruction(self, fs: Foreshadowing) -> ForeshadowInstruction:
        """Generate PLANT instruction.

        For first-time placement, use clearer descriptions.

        Args:
            fs: Foreshadowing data.

        Returns:
            PLANT instruction.
        """
        note = "伏線の初回設置。"
        if fs.seed and fs.seed.description:
            note += f" {fs.seed.description}"

        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=InstructionAction.PLANT,
            allowed_expressions=list(fs.ai_visibility.allowed_expressions),
            forbidden_expressions=list(fs.ai_visibility.forbidden_keywords),
            note=note,
            subtlety_target=self._calculate_subtlety(fs, InstructionAction.PLANT),
        )

    def _generate_reinforce_instruction(self, fs: Foreshadowing) -> ForeshadowInstruction:
        """Generate REINFORCE instruction.

        For reinforcement, be more subtle than planting.

        Args:
            fs: Foreshadowing data.

        Returns:
            REINFORCE instruction.
        """
        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=InstructionAction.REINFORCE,
            allowed_expressions=list(fs.ai_visibility.allowed_expressions),
            forbidden_expressions=list(fs.ai_visibility.forbidden_keywords),
            note="伏線の強化。控えめに想起させてください。",
            subtlety_target=self._calculate_subtlety(fs, InstructionAction.REINFORCE),
        )

    def _generate_hint_instruction(self, fs: Foreshadowing) -> ForeshadowInstruction:
        """Generate HINT instruction.

        For hints, be very subtle.

        Args:
            fs: Foreshadowing data.

        Returns:
            HINT instruction.
        """
        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=InstructionAction.HINT,
            allowed_expressions=list(fs.ai_visibility.allowed_expressions),
            forbidden_expressions=list(fs.ai_visibility.forbidden_keywords),
            note="非常に控えめなヒントのみ。気づかなくても問題ない程度に。",
            subtlety_target=self._calculate_subtlety(fs, InstructionAction.HINT),
        )

    def _generate_none_instruction(self, fs: Foreshadowing) -> ForeshadowInstruction:
        """Generate NONE instruction.

        For revealed or otherwise inactive foreshadowing.

        Args:
            fs: Foreshadowing data.

        Returns:
            NONE instruction.
        """
        return ForeshadowInstruction(
            foreshadowing_id=fs.id,
            action=InstructionAction.NONE,
            forbidden_expressions=list(fs.ai_visibility.forbidden_keywords),
            note="この伏線には今回触れないでください。",
            subtlety_target=10,
        )

    def _calculate_subtlety(
        self,
        fs: Foreshadowing,
        action: InstructionAction,
    ) -> int:
        """Calculate subtlety_target based on action and foreshadowing settings.

        Args:
            fs: Foreshadowing data.
            action: The action being taken.

        Returns:
            Subtlety target (1-10).
        """
        # Base values by action type
        base_subtlety = {
            InstructionAction.PLANT: 4,
            InstructionAction.REINFORCE: 6,
            InstructionAction.HINT: 8,
            InstructionAction.NONE: 10,
        }

        subtlety = base_subtlety.get(action, 5)

        # Adjust based on foreshadowing's own subtlety_level
        # If foreshadowing is meant to be more subtle, increase target
        if fs.subtlety_level >= 7:
            subtlety = min(10, subtlety + 2)
        elif fs.subtlety_level <= 3:
            subtlety = max(1, subtlety - 2)

        return subtlety

    def determine_action(
        self,
        foreshadowing: dict[str, Any],
        scene: SceneIdentifier,
    ) -> InstructionAction:
        """Determine action for a foreshadowing element (Protocol method).

        Args:
            foreshadowing: Foreshadowing data as dict.
            scene: Scene identifier.

        Returns:
            Determined action.
        """
        # Use identifier to find action
        identified = self.identifier.identify(scene)

        for item in identified:
            if item.foreshadowing_id == foreshadowing.get("id"):
                return item.suggested_action

        return InstructionAction.NONE

    def collect_forbidden_keywords(
        self,
        instructions: ForeshadowInstructions,
    ) -> list[str]:
        """Collect all forbidden keywords from instructions.

        Args:
            instructions: Foreshadowing instructions.

        Returns:
            Deduplicated list of forbidden keywords.
        """
        return instructions.get_all_forbidden()
