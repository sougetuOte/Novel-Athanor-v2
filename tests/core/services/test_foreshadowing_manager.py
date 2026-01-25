"""Tests for foreshadowing manager.

伏線状態遷移、Subtlety管理、可視性マッピングのテスト。
"""

import pytest

from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingAIVisibility,
    ForeshadowingStatus,
    ForeshadowingType,
)
from src.core.services.foreshadowing_manager import (
    ForeshadowingManager,
    get_recommended_visibility,
    get_visibility_from_subtlety,
    validate_status_transition,
)


def _create_foreshadowing(
    id: str = "FS-001",
    title: str = "テスト伏線",
    fs_type: ForeshadowingType = ForeshadowingType.PLOT_TWIST,
    status: ForeshadowingStatus = ForeshadowingStatus.REGISTERED,
    subtlety_level: int = 5,
    ai_visibility_level: int = 0,
) -> Foreshadowing:
    """テスト用の Foreshadowing を作成するヘルパー."""
    return Foreshadowing(
        id=id,
        title=title,
        fs_type=fs_type,
        status=status,
        subtlety_level=subtlety_level,
        ai_visibility=ForeshadowingAIVisibility(level=ai_visibility_level),
    )


class TestValidateStatusTransition:
    """validate_status_transition 関数のテスト."""

    def test_registered_to_planted(self) -> None:
        """registered → planted は有効."""
        assert validate_status_transition(
            ForeshadowingStatus.REGISTERED,
            ForeshadowingStatus.PLANTED,
        ) is True

    def test_planted_to_reinforced(self) -> None:
        """planted → reinforced は有効."""
        assert validate_status_transition(
            ForeshadowingStatus.PLANTED,
            ForeshadowingStatus.REINFORCED,
        ) is True

    def test_reinforced_to_revealed(self) -> None:
        """reinforced → revealed は有効."""
        assert validate_status_transition(
            ForeshadowingStatus.REINFORCED,
            ForeshadowingStatus.REVEALED,
        ) is True

    def test_planted_to_revealed(self) -> None:
        """planted → revealed は有効（直接回収）."""
        assert validate_status_transition(
            ForeshadowingStatus.PLANTED,
            ForeshadowingStatus.REVEALED,
        ) is True

    def test_reinforced_to_planted(self) -> None:
        """reinforced → planted は有効（巻き戻し）."""
        assert validate_status_transition(
            ForeshadowingStatus.REINFORCED,
            ForeshadowingStatus.PLANTED,
        ) is True

    def test_registered_to_revealed_invalid(self) -> None:
        """registered → revealed は無効（張らずに回収できない）."""
        assert validate_status_transition(
            ForeshadowingStatus.REGISTERED,
            ForeshadowingStatus.REVEALED,
        ) is False

    def test_revealed_to_any_invalid(self) -> None:
        """revealed → 任意 は無効（回収後は変更不可）."""
        assert validate_status_transition(
            ForeshadowingStatus.REVEALED,
            ForeshadowingStatus.PLANTED,
        ) is False

    def test_same_status_valid(self) -> None:
        """同じステータスへの遷移は有効."""
        assert validate_status_transition(
            ForeshadowingStatus.PLANTED,
            ForeshadowingStatus.PLANTED,
        ) is True


class TestGetRecommendedVisibility:
    """get_recommended_visibility 関数のテスト."""

    def test_registered_returns_hidden(self) -> None:
        """registered は HIDDEN を推奨."""
        result = get_recommended_visibility(ForeshadowingStatus.REGISTERED)
        assert result == AIVisibilityLevel.HIDDEN

    def test_planted_returns_know(self) -> None:
        """planted は KNOW を推奨."""
        result = get_recommended_visibility(ForeshadowingStatus.PLANTED)
        assert result == AIVisibilityLevel.KNOW

    def test_reinforced_returns_know(self) -> None:
        """reinforced は KNOW を推奨."""
        result = get_recommended_visibility(ForeshadowingStatus.REINFORCED)
        assert result == AIVisibilityLevel.KNOW

    def test_revealed_returns_use(self) -> None:
        """revealed は USE を推奨."""
        result = get_recommended_visibility(ForeshadowingStatus.REVEALED)
        assert result == AIVisibilityLevel.USE


