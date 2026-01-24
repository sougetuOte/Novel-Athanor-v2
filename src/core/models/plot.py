"""Plot models.

3階層のプロット（計画）を表現する Pydantic モデル。
"""

from typing import Literal

from pydantic import BaseModel, Field


class PlotBase(BaseModel):
    """プロットの基底クラス."""

    type: Literal["plot"] = "plot"
    work: str
    content: str = ""


class PlotL1(PlotBase):
    """全体プロット（L1）.

    作品全体の計画を表現する。
    """

    level: Literal["L1"] = "L1"
    logline: str = ""
    theme: str = ""
    three_act_structure: dict[str, str] = Field(default_factory=dict)
    character_arcs: list[str] = Field(default_factory=list)
    foreshadowing_master: list[str] = Field(default_factory=list)
    chapters: list[str] = Field(default_factory=list)  # L2へのリンク


class PlotL2(PlotBase):
    """章プロット（L2）.

    各章の計画を表現する。
    """

    level: Literal["L2"] = "L2"
    chapter_number: int
    chapter_name: str
    purpose: str = ""
    state_changes: list[str] = Field(default_factory=list)
    sequences: list[str] = Field(default_factory=list)  # L3へのリンク


class PlotL3(PlotBase):
    """シーケンスプロット（L3）.

    シーケンス（連続したシーン群）の計画を表現する。
    """

    level: Literal["L3"] = "L3"
    chapter_number: int
    sequence_number: int
    scenes: list[str] = Field(default_factory=list)
    pov: str = ""
    mood: str = ""
