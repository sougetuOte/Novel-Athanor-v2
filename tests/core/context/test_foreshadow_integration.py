"""Integration tests for foreshadow instruction generation.

Tests the complete flow:
ForeshadowingIdentifier -> InstructionGeneratorImpl -> ForbiddenKeywordCollector
"""

import time
from datetime import date
from pathlib import Path

import pytest

from src.core.context.forbidden_keyword_collector import ForbiddenKeywordCollector
from src.core.context.foreshadow_instruction import InstructionAction
from src.core.context.foreshadowing_identifier import ForeshadowingIdentifier
from src.core.context.instruction_generator import InstructionGeneratorImpl
from src.core.context.lazy_loader import FileLazyLoader
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
    work_dir = vault / "test_work"

    # Create directories
    (work_dir / "_foreshadowing").mkdir(parents=True)
    (work_dir / "_ai_control").mkdir(parents=True)

    # visibility.yaml
    (work_dir / "_ai_control" / "visibility.yaml").write_text(
        """global_forbidden_keywords:
  - 真の名前
  - 最終兵器
""",
        encoding="utf-8",
    )

    # forbidden_keywords.txt
    (work_dir / "_ai_control" / "forbidden_keywords.txt").write_text(
        """# グローバル禁止キーワード
世界の終末
神の名
""",
        encoding="utf-8",
    )

    return vault


@pytest.fixture
def repository(tmp_vault: Path) -> ForeshadowingRepository:
    """Create a foreshadowing repository."""
    return ForeshadowingRepository(tmp_vault, "test_work")


@pytest.fixture
def work_path(tmp_vault: Path) -> Path:
    """Get work directory path."""
    return tmp_vault / "test_work"


@pytest.fixture
def scene_ep010() -> SceneIdentifier:
    """Scene for episode 010."""
    return SceneIdentifier(episode_id="010")


@pytest.fixture
def scene_ep015() -> SceneIdentifier:
    """Scene for episode 015."""
    return SceneIdentifier(episode_id="015")


@pytest.fixture
def scene_unrelated() -> SceneIdentifier:
    """Scene with no related foreshadowing."""
    return SceneIdentifier(episode_id="999")


