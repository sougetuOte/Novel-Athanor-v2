# L3-6-1c: ヒント収集・統合

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-6-1c |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-6-1a, L3-6-1b |
| フェーズ | Phase E（伏線・Visibility 統合） |
| 参照仕様 | `docs/specs/novel-generator-v2/04_ai-information-control.md` |

## 概要

各ソースから収集したヒントを統合し、Ghost Writer に渡す形式に変換する。
伏線ヒント、可視性ヒント、キャラクターヒントを統合。

## 受け入れ条件

- [ ] `HintCollector` クラスが実装されている
- [ ] 伏線からのヒント収集
- [ ] 可視性からのヒント収集
- [ ] ヒントの優先度ソート
- [ ] プロンプト形式への変換
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/hint_collector.py`（新規）
- テスト: `tests/core/context/test_hint_collector.py`（新規）

### クラス定義

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from .visibility_context import VisibilityHint, VisibilityAwareContext
from .foreshadow_instruction import ForeshadowInstructions, InstructionAction


class HintSource(Enum):
    """ヒントのソース"""
    FORESHADOWING = "foreshadowing"  # 伏線システムから
    VISIBILITY = "visibility"        # 可視性システムから
    CHARACTER = "character"          # キャラクター設定から
    WORLD = "world"                  # 世界観設定から


@dataclass
class CollectedHint:
    """収集されたヒント

    Attributes:
        source: ヒントのソース
        category: カテゴリ（character, world_setting, plot）
        entity_id: 関連エンティティID
        hint_text: ヒントテキスト
        strength: 強度（0.0-1.0）
        priority: 優先度（計算済み）
    """
    source: HintSource
    category: str
    entity_id: str
    hint_text: str
    strength: float = 0.5
    priority: float = field(default=0.0, init=False)

    def __post_init__(self):
        """優先度を計算"""
        # ソースによる基本優先度
        source_weight = {
            HintSource.FORESHADOWING: 1.0,
            HintSource.VISIBILITY: 0.8,
            HintSource.CHARACTER: 0.6,
            HintSource.WORLD: 0.5,
        }
        base = source_weight.get(self.source, 0.5)
        self.priority = base * self.strength


@dataclass
class HintCollection:
    """収集されたヒントのコレクション

    Attributes:
        hints: ヒントリスト（優先度順）
        by_category: カテゴリ別ヒント
        by_entity: エンティティ別ヒント
    """
    hints: list[CollectedHint] = field(default_factory=list)
    by_category: dict[str, list[CollectedHint]] = field(default_factory=dict)
    by_entity: dict[str, list[CollectedHint]] = field(default_factory=dict)

    def add(self, hint: CollectedHint) -> None:
        """ヒントを追加"""
        self.hints.append(hint)

        # カテゴリ別
        if hint.category not in self.by_category:
            self.by_category[hint.category] = []
        self.by_category[hint.category].append(hint)

        # エンティティ別
        if hint.entity_id not in self.by_entity:
            self.by_entity[hint.entity_id] = []
        self.by_entity[hint.entity_id].append(hint)

    def sort_by_priority(self) -> None:
        """優先度でソート（降順）"""
        self.hints.sort(key=lambda h: h.priority, reverse=True)
        for hints in self.by_category.values():
            hints.sort(key=lambda h: h.priority, reverse=True)
        for hints in self.by_entity.values():
            hints.sort(key=lambda h: h.priority, reverse=True)

    def get_top_hints(self, n: int = 5) -> list[CollectedHint]:
        """上位N件のヒントを取得"""
        return self.hints[:n]


class HintCollector:
    """ヒント収集・統合

    各ソースからヒントを収集し、統合する。

    Ghost Writer に渡す際のヒント形式:
    - 伏線ヒント: 「〜を匂わせてください」
    - 可視性ヒント: 「〜には秘密がある雰囲気を」
    - キャラヒント: 「〜の内面を暗示」
    """

    def collect_all(
        self,
        visibility_context: Optional[VisibilityAwareContext] = None,
        foreshadow_instructions: Optional[ForeshadowInstructions] = None,
    ) -> HintCollection:
        """全ソースからヒントを収集

        Args:
            visibility_context: 可視性コンテキスト
            foreshadow_instructions: 伏線指示書

        Returns:
            統合されたヒントコレクション
        """
        collection = HintCollection()

        # 1. 可視性からのヒント
        if visibility_context:
            visibility_hints = self._collect_from_visibility(visibility_context)
            for hint in visibility_hints:
                collection.add(hint)

        # 2. 伏線からのヒント
        if foreshadow_instructions:
            foreshadow_hints = self._collect_from_foreshadowing(
                foreshadow_instructions
            )
            for hint in foreshadow_hints:
                collection.add(hint)

        # 優先度でソート
        collection.sort_by_priority()

        return collection

    def _collect_from_visibility(
        self,
        context: VisibilityAwareContext,
    ) -> list[CollectedHint]:
        """可視性コンテキストからヒントを収集"""
        collected = []

        for hint in context.hints:
            collected.append(CollectedHint(
                source=HintSource.VISIBILITY,
                category=hint.category,
                entity_id=hint.entity_id,
                hint_text=hint.hint_text,
                strength=hint.strength,
            ))

        return collected

    def _collect_from_foreshadowing(
        self,
        instructions: ForeshadowInstructions,
    ) -> list[CollectedHint]:
        """伏線指示書からヒントを収集

        HINT アクションの伏線からヒントを生成。
        PLANT/REINFORCE は指示書で直接扱う。
        """
        collected = []

        for inst in instructions.instructions:
            if inst.action == InstructionAction.HINT:
                # HINT アクションはヒントとして収集
                hint_text = self._generate_hint_text(inst)
                collected.append(CollectedHint(
                    source=HintSource.FORESHADOWING,
                    category="foreshadowing",
                    entity_id=inst.foreshadowing_id,
                    hint_text=hint_text,
                    strength=self._action_to_strength(inst.action),
                ))

        return collected

    def _generate_hint_text(self, inst) -> str:
        """指示からヒントテキストを生成"""
        if inst.note:
            return inst.note

        # デフォルトのヒントテキスト
        return f"{inst.foreshadowing_id}に関連する要素を控えめに匂わせてください"

    def _action_to_strength(self, action: InstructionAction) -> float:
        """アクションから強度を決定"""
        strength_map = {
            InstructionAction.PLANT: 0.8,
            InstructionAction.REINFORCE: 0.6,
            InstructionAction.HINT: 0.3,
            InstructionAction.NONE: 0.0,
        }
        return strength_map.get(action, 0.5)

    def format_for_prompt(
        self,
        collection: HintCollection,
        max_hints: int = 5,
    ) -> str:
        """プロンプト用にフォーマット

        Args:
            collection: ヒントコレクション
            max_hints: 最大ヒント数

        Returns:
            フォーマットされた文字列
        """
        if not collection.hints:
            return ""

        lines = ["## 執筆時のヒント\n"]
        lines.append("以下の要素を、自然な形で匂わせてください：\n")

        for hint in collection.get_top_hints(max_hints):
            # 強度に応じた表現
            intensity = self._strength_to_word(hint.strength)
            lines.append(f"- [{intensity}] {hint.hint_text}")

        return "\n".join(lines)

    def _strength_to_word(self, strength: float) -> str:
        """強度を言葉に変換"""
        if strength >= 0.7:
            return "重要"
        elif strength >= 0.4:
            return "中程度"
        else:
            return "控えめ"

    def format_by_category(
        self,
        collection: HintCollection,
    ) -> dict[str, str]:
        """カテゴリ別にフォーマット

        Args:
            collection: ヒントコレクション

        Returns:
            カテゴリ → フォーマット文字列
        """
        result = {}

        for category, hints in collection.by_category.items():
            lines = [f"### {category} ヒント"]
            for hint in hints:
                lines.append(f"- {hint.hint_text}")
            result[category] = "\n".join(lines)

        return result
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | collect_all() 全ソース | visibility + foreshadowing |
| 2 | collect_all() visibility のみ | 可視性ヒントのみ |
| 3 | collect_all() foreshadowing のみ | 伏線ヒントのみ |
| 4 | collect_all() 空 | ソースなし |
| 5 | _collect_from_visibility() | ヒント変換 |
| 6 | _collect_from_foreshadowing() | HINT アクション |
| 7 | HintCollection.add() | ヒント追加 |
| 8 | HintCollection.sort_by_priority() | 優先度ソート |
| 9 | HintCollection.get_top_hints() | 上位取得 |
| 10 | format_for_prompt() | プロンプト形式 |
| 11 | format_by_category() | カテゴリ別形式 |
| 12 | CollectedHint.priority 計算 | 優先度計算 |

### ヒント優先度の計算

```
priority = source_weight × strength

source_weight:
  FORESHADOWING: 1.0（伏線は最優先）
  VISIBILITY: 0.8
  CHARACTER: 0.6
  WORLD: 0.5

strength: 0.0 〜 1.0
```

### プロンプト出力例

```markdown
## 執筆時のヒント

以下の要素を、自然な形で匂わせてください：

- [重要] FS-001に関連する要素を控えめに匂わせてください
- [中程度] アイラには隠された一面がある
- [控えめ] 古代王国についてはまだ明かされていない秘密がある
```

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
