# L1-2-3: WorldSetting モデル（フェーズ対応）

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-2-3 |
| 優先度 | P0 |
| ステータス | ✅ done |
| 依存タスク | L0-1-2 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` |

## 概要

世界観設定を表現する Pydantic モデルを定義する。フェーズ管理に対応。

## 受け入れ条件

- [ ] `WorldSetting` クラスが `src/core/models/world_setting.py` に存在する
- [ ] `category` フィールドで設定種別を分類できる
- [ ] Character と同様のフェーズ管理に対応
- [ ] ユニットテストが存在する

## 技術的詳細

### モデル定義

```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Literal

class WorldSetting(BaseModel):
    type: Literal["world_setting"] = "world_setting"
    name: str
    category: str  # 例: "地理", "魔法体系", "組織" など
    phases: list[Phase] = Field(default_factory=list)
    current_phase: str | None = None
    ai_visibility: AIVisibilitySettings = Field(
        default_factory=AIVisibilitySettings
    )
    created: date
    updated: date
    tags: list[str] = Field(default_factory=list)

    # セクション別コンテンツ
    sections: dict[str, str] = Field(default_factory=dict)
```

### カテゴリ例

- 地理（Geography）
- 魔法体系（Magic System）
- 組織・勢力（Organizations）
- 歴史（History）
- 文化（Culture）
- アイテム（Items）

### ファイル配置

- `src/core/models/world_setting.py`
- `tests/core/models/test_world_setting.py`

## 実装メモ

- 2026-01-24: TDD で実装
- Character の Phase, AIVisibilitySettings を再利用
- テスト4件全て PASS

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
