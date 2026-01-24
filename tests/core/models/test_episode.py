"""Tests for Episode model."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.core.models.episode import Episode


class TestEpisode:
    """Episode モデルのテスト."""

    def test_create_episode_with_required_fields(self) -> None:
        """必須フィールドのみでエピソードを作成できる."""
        episode = Episode(
            work="テスト作品",
            episode_number=1,
            title="第一話",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        assert episode.type == "episode"
        assert episode.work == "テスト作品"
        assert episode.episode_number == 1
        assert episode.title == "第一話"
        assert episode.status == "draft"
        assert episode.word_count == 0
        assert episode.tags == []
        assert episode.body == ""

    def test_create_episode_with_all_fields(self) -> None:
        """全フィールドを指定してエピソードを作成できる."""
        episode = Episode(
            work="テスト作品",
            episode_number=10,
            title="第十話",
            sequence="seq_001",
            chapter="第一章",
            status="complete",
            word_count=5000,
            created=date(2026, 1, 1),
            updated=date(2026, 1, 24),
            tags=["action", "drama"],
            body="本文です。",
        )

        assert episode.sequence == "seq_001"
        assert episode.chapter == "第一章"
        assert episode.status == "complete"
        assert episode.word_count == 5000
        assert episode.tags == ["action", "drama"]
        assert episode.body == "本文です。"

    def test_episode_number_must_be_positive(self) -> None:
        """episode_number は1以上でなければならない."""
        with pytest.raises(ValidationError):
            Episode(
                work="テスト",
                episode_number=0,
                title="無効",
                created=date(2026, 1, 24),
                updated=date(2026, 1, 24),
            )

    def test_word_count_must_be_non_negative(self) -> None:
        """word_count は0以上でなければならない."""
        with pytest.raises(ValidationError):
            Episode(
                work="テスト",
                episode_number=1,
                title="無効",
                word_count=-1,
                created=date(2026, 1, 24),
                updated=date(2026, 1, 24),
            )

    def test_status_must_be_valid(self) -> None:
        """status は有効な値でなければならない."""
        with pytest.raises(ValidationError):
            Episode(
                work="テスト",
                episode_number=1,
                title="無効",
                status="invalid_status",  # type: ignore
                created=date(2026, 1, 24),
                updated=date(2026, 1, 24),
            )

    def test_episode_to_dict(self) -> None:
        """エピソードを辞書に変換できる."""
        episode = Episode(
            work="テスト作品",
            episode_number=1,
            title="第一話",
            created=date(2026, 1, 24),
            updated=date(2026, 1, 24),
        )

        data = episode.model_dump()

        assert data["type"] == "episode"
        assert data["work"] == "テスト作品"
        assert data["episode_number"] == 1
