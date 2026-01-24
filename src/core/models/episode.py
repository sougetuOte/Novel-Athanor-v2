"""Episode model.

エピソード（本文）を表現する Pydantic モデル。
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Episode(BaseModel):
    """エピソード（本文）モデル."""

    type: Literal["episode"] = "episode"
    work: str
    episode_number: int = Field(ge=1)
    title: str
    sequence: str | None = None
    chapter: str | None = None
    status: Literal["draft", "complete", "published"] = "draft"
    word_count: int = Field(default=0, ge=0)
    created: date
    updated: date
    tags: list[str] = Field(default_factory=list)

    # 本文（frontmatter 外）
    body: str = ""
