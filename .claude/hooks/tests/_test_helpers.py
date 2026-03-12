"""
_test_helpers.py - テスト共通ヘルパー（conftest.py 以外からも import 可能）

ループ状態ファイルの読み書き等、複数テストファイルで共用するユーティリティ。
"""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_STATE: dict = {
    "active": True,
    "iteration": 0,
    "max_iterations": 5,
    "command": "test_command",
    "target": "test_target",
    "started_at": "2026-03-10T00:00:00Z",
    "log": [],
}


def write_state(project_root: Path, state: dict) -> Path:
    """lam-loop-state.json を書き込む。"""
    state_file = project_root / ".claude" / "lam-loop-state.json"
    state_file.write_text(json.dumps(state), encoding="utf-8")
    return state_file


def read_state(project_root: Path) -> dict | None:
    """lam-loop-state.json を読み込む。存在しなければ None。"""
    state_file = project_root / ".claude" / "lam-loop-state.json"
    if not state_file.exists():
        return None
    return json.loads(state_file.read_text(encoding="utf-8"))
