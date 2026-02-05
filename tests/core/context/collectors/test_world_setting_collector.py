"""Tests for WorldSettingCollector (L3-4-2d).

TDD cycle for WorldSetting context collection with Phase filtering.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from src.core.context.collectors.world_setting_collector import (
    WorldSettingCollector,
    WorldSettingContext,
)
from src.core.context.lazy_loader import FileLazyLoader, LazyLoadResult, LoadPriority
from src.core.context.phase_filter import WorldSettingPhaseFilter
from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.scene_resolver import SceneResolver


@pytest.fixture
def temp_vault(tmp_path: Path) -> Path:
    """Create temporary vault structure."""
    vault = tmp_path / "vault"
    vault.mkdir()

    # world directory
    world_dir = vault / "world"
    world_dir.mkdir()

    return vault


@pytest.fixture
def mock_loader() -> Mock:
    """Create mock FileLazyLoader."""
    return Mock(spec=FileLazyLoader)


@pytest.fixture
def mock_resolver() -> Mock:
    """Create mock SceneResolver."""
    return Mock(spec=SceneResolver)


@pytest.fixture
def phase_filter() -> WorldSettingPhaseFilter:
    """Create WorldSettingPhaseFilter."""
    return WorldSettingPhaseFilter(phase_order=["initial", "arc_1", "finale"])


@pytest.fixture
def collector(
    temp_vault: Path,
    mock_loader: Mock,
    mock_resolver: Mock,
    phase_filter: WorldSettingPhaseFilter,
) -> WorldSettingCollector:
    """Create WorldSettingCollector."""
    return WorldSettingCollector(
        vault_root=temp_vault,
        loader=mock_loader,
        resolver=mock_resolver,
        phase_filter=phase_filter,
    )


# --- WorldSettingContext Tests ---


class TestWorldSettingContext:
    """Test WorldSettingContext dataclass."""

    def test_get_names_empty(self):
        """Empty context returns empty list."""
        context = WorldSettingContext()
        assert context.get_names() == []

    def test_get_names_single(self):
        """Single setting returns one name."""
        context = WorldSettingContext(settings={"魔法体系": "content"})
        assert context.get_names() == ["魔法体系"]

    def test_get_setting_exists(self):
        """get_setting returns content for existing name."""
        context = WorldSettingContext(settings={"魔法体系": "content"})
        assert context.get_setting("魔法体系") == "content"

    def test_get_setting_not_exists(self):
        """get_setting returns None for non-existent name."""
        context = WorldSettingContext()
        assert context.get_setting("魔法体系") is None


# --- WorldSettingCollector Tests ---


class TestWorldSettingCollector:
    """Test WorldSettingCollector."""

    def test_collect_single_setting(
        self,
        collector: WorldSettingCollector,
        mock_resolver: Mock,
        mock_loader: Mock,
        temp_vault: Path,
    ):
        """Test Case 1: collect() single setting."""
        # Arrange
        scene = SceneIdentifier(episode_id="010", current_phase="initial")

        setting_path = temp_vault / "world" / "魔法体系.md"
        mock_resolver.identify_world_settings.return_value = [setting_path]

        content = """---
name: 魔法体系
category: Magic System
created: 2026-01-26
updated: 2026-01-26
---

# 概要
魔法の基本原理
"""
        mock_loader.load.return_value = LazyLoadResult.ok(content)

        # Act
        result = collector.collect(scene)

        # Assert
        assert "魔法体系" in result.settings
        assert result.warnings == []
        mock_resolver.identify_world_settings.assert_called_once_with(scene)
        # Check loader call (path separators may vary by OS)
        actual_path = mock_loader.load.call_args[0][0]
        assert actual_path.replace("\\", "/") == "world/魔法体系.md"
        assert mock_loader.load.call_args[0][1] == LoadPriority.REQUIRED

    def test_collect_multiple_settings(
        self,
        collector: WorldSettingCollector,
        mock_resolver: Mock,
        mock_loader: Mock,
        temp_vault: Path,
    ):
        """Test Case 2: collect() multiple settings."""
        # Arrange
        scene = SceneIdentifier(episode_id="010", current_phase="arc_1")

        setting_paths = [
            temp_vault / "world" / "魔法体系.md",
            temp_vault / "world" / "地理" / "王都.md",
        ]
        mock_resolver.identify_world_settings.return_value = setting_paths

        contents = {
            "world/魔法体系.md": """---
name: 魔法体系
category: Magic System
created: 2026-01-26
updated: 2026-01-26
---

# 概要
魔法の基本原理
""",
            "world/地理/王都.md": """---
name: 王都
category: Geography
created: 2026-01-26
updated: 2026-01-26
---

# 概要
王国の首都
""",
        }

        def load_side_effect(path: str, priority):
            normalized = path.replace("\\", "/")
            return LazyLoadResult.ok(contents[normalized])

        mock_loader.load.side_effect = load_side_effect

        # Act
        result = collector.collect(scene)

        # Assert
        assert "魔法体系" in result.settings
        assert "王都" in result.settings
        assert result.warnings == []
        assert mock_loader.load.call_count == 2

    def test_collect_no_settings(
        self,
        collector: WorldSettingCollector,
        mock_resolver: Mock,
    ):
        """Test Case 3: collect() no settings - empty context."""
        # Arrange
        scene = SceneIdentifier(episode_id="010")
        mock_resolver.identify_world_settings.return_value = []

        # Act
        result = collector.collect(scene)

        # Assert
        assert result.settings == {}
        assert result.warnings == []

    def test_collect_with_phase_filter(
        self,
        collector: WorldSettingCollector,
        mock_resolver: Mock,
        mock_loader: Mock,
        temp_vault: Path,
    ):
        """Test Case 4: collect() with Phase filtering."""
        # Arrange
        scene = SceneIdentifier(episode_id="010", current_phase="initial")

        setting_path = temp_vault / "world" / "魔法体系.md"
        mock_resolver.identify_world_settings.return_value = [setting_path]

        content = """---
