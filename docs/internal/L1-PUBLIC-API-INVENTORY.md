# L1 Data Layer 公開API 棚卸し報告書

**作成日:** 2026-02-05  
**対象プロジェクト:** Novel-Athanor-v2  
**対象レイヤー:** L1 Data Layer  
**分析精度:** メソッドレベル（公開APIのみ）

---

## 1. src/core/models/ — Pydantic データモデル

### models/__init__.py

**`__all__` 公開エクスポート:**

| エクスポート名 | 種類 | 説明 |
|------------|-----|------|
| AIVisibility | class | AI可視性設定モデル |
| AIVisibilityLevel | enum | AI可視性レベル（0-3） |
| AIVisibilitySettings | class | キャラクター/世界観設定の可視性設定 |
| AllowedExpression | class | Level2で許可された表現 |
| Character | class | キャラクターモデル |
| DialogueStyle | class | 会話文スタイル設定 |
| EntityVisibilityConfig | class | エンティティ別可視性設定 |
| Episode | class | エピソードモデル |
| Foreshadowing | class | 伏線モデル |
| ForeshadowingAIVisibility | class | 伏線のAI可視性設定 |
| ForeshadowingPayoff | class | 伏線の回収 |
| ForeshadowingSeed | class | 伏線の種（設置内容） |
| ForeshadowingStatus | enum | 伏線ステータス |
| ForeshadowingType | enum | 伏線タイプ |
| POVType | enum | 視点タイプ |
| Phase | class | キャラクター/世界観設定のフェーズ |
| PlotBase | class | プロット基底クラス |
| PlotL1 | class | 全体プロット |
| PlotL2 | class | 章プロット |
| PlotL3 | class | シーケンスプロット |
| RelatedElements | class | 伏線に関連する要素 |
| Secret | class | 秘密情報モデル |
| SecretImportance | enum | 秘密の重要度 |
| SectionVisibility | class | セクション別可視性設定 |
| StyleGuide | class | 文体ガイド（定性分析） |
| StyleProfile | class | 文体プロファイル（定量分析） |
| SummaryBase | class | サマリ基底クラス |
| SummaryL1 | class | 全体サマリ |
| SummaryL2 | class | 章サマリ |
| SummaryL3 | class | シーケンスサマリ |
| TenseType | enum | 時制タイプ |
| TimelineEntry | class | 伏線のタイムラインエントリ |
| TimelineInfo | class | 伏線のタイムライン情報 |
| VisibilityConfig | class | 可視性設定全体 |
| WorldSetting | class | 世界観設定モデル |

---

### models/character.py

#### class Phase(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| name | str | 必須 | フェーズ名 |
| episodes | str | 必須 | エピソード範囲（"1-10" or "11-" 形式） |

**メソッド:**
（Pydantci BaseModel 標準メソッドのみ。カスタムメソッドなし）

---

#### class AIVisibilitySettings(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| default | int | 0 | AIに表示するデフォルト可視性レベル（0-3） |
| hidden_section | int | 0 | 隠し設定の可視性レベル（0-3） |

**バリデーション:**
- `default`: ge=0, le=3
- `hidden_section`: ge=0, le=3

**メソッド:**
（Pydantic BaseModel 標準メソッドのみ）

---

#### class Character(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| type | Literal["character"] | "character" | エンティティタイプ（固定値） |
| name | str | 必須 | キャラクター名 |
| phases | list[Phase] | [] | フェーズのリスト |
| current_phase | str \| None | None | 現在のフェーズ名 |
| ai_visibility | AIVisibilitySettings | AIVisibilitySettings() | AI可視性設定 |
| created | date | 必須 | 作成日 |
| updated | date | 必須 | 更新日 |
| tags | list[str] | [] | タグのリスト |
| sections | dict[str, str] | {} | セクション別コンテンツ |

**メソッド:**
（Pydantic BaseModel 標準メソッドのみ。カスタムメソッドなし）

---

### models/episode.py

#### class Episode(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| type | Literal["episode"] | "episode" | エンティティタイプ（固定値） |
| work | str | 必須 | 作品名 |
| episode_number | int | 必須 | エピソード番号（≥1） |
| title | str | 必須 | エピソードタイトル |
| sequence | str \| None | None | シーケンス番号 |
| chapter | str \| None | None | 章番号 |
| status | Literal["draft", "complete", "published"] | "draft" | ステータス |
| word_count | int | 0 | 単語数（≥0） |
| created | date | 必須 | 作成日 |
| updated | date | 必須 | 更新日 |
| tags | list[str] | [] | タグのリスト |
| body | str | "" | 本文（frontmatter 外） |

**バリデーション:**
- `episode_number`: ge=1
- `word_count`: ge=0

**メソッド:**
（Pydantic BaseModel 標準メソッドのみ）

---

### models/foreshadowing.py

