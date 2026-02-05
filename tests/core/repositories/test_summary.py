"""Tests for SummaryRepository."""

from datetime import date
from pathlib import Path

import pytest

from src.core.models.summary import SummaryL1, SummaryL2, SummaryL3
from src.core.repositories.summary import SummaryRepository


class TestSummaryRepository:
    """SummaryRepository のテスト."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """テスト用の一時 vault を作成."""
        (tmp_path / "_summary").mkdir()
        (tmp_path / "_summary" / "L2_chapters").mkdir()
        (tmp_path / "_summary" / "L3_sequences").mkdir()
        return tmp_path

    @pytest.fixture
    def repo(self, temp_vault: Path) -> SummaryRepository:
        """テスト用リポジトリを作成."""
        return SummaryRepository(temp_vault)

    @pytest.fixture
    def sample_summary_l1(self, repo: SummaryRepository) -> SummaryL1:
        """サンプル L1 サマリを作成."""
        summary = SummaryL1(
            work="test_work",
            content="Overall summary content",
            updated=date(2026, 2, 5),
            overall_progress="50% complete",
            completed_chapters=["Chapter 1", "Chapter 2"],
            key_events=["Event 1", "Event 2"],
        )
        repo.create(summary)
        return summary

    @pytest.fixture
    def sample_summary_l2(self, repo: SummaryRepository) -> SummaryL2:
        """サンプル L2 サマリを作成."""
        summary = SummaryL2(
            work="test_work",
            content="Chapter 1 summary content",
            updated=date(2026, 2, 5),
            chapter_number=1,
            chapter_name="First Chapter",
            actual_content="What actually happened",
            deviations_from_plot=["Deviation 1"],
        )
        repo.create(summary)
        return summary

    @pytest.fixture
    def sample_summary_l3(self, repo: SummaryRepository) -> SummaryL3:
        """サンプル L3 サマリを作成."""
        # L3 requires parent directory
        seq_dir = repo.vault_root / "_summary" / "L3_sequences" / "01_First Chapter"
        seq_dir.mkdir(parents=True, exist_ok=True)

        summary = SummaryL3(
            work="test_work",
            content="Sequence 1 content",
            updated=date(2026, 2, 5),
            chapter_number=1,
            sequence_number=1,
            episode_summaries=["Episode 1 summary", "Episode 2 summary"],
        )
        repo.create(summary)
        return summary

    def test_create_and_read_l1(self, repo: SummaryRepository) -> None:
        """L1 サマリを作成して読み込める."""
        summary = SummaryL1(
            work="test_work",
            content="Test content",
            updated=date(2026, 2, 5),
            overall_progress="Testing",
        )

        repo.create(summary)
        retrieved = repo.read("L1")

        assert retrieved.level == "L1"
        assert retrieved.work == "test_work"
        assert retrieved.overall_progress == "Testing"

    def test_create_and_read_l2(self, repo: SummaryRepository) -> None:
        """L2 サマリを作成して読み込める."""
        summary = SummaryL2(
            work="test_work",
            updated=date(2026, 2, 5),
            chapter_number=1,
            chapter_name="Chapter One",
            actual_content="Test content",
        )

        repo.create(summary)
        retrieved = repo.read("L2-1-Chapter One")

        assert retrieved.level == "L2"
        assert retrieved.chapter_number == 1
        assert retrieved.actual_content == "Test content"

    def test_create_and_read_l3(self, repo: SummaryRepository) -> None:
        """L3 サマリを作成して読み込める."""
        seq_dir = repo.vault_root / "_summary" / "L3_sequences" / "01_Chapter One"
        seq_dir.mkdir(parents=True, exist_ok=True)

        summary = SummaryL3(
            work="test_work",
            updated=date(2026, 2, 5),
            chapter_number=1,
            sequence_number=1,
            episode_summaries=["Summary 1"],
        )

        repo.create(summary)
        retrieved = repo.read("L3-1-Chapter One-1")

        assert retrieved.level == "L3"
        assert retrieved.sequence_number == 1
        assert len(retrieved.episode_summaries) == 1

    def test_get_by_level_l1(
        self, repo: SummaryRepository, sample_summary_l1: SummaryL1
    ) -> None:
        """レベル L1 でフィルタリングできる."""
        summaries = repo.get_by_level("L1")

        assert len(summaries) == 1
        assert summaries[0].level == "L1"

    def test_get_by_level_l2(
        self, repo: SummaryRepository, sample_summary_l2: SummaryL2
    ) -> None:
        """レベル L2 でフィルタリングできる."""
        summaries = repo.get_by_level("L2")

        assert len(summaries) == 1
        assert summaries[0].level == "L2"

    def test_get_by_level_l3(
        self, repo: SummaryRepository, sample_summary_l3: SummaryL3
    ) -> None:
        """レベル L3 でフィルタリングできる."""
        summaries = repo.get_by_level("L3")

        assert len(summaries) == 1
        assert summaries[0].level == "L3"

    def test_list_all(
        self,
        repo: SummaryRepository,
        sample_summary_l1: SummaryL1,
        sample_summary_l2: SummaryL2,
        sample_summary_l3: SummaryL3,
    ) -> None:
        """全サマリを取得できる."""
        summaries = repo.list_all()

        # L1(1) + L2(1) + L3(1) = 3
        assert len(summaries) >= 3
        levels = [s.level for s in summaries]
        assert "L1" in levels
        assert "L2" in levels
        assert "L3" in levels

    def test_list_all_empty(self, repo: SummaryRepository) -> None:
        """サマリがない場合は空リストを返す."""
        summaries = repo.list_all()

        assert summaries == []
