"""Tests for WriteFacade (L3 write facade)."""

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from src.core.context.write_facade import (
    DependencyNotConfiguredError,
    WriteFacade,
    WriteFacadeError,
    WriteOperationError,
)
from src.core.models.character import Character
from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingSeed,
    ForeshadowingStatus,
    ForeshadowingType,
    TimelineEntry,
    TimelineInfo,
)
from src.core.models.world_setting import WorldSetting
from src.core.repositories.base import EntityNotFoundError
from src.core.repositories.character import CharacterRepository
from src.core.repositories.foreshadowing import ForeshadowingRepository
from src.core.repositories.world_setting import WorldSettingRepository
from src.core.services.foreshadowing_manager import ForeshadowingManager

if TYPE_CHECKING:
    pass


# --- Exception tests ---


def test_write_facade_error_hierarchy():
    """Test that exception hierarchy is correct."""
    assert issubclass(WriteFacadeError, Exception)
    assert issubclass(WriteOperationError, WriteFacadeError)
    assert issubclass(DependencyNotConfiguredError, WriteFacadeError)


def test_write_operation_error_with_cause():
    """Test WriteOperationError stores cause."""
    cause = ValueError("Original error")
    error = WriteOperationError("Write failed", cause=cause)
    assert str(error) == "Write failed"
    assert error.cause is cause


def test_dependency_not_configured_error():
    """Test DependencyNotConfiguredError message format."""
    error = DependencyNotConfiguredError("foreshadowing_repository", "update_foreshadowing_status")
    assert "foreshadowing_repository" in str(error)
    assert "update_foreshadowing_status" in str(error)
    assert error.dependency_name == "foreshadowing_repository"
    assert error.method_name == "update_foreshadowing_status"


# --- Initialization tests ---


def test_write_facade_init_minimal(tmp_path: Path):
    """Test WriteFacade initialization with minimal arguments."""
    facade = WriteFacade(vault_root=tmp_path)
    assert facade is not None


def test_write_facade_init_with_all_dependencies(tmp_path: Path):
    """Test WriteFacade initialization with all dependencies."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")
    char_repo = CharacterRepository(tmp_path)
    ws_repo = WorldSettingRepository(tmp_path)
    fs_manager = ForeshadowingManager()

    facade = WriteFacade(
        vault_root=tmp_path,
        work_name="test_work",
        foreshadowing_repository=fs_repo,
        foreshadowing_manager=fs_manager,
        character_repository=char_repo,
        world_setting_repository=ws_repo,
    )
    assert facade is not None


# --- Dependency check tests ---


def test_update_foreshadowing_status_without_repository(tmp_path: Path):
    """Test update_foreshadowing_status raises error when repository is not configured."""
    facade = WriteFacade(vault_root=tmp_path)

    with pytest.raises(DependencyNotConfiguredError) as exc_info:
        facade.update_foreshadowing_status("FS-01", ForeshadowingStatus.PLANTED)

    assert exc_info.value.dependency_name == "foreshadowing_repository"
    assert exc_info.value.method_name == "update_foreshadowing_status"


def test_update_foreshadowing_status_without_manager(tmp_path: Path):
    """Test update_foreshadowing_status raises error when manager is not configured."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")
    facade = WriteFacade(
        vault_root=tmp_path,
        foreshadowing_repository=fs_repo,
        # foreshadowing_manager is None
    )

    with pytest.raises(DependencyNotConfiguredError) as exc_info:
        facade.update_foreshadowing_status("FS-01", ForeshadowingStatus.PLANTED)

    assert exc_info.value.dependency_name == "foreshadowing_manager"


def test_add_foreshadowing_event_without_repository(tmp_path: Path):
    """Test add_foreshadowing_event raises error when repository is not configured."""
    facade = WriteFacade(vault_root=tmp_path)
    event = TimelineEntry(
        episode="EP-01",
        type=ForeshadowingStatus.PLANTED,
        date=date.today(),
        expression="A mysterious hint",
        subtlety=7,
    )

    with pytest.raises(DependencyNotConfiguredError) as exc_info:
        facade.add_foreshadowing_event("FS-01", event)

    assert exc_info.value.dependency_name == "foreshadowing_repository"


