# レビュー依頼: L2 レイヤー実装 & L0/L1 整合性確認

## Meta

| 項目 | 値 |
|------|-----|
| Session ID | 2026-01-25_002 |
| 日時 | 2026-01-25 |
| 依頼者 | Camel (Claude Opus 4.5) |
| 依頼種別 | 実装レビュー + 整合性確認 |

---

## 1. レビュー対象

### 1.1 新規実装（L2 レイヤー）

| ファイル | 内容 |
|----------|------|
| `src/core/parsers/visibility_comment.py` | HTMLコメント `<!-- ai_visibility: N -->` パーサー |
| `src/core/services/visibility_controller.py` | セクション可視性判定 & フィルタリング |
| `src/core/services/expression_filter.py` | 禁止キーワードマッチャー |
| `src/core/services/foreshadowing_manager.py` | 伏線状態遷移 & 可視性マッピング |

### 1.2 対応テスト

| ファイル | テスト数 |
|----------|---------|
| `tests/core/parsers/test_visibility_comment.py` | 15件 |
| `tests/core/services/test_visibility_controller.py` | 14件 |
| `tests/core/services/test_expression_filter.py` | 12件 |
| `tests/core/services/test_foreshadowing_manager.py` | 28件 |

### 1.3 関連仕様書

- `docs/specs/novel-generator-v2/04_ai-information-control.md`

---

## 2. レビュー観点

### 2.1 L2 単体品質

- [ ] 仕様書 Section 2-7 との整合性
- [ ] セキュリティ（不正レベル指定時の例外発生確認）
- [ ] テストカバレッジの十分性

### 2.2 L0/L1 との整合性（主要観点）

| 確認項目 | 関連ファイル |
|----------|-------------|
| `AIVisibilityLevel` の L1 定義と L2 使用の一貫性 | `models/ai_visibility.py` ↔ `services/*` |
| `Foreshadowing` モデルと Manager の連携 | `models/foreshadowing.py` ↔ `services/foreshadowing_manager.py` |
| `ForeshadowingAIVisibility` の L1 定義と L2 更新ロジック | `models/foreshadowing.py` ↔ `services/foreshadowing_manager.py` |
| `Secret` モデルの `get_similarity_threshold()` と将来の L2 連携 | `models/secret.py` (L1) → 将来の expression_filter 拡張 |
| パーサー間の設計一貫性 | `parsers/frontmatter.py`, `parsers/obsidian_link.py` (L1) ↔ `parsers/visibility_comment.py` (L2) |

### 2.3 アーキテクチャ健全性

- [ ] 依存関係の方向性（L2 → L1 への一方向依存）
- [ ] 循環参照の有無
- [ ] モジュール境界の明確さ

---

## 3. 実装サマリー

### 3.1 L2-1: Visibility Controller

```
AIVisibilityLevel (L1 定義)
    ↓
parse_visibility_comments() → VisibilityMarker
    ↓
extract_section_visibility() → dict[section, level]
    ↓
filter_content_by_visibility() → FilteredContext
```

### 3.2 L2-2: Expression Filter

```
check_forbidden_keywords(text, keywords) → list[KeywordViolation]
check_text_safety(text, keywords) → SafetyCheckResult
```

### 3.3 L2-3: Foreshadowing Manager

```
状態遷移:
  REGISTERED → PLANTED → REINFORCED → REVEALED
       ↓           ↓           ↓
    ABANDONED ←────┴───────────┘
       ↓
    REGISTERED (復活)

可視性マッピング:
  Status + Subtlety → min(status_visibility, subtlety_visibility)
```

---

## 4. 品質指標

| 指標 | 値 |
|------|-----|
| テスト | 271件 全パス |
| mypy | エラー 0 件 |
| ruff | 警告 0 件 |
| 内部監査 | A 評価（全指摘対応済み） |

---

## 5. コミット履歴（L2 関連）

```
eb2ce36 fix: address audit findings for L2 layer
1551e9a feat(l2): implement AI information control layer
fd3ef8d fix: apply Antigravity review fixes (typing improvements)
```

---

## 6. 特に確認してほしい点

1. **セキュリティ設計**: 不正な `ai_visibility` レベル指定時に例外を発生させる設計は適切か？（WARN-002 対応）

2. **ABANDONED 遷移**: 追加した `ABANDONED` への遷移ルールは仕様書に明記されていないが、実用上必要と判断。この設計判断は妥当か？

3. **L1 モデルとの連携**: `ForeshadowingAIVisibility` の `level` フィールドを L2 で更新するロジックは適切か？

4. **将来拡張への備え**: `Secret.get_similarity_threshold()` を将来の Expression Filter 拡張で活用する設計方針は L2 実装と整合しているか？

---

## 7. 回答フォーマット

```markdown
# レビュー回答

## Meta
| 項目 | 値 |
|------|-----|
| Session ID | 2026-01-25_002 |
| 日時 | YYYY-MM-DD |
| レビュアー | Antigravity |
| 判定 | [A/B/C/D] |

## 1. L2 単体品質
...

## 2. L0/L1 との整合性
...

## 3. 問題点（あれば）
...

## 4. 推奨事項
...

## 5. 総合評価
...
```

---

## 8. 参照ファイル

レビュー時に参照すべきファイル:

```
# L2 実装
src/core/parsers/visibility_comment.py
src/core/services/visibility_controller.py
src/core/services/expression_filter.py
src/core/services/foreshadowing_manager.py

# L1 モデル（整合性確認用）
src/core/models/ai_visibility.py
src/core/models/foreshadowing.py
src/core/models/secret.py

# テスト
tests/core/parsers/test_visibility_comment.py
tests/core/services/test_*.py

# 仕様書
docs/specs/novel-generator-v2/04_ai-information-control.md
```
