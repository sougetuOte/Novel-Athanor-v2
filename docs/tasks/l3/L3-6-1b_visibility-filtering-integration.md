# L3-6-1b: 可視性フィルタリング統合

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-6-1b |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-6-1a, L2-2-1 |
| フェーズ | Phase E（伏線・Visibility 統合） |
| 参照仕様 | `docs/specs/novel-generator-v2/04_ai-information-control.md` |

## 概要

L2 の VisibilityController と連携し、AI可視性レベルに基づいた
コンテキストフィルタリングを実装する。

## 受け入れ条件

- [ ] `VisibilityFilteringService` クラスが実装されている
- [ ] L2 VisibilityController との連携
- [ ] キャラクター情報のフィルタリング
- [ ] 世界観情報のフィルタリング
- [ ] プロット情報のフィルタリング
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/visibility_filtering.py`（新規）
- テスト: `tests/core/context/test_visibility_filtering.py`（新規）

### クラス定義

```python
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum

from src.core.services.visibility_controller import (
    VisibilityController,
    AIVisibilityLevel,
)
from .filtered_context import FilteredContext
from .visibility_context import VisibilityAwareContext, VisibilityHint


@dataclass
class FilteringResult:
    """フィルタリング結果

    Attributes:
        filtered_data: フィルタリング後のデータ
        removed_count: 除外された項目数
        hints: 生成されたヒント
    """
    filtered_data: Any
    removed_count: int = 0
    hints: list[VisibilityHint] = field(default_factory=list)


