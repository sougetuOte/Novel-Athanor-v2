# L1-2-4: Plot L1/L2/L3 モデル

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-2-4 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | L0-1-2 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` Section 3.5 |

## 概要

3階層のプロット（計画）を表現する Pydantic モデルを定義する。

## 受け入れ条件

- [ ] `PlotL1`, `PlotL2`, `PlotL3` クラスが存在する
- [ ] 共通フィールドを持つ基底クラス `PlotBase` が存在する
- [ ] L1 → L2 → L3 の階層関係が表現できる
- [ ] ユニットテストが存在する

## 技術的詳細

### モデル定義

```python
from pydantic import BaseModel, Field
from typing import Literal

class PlotBase(BaseModel):
    type: Literal["plot"] = "plot"
    work: str
    content: str = ""

class PlotL1(PlotBase):
    level: Literal["L1"] = "L1"
    logline: str = ""
    theme: str = ""
    three_act_structure: dict[str, str] = Field(default_factory=dict)
    character_arcs: list[str] = Field(default_factory=list)
    foreshadowing_master: list[str] = Field(default_factory=list)
    chapters: list[str] = Field(default_factory=list)  # L2へのリンク

class PlotL2(PlotBase):
    level: Literal["L2"] = "L2"
    chapter_number: int
    chapter_name: str
    purpose: str = ""
    state_changes: list[str] = Field(default_factory=list)
    sequences: list[str] = Field(default_factory=list)  # L3へのリンク

class PlotL3(PlotBase):
    level: Literal["L3"] = "L3"
    chapter_number: int
    sequence_number: int
    scenes: list[str] = Field(default_factory=list)
    pov: str = ""
    mood: str = ""
```

### 階層関係

```
PlotL1 (全体計画)
  └─ PlotL2 (章計画) × N
       └─ PlotL3 (シーケンス計画) × M
            └─ Episode (実際の本文)
```

### ファイル配置

- `src/core/models/plot.py`
- `tests/core/models/test_plot.py`

## 実装メモ

- 2026-01-24: TDD で実装
- PlotBase 基底クラス + PlotL1/L2/L3 派生クラス
- テスト4件全て PASS

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
