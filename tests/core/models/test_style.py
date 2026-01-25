"""Tests for StyleGuide and StyleProfile models."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.core.models.style import (
    DialogueStyle,
    POVType,
    StyleGuide,
    StyleProfile,
    TenseType,
)


class TestPOVType:
    """POVType 列挙型のテスト."""

    def test_pov_values(self) -> None:
        """視点タイプの値を確認できる."""
        assert POVType.FIRST_PERSON == "first_person"
        assert POVType.THIRD_PERSON == "third_person"
        assert POVType.THIRD_PERSON_LIMITED == "third_person_limited"
        assert POVType.THIRD_PERSON_OMNISCIENT == "third_person_omniscient"


class TestTenseType:
    """TenseType 列挙型のテスト."""

    def test_tense_values(self) -> None:
        """時制タイプの値を確認できる."""
        assert TenseType.PAST == "past"
        assert TenseType.PRESENT == "present"


class TestDialogueStyle:
    """DialogueStyle モデルのテスト."""

    def test_create_dialogue_style(self) -> None:
        """会話文スタイルを作成できる."""
        style = DialogueStyle(
            quote_style="「」",
            inner_thought_style="（）",
            speaker_attribution="after",
        )
        assert style.quote_style == "「」"
        assert style.inner_thought_style == "（）"
        assert style.speaker_attribution == "after"

    def test_dialogue_style_defaults(self) -> None:
        """デフォルト値が設定される."""
        style = DialogueStyle()
        assert style.quote_style == "「」"
        assert style.inner_thought_style is None
        assert style.speaker_attribution is None


class TestStyleGuide:
    """StyleGuide モデルのテスト."""

    def test_create_style_guide_minimal(self) -> None:
        """最小限のフィールドで文体ガイドを作成できる."""
        guide = StyleGuide(
            work="作品名",
            pov=POVType.THIRD_PERSON_LIMITED,
            tense=TenseType.PAST,
        )
        assert guide.work == "作品名"
        assert guide.pov == POVType.THIRD_PERSON_LIMITED
        assert guide.tense == TenseType.PAST

    def test_create_style_guide_full(self) -> None:
        """すべてのフィールドを指定して文体ガイドを作成できる."""
        guide = StyleGuide(
            work="作品名",
            pov=POVType.FIRST_PERSON,
            tense=TenseType.PRESENT,
            style_characteristics=["簡潔な文章", "リズミカルな描写"],
            dialogue=DialogueStyle(
                quote_style="「」",
                inner_thought_style="（）",
            ),
            description_tendencies=["五感を使った描写", "比喩を多用"],
            avoid_expressions=["いわゆる", "まさに"],
            notes="特記事項",
            created=date(2026, 1, 1),
            updated=date(2026, 1, 25),
        )
        assert guide.style_characteristics == ["簡潔な文章", "リズミカルな描写"]
        assert guide.dialogue.quote_style == "「」"
        assert guide.avoid_expressions == ["いわゆる", "まさに"]

    def test_style_guide_defaults(self) -> None:
        """オプションフィールドのデフォルト値."""
        guide = StyleGuide(
            work="作品名",
            pov=POVType.THIRD_PERSON,
            tense=TenseType.PAST,
        )
        assert guide.style_characteristics == []
        assert guide.dialogue is None
        assert guide.description_tendencies == []
        assert guide.avoid_expressions == []


class TestStyleProfile:
    """StyleProfile モデルのテスト."""

    def test_create_style_profile_minimal(self) -> None:
        """最小限のフィールドで文体プロファイルを作成できる."""
        profile = StyleProfile(work="作品名")
        assert profile.work == "作品名"

    def test_create_style_profile_full(self) -> None:
        """すべてのフィールドを指定して文体プロファイルを作成できる."""
        profile = StyleProfile(
            work="作品名",
            avg_sentence_length=25.5,
            dialogue_ratio=0.35,
            ttr=0.68,
            pos_ratios={"名詞": 0.25, "動詞": 0.15, "形容詞": 0.08},
            frequent_words=["彼女", "思った", "言った"],
            sample_episodes=[1, 2, 3],
            analyzed_at=date(2026, 1, 25),
        )
        assert profile.avg_sentence_length == 25.5
        assert profile.dialogue_ratio == 0.35
        assert profile.ttr == 0.68
        assert profile.pos_ratios["名詞"] == 0.25
        assert len(profile.frequent_words) == 3

    def test_style_profile_defaults(self) -> None:
        """デフォルト値が設定される."""
        profile = StyleProfile(work="作品名")
        assert profile.avg_sentence_length is None
        assert profile.dialogue_ratio is None
        assert profile.ttr is None
        assert profile.pos_ratios == {}
        assert profile.frequent_words == []

    def test_style_profile_ratio_validation(self) -> None:
        """比率は 0.0-1.0 の範囲でなければならない."""
        with pytest.raises(ValidationError):
            StyleProfile(
                work="作品名",
                dialogue_ratio=1.5,  # 1.0 を超える
            )
        with pytest.raises(ValidationError):
            StyleProfile(
                work="作品名",
                ttr=-0.1,  # 0.0 未満
            )

    def test_style_profile_sentence_length_positive(self) -> None:
        """平均文長は正の値でなければならない."""
        with pytest.raises(ValidationError):
            StyleProfile(
                work="作品名",
                avg_sentence_length=-5.0,
            )
