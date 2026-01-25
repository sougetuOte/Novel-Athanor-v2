# L3-4-2a: Plot コンテキスト収集

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-4-2a |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-4-1b, L1-2-4 |
| フェーズ | Phase D（コンテキスト収集） |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 2.5 |

## 概要

プロット情報（L1/L2/L3）を収集するコレクターを実装する。
ContextCollector プロトコルに準拠。

## 受け入れ条件

- [ ] `PlotCollector` クラスが実装されている
- [ ] L1 プロット（テーマ）を収集できる
- [ ] L2 プロット（章目標）を収集できる
- [ ] L3 プロット（シーン構成）を収集できる
- [ ] ContextCollector プロトコルに準拠
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/collectors/plot_collector.py`（新規）
- テスト: `tests/core/context/collectors/test_plot_collector.py`（新規）

### クラス定義

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..scene_identifier import SceneIdentifier
from ..lazy_loader import FileLazyLoader, LoadPriority

@dataclass
class PlotContext:
    """プロットコンテキスト

    Attributes:
        l1_theme: L1 テーマ（全体方向性）
        l2_chapter: L2 章目標
        l3_scene: L3 シーン構成
    """
    l1_theme: Optional[str] = None
    l2_chapter: Optional[str] = None
    l3_scene: Optional[str] = None

    def to_dict(self) -> dict[str, Optional[str]]:
        """辞書形式に変換"""
        return {
            "plot_l1": self.l1_theme,
            "plot_l2": self.l2_chapter,
            "plot_l3": self.l3_scene,
        }


class PlotCollector:
    """プロットコンテキスト収集

    vault から L1/L2/L3 プロットを収集する。

    Attributes:
        vault_root: vault ルートパス
        loader: 遅延読み込みローダー
    """

    def __init__(
        self,
        vault_root: Path,
        loader: FileLazyLoader,
    ):
        self.vault_root = vault_root
        self.loader = loader

    def collect(self, scene: SceneIdentifier) -> PlotContext:
        """プロットコンテキストを収集

        Args:
            scene: シーン識別子

        Returns:
            収集したプロットコンテキスト
        """
        return PlotContext(
            l1_theme=self._collect_l1(),
            l2_chapter=self._collect_l2(scene),
            l3_scene=self._collect_l3(scene),
        )

    def _collect_l1(self) -> Optional[str]:
        """L1 プロット（テーマ）を収集

        パス: _plot/l1_theme.md
        優先度: OPTIONAL（なくても続行）
        """
        result = self.loader.load(
            "_plot/l1_theme.md",
            LoadPriority.OPTIONAL,
        )
        return result.data if result.success else None

    def _collect_l2(self, scene: SceneIdentifier) -> Optional[str]:
        """L2 プロット（章目標）を収集

        パス: _plot/l2_{chapter_id}.md
        優先度: OPTIONAL
        """
        if not scene.chapter_id:
            return None

        path = f"_plot/l2_{scene.chapter_id}.md"
        result = self.loader.load(path, LoadPriority.OPTIONAL)
        return result.data if result.success else None

    def _collect_l3(self, scene: SceneIdentifier) -> Optional[str]:
        """L3 プロット（シーン構成）を収集

        パス: _plot/l3_{episode_id}.md
        優先度: REQUIRED（シーン執筆に必須）
        """
        path = f"_plot/l3_{scene.episode_id}.md"
        result = self.loader.load(path, LoadPriority.REQUIRED)
        return result.data if result.success else None

    def collect_as_string(self, scene: SceneIdentifier) -> Optional[str]:
        """ContextCollector プロトコル準拠メソッド

        全プロットを統合した文字列を返す。

        Args:
            scene: シーン識別子

        Returns:
            統合されたプロット文字列
        """
        context = self.collect(scene)

        parts = []
        if context.l1_theme:
            parts.append(f"## テーマ（L1）\n{context.l1_theme}")
        if context.l2_chapter:
            parts.append(f"## 章目標（L2）\n{context.l2_chapter}")
        if context.l3_scene:
            parts.append(f"## シーン構成（L3）\n{context.l3_scene}")

        if not parts:
            return None

        return "\n\n".join(parts)
```

### vault 構造

```
vault/{作品名}/
└── _plot/
    ├── l1_theme.md          # テーマ、全体方向性
    ├── l2_chapter01.md      # 第1章の目標
    ├── l2_chapter02.md      # 第2章の目標
    ├── l3_ep010.md          # エピソード010のシーン構成
    └── l3_ep011.md          # エピソード011のシーン構成
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | collect() 全存在 | L1/L2/L3 全て |
| 2 | collect() L1 のみ | L2/L3 なし |
| 3 | collect() L3 のみ | L1/L2 なし |
| 4 | _collect_l1() | テーマ収集 |
| 5 | _collect_l2() chapter_id なし | None |
| 6 | _collect_l3() 存在 | シーン構成 |
| 7 | _collect_l3() 不在 | None (REQUIRED だが graceful) |
| 8 | collect_as_string() | 統合文字列 |
| 9 | to_dict() | 辞書変換 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
