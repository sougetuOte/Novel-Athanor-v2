# L3-3-1d: PhaseFilter テスト

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-3-1d |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-3-1b, L3-3-1c |
| フェーズ | Phase C（個別機能実装） |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` |

## 概要

CharacterPhaseFilter と WorldSettingPhaseFilter の
統合テストを実装する。

## 受け入れ条件

- [ ] CharacterPhaseFilter の全メソッドテスト
- [ ] WorldSettingPhaseFilter の全メソッドテスト
- [ ] フェーズ進行シナリオテスト
- [ ] エッジケース（空フェーズ、無効フェーズ等）
- [ ] テストカバレッジ 90% 以上

## 技術的詳細

### ファイル配置

- テスト: `tests/core/context/test_phase_filter.py`（既存ファイルに追加）

### テストフィクスチャ

```python
import pytest
from src.core.models.character import Character
from src.core.models.world_setting import WorldSetting
from src.core.context.phase_filter import (
    CharacterPhaseFilter,
    WorldSettingPhaseFilter,
    InvalidPhaseError,
)

@pytest.fixture
def phase_order() -> list[str]:
    """テスト用フェーズ順序"""
    return ["initial", "arc_1", "arc_2", "finale"]

@pytest.fixture
def sample_character() -> Character:
    """テスト用キャラクター"""
    return Character(
        name="アイラ",
        description="物語の主人公",
        details={
            "personality": "控えめで優しい",
            "phases": {
                "initial": {
                    "appearance": "村人の服装",
                    "role": "薬草師見習い",
                },
                "arc_1": {
                    "appearance": "高貴な雰囲気",
                    "secret_hint": "何か隠している様子",
                },
                "finale": {
                    "appearance": "女王の威厳",
                    "true_identity": "王族の末裔",
                },
            },
        },
    )

@pytest.fixture
def sample_world_setting() -> WorldSetting:
    """テスト用世界観設定"""
    return WorldSetting(
        name="魔法体系",
        category="magic_system",
        description="この世界の魔法の仕組み",
        details={
            "overview": "精霊との契約による魔法",
            "phases": {
                "initial": {
                    "known_magic": "基本的な精霊魔法",
                },
                "arc_2": {
                    "forbidden_magic": "禁忌の魔法",
                },
                "finale": {
                    "true_nature": "魔法の真実",
                },
            },
        },
    )
```

### テストケース一覧

#### CharacterPhaseFilter テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | filter_by_phase() initial | initial のみ |
| 2 | filter_by_phase() arc_1 | initial + arc_1 |
| 3 | filter_by_phase() finale | 全フェーズ |
| 4 | 無効フェーズ | InvalidPhaseError |
| 5 | get_available_phases() | ["initial", "arc_1", "finale"] |
| 6 | phases なしキャラ | 空リスト |
| 7 | to_context_string() | 文字列変換 |
| 8 | 非フェーズ情報保持 | personality 保持 |

#### WorldSettingPhaseFilter テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 9 | filter_by_phase() initial | initial のみ |
| 10 | filter_by_phase() arc_2 | initial + arc_2 |
| 11 | 無効フェーズ | InvalidPhaseError |
| 12 | get_available_phases() | ["initial", "arc_2", "finale"] |
| 13 | phases なし設定 | 空リスト |
| 14 | to_context_string() | 文字列変換 |
| 15 | 非フェーズ情報保持 | overview 保持 |

#### 統合テスト

| No. | テストケース | 内容 |
|-----|-------------|------|
| 16 | フェーズ進行シナリオ | initial → arc_1 → finale |
| 17 | 複数キャラクター | 複数を同時フィルタ |
| 18 | 複数設定 | 複数を同時フィルタ |
| 19 | 不連続フェーズ | arc_1 なしで arc_2 |

### テスト実装例

```python
class TestCharacterPhaseFilter:
    """CharacterPhaseFilter のテスト"""

    def test_filter_initial_only(
        self,
        phase_order: list[str],
        sample_character: Character,
    ):
        """initial フェーズのみフィルタ"""
        filter_impl = CharacterPhaseFilter(phase_order)

        result = filter_impl.filter_by_phase(sample_character, "initial")

        assert result.name == "アイラ"
        assert "initial" in result.details["phases"]
        assert "arc_1" not in result.details["phases"]
        assert "finale" not in result.details["phases"]
        # 非フェーズ情報は保持
        assert result.details["personality"] == "控えめで優しい"

    def test_filter_arc_1_includes_initial(
        self,
        phase_order: list[str],
        sample_character: Character,
    ):
        """arc_1 フェーズは initial も含む"""
        filter_impl = CharacterPhaseFilter(phase_order)

        result = filter_impl.filter_by_phase(sample_character, "arc_1")

        assert "initial" in result.details["phases"]
        assert "arc_1" in result.details["phases"]
        assert "finale" not in result.details["phases"]

    def test_invalid_phase_raises_error(
        self,
        phase_order: list[str],
        sample_character: Character,
    ):
        """無効なフェーズでエラー"""
        filter_impl = CharacterPhaseFilter(phase_order)

        with pytest.raises(InvalidPhaseError) as exc_info:
            filter_impl.filter_by_phase(sample_character, "invalid_phase")

        assert "Unknown phase" in str(exc_info.value)

    def test_get_available_phases(
        self,
        phase_order: list[str],
        sample_character: Character,
    ):
        """利用可能フェーズ取得"""
        filter_impl = CharacterPhaseFilter(phase_order)

        phases = filter_impl.get_available_phases(sample_character)

        # phase_order の順序を保持
        assert phases == ["initial", "arc_1", "finale"]
        # arc_2 はキャラクターに定義なし
        assert "arc_2" not in phases


class TestPhaseFilterIntegration:
    """統合テスト"""

    def test_phase_progression_scenario(
        self,
        phase_order: list[str],
        sample_character: Character,
    ):
        """フェーズ進行シナリオ"""
        filter_impl = CharacterPhaseFilter(phase_order)

        # 読者が物語を読み進めていく
        for i, phase in enumerate(["initial", "arc_1", "finale"]):
            result = filter_impl.filter_by_phase(sample_character, phase)
            available = list(result.details.get("phases", {}).keys())

            # 各フェーズで適切な情報のみが見える
            if phase == "initial":
                assert len(available) == 1
            elif phase == "arc_1":
                assert len(available) == 2
            else:  # finale
                assert len(available) == 3
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