class TestGetVisibilityFromSubtlety:
    """get_visibility_from_subtlety 関数のテスト."""

    def test_low_subtlety_returns_know(self) -> None:
        """subtlety 1-3 は KNOW を返す."""
        for level in [1, 2, 3]:
            result = get_visibility_from_subtlety(level)
            assert result == AIVisibilityLevel.KNOW

    def test_medium_subtlety_returns_know(self) -> None:
        """subtlety 4-7 は KNOW を返す."""
        for level in [4, 5, 6, 7]:
            result = get_visibility_from_subtlety(level)
            assert result == AIVisibilityLevel.KNOW

    def test_high_subtlety_returns_aware(self) -> None:
        """subtlety 8-10 は AWARE を返す."""
        for level in [8, 9, 10]:
            result = get_visibility_from_subtlety(level)
            assert result == AIVisibilityLevel.AWARE

    def test_invalid_subtlety_raises_error(self) -> None:
        """範囲外の subtlety はエラー."""
        with pytest.raises(ValueError):
            get_visibility_from_subtlety(0)
        with pytest.raises(ValueError):
            get_visibility_from_subtlety(11)


class TestForeshadowingManager:
    """ForeshadowingManager クラスのテスト."""

    def test_create_manager(self) -> None:
        """マネージャを作成できる."""
        manager = ForeshadowingManager()
        assert manager is not None

    def test_transition_status(self) -> None:
        """ステータスを遷移できる."""
        fs = _create_foreshadowing(status=ForeshadowingStatus.REGISTERED)
        manager = ForeshadowingManager()

        result = manager.transition_status(fs, ForeshadowingStatus.PLANTED)

        assert result.status == ForeshadowingStatus.PLANTED

    def test_transition_invalid_raises_error(self) -> None:
        """無効な遷移はエラー."""
        fs = _create_foreshadowing(status=ForeshadowingStatus.REGISTERED)
        manager = ForeshadowingManager()

        with pytest.raises(ValueError, match="Invalid status transition"):
            manager.transition_status(fs, ForeshadowingStatus.REVEALED)

    def test_get_effective_visibility(self) -> None:
        """有効な可視性を取得できる."""
        fs = _create_foreshadowing(
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=5,
        )
        manager = ForeshadowingManager()

        result = manager.get_effective_visibility(fs)

        # planted + subtlety 5 → KNOW
        assert result == AIVisibilityLevel.KNOW

    def test_get_effective_visibility_high_subtlety(self) -> None:
        """高 subtlety は AWARE を返す."""
        fs = _create_foreshadowing(
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=9,
        )
        manager = ForeshadowingManager()

        result = manager.get_effective_visibility(fs)

        # planted だが subtlety 9 → AWARE（より制限的な方）
        assert result == AIVisibilityLevel.AWARE

    def test_get_effective_visibility_revealed(self) -> None:
        """revealed は subtlety に関係なく USE."""
        fs = _create_foreshadowing(
            status=ForeshadowingStatus.REVEALED,
            subtlety_level=10,
        )
        manager = ForeshadowingManager()

        result = manager.get_effective_visibility(fs)

        # revealed は常に USE
        assert result == AIVisibilityLevel.USE

    def test_update_visibility_on_transition(self) -> None:
        """遷移時に可視性を自動更新できる."""
        fs = _create_foreshadowing(
            status=ForeshadowingStatus.REGISTERED,
            ai_visibility_level=0,
        )
        manager = ForeshadowingManager()

        result = manager.transition_status(
            fs,
            ForeshadowingStatus.PLANTED,
            update_visibility=True,
        )

        assert result.status == ForeshadowingStatus.PLANTED
        assert result.ai_visibility.level == 2  # KNOW

    def test_plant_foreshadowing(self) -> None:
        """伏線を張るショートカット."""
        fs = _create_foreshadowing(status=ForeshadowingStatus.REGISTERED)
        manager = ForeshadowingManager()

        result = manager.plant(fs)

        assert result.status == ForeshadowingStatus.PLANTED

    def test_reveal_foreshadowing(self) -> None:
        """伏線を回収するショートカット."""
        fs = _create_foreshadowing(status=ForeshadowingStatus.PLANTED)
        manager = ForeshadowingManager()

        result = manager.reveal(fs)

        assert result.status == ForeshadowingStatus.REVEALED
        assert result.ai_visibility.level == 3  # USE
