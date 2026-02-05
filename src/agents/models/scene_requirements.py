"""Scene requirements model for L4 agent pipeline."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from src.core.context.scene_identifier import SceneIdentifier


class SceneRequirements(BaseModel):
    """シーン要件モデル.

    L4 エージェントパイプラインに渡すシーン生成要件を定義する。

    Attributes:
        episode_id: エピソードID（必須、空文字不可）
        sequence_id: シーケンスID（オプション）
        chapter_id: チャプターID（オプション）
        current_phase: 現在のフェーズ（オプション）
        word_count: 目標文字数（デフォルト: 3000、正の整数）
        pov: 視点（デフォルト: "三人称限定視点"）
        mood: 雰囲気・トーン（オプション）
        special_instructions: 特別な指示（オプション）
    """

    episode_id: str = Field(..., min_length=1)
    sequence_id: str | None = None
    chapter_id: str | None = None
    current_phase: str | None = None
    word_count: int = Field(default=3000, gt=0)
    pov: str = "三人称限定視点"
    mood: str | None = None
    special_instructions: str | None = None

    @field_validator("episode_id")
    @classmethod
    def validate_episode_id(cls, v: str) -> str:
        """episode_id の検証."""
        if not v or not v.strip():
            raise ValueError("episode_id must not be empty")
        return v

    def to_scene_identifier(self) -> SceneIdentifier:
        """SceneIdentifier に変換する.

        Returns:
            SceneIdentifier インスタンス
        """
        return SceneIdentifier(
            episode_id=self.episode_id,
            sequence_id=self.sequence_id,
            chapter_id=self.chapter_id,
            current_phase=self.current_phase,
        )
