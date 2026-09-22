# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). While the version is
0.x, minor releases may change behavior.

## [Unreleased]

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

[Unreleased]: https://github.com/crrankyy/agent-builder-skill/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/crrankyy/agent-builder-skill/releases/tag/v0.1.0
