# L3-4-2e: StyleGuide コンテキスト収集

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-4-2e |
| 優先度 | P1 |
| ステータス | ✅ 完了 |
| 依存タスク | L3-4-1b, L1-2-9 |
| フェーズ | Phase D（コンテキスト収集） |
| 参照仕様 | `docs/specs/novel-generator-v2/02_architecture.md` Section 2.5 |

## 概要

スタイルガイドを収集するコレクターを実装する。
Ghost Writer に渡す文体指針を提供。

## 受け入れ条件

- [x] `StyleGuideCollector` クラスが実装されている
- [x] デフォルトスタイルガイドを収集できる
- [x] シーン固有スタイル（オーバーライド）に対応
- [x] ContextCollector プロトコルに準拠
- [x] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/collectors/style_guide_collector.py`（新規）
- テスト: `tests/core/context/collectors/test_style_guide_collector.py`（新規）

### クラス定義

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..scene_identifier import SceneIdentifier
from ..lazy_loader import FileLazyLoader, LoadPriority

@dataclass
class StyleGuideContext:
    """スタイルガイドコンテキスト

    Attributes:
        default_guide: デフォルトスタイルガイド
        scene_override: シーン固有のオーバーライド
        merged: 統合されたスタイルガイド
    """
    default_guide: Optional[str] = None
    scene_override: Optional[str] = None

    @property
    def merged(self) -> Optional[str]:
        """統合スタイルガイド

        scene_override があれば優先、なければ default_guide
        """
        if self.scene_override:
            if self.default_guide:
                return f"{self.default_guide}\n\n---\n\n## シーン固有スタイル\n{self.scene_override}"
            return self.scene_override
        return self.default_guide


class StyleGuideCollector:
    """スタイルガイドコンテキスト収集

    vault からスタイルガイドを収集する。
    スタイルガイドは必須コンテキスト。

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

    def collect(self, scene: SceneIdentifier) -> StyleGuideContext:
        """スタイルガイドを収集

        Args:
            scene: シーン識別子

        Returns:
            収集したスタイルガイドコンテキスト
        """
        return StyleGuideContext(
            default_guide=self._collect_default(),
            scene_override=self._collect_scene_override(scene),
        )

    def _collect_default(self) -> Optional[str]:
        """デフォルトスタイルガイドを収集

        パス: _style_guides/default.md
        優先度: REQUIRED
        """
        result = self.loader.load(
            "_style_guides/default.md",
            LoadPriority.REQUIRED,
        )
        return result.data if result.success else None

    def _collect_scene_override(
        self, scene: SceneIdentifier
    ) -> Optional[str]:
        """シーン固有スタイルオーバーライドを収集

        パス: _style_guides/episodes/{episode_id}.md
        または: _style_guides/chapters/{chapter_id}.md
        優先度: OPTIONAL
        """
        # エピソード固有
        episode_path = f"_style_guides/episodes/{scene.episode_id}.md"
        result = self.loader.load(episode_path, LoadPriority.OPTIONAL)
        if result.success and result.data:
            return result.data

        # 章固有
        if scene.chapter_id:
            chapter_path = f"_style_guides/chapters/{scene.chapter_id}.md"
            result = self.loader.load(chapter_path, LoadPriority.OPTIONAL)
            if result.success and result.data:
                return result.data

        return None

    def collect_as_string(self, scene: SceneIdentifier) -> Optional[str]:
        """ContextCollector プロトコル準拠メソッド

        統合されたスタイルガイドを返す。

        Args:
            scene: シーン識別子

        Returns:
            スタイルガイド文字列
        """
        context = self.collect(scene)
        return context.merged
```

### vault 構造

```
vault/{作品名}/
└── _style_guides/
    ├── default.md           # デフォルトスタイルガイド
    ├── episodes/            # エピソード固有オーバーライド
    │   ├── ep010.md
    │   └── ep015.md
    └── chapters/            # 章固有オーバーライド
        ├── chapter01.md
        └── chapter02.md
```

### スタイルガイドの内容例

```markdown
# デフォルトスタイルガイド

## 文体
- 三人称限定視点
- 過去形で記述
- 会話文は「」を使用

## 表現
- 比喩は控えめに
- 感情は行動で表現

## 禁止事項
- 読者への直接呼びかけ
- メタ的な表現
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | collect() デフォルトのみ | オーバーライドなし |
| 2 | collect() エピソード固有 | ep固有あり |
| 3 | collect() 章固有 | 章固有あり |
| 4 | collect() 両方あり | エピソード優先 |
| 5 | _collect_default() 存在 | ファイルあり |
| 6 | _collect_default() 不在 | None |
| 7 | merged プロパティ | 統合結果 |
| 8 | collect_as_string() | プロトコル準拠 |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
| 2026-02-01 | TDD 実装完了（13件テストパス、mypy エラー0件） |
