# L3-4-2b: Summary コンテキスト収集

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-4-2b |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-4-1b, L1-2-5 |
| フェーズ | Phase D（コンテキスト収集） |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 2.5 |

## 概要

サマリ情報（L1/L2/L3）を収集するコレクターを実装する。
ContextCollector プロトコルに準拠。

## 受け入れ条件

- [ ] `SummaryCollector` クラスが実装されている
- [ ] L1 サマリ（全体要約）を収集できる
- [ ] L2 サマリ（章要約）を収集できる
- [ ] L3 サマリ（直近シーン要約）を収集できる
- [ ] ContextCollector プロトコルに準拠
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/collectors/summary_collector.py`（新規）
- テスト: `tests/core/context/collectors/test_summary_collector.py`（新規）

### クラス定義

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..scene_identifier import SceneIdentifier
from ..lazy_loader import FileLazyLoader, LoadPriority

@dataclass
class SummaryContext:
    """サマリコンテキスト

    Attributes:
        l1_overall: L1 全体要約
        l2_chapter: L2 章要約
        l3_recent: L3 直近シーン要約
    """
    l1_overall: Optional[str] = None
    l2_chapter: Optional[str] = None
    l3_recent: Optional[str] = None

    def to_dict(self) -> dict[str, Optional[str]]:
        """辞書形式に変換"""
        return {
            "summary_l1": self.l1_overall,
            "summary_l2": self.l2_chapter,
            "summary_l3": self.l3_recent,
        }


class SummaryCollector:
    """サマリコンテキスト収集

    vault から L1/L2/L3 サマリを収集する。
    サマリは付加的情報のため、取得失敗時も続行する。

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

    def collect(self, scene: SceneIdentifier) -> SummaryContext:
        """サマリコンテキストを収集

        Args:
            scene: シーン識別子

        Returns:
            収集したサマリコンテキスト
        """
        return SummaryContext(
            l1_overall=self._collect_l1(),
            l2_chapter=self._collect_l2(scene),
            l3_recent=self._collect_l3(scene),
        )

    def _collect_l1(self) -> Optional[str]:
        """L1 サマリ（全体要約）を収集

        パス: _summary/l1_overall.md
        優先度: OPTIONAL
        """
        result = self.loader.load(
            "_summary/l1_overall.md",
            LoadPriority.OPTIONAL,
        )
        return result.data if result.success else None

    def _collect_l2(self, scene: SceneIdentifier) -> Optional[str]:
        """L2 サマリ（章要約）を収集

        パス: _summary/l2_{chapter_id}.md
        優先度: OPTIONAL
        """
        if not scene.chapter_id:
            return None

        path = f"_summary/l2_{scene.chapter_id}.md"
        result = self.loader.load(path, LoadPriority.OPTIONAL)
        return result.data if result.success else None

    def _collect_l3(self, scene: SceneIdentifier) -> Optional[str]:
        """L3 サマリ（直近シーン要約）を収集

        現在のエピソードの直前のサマリを取得。
        パス: _summary/l3_{previous_episode_id}.md
        優先度: OPTIONAL
        """
        previous_episode_id = self._get_previous_episode_id(scene.episode_id)
        if not previous_episode_id:
            return None

        path = f"_summary/l3_{previous_episode_id}.md"
        result = self.loader.load(path, LoadPriority.OPTIONAL)
        return result.data if result.success else None

    def _get_previous_episode_id(self, episode_id: str) -> Optional[str]:
        """前のエピソードIDを取得

        例: "ep010" → "ep009"

        Args:
            episode_id: 現在のエピソードID

        Returns:
            前のエピソードID、最初のエピソードなら None
        """
        # "ep010" のような形式を想定
        import re
        match = re.match(r"(ep|episode)?(\d+)", episode_id, re.IGNORECASE)
        if not match:
            return None

        prefix = match.group(1) or ""
        num = int(match.group(2))

        if num <= 1:
            return None

        return f"{prefix}{num - 1:03d}"

    def collect_as_string(self, scene: SceneIdentifier) -> Optional[str]:
        """ContextCollector プロトコル準拠メソッド

        全サマリを統合した文字列を返す。

        Args:
            scene: シーン識別子

        Returns:
            統合されたサマリ文字列
        """
        context = self.collect(scene)

        parts = []
        if context.l1_overall:
            parts.append(f"## 全体要約（L1）\n{context.l1_overall}")
        if context.l2_chapter:
            parts.append(f"## 章要約（L2）\n{context.l2_chapter}")
        if context.l3_recent:
            parts.append(f"## 直近シーン要約（L3）\n{context.l3_recent}")

        if not parts:
            return None

        return "\n\n".join(parts)
```

### vault 構造

```
vault/{作品名}/
└── _summary/
    ├── l1_overall.md        # 全体要約
    ├── l2_chapter01.md      # 第1章の要約
    ├── l2_chapter02.md      # 第2章の要約
    ├── l3_ep009.md          # ep009 終了時点の要約
    └── l3_ep010.md          # ep010 終了時点の要約
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | collect() 全存在 | L1/L2/L3 全て |
| 2 | collect() L1 のみ | L2/L3 なし |
| 3 | collect() 全なし | 空コンテキスト |
| 4 | _collect_l2() chapter_id なし | None |
| 5 | _collect_l3() 前エピソードあり | サマリ取得 |
| 6 | _collect_l3() 最初のエピソード | None |
| 7 | _get_previous_episode_id() | "ep010" → "ep009" |
| 8 | _get_previous_episode_id() ep001 | None |
| 9 | collect_as_string() | 統合文字列 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
