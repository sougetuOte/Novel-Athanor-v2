# レビュー回答: L3 Phase D - Context Collectors 実装監査

## Meta
| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-01_001 |
| 日時 | 2026-02-01 |
| レビュアー | Antigravity |
| 判定 | A |

## 1. Protocol 整合性評価
全ての Collector (`PlotCollector`, `SummaryCollector`, `CharacterCollector`, `WorldSettingCollector`, `StyleGuideCollector`) は `collect_as_string` メソッドを実装しており、`ContextCollector` Protocol を満たしています。
また、戻り値の型定義（`str | None`）も適切です。

## 2. L2 連携評価
- `CharacterCollector` は `src/models/character.py` の `Character` モデルを使用し、フロントマターのパースを行っています。
- `WorldSettingCollector` は `src/models/world_setting.py` の `WorldSetting` モデルを使用しています。
- 各 `PhaseFilter` クラスが正しく活用され、`Phase` モデルや `AIVisibilitySettings` が考慮されていることを確認しました。連携は適切です。

## 3. 仕様書整合性評価
- `08_agent-design.md` の Context Builder の責務（必要な情報の収集とフィルタリング）と整合しています。
- `load_priority` (REQUIRED/OPTIONAL) の制御により、Section 8.4 の "Graceful Degradation" が Collector レベルで実装されています。
    - 重要度が高い `plot_l3` や `style_guide.default` は `REQUIRED`。
    - 付加的な `summary` や過去情報は `OPTIONAL`。
- この実装方針は適切です。

## 4. 設計決定の評価

### 4.1 二重メソッド設計
**評価: 非常に適切 (Excellent)**
`collect()` で構造化データを返し、`collect_as_string()` で文字列を返す設計は、将来的な拡張性と現在のプロトコル遵守を両立させる良い設計です。
`ContextIntegratorImpl` が動的に `collect()` の存在を確認して最適化されたパス（個別のフィールドへの格納）を使用し、失敗時や未実装時に `collect_as_string()` にフォールバックする仕組みは堅牢です。

### 4.2 _load_file ヘルパーパターン
**評価: 適切 (Good)**
全 Collector で共通の処理を抽象化しており、DRY原則に従っています。将来的にエラーハンドリングやログ出力を強化する際、一箇所の修正で済むため保守性が高いです。

### 4.3 PhaseFilter 累積ロジックの使用
**評価: 適切 (Good)**
`CharacterCollector` および `WorldSettingCollector` は `phase_filter.to_context_string` を介してフィルタリングを行っています。
`phase_filter` 内部で `applicable_phases = set(self.phase_order[: phase_idx + 1])` として累積的にフェーズを扱っているため、過去のフェーズの情報も正しく含まれます。

## 5. 問題点・指摘事項

### [重要度: Info]
| No. | 対象ファイル | 問題内容 | 推奨対応 |
|-----|-------------|---------|---------|
| 1 | `context_integrator.py` | キャラクターと世界観設定が全て `_all` キーに結合して格納されている。 | `Plot` と同様に `collect()` メソッドの結果（Dict）を使い、個別のキーとして `FilteredContext` に格納することを推奨。 |

## 6. 質問への回答

### 6.1 ContextIntegratorImpl の統合方法
**回答:** `hasattr` + `isinstance` による動的ディスパッチは、Pythonにおいては一般的かつ有効な手法であり、現段階では適切です。
より厳密な型安全性が必要な場合は、`ContextCollector` を継承した `StructuredContextCollector` Protocol を定義し、`collect` メソッドを明示する手法もありますが、現在の実装でも十分に堅牢です。現状のままで問題ありません。

### 6.2 Character/WorldSetting の統合方法
**回答:** 現在の `"_all"` への一括格納は、`FilteredContext` の定義（`characters: dict[str, str]`）からすると、やや構造化のメリットを活かしきれていません。
`collect_as_string` は文字列として結合してしまうため、将来的に「特定のキャラクターの情報のみを抽出してPromptに含める」といった制御が難しくなります。
「5. 問題点」で指摘した通り、`_integrate_character` メソッドなどを追加し、`CharacterContext.characters` (Dict) の内容をそのまま `FilteredContext.characters` にマージする実装への変更を推奨します。

### 6.3 StyleGuideCollector の merged プロパティ
**回答:** 適切です。
`default` の後に `override` を結合する順序は、「一般的なルールの後に、例外・具体的なルールを記述する」という自然言語処理（およびLLMへの指示）のセオリーに適しています。書式も明確で問題ありません。

## 7. 総合評価
**判定: A (承認)**

Collectorの実装は非常に高品質で、Protocol設計、エラーハンドリング、L2モデル連携のすべてにおいて基準を満たしています。
特に「二重メソッド設計」による構造化データの保持とプロトコル準拠の両立は高く評価できます。
Infoレベルの指摘事項（キャラクター情報のDict保持）は、必須ではありませんが、今後の柔軟性のために検討してください。

## 8. 推奨事項
1. **Collector統合の構造化**: `ContextIntegratorImpl` において、`CharacterCollector` と `WorldSettingCollector` も `PlotCollector` と同様に、可能であれば `collect()` メソッドを使用して構造化データ（Dict）のまま統合するように改修することを推奨します。これにより `FilteredContext` が持つ辞書構造を最大限に活用できます。
