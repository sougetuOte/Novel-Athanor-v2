"""Data persistence repositories."""

from src.core.repositories.base import (
    BaseRepository,
    EntityExistsError,
    EntityNotFoundError,
    RepositoryError,
)
from src.core.repositories.character import CharacterRepository
from src.core.repositories.episode import EpisodeRepository
from src.core.repositories.world_setting import WorldSettingRepository

__all__ = [
    "BaseRepository",
    "CharacterRepository",
    "EntityExistsError",
    "EntityNotFoundError",
    "EpisodeRepository",
    "RepositoryError",
    "WorldSettingRepository",
]
