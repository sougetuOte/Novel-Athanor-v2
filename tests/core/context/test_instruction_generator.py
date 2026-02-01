"""Tests for instruction generator protocol."""

from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.foreshadow_instruction import (
    ForeshadowInstructions,
    ForeshadowInstruction,
    InstructionAction,
)
from src.core.context.instruction_generator import InstructionGenerator


class TestInstructionGeneratorProtocol:
    """Test InstructionGenerator protocol compliance."""

    def test_mock_implements_protocol(self):
        """Mock implements InstructionGenerator protocol."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene, [])
        assert isinstance(result, ForeshadowInstructions)

    def test_generate_with_empty_foreshadowings(self):
        """Generate empty instructions with no foreshadowings."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene, [])

        assert isinstance(result, ForeshadowInstructions)
        assert len(result.instructions) == 0
        assert len(result.global_forbidden_keywords) == 0

    def test_generate_with_foreshadowings(self):
        """Generate instructions with foreshadowings."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                instructions = ForeshadowInstructions()
                for fs in foreshadowings:
                    inst = ForeshadowInstruction(
                        foreshadowing_id=fs["id"],
                        action=InstructionAction.PLANT,
                    )
                    instructions.add_instruction(inst)
                return instructions

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.PLANT

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="010")
        foreshadowings = [{"id": "FS-001"}, {"id": "FS-002"}]
        result = generator.generate(scene, foreshadowings)

        assert len(result.instructions) == 2
        assert result.instructions[0].foreshadowing_id == "FS-001"
        assert result.instructions[1].foreshadowing_id == "FS-002"

    def test_determine_action_plant(self):
        """Determine PLANT action."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                if (
                    foreshadowing.get("status") == "registered"
                    and foreshadowing.get("plant_scene") == scene.episode_id
                ):
                    return InstructionAction.PLANT
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="010")
        foreshadowing = {
            "id": "FS-001",
            "status": "registered",
            "plant_scene": "010",
        }

        action = generator.determine_action(foreshadowing, scene)
        assert action == InstructionAction.PLANT

    def test_determine_action_reinforce(self):
        """Determine REINFORCE action."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                if (
                    foreshadowing.get("status") == "planted"
                    and scene.episode_id in foreshadowing.get("reinforce_scenes", [])
                ):
                    return InstructionAction.REINFORCE
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="015")
        foreshadowing = {
            "id": "FS-001",
            "status": "planted",
            "reinforce_scenes": ["015", "020"],
        }

        action = generator.determine_action(foreshadowing, scene)
        assert action == InstructionAction.REINFORCE

    def test_determine_action_hint(self):
        """Determine HINT action."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                if foreshadowing.get("status") == "planted":
                    return InstructionAction.HINT
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="012")
        foreshadowing = {
            "id": "FS-001",
            "status": "planted",
        }

        action = generator.determine_action(foreshadowing, scene)
        assert action == InstructionAction.HINT

    def test_determine_action_none(self):
        """Determine NONE action for revealed foreshadowing."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                if foreshadowing.get("status") == "revealed":
                    return InstructionAction.NONE
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return []

        generator: InstructionGenerator = MockGenerator()
        scene = SceneIdentifier(episode_id="050")
        foreshadowing = {
            "id": "FS-001",
            "status": "revealed",
        }

        action = generator.determine_action(foreshadowing, scene)
        assert action == InstructionAction.NONE

    def test_collect_forbidden_keywords_empty(self):
        """Collect forbidden keywords returns empty list when none exist."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return instructions.get_all_forbidden()

        generator: InstructionGenerator = MockGenerator()
        instructions = ForeshadowInstructions()

        keywords = generator.collect_forbidden_keywords(instructions)
        assert keywords == []

    def test_collect_forbidden_keywords_deduplicates(self):
        """Collect forbidden keywords deduplicates and sorts."""

        class MockGenerator:
            def generate(
                self,
                scene: SceneIdentifier,
                foreshadowings: list[dict],
            ) -> ForeshadowInstructions:
                return ForeshadowInstructions()

            def determine_action(
                self,
                foreshadowing: dict,
                scene: SceneIdentifier,
            ) -> InstructionAction:
                return InstructionAction.NONE

            def collect_forbidden_keywords(
                self,
                instructions: ForeshadowInstructions,
            ) -> list[str]:
                return instructions.get_all_forbidden()

        generator: InstructionGenerator = MockGenerator()
        instructions = ForeshadowInstructions()

        inst1 = ForeshadowInstruction(
            foreshadowing_id="FS-001",
            action=InstructionAction.PLANT,
            forbidden_expressions=["royal", "princess"],
        )
        inst2 = ForeshadowInstruction(
            foreshadowing_id="FS-002",
            action=InstructionAction.REINFORCE,
            forbidden_expressions=["princess", "blood"],
        )
        instructions.add_instruction(inst1)
        instructions.add_instruction(inst2)
        instructions.add_global_forbidden("royal")

        keywords = generator.collect_forbidden_keywords(instructions)
        # Should be deduplicated and sorted
        assert keywords == ["blood", "princess", "royal"]