#### class ForeshadowingType(str, Enum)

**メンバー:**

| メンバー名 | 値 | 説明 |
|-----------|-----|------|
| CHARACTER_SECRET | "character_secret" | キャラクター秘密関連の伏線 |
| PLOT_TWIST | "plot_twist" | プロット反転関連の伏線 |
| WORLD_REVEAL | "world_reveal" | 世界観明かし関連の伏線 |
| ITEM_SIGNIFICANCE | "item_significance" | アイテム重要性関連の伏線 |

---

#### class ForeshadowingStatus(str, Enum)

**メンバー:**

| メンバー名 | 値 | 説明 |
|-----------|-----|------|
| REGISTERED | "registered" | アイデアとして登録、本文には未出現 |
| PLANTED | "planted" | 本文中に伏線が張られた |
| REINFORCED | "reinforced" | 伏線が強化・補強された |
| REVEALED | "revealed" | 伏線が回収された |
| ABANDONED | "abandoned" | 回収を断念 |

---

#### class ForeshadowingSeed(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| content | str | 必須 | 伏線の内容 |
| description | str \| None | None | 説明 |

**メソッド:**
（Pydantic BaseModel 標準メソッドのみ）

---

#### class ForeshadowingPayoff(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| content | str | 必須 | 回収内容 |
| planned_episode | str \| None | None | 回収予定エピソード |
| description | str \| None | None | 説明 |

**メソッド:**
（Pydantic BaseModel 標準メソッドのみ）

---

#### class TimelineEntry(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| episode | str | 必須 | エピソード識別子 |
| type | ForeshadowingStatus | 必須 | タイムラインエントリのステータス |
| date | date | 必須 | 日付 |
| expression | str | 必須 | 表現・描写 |
| subtlety | int | 必須 | 微妙さレベル（1-10） |

**バリデーション:**
- `subtlety`: ge=1, le=10

---

#### class TimelineInfo(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| registered_at | date | 必須 | 登録日 |
| events | list[TimelineEntry] | [] | タイムラインイベント |

---

#### class RelatedElements(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| characters | list[str] | [] | 関連キャラクター |
| plot_threads | list[str] | [] | 関連プロット線 |
| locations | list[str] | [] | 関連ロケーション |

---

#### class ForeshadowingAIVisibility(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| level | int | 0 | AI可視性レベル（0-3） |
| forbidden_keywords | list[str] | [] | 禁止キーワード |
| allowed_expressions | list[str] | [] | 許可表現 |

**バリデーション:**
- `level`: ge=0, le=3

---

#### class Foreshadowing(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| id | str | 必須 | 伏線ID（FS-{episode}-{slug}形式） |
| title | str | 必須 | 伏線のタイトル |
| fs_type | ForeshadowingType | 必須 | 伏線タイプ |
| status | ForeshadowingStatus | 必須 | 伏線ステータス |
| subtlety_level | int | 必須 | 微妙さレベル（1-10） |
| ai_visibility | ForeshadowingAIVisibility | ForeshadowingAIVisibility() | AI可視性設定 |
| seed | ForeshadowingSeed \| None | None | 伏線の種 |
| payoff | ForeshadowingPayoff \| None | None | 伏線の回収 |
| timeline | TimelineInfo \| None | None | タイムライン情報 |
| related | RelatedElements | RelatedElements() | 関連要素 |
| prerequisite | list[str] | [] | 前提条件（ID）のリスト |

**バリデーション:**
- `subtlety_level`: ge=1, le=10

---

### models/plot.py

#### class PlotBase(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| type | Literal["plot"] | "plot" | エンティティタイプ（固定値） |
| work | str | 必須 | 作品名 |
| content | str | "" | プロット内容 |

---

#### class PlotL1(PlotBase)

**継承:** PlotBase

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| level | Literal["L1"] | "L1" | プロットレベル（固定値） |
| logline | str | "" | ログライン |
| theme | str | "" | テーマ |
| three_act_structure | dict[str, str] | {} | 三幕構成（キー: act name, 値: 説明） |
| character_arcs | list[str] | [] | キャラクターアーク |
| foreshadowing_master | list[str] | [] | 伏線マスターリスト |
| chapters | list[str] | [] | L2プロットへのリンク |

---

#### class PlotL2(PlotBase)

**継承:** PlotBase

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| level | Literal["L2"] | "L2" | プロットレベル（固定値） |
| chapter_number | int | 必須 | 章番号 |
| chapter_name | str | 必須 | 章名 |
| purpose | str | "" | 章の目的 |
| state_changes | list[str] | [] | 状態変化 |
| sequences | list[str] | [] | L3プロット（シーケンス）へのリンク |

---

#### class PlotL3(PlotBase)

