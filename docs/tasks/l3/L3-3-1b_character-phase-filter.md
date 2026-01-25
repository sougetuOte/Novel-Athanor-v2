# L3-3-1b: キャラクター Phase フィルタ

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-3-1b |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-3-1a, L1-2-2 |
| フェーズ | Phase C（個別機能実装） |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` |

## 概要

PhaseFilter プロトコルのキャラクター向け具象実装を作成する。
キャラクター設定の中から、現在のフェーズに適用可能な情報のみを抽出。

## 受け入れ条件

- [ ] `CharacterPhaseFilter` クラスが実装されている
- [ ] `filter_by_phase()` で指定フェーズまでの情報を抽出
- [ ] `get_available_phases()` でキャラクターの全フェーズを取得
- [ ] L1 で定義した Character モデルと連携
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/phase_filter.py`（既存ファイルに追加）
- テスト: `tests/core/context/test_phase_filter.py`（既存ファイルに追加）

### クラス定義

```python
from typing import Optional
from src.core.models.character import Character

class CharacterPhaseFilter:
    """キャラクター向け Phase フィルタ

    キャラクター設定をフェーズに基づいてフィルタリングする。
    指定されたフェーズまでの情報のみを抽出し、
    未来のフェーズの情報（ネタバレ）を除外する。

    Attributes:
        phase_order: フェーズの順序リスト（設定で定義）
    """

    def __init__(self, phase_order: list[str]):
        """
        Args:
            phase_order: フェーズの順序（例: ["initial", "arc_1", "arc_2", "finale"]）
        """
        self.phase_order = phase_order

    def filter_by_phase(
        self,
        character: Character,
        phase: str,
    ) -> Character:
        """キャラクターをフェーズでフィルタリング

        指定されたフェーズまでの情報のみを含むキャラクターを返す。

        Args:
            character: フィルタ対象のキャラクター
            phase: 現在のフェーズ

        Returns:
            フィルタ済みキャラクター

        Raises:
            InvalidPhaseError: 無効なフェーズが指定された場合
        """
        if phase not in self.phase_order:
            raise InvalidPhaseError(
                f"Unknown phase: {phase}. "
                f"Available: {self.phase_order}"
            )

        # 現在フェーズのインデックスを取得
        phase_idx = self.phase_order.index(phase)
        applicable_phases = set(self.phase_order[:phase_idx + 1])

        # キャラクターの詳細をフィルタリング
        filtered_details = self._filter_details(
            character.details,
            applicable_phases
        )

        # 新しいキャラクターインスタンスを生成
        return Character(
            name=character.name,
            description=character.description,
            details=filtered_details,
            visibility_overrides=character.visibility_overrides,
        )

    def _filter_details(
        self,
        details: dict,
        applicable_phases: set[str],
    ) -> dict:
        """詳細情報をフィルタリング

        詳細情報の構造:
        {
            "personality": "基本性格...",
            "phases": {
                "initial": {"appearance": "村人の服装"},
                "arc_1_reveal": {"appearance": "高貴な雰囲気"},
            }
        }
        """
        result = {}

        for key, value in details.items():
            if key == "phases":
                # フェーズ依存の情報
                filtered_phases = {
                    p: v for p, v in value.items()
                    if p in applicable_phases
                }
                if filtered_phases:
                    result[key] = filtered_phases
            else:
                # 非フェーズ依存の情報はそのまま
                result[key] = value

        return result

    def get_available_phases(self, character: Character) -> list[str]:
        """キャラクターで利用可能なフェーズ一覧

        Args:
            character: 対象キャラクター

        Returns:
            フェーズ名のリスト（phase_order の順序を保持）
        """
        if "phases" not in character.details:
            return []

        char_phases = set(character.details["phases"].keys())
        return [p for p in self.phase_order if p in char_phases]

    def to_context_string(
        self,
        character: Character,
        phase: str,
    ) -> str:
        """フィルタ済みキャラクターをコンテキスト文字列に変換

        Args:
            character: キャラクター
            phase: 現在のフェーズ

        Returns:
            Ghost Writer に渡すコンテキスト文字列
        """
        filtered = self.filter_by_phase(character, phase)

        lines = [f"# {filtered.name}"]
        if filtered.description:
            lines.append(filtered.description)

        for key, value in filtered.details.items():
            if key == "phases":
                for p, phase_data in value.items():
                    lines.append(f"\n## Phase: {p}")
                    for k, v in phase_data.items():
                        lines.append(f"- {k}: {v}")
            else:
                lines.append(f"\n## {key}")
                lines.append(str(value))

        return "\n".join(lines)
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | filter_by_phase() initial | 最初のフェーズのみ |
| 2 | filter_by_phase() arc_1 | initial + arc_1 |
| 3 | filter_by_phase() finale | 全フェーズ |
| 4 | filter_by_phase() 無効フェーズ | InvalidPhaseError |
| 5 | get_available_phases() | フェーズ一覧取得 |
| 6 | get_available_phases() 空 | phases なしキャラ |
| 7 | to_context_string() | 文字列変換 |
| 8 | 非フェーズ情報の保持 | personality 等 |

### キャラクター設定の構造例

```yaml
# vault/characters/アイラ.md
---
name: アイラ
description: 物語の主人公
---

## 基本情報
- 年齢: 17歳
- 職業: 村の薬草師見習い

## phases

### initial
- appearance: 質素な村人の服装
- personality: 控えめで優しい

### arc_1_reveal
- appearance: 時折見せる高貴な雰囲気
- secret: 王族の血を引いている（Level 2: KNOW）

### finale
- appearance: 女王としての威厳
- role: 国を導く存在
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
