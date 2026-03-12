"""
test_pre_tool_use.py - pre-tool-use.py の TDD テスト

W2-T2: Red フェーズ（テストファースト）
対応仕様: docs/internal/07_SECURITY_AND_AUTOMATION.md Section 5（Hooks-Based Permission System）
"""
from __future__ import annotations

import json
from pathlib import Path

# テスト対象フックのパス
HOOK_PATH = Path(__file__).resolve().parent.parent / "pre-tool-use.py"


class TestPreToolUse:
    """pre-tool-use.py の権限等級判定テスト"""

    def test_read_tool_pg_allow(self, hook_runner) -> None:
        """Read ツールは PG 級として許可される（exit 0、stdout 空）"""
        input_json = {
            "tool_name": "Read",
            "tool_input": {
                "file_path": "src/main.py",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        # PG 許可: stdout は空（hookSpecificOutput を出力しない）
        assert result.stdout.strip() == "", f"PG 許可時は stdout が空であるべき。got: {result.stdout!r}"

    def test_edit_specs_pm_ask(self, hook_runner) -> None:
        """Edit で docs/specs/*.md を編集すると PM ask が返る"""
        input_json = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "docs/specs/test.md",
                "old_string": "old",
                "new_string": "new",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        stdout = result.stdout.strip()
        assert stdout, "PM ask 時は stdout に JSON が出力されるべき"
        data = json.loads(stdout)
        assert "hookSpecificOutput" in data
        hook_output = data["hookSpecificOutput"]
        assert hook_output["permissionDecision"] == "ask"
        assert isinstance(hook_output["permissionDecisionReason"], str)
        assert len(hook_output["permissionDecisionReason"]) > 0

    def test_edit_rules_auto_generated_pm_ask(self, hook_runner) -> None:
        """Edit で .claude/rules/auto-generated/ 配下のファイルを編集すると PM ask が返る"""
        input_json = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": ".claude/rules/auto-generated/rule.md",
                "old_string": "old",
                "new_string": "new",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        stdout = result.stdout.strip()
        assert stdout, "PM ask 時は stdout に JSON が出力されるべき"
        data = json.loads(stdout)
        assert "hookSpecificOutput" in data
        hook_output = data["hookSpecificOutput"]
        assert hook_output["permissionDecision"] == "ask"
        assert isinstance(hook_output["permissionDecisionReason"], str)
        assert len(hook_output["permissionDecisionReason"]) > 0

    def test_absolute_path_normalization(self, hook_runner, project_root) -> None:
        """絶対パスが project_root からの相対パスに正規化されて SE 判定される"""
        abs_path = str(project_root / "src" / "main.py")
        input_json = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": abs_path,
                "old_string": "old",
                "new_string": "new",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        # SE 級: stdout は空（ask/deny を出力しない）
        assert result.stdout.strip() == "", f"SE 許可時は stdout が空であるべき。got: {result.stdout!r}"

    def test_edit_src_se_allow(self, hook_runner) -> None:
        """Edit で src/main.py を編集すると SE 許可（exit 0、stdout 空）"""
        input_json = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "src/main.py",
                "old_string": "old",
                "new_string": "new",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        # SE 許可: stdout は空
        assert result.stdout.strip() == "", f"SE 許可時は stdout が空であるべき。got: {result.stdout!r}"

    def test_log_truncation(self, hook_runner, project_root) -> None:
        """ログのターゲットフィールドが 100 文字でトランケートされる"""
        # 150 文字のパスを生成
        long_path = "src/" + "a" * 150 + ".py"
        input_json = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": long_path,
                "old_string": "old",
                "new_string": "new",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        # ログファイルを確認
        log_file = project_root / ".claude" / "logs" / "permission.log"
        assert log_file.exists(), "ログファイルが作成されるべき"
        log_content = log_file.read_text(encoding="utf-8")
        # ログの各フィールドを確認: timestamp, level, tool_name, target(100文字)
        lines = [line for line in log_content.strip().split("\n") if "Edit" in line and "aaa" in line]
        assert lines, "Edit のログが記録されるべき"
        last_line = lines[-1]
        fields = last_line.split("\t")
        # target フィールドは 4番目（0-indexed: 3）
        assert len(fields) >= 4, f"ログのフィールド数が不足: {fields!r}"
        target = fields[3]
        # trunc 後は 100 文字以内
        assert len(target) <= 100, f"target が 100 文字を超えている: {len(target)}"

    def test_glob_tool_pg_allow(self, hook_runner) -> None:
        """Glob ツールは PG 級として許可される（exit 0、stdout 空）"""
        input_json = {
            "tool_name": "Glob",
            "tool_input": {
                "pattern": "**/*.py",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        assert result.stdout.strip() == "", f"PG 許可時は stdout が空であるべき。got: {result.stdout!r}"

    def test_grep_tool_pg_allow(self, hook_runner) -> None:
        """Grep ツールは PG 級として許可される（exit 0、stdout 空）"""
        input_json = {
            "tool_name": "Grep",
            "tool_input": {
                "pattern": "def main",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        assert result.stdout.strip() == "", f"PG 許可時は stdout が空であるべき。got: {result.stdout!r}"


class TestPreToolUseAuditing:
    """AUDITING フェーズでの PG コマンド特別許可テスト"""

    def test_ruff_format_pg_in_auditing(self, hook_runner, project_root) -> None:
        """AUDITING フェーズで ruff format は PG 許可される"""
        phase_file = project_root / ".claude" / "current-phase.md"
        phase_file.write_text("**AUDITING**\n", encoding="utf-8")

        input_json = {
            "tool_name": "Bash",
            "tool_input": {
                "command": "ruff format src/",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        assert result.stdout.strip() == "", (
            f"AUDITING での ruff format は PG 許可であるべき。got: {result.stdout!r}"
        )

    def test_ruff_check_fix_pg_in_auditing(self, hook_runner, project_root) -> None:
        """AUDITING フェーズで ruff check --fix は PG 許可される"""
        phase_file = project_root / ".claude" / "current-phase.md"
        phase_file.write_text("**AUDITING**\n", encoding="utf-8")

        input_json = {
            "tool_name": "Bash",
            "tool_input": {
                "command": "ruff check --fix src/",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        assert result.stdout.strip() == "", (
            f"AUDITING での ruff check --fix は PG 許可であるべき。got: {result.stdout!r}"
        )

    def test_bash_command_se_without_auditing(self, hook_runner, project_root) -> None:
        """AUDITING フェーズ以外では ruff format は SE 扱い"""
        phase_file = project_root / ".claude" / "current-phase.md"
        phase_file.write_text("**BUILDING**\n", encoding="utf-8")

        input_json = {
            "tool_name": "Bash",
            "tool_input": {
                "command": "ruff format src/",
            },
        }
        result = hook_runner(HOOK_PATH, input_json)
        assert result.returncode == 0
        assert result.stdout.strip() == "", (
            f"BUILDING での ruff format は SE 許可であるべき。got: {result.stdout!r}"
        )
