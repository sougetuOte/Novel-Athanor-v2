# L3-5-1b: InstructionGenerator プロトコル定義

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-5-1b |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-5-1a |
| フェーズ | Phase B（プロトコル定義） |
| 参照仕様 | `docs/specs/novel-generator-v2/05_foreshadowing-system.md` |

## 概要

伏線指示書（ForeshadowInstructions）を生成するためのプロトコルを定義する。
シーンと伏線情報から、Ghost Writer に渡す指示書を生成する。

## 受け入れ条件

- [ ] `InstructionGenerator` プロトコルが定義されている
- [ ] `generate()` メソッドが定義されている
- [ ] シーンと伏線リストから指示書を生成できる
- [ ] 禁止キーワードの収集も行える
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/instruction_generator.py`（新規）
- テスト: `tests/core/context/test_instruction_generator.py`（新規）

### クラス定義

```python
from typing import Protocol
from .scene_identifier import SceneIdentifier
from .foreshadow_instruction import ForeshadowInstructions, ForeshadowInstruction

class InstructionGenerator(Protocol):
    """伏線指示書生成プロトコル

    シーンに関連する伏線情報から、Ghost Writer に渡す
    指示書を生成する責務を持つ。
    """

    def generate(
        self,
        scene: SceneIdentifier,
        foreshadowings: list[dict],  # L2 ForeshadowingManager からの出力
    ) -> ForeshadowInstructions:
        """伏線指示書を生成

        Args:
            scene: シーン識別子
            foreshadowings: シーンに関連する伏線情報のリスト

        Returns:
            生成された伏線指示書
        """
        ...

    def determine_action(
        self,
        foreshadowing: dict,
        scene: SceneIdentifier,
    ) -> "InstructionAction":
        """伏線のアクションを決定

        伏線のステータスとシーンの関係から、
        適切なアクション（PLANT/REINFORCE/HINT/NONE）を決定する。

        Args:
            foreshadowing: 伏線情報
            scene: シーン識別子

        Returns:
            決定されたアクション
        """
        ...

    def collect_forbidden_keywords(
        self,
        instructions: ForeshadowInstructions,
    ) -> list[str]:
        """禁止キーワードを収集

        指示書から全ての禁止キーワードを収集する。

        Args:
            instructions: 伏線指示書

        Returns:
            禁止キーワードリスト（重複排除済み）
        """
        ...
```

### アクション決定ロジック

| 伏線ステータス | シーンとの関係 | アクション |
|---------------|---------------|-----------|
| registered | plant_scene と一致 | PLANT |
| planted | reinforce_scenes に含まれる | REINFORCE |
| planted | それ以外 | HINT or NONE |
| revealed | - | NONE |

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | プロトコル準拠 | Mockで準拠確認 |
| 2 | generate() 空リスト | 伏線なし |
| 3 | generate() PLANT | 設置シーン |
| 4 | generate() REINFORCE | 強化シーン |
| 5 | determine_action() 各パターン | ステータス別 |
| 6 | collect_forbidden_keywords() | 重複排除 |

## 仕様との関連

`05_foreshadowing-system.md` で定義された伏線ライフサイクル
（registered → planted → reinforced → revealed）に基づいて
アクションを決定する。

`08_agent-design.md` Section 3.5 の出力形式に準拠した
`foreshadow_instructions` を生成する。

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
