"""Foreshadowing manager.

伏線の状態遷移、Subtlety管理、可視性自動マッピング。
仕様: docs/specs/novel-generator-v2/04_ai-information-control.md Section 7
"""

from typing import Any

from src.core.models.ai_visibility import AIVisibilityLevel
from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingAIVisibility,
    ForeshadowingStatus,
)

# 有効な状態遷移マップ
# キー: 現在のステータス, 値: 遷移可能なステータスのセット
VALID_TRANSITIONS: dict[ForeshadowingStatus, set[ForeshadowingStatus]] = {
    ForeshadowingStatus.REGISTERED: {
        ForeshadowingStatus.REGISTERED,
        ForeshadowingStatus.PLANTED,
        ForeshadowingStatus.ABANDONED,  # 張る前に断念
    },
    ForeshadowingStatus.PLANTED: {
        ForeshadowingStatus.PLANTED,
        ForeshadowingStatus.REINFORCED,
        ForeshadowingStatus.REVEALED,
        ForeshadowingStatus.ABANDONED,  # 回収を断念
    },
    ForeshadowingStatus.REINFORCED: {
        ForeshadowingStatus.REINFORCED,
        ForeshadowingStatus.PLANTED,  # 巻き戻し可能
        ForeshadowingStatus.REVEALED,
        ForeshadowingStatus.ABANDONED,  # 回収を断念
    },
    ForeshadowingStatus.REVEALED: {
        ForeshadowingStatus.REVEALED,  # 自己遷移のみ
    },
    ForeshadowingStatus.ABANDONED: {
        ForeshadowingStatus.ABANDONED,  # 自己遷移のみ
        ForeshadowingStatus.REGISTERED,  # 復活して再計画
    },
}

# ステータス → 推奨可視性マップ
STATUS_VISIBILITY_MAP: dict[ForeshadowingStatus, AIVisibilityLevel] = {
    ForeshadowingStatus.REGISTERED: AIVisibilityLevel.HIDDEN,
    ForeshadowingStatus.PLANTED: AIVisibilityLevel.KNOW,
    ForeshadowingStatus.REINFORCED: AIVisibilityLevel.KNOW,
    ForeshadowingStatus.REVEALED: AIVisibilityLevel.USE,
    ForeshadowingStatus.ABANDONED: AIVisibilityLevel.HIDDEN,
}


def validate_status_transition(
    current: ForeshadowingStatus,
    target: ForeshadowingStatus,
) -> bool:
    """ステータス遷移が有効かどうかを検証する.

    Args:
        current: 現在のステータス
        target: 遷移先のステータス

    Returns:
        有効な遷移なら True
    """
    valid_targets = VALID_TRANSITIONS.get(current, set())
    return target in valid_targets


def get_recommended_visibility(status: ForeshadowingStatus) -> AIVisibilityLevel:
    """ステータスに基づく推奨可視性を取得する.

    Args:
        status: 伏線のステータス

    Returns:
        推奨される可視性レベル
    """
    return STATUS_VISIBILITY_MAP.get(status, AIVisibilityLevel.HIDDEN)


def get_visibility_from_subtlety(subtlety_level: int) -> AIVisibilityLevel:
    """Subtlety レベルから可視性を取得する.

    Subtlety（巧みさ）が高いほど、AIの認識を制限する。
    - 1-7: KNOW（内容認識、暗示可能）
    - 8-10: AWARE（存在のみ認識）

    Args:
        subtlety_level: Subtlety レベル（1-10）

    Returns:
        推奨される可視性レベル

    Raises:
        ValueError: 範囲外のレベル
    """
    if subtlety_level < 1 or subtlety_level > 10:
        raise ValueError(
            f"Subtlety level must be 1-10, got {subtlety_level}"
        )

    if subtlety_level >= 8:
        return AIVisibilityLevel.AWARE
    return AIVisibilityLevel.KNOW


class ForeshadowingManager:
    """伏線マネージャ.

    伏線の状態遷移と可視性管理を担当する。
    """

    def transition_status(
        self,
        foreshadowing: Foreshadowing,
        target_status: ForeshadowingStatus,
        update_visibility: bool = False,
    ) -> Foreshadowing:
        """伏線のステータスを遷移させる.

        Args:
            foreshadowing: 対象の伏線
            target_status: 遷移先のステータス
            update_visibility: 可視性も自動更新するか

        Returns:
            更新された伏線（新しいインスタンス）

        Raises:
            ValueError: 無効な遷移の場合
        """
        if not validate_status_transition(foreshadowing.status, target_status):
            raise ValueError(
                f"Invalid status transition: {foreshadowing.status} → {target_status}"
            )

        # 新しいデータで更新
        update_data: dict[str, Any] = {
            "status": target_status,
        }

        if update_visibility:
            new_visibility = self.get_effective_visibility(
                foreshadowing.model_copy(update={"status": target_status})
            )
            # ForeshadowingAIVisibility を更新
            new_ai_visibility = ForeshadowingAIVisibility(
                level=new_visibility.value,
                forbidden_keywords=foreshadowing.ai_visibility.forbidden_keywords,
                allowed_expressions=foreshadowing.ai_visibility.allowed_expressions,
            )
            update_data["ai_visibility"] = new_ai_visibility

        return foreshadowing.model_copy(update=update_data)

    def get_effective_visibility(
        self,
        foreshadowing: Foreshadowing,
    ) -> AIVisibilityLevel:
        """有効な可視性レベルを取得する.

        ステータスと Subtlety の両方を考慮し、より制限的な方を返す。
        ただし、revealed の場合は常に USE を返す。

        Args:
            foreshadowing: 対象の伏線

        Returns:
            有効な可視性レベル
        """
        # revealed は常に USE
        if foreshadowing.status == ForeshadowingStatus.REVEALED:
            return AIVisibilityLevel.USE

        # ステータスベースの可視性
        status_visibility = get_recommended_visibility(foreshadowing.status)

        # Subtlety ベースの可視性
        subtlety_visibility = get_visibility_from_subtlety(
            foreshadowing.subtlety_level
        )

        # より制限的な方（数値が小さい方）を返す
        return AIVisibilityLevel(
            min(status_visibility.value, subtlety_visibility.value)
        )

    def plant(self, foreshadowing: Foreshadowing) -> Foreshadowing:
        """伏線を張る（planted に遷移）.

        Args:
            foreshadowing: 対象の伏線

        Returns:
            更新された伏線
        """
        return self.transition_status(
            foreshadowing,
            ForeshadowingStatus.PLANTED,
            update_visibility=True,
        )

    def reinforce(self, foreshadowing: Foreshadowing) -> Foreshadowing:
        """伏線を強化する（reinforced に遷移）.

        Args:
            foreshadowing: 対象の伏線

        Returns:
            更新された伏線
        """
        return self.transition_status(
            foreshadowing,
            ForeshadowingStatus.REINFORCED,
            update_visibility=True,
        )

    def reveal(self, foreshadowing: Foreshadowing) -> Foreshadowing:
        """伏線を回収する（revealed に遷移）.

        Args:
            foreshadowing: 対象の伏線

        Returns:
            更新された伏線
        """
        return self.transition_status(
            foreshadowing,
            ForeshadowingStatus.REVEALED,
            update_visibility=True,
        )
