#!/usr/bin/env python3
"""Generate the conversation histories used by the history-* eval cases.

  python3 evals/make_histories.py

Each history is a minimal Claude Code transcript (JSON lines):

1. the `/agent-builder` command message;
2. the skill text expanded from the current SKILL.md;
3. a curated first round of fallback-mode questions from the assistant.

The case's prompt.md then supplies the user's next reply. Re-run this script
whenever SKILL.md changes, so the embedded skill text stays current. The
histories are built from scratch; they contain no real session data.
"""

import json
import os
import re
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "agent-builder", "SKILL.md")
SESSION = "00000000-0000-4000-8000-00000000ab01"
CWD = "/workspace/project"
NAMESPACE = uuid.UUID("6f1b8f5e-7a2c-4c1e-9d55-0a1b2c3d4e5f")

REQUEST = (
    "A multi-source research agent for our product team. Given a research question, it searches "
    "the public web and queries our internal Postgres analytics database (read-only), then writes "
    "a sourced markdown report. Analysts run it on demand from the command line. It is read-only "
    "everywhere. Success: analysts rate at least 8 of 10 reports usable without edits, each report "
    "takes under 10 minutes and costs under 2 dollars. Out of scope: dashboards and writing to any system."
)

ROUND_ONE = """**agent-builder** · planning session

Plan mode or the question dialog isn't available here, so I'll ask in plain text and show the plan in chat. Nothing will be written until you reply with the exact approval phrase.

**Request, restated:** a command-line agent that answers a product research question using the public web and your internal Postgres analytics database, and writes a sourced markdown report.

**Observations:** the working directory is empty; there is no existing agent code and no `.agent-builder/` folder.

## Ledger: unnamed · P2 · Round 1

| # | Dimension | Status | Note |
|---|---|---|---|
| 1 | Outcome | Partial | Sourced markdown report; destination unknown |
| 2 | Users & trigger | Clear | Analysts, on demand, CLI |
| 3 | Inputs & sources | Partial | Web plus Postgres; which tables unknown |
| 4 | Actions & side effects | Conflicting | "Read-only everywhere" vs. "writes a report" |
| 5 | Autonomy & approval | Missing | |
| 6 | Success criteria | Clear | 8/10 usable, under 10 min and $2 |
| 7 | Non-goals | Clear | Dashboards; writing to any system |

---

**Round 1: Outcome, inputs and approval** (answer like `1a, 2a, 3b, 4a`)

**1. Where should the finished report go?**
   a) **A markdown file in a local output folder, with its path printed** (Recommended). Why: analysts can open, edit and share it. Trade-off: this is the only write, to the analyst's own disk.
   b) **Printed to the terminal only.** Trade-off: nothing is written, but reports are easy to lose.
   c) **Both a file and the terminal.**

**2. Which parts of the analytics database may the agent query?**
   a) **An allowlist of named schemas or views** (Recommended). Why: least access, and fewer wrong joins. Trade-off: someone maintains the list.
   b) **Anything the read-only role can see.** Trade-off: broader answers, more chance of touching sensitive tables.
   c) **Exported snapshots instead of live queries.** Trade-off: no live connection, but stale data.

**3. Where must a human approve during a run?**
   a) **Nowhere; the analyst reviews the finished report** (Recommended). Why: the agent is read-only and a run costs under $2. Trade-off: a wrong direction shows only at the end.
   b) **The analyst approves a research plan first.** Trade-off: catches misread questions early; the analyst waits at the terminal.
   c) **The analyst approves every SQL query.** Trade-off: most control, slowest.

**4. What range of questions should it handle?**
   a) **Open-ended product research; the agent picks web, database or both** (Recommended). Why: matches your description. Trade-off: broader behavior is harder to evaluate.
   b) **Always both sources.** Trade-off: narrower and easier to evaluate.
   c) **A fixed set of question templates.** Trade-off: most predictable, least flexible.

Next round: data sensitivity, scale, and citation format. Then I'll show a purpose statement to confirm."""


def skill_text():
    text = open(SKILL, encoding="utf-8").read()
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    subs = {
        "$ARGUMENTS": REQUEST,
        "${CLAUDE_SKILL_DIR}": "/plugin/skills/agent-builder",
        "${CLAUDE_SESSION_ID}": SESSION,
        "${CLAUDE_PLUGIN_DATA}": "/plugin-data",
        "${CLAUDE_PLUGIN_ROOT}": "/plugin",
    }
    for key, value in subs.items():
        body = body.replace(key, value)
    return "Base directory for this skill: /plugin/skills/agent-builder\n\n" + body


def entry(kind, message, parent, n, **extra):
    base = {
        "parentUuid": parent,
        "isSidechain": False,
        "type": kind,
        "message": message,
        "uuid": str(uuid.uuid5(NAMESPACE, "entry-%d" % n)),
        "timestamp": "2026-09-22T12:00:%02d.000Z" % n,
        "userType": "external",
        "entrypoint": "sdk-cli",
        "cwd": CWD,
        "sessionId": SESSION,
        "version": "2.1.278",
    }
    base.update(extra)
    return base


def build_history():
    prompt_id = str(uuid.uuid5(NAMESPACE, "prompt-1"))
    command = (
        "<command-message>agent-builder:agent-builder</command-message>\n"
        "<command-name>/agent-builder:agent-builder</command-name>\n"
        "<command-args>%s</command-args>" % REQUEST
    )
    e1 = entry("user", {"role": "user", "content": command}, None, 1, promptId=prompt_id)
    e2 = entry("user", {"role": "user", "content": [{"type": "text", "text": skill_text()}]},
               e1["uuid"], 2, promptId=prompt_id, isMeta=True)
    e3 = entry("assistant", {
        "model": "claude-sonnet-5", "id": "msg_history_round_1", "type": "message", "role": "assistant",
        "content": [{"type": "text", "text": ROUND_ONE}], "stop_reason": "end_turn", "stop_sequence": None,
        "usage": {"input_tokens": 0, "output_tokens": 0},
    }, e2["uuid"], 3)
    return [e1, e2, e3]


CASES = ["history-partial-answer-reask", "history-override-recommendation", "history-contradiction"]


def main():
    lines = "".join(json.dumps(e) + "\n" for e in build_history())
    for case in CASES:
        path = os.path.join(ROOT, "evals", case, "history.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(lines)
        print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