def create_foreshadowing(
    fs_id: str,
    status: ForeshadowingStatus,
    title: str = "Test Foreshadowing",
    forbidden_keywords: list[str] | None = None,
    allowed_expressions: list[str] | None = None,
    seed_description: str | None = None,
    subtlety_level: int = 5,
    reinforce_episodes: list[str] | None = None,
    reveal_episode: str | None = None,
    related_characters: list[str] | None = None,
) -> Foreshadowing:
    """Helper to create foreshadowing with full configuration."""
    timeline_events = []

    # If status is PLANTED or later, add a plant event
    if status in (
        ForeshadowingStatus.PLANTED,
        ForeshadowingStatus.REINFORCED,
        ForeshadowingStatus.REVEALED,
    ):
        # Extract plant episode from ID
        parts = fs_id.split("-")
        if len(parts) >= 2:
            plant_episode = parts[1]
            timeline_events.append(
                TimelineEntry(
                    episode=plant_episode,
                    type=ForeshadowingStatus.PLANTED,
                    date=date.today(),
                    expression="planted",
                    subtlety=subtlety_level,
                )
            )

    # Add reinforce events
    if reinforce_episodes:
        for ep in reinforce_episodes:
            timeline_events.append(
                TimelineEntry(
                    episode=ep,
                    type=ForeshadowingStatus.REINFORCED,
                    date=date.today(),
                    expression="reinforced",
                    subtlety=subtlety_level + 1,
                )
            )

    payoff = None
    if reveal_episode:
        payoff = ForeshadowingPayoff(
            content="payoff content",
            planned_episode=reveal_episode,
        )

    seed = ForeshadowingSeed(content="seed content")
    if seed_description:
        seed = ForeshadowingSeed(content="seed content", description=seed_description)

    return Foreshadowing(
        id=fs_id,
        title=title,
        fs_type=ForeshadowingType.PLOT_TWIST,
        status=status,
        subtlety_level=subtlety_level,
        ai_visibility=ForeshadowingAIVisibility(
            level=2,
            forbidden_keywords=forbidden_keywords or [],
            allowed_expressions=allowed_expressions or [],
        ),
        seed=seed,
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


# --- Integration Tests ---


class TestForeshadowIntegrationCompleteFlow:
    """Tests for complete flow: identify -> generate -> collect."""

    def test_complete_flow_plant_and_reinforce(
        self,
        repository: ForeshadowingRepository,
        work_path: Path,
        scene_ep010: SceneIdentifier,
    ):
        """Complete flow: scene -> identify -> generate -> collect forbidden."""
        # Setup: Create foreshadowing data
        # FS-010-secret should be PLANTED in ep010
        fs1 = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.REGISTERED,
            title="王族の秘密",
            forbidden_keywords=["王族", "血筋"],
            allowed_expressions=["気高い雰囲気", "見覚えのある光"],
            seed_description="自然に描写してください",
        )
        repository.create(fs1)

        # FS-005-magic was planted in ep005, should be REINFORCED in ep010
        fs2 = create_foreshadowing(
            fs_id="FS-005-magic",
            status=ForeshadowingStatus.PLANTED,
            title="禁忌の魔法",
            forbidden_keywords=["禁忌の魔法"],
            allowed_expressions=["古の技法"],
            reinforce_episodes=["010", "015"],
        )
        repository.create(fs2)

        # Create components
        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)
        loader = FileLazyLoader(work_path)
        collector = ForbiddenKeywordCollector(work_path, loader)

        # 1. Generate instructions
        instructions = generator.generate(scene_ep010)

        # 2. Collect forbidden keywords
        forbidden_result = collector.collect(scene_ep010, instructions)

        # Verify instructions
        assert len(instructions.instructions) == 2

        # PLANT instruction for FS-010-secret
        plant_inst = instructions.get_for_foreshadowing("FS-010-secret")
        assert plant_inst is not None
        assert plant_inst.action == InstructionAction.PLANT
        assert "王族" in plant_inst.forbidden_expressions
        assert "血筋" in plant_inst.forbidden_expressions
        assert "気高い雰囲気" in plant_inst.allowed_expressions

        # REINFORCE instruction for FS-005-magic
        reinforce_inst = instructions.get_for_foreshadowing("FS-005-magic")
        assert reinforce_inst is not None
        assert reinforce_inst.action == InstructionAction.REINFORCE

        # Verify forbidden keywords from all sources
        # From foreshadowing
        assert "王族" in forbidden_result.keywords
        assert "血筋" in forbidden_result.keywords
        assert "禁忌の魔法" in forbidden_result.keywords

        # From visibility.yaml
        assert "真の名前" in forbidden_result.keywords
        assert "最終兵器" in forbidden_result.keywords

        # From forbidden_keywords.txt
        assert "世界の終末" in forbidden_result.keywords
        assert "神の名" in forbidden_result.keywords

    def test_hint_with_appearing_characters(
        self,
        repository: ForeshadowingRepository,
        work_path: Path,
        scene_ep015: SceneIdentifier,
    ):
        """HINT instruction when related character appears."""
        # Setup: Create planted foreshadowing with related characters
        fs = create_foreshadowing(
            fs_id="FS-005-character",
            status=ForeshadowingStatus.PLANTED,
            title="キャラクターの秘密",
            forbidden_keywords=["秘密"],
            allowed_expressions=["影のある表情"],
            related_characters=["アイラ", "ライト"],
        )
        repository.create(fs)

        # Create components
        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        # Generate with appearing characters
        instructions = generator.generate(scene_ep015, appearing_characters=["アイラ", "その他"])

        # Verify HINT instruction
        hint_inst = instructions.get_for_foreshadowing("FS-005-character")
        assert hint_inst is not None
        assert hint_inst.action == InstructionAction.HINT


