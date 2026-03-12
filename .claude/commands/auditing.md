---
description: "AUDITINGフェーズを開始 - レビュー・リファクタリング・監査"
---

# AUDITINGフェーズ開始

あなたは今から **[AUDITING]** モードに入ります。

## 実行ステップ

1. **フェーズ状態を更新**
   - `.claude/current-phase.md` を `AUDITING` に更新する

2. **状態ファイルを確認**
   - `.claude/states/<feature>.json` を読み込む
   - `phase` が `BUILDING` で `current_task` が null（BUILDING 完了確認）
   - 状態ファイルの `phase` を `AUDITING` に更新

3. **必須ドキュメントを読み込む**
   - `docs/internal/03_QUALITY_STANDARDS.md` を精読
   - `docs/internal/02_DEVELOPMENT_FLOW.md` の Phase 3 を確認
   - 監査対象のコードと対応仕様書を読み込む

4. **AUDITINGルールを適用**
   - 品質基準への適合性を検証
   - "Broken Windows" の発見と修復
   - ドキュメントの整合性確認

5. **作業の進め方**
   - 品質監査には `quality-auditor` サブエージェントを推奨
   - 3 Agents Model で改善提案を検証
   - Context Compression が必要な場合は提案

## v4.0.0: 権限等級に基づく修正ルール

AUDITING フェーズでは権限等級（`.claude/rules/permission-levels.md`）に応じて修正が許可される:

- **PG級**: 自動修正可（フォーマット、typo、lint 違反等）
- **SE級**: 修正後に報告（テスト追加、内部リファクタリング等）
- **PM級**: 指摘のみ（修正禁止、承認ゲート）

## 監査チェックリスト

### コード品質
- [ ] 命名規則の一貫性
- [ ] エラーハンドリングの適切性
- [ ] パフォーマンス懸念の有無
- [ ] セキュリティリスクの有無

### Python 安全性（`.claude/rules/building-checklist.md` / R-7〜R-9 参照）
- [ ] 並列処理で共有可変オブジェクトを書き込んでいない（R-7）
- [ ] ミュータブル引数を防御コピーしている（R-8）
- [ ] `Optional[T]` の判定に `is not None` を使っている（R-9）
- [ ] `dict.get(key, default)` が有限集合キーに使われていない（R-6）

### コード明確性（Clarity over Brevity）
- [ ] ネストした三項演算子がない
- [ ] 過度に密なワンライナーがない
- [ ] デバッグ・拡張が容易な構造

### DRY・モジュール構造
- [ ] 同一ロジックが2ファイル以上にコピーされていない（R-10）
- [ ] `__init__.py` に `__all__` が定義され、公開 API が明示されている（S-2）
- [ ] `str` で済ませている引数・フィールドに `Literal` が使えないか確認（R-11）

### テスト衛生
- [ ] テストメソッドに `-> None` 型注釈がある（R-12）
- [ ] 遅い/不安定なテストに `@pytest.mark.slow` がある（R-12）
- [ ] 3ファイル以上で使うヘルパーが `conftest.py` に集約されている（R-12）
- [ ] テスト内にインライン import がない（R-12）

### ドキュメント整合性
- [ ] `docs/specs/` と実装の一致（A-5 参照）
- [ ] `docs/adr/` の決定事項が反映されている
- [ ] `docs/tasks/` のタスク状態が最新
- [ ] `.claude/` に追加・変更したファイルが `docs/internal/` に反映されている
- [ ] アーキテクチャ図・ディレクトリ構造が現状と一致している

### アーキテクチャ健全性
- [ ] 依存関係の適切性
- [ ] モジュール境界の明確さ
- [ ] 技術的負債の蓄積状況
- [ ] TODO/FIXME の棚卸し（完了済みタスクの TODO が残っていないか）

### 既存ルール適用漏れ点検（A-6）
- [ ] `.claude/rules/building-checklist.md` の R-1〜R-13 について grep/検索ベースで違反が残っていないか確認（目視のみの確認は禁止）

## 監査ポリシー（`.claude/rules/audit-fix-policy.md` 参照）

**A-1**: Critical / Warning / Info すべてに対応する。「Warning だから後回し」「Info だから無視」は禁止。

**A-2**: 対応不可 Issue は以下を明記する:
- 理由（技術的に着手不可能な根拠）
- 追跡方法（`docs/tasks/` 等）
- 暫定対策（あれば）

**A-3**: 修正後の再検証を実施する（テスト追加 → ruff → 全テスト）。

**A-4**: コード修正に伴う仕様ズレは `docs/specs/` と同一サイクル内で同時修正する。

**A-5**: 監査時に `docs/specs/` のデータモデル定義・アーキテクチャ図・Agent 定義の全件チェックを行う。

**A-6**: `building-checklist.md` の全ルール（R-1〜R-13）について grep/検索ベースで違反が残っていないか確認する。

## 成果物

監査結果は以下の形式で報告:

```markdown
# 監査レポート: [対象]

## サマリー
- 検出項目数: X件
- Critical: X件 / Warning: X件 / Info: X件

## Critical Issues
### [Issue-1]
- **場所**:
- **内容**:
- **推奨対応**:

## Warnings
...

## Documentation Sync Status
- specs: ✓/✗
- adr: ✓/✗
- tasks: ✓/✗

## 推奨アクション
1.
2.
```

## 監査完了と承認

監査完了時、ユーザーに承認を求める:

```
[監査] が完了しました。

成果物: docs/artifacts/audit-report-<feature>.md

確認後「承認」と入力してください。
修正が必要な場合は指示してください。
```

承認後、状態ファイルを更新し機能を完了状態にする。

## /full-review との使い分け

- `/auditing`: フェーズ切替。AUDITING モードに入り、手動で段階的に監査
- `/full-review`: ワンショット実行。並列監査 → 修正 → 検証を自動ループで完了

ワンショットで自動修正まで行いたい場合は `/full-review` を推奨。

## 確認メッセージ

以下を表示してユーザーに確認:

```
[AUDITING] フェーズを開始しました。

機能: [feature-name]
実装状態: [approved/未承認]

適用ルール:
- 品質基準への適合性検証
- ドキュメント整合性チェック（A-5）
- 既存ルール適用漏れ grep 点検（A-6）
- 技術的負債の棚卸し

読み込み済み:
- 03_QUALITY_STANDARDS.md
- 02_DEVELOPMENT_FLOW.md (Phase 3)
- .claude/rules/audit-fix-policy.md (A-1〜A-7)
- .claude/rules/phase-rules.md

何を監査しますか？
（対象ファイル/ディレクトリを指定してください）
```