# --- Tests for InstructionGeneratorImpl ---

from datetime import date
from pathlib import Path

import pytest

from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingAIVisibility,
    ForeshadowingPayoff,
    ForeshadowingSeed,
    ForeshadowingStatus,
    ForeshadowingType,
    RelatedElements,
    TimelineEntry,
    TimelineInfo,
)
from src.core.repositories.foreshadowing import ForeshadowingRepository


@pytest.fixture
def tmp_vault(tmp_path: Path) -> Path:
    """Create a temporary vault structure."""
    vault = tmp_path / "vault"
    (vault / "test_work" / "_foreshadowing").mkdir(parents=True)
    return vault


@pytest.fixture
def repository(tmp_vault: Path) -> ForeshadowingRepository:
    """Create a foreshadowing repository."""
    return ForeshadowingRepository(tmp_vault, "test_work")


def create_foreshadowing(
    fs_id: str,
    status: ForeshadowingStatus,
    plant_episode: str | None = None,
    reinforce_episodes: list[str] | None = None,
    forbidden_keywords: list[str] | None = None,
    allowed_expressions: list[str] | None = None,
    subtlety: int = 5,
) -> Foreshadowing:
    """Helper to create foreshadowing."""
    timeline_events = []

    if plant_episode:
        timeline_events.append(
            TimelineEntry(
                episode=plant_episode,
                type=ForeshadowingStatus.PLANTED,
                date=date.today(),
                expression="planted expression",
                subtlety=subtlety,
            )
        )

    if reinforce_episodes:
        for ep in reinforce_episodes:
            timeline_events.append(
                TimelineEntry(
                    episode=ep,
                    type=ForeshadowingStatus.REINFORCED,
                    date=date.today(),
                    expression="reinforced expression",
                    subtlety=subtlety + 1,
                )
            )

    return Foreshadowing(
        id=fs_id,
        title=f"Foreshadowing {fs_id}",
        fs_type=ForeshadowingType.PLOT_TWIST,
        status=status,
        subtlety_level=subtlety,
        ai_visibility=ForeshadowingAIVisibility(
            level=2,
            forbidden_keywords=forbidden_keywords or [],
            allowed_expressions=allowed_expressions or [],
        ),
        seed=ForeshadowingSeed(content="seed content"),
        payoff=None,
        timeline=TimelineInfo(
            registered_at=date.today(),
            events=timeline_events,
        ),
        related=RelatedElements(),
    )


class TestInstructionGeneratorImplImport:
    """Test InstructionGeneratorImpl can be imported."""

    def test_import(self):
        """InstructionGeneratorImpl can be imported."""
        from src.core.context.instruction_generator import InstructionGeneratorImpl

        assert InstructionGeneratorImpl is not None


