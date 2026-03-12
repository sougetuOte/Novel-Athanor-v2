# 監査統合レポート（イテレーション 1）

**対象**: `.claude/` + `docs/internal/`
**日付**: 2026-03-12

## サマリー

| 重要度 | 件数 |
|--------|:----:|
| Critical | 2 |
| Warning | 18 |
| Info | 14 |

| 等級 | 件数 |
|------|:----:|
| PG | 7 |
| SE | 23 |
| PM | 4 |

## Critical

| ID | 等級 | 内容 | ファイル |
|----|------|------|---------|
| C-1 | SE | `00_PROJECT_STRUCTURE.md` のディレクトリツリーに `docs/artifacts/` が欠落（SSOT不整合） | docs/internal/00_PROJECT_STRUCTURE.md |
| C-2 | SE | `novel-generator.json` の `currentActivity`, `qualityMetrics`, `updatedAt` が1ヶ月以上古い | .claude/states/novel-generator.json |

## Warning

| ID | 等級 | 内容 | ファイル |
|----|------|------|---------|
| W-1 | SE | R-10 違反: UTC タイムスタンプ関数が3ファイルに重複（post-tool-use.py, pre-compact.py, lam-stop-hook.py） | hooks 3ファイル |
| W-2 | SE | R-9 違反: `_hook_utils.py:32` の `if env_root:` は falsy チェック | _hook_utils.py:32 |
| W-3 | SE | R-9 違反: `pre-tool-use.py:77,93` の `if file_path:` / `if command:` | pre-tool-use.py:77,93 |
| W-4 | SE | `post-tool-use.py:121-127` の `except Exception: pass` でエラー黙殺 | post-tool-use.py:121 |
| W-5 | SE | `lam-stop-hook.py:553-556` 前サイクルログへの test_count 上書きが不明瞭 | lam-stop-hook.py:553 |
| W-6 | SE | `_detect_test/lint_framework` の戻り値型が扱いにくい（R-11） | lam-stop-hook.py:174,213 |
| W-7 | SE | シークレットスキャンが `src/` のみ、拡張子フィルタなし | lam-stop-hook.py:356-373 |
| W-8 | SE | `log_entry` の message にタブ・改行が含まれると TSV 崩壊 | _hook_utils.py:116 |
| W-9 | SE | `phase-rules.md` のルール番号範囲が古い（R-5〜R-12 → R-5〜R-13） | .claude/rules/phase-rules.md:41 |
| W-10 | SE | `00_PROJECT_STRUCTURE.md` の `docs/memos/` 説明が移行後の実態と不整合 | docs/internal/00_PROJECT_STRUCTURE.md |
| W-11 | SE | `99_reference_generic.md` の DRY 基準が `03_QUALITY_STANDARDS.md` と不一致 | docs/internal/99_reference_generic.md:101 |
| W-12 | SE | `current-phase.md` が旧パス `docs/memos/` を参照 | .claude/current-phase.md:11 |
| W-13 | SE | `novel-generator.json` の参照パスが旧 `docs/memos/` のまま | .claude/states/novel-generator.json:50-58 |
| W-14 | SE | `00_PROJECT_STRUCTURE.md` に `.claude/hooks/`, `.claude/logs/` 等の記載なし | docs/internal/00_PROJECT_STRUCTURE.md |
| W-15 | SE | `01_REQUIREMENT_MANAGEMENT.md` が旧パス `docs/memos/` を参照 | docs/internal/01_REQUIREMENT_MANAGEMENT.md:8 |
| W-16 | SE | `08_agent-design.md` に `code-reviewer.md` の記載なし | docs/specs/08_agent-design.md |
| W-17 | SE | テスト `test_hook_utils.py` で `monkeypatch` 未使用、手動 try/finally | .claude/hooks/tests/test_hook_utils.py:24-32 |
| W-18 | PM | `08_agent-design.md` に未実装エージェントの implementation パス残存 | docs/specs/08_agent-design.md:496-538 |

## Warning (PM級 — 要判断)

| ID | 等級 | 内容 | ファイル |
|----|------|------|---------|
| W-18 | PM | 未実装エージェント(consistency/foreshadowing/extract)のimplementation パス | docs/specs/08_agent-design.md |
| W-19 | PM | `settings.json` deny に `git reset/checkout --/clean/rebase` が欠落 | .claude/settings.json |
| W-20 | PM | `settings.json` deny のパターンがフルパス指定でバイパス可能 | .claude/settings.json |

## Info

| ID | 等級 | 内容 | ファイル |
|----|------|------|---------|
| I-1 | PG | `_hook_utils.py` の `log_entry`, `atomic_write_json` に `-> None` 型注釈欠落 | _hook_utils.py:104,119 |
| I-2 | SE | `_hook_utils.py` の `dict` 型注釈を `dict[str, Any]` に精密化すべき | _hook_utils.py:45 |
| I-3 | SE | `pre-compact.py:24` の `now_iso8601` に `_` プレフィックスなし | pre-compact.py:24 |
| I-4 | SE | `pre-tool-use.py:50-61` の `_PM_PATTERNS`/`_SE_PATTERNS` の優先順位コメントなし | pre-tool-use.py:50 |
| I-5 | PG | `lam-stop-hook.py:56` PEP 8 空行不足 | lam-stop-hook.py:56 |
| I-6 | PG | テストの `from __future__ import annotations` が3ファイルで欠落 | tests/test_*.py |
| I-7 | PG | テストヘルパーの型注釈精密化（`dict` → `dict[str, Any]`） | _test_helpers.py |
| I-8 | SE | `test_stop_hook.py:110-145` のスキーマテストが責務外 | test_stop_hook.py:110 |
| I-9 | SE | `test_pre_tool_use.py` 異常系テスト不足 | test_pre_tool_use.py |
| I-10 | SE | `test_post_tool_use.py` exitCode欠損の異常系テストなし | test_post_tool_use.py |
| I-11 | SE | `post-tool-use.py:193-195` JSONパース失敗時に空dictで上書きリスク | post-tool-use.py:193 |
| I-12 | SE | `novel-generator.json` の `updatedAt` が古い（C-2と同時対応） | novel-generator.json:68 |
| I-13 | SE | `full-review.md` の Opus 推奨と `code-reviewer.md` の `model: sonnet` の不整合 | full-review.md:259 |
| I-14 | PG | `00_PROJECT_STRUCTURE.md` に `src/core/vault/` の記載なし | 00_PROJECT_STRUCTURE.md |
