"""Data persistence repositories."""

from src.core.repositories.ai_visibility import AIVisibilityRepository
from src.core.repositories.base import (
    BaseRepository,
    EntityExistsError,
    EntityNotFoundError,
    RepositoryError,
)
from src.core.repositories.character import CharacterRepository
from src.core.repositories.episode import EpisodeRepository
from src.core.repositories.foreshadowing import ForeshadowingRepository
from src.core.repositories.plot import PlotRepository
from src.core.repositories.settings import SettingsRepository
from src.core.repositories.style import StyleGuideRepository, StyleProfileRepository
from src.core.repositories.summary import SummaryRepository
from src.core.repositories.world_setting import WorldSettingRepository

__all__ = [
    "AIVisibilityRepository",
    "BaseRepository",
    "CharacterRepository",
    "EntityExistsError",
    "EntityNotFoundError",
    "EpisodeRepository",
    "ForeshadowingRepository",
    "PlotRepository",
    "RepositoryError",
    "SettingsRepository",
    "StyleGuideRepository",
    "StyleProfileRepository",
    "SummaryRepository",
    "WorldSettingRepository",
]
