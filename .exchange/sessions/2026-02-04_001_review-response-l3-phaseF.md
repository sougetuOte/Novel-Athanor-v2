# レビュー回答: L3 Phase F - ContextBuilder ファサード 実装監査

## Meta
| 項目 | 値 |
|------|-----|
| Session ID | 2026-02-04_001 |
| 日時 | 2026-02-04 |
| レビュアー | Antigravity |
| 判定 | A (承認) |

---

## 1. ファサードパターン評価

### 1.1 単一エントリーポイント
`ContextBuilder` が L3 の複雑なサブシステム（Collector, Integrator, Filter, L2 Services）を完全に隠蔽し、`build_context(scene)` という極めてシンプルなインターフェースを提供している点を高く評価します。
これにより、L4 エージェント（Continuity Director, Ghost Writer）の実装コストが大幅に低減されます。

### 1.2 内部コンポーネントの隠蔽
内部で `PlotCollector`, `CharacterCollector` 等を適切に初期化・管理しており、外部に詳細を漏らしていません。テストコードにおいても、内部コンポーネントを意識せずにテスト記述ができていることが確認できました。

---

## 2. L2 サービスとの連携評価

### 2.1 疎結合な統合
`VisibilityController` および `ForeshadowingRepository` を Optional として扱い、存在しない場合でもシステムが停止しない（Good/Graceful Degradation）設計は堅牢です。
特に `instruction_generator.py` における Protocol パターン（`InstructionGenerator`）の定義と実装の分離は、テスト容易性と将来の拡張性を担保しています。

---

## 3. 仕様書整合性評価

### 3.1 Context Builder の責務 (Section 2.4)
`02_architecture.md` に定義された「Context Builder」の責務を満たしています。
AoT Parallel Collector については将来的な課題となっていますが、現在の実装は同期処理として正しく動作しています。

### 3.2 AI情報の制御
`04_ai-information-control.md` に基づき、Level 2 の禁止キーワード収集と、Level 1-2 のヒント収集が正しく実装されています。
`hint_collector.py` が Visibility と Foreshadowing の両ソースからヒントを統合し、優先度（priority）計算を行っている点は、Ghost Writer に適切なコンテキストを与える上で重要です。

---

## 4. 設計決定の評価

### 4.1 Hybrid DI パターン
**承認**: 適切です。
L3 はコンポーネント数が多いため、全てを外部注入（Pure DI）にすると利用側のボイラープレートコードが肥大化します。
「デフォルト構成は内部で自動構築し、カスタムが必要な場合のみ注入する」という Hybrid なアプローチは、ライブラリとしての使い勝手とテスト容易性のバランスが取れた実用的な解です。test_context_builder.py T4 ケースでもこの利点が活かされています。

### 4.2 ContextBuildResult の構成
**承認**: 適切です。
Phase E の成果物である `visibility_context` や `hints` を含めるのは、ContextBuilder の役割（L4 への完全な情報の提供）として必然です。
`errors` が現在未使用である点については、将来的な拡張（例えば外部API連携時のタイムアウト等）への備えとして維持することを推奨します。シグネチャを変更せずにエラー情報を追加できる余地を残すのは良いプラクティスです。

### 4.3 キャッシュ戦略
**条件付き承認**: 基本的に問題ありませんが、改善の余地があります。
- `current_phase` のキー除外について: 現在のロジックでは Foreshadowing は Episode ID ベースで管理されているため、Phase に依存せず整合性は保たれます。
- **改善提案**: メモリリーク防止のため、`lru_cache` のようなサイズ制限付きキャッシュ、あるいは定期的なパージ機構（例えばエピソード切り替え時にクリアするなど）の導入を検討してください。現状は `clear_all_caches` メソッドが用意されているため、これを適切に呼び出す運用（Continuity Director 側で管理）があれば問題ありません。

### 4.4 ExpressionFilter の除外
**承認**: 妥当です。
Reviewer Agent の責務である「能動的なフィルタリング・書き換え」を L3 に持ち込むべきではありません。L3 は「何が禁止されているか」というデータ（Forbidden Keywords）を提供するまでに留めるべきです。この境界線の判断はアーキテクチャ的に正しいです。

---

## 5. 問題点・指摘事項

### Warning (改善推奨)

| No. | 対象ファイル | 問題内容 | 推奨対応 |
|-----|-------------|---------|---------|
| 1 | `context_builder.py` | キャッシュのサイズ制限欠如 | Python 標準の `@functools.lru_cache` を利用するか、明示的なサイズ上限を設定することを推奨します（Long-running process でのメモリ圧迫予防）。 |
| 2 | `context_builder.py` | `build_context` 内の例外ハンドリングが汎用的 (`Exception`) | 特定の例外（FileNotFoundError, ValidationError 等）を捕捉し、予期せぬシステムエラー（NameError 等）は上位に伝播させた方がデバッグしやすい場合があります。 |

---

## 6. 質問への回答

### 6.1 build_context() のオーケストレーション
**適切です。**
順序依存関係（Foreshadowing Instructions → Forbidden Keywords → Hints）を正しく解決しています。
1. Integration (Base Data)
2. Foreshadowing (Source of Forbidden/Hints)
3. Forbidden (Dep: Foreshadowing)
4. Visibility (Dep: Base Data)
5. Hints (Dep: Visibility + Foreshadowing)
この順序でなければデータフローが成立しません。

### 6.2 Graceful Degradation の一貫性
**十分です。**
テスト `test_context_builder_build.py` の T9 ケース等で確認されている通り、各コンポーネントの不在や失敗が全体のクラッシュにつながらないよう設計されています。`success` フラグと `warnings` リストによる通知も適切です。

### 6.3 プロンプトフォーマット (NONE 指示の扱い)
**現状のままでAI制御の観点から正しいです。**
アクションが `NONE` の伏線は「今回は触れるべきではない（あるいはまだ存在しない）」ものです。これをプロンプトに「NONE: 〜」と明記すると、**Pink Elephant Paradox**（否定命令をすると逆に意識してしまう現象）を引き起こすリスクがあります。
AI 情報制御仕様（04_ai-information-control.md）の基本方針「Level 0 は存在自体を伝えない」と同様に、アクションなしのものはプロンプトから完全に除外するのが安全です。

---

## 7. 総合評価

L3 Context Builder レイヤーの集大成として、非常に高品質な実装です。
複雑な依存関係を整理し、L4 から使いやすいインターフェースを提供できています。
特に、以下の点が優れています：
- **堅牢性**: 外部依存（L2）がなくても動く
- **責務の分離**: L3（データ準備）と L4（実行・判断）の境界が明確
- **テスト可能性**: すべてのコンポーネントが単体・結合テスト可能

これで L3 レイヤーの実装完了を承認します。L4 Agent Layer の実装へ進んでください。
