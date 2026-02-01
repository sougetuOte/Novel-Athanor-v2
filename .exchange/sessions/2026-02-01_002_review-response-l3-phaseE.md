# レビュー回答: L3 Phase E - 伏線・Visibility 統合 実装監査

## Meta
| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-01_002 |
| 日時 | 2026-02-01 |
| レビュアー | Antigravity |
| 判定 | **A** |

## 1. 伏線システム連携評価
*   **ForeshadowingRepository との連携**: `ForeshadowingIdentifier` および `InstructionGeneratorImpl` は、リポジトリを通じて適切に伏線データを取得しています。`InstructionGeneratorImpl._generate_instruction` での `try-except` ブロックによる例外処理（WARN-002対応）も適切に実装されており、堅牢性が向上しています。
*   **アクション判定**: `ForeshadowingIdentifier` 内のロジック（`_should_plant`, `_should_reinforce`, `_should_hint`）は、仕様書のステータス遷移および条件と一致しており、適切です。
*   **禁止キーワード収集**: `ForbiddenKeywordCollector` が `ForeshadowInstructions` からキーワードを収集するフローは、設計通り機能しています。

## 2. 可視性システム連携評価
*   **VisibilityFilteringService**: L2 の `VisibilityController` を利用してコンテンツをフィルタリングする設計は、責務の分離が明確で適切です。
*   **Hint 収集**: `VisibilityResult` から `AWARE` レベルの情報をヒントとして抽出するロジックは、AI情報制御仕様の「Level 1: 認識のみ」および「Level 2: 内容認識（暗示）」の要件を満たしています。
*   **HintCollector**: 伏線システムからの HINT アクションと、可視性システムからの AWARE ヒントを統合し、優先度順にソートする仕組みは、Ghost Writer に渡すコンテキストの質を高める上で重要かつ適切に実装されています。

## 3. 仕様書整合性評価
| 仕様書 | 確認結果 |
|--------|----------|
| `04_ai-information-control.md` | AI可視性レベル（0-3）の挙動（除外、ヒント化、通常使用）が `VisibilityFilteringService` で正しく実装されています。 |
| `05_foreshadowing-system.md` | 伏線指示書の構造（Action, Note, Subtlety）およびライフサイクル（Registered -> Planted -> Reinforced -> Revealed）に基づくアクション生成は仕様通りです。 |
| `08_agent-design.md` | `ForbiddenKeywordCollector` における複数ソース（伏線、可視性設定、グローバル）からの禁止キーワード統合は、Section 8 の要件を満たしています。 |

## 4. 設計決定の評価

### 4.1 ForbiddenKeywordCollector の3ソース統合
**評価: 適切**
禁止キーワードは「いずれかのソースで禁止されていれば使用不可（Union）」であるべきため、ソース間の上書き優先度ではなく、全てのソースから収集して統合・重複排除する現在のアプローチは論理的に正しいです。`ForbiddenKeywordResult` でソース元を追跡できる構造もデバッグ容易性の観点から評価できます。

### 4.2 HintCollector の優先度計算
**評価: 適切**
`metrics` ベースの優先度計算（伏線 > 可視性 > キャラ > 世界観）は、物語の進行制御（伏線）を静的な設定情報よりも優先するという意図が明確であり、妥当です。また、`strength` という係数を設けることで、個別のヒントの重要度も反映できる柔軟性があります。

### 4.3 VisibilityFilteringService と L2 連携
**評価: 適切**
L3 側で再実装を行わず、L2 の `VisibilityController` に依存することで、判定ロジックの一元化が図られています。L3 は「Context Builder としてのデータの取り回し（コンテキストオブジェクトへの詰め替え）」に集中できており、責務分担が綺麗です。

## 5. 問題点・指摘事項

### [Info]
| No. | 対象ファイル | 問題内容 | 推奨対応 |
|-----|-------------|---------|---------|
| 1 | `visibility_context.py` | `VisibilityHint` の `source_section` フィールドが複合情報（category.entity）を持っている。 | 現状は `HintCollector` で簡易にパースされているため問題ありませんが、将来的にセクション名のルールが変わった場合に脆くなる可能性があります。将来的なリファクタリングで `category`, `entity_id` フィールドへの分割を検討しても良いでしょう。 |

## 6. 質問への回答

### 6.1 InstructionGenerator Protocol の変更
**回答: 妥当です**
変更後の `generate(self, scene: SceneIdentifier, appearing_characters: ...)` は、呼び出し元（ContinuityDirectorなど）が「どの伏線データを渡すべきか」を知る必要をなくし、`InstructionGenerator`（およびその背後にあるRepository）にデータ取得の責務をカプセル化しています。これにより、呼び出し側のコードがシンプルになり、凝集度が高まりました。`appearing_characters` は HINT 判定に必要な最小限の外部コンテキストであり、引数として適切です。

### 6.2 VisibilityHint のフィールド設計
**回答: 現状維持で問題ありませんが、将来的な改善候補です**
現状の `source_section` (例: "character.Alice") 文字列パースで機能要件は満たせています。前述の通り、型安全性と構造化の観点からは `category` と `entity_id` を分けるのが理想ですが、現在の複雑度であれば、文字列処理によるオーバーヘッドやリスクは許容範囲内です。

### 6.3 HINT アクションのみ HintCollector で収集
**回答: 非常に適切です**
`PLANT` や `REINFORCE` は、Ghost Writer に対して「このシーンで必ず実行すべき能動的なタスク」として指示されるべきものです。一方、`HINT` は「執筆の際に頭の片隅に置いておくべき文脈情報」としての性質が強く、Visibility システムからの「気配・暗示」と性質が近いです。
これらを意図的に分離し、`HINT` を `HintCollector` 経由で「ヒント情報」として統合、`PLANT`/`REINFORCE` を「伏線指示書」として独立させる設計は、AIへのプロンプト構成を明確にする上で優れた判断です。

## 7. 総合評価
**判定: A (承認)**

Phase E の実装は仕様書および設計意図を正確に反映しており、品質も高い水準にあります。特に、L2 の機能を適切に再利用しながら L3 独自のコンテキスト構築ロジック（ヒント収集、禁止キーワード統合）を実現している点は評価できます。コードの簡潔化や警告対応も行われており、マージに支障はありません。

## 8. 推奨事項
*   **Phase F への移行**: 予定通り Phase F（Context Builder ファサード）の実装に進んでください。
*   **統合テストの拡充**: Phase F で ContextBuilder 全体が組み上がった段階で、実際のデータ（Yamlファイル）を用いたエンドツーエンドに近いテストケースを行い、各Collectorの連携を確認することを推奨します。
