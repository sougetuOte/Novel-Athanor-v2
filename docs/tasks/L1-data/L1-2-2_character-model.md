# L1-2-2: Character モデル（フェーズ対応）

## メタ情報

| 項目 | 値 |
|------|-----|
| ID | L1-2-2 |
| 優先度 | P0 |
| ステータス | 🔲 backlog |
| 依存タスク | L0-1-2 |
| 参照仕様 | `docs/specs/novel-generator-v2/03_data-model.md` Section 3.2 |

## 概要

キャラクター設定を表現する Pydantic モデルを定義する。フェーズ管理に対応。

## 受け入れ条件

- [ ] `Character` クラスが `src/core/models/character.py` に存在する
- [ ] `Phase` サブモデルが定義されている
- [ ] `current_phase` でアクティブなフェーズを特定できる
- [ ] `ai_visibility` フィールドが存在する
- [ ] ユニットテストが存在する

## 技術的詳細

### モデル定義

```python
from pydantic import BaseModel, Field
from datetime import date

class Phase(BaseModel):
    name: str
    episodes: str  # "1-10" or "11-" 形式

class AIVisibilitySettings(BaseModel):
    default: int = Field(default=0, ge=0, le=3)
    hidden_section: int = Field(default=0, ge=0, le=3)

class Character(BaseModel):
    type: Literal["character"] = "character"
    name: str
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

### フェーズ管理

- `phases`: 全フェーズのリスト
- `current_phase`: 現在アクティブなフェーズ名
- `episodes` 形式: "1-10"（範囲）, "11-"（以降全て）

### ファイル配置

- `src/core/models/character.py`
- `tests/core/models/test_character.py`

## 実装メモ

（実装時に記録）

## 変更履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-01-24 | 初版作成 |
