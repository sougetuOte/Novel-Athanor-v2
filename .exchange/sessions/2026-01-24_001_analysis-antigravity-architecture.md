# Architecture Analysis: Auto-Novel-Athanor

## Meta

| Item   | Value                                         |
| ------ | --------------------------------------------- |
| Author | Antigravity (Living Architect)                |
| Date   | 2026-01-24                                    |
| Target | Novel-Athanor, NovelWriter, 302_novel_writing |
| Status | Draft                                         |

---

## 1. アーキテクチャ観点

### 1.1 Novel-Athanor

**評価**: **[Markdown-Centric / Human-in-the-Loop]**
ファイルシステムベースのMarkdown管理システムであり、最も「作家の思考プロセス」に近い構造をしています。

- **全体構造**: `vault/` 配下に作品ごとのディレクトリを持ち、設定・プロット・本文を分離管理。
- **データフロー**: 人間がコマンド (`/draft-scene` 等) を発行 -> System Promptが `vault` 内の関連ファイルをRAG的に取得 -> コンテキスト組み立て -> 生成 -> ファイル書き込み。
- **拡張性**: 高い。Markdownテンプレート (`vault/templates/`) を修正するだけでデータモデルを変更可能。
- **技術スタック**: 主体は Markdown + プロンプトエンジニアリング。実行環境として Claude Code (CLI) を想定。

**隠れた長所**: Git等のバージョン管理システムとの親和性が極めて高い。Diffが読みやすく、変更履歴がそのまま創作の軌跡になる。

### 1.2 NovelWriter

**評価**: **[Agent-Based / Code-Heavy]**
Pythonによる本格的なマルチエージェントシステム。自律性が高く、分析・提案機能に優れています。

- **全体構造**: `core/` にビジネスロジック、`agents/` にエージェント定義を持つ典型的なPythonアプリケーション。
- **データフロー**: `AdaptivePlanningAgent` が `story_data` (Dict) を受け取り、分析 (`analyze_story_arc`) 結果を `ArcAnalysis` オブジェクトとして返す。
- **拡張性**: Pythonのクラス継承によりロジックの拡張は容易だが、データ構造の変更はコード修正を伴う。
- **技術スタック**: Python, Pydantic/Dataclasses (推測), AI SDK。

**隠れた短所**: ユーザーの介入ポイントが「設定ファイルの編集」ではなく「コード/パラメータの調整」になりがちで、非エンジニアの作家にはハードルが高い可能性がある。

### 1.3 302_novel_writing

**評価**: **[Web-Application / Prompt-Template-Driven]**
Next.js製のWebアプリケーション。即時性とUI/UXに優れるが、長編管理には不向き。

- **全体構造**: フロントエンド主導。`src/app` 内のコンポーネントが直接サーバースアクション (`service.ts`) を呼び出す。
- **データフロー**: フォーム入力 -> 巨大なテンプレートプロンプト (`prompt.ts`) への埋め込み -> AI生成 -> ストリーミング表示。
- **拡張性**: 新しいジャンルやスタイルを追加するには、コード内の定数ファイル (`fantasyRomance.ts` 等) を追加する必要がある。
- **技術スタック**: TypeScript, Next.js, Vercel AI SDK。

**特徴**: 多言語対応 (i18n) が強固に組み込まれている。

### 1.4 Claude Codeとの差異・補完

Claude Codeの解析は正確ですが、以下の視点が不足しています：

- **NovelWriterの分析深度**: 単なる自動生成だけでなく、`ArcAnalysis` クラスによる「定量的評価（Pacing Score等）」の仕組みは、新システムの「品質管理」にそのまま転用可能なレベルで完成度が高いです。
- **302_novel_writingのプロンプト構造**: 単純なテキスト生成ではなく、XMLタグ (`<input>`, `<output_format>`) を活用した構造化プロンプト（`advanceRolePrompt` 等）を採用しており、これはNovel-Athanorのプロンプト設計にも取り入れるべきベストプラクティスです。

---

## 2. データモデル観点

### 2.1 Novel-Athanor

**評価**: **[Hierarchical Document Model]**

- **構造**: L1 (Series/Volume) -> L2 (Chapter) -> L3 (Sequence) の3層構造。
- **整合性**: **Phase Management** により、時系列によるキャラクター状態の変化（物語開始時 -> 覚醒後）を管理している点が秀逸。
- **課題**: 伏線管理が `plot_L1.md` 内の単純なテーブルのみであり、L3レベルの具体的な描写とのリンクがない。

### 2.2 NovelWriter

**評価**: **[Object-Oriented / Metric-Driven]**

- **構造**: `story_data` 辞書オブジェクトを中心に、`chapters`, `scenes` などのリストを持つインメモリ構造。
- **特徴**: `ArcAnalysis` クラスに見られるように、物語を「数値（Metrics）」と「状態（State）」で捉えている。
- **課題**: データの永続化形式が不明確（おそらくJSON）。人間が直接編集するには不向き。