def test_save_character_without_repository(tmp_path: Path):
    """Test save_character raises error when repository is not configured."""
    facade = WriteFacade(vault_root=tmp_path)
    character = Character(name="Alice", created=date.today(), updated=date.today())

    with pytest.raises(DependencyNotConfiguredError) as exc_info:
        facade.save_character(character)

    assert exc_info.value.dependency_name == "character_repository"


def test_save_world_setting_without_repository(tmp_path: Path):
    """Test save_world_setting raises error when repository is not configured."""
    facade = WriteFacade(vault_root=tmp_path)
    ws = WorldSetting(name="Magic System", category="Magic", created=date.today(), updated=date.today())

    with pytest.raises(DependencyNotConfiguredError) as exc_info:
        facade.save_world_setting(ws)

    assert exc_info.value.dependency_name == "world_setting_repository"


def test_get_all_characters_without_repository(tmp_path: Path):
    """Test get_all_characters raises error when repository is not configured."""
    facade = WriteFacade(vault_root=tmp_path)

    with pytest.raises(DependencyNotConfiguredError) as exc_info:
        facade.get_all_characters()

    assert exc_info.value.dependency_name == "character_repository"


def test_get_all_world_settings_without_repository(tmp_path: Path):
    """Test get_all_world_settings raises error when repository is not configured."""
    facade = WriteFacade(vault_root=tmp_path)

    with pytest.raises(DependencyNotConfiguredError) as exc_info:
        facade.get_all_world_settings()

    assert exc_info.value.dependency_name == "world_setting_repository"


def test_get_all_foreshadowings_without_repository(tmp_path: Path):
    """Test get_all_foreshadowings raises error when repository is not configured."""
    facade = WriteFacade(vault_root=tmp_path)

    with pytest.raises(DependencyNotConfiguredError) as exc_info:
        facade.get_all_foreshadowings()

    assert exc_info.value.dependency_name == "foreshadowing_repository"


# --- update_foreshadowing_status tests ---


def test_update_foreshadowing_status_success(tmp_path: Path):
    """Test successful foreshadowing status transition."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")
    fs_manager = ForeshadowingManager()

    # Create initial foreshadowing
    fs = Foreshadowing(
        id="FS-01-test",
        title="Test Foreshadow",
        fs_type=ForeshadowingType.CHARACTER_SECRET,
        status=ForeshadowingStatus.REGISTERED,
        subtlety_level=5,
        seed=ForeshadowingSeed(content="Test seed"),
    )
    fs_repo.create(fs)

    facade = WriteFacade(
        vault_root=tmp_path,
        work_name="test_work",
        foreshadowing_repository=fs_repo,
        foreshadowing_manager=fs_manager,
    )

    # Transition to PLANTED
    updated = facade.update_foreshadowing_status(
        "FS-01-test",
        ForeshadowingStatus.PLANTED,
        episode_id="EP-01",
    )

    assert updated.status == ForeshadowingStatus.PLANTED


def test_update_foreshadowing_status_invalid_transition(tmp_path: Path):
    """Test invalid status transition raises ValueError."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")
    fs_manager = ForeshadowingManager()

    # Create initial foreshadowing
    fs = Foreshadowing(
        id="FS-01-test",
        title="Test Foreshadow",
        fs_type=ForeshadowingType.CHARACTER_SECRET,
        status=ForeshadowingStatus.REGISTERED,
        subtlety_level=5,
        seed=ForeshadowingSeed(content="Test seed"),
    )
    fs_repo.create(fs)

    facade = WriteFacade(
        vault_root=tmp_path,
        work_name="test_work",
        foreshadowing_repository=fs_repo,
        foreshadowing_manager=fs_manager,
    )

    # Try to transition directly to REVEALED (should fail)
    with pytest.raises(ValueError):
        facade.update_foreshadowing_status(
            "FS-01-test",
            ForeshadowingStatus.REVEALED,
        )


