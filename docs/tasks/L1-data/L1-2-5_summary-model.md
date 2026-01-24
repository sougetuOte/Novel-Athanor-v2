# L1-2-5: Summary L1/L2/L3 モデル

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-2-5 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L0-1-2 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` Section 3.6 |

## 概要

3階層のサマリ（実績）を表現する Pydantic モデルを定義する。

## 受け入れ条件

- [ ] `SummaryL1`, `SummaryL2`, `SummaryL3` クラスが存在する
- [ ] Plot と対になる構造を持つ
- [ ] 実績としての情報（実際に書かれた内容の要約）を保持できる
- [ ] ユニットテストが存在する

## 技術的詳細

### モデル定義

```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

class SummaryBase(BaseModel):
    type: Literal["summary"] = "summary"
    work: str
    content: str = ""
    updated: date

class SummaryL1(SummaryBase):
    level: Literal["L1"] = "L1"
    overall_progress: str = ""
    completed_chapters: list[str] = Field(default_factory=list)
    key_events: list[str] = Field(default_factory=list)

class SummaryL2(SummaryBase):
    level: Literal["L2"] = "L2"
    chapter_number: int
    chapter_name: str
    actual_content: str = ""
    deviations_from_plot: list[str] = Field(default_factory=list)

class SummaryL3(SummaryBase):
    level: Literal["L3"] = "L3"
    chapter_number: int
    sequence_number: int
    episode_summaries: list[str] = Field(default_factory=list)
```

### Plot vs Summary

| 項目 | Plot（計画） | Summary（実績） |
|------|-------------|----------------|
| 目的 | 「こう書く予定」 | 「こう書いた」 |
| 更新タイミング | 執筆前 | 執筆後 |
| 用途 | 執筆ガイド | 振り返り、整合性確認 |

### ファイル配置

- `src/core/models/summary.py`
- `tests/core/models/test_summary.py`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