**継承:** PlotBase

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| level | Literal["L3"] | "L3" | プロットレベル（固定値） |
| chapter_number | int | 必須 | 章番号 |
| sequence_number | int | 必須 | シーケンス番号 |
| scenes | list[str] | [] | シーン識別子 |
| pov | str | "" | 視点キャラクター |
| mood | str | "" | シーケンスのムード |

---

### models/secret.py

#### class SecretImportance(str, Enum)

**メンバー:**

| メンバー名 | 値 | 説明 |
|-----------|-----|------|
| CRITICAL | "critical" | 最重要（類似度閾値: 0.55） |
| HIGH | "high" | 高重要度（類似度閾値: 0.60） |
| MEDIUM | "medium" | 中重要度（類似度閾値: 0.70） |
| LOW | "low" | 低重要度（類似度閾値: 0.75） |

---

#### class Secret(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| id | str | 必須 | 秘密ID |
| content | str | 必須 | 秘密の内容 |
| visibility | AIVisibilityLevel | AIVisibilityLevel.HIDDEN | AI可視性レベル |
| importance | SecretImportance | SecretImportance.MEDIUM | 秘密の重要度 |
| forbidden_keywords | list[str] | [] | 禁止キーワード |
| allowed_expressions | list[str] | [] | 許可表現 |
| related_entity | str \| None | None | 関連エンティティ識別子 |
| notes | str \| None | None | メモ |

**バリデータ:**
- `coerce_visibility`: 整数から AIVisibilityLevel に変換（0-3） ✓ Field Validator

**メソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| get_similarity_threshold | base_threshold: float = 0.70 | float | - | 重要度に応じた類似度閾値を取得 |

---

### models/style.py

#### class POVType(str, Enum)

**メンバー:**

| メンバー名 | 値 | 説明 |
|-----------|-----|------|
| FIRST_PERSON | "first_person" | 一人称視点 |
| THIRD_PERSON | "third_person" | 三人称視点 |
| THIRD_PERSON_LIMITED | "third_person_limited" | 限定的三人称視点 |
| THIRD_PERSON_OMNISCIENT | "third_person_omniscient" | 全知三人称視点 |

---

#### class TenseType(str, Enum)

**メンバー:**

| メンバー名 | 値 | 説明 |
|-----------|-----|------|
| PAST | "past" | 過去時制 |
| PRESENT | "present" | 現在時制 |

---

#### class DialogueStyle(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| quote_style | str | "「」" | 引用符スタイル |
| inner_thought_style | str \| None | None | 内心独白スタイル |
| speaker_attribution | str \| None | None | 話者帰属スタイル（"before", "after", "none"） |

---

#### class StyleGuide(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| work | str | 必須 | 作品名 |
| pov | POVType | 必須 | 視点タイプ |
| tense | TenseType | 必須 | 時制タイプ |
| style_characteristics | list[str] | [] | 文体特性 |
| dialogue | DialogueStyle \| None | None | 会話スタイル設定 |
| description_tendencies | list[str] | [] | 描写傾向 |
| avoid_expressions | list[str] | [] | 避けるべき表現 |
| notes | str \| None | None | メモ |
| created | date \| None | None | 作成日 |
| updated | date \| None | None | 更新日 |

---

#### class StyleProfile(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| work | str | 必須 | 作品名 |
| avg_sentence_length | float \| None | None | 平均文長（>0） |
| dialogue_ratio | float \| None | None | 会話比率（0.0-1.0） |
| ttr | float \| None | None | Type-Token Ratio（0.0-1.0） |
| pos_ratios | dict[str, float] | {} | 品詞比率（0.0-1.0） |
| frequent_words | list[str] | [] | 頻出語彙 |
| sample_episodes | list[int] | [] | サンプルエピソード番号 |
| analyzed_at | date \| None | None | 分析日 |

**バリデータ:**
- `validate_pos_ratios`: 各比率が 0.0-1.0 の範囲内か検証 ✓ Field Validator

**メソッド:**
（Pydantic BaseModel 標準メソッドのみ）

---

### models/summary.py

#### class SummaryBase(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| type | Literal["summary"] | "summary" | エンティティタイプ（固定値） |
| work | str | 必須 | 作品名 |
| content | str | "" | サマリ内容 |
| updated | date | 必須 | 更新日 |

---

#### class SummaryL1(SummaryBase)

**継承:** SummaryBase

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| level | Literal["L1"] | "L1" | サマリレベル（固定値） |
| overall_progress | str | "" | 全体進捗 |
| completed_chapters | list[str] | [] | 完了した章 |
| key_events | list[str] | [] | 主要イベント |

---

#### class SummaryL2(SummaryBase)

**継承:** SummaryBase

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| level | Literal["L2"] | "L2" | サマリレベル（固定値） |
| chapter_number | int | 必須 | 章番号 |
| chapter_name | str | 必須 | 章名 |
| actual_content | str | "" | 実際の内容 |
| deviations_from_plot | list[str] | [] | プロットからのずれ |

