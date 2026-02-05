"""Scene foreshadowing checker for integrated check output.

仕様 Section 4.5 check_foreshadowing_for_scene の統合出力実装。
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from src.core.models.foreshadowing import ForeshadowingStatus

from .foreshadow_instruction import ForeshadowInstruction, InstructionAction
from .foreshadowing_identifier import (
    ForeshadowingIdentifier,
    ForeshadowingReader,
    IdentifiedForeshadowing,
)
from .instruction_generator import InstructionGeneratorImpl
from .scene_identifier import SceneIdentifier


class AlertSeverity(Enum):
    """Alert severity level."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertType(Enum):
    """Alert type for foreshadowing management.

    仕様 Section 6 のアラートタイプに対応。
    """

    PAYOFF_REMINDER = "payoff_reminder"
    LONG_SILENCE = "long_silence"
    UNCLOSED_FORESHADOWING = "unclosed_foreshadowing"
    UNINTENTIONAL_FORESHADOWING = "unintentional_foreshadowing"
    PAYOFF_TIMING_SUGGESTION = "payoff_timing_suggestion"


@dataclass
class PlantSuggestion:
    """Plant suggestion for foreshadowing.

    仕様 Section 4.5 output.should_plant に対応。
    """

    foreshadowing_id: str
    title: str
    suggestion: str
    seed_description: str | None = None
    subtlety_level: int = 5
    related_characters: list[str] = field(default_factory=list)


@dataclass
class ReinforceSuggestion:
    """Reinforce suggestion for foreshadowing.

    仕様 Section 4.5 output.should_reinforce に対応。
    """

    foreshadowing_id: str
    title: str
    last_mentioned: str
    episodes_since: int
    suggestion: str
    current_subtlety: int = 5


@dataclass
class PayoffApproaching:
    """Approaching payoff information.

    仕様 Section 4.5 output.approaching_payoff に対応。
    """

    foreshadowing_id: str
    title: str
    planned_reveal: str
    remaining_episodes: int
    suggestion: str
    reinforcement_count: int = 0


@dataclass
class ForeshadowingAlert:
    """Foreshadowing alert.

    仕様 Section 6 の各アラートを統一フォーマットで表現。
    """

    alert_type: AlertType
    severity: AlertSeverity
    foreshadowing_id: str | None = None
    title: str = ""
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneForeshadowingCheck:
    """Integrated foreshadowing check result for a scene.

    仕様 Section 4.5 check_foreshadowing_for_scene の統合出力。
    """

    episode_id: str
    should_plant: list[PlantSuggestion] = field(default_factory=list)
    should_reinforce: list[ReinforceSuggestion] = field(default_factory=list)
    approaching_payoff: list[PayoffApproaching] = field(default_factory=list)
    active_instructions: list[ForeshadowInstruction] = field(default_factory=list)
    alerts: list[ForeshadowingAlert] = field(default_factory=list)
    summary: str = ""

    @property
    def has_suggestions(self) -> bool:
        """Check if any suggestions exist."""
        return bool(
            self.should_plant or self.should_reinforce or self.approaching_payoff
        )

    @property
    def has_alerts(self) -> bool:
        """Check if any alerts exist."""
        return bool(self.alerts)

    @property
    def total_actions(self) -> int:
        """Get total number of suggested actions."""
        return (
            len(self.should_plant)
            + len(self.should_reinforce)
            + len(self.approaching_payoff)
        )

    def get_critical_alerts(self) -> list[ForeshadowingAlert]:
        """Get only critical severity alerts."""
        return [a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]


