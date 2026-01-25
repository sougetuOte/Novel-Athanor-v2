# L3-1-1b: シーン→ファイルパス解決ロジック

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-1-1b |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-1-1a, L1-3-2 |
| フェーズ | Phase C（個別機能実装） |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 2.5 |

## 概要

SceneIdentifier から、関連するファイルパス群を解決するロジックを実装する。
エピソード本文、プロット、サマリ等のパスを特定する。

## 受け入れ条件

- [ ] `SceneResolver` クラスが定義されている
- [ ] `resolve_episode_path()` でエピソードパスを解決
- [ ] `resolve_plot_paths()` でプロット（L1/L2/L3）パスを解決
- [ ] `resolve_summary_paths()` でサマリ（L1/L2/L3）パスを解決
- [ ] vault_root を基準とした相対パス解決
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/scene_resolver.py`（新規）
- テスト: `tests/core/context/test_scene_resolver.py`（新規）

### クラス定義

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .scene_identifier import SceneIdentifier

@dataclass
class ResolvedPaths:
    """解決されたファイルパス群

    Attributes:
        episode: エピソード本文ファイル
        plot_l1: L1プロット（テーマ）
        plot_l2: L2プロット（章目標）
        plot_l3: L3プロット（シーン構成）
        summary_l1: L1サマリ
        summary_l2: L2サマリ
        summary_l3: L3サマリ
        style_guide: スタイルガイド
    """
    episode: Optional[Path] = None
    plot_l1: Optional[Path] = None
    plot_l2: Optional[Path] = None
    plot_l3: Optional[Path] = None
    summary_l1: Optional[Path] = None
    summary_l2: Optional[Path] = None
    summary_l3: Optional[Path] = None
    style_guide: Optional[Path] = None

class SceneResolver:
    """シーン→ファイルパス解決

    SceneIdentifier から vault 内の関連ファイルパスを解決する。
    """

    def __init__(self, vault_root: Path):
        """
        Args:
            vault_root: vault のルートパス
        """
        self.vault_root = vault_root

    def resolve_all(self, scene: SceneIdentifier) -> ResolvedPaths:
        """全ての関連パスを解決

        Args:
            scene: シーン識別子

        Returns:
            解決されたパス群
        """
        ...

    def resolve_episode_path(self, scene: SceneIdentifier) -> Optional[Path]:
        """エピソードファイルパスを解決

        パス形式: vault/{作品}/episodes/{episode_id}.md
        または: vault/{作品}/episodes/{chapter_id}/{episode_id}.md

        Args:
            scene: シーン識別子

        Returns:
            エピソードファイルパス、存在しなければ None
        """
        ...

    def resolve_plot_paths(
        self, scene: SceneIdentifier
    ) -> tuple[Optional[Path], Optional[Path], Optional[Path]]:
        """プロットパスを解決

        Returns:
            (L1パス, L2パス, L3パス)
        """
        ...

    def resolve_summary_paths(
        self, scene: SceneIdentifier
    ) -> tuple[Optional[Path], Optional[Path], Optional[Path]]:
        """サマリパスを解決

        Returns:
            (L1パス, L2パス, L3パス)
        """
        ...

    def resolve_style_guide_path(self) -> Optional[Path]:
        """スタイルガイドパスを解決

        パス形式: vault/{作品}/_style_guides/default.md
        """
        ...
```

### vault 構造との対応

```
vault/{作品名}/
├── episodes/           → resolve_episode_path()
│   └── {episode_id}.md
├── _plot/              → resolve_plot_paths()
│   ├── l1_theme.md
│   ├── l2_{chapter_id}.md
│   └── l3_{episode_id}.md
├── _summary/           → resolve_summary_paths()
│   ├── l1_overall.md
│   ├── l2_{chapter_id}.md
│   └── l3_{episode_id}.md
└── _style_guides/      → resolve_style_guide_path()
    └── default.md
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | resolve_episode_path() 存在 | ファイルあり |
| 2 | resolve_episode_path() 不在 | ファイルなし |
| 3 | resolve_episode_path() chapter付き | 章ディレクトリ |
| 4 | resolve_plot_paths() 全存在 | L1/L2/L3 全て |
| 5 | resolve_plot_paths() 部分存在 | L3 のみなし |
| 6 | resolve_summary_paths() | 同上 |
| 7 | resolve_all() | 全パス統合 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
