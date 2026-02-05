"""Tests for CharacterCollector."""

from pathlib import Path

import pytest

from src.core.context.collectors.character_collector import (
    CharacterCollector,
    CharacterContext,
)
from src.core.context.lazy_loader import FileLazyLoader
from src.core.context.phase_filter import CharacterPhaseFilter
from src.core.context.scene_identifier import SceneIdentifier
from src.core.context.scene_resolver import SceneResolver


class TestCharacterContext:
    """CharacterContext のテスト."""

    def test_get_names(self) -> None:
        """キャラクター名一覧を取得できる."""
        context = CharacterContext(
            characters={"アイラ": "フィルタ済み設定", "カルロス": "もう一つの設定"}
        )
        names = context.get_names()
        assert names == ["アイラ", "カルロス"]

    def test_get_character(self) -> None:
        """指定キャラクターの設定を取得できる."""
        context = CharacterContext(characters={"アイラ": "設定内容"})
        assert context.get_character("アイラ") == "設定内容"
        assert context.get_character("存在しない") is None

    def test_empty_context(self) -> None:
        """空のコンテキストを作成できる."""
        context = CharacterContext()
        assert context.get_names() == []
        assert context.warnings == []


class TestCharacterCollector:
    """CharacterCollector のテスト."""

    @pytest.fixture
    def temp_vault(self, tmp_path: Path) -> Path:
        """テスト用の一時 vault を作成."""
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "characters").mkdir()
        (vault / "episodes").mkdir()
        (vault / "_plot").mkdir()
        return vault

    @pytest.fixture
    def loader(self, temp_vault: Path) -> FileLazyLoader:
        """テスト用ローダー."""
        return FileLazyLoader(temp_vault)

    @pytest.fixture
    def resolver(self, temp_vault: Path) -> SceneResolver:
        """テスト用リゾルバー."""
        return SceneResolver(temp_vault)

    @pytest.fixture
    def phase_filter(self) -> CharacterPhaseFilter:
        """テスト用フェーズフィルタ."""
        return CharacterPhaseFilter(["initial", "arc_1", "finale"])

    @pytest.fixture
    def collector(
        self,
        temp_vault: Path,
        loader: FileLazyLoader,
        resolver: SceneResolver,
        phase_filter: CharacterPhaseFilter,
    ) -> CharacterCollector:
        """テスト用コレクター."""
        return CharacterCollector(temp_vault, loader, resolver, phase_filter)

    def _create_character_file(
        self, vault: Path, name: str, content: str
    ) -> None:
        """キャラクターファイルを作成."""
        char_file = vault / "characters" / f"{name}.md"
        char_file.write_text(content, encoding="utf-8")

    def _create_episode_file(
        self, vault: Path, episode_id: str, content: str
    ) -> None:
        """エピソードファイルを作成."""
        ep_file = vault / "episodes" / f"{episode_id}.md"
        ep_file.write_text(content, encoding="utf-8")

    def _create_plot_l3_file(
        self, vault: Path, episode_id: str, content: str
    ) -> None:
        """L3 プロットファイルを作成."""
        plot_file = vault / "_plot" / f"l3_{episode_id}.md"
        plot_file.write_text(content, encoding="utf-8")

    def test_collect_single_character(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """単一キャラクターを収集できる."""
        # Arrange: キャラクターファイルを作成
        char_content = """---
type: character
name: アイラ
phases:
  - name: initial
    episodes: "1-10"
current_phase: initial
ai_visibility:
  default: 3
  hidden_section: 0
created: 2026-01-24
updated: 2026-01-24
tags: []
sections:
  基本情報: テストキャラクター
---
"""
        self._create_character_file(temp_vault, "アイラ", char_content)

        # エピソードとプロットを作成（キャラクター参照を含む）
        episode_content = "登場人物: [[アイラ]]"
        self._create_episode_file(temp_vault, "001", episode_content)
        self._create_plot_l3_file(temp_vault, "001", episode_content)

        scene = SceneIdentifier(episode_id="001", current_phase="initial")

        # Act
        context = collector.collect(scene)

        # Assert
        assert "アイラ" in context.characters
        assert len(context.warnings) == 0

    def test_collect_multiple_characters(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """複数キャラクターを収集できる."""
        # Arrange
        for name in ["アイラ", "カルロス"]:
            char_content = f"""---
type: character
name: {name}
phases: []
current_phase: null
ai_visibility:
  default: 3
  hidden_section: 0
created: 2026-01-24
updated: 2026-01-24
tags: []
sections:
  基本情報: {name}の設定
---
"""
            self._create_character_file(temp_vault, name, char_content)

        episode_content = "登場人物: [[アイラ]], [[カルロス]]"
        self._create_episode_file(temp_vault, "002", episode_content)
        self._create_plot_l3_file(temp_vault, "002", episode_content)

        scene = SceneIdentifier(episode_id="002")

        # Act
        context = collector.collect(scene)

        # Assert
        assert len(context.characters) == 2
        assert "アイラ" in context.characters
        assert "カルロス" in context.characters

    def test_collect_no_characters(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """キャラクターがいない場合は空のコンテキストを返す."""
        # Arrange
        episode_content = "キャラクターなし"
        self._create_episode_file(temp_vault, "003", episode_content)
        self._create_plot_l3_file(temp_vault, "003", episode_content)

        scene = SceneIdentifier(episode_id="003")

        # Act
        context = collector.collect(scene)

        # Assert
        assert len(context.characters) == 0

    def test_collect_with_phase_filter(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """Phase フィルタが適用される."""
        # Arrange
        char_content = """---
type: character
name: アイラ
phases:
  - name: initial
    episodes: "1-10"
  - name: arc_1
    episodes: "11-20"
current_phase: arc_1
ai_visibility:
  default: 3
  hidden_section: 0
created: 2026-01-24
updated: 2026-01-24
tags: []
sections:
  基本情報: 初期設定
  秘密: arc_1で明かされる秘密
---
"""
        self._create_character_file(temp_vault, "アイラ", char_content)

        episode_content = "登場人物: [[アイラ]]"
        self._create_episode_file(temp_vault, "010", episode_content)
        self._create_plot_l3_file(temp_vault, "010", episode_content)

        scene = SceneIdentifier(episode_id="010", current_phase="initial")

        # Act
        context = collector.collect(scene)

        # Assert
        # initial フェーズのみの情報が含まれる
        result = context.characters["アイラ"]
        assert "initial" in result
        # arc_1 は含まれない（フィルタされる）
        assert "arc_1" not in result or "11-20" not in result

    def test_collect_without_phase(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """Phase 未指定の場合は全情報を返す."""
        # Arrange
        char_content = """---
type: character
name: アイラ
phases:
  - name: initial
    episodes: "1-10"
  - name: arc_1
    episodes: "11-20"
current_phase: arc_1
ai_visibility:
  default: 3
  hidden_section: 0
created: 2026-01-24
updated: 2026-01-24
tags: []
sections:
  基本情報: 初期設定
---
"""
        self._create_character_file(temp_vault, "アイラ", char_content)

        episode_content = "登場人物: [[アイラ]]"
        self._create_episode_file(temp_vault, "011", episode_content)
        self._create_plot_l3_file(temp_vault, "011", episode_content)

        scene = SceneIdentifier(episode_id="011")  # phase なし

        # Act
        context = collector.collect(scene)

        # Assert
        result = context.characters["アイラ"]
        # 全フェーズ情報が含まれる
        assert "アイラ" in result

    def test_collect_as_string(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """統合文字列を生成できる."""
        # Arrange
        for name in ["アイラ", "カルロス"]:
            char_content = f"""---
type: character
name: {name}
phases: []
current_phase: null
ai_visibility:
  default: 3
  hidden_section: 0
created: 2026-01-24
updated: 2026-01-24
tags: []
sections:
  基本情報: {name}の設定
---
"""
            self._create_character_file(temp_vault, name, char_content)

        episode_content = "登場人物: [[アイラ]], [[カルロス]]"
        self._create_episode_file(temp_vault, "012", episode_content)
        self._create_plot_l3_file(temp_vault, "012", episode_content)

        scene = SceneIdentifier(episode_id="012")

        # Act
        result = collector.collect_as_string(scene)

        # Assert
        assert result is not None
        assert "アイラ" in result
        assert "カルロス" in result
        assert "---" in result  # セパレータ

    def test_collect_as_string_empty(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """キャラクターがない場合は None を返す."""
        # Arrange
        episode_content = "キャラクターなし"
        self._create_episode_file(temp_vault, "013", episode_content)
        self._create_plot_l3_file(temp_vault, "013", episode_content)

        scene = SceneIdentifier(episode_id="013")

        # Act
        result = collector.collect_as_string(scene)

        # Assert
        assert result is None

    def test_load_failure_warning(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """読み込み失敗時は warnings に記録される."""
        # Arrange: 空のファイル（パース可能だが必須フィールド欠損）
        # Character モデルは必須フィールドを持つため、パースに失敗する
        char_content = """---
type: character
# name フィールドがない（必須）
---
"""
        self._create_character_file(temp_vault, "不完全キャラ", char_content)

        episode_content = "登場人物: [[不完全キャラ]]"
        self._create_episode_file(temp_vault, "014", episode_content)
        self._create_plot_l3_file(temp_vault, "014", episode_content)

        scene = SceneIdentifier(episode_id="014")

        # Act
        context = collector.collect(scene)

        # Assert
        # パースに失敗するため警告が記録される
        assert len(context.warnings) > 0
        assert any("パース失敗" in w for w in context.warnings)

    def test_parse_failure_warning(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """パース失敗時は warnings に記録される."""
        # Arrange: 不正な YAML を持つキャラクター
        invalid_content = """---
invalid yaml: [unclosed
---
"""
        self._create_character_file(temp_vault, "破損キャラ", invalid_content)

        episode_content = "登場人物: [[破損キャラ]]"
        self._create_episode_file(temp_vault, "015", episode_content)
        self._create_plot_l3_file(temp_vault, "015", episode_content)

        scene = SceneIdentifier(episode_id="015")

        # Act
        context = collector.collect(scene)

        # Assert
        # パースエラーまたは読み込みエラーが記録される
        assert len(context.warnings) > 0

    def test_error_message_format_matches_world_setting(
        self, temp_vault: Path, collector: CharacterCollector
    ) -> None:
        """エラーメッセージフォーマットが WorldSettingCollector と同じパターンである."""
        # Arrange: 不正なYAMLを持つキャラクター
        invalid_content = """---
invalid yaml: [unclosed
---
"""
        self._create_character_file(temp_vault, "破損キャラ", invalid_content)

        episode_content = "登場人物: [[破損キャラ]]"
        self._create_episode_file(temp_vault, "016", episode_content)
        self._create_plot_l3_file(temp_vault, "016", episode_content)

        scene = SceneIdentifier(episode_id="016")

        # Act
        context = collector.collect(scene)

        # Assert
        # WorldSettingCollector と同じフォーマット: "失敗: パス - エラー詳細"
        assert len(context.warnings) > 0
        # エラー詳細が含まれている（" - " で区切られている）
        warning = context.warnings[0]
        assert "パース失敗" in warning
        assert "破損キャラ" in warning or "path" in warning.lower()
