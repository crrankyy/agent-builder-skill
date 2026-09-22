# Decisions: multi-source-research

- Planned: 2026-09-22 with agent-builder 0.1.0
- Session: (example session)

## D-00 Purpose (confirmed)
The statement in §1, verbatim. **Status:** Amended 2026-09-22 by D-27 to allow an opt-in `--trace` file as a second local write.

Clarification answers that shaped it (rounds 1–3, no reasons given):
- The report is written to a local markdown file (1a).
- Internal numbers are computed in SQL only (2a).
- An allowlist of two views: `analytics.team_weekly_metrics` and `analytics.tool_rollouts` (3a). `tool_rollouts` records which tools each team adopted and when.
- Open-ended questions; the agent chooses its sources (4a).
- The analyst approves the plan, and the approval wait doesn't count toward the 10 minutes (1b).
- A hosted model is allowed; reports don't name teams (2b).
- Low load, about 5 analysts (3a).
- Numbered inline citations (4a).
- The bracketed small-sample sentence is kept (1a).

## Triage
| ID | Topic | Status | Reason |
|---|---|---|---|
| F-01 to F-05, F-07 to F-09 | Foundation | Decide now | Always applies, or code will be written |
| F-06 | Claude Code primitives | Not applicable | The runtime is the Agent SDK (D-09) |
| C-01 to C-05, C-08, C-12 | Capabilities | Decide now | Named systems, large outputs, pause at the gate |
| C-06 | Memory | Not applicable | Runs are independent (D-00) |
| C-07 | Retrieval | Not applicable | No internal document collection (D-00) |
| C-09 to C-11 | Multi-agent | Not applicable | Single agent (D-07) |
| O-01, O-02, O-12 | Interface, trigger, scale | From D-00 | Command line, on demand, low load |
| O-03 to O-10 | Operations | Decide now | Always applies, or external systems |
| O-11 | Deploy step | Not applicable | Local deployment (D-26) |
| Q-01 to Q-09 | Quality | Decide now / review round | Always applies; git repository |

## D-01 Agent name
- **Question asked:** "What should the agent be called?" · **Options offered:** `product-researcher` (Recommended); `research-agent`; other · **Recommendation and why (Claude):** short and descriptive
- **User's answer:** Other: "multi-source-research" · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-02 Triage
- **Question asked:** "Accept this triage?" · **Options offered:** Accept (Recommended); change rows; explain first · **Recommendation and why (Claude):** every row has a stated reason
- **User's answer:** Accept triage · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-03 Control
- **Question asked:** "Control: how much control and auditability do you need?" · **Options offered:** Moderate (Recommended); High; Low · **Recommendation and why (Claude):** plan approval and citations, with flexible search
- **User's answer:** Moderate · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-04 Complexity
- **Question asked:** "Complexity: how complex is the problem?" · **Options offered:** several domains, predictable (Recommended); open-ended; single domain · **Recommendation and why (Claude):** every run has the same shape
- **User's answer:** Several domains, predictable process · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-05 Resources
- **Question asked:** "Resources: what's the binding constraint?" · **Options offered:** tight budget per run (Recommended); ship fast; long-term platform; no hard constraint · **Recommendation and why (Claude):** $2 and 10 minutes are hard limits
- **User's answer:** Tight budget per run · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-06 Expertise
- **Question asked:** "Expertise: does it need deep expertise in one domain or several?" · **Options offered:** one domain, add skills (Recommended); several coordinating domains; not sure · **Recommendation and why (Claude):** product research throughout; know-how fits in skills
- **User's answer:** One domain, add skills · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-07 Pattern
- **Question asked:** "Which architecture pattern should the agent use?" · **Options offered:** single agent + skills + gate (Recommended); sequential; hierarchical; parallel (evaluator-optimizer named but not offered as an option) · **Recommendation and why (Claude):** tie-breaker 1, the simplest pattern meeting every hard requirement, backed by tie-breakers 3 and 4
- **User's answer:** Single agent with skills behind a plan-approval gate · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-08 Evolution
- **Question asked:** "Evolution: should the plan design for a later step beyond version 1?" · **Options offered:** Yes, next step named (Recommended); No; Hybrid now · **Recommendation and why (Claude):** the pressure points are known and preparing costs little
- **User's answer:** Yes: parallel web and database workers, triggered by measured limits · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-09 Runtime
- **Question asked:** "Which runtime should it be built on?" · **Options offered:** Agent SDK (Recommended); API loop; LangGraph + OpenRouter; Claude Code-native · **Recommendation and why (Claude):** strongest fit for a single agent; skills, hooks and a clear path to subagents
- **User's answer:** Claude Agent SDK · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-10 Code location
- **Question asked:** "Where should the agent's code live?" · **Options offered:** a new repository at a permanent path (Recommended); this repository's root; this repository's subfolder · **Recommendation and why (Claude):** the working folder is under the temporary `/private/tmp`
- **User's answer:** New git repository at `~/work/multi-source-research` · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-11 Language
- **Question asked:** "Which language?" · **Options offered:** Python (Recommended); TypeScript · **Recommendation and why (Claude):** the usual default for data-heavy agents
- **User's answer:** Python · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-12 Model access
- **Question asked:** "How will the agent reach its models?" · **Options offered:** Anthropic API (Recommended); Claude Platform on AWS or Foundry; Google Cloud; Bedrock · **Recommendation and why (Claude):** full web search and a simple setup
- **User's answer:** Anthropic API · **User's stated reason:** "we don't buy AI through a cloud provider" · **Delegated:** no · **Status:** Final

