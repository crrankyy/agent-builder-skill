# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). While the version is
0.x, minor releases may change behavior.

## [Unreleased]

## [0.2.0] - 2026-09-29

Fixes for the 29 confirmed findings of the 0.1.0 audit (one end-to-end session,
adversarially verified).

### Changed

- The purpose statement, the restatement, the Observations and the P6 decision
  table must appear in the reply text. Writing them to the plan file no longer
  counts as showing them.
- R6 now covers multiSelect questions (each recommended option carries its own
  label and Why / Trade-off, with a worked example). Questions about facts only
  the user knows carry no recommendation.
- Shorter interviews: triage no longer takes a round of its own. Small
  single-user agents default observability, deployment and scale to Not
  applicable. The first reply states the expected length and points to `/cost`.
- The agent-name slug is derived from the purpose and confirmed in the P6
  bundle instead of being asked on its own.
- The consistency pass runs from P2. A resolved conflict stays live for every
  later decision, and a conflict with D-00 offers amending the purpose.
- P6 reconciles every Decide-now triage row against a decision, and asks one
  question about all UNVERIFIED facts.
- SDK names and provider API details that weren't looked up are UNVERIFIED and
  re-checked in build step 2. Lookups cite only printed fields and never read a
  capped query as a count.
- Plan template: step 1 writes the plan path with `$HOME` and has a check that
  can pass. New self-checks cover satisfiable checks, guardrail coverage per
  transport, human-graded metrics and all seven ledger fields. §0 treats any
  difference from a step as an amendment, and a failing eval stops and asks.
- The model ID and version pin are asked even when the user named the model
  family.
- An empty `/agent-builder` asks a question instead of replying in plain text.

### Added

- C-13 Reporting period: a period in the purpose or a metric gets its boundary,
  timezone and date field asked, never assumed.
- Question-bank follow-up: an accepted option that leaves the user owing an
  input (a list, a template) is followed by a question for it.

### Fixed

- Plan guard: `sh`/`bash`/`zsh -c` commands are checked recursively. Shell and
  interpreter scripts, `make`, `wget` and `curl -o`/`-O` are blocked while
  planning. Inline `python3 -c` stays allowed for lookups.
- Plan guard: the state directory is always `~/.claude/agent-builder`, so a
  different `$CLAUDE_PLUGIN_DATA` in the hook can no longer silently disarm it.
- Plan guard: a question is held until the previous round's answers are written
  to the ledger (rule R8).

## [0.1.0] - 2026-09-22

### Added

- `agent-builder` skill: a plan-mode interview that turns a natural-language
  agent idea into an approved, executable build plan. It:
  - clarifies the purpose until the user confirms a purpose statement;
  - triages the question categories, then asks about pattern, runtime, models,
    tools, memory, operations and quality in themed rounds, each with a
    recommendation. The user decides every question;
  - runs a consistency pass after every round, and a review gate before the
    plan is written;
  - writes a self-contained plan with a Mermaid diagram, an eval plan, and
    acceptance checks for every step. The first step saves the plan to
    `.agent-builder/{agent-name}/` in the target project.
- Runtimes in scope: Claude Agent SDK, a Claude API tool-use loop, Claude
  Code-native setups, and LangGraph with OpenRouter.
- Live lookup of fast-changing facts (model IDs, package versions, APIs) with
  citations; distilled reference material for patterns and the decision
  framework.
- Plain-text fallback mode for sessions without plan mode or the question
  dialog.
- Plan guard hook (Python 3, standard library only): while a plan is being
  drafted, blocks file writes other than the plan file, and state-changing shell
  commands. Fails open.
- Plugin and marketplace manifests, CI (plugin validation, manifest and
  frontmatter checks, markdown lint, hook unit tests), a `claude plugin eval`
  suite, examples and contributor docs.

[Unreleased]: https://github.com/crrankyy/agent-builder-skill/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/crrankyy/agent-builder-skill/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/crrankyy/agent-builder-skill/releases/tag/v0.1.0
