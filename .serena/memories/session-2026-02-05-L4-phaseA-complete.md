# L4 Phase A 完了 (2026-02-05)

## 成果物
- 11 source files in `src/agents/`
- 58 tests in `tests/agents/`
- 全979テスト pass, mypy 0, ruff 0

## 実装内容

### Models (src/agents/models/)
- SceneRequirements: episode_id, word_count, pov, mood, to_scene_identifier()
- ReviewIssueType/IssueSeverity/ReviewStatus Enums
- ReviewIssue + ReviewResult (has_critical, issue_count)
- QualityAssessment Enum + QualityScore (average()) + QualityIssue + QualityResult (is_acceptable)
- PipelineConfig (max_review_retries, quality_threshold, etc.)

### Config (src/agents/config.py)
- MAX_REVIEW_RETRIES=3, QUALITY_THRESHOLDS, DEFAULT_WORD_COUNT=3000
- get_assessment(score) → "excellent"/"good"/"acceptable"/"needs_improvement"

### CLI Tools (src/agents/tools/)
- context_tool.py: serialize_context_result(), format_context_as_markdown(), run_build_context()
- cli.py: argparse with build-context/format-context subcommands
- __main__.py: python -m src.agents.tools entry

### Key Design Points
- Pydantic BaseModel for L4 models (L1と同じ規約)
- IssueSeverity は review_result.py で定義、quality_result.py で再利用(DRY)
- CLI は JSON in/out (Claude Code agents が parse しやすい)
- format_context_as_markdown は to_prompt_dict() を基盤とする基本フォーマッタ

## 次の手順
- Phase B: Ghost Writer (prompt formatter + agent MD)
- Phase C: Reviewer (prompt formatter + parser + review tool)
- Phase D: Quality Agent (prompt formatter + parser)
- Phase B/C/D は並列可能