---

#### class SummaryL3(SummaryBase)

**継承:** SummaryBase

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| level | Literal["L3"] | "L3" | サマリレベル（固定値） |
| chapter_number | int | 必須 | 章番号 |
| sequence_number | int | 必須 | シーケンス番号 |
| episode_summaries | list[str] | [] | エピソード別サマリ |

---

### models/world_setting.py

#### class WorldSetting(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| type | Literal["world_setting"] | "world_setting" | エンティティタイプ（固定値） |
| name | str | 必須 | 世界観設定名 |
| category | str | 必須 | カテゴリ（例: "Geography", "Magic System"） |
| phases | list[Phase] | [] | フェーズのリスト |
| current_phase | str \| None | None | 現在のフェーズ名 |
| ai_visibility | AIVisibilitySettings | AIVisibilitySettings() | AI可視性設定 |
| created | date | 必須 | 作成日 |
| updated | date | 必須 | 更新日 |
| tags | list[str] | [] | タグのリスト |
| sections | dict[str, str] | {} | セクション別コンテンツ |

---

### models/ai_visibility.py

#### class AIVisibilityLevel(IntEnum)

**メンバー:**

| メンバー名 | 値 | 説明 |
|-----------|-----|------|
| HIDDEN | 0 | 完全秘匿: AIは存在すら知らない |
| AWARE | 1 | 認識のみ: 「何かある」と知る |
| KNOW | 2 | 内容認識: 内容を知る（文章では出さない） |
| USE | 3 | 使用可能: 完全把握、文章で使用可 |

---

#### class AllowedExpression(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| expression | str | 必須 | 許可表現 |
| context | str \| None | None | 文脈（オプション） |

---

#### class AIVisibility(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| level | AIVisibilityLevel | AIVisibilityLevel.HIDDEN | AI可視性レベル |
| forbidden_keywords | list[str] | [] | 禁止キーワード |
| allowed_expressions | list[AllowedExpression] | [] | 許可表現リスト |

**バリデータ:**
- `coerce_expressions`: 文字列リストを AllowedExpression に変換 ✓ Field Validator
- `coerce_level`: 整数をレベルに変換 ✓ Field Validator

**メソッド:**
（Pydantic BaseModel 標準メソッドのみ）

---

#### class SectionVisibility(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| section_name | str | 必須 | セクション名 |
| level | AIVisibilityLevel | AIVisibilityLevel.HIDDEN | 可視性レベル |
| forbidden_keywords | list[str] | [] | 禁止キーワード |
| allowed_expressions | list[str] | [] | 許可表現 |

---

#### class EntityVisibilityConfig(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| entity_type | str | 必須 | エンティティタイプ（character, world_setting など） |
| entity_name | str | 必須 | エンティティ名 |
| default_level | AIVisibilityLevel | AIVisibilityLevel.HIDDEN | デフォルト可視性レベル |
| sections | list[SectionVisibility] | [] | セクション別可視性 |

---

#### class VisibilityConfig(BaseModel)

**継承:** pydantic.BaseModel

**フィールド:**

| フィールド名 | 型 | デフォルト | 説明 |
|------------|---|----------|------|
| version | str | "1.0" | 設定バージョン |
| default_visibility | AIVisibilityLevel | AIVisibilityLevel.HIDDEN | デフォルト可視性レベル |
| entities | list[EntityVisibilityConfig] | [] | エンティティ別設定 |

**メソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| get_entity | entity_type: str, entity_name: str | EntityVisibilityConfig \| None | - | エンティティ設定を取得 |

---

## 2. src/core/parsers/ — パーサーレイヤー

### parsers/__init__.py

**`__all__` 公開エクスポート:**

| エクスポート名 | 種類 | 説明 |
|------------|-----|------|
| ParseError | exception | frontmatter 解析失敗例外 |
| parse_frontmatter | function | Markdown frontmatter を YAML+本文に分割 |
| Section | class | Markdown セクション |
| extract_body | function | frontmatter を除いた本文を抽出 |
| extract_sections | function | 本文をセクション単位で分割 |

---

### parsers/frontmatter.py

#### exception ParseError

**継承:** Exception

**説明:** frontmatter 解析失敗時の例外

---

#### class ParseResult (dataclass)

**フィールド:**

| フィールド名 | 型 | 説明 |
|------------|---|------|
| result_type | str | "structured" または "raw_text" |
| frontmatter | dict[str, Any] \| None | パースされた frontmatter（structured の場合） |
| body | str \| None | パースされた本文（structured の場合） |
| raw_content | str \| None | 生のコンテンツ（raw_text の場合） |
| error | str \| None | エラーメッセージ（raw_text の場合） |

---

#### function parse_frontmatter

**署名:**
```python
def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]
```

**引数:**
- `content: str` - Markdown ファイルの内容

