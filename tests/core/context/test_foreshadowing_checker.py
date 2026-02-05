"""Tests for foreshadowing checker (integrated scene check).

仕様 Section 4.5 check_foreshadowing_for_scene の統合出力テスト。
"""

from datetime import date
from unittest.mock import Mock

import pytest

from src.core.context.foreshadow_instruction import (
    InstructionAction,
)
from src.core.context.foreshadowing_checker import (
    AlertSeverity,
    AlertType,
    ForeshadowingAlert,
    PayoffApproaching,
    PlantSuggestion,
    ReinforceSuggestion,
    SceneForeshadowingCheck,
    SceneForeshadowingChecker,
)
from src.core.context.foreshadowing_identifier import (
    ForeshadowingIdentifier,
    IdentifiedForeshadowing,
)
from src.core.context.instruction_generator import InstructionGeneratorImpl
from src.core.context.scene_identifier import SceneIdentifier
from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingPayoff,
    ForeshadowingSeed,
    ForeshadowingStatus,
    ForeshadowingType,
    TimelineEntry,
    TimelineInfo,
)


class TestPlantSuggestion:
    """Tests for PlantSuggestion data class."""

    def test_create_plant_suggestion(self):
        """Test creating a PlantSuggestion."""
        suggestion = PlantSuggestion(
            foreshadowing_id="FS-010-secret",
            title="主人公の秘密",
            suggestion="この場面で自然に設置できます",
            seed_description="何気なくロケットを触る描写",
            subtlety_level=7,
            related_characters=["主人公"],
        )

        assert suggestion.foreshadowing_id == "FS-010-secret"
        assert suggestion.title == "主人公の秘密"
        assert suggestion.suggestion == "この場面で自然に設置できます"
        assert suggestion.seed_description == "何気なくロケットを触る描写"
        assert suggestion.subtlety_level == 7
        assert suggestion.related_characters == ["主人公"]

    def test_plant_suggestion_defaults(self):
        """Test PlantSuggestion with default values."""
        suggestion = PlantSuggestion(
            foreshadowing_id="FS-010-secret",
            title="主人公の秘密",
            suggestion="設置を推奨",
        )

        assert suggestion.seed_description is None
        assert suggestion.subtlety_level == 5
        assert suggestion.related_characters == []


class TestReinforceSuggestion:
    """Tests for ReinforceSuggestion data class."""

    def test_create_reinforce_suggestion(self):
        """Test creating a ReinforceSuggestion."""
        suggestion = ReinforceSuggestion(
            foreshadowing_id="FS-010-secret",
            title="主人公の秘密",
            last_mentioned="EP-008",
            episodes_since=5,
            suggestion="長期未言及のため強化推奨",
            current_subtlety=7,
        )

        assert suggestion.foreshadowing_id == "FS-010-secret"
        assert suggestion.title == "主人公の秘密"
        assert suggestion.last_mentioned == "EP-008"
        assert suggestion.episodes_since == 5
        assert suggestion.suggestion == "長期未言及のため強化推奨"
        assert suggestion.current_subtlety == 7


class TestPayoffApproaching:
    """Tests for PayoffApproaching data class."""

    def test_create_payoff_approaching(self):
        """Test creating a PayoffApproaching."""
        payoff = PayoffApproaching(
            foreshadowing_id="FS-010-secret",
            title="主人公の秘密",
            planned_reveal="EP-020",
            remaining_episodes=3,
            suggestion="回収が近いです。最終的な強化を検討",
            reinforcement_count=2,
        )

        assert payoff.foreshadowing_id == "FS-010-secret"
        assert payoff.title == "主人公の秘密"
        assert payoff.planned_reveal == "EP-020"
        assert payoff.remaining_episodes == 3
        assert payoff.suggestion == "回収が近いです。最終的な強化を検討"
        assert payoff.reinforcement_count == 2


