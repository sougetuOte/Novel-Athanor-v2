---
description: シーンのドラフトを生成する統合パイプライン（コンテキスト構築→執筆→レビュー→品質評価）
allowed-tools: Bash, Read, Write, Glob, Grep, Task
---

# /draft-scene

シーンのドラフトテキストを生成する統合パイプラインを実行します。

## 引数

- `$ARGUMENTS` — `[vault_root] [episode_id] [--sequence SEQ] [--chapter CH] [--phase PHASE] [--word-count N] [--pov POV] [--mood MOOD] [--instructions "特別指示"]`
  - vault_root: vault ルートパス（例: `vault/my_novel`）
  - episode_id: エピソード ID（例: `010`）
  - --sequence: シーケンス ID（省略可）
  - --chapter: チャプター ID（省略可）
  - --phase: 現在フェーズ（省略可）
  - --word-count: 目標文字数（デフォルト: 3000）
  - --pov: 視点（デフォルト: 三人称限定視点）
  - --mood: ムード（省略可）
  - --instructions: 特別指示（省略可）

## パイプライン実行フロー

### Step 1: コンテキスト構築

Python CLI でシーンのコンテキストを構築する。

```bash
python -m src.agents.tools build-context \
  --vault-root $VAULT_ROOT \
  --episode $EPISODE_ID \
  [--sequence $SEQUENCE] \
  [--chapter $CHAPTER] \
  [--phase $PHASE] \
  [--work $WORK_NAME]
```

`--work` は省略可能。省略時は `vault-root` のディレクトリ名が使用される。
伏線レジストリ（`_foreshadowing/registry.yaml`）が存在する場合に自動的に伏線指示と禁止キーワードが取得される。

出力 JSON を確認し:
- **errors あり** → パイプラインを停止し、ユーザーにエラー内容を報告
- **warnings あり** → 警告をログ出力して続行

### Step 2: コンテキストのフォーマット

JSON 結果を Markdown に変換する。

```bash
python -m src.agents.tools format-context --input context_result.json
```

出力された Markdown テキストを後続ステップで使用する。

### Step 3: Ghost Writer によるドラフト生成

ghost-writer サブエージェントを spawn し、以下を task メッセージとして渡す:

1. Step 2 で生成したコンテキスト Markdown
2. シーン要件:
   - episode_id, sequence_id, chapter_id
   - word_count（目標文字数）
   - pov（視点）
   - mood（ムード、指定時のみ）
   - special_instructions（特別指示、指定時のみ）
3. 禁止キーワードリスト（コンテキストから抽出）
4. 伏線指示書（コンテキストから抽出）

Ghost Writer の出力（ドラフトテキスト）を受け取る。

### Step 4: アルゴリズミックレビュー

ドラフトテキストに対して禁止キーワードの機械的チェックを実行する。

```bash
python -m src.agents.tools check-review \
  --draft draft.txt \
  --keywords "禁止KW1,禁止KW2,..."
```

- **approved** → Step 5 へ
- **rejected** → Step 6（リトライ）へ

### Step 5: LLM レビュー

reviewer サブエージェントを spawn し、以下を渡す:

1. ドラフトテキスト
2. コンテキスト（秘密情報、伏線制約など）
3. Step 4 のアルゴリズミックチェック結果

Reviewer は以下を確認:
- 秘密内容との類似度
- 伏線制約チェック（forbidden_expressions、subtlety_target）
- 設定文直接引用チェック

結果:
- **approved / warning** → Step 7 へ
- **rejected** → Step 6（リトライ）へ

### Step 6: リトライ or Human Fallback

rejected の場合、Ghost Writer にレビュー結果（問題箇所と修正提案）を渡して再生成を依頼する。

- リトライ回数 < 3 → Step 3 に戻る（レビュー指摘を修正指示として追加）
- リトライ回数 >= 3 → **Human Fallback**: ユーザーに差し戻す

```
Human Fallback

自動修正の上限（3回）に達しました。
以下の問題を手動で確認・修正してください:

[最後のレビュー結果]
[ドラフトテキストの保存先]
```

### Step 7: 品質評価

quality-agent サブエージェントを spawn し、以下を渡す:

1. 最終ドラフトテキスト
2. シーン要件
3. プロット・キャラクター情報（品質評価の基準として）
4. スタイルガイド（あれば）

Quality Agent の評価結果（7スコア + 総合 + 改善提案）を受け取る。

### Step 8: 結果報告

ユーザーに以下を報告する:

```
/draft-scene 完了

## ドラフト
- ファイル: [保存先パス]
- 文字数: [実際の文字数] / [目標文字数]

## レビュー結果
- ステータス: [approved / warning]
- 指摘事項: [件数]（あれば詳細を列挙）

## 品質評価
| 観点 | スコア |
|------|--------|
| coherence | X.XX |
| pacing | X.XX |
| prose | X.XX |
| character_score | X.XX |
| style | X.XX |
| reader_excitement | X.XX |
| emotional_resonance | X.XX |
| **overall** | **X.XX** |

- 総合評価: [excellent / good / acceptable / needs_improvement]
- 改善提案: [あれば列挙]

## リトライ回数
- [N] 回（0 = 一発 approved）
```

## ドラフト保存先

生成したドラフトは以下に保存する:

```
$VAULT_ROOT/episodes/ep[EPISODE_ID]/drafts/draft_[timestamp].md
```

`drafts/` ディレクトリが存在しない場合は作成する。

## 注意事項

- コンテキスト構築でエラーが発生した場合は、原因を調査してからリトライする（vault構造の問題が多い）
- Ghost Writer への指示にはコンテキスト全文を含めること（部分的な情報では品質が下がる）
- レビューの rejected 理由は Ghost Writer への再指示に必ず含めること
- 品質評価の overall が 0.5 未満の場合は、ユーザーにリライトを提案すること

## 参照ドキュメント

- `docs/memos/2026-02-05-l4-core-design.md` (Section 7.4: /draft-scene コマンド設計)
- `.claude/agents/ghost-writer.md` (Ghost Writer エージェント定義)
- `.claude/agents/reviewer.md` (Reviewer エージェント定義)
- `.claude/agents/quality-agent.md` (Quality Agent エージェント定義)
- `src/agents/config.py` (MAX_REVIEW_RETRIES, QUALITY_THRESHOLDS)