**戻り値:**
- `tuple[dict[str, Any], str]` - (frontmatter辞書, 本文)

**例外:**
- `ParseError` - YAML の解析に失敗した場合

**説明:** Markdown コンテンツから frontmatter と本文を抽出

---

#### function parse_frontmatter_with_fallback

**署名:**
```python
def parse_frontmatter_with_fallback(content: str) -> ParseResult
```

**引数:**
- `content: str` - Markdown ファイルの内容

**戻り値:**
- `ParseResult` - パース結果（structured または raw_text）

**例外:** なし（常に ParseResult を返す）

**説明:** パース失敗時に生テキストでフォールバック。仕様書 03_data-model.md に基づく実装

---

### parsers/markdown.py

#### class Section (dataclass)

**フィールド:**

| フィールド名 | 型 | 説明 |
|------------|---|------|
| title | str | セクションタイトル |
| level | int | ヘッダーレベル（1-6） |
| content | str | セクションコンテンツ |
| start_line | int | セクション開始行番号 |
| end_line | int | セクション終了行番号 |

---

#### function extract_body

**署名:**
```python
def extract_body(content: str) -> str
```

**引数:**
- `content: str` - Markdown ファイルの内容

**戻り値:**
- `str` - frontmatter を除いた本文

**例外:** なし

**説明:** Markdown コンテンツから本文（frontmatter 以降）を抽出

---

#### function extract_sections

**署名:**
```python
def extract_sections(body: str) -> list[Section]
```

**引数:**
- `body: str` - frontmatter を除いた Markdown 本文

**戻り値:**
- `list[Section]` - Section のリスト

**例外:** なし

**説明:** Markdown 本文をセクション単位で分割。見出しパターン: `^#{1,6}\s+` (MULTILINE)

---

### parsers/obsidian_link.py

#### class ObsidianLink (dataclass)

**フィールド:**

| フィールド名 | 型 | 説明 |
|------------|---|------|
| target | str | リンクターゲット |
| display | str \| None | 表示テキスト（オプション） |
| heading | str \| None | ヘッディングアンカー（オプション） |
| block_id | str \| None | ブロックID（オプション） |

**プロパティ:**

| プロパティ名 | 戻り値型 | 説明 |
|-----------|---------|------|
| display_text | str | 表示テキスト（display がなければ target） |
| filename | str | ファイル名部分（パス含む場合は最後の部分） |

**メソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| to_markdown | - | str | - | Obsidian リンク形式に変換 |

---

#### function parse_link

**署名:**
```python
def parse_link(link_text: str) -> ObsidianLink | None
```

**引数:**
- `link_text: str` - リンク文字列（[[...]] 形式）

**戻り値:**
- `ObsidianLink | None` - ObsidianLink オブジェクト、または解析不可の場合は None

**例外:** なし

**説明:** リンク文字列をパース。パターン: `\[\[([^\]|#]+)(?:#(\^)?([^\]|]+))?(?:\|([^\]]+))?\]\]`

---

#### function extract_links

**署名:**
```python
def extract_links(text: str) -> list[ObsidianLink]
```

**引数:**
- `text: str` - パース対象テキスト

**戻り値:**
- `list[ObsidianLink]` - 抽出されたリンク（出現順）

**例外:** なし

**説明:** テキストからすべての Obsidian リンクを抽出

---

### parsers/visibility_comment.py

#### class VisibilityMarker (dataclass)

**フィールド:**

| フィールド名 | 型 | 説明 |
|------------|---|------|
| level | AIVisibilityLevel | AI可視性レベル |
| line_number | int | コメント行番号（1-indexed） |
| section_name | str \| None | 関連セクション名（オプション） |

---

#### function parse_visibility_comments

**署名:**
```python
def parse_visibility_comments(content: str) -> list[VisibilityMarker]
```

**引数:**
- `content: str` - パース対象 Markdown コンテンツ

**戻り値:**
- `list[VisibilityMarker]` - 検出された可視性マーカー

**例外:**
- `ValueError` - 無効な可視性レベル（0-3 以外）が指定された場合

**説明:** コンテンツ内の可視性コメント `<!-- ai_visibility: N -->` をパース

---

#### function extract_section_visibility

**署名:**
```python
def extract_section_visibility(
    content: str,
    default_level: AIVisibilityLevel = AIVisibilityLevel.USE
) -> dict[str, AIVisibilityLevel]
```

**引数:**
- `content: str` - Markdown コンテンツ
- `default_level: AIVisibilityLevel` - デフォルト可視性レベル

**戻り値:**
- `dict[str, AIVisibilityLevel]` - セクション名 → 可視性レベルの辞書

**例外:**
- `ValueError` - 無効な可視性レベルが指定された場合

**説明:** 各セクションの可視性レベルを抽出。コメントは直前のセクションに適用される

---