## D-13 Main model
- **Question asked:** "Which model should the main agent use?" · **Options offered:** Sonnet 5 (Recommended); Opus 5; Haiku 4.5 (Fable 5.1 named, over budget) · **Recommendation and why (Claude):** fits $2 with headroom on the estimate; fast
- **User's answer:** `claude-sonnet-5` · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-14 Background model
- **Question asked:** "Which model should the SDK use for background work?" · **Options offered:** same as main (Recommended); Haiku 4.5 pinned · **Recommendation and why (Claude):** tiny cost difference; Haiku 4.5 retires soon
- **User's answer:** Same as main (`claude-sonnet-5`) · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-15 Package manager
- **Question asked:** "Which Python package manager?" · **Options offered:** uv (Recommended); pip + venv; poetry · **Recommendation and why (Claude):** the SDK quickstart uses it; it keeps a lockfile
- **User's answer:** uv · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-16 Unverified U-1 and U-2
- **Question asked:** "How should I handle the two unverified facts?" · **Options offered:** re-check in step 2 (Recommended); research now; user supplies · **Recommendation and why (Claude):** neither changes a decision
- **User's answer:** Re-check in step 2 · **User's stated reason:** none given · **Delegated:** no · **Status:** Final (U-1 no longer matters after D-17)

## D-17 Web tools
- **Question asked:** "How should the agent search and read the web?" · **Options offered:** built-in WebSearch + WebFetch (Recommended); WebSearch + custom fetch; third-party search API · **Recommendation and why (Claude):** no code to write
- **User's answer:** Built-in WebSearch plus a custom fetch tool (size cap, domain blocklist) · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-18 Postgres
- **Question asked:** "How should the agent connect to Postgres?" · **Options offered:** custom in-process tool (Recommended); third-party server; read-only exports · **Recommendation and why (Claude):** no maintained official server; the allowlist is enforced in code
- **User's answer:** Custom in-process tool · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-19 Tool output
- **Question asked:** "How should tools keep their output small?" · **Options offered:** paginate, filter and cap (Recommended); truncate; no limits · **Recommendation and why (Claude):** protects the budget and the SQL-aggregation rule
- **User's answer:** Paginate, filter and cap · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-20 Skills
- **Question asked:** "Skills: what domain knowledge does the agent get, and from where?" · **Options offered:** three bundled skills, project only (Recommended); system prompt only; bundled + `~/.claude` · **Recommendation and why (Claude):** follows D-06; identical behavior for every analyst
- **User's answer:** Three bundled skills, project only; the metric definitions come from `docs/metrics.md` in the analytics repository and the team copies them in · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-21 Conflict: D-00 vs. SDK transcripts
- **Question asked:** "Conflict: D-00 vs. the SDK's default transcripts." · **Options offered:** mitigate, transcripts off (Recommended); accept the risk; retention limit · **Recommendation and why (Claude):** keeps the explicit requirement
- **User's answer:** Transcripts off (`CLAUDE_CODE_SKIP_PROMPT_HISTORY`) · **User's stated reason:** none given · **Delegated:** no · **Status:** Final (linked to D-00 and D-09)

