# L3-2-1b: LazyLoadedContent データクラス

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L3-2-1b |
| 優先度 | P1 |
| ステータス | 🔲 backlog |
| 依存タスク | L3-2-1a |
| フェーズ | Phase B（プロトコル定義） |
| 参照仕様 | `docs/specs/novel-generator-v2/08_agent-design.md` Section 8.4 |

## 概要

遅延読み込みされたコンテンツを保持するデータクラスを定義する。
メタデータ（読み込み元、タイムスタンプ、優先度）を含む。

## 受け入れ条件

- [ ] `LazyLoadedContent` データクラスが定義されている
- [ ] ソースパス（読み込み元）フィールドがある
- [ ] 読み込み時刻フィールドがある
- [ ] 優先度（REQUIRED/OPTIONAL）フィールドがある
- [ ] コンテンツの種別（plot/character/world等）フィールドがある
- [ ] ユニットテストが存在する

## 技術的詳細

### ファイル配置

- 実装: `src/core/context/lazy_loader.py`（既存ファイルに追加）
- テスト: `tests/core/context/test_lazy_loader.py`（既存ファイルに追加）

### クラス定義

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar, Optional
from pathlib import Path

from .lazy_loader import LoadPriority

T = TypeVar('T')

class ContentType(Enum):
    """コンテンツ種別"""
    PLOT = "plot"
    SUMMARY = "summary"
    CHARACTER = "character"
    WORLD_SETTING = "world_setting"
    STYLE_GUIDE = "style_guide"
    FORESHADOWING = "foreshadowing"
    REFERENCE = "reference"

@dataclass
class LazyLoadedContent(Generic[T]):
    """遅延読み込みされたコンテンツ

    Attributes:
        content: 実際のコンテンツデータ
        source_path: 読み込み元ファイルパス
        content_type: コンテンツの種別
        priority: 読み込み優先度（REQUIRED/OPTIONAL）
        loaded_at: 読み込み時刻
        cache_key: キャッシュ用のキー
    """
    content: T
    source_path: Path
    content_type: ContentType
    priority: LoadPriority
    loaded_at: datetime = field(default_factory=datetime.now)
    cache_key: Optional[str] = None

    def is_stale(self, max_age_seconds: float = 300.0) -> bool:
        """キャッシュが古くなったかどうか

        Args:
            max_age_seconds: 最大キャッシュ有効期間（デフォルト5分）

        Returns:
            True if キャッシュが古い
        """
        age = (datetime.now() - self.loaded_at).total_seconds()
        return age > max_age_seconds

    def get_identifier(self) -> str:
        """一意識別子を取得

        Returns:
            cache_key があればそれを、なければ source_path を返す
        """
        return self.cache_key or str(self.source_path)
```

### テストケース

| No. | テストケース | 内容 |
|-----|-------------|------|
| 1 | ContentType 列挙型 | 全種別が定義されている |
| 2 | 基本生成 | 必須パラメータで生成 |
| 3 | loaded_at デフォルト | 現在時刻が自動設定される |
| 4 | is_stale() True | 古いコンテンツ |
| 5 | is_stale() False | 新しいコンテンツ |
| 6 | get_identifier() cache_key | cache_key優先 |
| 7 | get_identifier() path | cache_keyなし時はpath |

## 仕様との関連

`08_agent-design.md` Section 8.4 の Graceful Degradation で定義された
「必須」と「付加的」のコンテキスト分類を `LoadPriority` で表現する。

| コンテンツ種別 | デフォルト優先度 |
|---------------|-----------------|
| CHARACTER | REQUIRED |
| PLOT | REQUIRED |
| STYLE_GUIDE | REQUIRED |
| REFERENCE | OPTIONAL |
| SUMMARY | OPTIONAL |

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-26 | 初版作成 |