class TestForeshadowIntegrationSubtlety:
    """Tests for subtlety calculation."""

    def test_subtlety_by_action_type(
        self,
        repository: ForeshadowingRepository,
        scene_ep010: SceneIdentifier,
    ):
        """Different action types have different base subtlety."""
        # PLANT: FS-010-plant
        fs1 = create_foreshadowing(
            fs_id="FS-010-plant",
            status=ForeshadowingStatus.REGISTERED,
            subtlety_level=5,  # Normal
        )
        repository.create(fs1)

        # REINFORCE: FS-005-reinforce planted in ep005, reinforce in ep010
        fs2 = create_foreshadowing(
            fs_id="FS-005-reinforce",
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=5,
            reinforce_episodes=["010"],
        )
        repository.create(fs2)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        instructions = generator.generate(scene_ep010)

        plant_inst = instructions.get_for_foreshadowing("FS-010-plant")
        reinforce_inst = instructions.get_for_foreshadowing("FS-005-reinforce")

        # PLANT should have lower subtlety (more visible)
        # REINFORCE should have higher subtlety (more subtle)
        assert plant_inst is not None
        assert reinforce_inst is not None
        assert plant_inst.subtlety_target < reinforce_inst.subtlety_target

    def test_subtlety_adjusted_by_foreshadowing_level(
        self,
        repository: ForeshadowingRepository,
        scene_ep010: SceneIdentifier,
    ):
        """Subtlety is adjusted by foreshadowing's own subtlety_level."""
        # High subtlety foreshadowing
        fs_subtle = create_foreshadowing(
            fs_id="FS-010-subtle",
            status=ForeshadowingStatus.REGISTERED,
            subtlety_level=8,  # High subtlety
        )
        repository.create(fs_subtle)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        instructions = generator.generate(scene_ep010)

        inst = instructions.get_for_foreshadowing("FS-010-subtle")
        assert inst is not None
        # High subtlety foreshadowing should have higher subtlety_target
        assert inst.subtlety_target >= 6  # Base PLANT (4) + adjustment (2)


class TestForeshadowIntegrationEmptyScenarios:
    """Tests for empty/edge case scenarios."""

    def test_empty_repository(
        self,
        repository: ForeshadowingRepository,
        work_path: Path,
        scene_ep010: SceneIdentifier,
    ):
        """Empty repository returns empty instructions."""
        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)
        loader = FileLazyLoader(work_path)
        collector = ForbiddenKeywordCollector(work_path, loader)

        instructions = generator.generate(scene_ep010)
        forbidden_result = collector.collect(scene_ep010, instructions)

        assert len(instructions.instructions) == 0
        # Still has global/visibility keywords
        assert "真の名前" in forbidden_result.keywords

    def test_unrelated_scene(
        self,
        repository: ForeshadowingRepository,
        scene_unrelated: SceneIdentifier,
    ):
        """Scene with no matching foreshadowing returns empty."""
        fs = create_foreshadowing(
            fs_id="FS-010-secret",
            status=ForeshadowingStatus.REGISTERED,
        )
        repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        instructions = generator.generate(scene_unrelated)

        assert len(instructions.instructions) == 0


class TestForeshadowIntegrationPerformance:
    """Performance tests."""

    def test_performance_within_limit(
        self,
        repository: ForeshadowingRepository,
        work_path: Path,
        scene_ep010: SceneIdentifier,
    ):
        """Complete flow finishes within 100ms."""
        # Create multiple foreshadowing entries
        for i in range(10):
            fs = create_foreshadowing(
                fs_id=f"FS-010-test{i}",
                status=ForeshadowingStatus.REGISTERED,
                forbidden_keywords=[f"keyword{i}"],
            )
            repository.create(fs)

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)
        loader = FileLazyLoader(work_path)
        collector = ForbiddenKeywordCollector(work_path, loader)

        start = time.time()
        instructions = generator.generate(scene_ep010)
        _ = collector.collect(scene_ep010, instructions)
        elapsed = time.time() - start

        assert elapsed < 0.1  # 100ms


class TestForeshadowIntegrationRevealEpisode:
    """Tests for reveal episode handling."""

    def test_reveal_episode_gets_reinforce(
        self,
        repository: ForeshadowingRepository,
    ):
        """Foreshadowing in reveal episode gets REINFORCE action."""
        # Foreshadowing with planned reveal in ep020
        fs = create_foreshadowing(
            fs_id="FS-005-reveal",
            status=ForeshadowingStatus.REINFORCED,
            reveal_episode="020",
        )
        repository.create(fs)

        scene_reveal = SceneIdentifier(episode_id="020")

        identifier = ForeshadowingIdentifier(repository)
        generator = InstructionGeneratorImpl(repository, identifier)

        instructions = generator.generate(scene_reveal)

        inst = instructions.get_for_foreshadowing("FS-005-reveal")
        assert inst is not None
        # Should be REINFORCE to prepare for reveal
        assert inst.action == InstructionAction.REINFORCE