class SceneForeshadowingChecker:
    """Scene foreshadowing checker for integrated check output.

    仕様 Section 4.5 check_foreshadowing_for_scene の統合チェッカー。
    """

    # Pattern to extract episode number from episode ID
    _EPISODE_PATTERN = re.compile(r"(?:EP-)?0*(\d+)")

    def __init__(
        self,
        foreshadowing_identifier: ForeshadowingIdentifier,
        instruction_generator: InstructionGeneratorImpl,
        foreshadowing_reader: ForeshadowingReader,
    ) -> None:
        """Initialize SceneForeshadowingChecker.

        Args:
            foreshadowing_identifier: Foreshadowing identifier instance.
            instruction_generator: Instruction generator instance.
            foreshadowing_reader: Foreshadowing reader instance.
        """
        self.identifier = foreshadowing_identifier
        self.generator = instruction_generator
        self.reader = foreshadowing_reader

    def check(
        self,
        scene: SceneIdentifier,
        *,
        appearing_characters: list[str] | None = None,
        silence_threshold: int = 5,
        payoff_threshold: int = 3,
    ) -> SceneForeshadowingCheck:
        """Execute integrated foreshadowing check for a scene.

        仕様 Section 4.5 check_foreshadowing_for_scene の実装。

        Args:
            scene: Scene identifier.
            appearing_characters: Characters appearing in the scene.
            silence_threshold: Episode threshold for long silence alert.
            payoff_threshold: Episode threshold for approaching payoff detection.

        Returns:
            Integrated foreshadowing check result.
        """
        result = SceneForeshadowingCheck(episode_id=scene.episode_id)

        # 1. ForeshadowingIdentifier.identify() で関連伏線を特定
        identified = self.identifier.identify(scene, appearing_characters)

        # 2. IdentifiedForeshadowing を PlantSuggestion / ReinforceSuggestion に変換
        for item in identified:
            if item.suggested_action == InstructionAction.PLANT:
                result.should_plant.append(self._to_plant_suggestion(item))
            elif item.suggested_action in (
                InstructionAction.REINFORCE,
                InstructionAction.HINT,
            ):
                result.should_reinforce.append(
                    self._to_reinforce_suggestion(item, scene)
                )

        # 3. payoff が近い伏線を PayoffApproaching に変換
        result.approaching_payoff.extend(
            self._detect_approaching_payoff(scene, payoff_threshold)
        )

        # 4. long_silence アラートを生成
        result.alerts.extend(self._detect_long_silence(scene, silence_threshold))

        # 5. InstructionGeneratorImpl.generate() で active_instructions を取得
        instructions = self.generator.generate(scene, appearing_characters)
        result.active_instructions = instructions.instructions

        return result

    def _to_plant_suggestion(self, identified: IdentifiedForeshadowing) -> PlantSuggestion:
        """Convert IdentifiedForeshadowing to PlantSuggestion.

        Args:
            identified: Identified foreshadowing.

        Returns:
            PlantSuggestion instance.
        """
        # ForeshadowingReader で詳細情報を取得
        foreshadowing = self.reader.read(identified.foreshadowing_id)

        return PlantSuggestion(
            foreshadowing_id=identified.foreshadowing_id,
            title=foreshadowing.title,
            suggestion=identified.relevance_reason,
            seed_description=(
                foreshadowing.seed.description if foreshadowing.seed else None
            ),
            subtlety_level=foreshadowing.subtlety_level,
            related_characters=foreshadowing.related.characters,
        )

    def _to_reinforce_suggestion(
        self, identified: IdentifiedForeshadowing, scene: SceneIdentifier
    ) -> ReinforceSuggestion:
        """Convert IdentifiedForeshadowing to ReinforceSuggestion.

        Args:
            identified: Identified foreshadowing.
            scene: Current scene identifier.

        Returns:
            ReinforceSuggestion instance.
        """
        # ForeshadowingReader で詳細情報を取得
        foreshadowing = self.reader.read(identified.foreshadowing_id)

        # timeline から last_mentioned を算出
        last_mentioned = "unknown"
        episodes_since = 0
        if foreshadowing.timeline and foreshadowing.timeline.events:
            # 最後のイベントを取得
            last_event = foreshadowing.timeline.events[-1]
            last_mentioned = last_event.episode
            # エピソード番号の差分を計算
            episodes_since = self._calculate_episode_gap(
                last_event.episode, scene.episode_id
            )

        return ReinforceSuggestion(
            foreshadowing_id=identified.foreshadowing_id,
            title=foreshadowing.title,
            last_mentioned=last_mentioned,
            episodes_since=episodes_since,
            suggestion=identified.relevance_reason,
            current_subtlety=foreshadowing.subtlety_level,
        )

    def _detect_approaching_payoff(
        self, scene: SceneIdentifier, threshold: int
    ) -> list[PayoffApproaching]:
        """Detect foreshadowing with approaching payoff.

        Args:
            scene: Current scene identifier.
            threshold: Episode threshold for approaching detection.

        Returns:
            List of PayoffApproaching instances.
        """
        result = []
        all_foreshadowing = self.reader.list_all()
        current_ep_num = self._normalize_episode(scene.episode_id)

        for fs in all_foreshadowing:
            # payoff.planned_episode が設定されているかチェック
            if not fs.payoff or not fs.payoff.planned_episode:
                continue

            planned_ep_num = self._normalize_episode(fs.payoff.planned_episode)
            remaining = planned_ep_num - current_ep_num

            # threshold 以内の場合のみ検出
            if 0 < remaining <= threshold:
                # reinforcement_count を計算
                reinforcement_count = 0
                if fs.timeline and fs.timeline.events:
                    reinforcement_count = sum(
                        1
                        for event in fs.timeline.events
                        if event.type == ForeshadowingStatus.REINFORCED
                    )

                result.append(
                    PayoffApproaching(
                        foreshadowing_id=fs.id,
                        title=fs.title,
                        planned_reveal=fs.payoff.planned_episode,
                        remaining_episodes=remaining,
                        suggestion="回収が近いです。最終的な強化を検討",
                        reinforcement_count=reinforcement_count,
                    )
                )

        return result

    def _detect_long_silence(
        self, scene: SceneIdentifier, threshold: int
    ) -> list[ForeshadowingAlert]:
        """Detect foreshadowing with long silence.

        Args:
            scene: Current scene identifier.
            threshold: Episode threshold for long silence detection.

        Returns:
            List of ForeshadowingAlert instances.
        """
        result = []
        all_foreshadowing = self.reader.list_all()
        current_ep_num = self._normalize_episode(scene.episode_id)

        for fs in all_foreshadowing:
            # planted/reinforced 状態のみチェック
            if fs.status not in (
                ForeshadowingStatus.PLANTED,
                ForeshadowingStatus.REINFORCED,
            ):
                continue

            # timeline.events から最後のイベントを取得
            if not fs.timeline or not fs.timeline.events:
                continue

            last_event = fs.timeline.events[-1]
            last_ep_num = self._normalize_episode(last_event.episode)
            gap = current_ep_num - last_ep_num

            # threshold 以上経過していればアラート生成
            if gap >= threshold:
                result.append(
                    ForeshadowingAlert(
                        alert_type=AlertType.LONG_SILENCE,
                        severity=AlertSeverity.WARNING,
                        foreshadowing_id=fs.id,
                        title="長期未言及",
                        message=f"伏線「{fs.title}」が{gap}エピソード未言及です",
                        data={"episodes_since": gap},
                    )
                )

        return result

    def _normalize_episode(self, episode_id: str) -> int:
        """Normalize episode ID to integer.

        エピソードID（"010", "ep010", "EP-010" 等）を正規化して整数に変換。
        ForeshadowingIdentifier._episode_matches() と同様のロジック。

        Args:
            episode_id: Episode ID string.

        Returns:
            Episode number as integer.

        Raises:
            ValueError: If episode ID cannot be normalized.
        """
        match = self._EPISODE_PATTERN.search(episode_id)
        if not match:
            raise ValueError(f"Invalid episode ID format: {episode_id}")
        return int(match.group(1))

    def _calculate_episode_gap(self, from_episode: str, to_episode: str) -> int:
        """Calculate episode gap between two episodes.

        Args:
            from_episode: Starting episode ID.
            to_episode: Ending episode ID.

        Returns:
            Episode gap (to - from).
        """
        from_num = self._normalize_episode(from_episode)
        to_num = self._normalize_episode(to_episode)
        return to_num - from_num
