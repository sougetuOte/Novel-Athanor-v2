# L3-3-1a: PhaseFilter プロトコル定義

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-3-1a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | なし |
| 並列実行 | Phase A グループ（他プロトコルと並列可） |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` Section 5.2 |

## 概要

`current_phase` に基づいてキャラクターや世界観設定をフィルタリングするための
Protocol（インターフェース）を定義する。

## 受け入れ条件

- [ ] `PhaseFilter` Protocol が typing.Protocol を継承している
- [ ] `filter_by_phase()` メソッドが定義されている
- [ ] `get_available_phases()` メソッドが定義されている
- [ ] ユニットテスト（Protocol準拠確認）が存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/phase_filter.py`
- テスト: `tests/core/context/test_phase_filter.py`

### クラス定義

```python
from typing import Protocol, TypeVar, Generic

T = TypeVar('T')

class PhaseFilter(Protocol[T]):
    """フェーズに基づくフィルタリングプロトコル

    キャラクターや世界観設定は、物語の進行（フェーズ）に応じて
    利用可能な情報が変化する。このProtocolは、現在のフェーズに
    適用可能な情報のみを抽出する機能を定義する。

    Example:
        キャラクター「アイラ」の設定:
        - 初期フェーズ: 「村の少女」
        - arc_1_reveal: 「実は王族の血筋」（この情報が追加）

        current_phase="arc_1_reveal" でフィルタすると、
        「実は王族の血筋」の情報も含めて返す。
    """

    def filter_by_phase(self, entity: T, phase: str) -> T:
        """指定フェーズに適用可能な情報のみを抽出

        Args:
            entity: フィルタ対象のエンティティ
            phase: 現在のフェーズ

        Returns:
            フェーズに適用可能な情報のみを含むエンティティ
        """
        ...

    def get_available_phases(self, entity: T) -> list[str]:
        """エンティティで利用可能なフェーズ一覧を取得

        Args:
            entity: 対象のエンティティ

        Returns:
            利用可能なフェーズ名のリスト
        """
        ...


class PhaseFilterError(Exception):
    """フェーズフィルタリング時のエラー"""
    pass


class InvalidPhaseError(PhaseFilterError):
    """無効なフェーズが指定された"""
    pass
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | Protocol準拠確認 | 具体クラスがProtocolを満たす |
| 2 | PhaseFilterError | 例外クラスの存在確認 |
| 3 | InvalidPhaseError | 例外クラスの継承確認 |

## フェーズフィルタリングの仕様

### Character モデルでの適用

L1-2-2 で定義した Character モデルは `phases` フィールドを持つ:

```python
class Character(BaseModel):
    name: str
    phases: dict[str, CharacterPhase]  # フェーズ名 → その時点での情報
```

フェーズフィルタは、指定されたフェーズ以前の全情報を統合して返す。

### WorldSetting モデルでの適用

L1-2-3 で定義した WorldSetting モデルも同様に `phases` を持つ。

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