### 2.3 統合時の注意点

Novel-Athanorの「読みやすいMarkdown」と NovelWriterの「計算可能なData Class」の間のギャップが最大の課題です。
**推奨**: マスターデータはMarkdown（Novel-Athanor方式）とし、分析・生成時にそれをPythonオブジェクト（NovelWriter方式）にパースして扱う **"Hybird Parsing"** アプローチを採用すべきです。

---

## 3. 機能フロー観点

### 3.1 優れた生成フロー

**Novel-Athanorの「コンテキスト構築フロー」** が最も優れています。
`/draft-scene ep.5` と打つだけで、現在のフェーズ(`current_phase`)に基づいたキャラクター設定のみを抽出し、プロンプトに含める仕組みは、長編執筆において必須の機能です。

### 3.2 プロンプト設計の比較

**302_novel_writing** のプロンプト（`prompt.ts`）は非常に優秀です。

- **Role Definition**: `You are a professional novel editing assistant.`
- **Constraint Checklist**: 何をすべきでないか（AI感のあるまとめ、タイトル生成の禁止など）が明記されている。
- **XML Structure**: 出力をXMLタグで囲ませることで、後処理（パース）を容易にしている。

---

## 4. 伏線管理観点（新システム向け重点項目）

### 4.1 既存システムの状況

Claude Codeの指摘通り、3システムとも本格的な伏線管理機能は欠如しています。

### 4.2 提言: "Chekhov's Gun Tracker"

伏線管理システムを新規設計する場合、以下のデータモデルを推奨します。

```json
{
  "foreshadowing_id": "FS-001",
  "content": "主人公が古びたロケット（ペンダント）を持っている",
  "seed": {
    "location": "L3_seq_01.md",
    "description": "何気なくロケットを触る描写",
    "subtlety_level": 5 // 1(明白) - 10(極めて微細)
  },
  "payoff": {
    "planned_location": "L3_seq_20.md",
    "description": "ロケットの中の写真が敵の正体を示している",
    "status": "planned" // planned, planted, realized, ignored
  }
}
```

### 4.3 隠し設定の扱い

Novel-Athanorの `## 隠し設定` は、単純ですが強力です。しかし、「AIに隠す」だけでは不十分で、「AIに**伏線として**認識させる（ネタバレはさせずに、匂わせる）」という **Level 2 (内容認識)** の制御が必要です。

---

## 5. AI情報制御観点（最重要・新規要件）

### 5.1 4段階モデルへの評価

提案されたモデルは妥当ですが、実装においては **"Context Filter Layer"** が必要です。

| Level | 名称         | 実装イメージ (プロンプト制御)                                                                    |
| ----- | ------------ | ------------------------------------------------------------------------------------------------ |
| **0** | **完全秘匿** | プロンプトに一切含めない（除外）                                                                 |
| **1** | **認識のみ** | `System: "There is a hidden secret about X, but do NOT reveal it."`                              |
| **2** | **内容認識** | `System: "Secret content is Y. Use this to create tension/hints, but NEVER state Y explicitly."` |
| **3** | **使用可能** | 通常のコンテキストとして含める                                                                   |

### 5.2 「そのまま書いてしまう」問題への対策

302_novel_writingのプロンプトに見られる **"Negative Constraints"** (やってはいけないことリスト) の強化に加え、**"Reviewer Agent"** による事後チェックが有効です。
生成されたテキストを別のAIエージェントが読み、「この文章は設定資料Xの秘密を漏らしていませんか？」とチェックするフローを導入すべきです。

---

## 6. パフォーマンス・スケーラビリティ観点

### 6.1 大規模作品対応

MarkdownファイルをベースにするNovel-Athanor方式が、ファイルサイズやメモリ管理の観点で最もスケーラブルです。
すべてを1つのJSONやメモリに乗せるNovelWriter方式は、100話を超えるとコンテキストウィンドウの枯渇や処理速度の低下を招きます。

### 6.2 推奨アーキテクチャ

**"Lazy Loading Context"**
全データではなく、現在執筆中のエピソードに関連する L1/L2/L3 と、現在のフェーズのキャラクターデータのみを動的にロードする仕組みが必要です。

---

## 8. 新システム設計への提言

### 8.1 採用すべき要素

1.  **Novel-Athanor**: ディレクトリ構成、L1/L2/L3階層、フェーズ管理概念。
2.  **NovelWriter**: `ArcAnalysis` による品質スコアリング、マルチエージェントによる分業（執筆役とレビュー役）。
3.  **302_novel_writing**: XMLタグを活用した構造化プロンプト、制約条件の明文化技術。

### 8.2 避けるべき要素

1.  **NovelWriter**: データの完全インメモリ化（JSON巨大化問題）。
2.  **302_novel_writing**: スタイル定義のハードコード（TypeScriptファイルへの埋め込み）。設定は外部yaml/mdに出すべき。

### 8.3 統合時の課題