## D-22 Approval gate and resuming
- **Question asked:** "How does a run cross the approval gate, and what happens after a crash?" · **Options offered:** two stages, no checkpoints (Recommended); plus a saved plan file; one continuous session · **Recommendation and why (Claude):** only the plan crosses the gate; clean research context
- **User's answer:** Two stages in one process, no checkpoints · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-23 Approval actions
- **Question asked:** "What can the analyst do at the approval gate?" · **Options offered:** approve/feedback/cancel (Recommended); approve/cancel; edit in an editor · **Recommendation and why (Claude):** fix a misread question before spending on research
- **User's answer:** Approve, send feedback (revise, capped), or cancel · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-24 Report production
- **Question asked:** "How is the report produced?" · **Options offered:** agent markdown + code checks (Recommended); structured JSON rendered by code; markdown + JSON sidecar · **Recommendation and why (Claude):** natural prose with guaranteed exact parts
- **User's answer:** The agent writes the markdown; code appends the SQL and checks the report · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-25 Context
- **Question asked:** "How should the agent keep its context under control?" · **Options offered:** automatic compaction + capped tools (Recommended); subagent for reading pages; summarize and hand off · **Recommendation and why (Claude):** the budget ends a run long before 1M tokens
- **User's answer:** Automatic compaction plus capped tools · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-26 Deployment
- **Question asked:** "Where does the agent run?" · **Options offered:** analysts' laptops (Recommended); a shared machine; a container · **Recommendation and why (Claude):** D-00 puts the report on the analyst's machine; low load
- **User's answer:** Each analyst's laptop; laptops reach Postgres over the corporate VPN · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-27 Tracing
- **Question asked:** "How will you see what the agent did and why?" · **Options offered:** run summary + opt-in trace (Recommended); always trace with retention; summary only; OpenTelemetry · **Recommendation and why (Claude):** normal runs keep a single write
- **User's answer:** Run summary plus opt-in `--trace`, which also amends D-00 · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-28 Errors
- **Question asked:** "What happens when a step fails?" · **Options offered:** retry then fail loudly (Recommended); partial report marked INCOMPLETE; cheaper-model fallback · **Recommendation and why (Claude):** never a half-finished report that looks finished
- **User's answer:** Retry with backoff, then fail loudly; no report · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-29 Containment
- **Question asked:** "How is the agent contained? Pick any." · **Options offered:** minimal tools + `dontAsk` (Recommended); internal-address block (Recommended); database grants on the two views (Recommended); container · **Recommendation and why (Claude):** no shell or file tools; VPN exposure
- **User's answer:** a, b, c · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-30 Guardrails
- **Question asked:** "Which guardrails should the plan include? Pick any." · **Options offered:** injection defenses (Recommended); fetch only search-result URLs (Recommended); personal-data redaction; topic restriction · **Recommendation and why (Claude):** closes the main way to leak data
- **User's answer:** a, b · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-31 Where pseudonyms are applied
- **Question asked:** "Where do team names get replaced with pseudonyms?" · **Options offered:** in the SQL tool (Recommended); at write time · **Recommendation and why (Claude):** the model never sees real names
- **User's answer:** In the SQL tool, before results reach the model · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-32 Pseudonym lifetime
- **Question asked:** "How long does a pseudonym stay the same?" · **Options offered:** only within one report (Recommended; the more private option, with no strong basis either way); across all reports · **Recommendation and why (Claude):** teams can't be tracked across reports; no key needed
- **User's answer:** Only within one report · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-33 Secrets
- **Question asked:** "How are the API key and database credentials stored on each laptop?" · **Options offered:** OS keychain (Recommended); `.env`; password-manager tool · **Recommendation and why (Claude):** no plaintext secrets on disk
- **User's answer:** macOS Keychain; all 5 analysts use macOS · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-34 Credentials
- **Question asked:** "Credentials per analyst, or shared?" · **Options offered:** per analyst (Recommended); shared; mixed · **Recommendation and why (Claude):** revocation, audit trail, cost per analyst
- **User's answer:** Per analyst · **User's stated reason:** none given · **Delegated:** no · **Status:** Final (spend-limit wording resolved by D-37)

