#!/usr/bin/env python3
"""agent-builder plan guard.

Blocks file writes and state-changing shell commands while an agent-builder
planning session is active, so nothing is built before the user approves the
plan. The guard lifts when the plan is approved (ExitPlanMode), when the user
types the fallback approval phrase or "exit agent-builder", or on `stop`.
Standard library only.

Usage:
  plan_guard.py hook                          Claude Code hook entry point (JSON on stdin)
  plan_guard.py start SESSION [--data-dir D] [--plugin-root R]
                                              Mark SESSION as planning
  plan_guard.py set-plan SESSION PATH [--data-dir D]
                                              Record the plan-mode plan file
  plan_guard.py stop SESSION [--data-dir D]   End planning for SESSION
  plan_guard.py status SESSION [--data-dir D] Print whether SESSION is planning

The marker lives at <data-dir>/planning/<session>.json, where <data-dir> is
--data-dir, else $CLAUDE_PLUGIN_DATA, else ~/.claude/agent-builder. The hook
fails open: on any internal error it prints a one-line warning and lets the
tool call through.
"""

import json
import os
import re
import shlex
import sys
import time

MARKER_MAX_AGE = 7 * 24 * 3600  # markers older than this are stale and ignored
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
APPROVAL_PHRASE = "approve agent plan"      # fallback-mode approval (references/fallback-mode.md)
EXIT_PHRASE = "exit agent-builder"
EXIT_HINT = (
    "To leave planning without a plan, tell Claude \"exit agent-builder\"; "
    "otherwise finish the questions and approve the plan."
)

# Commands that change state on their own.
MUTATING_COMMANDS = {
    "rm", "rmdir", "mv", "cp", "mkdir", "touch", "chmod", "chown", "ln", "tee",
    "dd", "truncate", "install", "rsync", "unlink", "shred",
}
# Sub-commands that install packages or scaffold projects.
PACKAGE_SUBCOMMANDS = {
    "pip": {"install", "uninstall"},
    "pip3": {"install", "uninstall"},
    "uv": {"add", "remove", "sync", "init", "pip", "tool", "venv", "lock"},
    "poetry": {"add", "remove", "install", "init", "new", "lock", "update"},
    "pipx": {"install", "uninstall", "inject"},
    "conda": {"install", "create", "remove", "update"},
    "npm": {"install", "i", "add", "ci", "init", "create", "uninstall", "remove", "rm", "link", "publish", "update"},
    "pnpm": {"install", "i", "add", "init", "create", "remove", "rm", "link", "publish", "update", "dlx"},
    "yarn": {"install", "add", "init", "create", "remove", "link", "publish", "upgrade", "dlx"},
    "bun": {"install", "i", "add", "init", "create", "remove", "rm", "link", "publish", "update", "x"},
    "brew": {"install", "uninstall", "reinstall", "upgrade", "tap"},
    "apt": {"install", "remove", "purge", "upgrade"},
    "apt-get": {"install", "remove", "purge", "upgrade"},
    "cargo": {"install", "add", "new", "init", "remove"},
    "go": {"install", "get", "mod"},
    "gem": {"install", "uninstall"},
}
# git sub-commands that are read-only; everything else counts as mutating.
GIT_READ_ONLY = {
    "status", "log", "diff", "show", "rev-parse", "ls-files", "ls-tree", "blame",
    "describe", "shortlog", "grep", "cat-file", "remote", "config", "branch",
    "tag", "reflog", "help", "version", "--version", "check-ignore", "for-each-ref",
}
# For these, specific flags make them mutating.
GIT_MUTATING_FLAGS = {
    "branch": {"-d", "-D", "-m", "-M", "-c", "-C", "--delete", "--move", "--copy", "--set-upstream-to", "-u"},
    "tag": {"-a", "-d", "-s", "-f", "--delete", "--annotate", "--sign"},
    "config": {"--add", "--unset", "--unset-all", "--replace-all", "--rename-section", "--remove-section", "-e", "--edit"},
    "remote": {"add", "remove", "rm", "rename", "set-url", "set-head", "prune"},
}
WRAPPERS = {"sudo", "env", "time", "nohup", "nice", "command", "exec", "builtin", "xargs"}
SEGMENT_BREAKS = {";", "&&", "||", "|", "&", "|&", "(", ")", "{", "}", "$(", "`"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>"}
SAFE_TARGETS = {"/dev/null", "/dev/stdout", "/dev/stderr"}


# ---------------------------------------------------------------- state

def data_dir(explicit=None):
    base = explicit or os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(
        os.path.expanduser("~"), ".claude", "agent-builder")
    return os.path.join(base, "planning")


def marker_path(session, explicit_dir=None):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session)
    return os.path.join(data_dir(explicit_dir), safe + ".json")


