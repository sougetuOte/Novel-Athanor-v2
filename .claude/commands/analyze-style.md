---
description: 既存エピソードの文体を分析し、StyleGuide/StyleProfile を自動生成する
allowed-tools: Bash, Read, Write, Glob, Grep, Task
---

# /analyze-style

作品の既存エピソードを分析し、StyleGuide（定性）と StyleProfile（定量）を自動生成します。

## 引数

- `$ARGUMENTS` — `[作品名] [--episodes 1,2,3] [--update]`
  - 作品名: vault 内の作品ディレクトリ名
  - --episodes: 分析対象エピソード番号（省略時は全エピソード）
  - --update: 既存ガイドがあれば差分更新モード

## ワークフロー

### Step 1: エピソード収集 + 定量分析

```bash
python -m src.agents.tools analyze-style \
  --vault vault/$WORK --work $WORK [--episodes $EPISODES]
```

出力されたプロンプトテキストを確認する。

### Step 2: Style Agent に委任

style-agent サブエージェントに以下を委任:
- Step 1 の出力テキストを入力として渡す
- StyleGuide（定性分析）の生成
- StyleProfile（定量分析）の生成

### Step 3: 結果の保存

Style Agent の出力を受け取り、vault に保存:

```bash
python -m src.agents.tools save-style \
  --vault vault/$WORK --work $WORK \
  --type guide --input /tmp/guide_output.txt

python -m src.agents.tools save-style \
  --vault vault/$WORK --work $WORK \
  --type profile --input /tmp/profile_output.txt
```

### Step 4: ユーザーに報告

生成された StyleGuide / StyleProfile のサマリを表示:
- POV、時制、主な文体特徴
- 平均文長、会話比率、TTR
- 改善推奨事項（あれば）
