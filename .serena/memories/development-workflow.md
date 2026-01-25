# 開発ワークフロー（PLANNING / BUILDING / AUDITING）

## 概要

本プロジェクトは3つのフェーズでワークフローを管理する。
フェーズ切り替えはスラッシュコマンド（`/planning`, `/building`, `/auditing`）で行う。

```
PLANNING → BUILDING → AUDITING → (繰り返し)
```

## Phase 1: PLANNING（設計フェーズ）

### 目的
コードを書く前に、要件定義・設計・タスク分解を行う。

### 承認ゲートフロー
```
requirements → [承認] → design → [承認] → tasks → [承認] → BUILDING へ
```

### MUST（必須）
- `docs/specs/`, `docs/adr/`, `docs/tasks/` への出力
- Mermaid 図表の作成
- 既存コードの読み取り（仕様策定のため）
- 各成果物完成時に「承認」を求める

### MUST NOT（禁止）
- 実装コードの生成（`.ts`, `.py` 等）
- `src/` への変更
- 設定ファイルの変更
- 未承認での次サブフェーズ進行

### AoT フレームワーク連携
| ステップ | 適用 | 担当エージェント |
|----------|------|-----------------|
| 要件定義 | 要件の Atom 分解 | requirement-analyst |
| 設計 | 設計の Atom 分解 | design-architect |
| タスク分割 | タスクの Atom 化 | task-decomposer |

## Phase 2: BUILDING（実装フェーズ）

### 目的
TDD サイクルを厳守した実装を行う。

### TDD サイクル（t-wada style）
```
Step 1: Spec & Task Update   - ドキュメント更新案を提示
Step 2: Red (Test First)     - 失敗するテストを作成
Step 3: Green (Minimal)      - テストを通す最小限のコード
Step 4: Refactor            - 設計改善（テストは常にパス）
Step 5: Commit & Review     - サイクル完了報告
```

### MUST（必須）
- 仕様書の事前確認（`docs/specs/`）
- TDD サイクル厳守
- ドキュメント同期（コード変更時は対応ドキュメントも更新）
- 1サイクル完了ごとにユーザーに報告

### MUST NOT（禁止）
- 仕様なし実装
- テストなし実装
- ドキュメント未更新

### 担当エージェント
- tdd-developer

## Phase 3: AUDITING（監査フェーズ）

### 目的
品質監査、リファクタリング、ドキュメント保守を行う。

### 活動内容
1. Full Codebase Review - "Broken Windows" の修復
2. Massive Refactoring - アーキテクチャレベルの改善
3. Documentation Gardening - ドキュメントの整合性確認
4. Context Compression - 長期セッション時の決定事項書き出し

### チェックリスト

**コード品質**:
- [ ] 命名が意図を表現している
- [ ] 単一責任原則を守っている
- [ ] エラーケースが網羅されている

**コード明確性**:
- [ ] ネストした三項演算子がない
- [ ] 過度に密なワンライナーがない
- [ ] デバッグ・拡張が容易な構造

**ドキュメント整合性**:
- [ ] 仕様と実装の差異がない
- [ ] ADR 決定事項が反映されている

### 重要度分類
| 重要度 | 説明 |
|--------|------|
| Critical | 即座に対応必要 |
| Warning | 対応推奨 |
| Info | 参考情報 |

### 担当エージェント
- quality-auditor

## 意思決定プロトコル（Three Agents Model）

重要な意思決定には3つの視点を適用する:

| Agent | ペルソナ | フォーカス |
|-------|---------|-----------|
| Affirmative | 推進者 | Value, Speed, Innovation |
| Critical | 批判者 | Risk, Security, Debt |
| Mediator | 調停者 | Synthesis, Balance, Decision |

### 実行フロー
```
1. Divergence（発散） - 両者が意見を出し尽くす
2. Debate（議論）     - 対立ポイントの解決策を検討
3. Convergence（収束）- Mediator が最終決定
```

### AoT 適用条件
- 判断ポイントが **2つ以上**
- 影響レイヤー/モジュールが **3つ以上**
- 有効な選択肢が **3つ以上**

## 参照ドキュメント

- `docs/internal/02_DEVELOPMENT_FLOW.md` - 開発フロー SSOT
- `docs/internal/06_DECISION_MAKING.md` - 意思決定プロトコル SSOT
- `.claude/rules/phase-*.md` - フェーズ別ガードレール