## 3. src/core/repositories/ — リポジトリレイヤー

### repositories/__init__.py

**`__all__` 公開エクスポート:**

| エクスポート名 | 種類 | 説明 |
|------------|-----|------|
| BaseRepository | class | 基底リポジトリクラス |
| CharacterRepository | class | Character 用リポジトリ |
| EntityExistsError | exception | エンティティ存在エラー |
| EntityNotFoundError | exception | エンティティ未検出エラー |
| EpisodeRepository | class | Episode 用リポジトリ |
| RepositoryError | exception | リポジトリ操作基底例外 |
| WorldSettingRepository | class | WorldSetting 用リポジトリ |

---

### repositories/base.py

#### exception RepositoryError

**継承:** Exception

**説明:** リポジトリ操作の基底例外

---

#### exception EntityNotFoundError

**継承:** RepositoryError

**説明:** エンティティが見つからない場合の例外

---

#### exception EntityExistsError

**継承:** RepositoryError

**説明:** エンティティが既に存在する場合の例外

---

#### class BaseRepository (Generic[T])

**型パラメータ:**
- `T: BaseModel` - 対象モデルタイプ

**継承:** ABC (Abstract Base Class), Generic[T]

**コンストラクタ:**

| メソッド名 | 引数 | 説明 |
|-----------|------|------|
| \_\_init__ | vault_root: Path | Vault ルートディレクトリを指定 |

**抽象メソッド:**

| メソッド名 | 引数 | 戻り値 | 説明 |
|-----------|------|--------|------|
| \_get_path | identifier: str | Path | エンティティのファイルパスを返す |
| \_model_class | - | type[T] | 対象モデルクラスを返す |
| \_get_identifier | entity: T | str | エンティティから識別子を取得 |

**公開メソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| create | entity: T | Path | EntityExistsError | 新規エンティティ作成 |
| read | identifier: str | T | EntityNotFoundError | エンティティ読み込み |
| update | entity: T | None | EntityNotFoundError | エンティティ更新 |
| delete | identifier: str | None | EntityNotFoundError | エンティティ削除 |
| exists | identifier: str | bool | - | エンティティ存在確認 |

**プロテクテッドメソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| \_read | path: Path | T | - | ファイルからモデルを読み込み（frontmatter + body） |
| \_write | path: Path, entity: T | None | - | モデルをファイルに書き込み（frontmatter 形式） |
| \_serialize | entity: T | str | - | エンティティを Markdown 形式にシリアライズ |

**注記:** body フィールドは Episode のような本文を持つモデル用。Character/WorldSetting などは Pydantic の extra='ignore' により無視される

---

### repositories/character.py

#### class CharacterRepository(BaseRepository[Character])

**継承:** BaseRepository[Character]

**コンストラクタ:**

| メソッド名 | 引数 | 説明 |
|-----------|------|------|
| \_\_init__ | vault_root: Path | Vault ルートディレクトリを指定 |

**実装メソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| \_get_path | identifier: str | Path | - | キャラクター名からファイルパスを取得 |
| \_model_class | - | type[Character] | - | Character クラスを返す |
| \_get_identifier | entity: Character | str | - | キャラクター名を識別子として返す |

**カスタムメソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| list_all | - | list[Character] | - | 全キャラクターを取得 |
| get_by_tag | tag: str | list[Character] | - | タグでフィルタリング |
| get_current_phase_content | name: str | dict[str, str] | EntityNotFoundError | 現フェーズのコンテンツを取得（TODO: Phase Filter 対応予定） |
| update_phase | name: str, new_phase: str | None | ValueError, EntityNotFoundError | フェーズを更新 |

---

### repositories/episode.py

#### class EpisodeRepository(BaseRepository[Episode])

**継承:** BaseRepository[Episode]

**コンストラクタ:**

| メソッド名 | 引数 | 説明 |
|-----------|------|------|
| \_\_init__ | vault_root: Path | Vault ルートディレクトリを指定 |

**実装メソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| \_get_path | identifier: str | Path | - | エピソード番号からファイルパスを取得（ep_XXXX.md） |
| \_model_class | - | type[Episode] | - | Episode クラスを返す |
| \_get_identifier | entity: Episode | str | - | エピソード番号を識別子として返す |

**カスタムメソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| list_all | - | list[Episode] | - | 全エピソード取得（エピソード番号順ソート） |
| get_range | start: int, end: int | list[Episode] | - | 範囲指定でエピソード取得（開始〜終了 含む） |
| get_by_status | status: str | list[Episode] | - | ステータスでフィルタリング |
| get_latest | - | Episode \| None | - | 最新エピソードを取得 |

---

### repositories/foreshadowing.py

#### class ForeshadowingRepository

**コンストラクタ:**