class TestForeshadowingAlert:
    """Tests for ForeshadowingAlert data class."""

    def test_create_alert_payoff_reminder(self):
        """Test creating a payoff reminder alert."""
        alert = ForeshadowingAlert(
            alert_type=AlertType.PAYOFF_REMINDER,
            severity=AlertSeverity.WARNING,
            foreshadowing_id="FS-010-secret",
            title="回収リマインダー",
            message="伏線「主人公の秘密」の回収予定が近づいています",
            data={"remaining_episodes": 3},
        )

        assert alert.alert_type == AlertType.PAYOFF_REMINDER
        assert alert.severity == AlertSeverity.WARNING
        assert alert.foreshadowing_id == "FS-010-secret"
        assert alert.title == "回収リマインダー"
        assert alert.message == "伏線「主人公の秘密」の回収予定が近づいています"
        assert alert.data["remaining_episodes"] == 3

    def test_create_alert_long_silence(self):
        """Test creating a long silence alert."""
        alert = ForeshadowingAlert(
            alert_type=AlertType.LONG_SILENCE,
            severity=AlertSeverity.WARNING,
            foreshadowing_id="FS-008-door",
            title="長期未言及",
            message="伏線「封印された扉」が12エピソード未言及です",
            data={"episodes_since": 12},
        )

        assert alert.alert_type == AlertType.LONG_SILENCE
        assert alert.severity == AlertSeverity.WARNING


class TestSceneForeshadowingCheck:
    """Tests for SceneForeshadowingCheck data class."""

    def test_create_empty_check(self):
        """Test creating an empty SceneForeshadowingCheck."""
        check = SceneForeshadowingCheck(episode_id="EP-010")

        assert check.episode_id == "EP-010"
        assert check.should_plant == []
        assert check.should_reinforce == []
        assert check.approaching_payoff == []
        assert check.active_instructions == []
        assert check.alerts == []
        assert check.summary == ""

    def test_has_suggestions_property(self):
        """Test has_suggestions property."""
        check = SceneForeshadowingCheck(episode_id="EP-010")
        assert not check.has_suggestions

        check.should_plant.append(
            PlantSuggestion(
                foreshadowing_id="FS-010-secret",
                title="秘密",
                suggestion="設置推奨",
            )
        )
        assert check.has_suggestions

    def test_has_alerts_property(self):
        """Test has_alerts property."""
        check = SceneForeshadowingCheck(episode_id="EP-010")
        assert not check.has_alerts

        check.alerts.append(
            ForeshadowingAlert(
                alert_type=AlertType.LONG_SILENCE,
                severity=AlertSeverity.WARNING,
            )
        )
        assert check.has_alerts

    def test_total_actions_property(self):
        """Test total_actions property."""
        check = SceneForeshadowingCheck(episode_id="EP-010")
        assert check.total_actions == 0

        check.should_plant.append(
            PlantSuggestion(
                foreshadowing_id="FS-010-secret",
                title="秘密",
                suggestion="設置",
            )
        )
        check.should_reinforce.append(
            ReinforceSuggestion(
                foreshadowing_id="FS-008-door",
                title="扉",
                last_mentioned="EP-005",
                episodes_since=5,
                suggestion="強化",
            )
        )
        check.approaching_payoff.append(
            PayoffApproaching(
                foreshadowing_id="FS-005-magic",
                title="魔法",
                planned_reveal="EP-015",
                remaining_episodes=2,
                suggestion="回収準備",
            )
        )

        assert check.total_actions == 3

    def test_get_critical_alerts(self):
        """Test get_critical_alerts method."""
        check = SceneForeshadowingCheck(episode_id="EP-010")

        check.alerts.append(
            ForeshadowingAlert(
                alert_type=AlertType.LONG_SILENCE,
                severity=AlertSeverity.WARNING,
            )
        )
        check.alerts.append(
            ForeshadowingAlert(
                alert_type=AlertType.UNCLOSED_FORESHADOWING,
                severity=AlertSeverity.CRITICAL,
            )
        )
        check.alerts.append(
            ForeshadowingAlert(
                alert_type=AlertType.PAYOFF_REMINDER,
                severity=AlertSeverity.INFO,
            )
        )

        critical = check.get_critical_alerts()
        assert len(critical) == 1
        assert critical[0].severity == AlertSeverity.CRITICAL
        assert critical[0].alert_type == AlertType.UNCLOSED_FORESHADOWING


