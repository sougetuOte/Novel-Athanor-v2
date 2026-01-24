"""Summary models.

3階層のサマリ（実績）を表現する Pydantic モデル。
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class SummaryBase(BaseModel):
    """サマリの基底クラス."""

    type: Literal["summary"] = "summary"
    work: str
    content: str = ""
    updated: date


class SummaryL1(SummaryBase):
    """全体サマリ（L1）.

    作品全体の実績を表現する。
    """

    level: Literal["L1"] = "L1"
    overall_progress: str = ""
    completed_chapters: list[str] = Field(default_factory=list)
    key_events: list[str] = Field(default_factory=list)


class SummaryL2(SummaryBase):
    """章サマリ（L2）.

    各章の実績を表現する。
    """

    level: Literal["L2"] = "L2"
    chapter_number: int
    chapter_name: str
    actual_content: str = ""
    deviations_from_plot: list[str] = Field(default_factory=list)


class SummaryL3(SummaryBase):
    """シーケンスサマリ（L3）.

    シーケンスの実績を表現する。
    """

    level: Literal["L3"] = "L3"
    chapter_number: int
    sequence_number: int
    episode_summaries: list[str] = Field(default_factory=list)