name: 魔法体系
category: Magic System
phases:
  - name: initial
    episodes: "010"
  - name: arc_1
    episodes: "020"
created: 2026-01-26
updated: 2026-01-26
---

# 概要
基本情報
"""
        mock_loader.load.return_value = LazyLoadResult.ok(content)

        # Act
        result = collector.collect(scene)

        # Assert
        assert "魔法体系" in result.settings
        # Phase filter should be applied
        assert "initial" in result.settings["魔法体系"]
        # arc_1 should be excluded
        assert result.warnings == []

    def test_collect_without_phase(
        self,
        collector: WorldSettingCollector,
        mock_resolver: Mock,
        mock_loader: Mock,
        temp_vault: Path,
    ):
        """Test Case 5: collect() without Phase - all information."""
        # Arrange
        scene = SceneIdentifier(episode_id="010", current_phase=None)

        setting_path = temp_vault / "world" / "魔法体系.md"
        mock_resolver.identify_world_settings.return_value = [setting_path]

        content = """---
name: 魔法体系
category: Magic System
created: 2026-01-26
updated: 2026-01-26
---

# 概要
基本情報
"""
        mock_loader.load.return_value = LazyLoadResult.ok(content)

        # Act
        result = collector.collect(scene)

        # Assert
        assert "魔法体系" in result.settings
        # Should include category when no phase filter
        assert "Magic System" in result.settings["魔法体系"]

    def test_collect_subdirectory(
        self,
        collector: WorldSettingCollector,
        mock_resolver: Mock,
        mock_loader: Mock,
        temp_vault: Path,
    ):
        """Test Case 6: collect() subdirectory - hierarchy support."""
        # Arrange
        scene = SceneIdentifier(episode_id="010")

        setting_path = temp_vault / "world" / "地理" / "王都.md"
        mock_resolver.identify_world_settings.return_value = [setting_path]

        content = """---
name: 王都
category: Geography
created: 2026-01-26
updated: 2026-01-26
---

# 概要
王国の首都
"""
        mock_loader.load.return_value = LazyLoadResult.ok(content)

        # Act
        result = collector.collect(scene)

        # Assert
        assert "王都" in result.settings

    def test_parse_world_setting(
        self,
        collector: WorldSettingCollector,
        temp_vault: Path,
    ):
        """Test Case 7: _parse_world_setting() parsing."""
        # Arrange
        path = temp_vault / "world" / "test.md"
        content = """---
name: テスト設定
category: Test Category
phases:
  - name: initial
    episodes: "010"
created: 2026-01-26
updated: 2026-01-27
tags: [test, sample]
---

# セクション1
内容1

# セクション2
内容2
"""

        # Act
        setting, error = collector._parse_world_setting(path, content)

        # Assert
        assert error is None
        assert setting is not None
        assert setting.name == "テスト設定"
        assert setting.category == "Test Category"
        assert len(setting.phases) == 1
        assert setting.phases[0].name == "initial"
        assert "セクション1" in setting.sections
        assert "セクション2" in setting.sections
        assert setting.tags == ["test", "sample"]

    def test_collect_as_string(
        self,
        collector: WorldSettingCollector,
        mock_resolver: Mock,
        mock_loader: Mock,
        temp_vault: Path,
    ):
        """Test Case 8: collect_as_string() integration."""
        # Arrange
        scene = SceneIdentifier(episode_id="010")

        setting_paths = [
            temp_vault / "world" / "設定1.md",
            temp_vault / "world" / "設定2.md",
        ]
        mock_resolver.identify_world_settings.return_value = setting_paths

        contents = {
            "world/設定1.md": """---
name: 設定1
category: Cat1
created: 2026-01-26
updated: 2026-01-26
---

# 概要
説明1
""",
            "world/設定2.md": """---
name: 設定2
category: Cat2
created: 2026-01-26
updated: 2026-01-26
---

# 概要
説明2
""",
        }

        def load_side_effect(path: str, priority):
            normalized = path.replace("\\", "/")
            return LazyLoadResult.ok(contents[normalized])

        mock_loader.load.side_effect = load_side_effect

        # Act
        result = collector.collect_as_string(scene)

        # Assert
        assert result is not None
        assert "設定1" in result
        assert "設定2" in result
        assert "---" in result  # separator

    def test_load_failure_warning(
        self,
        collector: WorldSettingCollector,
        mock_resolver: Mock,
        mock_loader: Mock,
        temp_vault: Path,
    ):
        """Test Case 9: load failure adds warning."""
        # Arrange
        scene = SceneIdentifier(episode_id="010")

        setting_path = temp_vault / "world" / "missing.md"
        mock_resolver.identify_world_settings.return_value = [setting_path]

        mock_loader.load.return_value = LazyLoadResult.fail("File not found")

        # Act
        result = collector.collect(scene)

        # Assert
        assert result.settings == {}
        assert len(result.warnings) == 1
        assert "世界観設定読み込み失敗" in result.warnings[0]
