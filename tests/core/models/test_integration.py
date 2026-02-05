"""Integration tests for all models."""

from datetime import date

import yaml

from src.core.models import (
    Character,
    Episode,
    Phase,
    PlotL1,
    PlotL2,
    SummaryL1,
    WorldSetting,
)


class TestModelJsonRoundTrip:
    """モデルの JSON 往復テスト."""

    def test_episode_json_roundtrip(self) -> None:
        """Episode を JSON に変換して復元できる."""
        original = Episode(
            work="テスト作品",
            episode_number=1,
            title="第一話",
            status="draft",
            tags=["action"],
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
            body="本文です。",
        )

        json_str = original.model_dump_json()
        restored = Episode.model_validate_json(json_str)

        assert restored.work == original.work
        assert restored.episode_number == original.episode_number
        assert restored.title == original.title
        assert restored.tags == original.tags

    def test_character_json_roundtrip(self) -> None:
        """Character を JSON に変換して復元できる."""
        original = Character(
            name="主人公",
            phases=[Phase(name="序盤", episodes="1-10")],
            current_phase="序盤",
            tags=["hero"],
            sections={"基本情報": "テスト"},
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        json_str = original.model_dump_json()
        restored = Character.model_validate_json(json_str)

        assert restored.name == original.name
        assert restored.current_phase == original.current_phase
        assert len(restored.phases) == len(original.phases)

    def test_plot_json_roundtrip(self) -> None:
        """PlotL1 を JSON に変換して復元できる."""
        original = PlotL1(
            work="テスト作品",
            logline="勇者が魔王を倒す",
            theme="成長",
            chapters=["chapter_01"],
        )

        json_str = original.model_dump_json()
        restored = PlotL1.model_validate_json(json_str)

        assert restored.work == original.work
        assert restored.logline == original.logline


class TestModelDictConversion:
    """モデルの辞書変換テスト."""

    def test_episode_dict_roundtrip(self) -> None:
        """Episode を辞書に変換して復元できる."""
        original = Episode(
            work="テスト",
            episode_number=1,
            title="第一話",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        data = original.model_dump()
        restored = Episode.model_validate(data)

        assert restored == original

    def test_world_setting_dict_roundtrip(self) -> None:
        """WorldSetting を辞書に変換して復元できる."""
        original = WorldSetting(
            name="魔法体系",
            category="Magic System",
            sections={"概要": "魔法の説明"},
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        data = original.model_dump()
        restored = WorldSetting.model_validate(data)

        assert restored.name == original.name
        assert restored.sections == original.sections


class TestModelYamlCompatibility:
    """モデルの YAML 互換性テスト."""

    def test_episode_yaml_roundtrip(self) -> None:
        """Episode を YAML 形式で往復できる."""
        original = Episode(
            work="テスト",
            episode_number=1,
            title="第一話",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        # model -> dict -> yaml -> dict -> model
        data = original.model_dump(mode="json")  # date を文字列に変換
        yaml_str = yaml.dump(data, allow_unicode=True)
        loaded = yaml.safe_load(yaml_str)
        restored = Episode.model_validate(loaded)

        assert restored.work == original.work
        assert restored.episode_number == original.episode_number

    def test_summary_yaml_roundtrip(self) -> None:
        """SummaryL1 を YAML 形式で往復できる."""
        original = SummaryL1(
            work="テスト",
            updated=date(2026, 1, 24),
            overall_progress="進行中",
            key_events=["イベント1", "イベント2"],
        )

        data = original.model_dump(mode="json")
        yaml_str = yaml.dump(data, allow_unicode=True)
        loaded = yaml.safe_load(yaml_str)
        restored = SummaryL1.model_validate(loaded)

        assert restored.work == original.work
        assert restored.key_events == original.key_events


class TestModelRelations:
    """モデル間の関連テスト."""

    def test_plot_hierarchy(self) -> None:
        """Plot の階層関係が正しく表現できる."""
        l1 = PlotL1(
            work="テスト",
            chapters=["chapter_01", "chapter_02"],
        )
        l2 = PlotL2(
            work="テスト",
            chapter_number=1,
            chapter_name="第一章",
            sequences=["seq_001"],
        )

        # L1 から L2 への参照が論理的に成立
        assert "chapter_01" in l1.chapters
        assert l2.chapter_number == 1

    def test_character_phase_consistency(self) -> None:
        """Character のフェーズ整合性をテスト."""
        char = Character(
            name="主人公",
            phases=[
                Phase(name="序盤", episodes="1-10"),
                Phase(name="中盤", episodes="11-20"),
            ],
            current_phase="序盤",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        # current_phase が phases に存在するか確認
        phase_names = [p.name for p in char.phases]
        assert char.current_phase in phase_names