class VisibilityFilteringService:
    """可視性フィルタリングサービス

    L2 の VisibilityController と連携し、
    AI可視性レベルに基づいてコンテキストをフィルタリングする。

    Attributes:
        visibility_controller: L2 の可視性コントローラー
    """

    def __init__(
        self,
        visibility_controller: VisibilityController,
    ):
        self.visibility_controller = visibility_controller

    def filter_context(
        self,
        context: FilteredContext,
        target_level: AIVisibilityLevel = AIVisibilityLevel.KNOW,
    ) -> VisibilityAwareContext:
        """コンテキスト全体をフィルタリング

        Args:
            context: フィルタリング前のコンテキスト
            target_level: 目標可視性レベル

        Returns:
            可視性を考慮したコンテキスト
        """
        result = VisibilityAwareContext(
            base_context=context,
            visibility_level=target_level,
        )

        # 各カテゴリをフィルタリング
        if context.characters:
            char_result = self.filter_characters(
                context.characters,
                target_level,
            )
            result.filtered_characters = char_result.filtered_data
            result.hints.extend(char_result.hints)

        if context.world_settings:
            world_result = self.filter_world_settings(
                context.world_settings,
                target_level,
            )
            result.filtered_world_settings = world_result.filtered_data
            result.hints.extend(world_result.hints)

        # プロットは特別扱い（通常フィルタリングしない）
        result.filtered_plot = self._filter_plot_if_needed(
            context,
            target_level,
        )

        return result

    def filter_characters(
        self,
        characters: dict[str, str],
        target_level: AIVisibilityLevel,
    ) -> FilteringResult:
        """キャラクター情報をフィルタリング

        Args:
            characters: キャラクター名 → 情報 のマップ
            target_level: 目標可視性レベル

        Returns:
            フィルタリング結果
        """
        filtered = {}
        hints = []
        removed = 0

        for name, info in characters.items():
            # L2 から可視性を取得
            visibility = self.visibility_controller.get_character_visibility(
                name
            )

            if self._is_visible(visibility, target_level):
                # フィルタリング後の情報を生成
                filtered_info = self._filter_character_info(
                    info, visibility, target_level
                )
                filtered[name] = filtered_info

                # ヒント生成（AWARE レベルの場合）
                if visibility == AIVisibilityLevel.AWARE:
                    hints.append(VisibilityHint(
                        category="character",
                        entity_id=name,
                        hint_text=f"{name}には隠された一面がある",
                        strength=0.3,
                    ))
            else:
                removed += 1

        return FilteringResult(
            filtered_data=filtered,
            removed_count=removed,
            hints=hints,
        )

    def filter_world_settings(
        self,
        world_settings: dict[str, str],
        target_level: AIVisibilityLevel,
    ) -> FilteringResult:
        """世界観情報をフィルタリング

        Args:
            world_settings: 設定名 → 情報 のマップ
            target_level: 目標可視性レベル

        Returns:
            フィルタリング結果
        """
        filtered = {}
        hints = []
        removed = 0

        for name, info in world_settings.items():
            visibility = self.visibility_controller.get_setting_visibility(
                name
            )

            if self._is_visible(visibility, target_level):
                filtered_info = self._filter_world_info(
                    info, visibility, target_level
                )
                filtered[name] = filtered_info

                if visibility == AIVisibilityLevel.AWARE:
                    hints.append(VisibilityHint(
                        category="world_setting",
                        entity_id=name,
                        hint_text=f"{name}についてはまだ明かされていない秘密がある",
                        strength=0.2,
                    ))
            else:
                removed += 1

        return FilteringResult(
            filtered_data=filtered,
            removed_count=removed,
            hints=hints,
        )

    def _is_visible(
        self,
        visibility: AIVisibilityLevel,
        target_level: AIVisibilityLevel,
    ) -> bool:
        """可視性レベルが目標以上か判定

        可視性の順序: HIDDEN < AWARE < KNOW < USE
        """
        level_order = {
            AIVisibilityLevel.HIDDEN: 0,
            AIVisibilityLevel.AWARE: 1,
            AIVisibilityLevel.KNOW: 2,
            AIVisibilityLevel.USE: 3,
        }

        # HIDDEN は常に不可視
        if visibility == AIVisibilityLevel.HIDDEN:
            return False

        return level_order[visibility] >= level_order[target_level]

    def _filter_character_info(
        self,
        info: str,
        visibility: AIVisibilityLevel,
        target_level: AIVisibilityLevel,
    ) -> str:
        """キャラクター情報を可視性に応じて加工

        AWARE: 基本情報のみ
        KNOW: 詳細情報含む
        USE: 全情報
        """
        if visibility == AIVisibilityLevel.USE:
            return info

        if visibility == AIVisibilityLevel.KNOW:
            # 秘密セクションを除去
            return self._remove_secret_sections(info)

        if visibility == AIVisibilityLevel.AWARE:
            # 基本情報のみ抽出
            return self._extract_basic_info(info)

        return ""

    def _filter_world_info(
        self,
        info: str,
        visibility: AIVisibilityLevel,
        target_level: AIVisibilityLevel,
    ) -> str:
        """世界観情報を可視性に応じて加工"""
        # キャラクター情報と同様のロジック
        return self._filter_character_info(info, visibility, target_level)

    def _filter_plot_if_needed(
        self,
        context: FilteredContext,
        target_level: AIVisibilityLevel,
    ) -> dict[str, Optional[str]]:
        """プロット情報のフィルタリング（通常は行わない）

        プロットは Ghost Writer に必要なため、
        基本的にはフィルタリングしない。
        """
        return {
            "l1": context.plot_l1,
            "l2": context.plot_l2,
            "l3": context.plot_l3,
        }

    def _remove_secret_sections(self, text: str) -> str:
        """秘密セクション（## 秘密 など）を除去"""
        import re
        # ## 秘密 から次のセクションまでを除去
        pattern = r"##\s*(秘密|Secret|Hidden).*?(?=##|\Z)"
        return re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)

    def _extract_basic_info(self, text: str) -> str:
        """基本情報セクションのみ抽出"""
        import re
        # ## 基本情報 セクションを抽出
        match = re.search(
            r"##\s*(基本情報|Basic Info|Overview).*?(?=##|\Z)",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if match:
            return match.group(0)
        # 見つからない場合は最初の段落のみ
        lines = text.split("\n\n")
        return lines[0] if lines else ""
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | filter_context() 全カテゴリ | キャラ+世界観 |
| 2 | filter_characters() HIDDEN | 除外される |
| 3 | filter_characters() AWARE | 基本情報のみ+ヒント |
| 4 | filter_characters() KNOW | 秘密除去 |
| 5 | filter_characters() USE | 全情報 |
| 6 | filter_world_settings() | 世界観フィルタ |
| 7 | _is_visible() レベル判定 | 順序判定 |
| 8 | _remove_secret_sections() | 秘密除去 |
| 9 | _extract_basic_info() | 基本情報抽出 |
| 10 | hints 生成 | AWARE時のヒント |

### 可視性レベルと出力

| レベル | キャラクター情報 | 世界観情報 | ヒント |
|--------|----------------|-----------|--------|
| HIDDEN | 除外 | 除外 | なし |
| AWARE | 基本情報のみ | 基本情報のみ | あり |
| KNOW | 秘密以外 | 秘密以外 | なし |
| USE | 全情報 | 全情報 | なし |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
