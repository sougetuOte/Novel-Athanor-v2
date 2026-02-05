"""Tests for SceneIdentifier data class."""

from dataclasses import FrozenInstanceError

import pytest

from src.core.context.scene_identifier import SceneIdentifier


class TestSceneIdentifierCreation:
    """Test SceneIdentifier instance creation."""

    def test_create_with_episode_id_only(self):
        """episode_id のみで生成できる."""
        scene = SceneIdentifier(episode_id="010")
        assert scene.episode_id == "010"
        assert scene.sequence_id is None
        assert scene.chapter_id is None
        assert scene.current_phase is None

    def test_create_with_all_fields(self):
        """全フィールドを指定して生成できる."""
        scene = SceneIdentifier(
            episode_id="010",
            sequence_id="seq_01",
            chapter_id="ch_03",
            current_phase="arc_1_reveal",
        )
        assert scene.episode_id == "010"
        assert scene.sequence_id == "seq_01"
        assert scene.chapter_id == "ch_03"
        assert scene.current_phase == "arc_1_reveal"

    def test_create_with_partial_fields(self):
        """一部のフィールドのみ指定して生成できる."""
        scene = SceneIdentifier(episode_id="ep015", sequence_id="seq_02")
        assert scene.episode_id == "ep015"
        assert scene.sequence_id == "seq_02"
        assert scene.chapter_id is None
        assert scene.current_phase is None


class TestSceneIdentifierValidation:
    """Test SceneIdentifier validation."""

    def test_empty_episode_id_raises_error(self):
        """空文字の episode_id は ValueError."""
        with pytest.raises(ValueError, match="episode_id is required"):
            SceneIdentifier(episode_id="")

    def test_none_episode_id_raises_error(self):
        """None の episode_id は TypeError または ValueError."""
        # Python の dataclass では None を渡すと型エラーにならないが、
        # __post_init__ でバリデーションする
        with pytest.raises(ValueError, match="episode_id is required"):
            SceneIdentifier(episode_id=None)  # type: ignore


class TestSceneIdentifierImmutability:
    """Test SceneIdentifier is frozen (immutable)."""

    def test_cannot_modify_episode_id(self):
        """episode_id を変更できない."""
        scene = SceneIdentifier(episode_id="010")
        with pytest.raises(FrozenInstanceError):
            scene.episode_id = "020"  # type: ignore

    def test_cannot_modify_sequence_id(self):
        """sequence_id を変更できない."""
        scene = SceneIdentifier(episode_id="010", sequence_id="seq_01")
        with pytest.raises(FrozenInstanceError):
            scene.sequence_id = "seq_02"  # type: ignore


class TestSceneIdentifierStr:
    """Test SceneIdentifier string representation."""

    def test_str_with_episode_only(self):
        """episode_id のみの場合の文字列表現."""
        scene = SceneIdentifier(episode_id="010")
        assert str(scene) == "ep:010"

    def test_str_with_sequence(self):
        """sequence_id を含む場合の文字列表現."""
        scene = SceneIdentifier(episode_id="010", sequence_id="seq_01")
        assert str(scene) == "ep:010/seq:seq_01"

    def test_str_with_chapter(self):
        """chapter_id を含む場合の文字列表現."""
        scene = SceneIdentifier(episode_id="010", chapter_id="ch_03")
        assert str(scene) == "ep:010/ch:ch_03"

    def test_str_with_all_location_fields(self):
        """全ロケーションフィールドを含む場合の文字列表現."""
        scene = SceneIdentifier(
            episode_id="010",
            sequence_id="seq_01",
            chapter_id="ch_03",
        )
        assert str(scene) == "ep:010/seq:seq_01/ch:ch_03"


class TestSceneIdentifierEquality:
    """Test SceneIdentifier equality comparison."""

    def test_equal_instances(self):
        """同じ値を持つインスタンスは等価."""
        scene1 = SceneIdentifier(episode_id="010", sequence_id="seq_01")
        scene2 = SceneIdentifier(episode_id="010", sequence_id="seq_01")
        assert scene1 == scene2

    def test_different_instances(self):
        """異なる値を持つインスタンスは非等価."""
        scene1 = SceneIdentifier(episode_id="010")
        scene2 = SceneIdentifier(episode_id="020")
        assert scene1 != scene2

    def test_hashable(self):
        """SceneIdentifier はハッシュ可能（dict のキーに使える）."""
        scene = SceneIdentifier(episode_id="010")
        d = {scene: "test"}
        assert d[scene] == "test"
