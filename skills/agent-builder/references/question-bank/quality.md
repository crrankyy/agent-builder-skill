# Quality questions

Asked at the end of P5. Q-07 and Q-08 are asked at the review gate (P6).

## Q-01 Success metrics and targets

- **Header:** `Metrics`
- **Question:** propose concrete metrics derived from the success criteria in
  D-00 (for example "≥ 85% of test questions answered correctly", "p95 latency
  under 30 s", "cost under $0.50 per run") and ask:
  - **Accept metrics.**
  - **Change targets** (say which).
  - **Add or remove metrics.**
- **Applies when:** always.
- **Ledger key:** `metrics`.

## Q-02 Eval dataset

- **Header:** `Eval data`
- **Question:** "Where do the agent's test cases come from?"
- **Options:**
  - **Hand-written cases** covering typical inputs, edge cases and failures.
    Trade-off: high quality; small.
  - **Sampled from real inputs** (anonymized). Trade-off: realistic; needs
    access and privacy care.
  - **Synthetic, then human-reviewed.** Trade-off: scalable; review effort.
- **Recommend when:** no production data yet → hand-written (start with about
  20 cases).
- **Applies when:** always.
- **Ledger key:** `evals.dataset`.

## Q-03 Grading

- **Header:** `Grading`
- **Question:** "How are results judged?" (multiSelect)
- **Options:** Exact or programmatic checks (schema, values, tool calls) /
  Model-as-judge rubric / Human review sample / Pairwise comparison against a
  baseline.
- **Recommend when:** structured outputs → programmatic checks. Prose →
  model-as-judge plus a small human sample.
- **Applies when:** always.
- **Ledger key:** `evals.grading`.

## Q-04 Eval tooling

- **Header:** `Eval tool`
- **Question:** "What runs the evals?"
- **Options:** A test runner with an eval script (e.g. pytest or vitest) / A
  dedicated eval framework (name it after lookup) / The runtime's own eval or
  tracing tools / A custom script.
- **Recommend when:** keep it close to the chosen language's test runner unless
  the team already uses an eval framework.
- **Applies when:** always.
- **Look up live:** the current state of any named framework.
- **Ledger key:** `evals.tooling`.

## Q-05 Test layers (multiSelect)

- **Header:** `Tests`
- **Question:** "Which automated tests should the plan include?"
- **Options:** Unit tests for tools and helpers / Integration tests with mocked
  external APIs / End-to-end runs against a sandbox / Regression evals on each
  change.
- **Recommend when:** at least unit tests for tools plus one end-to-end smoke
  test.
- **Applies when:** code is written.
- **Ledger key:** `tests`.

## Q-06 The agent's CI

- **Header:** `Agent CI`
- **Question:** "Should the agent's repository get CI?"
- **Options:**
  - **GitHub Actions: lint + tests** (evals on demand).
  - **GitHub Actions: lint + tests + evals** (needs an API-key secret; costs
    tokens).
  - **Other CI** (name it).
  - **No CI for now.**
- **Applies when:** the code lives in a git repository.
- **Ledger key:** `agent_ci`.

## Q-07 Git workflow during execution (asked at P6)

- **Header:** `Git flow`
- **Question:** "How should the build be committed while the plan executes?"
- **Options:**
  - **Feature branch, one commit per plan step.** Trade-off: easy to review and
    revert.
  - **Feature branch, one commit at the end.**
  - **Commit to the current branch.**
  - **Don't commit.** You review and commit.
- **Applies when:** the target is a git repository. If it isn't, ask whether to
  initialise one (as a plan step) or proceed without git.
- **Ledger key:** `git_flow`.

## Q-08 `.agent-builder/` in git (always asked at P6)

- **Header:** `Plan in git`
- **Question:** "Should `.agent-builder/` (this plan and its decisions log) be
  committed, or kept out of git?"
- **Options:**
  - **Commit it.** Reviewable, versioned history of decisions.
  - **Add it to .gitignore.** Keeps plans private.
- **Applies when:** always, even outside a git repository. There it records the
  intent for when the folder becomes a repository.
- **Ledger key:** `agent_builder_git`.

## Q-09 Documentation deliverables (multiSelect)

- **Header:** `Docs`
- **Question:** "Which docs should the build produce?"
- **Options:** README with setup and usage / Runbook (operations, failure
  handling) / Architecture overview (with the diagram) / No extra docs.
- **Applies when:** always.
- **Ledger key:** `docs`.