- **Markdown vs Python Object**: 「人間が書きやすいMarkdown」を「プログラムが扱いやすいObject」に変換するパーサーの堅牢性が鍵となります。
- **コンテキスト長**: 伏線情報やAI制御情報が増えるほど、プロンプトが肥大化します。ベクトル検索(RAG)や要約による圧縮技術が必須になります。

### 8.4 新規開発の優先順位

1.  **AI情報制御基盤 (Information Control Layer)**
    - 理由: これがないと、どんなに良い伏線システムを作っても、AIが即座にネタバレしてしまい、システムとして破綻するため。
2.  **伏線管理システム (Foreshadowing Manager)**
    - 理由: 情報制御の上に乗るアプリケーション層であるため。

### 8.5 アーキテクチャ推奨

```mermaid
graph TD
    User[Writer] -->|Writes/Edits| MD[Markdown Vault (L1/L2/L3)]

    subgraph "Core System (Python)"
        Parser[Hybrid Parser] -->|Load| MD
        Parser -->|Parse| ContextObj[Context Objects]

        InfoCtrl[Information Control Layer] -->|Filter (Level 0-3)| ContextObj
        InfoCtrl -->|Filtered Context| Agent[Writing Agent]

        FSM[Foreshadowing Specialist] -->|Inject Seeds| InfoCtrl
        Reviewer[Quality Reviewer] -->|Check Leakage| Agent
    end

    Agent -->|Generate| Draft[Draft Content]
    Reviewer -->|Review| Draft
```

**結論**:
Novel-Athanorをベースキャンプとし、NovelWriterの頭脳（分析ロジック）と302_novel_writingの話術（プロンプト技術）を移植する。そして、その中心に強力な「門番（AI情報制御）」を配置するアーキテクチャを提案します。

## 9. 推奨チーム編成（Claude Code Agents）

本プロジェクトを実現するための、Claude Code上でのエージェント（機能人格）のチーム編成案を提示します。これらは「仮想編集部」として機能します。

### 9.1 チーム構成員

| 役割名                           | 職務 (Responsibility)                                                                                                                                              | Novel-Athanorでの実装形態                                 |
| :------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------- |
| **Chief Editor** (編集長)        | **オーケストレーション**。<br>ユーザー意図の解釈、タスクの分解、各エージェントへの指示出し。最終的な成果物の統合。                                                 | `Main System Prompt` (Claude Code自体のPersona)           |
| **Continuity Director** (記録係) | **情報制御・整合性管理**。<br>「門番」として、Writerに渡すコンテキストからネタバレを削除(Level 0-1)し、伏線指示(Level 2)を注入する。                               | `Foreshadowing Manager` + `Context Filter` (Python Logic) |
| **Ghost Writer** (執筆担当)      | **実テキスト生成**。<br>与えられたコンテキストとスタイルガイドに従い、指定されたフォーマットで執筆する。設定の矛盾や伏線については責任を負わない（知らないため）。 | `Generation Agent` (Prompt Engineering)                   |
| **Reviewer** (校閲担当)          | **品質管理・検閲**。<br>生成されたテキストを読み、「情報漏洩がないか」「文体が崩れていないか」をチェックする。                                                     | `ArcAnalysis` (NovelWriter) + `Review Agent`              |

### 9.2 協調ワークフロー例 ("The Relay")

1.  **Preparation (Chief -> Director)**
    - ユーザーが `/draft-scene` を実行。
    - **Chief** が **Director** に「このシーンに必要な『安全な』資料を集めろ」と指示。
    - **Director** が L1/L2/L3 とキャラクター設定をロードし、Visibility Levelに基づいてフィルタリング。

2.  **Drafting (Director -> Writer)**
    - **Director** が「設定資料（検閲済み）」と「伏線挿入指示書」を **Writer** に渡す。
    - **Writer** が執筆を実行。

3.  **Review (Writer -> Reviewer)**
    - 生成された原稿を **Reviewer** が回読。
    - チェック項目:
      - 「Level 0/1 の秘密が書かれていないか？」（Leakage Check）
      - 「302_novel_writing の禁止用語（AI感のあるまとめ）が含まれていないか？」

4.  **Finalize (Reviewer -> Chief)**
    - 問題なければ **Chief** がファイルに書き込み、ユーザーに報告。
    - 問題があれば **Chief** が **Writer** に修正指示（Feedback Loop）。

### 9.3 実装への提言

これを実現するためには、単一のプロンプトですべてを行わせるのではなく、**「思考の連鎖（Chain of Thought）」を明示的なツール呼び出し（Tool Use）に分割する** 設計が必要です。

- `get_filtered_context(scene_id)` というツールを用意し、これを呼ばないと執筆を開始できないようにする。
- `review_draft(text)` というツールを用意し、これをパスしないと完了できないようにする。

これにより、Claude Codeは「ひとりの天才」として振る舞うのではなく、「編集部の指揮官」として振る舞うようになります。
