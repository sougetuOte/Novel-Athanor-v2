"""
test_pre_compact.py - pre-compact.py の TDD テスト

対応仕様: CLAUDE.md Section "Context Management"
          pre-compact.py モジュール docstring（H4 設計書準拠）

テスト対象機能:
- PreCompact 発火フラグファイルの作成
- SESSION_STATE.md への記録（冪等処理）
- SESSION_STATE.md が存在しない場合の loop.log フォールバック
- lam-loop-state.json のバックアップ
- エラー時でも exit 0 を返すこと
"""
import json
import re
import shutil
from pathlib import Path

from _test_helpers import DEFAULT_STATE, write_state

# テスト対象フックのパス
HOOK_PATH = Path(__file__).resolve().parent.parent / "pre-compact.py"


class TestPreCompact:
    """pre-compact.py の PreCompact hook テスト"""

    def test_pre_compact_flag_created(self, hook_runner, project_root) -> None:
        """PreCompact 発火フラグファイルがタイムスタンプ付きで作成される。"""
        flag_path = project_root / ".claude" / "pre-compact-fired"
        assert not flag_path.exists()

        result = hook_runner(HOOK_PATH)

        assert result.returncode == 0
        assert flag_path.exists(), "pre-compact-fired フラグファイルが作成されるべき"
        content = flag_path.read_text(encoding="utf-8").strip()
        # ISO 8601 形式: YYYY-MM-DDTHH:MM:SSZ
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", content), (
            f"タイムスタンプが ISO 8601 形式 (YYYY-MM-DDTHH:MM:SSZ) であるべき。got: {content!r}"
        )

    def test_session_state_updated(self, hook_runner, project_root) -> None:
        """SESSION_STATE.md が存在する場合、PreCompact セクションが末尾に追記される。"""
        session_state = project_root / "SESSION_STATE.md"
        session_state.write_text(
            "# SESSION STATE\n\n## 現在のフェーズ\nBUILDING\n",
            encoding="utf-8",
        )

        result = hook_runner(HOOK_PATH)

        assert result.returncode == 0
        content = session_state.read_text(encoding="utf-8")
        assert "## PreCompact 発火" in content, (
            "SESSION_STATE.md に '## PreCompact 発火' セクションが追記されるべき"
        )
        assert "- 時刻: " in content, (
            "SESSION_STATE.md に '- 時刻: ' 行が含まれるべき"
        )

    def test_session_state_idempotent(self, hook_runner, project_root) -> None:
        """SESSION_STATE.md に既に PreCompact セクションがある場合、2回目の実行で
        セクションが重複せず時刻のみが更新される。"""
        session_state = project_root / "SESSION_STATE.md"
        session_state.write_text(
            "# SESSION STATE\n\n## 現在のフェーズ\nBUILDING\n",
            encoding="utf-8",
        )

        # 1回目
        hook_runner(HOOK_PATH)
        content_after_first = session_state.read_text(encoding="utf-8")
        count_after_first = content_after_first.count("## PreCompact 発火")
        assert count_after_first == 1, (
            f"1回目実行後、セクションは1つだけ存在すべき。got: {count_after_first}"
        )

        # 2回目
        hook_runner(HOOK_PATH)
        content_after_second = session_state.read_text(encoding="utf-8")
        count_after_second = content_after_second.count("## PreCompact 発火")
        assert count_after_second == 1, (
            f"2回目実行後もセクションは1つだけ存在すべき（重複禁止）。got: {count_after_second}"
        )
        # 時刻行も1つだけ
        count_time_lines = content_after_second.count("- 時刻: ")
        assert count_time_lines == 1, (
            f"'- 時刻: ' 行は1つだけ存在すべき。got: {count_time_lines}"
        )

    def test_fallback_log_when_no_session_state(self, hook_runner, project_root) -> None:
        """SESSION_STATE.md が存在しない場合、loop.log にフォールバック記録される。"""
        session_state = project_root / "SESSION_STATE.md"
        assert not session_state.exists()

        result = hook_runner(HOOK_PATH)

        assert result.returncode == 0
        log_path = project_root / ".claude" / "logs" / "loop.log"
        assert log_path.exists(), "loop.log が作成されるべき"
        log_content = log_path.read_text(encoding="utf-8")
        assert "PreCompact fired" in log_content, (
            f"loop.log に 'PreCompact fired' が記録されるべき。got: {log_content!r}"
        )
        assert "no SESSION_STATE.md" in log_content, (
            f"loop.log に 'no SESSION_STATE.md' が記録されるべき。got: {log_content!r}"
        )

    def test_loop_state_backup(self, hook_runner, project_root) -> None:
        """lam-loop-state.json が存在する場合、.bak ファイルにコピーされる。"""
        write_state(project_root, DEFAULT_STATE)
        loop_state = project_root / ".claude" / "lam-loop-state.json"
        bak_path = project_root / ".claude" / "lam-loop-state.json.bak"
        assert loop_state.exists()
        assert not bak_path.exists()

        result = hook_runner(HOOK_PATH)

        assert result.returncode == 0
        assert bak_path.exists(), "lam-loop-state.json.bak が作成されるべき"
        original_data = json.loads(loop_state.read_text(encoding="utf-8"))
        backup_data = json.loads(bak_path.read_text(encoding="utf-8"))
        assert original_data == backup_data, (
            "バックアップの内容がオリジナルと一致するべき"
        )

    def test_always_exits_zero(self, hook_runner, project_root) -> None:
        """エラーが発生しても exit 0 を返し、コンテキスト圧縮をブロックしない。

        .claude/ ディレクトリを削除することで write_pre_compact_flag が
        OSError を起こす状況を再現する。
        """
        # .claude/ ディレクトリを削除して書き込み失敗を誘発
        shutil.rmtree(project_root / ".claude")

        result = hook_runner(HOOK_PATH)

        assert result.returncode == 0, (
            f"エラー時でも exit 0 を返すべき。got: {result.returncode}"
        )
