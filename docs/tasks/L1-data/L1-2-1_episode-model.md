# L1-2-1: Episode モデル

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-2-1 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | L0-1-2 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` Section 3.1 |

## 概要

エピソード（本文）を表現する Pydantic モデルを定義する。

## 受け入れ条件

- [ ] `Episode` クラスが `src/core/models/episode.py` に存在する
- [ ] Pydantic BaseModel を継承している
- [ ] 仕様書の全フィールドが定義されている
- [ ] バリデーションが正しく動作する
- [ ] ユニットテストが存在する

## 技術的詳細

### モデル定義

```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Literal

class Episode(BaseModel):
    type: Literal["episode"] = "episode"
    work: str
    episode_number: int = Field(ge=1)
    title: str
    sequence: str | None = None
    chapter: str | None = None
    status: Literal["draft", "complete", "published"] = "draft"
    word_count: int = Field(default=0, ge=0)
    created: date
    updated: date
    tags: list[str] = Field(default_factory=list)

    # 本文（frontmatter 外）
    body: str = ""
```

### バリデーションルール

- `episode_number` >= 1
- `word_count` >= 0
- `status` は定義された値のみ

### ファイル配置

- `src/core/models/episode.py`
- `tests/core/models/test_episode.py`

## 実装メモ

- 2026-01-24: TDD で実装
- Pydantic BaseModel 継承
- バリデーション: episode_number>=1, word_count>=0, status列挙
- テスト6件全て PASS

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
