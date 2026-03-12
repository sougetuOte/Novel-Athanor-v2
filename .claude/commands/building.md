---
description: "BUILDINGフェーズを開始 - TDD実装サイクル"
---

# BUILDINGフェーズ開始

あなたは今から **[BUILDING]** モードに入ります。

## 実行ステップ

1. **フェーズ状態を更新**
   - `.claude/current-phase.md` を `BUILDING` に更新する

2. **状態ファイルを確認**
   - `.claude/states/<feature>.json` を読み込む
   - PLANNING の全サブフェーズ（requirements, design, tasks）が approved か確認
   - 未承認があれば警告し、PLANNING に戻ることを提案

3. **必須ドキュメントを読み込む**
   - `docs/internal/02_DEVELOPMENT_FLOW.md` の Phase 2 を精読
   - `docs/internal/03_QUALITY_STANDARDS.md` を確認
   - 関連する `docs/specs/` の仕様書を読み込む

4. **状態ファイルを更新**
   - `phase` を `BUILDING` に更新
   - `current_task` を実装対象タスクIDに更新

5. **BUILDINGルールを適用**
   - **TDDサイクル厳守**: Red → Green → Refactor
   - 仕様書とコードの同期は絶対
   - 1サイクル完了ごとにユーザーに報告

6. **作業の進め方**
   - TDD実装には `tdd-developer` サブエージェントを推奨
   - 実装前に必ず `docs/specs/` の対応仕様を確認
   - コード変更時は対応ドキュメントも同時更新（Atomic Commit）

## 前提条件チェック

BUILDING に入る前に以下を確認:

```
PLANNING 承認状態:
- requirements: [approved/未承認]
- design: [approved/未承認]
- tasks: [approved/未承認]
```

未承認がある場合:
```
⚠️ BUILDING に移行できません

以下のサブフェーズが未承認です:
- [未承認サブフェーズ]

/planning で承認を完了してください。
```

## TDDサイクル（t-wada style）

**重要**: 各ステップで `.claude/rules/building-checklist.md`（R-1〜R-12, S-1〜S-2）のルールを適用すること。

### Step 1: Spec & Task Update
- コードを書く前に `docs/specs/` の更新案を提示

### Step 2: Red (Test First)
- 失敗するテストを先に書く
- テストは「実行可能な仕様書」
- **[R-4]** タスクの FR 番号をテスト docstring に転記し、各 FR に最低 1 テスト対応を確認
- **[R-5]** 異常系・エラーパス・境界値のテストも Red で書く
- **[R-12]** テストメソッドに `-> None` 型注釈を付ける。遅い/不安定なテストには `@pytest.mark.slow` を付ける。3ファイル以上で使うヘルパーは `conftest.py` に集約する。インライン import 禁止

### Step 3: Green (Minimal Implementation)
- テストを通す最小限のコードを実装
- 美しさより速さを優先
- **[R-2]** 3 分岐以上の有限値セットは dict ディスパッチ（if-chain 禁止）
- **[R-3]** 定数を定義したら同サイクル内で使用（未参照定数を残さない）
- **[R-6]** else/default のデフォルト値は正当な理由がなければ `raise ValueError`。`dict.get(key, default)` は有限セットキーには使わず `dict[key]` を使う
- **[R-7]** 並列処理で共有オブジェクトを複数スレッドから書き込まない。各スレッドにローカルな結果オブジェクトを持たせ、メインスレッドでマージする
- **[R-8]** リスト・辞書の引数は防御コピーする（`list(arg)` 等）。デフォルト引数に `[]`/`{}` を使わない
- **[R-9]** `Optional[T]` の判定は `if x is not None:` を使う（`if x:` 禁止）
- **[R-10]** 同じロジックが2ファイル以上に出現したら `_utils.py` 等に抽出する
- **[R-11]** 取りうる値が有限集合の場合、`str` ではなく `Literal["a", "b"]` を使う

### Step 3.5: Post-Green Verification（Green 直後）
- **[R-1]** 対応 FR/設計仕様を**再読**し、フィールド名・定数値・文言の文字単位一致を照合
- **[R-5]** `pytest --cov` で未カバー行を確認し、テスト必要な行を追加
- **[S-1]** 新しい定数・メソッド・スキーマを追加した場合、`docs/specs/` の対応セクションに記載があるか確認。記載がなければ同サイクル内で仕様を更新する
- **[S-2]** 新しいパッケージやモジュールを追加した場合、`__init__.py` に `__all__` を定義し、公開 API を明示的にエクスポートする

### Step 4: Refactor
- Green になってから設計を改善
- 重複排除、可読性向上

### Step 5: Commit & Review
- ユーザーに報告
- 必要に応じて `docs/memos/walkthrough-<feature>.md` に検証結果をまとめる

## TDD 内省パイプライン（v4.0.0 Wave 4 実装済み）

BUILDING フェーズでの TDD サイクル中、テスト失敗→成功のパターンは PostToolUse hook によって `.claude/tdd-patterns.log` に自動記録される。
閾値（3回）に達したパターンは `/pattern-review` コマンドで審査し、承認されれば `.claude/rules/auto-generated/` にルールとして昇格する。
詳細: `.claude/rules/auto-generated/trust-model.md`

## 禁止事項

- 仕様書なしでの実装開始
- テストなしでの本実装
- ドキュメント更新なしのコード変更
- **PLANNING が未承認のまま実装を開始すること**

## フェーズ終了条件

以下を満たしたら `/auditing` でAUDITINGフェーズに移行:

- [ ] 全テストがパス
- [ ] 仕様書とコードが同期している
- [ ] `docs/memos/walkthrough-<feature>.md` で検証完了（任意）
- [ ] 状態ファイルの `current_task` を null に、`completed_tasks` にタスクIDを追加

## 確認メッセージ

以下を表示してユーザーに確認:

```
[BUILDING] フェーズを開始しました。

PLANNING 承認状態:
- requirements: ✅ approved
- design: ✅ approved
- tasks: ✅ approved

適用ルール:
- TDDサイクル: Red → Green → Refactor
- ドキュメント同期: 必須
- 報告: 1サイクルごと
- building-checklist: R-1〜R-12, S-1〜S-2 適用

読み込み済み:
- 02_DEVELOPMENT_FLOW.md (Phase 2)
- 03_QUALITY_STANDARDS.md
- .claude/rules/building-checklist.md

どのタスクから実装しますか？
```
