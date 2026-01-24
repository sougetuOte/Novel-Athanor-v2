"""Tests for Plot models."""

from src.core.models.plot import PlotBase, PlotL1, PlotL2, PlotL3


class TestPlotL1:
    """PlotL1 モデルのテスト."""

    def test_create_plot_l1_minimal(self) -> None:
        """最小限のフィールドでL1プロットを作成できる."""
        plot = PlotL1(work="テスト作品")

        assert plot.type == "plot"
        assert plot.level == "L1"
        assert plot.work == "テスト作品"
        assert plot.logline == ""
        assert plot.theme == ""

    def test_create_plot_l1_full(self) -> None:
        """全フィールドを指定してL1プロットを作成できる."""
        plot = PlotL1(
            work="テスト作品",
            logline="勇者が魔王を倒す物語",
            theme="成長と犠牲",
            three_act_structure={
                "act1": "日常から冒険へ",
                "act2": "試練と成長",
                "act3": "最終決戦",
            },
            character_arcs=["主人公: 臆病→勇敢"],
            foreshadowing_master=["伏線1", "伏線2"],
            chapters=["chapter_01", "chapter_02"],
            content="全体プロット詳細...",
        )

        assert plot.logline == "勇者が魔王を倒す物語"
        assert len(plot.three_act_structure) == 3
        assert len(plot.chapters) == 2


class TestPlotL2:
    """PlotL2 モデルのテスト."""

    def test_create_plot_l2(self) -> None:
        """L2プロットを作成できる."""
        plot = PlotL2(
            work="テスト作品",
            chapter_number=1,
            chapter_name="旅立ち",
            purpose="主人公の日常と旅立ちの動機を描く",
            state_changes=["主人公が村を出る決意をする"],
            sequences=["seq_001", "seq_002"],
        )

        assert plot.level == "L2"
        assert plot.chapter_number == 1
        assert plot.chapter_name == "旅立ち"
        assert len(plot.sequences) == 2


class TestPlotL3:
    """PlotL3 モデルのテスト."""

    def test_create_plot_l3(self) -> None:
        """L3プロットを作成できる."""
        plot = PlotL3(
            work="テスト作品",
            chapter_number=1,
            sequence_number=1,
            scenes=["scene_1", "scene_2", "scene_3"],
            pov="主人公",
            mood="希望と不安",
        )

        assert plot.level == "L3"
        assert plot.chapter_number == 1
        assert plot.sequence_number == 1
        assert plot.pov == "主人公"
        assert len(plot.scenes) == 3

    def test_plot_to_dict(self) -> None:
        """プロットを辞書に変換できる."""
        plot = PlotL1(work="テスト", logline="テストログライン")

        data = plot.model_dump()

        assert data["type"] == "plot"
        assert data["level"] == "L1"
        assert data["logline"] == "テストログライン"
