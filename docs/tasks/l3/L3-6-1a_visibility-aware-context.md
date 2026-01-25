# L3-6-1a: VisibilityAwareContext データクラス

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-6-1a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-4-1a |
| 並列実行 | Phase A グループ（他データクラスと並列可） |
| 参照仕様 | `docs/specs/novel-generator-v2/04_ai-information-control.md` |

## 概要

AI可視性レベルに基づいてフィルタリングされた情報と、
ヒント（Level 1/2 用の間接的な情報）を保持するデータクラスを定義する。

## 受け入れ条件

- [ ] `VisibilityAwareContext` データクラスが定義されている
- [ ] `FilteredContext` を内包または継承している
- [ ] `hints` フィールドが存在する
- [ ] `excluded_sections` フィールドが存在する
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/visibility_context.py`
- テスト: `tests/core/context/test_visibility_context.py`

### クラス定義

```python
from dataclasses import dataclass, field
from typing import Optional
from src.core.models.ai_visibility import AIVisibilityLevel
from .context_integrator import FilteredContext

@dataclass
class VisibilityHint:
    """可視性ヒント

    Level 1-2 の情報に対して、直接的な内容ではなく
    間接的なヒントを提供する。

    Attributes:
        source_section: ヒントの元となったセクション
        hint_text: ヒントテキスト
        level: 元の可視性レベル
    """
    source_section: str
    hint_text: str
    level: AIVisibilityLevel

@dataclass
class VisibilityAwareContext:
    """可視性フィルタリング済みコンテキスト

    FilteredContext に加えて、AI可視性に基づく追加情報を保持する。

    Attributes:
        base_context: 基本のフィルタ済みコンテキスト
        hints: Level 1-2 用のヒントリスト
        excluded_sections: 除外されたセクション名リスト
        current_visibility_level: 適用された可視性レベル
        forbidden_keywords: このコンテキストでの禁止キーワード
    """
    base_context: FilteredContext
    hints: list[VisibilityHint] = field(default_factory=list)
    excluded_sections: list[str] = field(default_factory=list)
    current_visibility_level: AIVisibilityLevel = AIVisibilityLevel.USE
    forbidden_keywords: list[str] = field(default_factory=list)

    def get_hints_by_level(self, level: AIVisibilityLevel) -> list[VisibilityHint]:
        """指定レベルのヒントのみ取得"""
        return [h for h in self.hints if h.level == level]

    def has_hints(self) -> bool:
        """ヒントが存在するか"""
        return len(self.hints) > 0

    def count_excluded(self) -> int:
        """除外されたセクション数"""
        return len(self.excluded_sections)

    def add_hint(self, hint: VisibilityHint) -> None:
        """ヒントを追加"""
        self.hints.append(hint)

    def add_excluded_section(self, section: str) -> None:
        """除外セクションを追加"""
        if section not in self.excluded_sections:
            self.excluded_sections.append(section)

    def merge_forbidden_keywords(self, keywords: list[str]) -> None:
        """禁止キーワードをマージ（重複排除）"""
        current_set = set(self.forbidden_keywords)
        current_set.update(keywords)
        self.forbidden_keywords = sorted(current_set)

    def to_ghost_writer_context(self) -> dict:
        """Ghost Writer 用のコンテキスト辞書を生成

        ヒントを適切な形式で統合したコンテキストを返す。
        """
        result = self.base_context.to_prompt_dict()

        # ヒントを追加
        if self.hints:
            hint_texts = [h.hint_text for h in self.hints]
            result["foreshadow_hints"] = "\n".join(hint_texts)

        # メタ情報
        result["_excluded_count"] = self.count_excluded()
        result["_visibility_level"] = self.current_visibility_level.value

        return result
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | 空のVisibilityAwareContext | デフォルト値で生成 |
| 2 | VisibilityHint生成 | 正常なパラメータで生成 |
| 3 | get_hints_by_level() | 指定レベルのヒントのみ取得 |
| 4 | has_hints() True | ヒント存在時 |
| 5 | has_hints() False | ヒントなし時 |
| 6 | count_excluded() | 除外セクション数 |
| 7 | add_hint() | ヒント追加 |
| 8 | add_excluded_section() | 除外セクション追加（重複なし） |
| 9 | merge_forbidden_keywords() | 禁止キーワードマージ |
| 10 | to_ghost_writer_context() | 辞書変換 |

## 可視性レベルとヒントの関係

| Level | 名称 | コンテキスト | ヒント |
|-------|------|-------------|--------|
| 0 | HIDDEN | 除外 | なし |
| 1 | AWARE | 除外 | 存在のみヒント |
| 2 | KNOW | 除外 | 内容のヒント |
| 3 | USE | 含める | 不要 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