## D-35 Cost controls
- **Question asked:** "Cost controls. Pick any." · **Options offered:** hard cap (Recommended); soft wrap-up (Recommended); search/fetch limits (Recommended); monthly workspace limit · **Recommendation and why (Claude):** protects the $2 cap without throwing away runs
- **User's answer:** a, b, c · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-36 Unverified U-3 and U-4
- **Question asked:** "How should I handle the unverified items?" · **Options offered:** re-check in step 2 (Recommended); research now; user supplies · **Recommendation and why (Claude):** very likely workable
- **User's answer:** Re-check in step 2; stop and ask if either fails · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-37 Conflict: D-34 vs. D-35
- **Question asked:** "Conflict: D-34 (a workspace spend limit) vs. D-35 (no workspace spend limit)." · **Options offered:** a high backstop limit (Recommended); a normal monthly limit; no limit · **Recommendation and why (Claude):** stops runaway bugs without blocking normal use
- **User's answer:** A high backstop limit (about $400 a month, per D-45 item 11) · **User's stated reason:** none given · **Delegated:** no · **Status:** Final (linked to D-34 and D-35)

## D-38 Metrics
- **Question asked:** "Success metrics." (M-1 to M-7 proposed) · **Options offered:** accept (Recommended); change targets; add or remove · **Recommendation and why (Claude):** drawn from D-00
- **User's answer:** Accept · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-39 Eval dataset
- **Question asked:** "Where do the eval test questions come from?" · **Options offered:** about 20 hand-written (Recommended); sampled from real questions; synthetic then reviewed · **Recommendation and why (Claude):** no production history yet; covers edge cases on purpose
- **User's answer:** About 20 hand-written by analysts · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-40 Grading
- **Question asked:** "How are eval results judged? Pick any." · **Options offered:** code checks (Recommended); model judge on `claude-opus-5` (Recommended); analyst review (Recommended); comparison with the previous version · **Recommendation and why (Claude):** covers exactness, groundedness and D-00's measure
- **User's answer:** a, b, c · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-41 Eval tooling
- **Question asked:** "What runs the evals?" · **Options offered:** pytest + eval script (Recommended); an eval framework; a custom script only · **Recommendation and why (Claude):** close to the standard test runner
- **User's answer:** pytest plus an eval script · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-42 Tests
- **Question asked:** "Which automated tests should the plan include? Pick any." · **Options offered:** unit (Recommended); integration (Recommended); end-to-end smoke (Recommended); full evals on every change · **Recommendation and why (Claude):** guards are the critical code; evals are expensive
- **User's answer:** a, b, c · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-43 CI
- **Question asked:** "Should the repository get CI?" · **Options offered:** GitHub Actions lint + tests (Recommended); plus smoke test; other CI; none · **Recommendation and why (Claude):** CI can't reach the VPN
- **User's answer:** GitHub Actions: lint and tests; evals on demand · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-44 Docs
- **Question asked:** "Which docs should the build produce? Pick any." · **Options offered:** README (Recommended); runbook (Recommended); architecture overview (Recommended); none
- **User's answer:** a, b, c · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-45 Derived-details bundle
- **Question asked:** "The derived-details bundle above" · **Options offered:** accept all (Recommended); edit some
- **User's answer:** Accept all · **User's stated reason:** none given · **Delegated:** no · **Status:** Final
- **Items:**
  1. **Layout.** `src/multi_source_research/` with `cli.py`, `stages.py`, `tools/sql.py`, `tools/fetch.py`, `pseudonyms.py`, `checks.py`, `config.py`; `.claude/skills/…/SKILL.md`; `tests/`, `evals/`, `docs/`.
  2. **Running it.** The command is `msr "<question>"` with `--trace` and `--out DIR`. Installed from a uv clone. The SDK working folder is the clone, with `setting_sources=["project"]`.
  3. **Output files.** Reports go to `./reports/{date}-{slug}.md`, with `-2`, … on collision. Traces go to `./traces/{stem}.jsonl`, opt-in only, holding only what the model saw, never auto-deleted.
  4. **Report structure.** Question, Answer summary, Web findings, Internal data findings, Limitations, Sources, Appendix A (SQL), Appendix B (run details).
  5. **Limits.**
     - 200 rows per page;
     - a 30-second statement timeout;
     - fetched pages in parts of about 6,000 tokens;
     - at most 20 searches and 12 fetches;
     - at most 3 feedback rounds;
     - planning limited to 5 turns;
     - a hard stop at 12 minutes.
  6. **Budget.** The research cap is $2.00 minus planning spend. Wrap-up at $1.50 or 7 minutes. Effort starts at the default and is tuned in evals.
  7. **Stage setup.** Planning: Skill only, with `output_format`. Research: WebSearch, Skill, `sql_query` and `fetch_page`; `dontAsk`; the three skills; `CLAUDE_CODE_SKIP_PROMPT_HISTORY=1`; both model settings set to `claude-sonnet-5`.
  8. **Pseudonyms.** Team A, B, … in random order per run, with the mapping in memory only.
  9. **Metrics.** The definitions are inlined in `sql-analysis/SKILL.md`.
  10. **Keychain.** Uses `security` with service `multi-source-research` and accounts `anthropic_api_key` and `pg_dsn`.
  11. **Workspace backstop.** About $400 a month, set by a person in the Console.
  12. **Packages.** `claude-agent-sdk` (pinned in `uv.lock`), `psycopg`, `trafilatura`, `pytest`, `ruff`, all verified in step 2.
  13. **Evals.** `evals/questions.yaml`, `evals/run.py`, results in `evals/results/{date}/`; the malicious-page fixture.
  14. **CI.** `.github/workflows/ci.yml`. Creating the repository and pushing are left to the user.
  15. **`.gitignore`.** `reports/`, `traces/`, `evals/results/`, `.env*`, `.venv/`.
  16. **Plan files.** `.agent-builder/multi-source-research/plan.md` and `decisions.md`, in the repository.

