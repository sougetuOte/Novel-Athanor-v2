# L3-5-2d: 許可表現リスト収集

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-5-2d |
| 優先度 | P2 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-5-2b |
| フェーズ | Phase E（伏線・Visibility 統合） |
| 参照仕様 | `docs/specs/novel-generator-v2/05_foreshadowing-system.md` |

## 概要

伏線を匂わせる際に使用してよい許可表現を収集するロジックを実装する。
伏線ごとに定義された allowed_expressions を統合。

**注意**: P2 タスクのため、P1 完了後に実装。

## 受け入れ条件

- [ ] `AllowedExpressionCollector` クラスが実装されている
- [ ] 伏線の allowed_expressions を収集できる
- [ ] 伏線ID ごとの許可表現マップを生成できる
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/allowed_expression_collector.py`（新規）
- テスト: `tests/core/context/test_allowed_expression_collector.py`（新規）

### クラス定義

```python
from dataclasses import dataclass, field
from typing import Optional

from .foreshadow_instruction import ForeshadowInstructions, InstructionAction

@dataclass
class AllowedExpressionResult:
    """許可表現収集結果

    Attributes:
        by_foreshadowing: 伏線ID → 許可表現リスト
        all_expressions: 全許可表現（重複排除済み）
    """
    by_foreshadowing: dict[str, list[str]] = field(default_factory=dict)
    all_expressions: list[str] = field(default_factory=list)

    def get_for_foreshadowing(self, fs_id: str) -> list[str]:
        """特定の伏線の許可表現を取得"""
        return self.by_foreshadowing.get(fs_id, [])

    def has_expression(self, expression: str) -> bool:
        """表現が許可されているか"""
        return expression in self.all_expressions


class AllowedExpressionCollector:
    """許可表現収集

    伏線を匂わせる際に使用してよい表現を収集する。
    """

    def collect(
        self,
        foreshadow_instructions: ForeshadowInstructions,
    ) -> AllowedExpressionResult:
        """許可表現を収集

        アクティブな伏線（PLANT/REINFORCE/HINT）の
        許可表現を収集する。

        Args:
            foreshadow_instructions: 伏線指示書

        Returns:
            収集結果
        """
        result = AllowedExpressionResult()
        all_set = set()

        for inst in foreshadow_instructions.get_active_instructions():
            if inst.allowed_expressions:
                result.by_foreshadowing[inst.foreshadowing_id] = (
                    inst.allowed_expressions.copy()
                )
                all_set.update(inst.allowed_expressions)

        result.all_expressions = sorted(all_set)
        return result

    def collect_for_action(
        self,
        foreshadow_instructions: ForeshadowInstructions,
        action: InstructionAction,
    ) -> AllowedExpressionResult:
        """特定アクションの許可表現のみ収集

        Args:
            foreshadow_instructions: 伏線指示書
            action: 対象アクション

        Returns:
            収集結果
        """
        result = AllowedExpressionResult()
        all_set = set()

        for inst in foreshadow_instructions.instructions:
            if inst.action == action and inst.allowed_expressions:
                result.by_foreshadowing[inst.foreshadowing_id] = (
                    inst.allowed_expressions.copy()
                )
                all_set.update(inst.allowed_expressions)

        result.all_expressions = sorted(all_set)
        return result

    def format_for_prompt(
        self,
        result: AllowedExpressionResult,
    ) -> str:
        """プロンプト用にフォーマット

        Ghost Writer に渡すための文字列形式に変換。

        Args:
            result: 収集結果

        Returns:
            フォーマットされた文字列
        """
        if not result.by_foreshadowing:
            return ""

        lines = ["## 使用可能な暗示表現\n"]
        lines.append("以下の表現は、伏線を匂わせる際に使用できます：\n")

        for fs_id, expressions in result.by_foreshadowing.items():
            lines.append(f"### {fs_id}")
            for expr in expressions:
                lines.append(f"- 「{expr}」")
            lines.append("")

        return "\n".join(lines)
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | collect() 単一伏線 | 1つの伏線 |
| 2 | collect() 複数伏線 | 複数伏線統合 |
| 3 | collect() 空指示書 | 空の結果 |
| 4 | collect_for_action() PLANT | PLANT のみ |
| 5 | get_for_foreshadowing() | 特定伏線取得 |
| 6 | has_expression() | 許可判定 |
| 7 | format_for_prompt() | プロンプト形式 |

### 許可表現の例

```yaml
# 伏線 FS-001: アイラの王族の血筋
allowed_expressions:
  - "彼女の瞳には見覚えのある光があった"
  - "どこか気高い雰囲気"
  - "不思議な威厳"

# 伏線 FS-002: 禁忌の魔法の存在
allowed_expressions:
  - "古い文献にはある種の禁じられた技法への言及があった"
  - "師匠が語ることを避ける話題"
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
