"""Tests for skills/agent-builder/scripts/plan_guard.py (stdlib unittest).

Run from the repo root:  python3 -m unittest discover -s tests -v
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "agent-builder", "scripts", "plan_guard.py")
sys.path.insert(0, os.path.dirname(SCRIPT))

import plan_guard  # noqa: E402


class RiskyShellTest(unittest.TestCase):
    ALLOWED = [
        "ls -la",
        "git status",
        "git log --oneline | head -5",
        "git diff HEAD~1",
        "git branch",
        "git branch -a",
        "git remote -v",
        "git config user.name",
        "cat README.md",
        "grep -rn 'a > b' src",
        "echo hi 2>/dev/null",
        "find . -name '*.py' 2>&1 | head",
        "curl -s https://pypi.org/pypi/langgraph/json | python3 -c 'import json,sys; print(1)'",
        "npm view @langchain/langgraph version",
        "pip show anthropic",
        "python3 /x/scripts/plan_guard.py stop abc --data-dir /d",
        "echo 'unbalanced",
    ]
    BLOCKED = [
        "rm -rf build",
        "mkdir -p src",
        "touch notes.md",
        "cp a b",
        "mv a b",
        "chmod +x run.sh",
        "echo hi > notes.txt",
        "echo hi >> notes.txt",
        "cat <<EOF > app.py\nprint(1)\nEOF",
        "ls && touch x",
        "echo $(rm -rf x)",
        "tee out.log",
        "sed -i '' 's/a/b/' f",
        "npm install",
        "npm i express",
        "pnpm add zod",
        "pip install anthropic",
        "python3 -m pip install anthropic",
        "python3 -m venv .venv",
        "uv add langgraph",
        "poetry add langgraph",
        "brew install jq",
        "sudo apt-get install jq",
        "FOO=1 npm i",
        "npx create-next-app demo",
        "git add .",
        "git commit -m wip",
        "git push origin main",
        "git init",
        "git checkout -b feature",
        "git branch new-feature",
        "git remote add origin https://example.com/r.git",
        "git config user.name bob",
        "git -C repo commit -m x",
    ]

    def test_allowed_commands(self):
        for cmd in self.ALLOWED:
            with self.subTest(cmd=cmd):
                self.assertIsNone(plan_guard.risky_reason(cmd))

    def test_blocked_commands(self):
        for cmd in self.BLOCKED:
            with self.subTest(cmd=cmd):
                self.assertIsNotNone(plan_guard.risky_reason(cmd))


class GuardCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = os.path.join(self.tmp.name, "data")
        self.home = os.path.join(self.tmp.name, "home")
        os.makedirs(self.home)
        self.env = dict(os.environ, CLAUDE_PLUGIN_DATA=self.data, HOME=self.home)

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, SCRIPT, *args], input=stdin, env=self.env,
                              capture_output=True, text=True)

    def hook(self, payload):
        result = self.cli("hook", stdin=json.dumps(payload))
        decision = None
        if result.stdout.strip().startswith("{"):
            decision = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"]
        return result, decision

    def pre(self, tool, tool_input, session="s1", mode="default"):
        return self.hook({"hook_event_name": "PreToolUse", "session_id": session,
                          "permission_mode": mode, "tool_name": tool, "tool_input": tool_input})

    # ------------------------------------------------------------------ lifecycle

    def test_no_marker_allows_everything(self):
        _, decision = self.pre("Write", {"file_path": "/tmp/x.py"})
        self.assertIsNone(decision)
        _, decision = self.pre("Bash", {"command": "npm install"})
        self.assertIsNone(decision)

    def test_start_status_stop(self):
        self.assertEqual(self.cli("status", "s1").stdout.strip(), "not planning")
        self.assertEqual(self.cli("start", "s1").returncode, 0)
        self.assertEqual(self.cli("status", "s1").stdout.strip(), "planning")
        self.assertIn("planning ended", self.cli("stop", "s1").stdout)
        self.assertEqual(self.cli("status", "s1").stdout.strip(), "not planning")

    def test_explicit_data_dir(self):
        other = os.path.join(self.tmp.name, "other")
        self.cli("start", "s1", "--data-dir", other)
        self.assertTrue(os.path.exists(os.path.join(other, "planning", "s1.json")))
        self.assertEqual(self.cli("status", "s1").stdout.strip(), "not planning")  # env dir untouched

    def test_empty_flag_values_are_ignored(self):
        # An unset ${CLAUDE_PLUGIN_DATA} expands to nothing: "--data-dir --plugin-root".
        result = self.cli("start", "s1", "--data-dir", "--plugin-root")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.cli("status", "s1").stdout.strip(), "planning")
        self.assertIn("installed as a plugin", result.stdout)

    def test_plugin_root_message(self):
        result = self.cli("start", "s1", "--plugin-root", "/plugins/agent-builder")
        self.assertNotIn("installed as a plugin", result.stdout)

    # ------------------------------------------------------------------ blocking

    def test_blocks_writes_and_risky_shell_while_planning(self):
        self.cli("start", "s1")
        _, decision = self.pre("Write", {"file_path": "/work/app.py"})
        self.assertEqual(decision, "deny")
        _, decision = self.pre("Edit", {"file_path": "/work/app.py"})
        self.assertEqual(decision, "deny")
        _, decision = self.pre("NotebookEdit", {"notebook_path": "/work/n.ipynb"})
        self.assertEqual(decision, "deny")
        result, decision = self.pre("Bash", {"command": "pip install langgraph"})
        self.assertEqual(decision, "deny")
        self.assertIn("exit agent-builder", result.stdout)
        _, decision = self.pre("Bash", {"command": "git status"})
        self.assertIsNone(decision)
        _, decision = self.pre("Read", {"file_path": "/work/app.py"})
        self.assertIsNone(decision)

    def test_plan_file_is_writable(self):
        self.cli("start", "s1")
        plan = os.path.join(self.tmp.name, "plans", "p.md")
        self.cli("set-plan", "s1", plan)
        _, decision = self.pre("Write", {"file_path": plan})
        self.assertIsNone(decision)
        _, decision = self.pre("Write", {"file_path": plan + ".bak"})
        self.assertEqual(decision, "deny")

    def test_default_plans_dir_allowed_in_plan_mode_before_set_plan(self):
        self.cli("start", "s1")
        plan = os.path.join(self.home, ".claude", "plans", "some-plan.md")
        _, decision = self.pre("Write", {"file_path": plan}, mode="plan")
        self.assertIsNone(decision)
        _, decision = self.pre("Write", {"file_path": plan}, mode="default")
        self.assertEqual(decision, "deny")

    def test_guard_stop_command_is_allowed(self):
        self.cli("start", "s1")
        _, decision = self.pre("Bash", {"command": "python3 %s stop s1" % SCRIPT})
        self.assertIsNone(decision)

    def test_other_sessions_unaffected(self):
        self.cli("start", "s1")
        _, decision = self.pre("Write", {"file_path": "/work/app.py"}, session="s2")
        self.assertIsNone(decision)

    def test_stop_lifts_the_block(self):
        self.cli("start", "s1")
        self.cli("stop", "s1")
        _, decision = self.pre("Write", {"file_path": "/work/app.py"})
        self.assertIsNone(decision)

    def test_plan_approval_clears_marker(self):
        self.cli("start", "s1")
        self.hook({"hook_event_name": "PostToolUse", "session_id": "s1", "tool_name": "ExitPlanMode",
                   "tool_input": {}, "tool_response": {"plan": "x", "filePath": "/p.md"}})
        self.assertEqual(self.cli("status", "s1").stdout.strip(), "not planning")

    def test_exit_plan_mode_records_plan_path(self):
        self.cli("start", "s1")
        plan = os.path.join(self.tmp.name, "custom-plans", "p.md")
        self.pre("ExitPlanMode", {"planFilePath": plan})
        _, decision = self.pre("Write", {"file_path": plan})
        self.assertIsNone(decision)

    def test_stale_marker_is_ignored(self):
        self.cli("start", "s1")
        path = plan_guard.marker_path("s1", self.data)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        data["started_at"] = time.time() - plan_guard.MARKER_MAX_AGE - 60
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        _, decision = self.pre("Write", {"file_path": "/work/app.py"})
        self.assertIsNone(decision)
        self.assertFalse(os.path.exists(path))

    def prompt(self, text, session="s1"):
        return self.hook({"hook_event_name": "UserPromptSubmit", "session_id": session, "prompt": text})

    def test_fallback_approval_phrase_lifts_guard(self):
        self.cli("start", "s1")
        result, _ = self.prompt("  Approve agent plan. ")
        self.assertIn("approved the plan", result.stdout)
        self.assertEqual(self.cli("status", "s1").stdout.strip(), "not planning")

    def test_exit_phrase_lifts_guard(self):
        self.cli("start", "s1")
        result, _ = self.prompt("exit agent-builder please")
        self.assertIn("exited agent-builder", result.stdout)
        self.assertEqual(self.cli("status", "s1").stdout.strip(), "not planning")

    def test_other_prompts_keep_guard(self):
        self.cli("start", "s1")
        for text in ("1a, 2b", "approve", "I approve agent plan changes", "should I exit agent-builder?"):
            with self.subTest(text=text):
                result, _ = self.prompt(text)
                self.assertEqual(result.stdout.strip(), "")
                self.assertEqual(self.cli("status", "s1").stdout.strip(), "planning")

    def test_prompt_without_marker_is_silent(self):
        result, _ = self.prompt("approve agent plan")
        self.assertEqual(result.stdout.strip(), "")

    # ------------------------------------------------------------------ fail open

    def test_invalid_input_fails_open_with_warning(self):
        result = self.cli("hook", stdin="not json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.strip(), "")
        self.assertIn("allowing the action", result.stderr)

    def test_missing_session_allows(self):
        _, decision = self.hook({"hook_event_name": "PreToolUse", "tool_name": "Write",
                                 "tool_input": {"file_path": "/x"}})
        self.assertIsNone(decision)


if __name__ == "__main__":
    unittest.main()