## D-46 `.agent-builder/` in git
- **Question asked:** "Should `.agent-builder/` be committed, or kept out of git?" · **Options offered:** commit (Recommended); gitignore · **Recommendation and why (Claude):** a reviewable history of decisions
- **User's answer:** Commit it · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-47 Git workflow
- **Question asked:** "How should the build be committed while the plan executes?" · **Options offered:** feature branch, one commit per step (Recommended); one commit at the end; commit to `main`; don't commit · **Recommendation and why (Claude):** easy to review and roll back
- **User's answer:** Feature branch (`build/v1`), one commit per step · **User's stated reason:** none given · **Delegated:** no · **Status:** Final

## D-48 Decisions final
- **Question asked:** "Are all decisions final?" · **Options offered:** Yes, finalize (Recommended); change some; add a missing requirement
- **User's answer:** Yes, finalize · **User's stated reason:** none given · **Delegated:** no · **Status:** Final. It was given before D-49 to D-51, which are confirmed by plan approval.

## D-49 Report-check failure
- **Question asked:** "What happens when a finished report fails the code checks (D-24)?" · **Options offered:** one repair turn (Recommended); a failed run; save with a banner · **Recommendation and why (Claude):** most failures are small; protects M-7
- **User's answer:** One repair turn; a team-name leak fails the run outright · **User's stated reason:** none given · **Delegated:** no · **Status:** Final on approval

## D-50 Evals and the approval gate
- **Question asked:** "Evals run unattended. How do they get past the approval gate?" · **Options offered:** approve automatically and save the plan (Recommended); analyst approves each; pre-written plans · **Recommendation and why (Claude):** runs unattended while plan quality stays visible
- **User's answer:** Approve the first plan automatically and save it · **User's stated reason:** none given · **Delegated:** no · **Status:** Final on approval

## D-51 Internal network list
- **Question asked:** "The fetch tool's internal-address block (D-29b) needs your organization's specifics." · **Options offered:** type them now; make it a precondition (Recommended if not to hand) · **Recommendation and why (Claude):** don't block the plan on IT input
- **User's answer:** A precondition from IT, needed at step 6; standard ranges are always blocked · **User's stated reason:** none given · **Delegated:** no · **Status:** Final on approval
