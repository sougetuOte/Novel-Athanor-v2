"""Tests for WorldSettingRepository."""

from datetime import date
from pathlib import Path

import pytest

from src.core.models.character import Phase
from src.core.models.world_setting import WorldSetting
from src.core.repositories.world_setting import WorldSettingRepository


class TestWorldSettingRepository:
    """WorldSettingRepository のテスト."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """テスト用の一時 vault を作成."""
        (tmp_path / "world").mkdir()
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> WorldSettingRepository:
        """WorldSettingRepository を作成."""
        return WorldSettingRepository(temp_vault)

    @pytest.fixture
    def sample_world_setting(self) -> WorldSetting:
        """サンプル世界観設定を作成."""
        return WorldSetting(
            name="魔法体系",
            category="Magic System",
            phases=[
                Phase(name="序盤", episodes="1-10"),
                Phase(name="中盤", episodes="11-20"),
            ],
            current_phase="序盤",
            tags=["magic", "core"],
            sections={"概要": "この世界の魔法体系について"},
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

    def test_list_all(
        self, repo: WorldSettingRepository, sample_world_setting: WorldSetting
    ) -> None:
        """list_all で全世界観設定を取得できる."""
        repo.create(sample_world_setting)
        ws2 = WorldSetting(
            name="地理",
            category="Geography",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )
        repo.create(ws2)

        result = repo.list_all()
        assert len(result) == 2
        names = [ws.name for ws in result]
        assert "魔法体系" in names
        assert "地理" in names

    def test_list_all_empty(self, repo: WorldSettingRepository) -> None:
        """空の場合は空リストを返す."""
        result = repo.list_all()
        assert result == []

    def test_get_by_category(
        self, repo: WorldSettingRepository, sample_world_setting: WorldSetting
    ) -> None:
        """カテゴリでフィルタリングできる."""
        repo.create(sample_world_setting)
        ws2 = WorldSetting(
            name="地理",
            category="Geography",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )
        repo.create(ws2)

        magic_settings = repo.get_by_category("Magic System")
        assert len(magic_settings) == 1
        assert magic_settings[0].name == "魔法体系"

    def test_get_by_tag(
        self, repo: WorldSettingRepository, sample_world_setting: WorldSetting
    ) -> None:
        """タグでフィルタリングできる."""
        repo.create(sample_world_setting)
        ws2 = WorldSetting(
            name="地理",
            category="Geography",
            tags=["geography"],
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )
        repo.create(ws2)

        core_settings = repo.get_by_tag("core")
        assert len(core_settings) == 1
        assert core_settings[0].name == "魔法体系"

    def test_update_phase(
        self, repo: WorldSettingRepository, sample_world_setting: WorldSetting
    ) -> None:
        """フェーズを更新できる."""
        repo.create(sample_world_setting)

        repo.update_phase("魔法体系", "中盤")

        updated = repo.read("魔法体系")
        assert updated.current_phase == "中盤"

    def test_update_phase_invalid_raises_error(
        self, repo: WorldSettingRepository, sample_world_setting: WorldSetting
    ) -> None:
        """存在しないフェーズへの更新はエラー."""
        repo.create(sample_world_setting)

        with pytest.raises(ValueError, match="Unknown phase"):
            repo.update_phase("魔法体系", "存在しないフェーズ")