class TestSceneForeshadowingChecker:
    """Tests for SceneForeshadowingChecker."""

    @pytest.fixture
    def mock_reader(self):
        """Create a mock ForeshadowingReader."""
        reader = Mock()
        return reader

    @pytest.fixture
    def mock_identifier(self):
        """Create a mock ForeshadowingIdentifier."""
        return Mock(spec=ForeshadowingIdentifier)

    @pytest.fixture
    def mock_generator(self):
        """Create a mock InstructionGeneratorImpl."""
        return Mock(spec=InstructionGeneratorImpl)

    @pytest.fixture
    def checker(self, mock_identifier, mock_generator, mock_reader):
        """Create a SceneForeshadowingChecker instance."""
        return SceneForeshadowingChecker(
            foreshadowing_identifier=mock_identifier,
            instruction_generator=mock_generator,
            foreshadowing_reader=mock_reader,
        )

    def test_check_with_plant_action(
        self, checker, mock_identifier, mock_generator, mock_reader
    ):
        """Test check() with PLANT action detected."""
        scene = SceneIdentifier(episode_id="010")

        # Mock ForeshadowingIdentifier to return PLANT action
        identified = IdentifiedForeshadowing(
            foreshadowing_id="FS-010-secret",
            suggested_action=InstructionAction.PLANT,
            status="registered",
            relevance_reason="設置予定エピソード",
        )
        mock_identifier.identify.return_value = [identified]

        # Mock ForeshadowingReader to return foreshadowing data
        foreshadowing = Foreshadowing(
            id="FS-010-secret",
            title="主人公の秘密",
            fs_type=ForeshadowingType.CHARACTER_SECRET,
            status=ForeshadowingStatus.REGISTERED,
            subtlety_level=7,
            seed=ForeshadowingSeed(
                content="ロケットを持っている",
                description="何気なくロケットを触る",
            ),
        )
        mock_reader.read.return_value = foreshadowing
        mock_reader.list_all.return_value = [foreshadowing]

        # Mock InstructionGenerator
        mock_generator.generate.return_value = Mock(instructions=[])

        # Execute
        result = checker.check(scene)

        # Assert
        assert result.episode_id == "010"
        assert len(result.should_plant) == 1
        assert result.should_plant[0].foreshadowing_id == "FS-010-secret"
        assert result.should_plant[0].title == "主人公の秘密"
        assert result.should_plant[0].seed_description == "何気なくロケットを触る"
        assert result.should_plant[0].subtlety_level == 7

    def test_check_with_reinforce_action(
        self, checker, mock_identifier, mock_generator, mock_reader
    ):
        """Test check() with REINFORCE action detected."""
        scene = SceneIdentifier(episode_id="013")

        # Mock ForeshadowingIdentifier to return REINFORCE action
        identified = IdentifiedForeshadowing(
            foreshadowing_id="FS-010-secret",
            suggested_action=InstructionAction.REINFORCE,
            status="planted",
            relevance_reason="強化推奨",
        )
        mock_identifier.identify.return_value = [identified]

        # Mock ForeshadowingReader to return foreshadowing with timeline
        foreshadowing = Foreshadowing(
            id="FS-010-secret",
            title="主人公の秘密",
            fs_type=ForeshadowingType.CHARACTER_SECRET,
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=7,
            timeline=TimelineInfo(
                registered_at=date(2026, 1, 1),
                events=[
                    TimelineEntry(
                        episode="EP-010",
                        type=ForeshadowingStatus.PLANTED,
                        date=date(2026, 1, 10),
                        expression="ロケットを握る",
                        subtlety=7,
                    )
                ],
            ),
        )
        mock_reader.read.return_value = foreshadowing
        mock_reader.list_all.return_value = [foreshadowing]

        # Mock InstructionGenerator
        mock_generator.generate.return_value = Mock(instructions=[])

        # Execute
        result = checker.check(scene)

        # Assert
        assert result.episode_id == "013"
        assert len(result.should_reinforce) == 1
        assert result.should_reinforce[0].foreshadowing_id == "FS-010-secret"
        assert result.should_reinforce[0].title == "主人公の秘密"
        assert result.should_reinforce[0].last_mentioned == "EP-010"
        assert result.should_reinforce[0].episodes_since == 3

    def test_check_with_approaching_payoff(
        self, checker, mock_identifier, mock_generator, mock_reader
    ):
        """Test check() with approaching payoff detected."""
        scene = SceneIdentifier(episode_id="018")

        # Mock no identified foreshadowing (approaching payoff is separate detection)
        mock_identifier.identify.return_value = []

        # Mock ForeshadowingReader to return foreshadowing with payoff
        foreshadowing = Foreshadowing(
            id="FS-010-secret",
            title="主人公の秘密",
            fs_type=ForeshadowingType.CHARACTER_SECRET,
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=7,
            payoff=ForeshadowingPayoff(
                content="ロケットの秘密が明らかになる",
                planned_episode="EP-020",
            ),
            timeline=TimelineInfo(
                registered_at=date(2026, 1, 1),
                events=[
                    TimelineEntry(
                        episode="EP-010",
                        type=ForeshadowingStatus.PLANTED,
                        date=date(2026, 1, 10),
                        expression="ロケットを握る",
                        subtlety=7,
                    ),
                    TimelineEntry(
                        episode="EP-015",
                        type=ForeshadowingStatus.REINFORCED,
                        date=date(2026, 1, 15),
                        expression="ロケットの紋章",
                        subtlety=6,
                    ),
                ],
            ),
        )
        mock_reader.list_all.return_value = [foreshadowing]

        # Mock InstructionGenerator
        mock_generator.generate.return_value = Mock(instructions=[])

        # Execute (with payoff_threshold=3, so EP-018 should detect EP-020 payoff)
        result = checker.check(scene, payoff_threshold=3)

        # Assert
        assert result.episode_id == "018"
        assert len(result.approaching_payoff) == 1
        assert result.approaching_payoff[0].foreshadowing_id == "FS-010-secret"
        assert result.approaching_payoff[0].title == "主人公の秘密"
        assert result.approaching_payoff[0].planned_reveal == "EP-020"
        assert result.approaching_payoff[0].remaining_episodes == 2
        assert result.approaching_payoff[0].reinforcement_count == 1

    def test_check_with_long_silence_alert(
        self, checker, mock_identifier, mock_generator, mock_reader
    ):
        """Test check() with long silence alert generated."""
        scene = SceneIdentifier(episode_id="020")

        # Mock no identified foreshadowing
        mock_identifier.identify.return_value = []

        # Mock ForeshadowingReader to return foreshadowing with long silence
        foreshadowing = Foreshadowing(
            id="FS-010-secret",
            title="主人公の秘密",
            fs_type=ForeshadowingType.CHARACTER_SECRET,
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=7,
            timeline=TimelineInfo(
                registered_at=date(2026, 1, 1),
                events=[
                    TimelineEntry(
                        episode="EP-010",
                        type=ForeshadowingStatus.PLANTED,
                        date=date(2026, 1, 10),
                        expression="ロケットを握る",
                        subtlety=7,
                    )
                ],
            ),
        )
        mock_reader.list_all.return_value = [foreshadowing]

        # Mock InstructionGenerator
        mock_generator.generate.return_value = Mock(instructions=[])

        # Execute (with silence_threshold=5, so EP-020 - EP-010 = 10 episodes exceeds threshold)
        result = checker.check(scene, silence_threshold=5)

        # Assert
        assert result.episode_id == "020"
        assert len(result.alerts) >= 1
        long_silence_alerts = [
            a for a in result.alerts if a.alert_type == AlertType.LONG_SILENCE
        ]
        assert len(long_silence_alerts) == 1
        assert long_silence_alerts[0].foreshadowing_id == "FS-010-secret"
        assert long_silence_alerts[0].severity == AlertSeverity.WARNING

    def test_check_with_no_foreshadowing(
        self, checker, mock_identifier, mock_generator, mock_reader
    ):
        """Test check() when no foreshadowing exists."""
        scene = SceneIdentifier(episode_id="010")

        # Mock empty results
        mock_identifier.identify.return_value = []
        mock_reader.list_all.return_value = []
        mock_generator.generate.return_value = Mock(instructions=[])

        # Execute
        result = checker.check(scene)

        # Assert
        assert result.episode_id == "010"
        assert result.should_plant == []
        assert result.should_reinforce == []
        assert result.approaching_payoff == []
        assert result.alerts == []
        assert not result.has_suggestions
        assert not result.has_alerts
