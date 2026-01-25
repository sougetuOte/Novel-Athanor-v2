"""Style models.

文体ガイド（StyleGuide）と文体プロファイル（StyleProfile）のモデル。
仕様書 03_data-model.md および analysis-novel-athanor-datamodel.md に基づく実装。
"""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class POVType(str, Enum):
    """視点タイプ."""

    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"
    THIRD_PERSON_LIMITED = "third_person_limited"
    THIRD_PERSON_OMNISCIENT = "third_person_omniscient"


class TenseType(str, Enum):
    """時制タイプ."""

    PAST = "past"
    PRESENT = "present"


class DialogueStyle(BaseModel):
    """会話文のスタイル設定."""

    quote_style: str = "「」"
    inner_thought_style: str | None = None
    speaker_attribution: str | None = None  # "before", "after", "none"


class StyleGuide(BaseModel):
    """文体ガイド（定性分析）.

    執筆時のスタイル指針を定義する。
    ファイルパス: vault/{作品名}/_style_guides/style-guide.md
    """

    work: str
    pov: POVType
    tense: TenseType
    style_characteristics: list[str] = Field(default_factory=list)
    dialogue: DialogueStyle | None = None
    description_tendencies: list[str] = Field(default_factory=list)
    avoid_expressions: list[str] = Field(default_factory=list)
    notes: str | None = None
    created: date | None = None
    updated: date | None = None


class StyleProfile(BaseModel):
    """文体プロファイル（定量分析）.

    既存テキストから抽出した統計情報。
    ファイルパス: vault/{作品名}/_style_profiles/{作品名}.md
    """

    work: str
    avg_sentence_length: float | None = Field(default=None, gt=0)
    dialogue_ratio: float | None = Field(default=None, ge=0.0, le=1.0)
    ttr: float | None = Field(default=None, ge=0.0, le=1.0)  # Type-Token Ratio
    pos_ratios: dict[str, float] = Field(default_factory=dict)
    frequent_words: list[str] = Field(default_factory=list)
    sample_episodes: list[int] = Field(default_factory=list)
    analyzed_at: date | None = None

    @field_validator("pos_ratios")
    @classmethod
    def validate_pos_ratios(cls, v: dict[str, float]) -> dict[str, float]:
        """品詞比率の値を検証する."""
        for key, ratio in v.items():
            if ratio < 0.0 or ratio > 1.0:
                raise ValueError(f"POS ratio for '{key}' must be between 0.0 and 1.0")
        return v
