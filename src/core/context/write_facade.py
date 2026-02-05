"""L3 WriteFacade: Write operations facade for L4 agents.

This module provides a write-only facade that L4 agents use to persist
entities and update state. It complements ContextBuilder (read-only facade).
"""

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from src.core.models.character import Character
from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingStatus,
    TimelineEntry,
)
from src.core.models.world_setting import WorldSetting
from src.core.repositories.character import CharacterRepository
from src.core.repositories.foreshadowing import ForeshadowingRepository
from src.core.repositories.world_setting import WorldSettingRepository
from src.core.services.foreshadowing_manager import ForeshadowingManager

if TYPE_CHECKING:
    from src.core.models.style import StyleProfile


class WriteFacadeError(Exception):
    """WriteFacade base exception."""

    pass


class WriteOperationError(WriteFacadeError):
    """Write operation execution error."""

    def __init__(self, message: str, *, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause


class DependencyNotConfiguredError(WriteFacadeError):
    """Error raised when required dependency is not configured."""

    def __init__(self, dependency_name: str, method_name: str):
        super().__init__(
            f"{dependency_name} is not configured. Required for {method_name}()."
        )
        self.dependency_name = dependency_name
        self.method_name = method_name


class WriteFacade:
    """L3 write facade for L4 agents.

    Provides write operations to persist entities and update state.
    Complements ContextBuilder (read-only facade).
    """

    def __init__(
        self,
        vault_root: Path,
        *,
        work_name: str = "",
        foreshadowing_repository: ForeshadowingRepository | None = None,
        foreshadowing_manager: ForeshadowingManager | None = None,
        character_repository: CharacterRepository | None = None,
        world_setting_repository: WorldSettingRepository | None = None,
    ) -> None:
        """Initialize WriteFacade.

        Args:
            vault_root: Root directory of the vault
            work_name: Name of the work (optional, default: "")
            foreshadowing_repository: Foreshadowing repository (optional)
            foreshadowing_manager: Foreshadowing manager service (optional)
            character_repository: Character repository (optional)
            world_setting_repository: World setting repository (optional)
        """
        self._vault_root = vault_root
        self._work_name = work_name
        self._foreshadowing_repository = foreshadowing_repository
        self._foreshadowing_manager = foreshadowing_manager
        self._character_repository = character_repository
        self._world_setting_repository = world_setting_repository

    def update_foreshadowing_status(
        self,
        foreshadowing_id: str,
        new_status: ForeshadowingStatus,
        *,
        episode_id: str | None = None,
        update_visibility: bool = True,
    ) -> Foreshadowing:
        """Update foreshadowing status with L2 validation.

        Args:
            foreshadowing_id: Foreshadowing ID
            new_status: Target status
            episode_id: Episode ID that triggered the transition (for timeline)
            update_visibility: Whether to auto-update visibility (default: True)

        Returns:
            Updated Foreshadowing instance

        Raises:
            DependencyNotConfiguredError: If repository or manager is not configured
            EntityNotFoundError: If foreshadowing not found
            ValueError: If invalid status transition
            RepositoryError: If persistence fails
        """
        if self._foreshadowing_repository is None:
            raise DependencyNotConfiguredError(
                "foreshadowing_repository", "update_foreshadowing_status"
            )
        if self._foreshadowing_manager is None:
            raise DependencyNotConfiguredError(
                "foreshadowing_manager", "update_foreshadowing_status"
            )

        # Read current entity
        current = self._foreshadowing_repository.read(foreshadowing_id)

        # Transition status using L2 ForeshadowingManager
        updated = self._foreshadowing_manager.transition_status(
            current, new_status, update_visibility=update_visibility
        )

        # Persist to repository
        self._foreshadowing_repository.update(updated)

        return updated

    def add_foreshadowing_event(
        self,
        foreshadowing_id: str,
        event: TimelineEntry,
    ) -> Foreshadowing:
        """Add event to foreshadowing timeline.

        Args:
            foreshadowing_id: Foreshadowing ID
            event: Timeline event to add

        Returns:
            Updated Foreshadowing instance

        Raises:
            DependencyNotConfiguredError: If repository is not configured
            EntityNotFoundError: If foreshadowing not found
            ValidationError: If event validation fails
            RepositoryError: If persistence fails
        """
        if self._foreshadowing_repository is None:
            raise DependencyNotConfiguredError(
                "foreshadowing_repository", "add_foreshadowing_event"
            )

        # Read current entity
        current = self._foreshadowing_repository.read(foreshadowing_id)

        # Add event to timeline
        from datetime import date

        from src.core.models.foreshadowing import TimelineInfo

        if current.timeline is None:
            # Create new timeline if it doesn't exist
            new_timeline = TimelineInfo(
                registered_at=date.today(),
                events=[event],
            )
        else:
            # Add to existing timeline
            new_timeline = TimelineInfo(
                registered_at=current.timeline.registered_at,
                events=current.timeline.events + [event],
            )

        # Update entity with new timeline
        updated = current.model_copy(update={"timeline": new_timeline})

        # Persist
        self._foreshadowing_repository.update(updated)

        return updated

    def save_character(self, character: Character) -> Path:
        """Save character entity.

        If character exists, updates it; otherwise creates it.

        Args:
            character: Character entity to save

        Returns:
            Path to saved file

        Raises:
            DependencyNotConfiguredError: If repository is not configured
            ValidationError: If character validation fails
            RepositoryError: If persistence fails
        """
        if self._character_repository is None:
            raise DependencyNotConfiguredError(
                "character_repository", "save_character"
            )

        if self._character_repository.exists(character.name):
            # Update existing character
            self._character_repository.update(character)
            return self._character_repository._get_path(character.name)
        else:
            # Create new character
            return self._character_repository.create(character)

    def save_world_setting(self, world_setting: WorldSetting) -> Path:
        """Save world setting entity.

        If world setting exists, updates it; otherwise creates it.

        Args:
            world_setting: WorldSetting entity to save

        Returns:
            Path to saved file

        Raises:
            DependencyNotConfiguredError: If repository is not configured
            ValidationError: If world setting validation fails
            RepositoryError: If persistence fails
        """
        if self._world_setting_repository is None:
            raise DependencyNotConfiguredError(
                "world_setting_repository", "save_world_setting"
            )

        if self._world_setting_repository.exists(world_setting.name):
            # Update existing world setting
            self._world_setting_repository.update(world_setting)
            return self._world_setting_repository._get_path(world_setting.name)
        else:
            # Create new world setting
            return self._world_setting_repository.create(world_setting)

    def save_summary(
        self,
        level: Literal["L1", "L2", "L3"],
        content: str,
        *,
        work: str = "",
        chapter_number: int | None = None,
        chapter_name: str | None = None,
        sequence_number: int | None = None,
    ) -> Path:
        """Save summary.

        Note: SummaryRepository is not yet implemented (C3).
        This method uses VaultPathResolver and direct file write.

        Args:
            level: Summary level ("L1", "L2", "L3")
            content: Summary content
            work: Work name
            chapter_number: Chapter number (required for L2/L3)
            chapter_name: Chapter name (required for L2/L3)
            sequence_number: Sequence number (required for L3)

        Returns:
            Path to saved file

        Raises:
            WriteFacadeError: If required arguments are missing
            ValueError: If invalid level or argument combination
            OSError: If file write fails
        """
        # Validate arguments
        if level == "L2" or level == "L3":
            if chapter_number is None or chapter_name is None:
                raise WriteFacadeError(
                    f"{level} summary requires chapter_number and chapter_name"
                )
        if level == "L3":
            if sequence_number is None:
                raise WriteFacadeError("L3 summary requires sequence_number")

        # Resolve path using VaultPathResolver
        from src.core.vault.path_resolver import VaultPathResolver

        resolver = VaultPathResolver(self._vault_root)
        path = resolver.resolve_summary(
            level=level,
            chapter_number=chapter_number,
            chapter_name=chapter_name,
            sequence_number=sequence_number,
        )

        # Write atomically
        self._atomic_write(path, content)

        return path

    def save_style_profile(self, profile: "StyleProfile") -> Path:
        """Save style profile.

        Note: StyleProfileRepository is not yet implemented.
        This method saves to vault/{work_name}/_style_profiles/{work}.md.

        Args:
            profile: StyleProfile entity to save

        Returns:
            Path to saved file

        Raises:
            WriteFacadeError: If vault_root is not configured
            ValidationError: If profile validation fails
            OSError: If file write fails
        """
        # Determine directory path
        if self._work_name:
            style_profiles_dir = self._vault_root / self._work_name / "_style_profiles"
        else:
            style_profiles_dir = self._vault_root / "_style_profiles"
        path = style_profiles_dir / f"{profile.work}.md"

        # Serialize profile to YAML frontmatter + content
        import yaml

        frontmatter = profile.model_dump(mode="json", exclude_none=True)
        content = "---\n"
        content += yaml.dump(frontmatter, allow_unicode=True)
        content += "---\n"
        content += "\n# Style Profile\n\n"
        content += f"Auto-generated style profile for {profile.work}\n"

        # Write atomically
        self._atomic_write(path, content)

        return path

    def get_all_characters(
        self,
        *,
        include_all_phases: bool = True,
    ) -> list[Character]:
        """Get all characters without phase filter.

        For consistency checks (Consistency Agent).

        Args:
            include_all_phases: If True, no phase filter is applied (default)

        Returns:
            List of all characters

        Raises:
            DependencyNotConfiguredError: If repository is not configured
        """
        if self._character_repository is None:
            raise DependencyNotConfiguredError(
                "character_repository", "get_all_characters"
            )

        return self._character_repository.list_all()

    def get_all_world_settings(
        self,
        *,
        include_all_phases: bool = True,
    ) -> list[WorldSetting]:
        """Get all world settings without phase filter.

        For consistency checks (Consistency Agent).

        Args:
            include_all_phases: If True, no phase filter is applied (default)

        Returns:
            List of all world settings

        Raises:
            DependencyNotConfiguredError: If repository is not configured
        """
        if self._world_setting_repository is None:
            raise DependencyNotConfiguredError(
                "world_setting_repository", "get_all_world_settings"
            )

        return self._world_setting_repository.list_all()

    def get_all_foreshadowings(
        self,
        *,
        status_filter: ForeshadowingStatus | None = None,
    ) -> list[Foreshadowing]:
        """Get all foreshadowings.

        For consistency checks (Consistency Agent).

        Args:
            status_filter: If specified, only return foreshadowings with this status

        Returns:
            List of foreshadowings

        Raises:
            DependencyNotConfiguredError: If repository is not configured
        """
        if self._foreshadowing_repository is None:
            raise DependencyNotConfiguredError(
                "foreshadowing_repository", "get_all_foreshadowings"
            )

        all_foreshadowings = self._foreshadowing_repository.list_all()

        if status_filter is not None:
            return [fs for fs in all_foreshadowings if fs.status == status_filter]

        return all_foreshadowings

    def _atomic_write(self, path: Path, content: str) -> None:
        """Write file atomically using write-to-temp-then-rename pattern.

        Args:
            path: Target file path
            content: Content to write

        Raises:
            OSError: If file write fails
        """
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path.write_text(content, encoding="utf-8")
            tmp_path.replace(path)
        except OSError:
            if tmp_path.exists():
                tmp_path.unlink()
            raise
