# Contributing to agent-builder

Thanks for helping improve agent-builder. This guide covers the development
loop, the rules that keep the skill trustworthy, and how releases work.

## Ground rules

1. **The user decides.** Every change must preserve the core contract:
   - Claude recommends; the user decides every question.
   - Nothing is assumed.
   - Nothing is built before the plan is approved.

   A PR that weakens any of these needs a very strong reason.
2. **No fast facts in the references.** Model IDs, package versions, API names
   and prices go stale. The files under `skills/agent-builder/references/` hold
   lasting principles only; the skill looks facts up live
   (`references/live-lookup.md`).
3. **Own words only.** Reference material summarizes public guidance in our own
   words and links to the source. Don't paste text from articles, docs or books.
4. **Keep SKILL.md lean.** It must stay under 500 lines, with the hard rules
   first (only the first part of a skill survives context compaction). Put
   detail in a reference file and link it from the phase that needs it.
5. **The description budget is real.** `description` plus `when_to_use` must
   stay within 1,536 characters. CI checks this.

## Development loop

```bash
# load the plugin from your working copy
claude --plugin-dir .
# after editing files, inside Claude Code:
/reload-plugins
```

Try a vague request, a detailed request, and a request that shouldn't trigger
the skill at all. For a headless check of fallback mode:

```bash
claude -p "/agent-builder an agent for my team" --plugin-dir .
```

## Checks

Run these before opening a PR (CI runs all but the evals):

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repo.py            # needs: pip install pyyaml
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
npx markdownlint-cli2 "**/*.md"
```

### Evals

The suite in `evals/` runs real model sessions, so it costs tokens. Run it
locally when you change `SKILL.md` or a reference that changes behavior:

```bash
claude plugin eval . --allow-tools Write Edit --scaffold --judge-model sonnet --threshold 0.8
# iterate on one case cheaply:
claude plugin eval . --case slash-vague-asks-purpose --runs 1 --ablation none
```

- Paste the summary table into your PR.
- Eval runs are non-interactive. The skill runs in its plain-text fallback mode
  there, which is expected.
- `--scaffold` runs the case scaffold scripts on your machine. Read them first;
  they only create small fixture files.
- The `history-*` cases resume a generated conversation (`history.jsonl`).
  Regenerate them with `python3 evals/make_histories.py` whenever you change
  `SKILL.md`, so the embedded skill text stays current. The histories are built
  from scratch. Never commit a real session transcript: it contains your
  settings, paths and account details.

## Changing the plan guard

`skills/agent-builder/scripts/plan_guard.py` must stay standard-library only,
and must fail open. For every new command pattern, add a test case to
`tests/test_plan_guard.py`, in both the allowed list and the blocked list where
it matters.

## Commits, versions and releases

- Keep commits focused, with a clear subject line in the imperative mood.
- Add user-visible changes under `## [Unreleased]` in `CHANGELOG.md`.
- A release bumps `version` in `.claude-plugin/plugin.json`, and the matching
  "skill version" line near the top of `SKILL.md`. Installed users only receive
  updates when the plugin.json version changes. It also moves the Unreleased entries
  under a new version heading, which must match; CI checks that. Then tag
  `vX.Y.Z`.
- While the version is 0.x, a minor version may change behavior. Say so in the
  changelog.

## Reporting problems

Use the issue templates. For "it triggered when it shouldn't have" (or didn't
trigger when it should), use the **Trigger report** template, and include your
exact prompt.