| メソッド名 | 引数 | 説明 |
|-----------|------|------|
| \_\_init__ | vault_root: Path, work_name: str | Vault ルートと作品名を指定 |

**管理対象:** vault/{work_name}/_foreshadowing/registry.yaml

**プロテクテッドメソッド:**

| メソッド名 | 引数 | 戻り値 | 説明 |
|-----------|------|--------|------|
| \_get_registry_path | - | Path | レジストリファイルパスを返す |
| \_load_registry | - | dict[str, Any] | YAML レジストリを読み込む |
| \_save_registry | data: dict[str, Any] | None | YAML レジストリを保存（last_updated 自動更新） |
| \_find_index | registry: dict, fs_id: str | int \| None | ID から伏線のインデックスを検索 |

**公開メソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| create | entity: Foreshadowing | None | EntityExistsError | 伏線を新規作成 |
| read | fs_id: str | Foreshadowing | EntityNotFoundError | 伏線を読み込み |
| update | entity: Foreshadowing | None | EntityNotFoundError | 伏線を更新 |
| delete | fs_id: str | None | EntityNotFoundError | 伏線を削除 |
| exists | fs_id: str | bool | - | 伏線が存在するか確認 |
| list_all | - | list[Foreshadowing] | - | すべての伏線をリスト |
| list_by_status | status: ForeshadowingStatus | list[Foreshadowing] | - | ステータスでフィルタしてリスト |

---

### repositories/world_setting.py

#### class WorldSettingRepository(BaseRepository[WorldSetting])

**継承:** BaseRepository[WorldSetting]

**コンストラクタ:**

| メソッド名 | 引数 | 説明 |
|-----------|------|------|
| \_\_init__ | vault_root: Path | Vault ルートディレクトリを指定 |

**実装メソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| \_get_path | identifier: str | Path | - | 世界観設定名からファイルパスを取得 |
| \_model_class | - | type[WorldSetting] | - | WorldSetting クラスを返す |
| \_get_identifier | entity: WorldSetting | str | - | 世界観設定名を識別子として返す |

**カスタムメソッド:**

| メソッド名 | 引数 | 戻り値 | 例外 | 説明 |
|-----------|------|--------|------|------|
| list_all | - | list[WorldSetting] | - | 全世界観設定を取得 |
| get_by_category | category: str | list[WorldSetting] | - | カテゴリでフィルタリング |
| get_by_tag | tag: str | list[WorldSetting] | - | タグでフィルタリング |
| update_phase | name: str, new_phase: str | None | ValueError, EntityNotFoundError | フェーズを更新 |

---

## 4. src/core/vault/ — Vault ユーティリティ

### vault/__init__.py

**内容:** 空（スペース）

---

### vault/path_resolver.py

#### class VaultPathResolver

**コンストラクタ:**

| メソッド名 | 引数 | 説明 |
|-----------|------|------|
| \_\_init__ | vault_root: Path | Vault ルートディレクトリを指定 |

**メソッド:**

| メソッド名 | 引数 | 戻り値 | 説明 |
|-----------|------|--------|------|
| resolve_episode | episode_number: int | Path | エピソードファイルパス (episodes/ep_XXXX.md) |
| resolve_character | name: str | Path | キャラクターファイルパス (characters/{name}.md) |
| resolve_world_setting | name: str | Path | 世界観設定ファイルパス (world/{name}.md) |
| resolve_plot | level: Literal["L1", "L2", "L3"], chapter_number: int \| None, chapter_name: str \| None, sequence_number: int \| None | Path | プロットファイルパス（レベルに応じた構造） |
| resolve_foreshadowing | - | Path | 伏線レジストリパス (_foreshadowing/registry.yaml) |
| exists | path: Path | bool | vault_root からの相対パスについてファイル存在確認 |

**パス生成ルール:**

- **L1 Plot:** `_plot/L1_overall.md`
- **L2 Plot:** `_plot/L2_chapters/{chapter_number:02d}_{chapter_name}.md`
- **L3 Plot:** `_plot/L3_sequences/{chapter_number:02d}_{chapter_name}/seq_{sequence_number:03d}.md`

---

### vault/init.py

#### class VaultStructure

**クラス属性（定数）:**

| 属性名 | 型 | 説明 |
|--------|-----|------|
| DIRECTORIES | list[str] | 必須ディレクトリのリスト |
| SUBDIRECTORIES | list[str] | サブディレクトリのリスト |
| TEMPLATE_FILES | dict[str, str] | テンプレートファイル（パス → コンテンツ） |

**必須ディレクトリ:**
```
episodes, characters, world, _plot, _summary, _foreshadowing,
_ai_control, _settings, _style_guides, _style_profiles
```

**サブディレクトリ:**
```
_plot/L2_chapters, _plot/L3_sequences,
_summary/L2_chapters, _summary/L3_sequences
```