def read_marker(session, explicit_dir=None):
    path = marker_path(session, explicit_dir)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if time.time() - float(data.get("started_at", 0)) > MARKER_MAX_AGE:
        try:
            os.remove(path)
        except OSError:
            pass
        return None
    return data


def write_marker(session, data, explicit_dir=None):
    path = marker_path(session, explicit_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    os.replace(tmp, path)


def remove_marker(session, explicit_dir=None):
    try:
        os.remove(marker_path(session, explicit_dir))
        return True
    except OSError:
        return False


# ---------------------------------------------------------------- shell analysis

def _tokens(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _segments(command):
    """Split a shell command into simple-command token lists (best effort)."""
    segments = []
    for line in command.splitlines():
        line = line.replace("$(", " ( ").replace("`", " ; ")
        current = []
        for tok in _tokens(line):
            if tok in SEGMENT_BREAKS:
                if current:
                    segments.append(current)
                current = []
            else:
                current.append(tok)
        if current:
            segments.append(current)
    return segments


def _strip_prefix(words):
    """Drop leading VAR=value assignments and wrapper commands."""
    i = 0
    while i < len(words):
        w = words[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w):
            i += 1
        elif os.path.basename(w) in WRAPPERS:
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 1
        else:
            break
    return words[i:]


def _is_guard_call(words):
    return any(w.endswith("plan_guard.py") for w in words)


def risky_reason(command):
    """Return a short reason if the command changes state, else None."""
    try:
        segments = _segments(command)
    except ValueError:
        # Unbalanced quotes etc.: fall back to a coarse check on the raw text.
        if re.search(r"(^|[\s;&|])(rm|mv|cp|mkdir|touch|tee)\s", command) or re.search(
                r"[^<>&0-9]>{1,2}\s*[^&\s]", command):
            return "unparseable command that looks state-changing"
        return None

    for words in segments:
        # redirects into files
        for i, tok in enumerate(words):
            if tok in REDIRECTS:
                target = words[i + 1] if i + 1 < len(words) else ""
                if target not in SAFE_TARGETS:
                    return "output redirect into a file (%s)" % (target or "?")
        words = [w for w in words if w not in REDIRECTS and w not in {"<", "<<", "<<<"}]
        if _is_guard_call(words):
            continue
        words = _strip_prefix(words)
        if not words:
            continue
        cmd = os.path.basename(words[0])
        args = words[1:]
        if cmd in MUTATING_COMMANDS:
            return "'%s' changes files" % cmd
        if cmd in {"sed", "perl"} and any(a == "-i" or a.startswith("-i") or a.startswith("--in-place") for a in args):
            return "in-place edit with %s" % cmd
        if cmd in {"python", "python3"} and len(args) >= 2 and args[0] == "-m" and args[1] in {"pip", "venv"}:
            if args[1] == "venv" or (len(args) > 2 and args[2] in PACKAGE_SUBCOMMANDS["pip"]):
                return "python -m %s changes the environment" % args[1]
        if cmd in PACKAGE_SUBCOMMANDS and args and args[0] in PACKAGE_SUBCOMMANDS[cmd]:
            return "'%s %s' installs or scaffolds packages" % (cmd, args[0])
        if cmd in {"npx", "bunx"} and args and re.match(r"^(create-|@[^/]+/create)", args[0]):
            return "'%s %s' scaffolds a project" % (cmd, args[0])
        if cmd == "git":
            # skip global options such as -C <dir>, -c key=val
            j = 0
            while j < len(args) and args[j].startswith("-"):
                j += 2 if args[j] in {"-C", "-c"} else 1
            if j >= len(args):
                continue
            sub = args[j]
            rest = args[j + 1:]
            if sub not in GIT_READ_ONLY:
                return "'git %s' changes the repository" % sub
            flags = GIT_MUTATING_FLAGS.get(sub, set())
            if sub == "remote":
                if rest and rest[0] in flags:
                    return "'git remote %s' changes the repository" % rest[0]
            elif sub in {"branch", "tag", "config"}:
                if any(a in flags for a in rest):
                    return "'git %s' with %s changes the repository" % (sub, next(a for a in rest if a in flags))
                if sub == "config" and len([a for a in rest if not a.startswith("-")]) >= 2:
                    return "'git config' sets a value"
                if sub in {"branch", "tag"} and [a for a in rest if not a.startswith("-")] and not any(
                        a in {"-l", "--list", "-a", "-r", "--all", "--contains", "--merged", "--no-merged", "-v", "-vv"} for a in rest):
                    return "'git %s <name>' creates a %s" % (sub, sub)
    return None


# ---------------------------------------------------------------- hook

def _deny(reason):
    json.dump({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "agent-builder is still planning, so %s is blocked until you approve the plan. %s"
                                    % (reason, EXIT_HINT),
    }}, sys.stdout)
    return 0


def _same_path(a, b):
    try:
        return os.path.realpath(os.path.expanduser(a)) == os.path.realpath(os.path.expanduser(b))
    except (TypeError, ValueError):
        return False


def _default_plans_dir():
    return os.path.join(os.path.expanduser("~"), ".claude", "plans")


def _normalise(text):
    return re.sub(r"\s+", " ", text).strip().strip(".!\"'`*").strip().lower()


def _handle_prompt(session, prompt):
    """Lift the guard when the user types the approval or exit phrase.

    This works even where the skill can no longer run shell commands, e.g. in
    headless fallback mode after its tool pre-approvals have expired.
    """
    if read_marker(session) is None:
        return 0
    text = _normalise(prompt)
    if text == APPROVAL_PHRASE:
        remove_marker(session)
        print("agent-builder plan guard: the user approved the plan; the write guard is lifted.")
    elif text.startswith(EXIT_PHRASE):
        remove_marker(session)
        print("agent-builder plan guard: the user exited agent-builder; the write guard is lifted.")
    return 0


def handle_hook(payload):
    event = payload.get("hook_event_name")
    session = payload.get("session_id") or ""
    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    if not session:
        return 0

    if event == "PostToolUse" and tool == "ExitPlanMode":
        remove_marker(session)  # the plan was approved
        return 0
    if event == "UserPromptSubmit":
        return _handle_prompt(session, payload.get("prompt") or "")
    if event != "PreToolUse":
        return 0

    marker = read_marker(session)
    if marker is None:
        return 0

    if tool == "ExitPlanMode":
        plan_file = tool_input.get("planFilePath")
        if plan_file and not marker.get("plan_file"):
            marker["plan_file"] = plan_file
            write_marker(session, marker)
        return 0

    if tool in WRITE_TOOLS:
        target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        plan_file = marker.get("plan_file")
        if plan_file and _same_path(target, plan_file):
            return 0
        if not plan_file and payload.get("permission_mode") == "plan" and target:
            plans = os.path.realpath(_default_plans_dir())
            if os.path.realpath(os.path.expanduser(target)).startswith(plans + os.sep):
                return 0
        return _deny("writing %s" % (target or "files"))

    if tool == "Bash":
        reason = risky_reason(tool_input.get("command") or "")
        if reason:
            return _deny("this shell command (%s)" % reason)
    return 0


# ---------------------------------------------------------------- CLI

def _take_flag(args, name):
    """Remove `name VALUE` from args; return VALUE, or None if absent or empty.

    An unset variable expands to nothing, which can leave the flag followed by
    the next flag; that also counts as no value.
    """
    if name not in args:
        return args, None
    k = args.index(name)
    value = args[k + 1] if k + 1 < len(args) else None
    if value is None or value.startswith("--") or not value.strip():
        return args[:k] + args[k + 1:], None
    return args[:k] + args[k + 2:], value


def _cli(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    cmd, args = argv[0], argv[1:]
    args, explicit_dir = _take_flag(args, "--data-dir")
    args, plugin_root = _take_flag(args, "--plugin-root")

    if cmd == "hook":
        try:
            payload = json.load(sys.stdin)
            return handle_hook(payload)
        except Exception as exc:  # fail open, but say so
            sys.stderr.write("agent-builder plan guard error (allowing the action): %s\n" % exc)
            return 1
    if cmd in {"start", "stop", "status", "set-plan"} and not args:
        print("usage: plan_guard.py %s SESSION" % cmd)
        return 2
    session = args[0] if args else ""
    if cmd == "start":
        write_marker(session, {"session_id": session, "plan_file": None,
                               "started_at": time.time(), "version": 1}, explicit_dir)
        hooked = bool(plugin_root or os.environ.get("CLAUDE_PLUGIN_ROOT"))
        print("plan-guard: planning started for this session%s" % (
            "" if hooked else " (write-blocking hook only runs when agent-builder is installed as a plugin)"))
        return 0
    if cmd == "set-plan":
        marker = read_marker(session, explicit_dir) or {"session_id": session, "started_at": time.time(), "version": 1}
        marker["plan_file"] = args[1] if len(args) > 1 else None
        write_marker(session, marker, explicit_dir)
        print("plan-guard: plan file recorded")
        return 0
    if cmd == "stop":
        removed = remove_marker(session, explicit_dir)
        print("plan-guard: planning ended" if removed else "plan-guard: no active planning session")
        return 0
    if cmd == "status":
        print("planning" if read_marker(session, explicit_dir) else "not planning")
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
