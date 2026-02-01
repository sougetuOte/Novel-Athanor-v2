"""Tests for foreshadowing identifier."""

from datetime import date
from pathlib import Path

import pytest

from src.core.context.foreshadow_instruction import InstructionAction
from src.core.context.scene_identifier import SceneIdentifier
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


# --- Test Fixtures ---


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


@pytest.fixture
def scene_ep010() -> SceneIdentifier:
    """Scene for episode 010."""
    return SceneIdentifier(episode_id="010")


@pytest.fixture
def scene_ep015() -> SceneIdentifier:
    """Scene for episode 015."""
    return SceneIdentifier(episode_id="015")


def create_foreshadowing(
    fs_id: str,
    status: ForeshadowingStatus,
    plant_episode: str | None = None,
    reinforce_episodes: list[str] | None = None,
    reveal_episode: str | None = None,
    related_characters: list[str] | None = None,
) -> Foreshadowing:
    """Helper to create foreshadowing with timeline."""
    timeline_events = []

    if plant_episode:
        timeline_events.append(
            TimelineEntry(
                episode=plant_episode,
                type=ForeshadowingStatus.PLANTED,
                date=date.today(),
                expression="planted expression",
                subtlety=5,
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
                    subtlety=6,
                )
            )

    payoff = None
    if reveal_episode:
        payoff = ForeshadowingPayoff(
            content="payoff content",
            planned_episode=reveal_episode,
        )

    return Foreshadowing(
        id=fs_id,
        title=f"Foreshadowing {fs_id}",
        fs_type=ForeshadowingType.PLOT_TWIST,
        status=status,
        subtlety_level=5,
        ai_visibility=ForeshadowingAIVisibility(
            level=2,
            forbidden_keywords=["secret", "truth"],
            allowed_expressions=["mysterious", "shadow"],
        ),
        seed=ForeshadowingSeed(content="seed content"),
        payoff=payoff,
        timeline=TimelineInfo(
            registered_at=date.today(),
            events=timeline_events,
        ),
        related=RelatedElements(
            characters=related_characters or [],
            plot_threads=[],
            locations=[],
        ),
    )


# --- Tests for ForeshadowingIdentifier ---


class TestForeshadowingIdentifierImport:
    """Test that ForeshadowingIdentifier can be imported."""

    def test_import(self):
        """ForeshadowingIdentifier can be imported."""
        from src.core.context.foreshadowing_identifier import (
            ForeshadowingIdentifier,
            IdentifiedForeshadowing,
        )

        assert ForeshadowingIdentifier is not None
        assert IdentifiedForeshadowing is not None


class TestIdentifiedForeshadowing:
    """Tests for IdentifiedForeshadowing dataclass."""

    def test_create(self):
        """IdentifiedForeshadowing can be created."""
        from src.core.context.foreshadowing_identifier import IdentifiedForeshadowing

        identified = IdentifiedForeshadowing(
            foreshadowing_id="FS-010-secret",
            suggested_action=InstructionAction.PLANT,
            status="registered",
            relevance_reason="plant_scene matches",
        )

        assert identified.foreshadowing_id == "FS-010-secret"
        assert identified.suggested_action == InstructionAction.PLANT
        assert identified.status == "registered"
        assert "plant_scene" in identified.relevance_reason


