"""Tests for WorldSetting model."""

from datetime import date

from src.core.models.character import Phase
from src.core.models.world_setting import WorldSetting


class TestWorldSetting:
    """WorldSetting モデルのテスト."""

    def test_create_world_setting_minimal(self) -> None:
        """最小限のフィールドで世界観設定を作成できる."""
        ws = WorldSetting(
            name="魔法体系",
            category="Magic System",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        assert ws.type == "world_setting"
        assert ws.name == "魔法体系"
        assert ws.category == "Magic System"
        assert ws.phases == []
        assert ws.current_phase is None

    def test_create_world_setting_with_phases(self) -> None:
        """フェーズ付きで世界観設定を作成できる."""
        ws = WorldSetting(
            name="王国の歴史",
            category="History",
            phases=[
                Phase(name="建国期", episodes="1-10"),
                Phase(name="動乱期", episodes="11-20"),
            ],
            current_phase="建国期",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        assert len(ws.phases) == 2
        assert ws.current_phase == "建国期"

    def test_create_world_setting_with_sections(self) -> None:
        """セクション付きで世界観設定を作成できる."""
        ws = WorldSetting(
            name="大陸地理",
            category="Geography",
            sections={
                "概要": "この世界は3つの大陸からなる",
                "東大陸": "魔法文明が発達",
            },
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        assert "概要" in ws.sections
        assert "東大陸" in ws.sections

    def test_world_setting_to_dict(self) -> None:
        """世界観設定を辞書に変換できる."""
        ws = WorldSetting(
            name="組織",
            category="Organizations",
            tags=["faction", "guild"],
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        data = ws.model_dump()

        assert data["type"] == "world_setting"
        assert data["category"] == "Organizations"