def test_update_foreshadowing_status_nonexistent_id(tmp_path: Path):
    """Test update_foreshadowing_status with nonexistent ID raises error."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")
    fs_manager = ForeshadowingManager()

    facade = WriteFacade(
        vault_root=tmp_path,
        work_name="test_work",
        foreshadowing_repository=fs_repo,
        foreshadowing_manager=fs_manager,
    )

    with pytest.raises(EntityNotFoundError):
        facade.update_foreshadowing_status(
            "FS-NONEXISTENT",
            ForeshadowingStatus.PLANTED,
        )


# --- add_foreshadowing_event tests ---


def test_add_foreshadowing_event_success(tmp_path: Path):
    """Test adding event to foreshadowing timeline."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")

    # Create initial foreshadowing
    fs = Foreshadowing(
        id="FS-01-test",
        title="Test Foreshadow",
        fs_type=ForeshadowingType.CHARACTER_SECRET,
        status=ForeshadowingStatus.PLANTED,
        subtlety_level=5,
        seed=ForeshadowingSeed(content="Test seed"),
        timeline=TimelineInfo(registered_at=date.today(), events=[]),
    )
    fs_repo.create(fs)

    facade = WriteFacade(
        vault_root=tmp_path,
        work_name="test_work",
        foreshadowing_repository=fs_repo,
    )

    event = TimelineEntry(
        episode="EP-01",
        type=ForeshadowingStatus.PLANTED,
        date=date.today(),
        expression="A mysterious hint",
        subtlety=7,
    )

    updated = facade.add_foreshadowing_event("FS-01-test", event)

    assert len(updated.timeline.events) == 1
    assert updated.timeline.events[0].episode == "EP-01"


