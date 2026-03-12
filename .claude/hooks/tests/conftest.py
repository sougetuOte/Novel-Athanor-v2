"""
conftest.py - pytest 共通 fixtures

W2-T1: conftest.py（共通 pytest fixtures）
対応仕様: design.md Section 4
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

# tests/ ディレクトリを sys.path に追加（_test_helpers を import 可能にする）
_TESTS_DIR = str(Path(__file__).resolve().parent)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

# hooks/ ディレクトリを sys.path に追加（_hook_utils を直接 import 可能にする）
_HOOKS_DIR = str(Path(__file__).resolve().parent.parent)
if _HOOKS_DIR not in sys.path:
    sys.path.insert(0, _HOOKS_DIR)


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """テスト用の仮プロジェクトルートを作成する。

    .claude/logs/ ディレクトリと .claude/ ディレクトリを作成し、
    フックが期待するディレクトリ構造を再現する。
    実プロジェクトへの汚染を防ぐため tmp_path を使用する。
    """
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    logs_dir = claude_dir / "logs"
    logs_dir.mkdir()
    return tmp_path


@pytest.fixture
def hook_runner(project_root: Path) -> Callable[..., subprocess.CompletedProcess[str]]:
    """フックを subprocess で実行するヘルパー関数を返す fixture。

    返す run_hook() 関数の仕様:
    - subprocess.run で sys.executable を使用（python3 ハードコード回避）
    - stdin JSON 入力対応
    - stdout, stderr, exit code を CompletedProcess として返却
    - タイムアウト 30 秒設定
    - LAM_PROJECT_ROOT を tmp_path に設定（実プロジェクト汚染防止）
    """

    def run_hook(
        hook_path: Path | str,
        input_json: dict[str, Any] | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """フックスクリプトを subprocess で実行する。

        Args:
            hook_path: 実行するフックスクリプトのパス（Path または str）
            input_json: stdin に渡す JSON オブジェクト。None の場合は空文字列を渡す
            env: 追加の環境変数。LAM_PROJECT_ROOT は自動設定される

        Returns:
            subprocess.CompletedProcess: stdout, stderr, returncode を含む
        """
        stdin_input = json.dumps(input_json) if input_json is not None else ""
        merged_env = {
            **os.environ,
            "LAM_PROJECT_ROOT": str(project_root),
            **(env or {}),
        }
        return subprocess.run(
            [sys.executable, str(hook_path)],
            input=stdin_input,
            capture_output=True,
            text=True,
            env=merged_env,
            timeout=30,
        )

    return run_hook