class TestForeshadowingIdentifierPlant:
    """Tests for PLANT action identification."""

    def test_identify_plant_by_id_episode(self, repository: ForeshadowingRepository, scene_ep010: SceneIdentifier):
        """Identify PLANT action when episode matches ID pattern."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        # FS-010-xxx should be planted in episode 010
        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.REGISTERED,
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        results = identifier.identify(scene_ep010)

        assert len(results) == 1
        assert results[0].foreshadowing_id == "FS-010-secret"
        assert results[0].suggested_action == InstructionAction.PLANT

    def test_no_plant_wrong_episode(self, repository: ForeshadowingRepository, scene_ep015: SceneIdentifier):
        """No PLANT when episode doesn't match."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.REGISTERED,
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        results = identifier.identify(scene_ep015)

        # Should not identify this for planting
        plant_results = [r for r in results if r.suggested_action == InstructionAction.PLANT]
        assert len(plant_results) == 0

    def test_no_plant_already_planted(self, repository: ForeshadowingRepository, scene_ep010: SceneIdentifier):
        """No PLANT when already planted."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="010",
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        results = identifier.identify(scene_ep010)

        plant_results = [r for r in results if r.suggested_action == InstructionAction.PLANT]
        assert len(plant_results) == 0


class TestForeshadowingIdentifierReinforce:
    """Tests for REINFORCE action identification."""

    def test_identify_reinforce_from_timeline(self, repository: ForeshadowingRepository, scene_ep015: SceneIdentifier):
        """Identify REINFORCE when episode in timeline events."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="010",
            reinforce_episodes=["015", "020"],
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        results = identifier.identify(scene_ep015)

        reinforce_results = [r for r in results if r.suggested_action == InstructionAction.REINFORCE]
        assert len(reinforce_results) == 1
        assert reinforce_results[0].foreshadowing_id == "FS-010-secret"

    def test_no_reinforce_wrong_episode(self, repository: ForeshadowingRepository, scene_ep010: SceneIdentifier):
        """No REINFORCE when episode not in timeline."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        fs = create_foreshadowing(
            fs_id="FS-005-mystery",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="005",
            reinforce_episodes=["015", "020"],
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        results = identifier.identify(scene_ep010)

        reinforce_results = [r for r in results if r.suggested_action == InstructionAction.REINFORCE]
        assert len(reinforce_results) == 0


class TestForeshadowingIdentifierHint:
    """Tests for HINT action identification."""

    def test_identify_hint_with_appearing_characters(self, repository: ForeshadowingRepository, scene_ep015: SceneIdentifier):
        """Identify HINT when related character appears (via parameter)."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="010",
            related_characters=["Alice", "Bob"],
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        # Pass appearing characters as parameter
        results = identifier.identify(scene_ep015, appearing_characters=["Alice", "Charlie"])

        hint_results = [r for r in results if r.suggested_action == InstructionAction.HINT]
        assert len(hint_results) == 1

    def test_no_hint_no_related_chars(self, repository: ForeshadowingRepository, scene_ep015: SceneIdentifier):
        """No HINT when no related characters appear."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="010",
            related_characters=["Alice", "Bob"],
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        # Pass non-related characters
        results = identifier.identify(scene_ep015, appearing_characters=["Charlie", "David"])

        hint_results = [r for r in results if r.suggested_action == InstructionAction.HINT]
        assert len(hint_results) == 0

    def test_no_hint_without_appearing_chars_param(self, repository: ForeshadowingRepository, scene_ep015: SceneIdentifier):
        """No HINT when appearing_characters not provided."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="010",
            related_characters=["Alice", "Bob"],
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        # No appearing_characters parameter
        results = identifier.identify(scene_ep015)

        hint_results = [r for r in results if r.suggested_action == InstructionAction.HINT]
        assert len(hint_results) == 0


class TestForeshadowingIdentifierReveal:
    """Tests for REVEAL consideration."""

    def test_identify_reveal_episode(self, repository: ForeshadowingRepository):
        """Identify when reveal episode matches."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.REINFORCED,
            plant_episode="010",
            reveal_episode="025",
        )
        repository.create(fs)

        scene_reveal = SceneIdentifier(episode_id="025")

        identifier = ForeshadowingIdentifier(repository)
        results = identifier.identify(scene_reveal)

        # Should be identified for reveal consideration
        assert len(results) >= 1
        assert any(r.foreshadowing_id == "FS-010-secret" for r in results)


class TestForeshadowingIdentifierMultiple:
    """Tests for multiple foreshadowing elements."""

    def test_identify_multiple(self, repository: ForeshadowingRepository, scene_ep010: SceneIdentifier):
        """Identify multiple foreshadowing elements."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        # One for planting
        fs1 = create_foreshadowing(
            fs_id="FS-010-secret1",
            status=ForeshadowingStatus.REGISTERED,
        )
        repository.create(fs1)

        # One already planted, related char appears
        fs2 = create_foreshadowing(
            fs_id="FS-005-secret2",
            status=ForeshadowingStatus.PLANTED,
            plant_episode="005",
            related_characters=["Hero"],
        )
        repository.create(fs2)

        identifier = ForeshadowingIdentifier(repository)
        results = identifier.identify(scene_ep010, appearing_characters=["Hero"])

        assert len(results) >= 2

    def test_empty_repository(self, repository: ForeshadowingRepository, scene_ep010: SceneIdentifier):
        """Empty results from empty repository."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        identifier = ForeshadowingIdentifier(repository)
        results = identifier.identify(scene_ep010)

        assert results == []


class TestForeshadowingIdentifierHelpers:
    """Tests for helper methods."""

    def test_extract_episode_from_id(self, repository: ForeshadowingRepository):
        """Extract episode from foreshadowing ID."""
        from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier

        identifier = ForeshadowingIdentifier(repository)

        assert identifier._extract_episode_from_id("FS-010-secret") == "010"
        assert identifier._extract_episode_from_id("FS-003-mystery") == "003"
        assert identifier._extract_episode_from_id("FS-123-item") == "123"
        assert identifier._extract_episode_from_id("invalid-id") is None
