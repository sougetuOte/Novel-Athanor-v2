# L3-5-1a: ForeshadowInstruction データクラス

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-5-1a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | なし |
| 並列実行 | Phase A グループ（他データクラスと並列可） |
| 参照仕様 | `docs/specs/novel-generator-v2/05_foreshadowing-system.md` |

## 概要

伏線に関する指示を Ghost Writer に伝えるためのデータクラスを定義する。
「このシーンでどの伏線をどう扱うか」を明確に指示する。

## 受け入れ条件

- [ ] `InstructionAction` Enum が定義されている
- [ ] `ForeshadowInstruction` データクラスが定義されている
- [ ] `ForeshadowInstructions` コンテナクラスが定義されている
- [ ] `get_all_forbidden()` メソッドが実装されている
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/foreshadow_instruction.py`
- テスト: `tests/core/context/test_foreshadow_instruction.py`

### クラス定義

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class InstructionAction(Enum):
    """伏線指示アクション

    - PLANT: 伏線を初めて設置する
    - REINFORCE: 既存の伏線を強化する
    - HINT: 軽くヒントを出す
    - NONE: このシーンでは伏線に触れない
    """
    PLANT = "plant"
    REINFORCE = "reinforce"
    HINT = "hint"
    NONE = "none"

@dataclass
class ForeshadowInstruction:
    """個別の伏線指示

    Ghost Writer に対して、特定の伏線をどう扱うかを指示する。

    Attributes:
        foreshadowing_id: 伏線のID（例: "FS-001"）
        action: 今回のアクション
        allowed_expressions: 使ってよい表現のリスト
        forbidden_expressions: 絶対に使ってはいけない表現のリスト
        note: 自然言語での補足指示
        subtlety_target: 目標の繊細さレベル（1-10、低いほど露骨）
    """

    foreshadowing_id: str
    action: InstructionAction
    allowed_expressions: list[str] = field(default_factory=list)
    forbidden_expressions: list[str] = field(default_factory=list)
    note: Optional[str] = None
    subtlety_target: int = 5

    def __post_init__(self):
        if not 1 <= self.subtlety_target <= 10:
            raise ValueError(
                f"subtlety_target must be 1-10, got {self.subtlety_target}"
            )

    def should_act(self) -> bool:
        """このシーンで何らかのアクションが必要か"""
        return self.action != InstructionAction.NONE

    def is_planting(self) -> bool:
        """初回設置か"""
        return self.action == InstructionAction.PLANT

@dataclass
class ForeshadowInstructions:
    """シーン全体の伏線指示書

    複数の伏線指示をまとめ、グローバルな禁止キーワードも管理する。

    Attributes:
        instructions: 個別の伏線指示リスト
        global_forbidden_keywords: 全体で禁止されているキーワード
    """

    instructions: list[ForeshadowInstruction] = field(default_factory=list)
    global_forbidden_keywords: list[str] = field(default_factory=list)

    def get_all_forbidden(self) -> list[str]:
        """全禁止キーワードを取得（重複排除）

        グローバル禁止キーワードと各伏線の禁止表現を統合する。
        """
        result = set(self.global_forbidden_keywords)
        for inst in self.instructions:
            result.update(inst.forbidden_expressions)
        return sorted(result)

    def get_active_instructions(self) -> list[ForeshadowInstruction]:
        """アクションが必要な指示のみ取得"""
        return [inst for inst in self.instructions if inst.should_act()]

    def add_instruction(self, instruction: ForeshadowInstruction) -> None:
        """指示を追加"""
        self.instructions.append(instruction)

    def add_global_forbidden(self, keyword: str) -> None:
        """グローバル禁止キーワードを追加"""
        if keyword not in self.global_forbidden_keywords:
            self.global_forbidden_keywords.append(keyword)

    def count_by_action(self) -> dict[InstructionAction, int]:
        """アクション別の指示数をカウント"""
        counts: dict[InstructionAction, int] = {}
        for inst in self.instructions:
            counts[inst.action] = counts.get(inst.action, 0) + 1
        return counts
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | InstructionAction列挙 | PLANT, REINFORCE, HINT, NONE が存在 |
| 2 | ForeshadowInstruction生成 | 正常なパラメータで生成 |
| 3 | subtlety_target範囲外 | 0 や 11 で ValueError |
| 4 | should_act() True | action=PLANT 時 |
| 5 | should_act() False | action=NONE 時 |
| 6 | is_planting() | PLANT時のみTrue |
| 7 | ForeshadowInstructions生成 | 空リストで生成 |
| 8 | get_all_forbidden() | グローバル + 各指示の統合 |
| 9 | get_all_forbidden() 重複排除 | 重複キーワードが1つになる |
| 10 | get_active_instructions() | NONE以外のみ取得 |
| 11 | count_by_action() | アクション別カウント |

## 設計根拠

### なぜ InstructionAction を分けるか

仕様書（05_foreshadowing-system.md）の状態遷移に対応:
- PLANT: registered → planted
- REINFORCE: planted → reinforced
- HINT: planted/reinforced 時の軽い言及
- NONE: 今回は触れない（でも禁止キーワードは守る）

### subtlety_target の活用

L2 の ForeshadowingManager で管理している subtlety_level を
Ghost Writer への指示として変換する。

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
