# Novel-Athanor-v2

**A Semi-Automated Novel Generation System Where AI and Users Collaborate to Create Stories**

## Project Overview

Novel-Athanor-v2 is a novel writing support system that aims for **collaborative creation** leveraging user creativity, rather than full automation.

### Key Differentiators

| Feature | Description |
|---------|-------------|
| **AI Information Control** | 4-level visibility system for spoiler prevention |
| **Foreshadowing Management** | Chekhov's Gun Tracker with subtlety scale (1-10) |
| **Hybrid Workflow** | Balance of automation and human judgment (Phase-Gate-Approval) |

### 4-Level AI Visibility

| Level | Name | AI Awareness |
|-------|------|--------------|
| 0 | Fully Hidden | Unaware of existence |
| 1 | Awareness Only | Knows "something exists" |
| 2 | Content Aware | Knows content but doesn't write it |
| 3 | Usable | Free to use |

## Current Status

**L4 Agent Layer - In Progress**

| Phase | Status |
|-------|--------|
| Analysis | ✅ Complete |
| Specification | ✅ Complete |
| L1-L3 Core Implementation | ✅ Complete (921 tests) |
| L4 Agent Layer | 🔨 Phase A-E Done / Phase F-G Remaining |

- Tests: **1,103** (mypy: 0, ruff: 0)
- Implemented Agents: Ghost Writer, Reviewer, Quality Agent, Style Agent

## Documentation

### Specifications

Integrated specifications are in `docs/specs/novel-generator-v2/`:

| File | Content |
|------|---------|
| `00_overview.md` | System Overview |
| `01_requirements.md` | Functional/Non-functional Requirements |
| `02_architecture.md` | Architecture Design |
| `03_data-model.md` | Data Model |
| `04_ai-information-control.md` | AI Information Control (4-level visibility) |
| `05_foreshadowing-system.md` | Foreshadowing Management System |
| `06_quality-management.md` | Quality Management |
| `07_workflow.md` | Workflow (The Relay) |
| `08_agent-design.md` | Agent Design |
| `09_migration.md` | Migration Plan |

### Analyzed Projects

| Project | Source | Strengths |
|---------|--------|-----------|
| Novel-Athanor | User-created | Setting management, phase management |
| NovelWriter | [GitHub](https://github.com/EdwardAThomson/NovelWriter) | Multi-agent, auto-generation |
| 302_novel_writing | [GitHub](https://github.com/302ai/302_novel_writing) | Web UI, multilingual |

## Tech Stack

| Category | Technology |
|----------|------------|
| Runtime | Claude Code (CLI) |
| AI | Claude (Opus/Sonnet/Haiku) |
| Data Format | Markdown + YAML frontmatter |
| Integration | Obsidian (vault structure) |
| Language | Python 3.10+ |

## Development Methodology

This project adopts the **Living Architect Model**.

- Phase Control: `/planning` → `/building` → `/auditing`
- Approval Gates: User approval required at each sub-phase completion
- Details: `CHEATSHEET.md`

## License

MIT License
