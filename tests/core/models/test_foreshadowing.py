"""Tests for Foreshadowing model."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.core.models.foreshadowing import (
    Foreshadowing,
    ForeshadowingAIVisibility,
    ForeshadowingPayoff,
    ForeshadowingSeed,
    ForeshadowingStatus,
    ForeshadowingType,
    RelatedElements,
    TimelineEntry,
    TimelineInfo,
)


class TestForeshadowingType:
    """ForeshadowingType 列挙型のテスト."""

    def test_valid_types(self) -> None:
        """有効な伏線タイプを確認できる."""
        assert ForeshadowingType.CHARACTER_SECRET == "character_secret"
        assert ForeshadowingType.PLOT_TWIST == "plot_twist"
        assert ForeshadowingType.WORLD_REVEAL == "world_reveal"
        assert ForeshadowingType.ITEM_SIGNIFICANCE == "item_significance"


class TestForeshadowingStatus:
    """ForeshadowingStatus 列挙型のテスト."""

    def test_valid_statuses(self) -> None:
        """有効なステータスを確認できる."""
        assert ForeshadowingStatus.REGISTERED == "registered"
        assert ForeshadowingStatus.PLANTED == "planted"
        assert ForeshadowingStatus.REINFORCED == "reinforced"
        assert ForeshadowingStatus.REVEALED == "revealed"
        assert ForeshadowingStatus.ABANDONED == "abandoned"


class TestForeshadowingSeed:
    """ForeshadowingSeed モデルのテスト."""

    def test_create_seed(self) -> None:
        """伏線の種を作成できる."""
        seed = ForeshadowingSeed(
            content="主人公が古びたロケットを持っている",
            description="何気なくロケットを触る描写",
        )
        assert seed.content == "主人公が古びたロケットを持っている"
        assert seed.description == "何気なくロケットを触る描写"

    def test_seed_description_optional(self) -> None:
        """description は省略可能."""
        seed = ForeshadowingSeed(content="伏線の内容")
        assert seed.content == "伏線の内容"
        assert seed.description is None


class TestForeshadowingPayoff:
    """ForeshadowingPayoff モデルのテスト."""

    def test_create_payoff(self) -> None:
        """伏線の回収を作成できる."""
        payoff = ForeshadowingPayoff(
            content="ロケットの中の写真が敵の正体を示している",
            planned_episode="EP-050",
            description="ロケットを開くと、そこには...",
        )
        assert payoff.content == "ロケットの中の写真が敵の正体を示している"
        assert payoff.planned_episode == "EP-050"
        assert payoff.description == "ロケットを開くと、そこには..."

    def test_payoff_optional_fields(self) -> None:
        """planned_episode と description は省略可能."""
        payoff = ForeshadowingPayoff(content="回収の内容")
        assert payoff.content == "回収の内容"
        assert payoff.planned_episode is None
        assert payoff.description is None


class TestTimelineEntry:
    """TimelineEntry モデルのテスト."""

    def test_create_timeline_entry(self) -> None:
        """タイムラインエントリを作成できる."""
        entry = TimelineEntry(
            episode="EP-003",
            type=ForeshadowingStatus.PLANTED,
            date=date(2026, 1, 21),
            expression="彼女はいつもロケットを握りしめていた",
            subtlety=5,
        )
        assert entry.episode == "EP-003"
        assert entry.type == ForeshadowingStatus.PLANTED
        assert entry.expression == "彼女はいつもロケットを握りしめていた"
        assert entry.subtlety == 5


class TestTimelineInfo:
    """TimelineInfo モデルのテスト."""

    def test_create_timeline_info(self) -> None:
        """タイムライン情報を作成できる."""
        timeline = TimelineInfo(
            registered_at=date(2026, 1, 20),
            events=[
                TimelineEntry(
                    episode="EP-003",
                    type=ForeshadowingStatus.PLANTED,
                    date=date(2026, 1, 21),
                    expression="彼女はいつもロケットを握りしめていた",
                    subtlety=5,
                ),
            ],
        )
        assert timeline.registered_at == date(2026, 1, 20)
        assert len(timeline.events) == 1

    def test_timeline_events_default_empty(self) -> None:
        """events のデフォルトは空リスト."""
        timeline = TimelineInfo(registered_at=date(2026, 1, 20))
        assert timeline.events == []


class TestRelatedElements:
    """RelatedElements モデルのテスト."""

    def test_create_related_elements(self) -> None:
        """関連要素を作成できる."""
        related = RelatedElements(
            characters=["主人公", "謎の老人"],
            plot_threads=["PT-003"],
            locations=["王城"],
        )
        assert related.characters == ["主人公", "謎の老人"]
        assert related.plot_threads == ["PT-003"]
        assert related.locations == ["王城"]

    def test_related_elements_defaults(self) -> None:
        """すべてのフィールドのデフォルトは空リスト."""
        related = RelatedElements()
        assert related.characters == []
        assert related.plot_threads == []
        assert related.locations == []


class TestForeshadowingAIVisibility:
    """ForeshadowingAIVisibility モデルのテスト."""

    def test_create_ai_visibility(self) -> None:
        """AI可視性設定を作成できる."""
        visibility = ForeshadowingAIVisibility(
            level=2,
            forbidden_keywords=["王族", "血筋"],
            allowed_expressions=["彼女の瞳には見覚えのある光があった"],
        )
        assert visibility.level == 2
        assert visibility.forbidden_keywords == ["王族", "血筋"]
        assert visibility.allowed_expressions == ["彼女の瞳には見覚えのある光があった"]

    def test_ai_visibility_defaults(self) -> None:
        """デフォルト値が設定される."""
        visibility = ForeshadowingAIVisibility()
        assert visibility.level == 0
        assert visibility.forbidden_keywords == []
        assert visibility.allowed_expressions == []

    def test_ai_visibility_level_validation(self) -> None:
        """level は 0-3 の範囲でなければならない."""
        with pytest.raises(ValidationError):
            ForeshadowingAIVisibility(level=4)
        with pytest.raises(ValidationError):
            ForeshadowingAIVisibility(level=-1)


class TestForeshadowing:
    """Foreshadowing モデルのテスト."""

    def test_create_minimal_foreshadowing(self) -> None:
        """最小限のフィールドで伏線を作成できる."""
        foreshadowing = Foreshadowing(
            id="FS-03-rocket",
            title="主人公の出生の秘密",
            fs_type=ForeshadowingType.CHARACTER_SECRET,
            status=ForeshadowingStatus.REGISTERED,
            subtlety_level=7,
        )
        assert foreshadowing.id == "FS-03-rocket"
        assert foreshadowing.title == "主人公の出生の秘密"
        assert foreshadowing.fs_type == ForeshadowingType.CHARACTER_SECRET
        assert foreshadowing.status == ForeshadowingStatus.REGISTERED
        assert foreshadowing.subtlety_level == 7

    def test_create_full_foreshadowing(self) -> None:
        """すべてのフィールドを指定して伏線を作成できる."""
        foreshadowing = Foreshadowing(
            id="FS-03-rocket",
            title="主人公の出生の秘密",
            fs_type=ForeshadowingType.CHARACTER_SECRET,
            status=ForeshadowingStatus.PLANTED,
            subtlety_level=7,
            ai_visibility=ForeshadowingAIVisibility(
                level=2,
                forbidden_keywords=["王族", "血筋"],
                allowed_expressions=["彼女の瞳には見覚えのある光があった"],
            ),
            seed=ForeshadowingSeed(
                content="主人公が古びたロケットを持っている",
                description="何気なくロケットを触る描写",
            ),
            payoff=ForeshadowingPayoff(
                content="ロケットの中の写真が敵の正体を示している",
                planned_episode="EP-050",
            ),
            timeline=TimelineInfo(
                registered_at=date(2026, 1, 20),
                events=[
                    TimelineEntry(
                        episode="EP-003",
                        type=ForeshadowingStatus.PLANTED,
                        date=date(2026, 1, 21),
                        expression="彼女はいつもロケットを握りしめていた",
                        subtlety=5,
                    ),
                ],
            ),
            related=RelatedElements(
                characters=["主人公", "謎の老人"],
                plot_threads=["PT-003"],
                locations=["王城"],
            ),
            prerequisite=["FS-08-sealed-door/planted"],
        )
        assert foreshadowing.id == "FS-03-rocket"
        assert foreshadowing.ai_visibility.level == 2
        assert foreshadowing.seed is not None
        assert foreshadowing.payoff is not None
        assert len(foreshadowing.timeline.events) == 1
        assert foreshadowing.related.characters == ["主人公", "謎の老人"]
        assert foreshadowing.prerequisite == ["FS-08-sealed-door/planted"]

    def test_subtlety_level_validation(self) -> None:
        """subtlety_level は 1-10 の範囲でなければならない."""
        with pytest.raises(ValidationError):
            Foreshadowing(
                id="FS-01-test",
                title="テスト",
                fs_type=ForeshadowingType.PLOT_TWIST,
                status=ForeshadowingStatus.REGISTERED,
                subtlety_level=0,
            )
        with pytest.raises(ValidationError):
            Foreshadowing(
                id="FS-01-test",
                title="テスト",
                fs_type=ForeshadowingType.PLOT_TWIST,
                status=ForeshadowingStatus.REGISTERED,
                subtlety_level=11,
            )

    def test_foreshadowing_defaults(self) -> None:
        """オプションフィールドのデフォルト値."""
        foreshadowing = Foreshadowing(
            id="FS-01-test",
            title="テスト",
            fs_type=ForeshadowingType.PLOT_TWIST,
            status=ForeshadowingStatus.REGISTERED,
            subtlety_level=5,
        )
        assert foreshadowing.ai_visibility.level == 0
        assert foreshadowing.seed is None
        assert foreshadowing.payoff is None
        assert foreshadowing.related.characters == []
        assert foreshadowing.prerequisite == []

    def test_foreshadowing_id_format(self) -> None:
        """ID は FS-{episode}-{slug} 形式を推奨（バリデーションはなし）."""
        # 任意の形式を許容するが、推奨形式をドキュメント化
        foreshadowing = Foreshadowing(
            id="FS-03-rocket",
            title="テスト",
            fs_type=ForeshadowingType.PLOT_TWIST,
            status=ForeshadowingStatus.REGISTERED,
            subtlety_level=5,
        )
        assert foreshadowing.id == "FS-03-rocket"