def test_add_foreshadowing_event_creates_timeline(tmp_path: Path):
    """Test adding event to foreshadowing without timeline creates timeline."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")

    # Create foreshadowing without timeline
    fs = Foreshadowing(
        id="FS-01-test",
        title="Test Foreshadow",
        fs_type=ForeshadowingType.CHARACTER_SECRET,
        status=ForeshadowingStatus.PLANTED,
        subtlety_level=5,
        seed=ForeshadowingSeed(content="Test seed"),
        timeline=None,
    )
    fs_repo.create(fs)

    facade = WriteFacade(
        vault_root=tmp_path,
        work_name="test_work",
        foreshadowing_repository=fs_repo,
    )

    event = TimelineEntry(
        episode="EP-01",
        type=ForeshadowingStatus.PLANTED,
        date=date.today(),
        expression="A mysterious hint",
        subtlety=7,
    )

    updated = facade.add_foreshadowing_event("FS-01-test", event)

    assert updated.timeline is not None
    assert len(updated.timeline.events) == 1


# --- save_character tests ---


def test_save_character_create(tmp_path: Path):
    """Test saving new character creates file."""
    char_repo = CharacterRepository(tmp_path)
    facade = WriteFacade(
        vault_root=tmp_path,
        character_repository=char_repo,
    )

    character = Character(name="Alice", created=date.today(), updated=date.today())
    path = facade.save_character(character)

    assert path.exists()
    assert path.name == "Alice.md"


def test_save_character_update(tmp_path: Path):
    """Test saving existing character updates file."""
    char_repo = CharacterRepository(tmp_path)
    facade = WriteFacade(
        vault_root=tmp_path,
        character_repository=char_repo,
    )

    # Create initial character
    character = Character(name="Alice", created=date.today(), updated=date.today())
    char_repo.create(character)

    # Update character with tags
    updated_character = Character(name="Alice", created=date.today(), updated=date.today(), tags=["updated"])
    path = facade.save_character(updated_character)

    assert path.exists()
    loaded = char_repo.read("Alice")
    assert "updated" in loaded.tags


# --- save_world_setting tests ---


def test_save_world_setting_create(tmp_path: Path):
    """Test saving new world setting creates file."""
    ws_repo = WorldSettingRepository(tmp_path)
    facade = WriteFacade(
        vault_root=tmp_path,
        world_setting_repository=ws_repo,
    )

    ws = WorldSetting(name="Magic System", category="Magic", created=date.today(), updated=date.today())
    path = facade.save_world_setting(ws)

    assert path.exists()
    assert path.name == "Magic System.md"


def test_save_world_setting_update(tmp_path: Path):
    """Test saving existing world setting updates file."""
    ws_repo = WorldSettingRepository(tmp_path)
    facade = WriteFacade(
        vault_root=tmp_path,
        world_setting_repository=ws_repo,
    )

    # Create initial world setting
    ws = WorldSetting(name="Magic System", category="Magic", created=date.today(), updated=date.today())
    ws_repo.create(ws)

    # Update world setting with tags
    updated_ws = WorldSetting(name="Magic System", category="Magic", created=date.today(), updated=date.today(), tags=["updated"])
    path = facade.save_world_setting(updated_ws)

    assert path.exists()
    loaded = ws_repo.read("Magic System")
    assert "updated" in loaded.tags


# --- save_summary tests ---


def test_save_summary_l1(tmp_path: Path):
    """Test saving L1 summary."""
    facade = WriteFacade(vault_root=tmp_path, work_name="test_work")

    path = facade.save_summary(
        level="L1",
        content="Overall story summary",
        work="test_work",
    )

    assert path.exists()
    assert path.read_text(encoding="utf-8") == "Overall story summary"


def test_save_summary_l2(tmp_path: Path):
    """Test saving L2 summary."""
    facade = WriteFacade(vault_root=tmp_path, work_name="test_work")

    path = facade.save_summary(
        level="L2",
        content="Chapter summary",
        work="test_work",
        chapter_number=1,
        chapter_name="Chapter One",
    )

    assert path.exists()
    assert "Chapter summary" in path.read_text(encoding="utf-8")


def test_save_summary_l3(tmp_path: Path):
    """Test saving L3 summary."""
    facade = WriteFacade(vault_root=tmp_path, work_name="test_work")

    path = facade.save_summary(
        level="L3",
        content="Scene summary",
        work="test_work",
        chapter_number=1,
        chapter_name="Chapter One",
        sequence_number=1,
    )

    assert path.exists()
    assert "Scene summary" in path.read_text(encoding="utf-8")


def test_save_summary_l2_missing_chapter_info(tmp_path: Path):
    """Test save_summary L2 with missing chapter info raises error."""
    facade = WriteFacade(vault_root=tmp_path, work_name="test_work")

    with pytest.raises(WriteFacadeError):
        facade.save_summary(
            level="L2",
            content="Chapter summary",
            work="test_work",
            # Missing chapter_number and chapter_name
        )


def test_save_summary_l3_missing_sequence_number(tmp_path: Path):
    """Test save_summary L3 with missing sequence_number raises error."""
    facade = WriteFacade(vault_root=tmp_path, work_name="test_work")

    with pytest.raises(WriteFacadeError):
        facade.save_summary(
            level="L3",
            content="Scene summary",
            work="test_work",
            chapter_number=1,
            chapter_name="Chapter One",
            # Missing sequence_number
        )


# --- _atomic_write tests ---


def test_atomic_write_creates_parent_directory(tmp_path: Path):
    """Test _atomic_write creates parent directory if it doesn't exist."""
    facade = WriteFacade(vault_root=tmp_path)

    target_path = tmp_path / "nested" / "dir" / "file.txt"
    facade._atomic_write(target_path, "test content")

    assert target_path.exists()
    assert target_path.read_text(encoding="utf-8") == "test content"