class TestInstructionGeneratorImplGenerate:
    """Tests for generate() method."""

    def test_generate_empty_repository(self, repository: ForeshadowingRepository):
        """Generate returns empty instructions for empty repository."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier
        from src.core.context.instruction_generator import InstructionGeneratorImpl

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene)

        assert isinstance(result, ForeshadowInstructions)
        assert len(result.instructions) == 0

    def test_generate_plant_instruction(self, repository: ForeshadowingRepository):
        """Generate PLANT instruction."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier
        from src.core.context.instruction_generator import InstructionGeneratorImpl

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.REGISTERED,
            forbidden_keywords=["truth", "reveal"],
            allowed_expressions=["mysterious", "shadow"],
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene)

        assert len(result.instructions) == 1
        inst = result.instructions[0]
        assert inst.foreshadowing_id == "FS-010-secret"
        assert inst.action == InstructionAction.PLANT
        assert "truth" in inst.forbidden_expressions
        assert "mysterious" in inst.allowed_expressions

    def test_generate_reinforce_instruction(self, repository: ForeshadowingRepository):
        """Generate REINFORCE instruction."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier
        from src.core.context.instruction_generator import InstructionGeneratorImpl

        fs = create_foreshadowing(
            fs_id="FS-005-mystery",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="005",
            reinforce_episodes=["010", "015"],
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene)

        assert len(result.instructions) == 1
        inst = result.instructions[0]
        assert inst.action == InstructionAction.REINFORCE

    def test_generate_multiple_instructions(self, repository: ForeshadowingRepository):
        """Generate multiple instructions."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier
        from src.core.context.instruction_generator import InstructionGeneratorImpl

        # One for planting
        fs1 = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.REGISTERED,
        )
        repository.create(fs1)

        # One for reinforcing
        fs2 = create_foreshadowing(
            fs_id="FS-005-mystery",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="005",
            reinforce_episodes=["010"],
        )
        repository.create(fs2)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene)

        assert len(result.instructions) == 2
        actions = {inst.action for inst in result.instructions}
        assert InstructionAction.PLANT in actions
        assert InstructionAction.REINFORCE in actions


class TestInstructionGeneratorImplSubtlety:
    """Tests for subtlety_target calculation."""

    def test_plant_subtlety(self, repository: ForeshadowingRepository):
        """PLANT gets lower subtlety (more obvious)."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier
        from src.core.context.instruction_generator import InstructionGeneratorImpl

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.REGISTERED,
            subtlety=5,
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene)

        inst = result.instructions[0]
        # PLANT subtlety should be around 4 (more obvious)
        assert 1 <= inst.subtlety_target <= 6

    def test_hint_subtlety(self, repository: ForeshadowingRepository):
        """HINT gets higher subtlety (more subtle)."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier
        from src.core.context.instruction_generator import InstructionGeneratorImpl

        fs = create_foreshadowing(
            fs_id="FS-005-secret",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="005",
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene, appearing_characters=["Hero"])

        # Should not have HINT without related characters
        hint_insts = [i for i in result.instructions if i.action == InstructionAction.HINT]
        # HINT subtlety should be around 8 (more subtle)
        for inst in hint_insts:
            assert inst.subtlety_target >= 6


class TestInstructionGeneratorImplForbiddenKeywords:
    """Tests for forbidden keywords collection."""

    def test_collect_from_instructions(self, repository: ForeshadowingRepository):
        """Collect forbidden keywords from all instructions."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier
        from src.core.context.instruction_generator import InstructionGeneratorImpl

        fs1 = create_foreshadowing(
            fs_id="FS-010-secret1",
            status=ForeshadowingStatus.REGISTERED,
            forbidden_keywords=["truth", "reveal"],
        )
        fs2 = create_foreshadowing(
            fs_id="FS-010-secret2",
            status=ForeshadowingStatus.REGISTERED,
            forbidden_keywords=["mystery", "truth"],  # "truth" duplicated
        )
        repository.create(fs1)
        repository.create(fs2)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        scene = SceneIdentifier(episode_id="010")
        result = generator.generate(scene)

        keywords = generator.collect_forbidden_keywords(result)
        # Should be deduplicated
        assert "truth" in keywords
        assert "reveal" in keywords
        assert "mystery" in keywords
        assert len([k for k in keywords if k == "truth"]) == 1  # No duplicates
