"""Settings model.

Work-level configuration settings.
"""

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Work-level configuration settings.

    This model contains work-level configuration such as title, author,
    and default AI visibility settings.

    Attributes:
        work_id: Work identifier
        title: Work title
        author: Author name
        genre: Genre (optional)
        target_audience: Target audience (optional)
        episode_naming: Episode naming convention (default: "Episode {n}")
        volumes_enabled: Whether volume structure is used
        default_ai_visibility: Default AI visibility level (0=HIDDEN per Secure by Default)
    """

    work_id: str
    title: str
    author: str
    genre: str = ""
    target_audience: str = ""
    episode_naming: str = "Episode {n}"
    volumes_enabled: bool = False
    default_ai_visibility: int = Field(default=0, ge=0, le=3)