def test_atomic_write_overwrites_existing_file(tmp_path: Path):
    """Test _atomic_write overwrites existing file."""
    facade = WriteFacade(vault_root=tmp_path)

    target_path = tmp_path / "file.txt"
    target_path.write_text("old content", encoding="utf-8")

    facade._atomic_write(target_path, "new content")

    assert target_path.read_text(encoding="utf-8") == "new content"


# --- get_all_* tests ---


def test_get_all_characters(tmp_path: Path):
    """Test get_all_characters returns all characters."""
    char_repo = CharacterRepository(tmp_path)
    facade = WriteFacade(
        vault_root=tmp_path,
        character_repository=char_repo,
    )

    # Create test characters
    char_repo.create(Character(name="Alice", created=date.today(), updated=date.today()))
    char_repo.create(Character(name="Bob", created=date.today(), updated=date.today()))

    characters = facade.get_all_characters()

    assert len(characters) == 2
    names = {c.name for c in characters}
    assert "Alice" in names
    assert "Bob" in names


def test_get_all_world_settings(tmp_path: Path):
    """Test get_all_world_settings returns all world settings."""
    ws_repo = WorldSettingRepository(tmp_path)
    facade = WriteFacade(
        vault_root=tmp_path,
        world_setting_repository=ws_repo,
    )

    # Create test world settings
    ws_repo.create(WorldSetting(name="Magic System", category="Magic", created=date.today(), updated=date.today()))
    ws_repo.create(WorldSetting(name="Geography", category="Geography", created=date.today(), updated=date.today()))

    world_settings = facade.get_all_world_settings()

    assert len(world_settings) == 2
    names = {ws.name for ws in world_settings}
    assert "Magic System" in names
    assert "Geography" in names


def test_get_all_foreshadowings(tmp_path: Path):
    """Test get_all_foreshadowings returns all foreshadowings."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")
    facade = WriteFacade(
        vault_root=tmp_path,
        work_name="test_work",
        foreshadowing_repository=fs_repo,
    )

    # Create test foreshadowings
    fs1 = Foreshadowing(
        id="FS-01-test",
        title="Test 1",
        fs_type=ForeshadowingType.CHARACTER_SECRET,
        status=ForeshadowingStatus.REGISTERED,
        subtlety_level=5,
        seed=ForeshadowingSeed(content="Seed 1"),
    )
    fs2 = Foreshadowing(
        id="FS-02-test",
        title="Test 2",
        fs_type=ForeshadowingType.PLOT_TWIST,
        status=ForeshadowingStatus.PLANTED,
        subtlety_level=7,
        seed=ForeshadowingSeed(content="Seed 2"),
    )
    fs_repo.create(fs1)
    fs_repo.create(fs2)

    foreshadowings = facade.get_all_foreshadowings()

    assert len(foreshadowings) == 2


def test_get_all_foreshadowings_with_status_filter(tmp_path: Path):
    """Test get_all_foreshadowings with status filter."""
    fs_repo = ForeshadowingRepository(tmp_path, work_name="test_work")
    facade = WriteFacade(
        vault_root=tmp_path,
        work_name="test_work",
        foreshadowing_repository=fs_repo,
    )

    # Create test foreshadowings with different statuses
    fs1 = Foreshadowing(
        id="FS-01-test",
        title="Test 1",
        fs_type=ForeshadowingType.CHARACTER_SECRET,
        status=ForeshadowingStatus.REGISTERED,
        subtlety_level=5,
        seed=ForeshadowingSeed(content="Seed 1"),
    )
    fs2 = Foreshadowing(
        id="FS-02-test",
        title="Test 2",
        fs_type=ForeshadowingType.PLOT_TWIST,
        status=ForeshadowingStatus.PLANTED,
        subtlety_level=7,
        seed=ForeshadowingSeed(content="Seed 2"),
    )
    fs_repo.create(fs1)
    fs_repo.create(fs2)

    planted = facade.get_all_foreshadowings(status_filter=ForeshadowingStatus.PLANTED)

    assert len(planted) == 1
    assert planted[0].id == "FS-02-test"
