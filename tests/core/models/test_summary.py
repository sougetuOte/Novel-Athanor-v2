"""Tests for Summary models."""

from datetime import date

from src.core.models.summary import SummaryBase, SummaryL1, SummaryL2, SummaryL3


class TestSummaryL1:
    """SummaryL1 モデルのテスト."""

    def test_create_summary_l1_minimal(self) -> None:
        """最小限のフィールドでL1サマリを作成できる."""
        summary = SummaryL1(
            work="テスト作品",
            updated=date(2026, 1, 24),
        )

        assert summary.type == "summary"
        assert summary.level == "L1"
        assert summary.work == "テスト作品"
        assert summary.overall_progress == ""

    def test_create_summary_l1_full(self) -> None:
        """全フィールドを指定してL1サマリを作成できる."""
        summary = SummaryL1(
            work="テスト作品",
            updated=date(2026, 1, 24),
            overall_progress="第一章完了、第二章執筆中",
            completed_chapters=["chapter_01"],
            key_events=["主人公が旅立った", "最初の仲間と出会った"],
            content="全体サマリ詳細...",
        )

        assert summary.overall_progress == "第一章完了、第二章執筆中"
        assert len(summary.completed_chapters) == 1
        assert len(summary.key_events) == 2


class TestSummaryL2:
    """SummaryL2 モデルのテスト."""

    def test_create_summary_l2(self) -> None:
        """L2サマリを作成できる."""
        summary = SummaryL2(
            work="テスト作品",
            updated=date(2026, 1, 24),
            chapter_number=1,
            chapter_name="旅立ち",
            actual_content="実際に書いた内容の要約",
            deviations_from_plot=["予定より早く仲間が登場"],
        )

        assert summary.level == "L2"
        assert summary.chapter_number == 1
        assert summary.chapter_name == "旅立ち"
        assert len(summary.deviations_from_plot) == 1


class TestSummaryL3:
    """SummaryL3 モデルのテスト."""

    def test_create_summary_l3(self) -> None:
        """L3サマリを作成できる."""
        summary = SummaryL3(
            work="テスト作品",
            updated=date(2026, 1, 24),
            chapter_number=1,
            sequence_number=1,
            episode_summaries=["ep1: 主人公の紹介", "ep2: 事件発生"],
        )

        assert summary.level == "L3"
        assert summary.chapter_number == 1
        assert summary.sequence_number == 1
        assert len(summary.episode_summaries) == 2

    def test_summary_to_dict(self) -> None:
        """サマリを辞書に変換できる."""
        summary = SummaryL1(
            work="テスト",
            updated=date(2026, 1, 24),
            overall_progress="進行中",
        )

        data = summary.model_dump()

        assert data["type"] == "summary"
        assert data["level"] == "L1"
        assert data["overall_progress"] == "進行中"
