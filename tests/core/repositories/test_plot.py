"""Tests for PlotRepository."""

from pathlib import Path

import pytest

from src.core.models.plot import PlotL1, PlotL2, PlotL3
from src.core.repositories.plot import PlotRepository


class TestPlotRepository:
    """PlotRepository のテスト."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """テスト用の一時 vault を作成."""
        (tmp_path / "_plot").mkdir()
        (tmp_path / "_plot" / "L2_chapters").mkdir()
        (tmp_path / "_plot" / "L3_sequences").mkdir()
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> PlotRepository:
        """テスト用リポジトリを作成."""
        return PlotRepository(temp_vault)

    @pytest.fixture
    def sample_plot_l1(self, repo: PlotRepository) -> PlotL1:
        """サンプル L1 プロットを作成."""
        plot = PlotL1(
            work="test_work",
            content="Overall plot content",
            logline="Test logline",
            theme="Test theme",
            three_act_structure={
                "act1": "Setup",
                "act2": "Confrontation",
                "act3": "Resolution",
            },
            character_arcs=["Arc 1", "Arc 2"],
            foreshadowing_master=["Foreshadowing 1"],
            chapters=["Chapter 1", "Chapter 2"],
        )
        repo.create(plot)
        return plot

    @pytest.fixture
    def sample_plot_l2(self, repo: PlotRepository) -> PlotL2:
        """サンプル L2 プロットを作成."""
        plot = PlotL2(
            work="test_work",
            content="Chapter 1 plot content",
            chapter_number=1,
            chapter_name="First Chapter",
            purpose="Introduction",
            state_changes=["State change 1"],
            sequences=["Sequence 1", "Sequence 2"],
        )
        repo.create(plot)
        return plot

    @pytest.fixture
    def sample_plot_l3(self, repo: PlotRepository) -> PlotL3:
        """サンプル L3 プロットを作成."""
        # L3 requires parent directory
        seq_dir = repo.vault_root / "_plot" / "L3_sequences" / "01_First Chapter"
        seq_dir.mkdir(parents=True, exist_ok=True)

        plot = PlotL3(
            work="test_work",
            content="Sequence 1 content",
            chapter_number=1,
            sequence_number=1,
            scenes=["Scene 1", "Scene 2"],
            pov="Protagonist",
            mood="Tense",
        )
        repo.create(plot)
        return plot

    def test_create_and_read_l1(self, repo: PlotRepository) -> None:
        """L1 プロットを作成して読み込める."""
        plot = PlotL1(
            work="test_work",
            content="Test content",
            logline="Test logline",
        )

        repo.create(plot)
        retrieved = repo.read("L1")

        assert retrieved.level == "L1"
        assert retrieved.work == "test_work"
        assert retrieved.logline == "Test logline"

    def test_create_and_read_l2(self, repo: PlotRepository) -> None:
        """L2 プロットを作成して読み込める."""
        plot = PlotL2(
            work="test_work",
            chapter_number=1,
            chapter_name="Chapter One",
            purpose="Test purpose",
        )

        repo.create(plot)
        retrieved = repo.read("L2-1-Chapter One")

        assert retrieved.level == "L2"
        assert retrieved.chapter_number == 1
        assert retrieved.purpose == "Test purpose"

    def test_create_and_read_l3(self, repo: PlotRepository) -> None:
        """L3 プロットを作成して読み込める."""
        seq_dir = repo.vault_root / "_plot" / "L3_sequences" / "01_Chapter One"
        seq_dir.mkdir(parents=True, exist_ok=True)

        plot = PlotL3(
            work="test_work",
            chapter_number=1,
            sequence_number=1,
            pov="Hero",
        )

        repo.create(plot)
        retrieved = repo.read("L3-1-Chapter One-1")

        assert retrieved.level == "L3"
        assert retrieved.sequence_number == 1
        assert retrieved.pov == "Hero"

    def test_get_by_level_l1(
        self, repo: PlotRepository, sample_plot_l1: PlotL1
    ) -> None:
        """レベル L1 でフィルタリングできる."""
        plots = repo.get_by_level("L1")

        assert len(plots) == 1
        assert plots[0].level == "L1"

    def test_get_by_level_l2(
        self, repo: PlotRepository, sample_plot_l2: PlotL2
    ) -> None:
        """レベル L2 でフィルタリングできる."""
        plots = repo.get_by_level("L2")

        assert len(plots) == 1
        assert plots[0].level == "L2"

    def test_get_by_level_l3(
        self, repo: PlotRepository, sample_plot_l3: PlotL3
    ) -> None:
        """レベル L3 でフィルタリングできる."""
        plots = repo.get_by_level("L3")

        assert len(plots) == 1
        assert plots[0].level == "L3"

    def test_list_all(
        self,
        repo: PlotRepository,
        sample_plot_l1: PlotL1,
        sample_plot_l2: PlotL2,
        sample_plot_l3: PlotL3,
    ) -> None:
        """全プロットを取得できる."""
        plots = repo.list_all()

        # L1(1) + L2(1) + L3(1) = 3
        assert len(plots) >= 3
        levels = [p.level for p in plots]
        assert "L1" in levels
        assert "L2" in levels
        assert "L3" in levels

    def test_list_all_empty(self, repo: PlotRepository) -> None:
        """プロットがない場合は空リストを返す."""
        plots = repo.list_all()

        assert plots == []