**テンプレートファイル:**
- `_foreshadowing/registry.yaml` - 伏線マスター登録簿
- `_ai_control/visibility.yaml` - AI情報制御設定
- `_settings/pacing_profile.yaml` - 作品ペース設定
- `_settings/quality_thresholds.yaml` - 品質閾値設定

---

#### class VaultInitializer

**コンストラクタ:**

| メソッド名 | 引数 | 説明 |
|-----------|------|------|
| \_\_init__ | vault_path: Path, work_name: str | Vault ルートと作品名を指定 |

**メソッド:**

| メソッド名 | 引数 | 戻り値 | 説明 |
|-----------|------|--------|------|
| get_work_path | - | Path | 作品ディレクトリパスを取得 |
| initialize | - | None | Vault ディレクトリ構造とテンプレートファイルを作成（冪等性保証） |

---

## L1 公開API サマリ

### 統計情報

| カテゴリ | 件数 |
|---------|------|
| **モデル** | |
| - Enum/IntEnum | 8個 |
| - BaseModel クラス | 34個 |
| - dataclass | 2個 |
| **パーサー** | |
| - 例外 | 1個 |
| - 関数 | 6個 |
| **リポジトリ** | |
| - 基底・実装クラス | 5個 |
| - 例外 | 3個 |
| **Vault ユーティリティ** | |
| - クラス | 2個 |
| **総公開メソッド/関数数** | 68+ |

### エンティティ型別

| エンティティ | モデル | リポジトリ | 説明 |
|-----------|--------|-----------|------|
| Character | Character | CharacterRepository | キャラクター設定（フェーズ対応） |
| Episode | Episode | EpisodeRepository | エピソード（本文） |
| WorldSetting | WorldSetting | WorldSettingRepository | 世界観設定（フェーズ対応） |
| Foreshadowing | Foreshadowing | ForeshadowingRepository | 伏線管理（YAML レジストリ） |
| Plot | PlotL1, L2, L3 | （未実装リポジトリ） | 3階層プロット |
| Summary | SummaryL1, L2, L3 | （未実装リポジトリ） | 3階層サマリ |

### AI可視性制御

| クラス | 説明 |
|--------|------|
| AIVisibilityLevel | 4段階レベル（HIDDEN=0, AWARE=1, KNOW=2, USE=3） |
| AIVisibility | 個別設定（レベル + 禁止キーワード + 許可表現） |
| VisibilityConfig | 全体設定（vault/{work}/_ai_control/visibility.yaml） |
| ForeshadowingAIVisibility | 伏線向け設定 |
| AIVisibilitySettings | Character/WorldSetting 向け設定 |

### パーサー対応形式

| パーサー | 入力形式 | 出力形式 |
|---------|---------|---------|
| frontmatter | YAML + 本文 | dict + str（フォールバック対応） |
| markdown | Markdown 本文 | Section リスト |
| obsidian_link | [[target\|display]] | ObsidianLink |
| visibility_comment | `<!-- ai_visibility: N -->` | VisibilityMarker |

### ファイル形式

| タイプ | 形式 | パス例 |
|--------|------|--------|
| Character | Markdown + YAML frontmatter | `vault/{work}/characters/{name}.md` |
| Episode | Markdown + YAML frontmatter | `vault/{work}/episodes/ep_XXXX.md` |
| WorldSetting | Markdown + YAML frontmatter | `vault/{work}/world/{name}.md` |
| Foreshadowing | YAML レジストリ | `vault/{work}/_foreshadowing/registry.yaml` |
| Plot | Markdown + YAML frontmatter | `vault/{work}/_plot/L1_overall.md` など |

---

## 重要な実装特性

### Secure by Default

- `AIVisibilityLevel` デフォルト: **HIDDEN (0)**
- `VisibilityConfig.default_visibility` デフォルト: **HIDDEN (0)**
- 秘密情報 (`Secret`) の可視性デフォルト: **HIDDEN (0)**

### フォールバック処理

- Frontmatter パース失敗時も `parse_frontmatter_with_fallback` により生テキストとして保持
- 仕様書 03_data-model.md Section 7.2 に基づく実装

### 冪等性

- `VaultInitializer.initialize()` は既存ファイルを上書きしない
- テンプレートファイルは存在しない場合のみ作成

### Phase 管理

- Character と WorldSetting は複数フェーズに対応
- `current_phase` で現在のフェーズを指定
- Phase Filter による content フィルタリングは L2 フェーズで実装予定

---

## バージョン情報

- **Vault 仕様バージョン:** 1.0
- **YAML フォーマット:** UTF-8 with `allow_unicode: True`
- **Markdown フォーマット:** UTF-8 with frontmatter separator `---`

---

**報告日:** 2026-02-05  
**精度:** メソッドシグネチャレベル（実装詳細を除外）  
**カバレッジ:** 公開API 100%（プライベートメソッド `_` prefix 除外）
