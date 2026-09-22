# Decisions: multi-source-research

- Planned: 2026-09-22 with agent-builder 0.1.0
- Session: (example session)
- Mode: fallback (plain-text questions; plan shown in chat)
- Review gate: "Are all decisions final?" → Yes, finalize (Round 16)

## D-00 Purpose (confirmed)
(The text is in §1 of the plan.) Confirmed in Round 3 with "keep the bracketed sentence".
- **Status:** Amended 2026-09-22 by D-24: "The only write is the report file on the analyst's machine" became "The agent writes only local files in its own folders on the analyst's machine (reports, run state, logs)."
- Purpose inputs (Rounds 1–2):
  - report destination: a markdown file in a local output folder;
  - "correlate": SQL-computed numbers only, with queries, no causal claims;
  - database: an allowlist of two views, and "tool_rollouts records which tools each team adopted and when";
  - questions: open-ended, and the agent decides the sources;
  - approval: the analyst approves the research plan; user note: "the time the analyst takes to approve does not count toward the 10 minutes";
  - data: hosted model OK, reports pseudonymize teams;
  - scale: low, "about 5 analysts";
  - sources: numbered inline citations plus a SQL appendix.

## Triage
| ID | Topic | Status | Reason |
|---|---|---|---|
| F-01–F-05, F-07–F-09 | Foundation | Decide now | Always / code is written |
| F-06 | Claude Code primitives | Conditional → Not applicable (D-10) | Runtime isn't Claude Code-native |
| C-01–C-05, C-08, C-12 | Capabilities | Decide now | Named systems, large outputs, long runs, approval pause |
| C-06 | Memory | Not applicable | D-00 describes independent on-demand runs |
| C-07 | Document retrieval | Not applicable | No internal document corpus; web covered by C-02 |
| C-09–C-11 | Multi-agent details | Conditional → Not applicable (D-18) | Single agent |
| O-01 / O-02 / O-12 | Interface / trigger / scale | From D-00 | Command line / on demand / low load, about 5 analysts |
| O-03–O-10 | Operations | Decide now | Always, or systems are reached |
| O-11 | Deploy step | Conditional → Not applicable (D-32) | Local target |
| Q-01–Q-05, Q-09 | Quality | Decide now | Always / code is written |
| Q-06 | Agent CI | Conditional → Decide now | Code is in a git repo (D-11) |
| Q-07 / Q-08 | Git flow / plan in git | At review gate | Git repo / always |

Process note (not an agent decision): the first lookups were blocked by permissions. The user chose "Allow WebFetch and retry" and allowed web lookups (Round 7).

## D-01 Agent name
- **Question asked:** "What should the agent be called?"
- **Options offered:** `product-researcher` (Recommended); `research-agent`; something else
- **Recommendation and why (Claude):** `product-researcher`: short, and says what it does for whom
- **User's answer:** Other: "multi-source-research"
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-02 Triage
- **Question asked:** "Accept this triage?"
- **Options offered:** Accept triage (Recommended); Change some rows; Explain first
- **Recommendation and why (Claude):** every row has a stated reason; the Not-applicable rows follow from D-00
- **User's answer:** Accept triage
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-03 Control
- **Question asked:** "Control: how much control and auditability do you need?"
- **Options offered:** Moderate: oversight at key steps (Recommended); High: every decision traceable; Low: exploration is the point
- **Recommendation and why (Claude):** analysts approve the plan and claims must be cited, but the search path varies
- **User's answer:** Moderate
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-04 Complexity
- **Question asked:** "Complexity: how complex is the problem?"
- **Options offered:** Several domains, predictable process (Recommended); Complex and open-ended; Single domain, repeatable
- **Recommendation and why (Claude):** every run has the same shape even though the questions vary
- **User's answer:** Several domains, predictable process
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-05 Resources
- **Question asked:** "Resources: what's the binding constraint?"
- **Options offered:** Tight budget per run (Recommended); Ship fast; Long-term platform; No hard constraint
- **Recommendation and why (Claude):** $2 and 10 minutes per report are hard limits in D-00
- **User's answer:** Tight budget per run
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-06 Expertise
- **Question asked:** "Expertise: does it need deep expertise in one domain or several?"
- **Options offered:** One domain, add skills (Recommended); Several domains that must coordinate; Not sure yet
- **Recommendation and why (Claude):** it's product research throughout; the know-how can be packaged as skills
- **User's answer:** One domain, add skills
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-07 Pattern (F-01)
- **Question asked:** "Which architecture pattern should the agent use?" (the evaluator-optimizer was named as possible)
- **Options offered:** Single agent with skills, behind a plan-approval gate (Recommended); Sequential workflow; Hierarchical; Parallel workflow
- **Recommendation and why (Claude):** tie-breaker 1 (the simplest pattern meeting every hard requirement), backed by skills-first and lowest cost
- **User's answer:** Single agent with skills, behind a plan-approval gate
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-08 Evolution (F-02)
- **Question asked:** "Evolution: should the plan design for a later step beyond version 1?"
- **Options offered:** Yes: name the next step (Recommended); No: build exactly this; Hybrid now
- **Recommendation and why (Claude):** the likely pressure points (context, the 10-minute limit) are known, and preparing for them costs little
- **User's answer:** Yes. Next step: parallel web and database workers under a lead, used when context overflows or runs exceed 10 minutes
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-09 Runtime (F-04)
- **Question asked:** "Which runtime should it be built on?"
- **Options offered:** Claude Agent SDK (Recommended); Claude API tool-use loop; LangGraph with OpenRouter; Claude Code-native
- **Recommendation and why (Claude):** Agent SDK: the strongest fit for a single agent, with native skills, hooks for the gate, and subagents for the next step
- **User's answer:** LangGraph with OpenRouter
- **User's stated reason:** "we want LangGraph for the explicit graph and built-in checkpointed pause for approval"
- **Delegated:** no
- **Status:** Final

## D-10 Claude Code primitives (F-06)
- **Question asked:** none; triage rule (D-02): only applies to a Claude Code-native runtime
- **Options offered:** n/a
- **Recommendation and why (Claude):** Not applicable, because D-09 is LangGraph
- **User's answer:** covered by accepting the triage (D-02)
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-11 Code location (F-03)
- **Question asked:** "Where should the agent's code live?"
- **Options offered:** This repository, at its root (Recommended); A new git repository at a permanent path; A new directory without git
- **Recommendation and why (Claude):** already an empty git repo and planning started here; moving it later is one `mv` (the `/tmp` risk was flagged)
- **User's answer:** This repository, at its root
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-12 Language (F-05)
- **Question asked:** "Which language?"
- **Options offered:** Python (Recommended); JavaScript/TypeScript
- **Recommendation and why (Claude):** a data- and SQL-heavy agent; no existing code to match
- **User's answer:** Python
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-13 Model access (F-07)
- **Question asked:** "Model access through OpenRouter: how should team-level data be routed?"
- **Options offered:** Route only to providers that don't keep or train on prompts (Recommended); Default routing; Routing team data through OpenRouter isn't acceptable
- **Recommendation and why (Claude):** keeps the extra middle party from holding team data
- **User's answer:** Route only to providers that don't keep or train on prompts; "we already have an OpenRouter account and API key"
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-14 Model: main agent (F-08)
- **Question asked:** "Which model should the main research agent use?"
- **Options offered:** Claude Sonnet 5 (Recommended); Claude Opus 5; Claude Haiku 4.5
- **Recommendation and why (Claude):** the only strong tier that fits $2 by estimate; 1M context; retirement not before 2027-06-30
- **User's answer:** Claude Sonnet 5 (`anthropic/claude-sonnet-5`)
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-15 Model: page shrinking (F-08)
- **Question asked:** "Should a separate step shrink fetched web pages before the main agent reads them?"
- **Options offered:** Yes, using Sonnet 5 (Recommended); Yes, using Haiku 4.5; No separate step
- **Recommendation and why (Claude):** keeps raw pages out of the main context; one model to manage; no Haiku retirement risk
- **User's answer:** Yes, using Sonnet 5
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-16 OpenRouter data setting
- **Question asked:** "Which OpenRouter setting should enforce D-13?"
- **Options offered:** Zero data retention (`zdr`), account-wide (Recommended); `data_collection: "deny"`; Both
- **Recommendation and why (Claude):** matches "don't keep prompts" literally; Claude stays available via Bedrock and Vertex
- **User's answer:** ZDR, enforced account-wide
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-17 Package manager (F-09)
- **Question asked:** "Which Python package manager?"
- **Options offered:** uv (Recommended); pip + venv; poetry
- **Recommendation and why (Claude):** a lockfile gives every analyst an identical install, and uv installs the required Python
- **User's answer:** uv
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-18 Multi-agent topics (C-09, C-10, C-11)
- **Question asked:** none; triage rule (D-02): only for multi-agent or evaluator patterns
- **Options offered:** n/a
- **Recommendation and why (Claude):** Not applicable, because D-07 is a single agent
- **User's answer:** covered by accepting the triage (D-02)
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-19 Postgres integration (C-02)
- **Question asked:** "How should the agent connect to Postgres?"
- **Options offered:** In-code tool using psycopg 3.3.6 (Recommended); A community MCP server; A read-only snapshot
- **Recommendation and why (Claude):** no official or maintained MCP server exists; only two views; the allowlist and read-only rule are enforced in our own code
- **User's answer:** In-code psycopg tool
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-20 Web search (C-02)
- **Question asked:** "How should the agent search the web?" (Google, SearchApi, Perplexity, You.com, SerpAPI named)
- **Options offered:** Tavily via LangChain (Recommended); OpenRouter `openrouter:web_search`; Exa via LangChain
- **Recommendation and why (Claude):** the model decides its own queries; results include content; kept separate from model routing and ZDR
- **User's answer:** Tavily via LangChain
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-21 Web page reading (C-02)
- **Question asked:** "How should the agent read full web pages?"
- **Options offered:** In-code fetch tool (Recommended); Only the search provider's content
- **Recommendation and why (Claude):** works with any search provider; D-15's shrinking step lives here
- **User's answer:** In-code fetch tool
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-22 Skills (C-04)
- **Question asked:** "How should 'skills' (D-06, D-07) work in LangGraph?"
- **Options offered:** A plain LangGraph graph with `SKILL.md`-format files loaded per step (Recommended); Deep Agents for the research step; No skills files
- **Recommendation and why (Claude):** matches the D-09 reason ("explicit graph"); same file format as Deep Agents; no extra framework
- **User's answer:** Plain LangGraph graph with `SKILL.md` files; "the three skill topics are right" (SQL analysis method; citation and pseudonym rules; report structure)
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-23 Tool sources (C-01)
- **Question asked:** none separately; follows from the answers to D-19–D-21, shown at the review gate
- **Options offered:** n/a
- **Recommendation and why (Claude):** n/a
- **User's answer:** In-code tools plus LangChain's Tavily tool; no MCP servers (confirmed via "Yes, finalize")
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-24 Local-write scope (D-00)
- **Question asked:** "How strict is 'the only write is the report file'?"
- **Options offered:** Amend D-00: local files only in its own folders (Recommended); Keep it strict; Allow run state and logs but delete them after success
- **Recommendation and why (Claude):** keeps the intent (read-only on every system) while allowing resume and traces
- **User's answer:** Amend D-00
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-25 Tool output limits (C-03)
- **Question asked:** "How should tools keep responses small?"
- **Options offered:** Paginate, filter and cap (Recommended); Truncate with a notice; No limits
- **Recommendation and why (Claude):** small, cheap turns; pushes the agent toward SQL aggregates
- **User's answer:** Paginate, filter and cap
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-26 Context management (C-05)
- **Question asked:** "How should the agent keep its context under control during a run?"
- **Options offered:** Capped tools, page shrinking, source register and context editing (Recommended); The same with Summarization; Capped tools and page shrinking only
- **Recommendation and why (Claude):** keeps per-turn cost flat; the register means no citation is lost
- **User's answer:** Capped tools + page shrinking + source register + Context editing middleware, with a `create_agent` research step inside the graph
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-27 Output format (C-12)
- **Question asked:** "What form should the output take?"
- **Options offered:** Markdown with a YAML metadata block (Recommended); Markdown plus a JSON sidecar; Markdown only
- **Recommendation and why (Claude):** one file; evals and budget tracking can read it by script
- **User's answer:** Markdown with a YAML metadata block
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-28 Resume (C-08)
- **Question asked:** "How should a run survive a crash or a long approval wait?"
- **Options offered:** A SQLite checkpointer, saving every step (Recommended); In memory only; No resume
- **Recommendation and why (Claude):** this is the "checkpointed pause" behind D-09; D-24 allows it
- **User's answer:** SQLite checkpointer, every step, resume by run ID
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-29 Approval details (O-03)
- **Question asked:** "What can the analyst do when the plan is shown?"
- **Options offered:** Approve, give feedback, or cancel (Recommended); Approve or cancel only; Approve, cancel, or edit the plan directly
- **Recommendation and why (Claude):** a misread question is fixed in one loop instead of a rerun
- **User's answer:** Approve / feedback (revise, up to N times) / cancel
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-30 Containment (O-04)
- **Question asked:** "How is the agent contained?" (choose any)
- **Options offered:** Read-only role on the two views (Recommended); Strict tool list (Recommended); Fetch refuses internal addresses (Recommended); Container or VM (not recommended)
- **Recommendation and why (Claude):** enforces D-00 in the database; nothing else needed; blocks internal-URL leaks
- **User's answer:** a, b, c
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-31 Deployment target (O-10)
- **Question asked:** "Where will the agent run?"
- **Options offered:** Each analyst's laptop (Recommended); A shared internal machine; A container image
- **Recommendation and why (Claude):** D-00 command line with reports on the analyst's machine; low load
- **User's answer:** Each analyst's laptop, installed with uv
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-32 Deploy as a plan step (O-11)
- **Question asked:** none; triage rule (D-02): only applies when the target isn't local
- **Options offered:** n/a
- **Recommendation and why (Claude):** Not applicable (D-31 is local)
- **User's answer:** covered by accepting the triage (D-02)
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-33 Secrets (O-05)
- **Question asked:** "How are credentials provided on each laptop?", plus the database login model
- **Options offered:** A `.env` file (Recommended); The OS keychain; A cloud secret manager. Plus: (i) one login per analyst (Recommended); (ii) one shared login
- **Recommendation and why (Claude):** the simplest for a local CLI with narrowly scoped credentials; per-analyst logins give a trail and single revocation
- **User's answer:** a-i
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-34 Guardrails (O-06)
- **Question asked:** "Which guardrails?" (choose any)
- **Options offered:** Prompt-injection defences (Recommended); Code check on the report before saving (Recommended); Search-query screen (Recommended); PII-detection middleware (not recommended)
- **Recommendation and why (Claude):** untrusted web input; enforce D-00 in code; stop team names reaching Tavily
- **User's answer:** a, b, c
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-35 Pseudonyms
- **Question asked:** "How should team pseudonyms work?" (replaced inside the SQL tool in every option)
- **Options offered:** A fresh random mapping each run, never saved (Recommended); The same pseudonym across reports; A fresh mapping, saved in run state
- **Recommendation and why (Claude):** the most private, the simplest, and reversible
- **User's answer:** A fresh random mapping each run, never saved
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Amended 2026-09-22 by D-37: the mapping is derived from a keyed hash of run ID + secret, so it's reproducible on resume and still never saved

## D-36 Tracing (O-07)
- **Question asked:** "How will you see what the agent did?", plus retention days
- **Options offered:** A local structured log per run (Recommended); LangSmith; OpenTelemetry; OpenRouter dashboard only. Retention: 30 days recommended
- **Recommendation and why (Claude):** data stays local (D-24); no extra vendor; enough for debugging and evals
- **User's answer:** Local JSON-lines log per run + 30 days
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-37 Conflict: D-28 × D-35
- **Question asked:** "Conflict: D-35 (random pseudonym mapping, never saved) vs. D-28 (resume after a crash)"
- **Options offered:** Add a mitigation: keyed hash of run ID + secret key in `.env` (Recommended); Change D-35: save the mapping; Change D-28: in memory only; Keep both and accept the risk
- **Recommendation and why (Claude):** keeps both of the user's explicit choices intact
- **User's answer:** Add a mitigation (keyed hash)
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final (linked to D-28 and D-35)

## D-38 Cost controls (O-08)
- **Question asked:** "How should cost be controlled?" (choose any)
- **Options offered:** Per-run budgets for cost and agent time (Recommended); Prompt caching (Recommended); Call limits (Recommended); A cheaper model for page shrinking (not recommended)
- **Recommendation and why (Claude):** turns D-00's limits into enforced rules; caching is needed for the estimate; call limits are a backstop against loops
- **User's answer:** a, b, c
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-39 Error handling (O-09)
- **Question asked:** "What happens when a step fails?"
- **Options offered:** Retry with backoff, then stop with a clear error and the run ID (Recommended); Retry, then fall back to a partial report; Retry, then switch to another model
- **Recommendation and why (Claude):** the analyst is present; checkpoints mean little is lost
- **User's answer:** Retry with backoff, then stop with a clear error and the run ID
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-40 Metrics (Q-01)
- **Question asked:** "Success metrics" (M1–M6 as proposed)
- **Options offered:** Accept these metrics (Recommended); Change targets; Add or remove metrics
- **Recommendation and why (Claude):** M1–M3 are the D-00 criteria; M4–M6 make the sourcing and pseudonym rules checkable
- **User's answer:** Accept
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-41 Eval dataset (Q-02)
- **Question asked:** "Where do the eval cases come from?", plus the database used for evals
- **Options offered:** About 20 hand-written questions (Recommended); Sampled from real requests; Synthetic then reviewed. Database: (i) test database plus live views for rated runs (Recommended); (ii) live only; (iii) test database only
- **Recommendation and why (Claude):** no real runs yet; known answers make M6 checkable
- **User's answer:** a-i
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-42 Grading (Q-03)
- **Question asked:** "How are results graded?" (choose any), plus the judge model
- **Options offered:** Programmatic checks (Recommended); Model-as-judge rubric (Recommended); Analyst ratings (Recommended); Pairwise comparison against a baseline (later). Judge: Opus 5 (Recommended); Sonnet 5
- **Recommendation and why (Claude):** code can't grade prose; M1 needs people; a different, stronger judge reduces self-preference
- **User's answer:** a, b, c + Opus 5 (`anthropic/claude-opus-5`)
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-43 Eval tooling (Q-04)
- **Question asked:** "What runs the evals?"
- **Options offered:** pytest plus an eval script (Recommended); LangSmith evaluations; A dedicated eval framework
- **Recommendation and why (Claude):** stays with the standard runner; data stays local (D-36)
- **User's answer:** pytest plus an eval script
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-44 Test layers (Q-05)
- **Question asked:** "Which automated tests?" (choose any)
- **Options offered:** Unit tests (Recommended); Integration tests (Recommended); End-to-end smoke test on demand (Recommended); Full evals on every change (not recommended)
- **Recommendation and why (Claude):** covers every guard and the graph flow; full evals cost about $30–40 per run
- **User's answer:** a, b, c
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-45 CI (Q-06)
- **Question asked:** "Should the agent's repository get CI?"
- **Options offered:** GitHub Actions: lint + unit and integration tests (Recommended); GitHub Actions: lint + tests + evals; Other CI; No CI for now
- **Recommendation and why (Claude):** no keys or token cost in CI; every change checked
- **User's answer:** GitHub Actions: lint + unit and integration tests
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-46 Documentation (Q-09)
- **Question asked:** "Which docs should the build produce?" (choose any)
- **Options offered:** README (Recommended); Runbook (Recommended); Architecture overview (Recommended); No extra docs
- **Recommendation and why (Claude):** the users are analysts; the diagram already exists; it helps the D-08 next step
- **User's answer:** a, b, c
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-47 `.agent-builder/` in git (Q-08)
- **Question asked:** "Should `.agent-builder/` be committed or kept out of git?"
- **Options offered:** Commit it (Recommended); Add it to `.gitignore`
- **Recommendation and why (Claude):** the reasons behind each choice travel with the code; no secrets in the plan
- **User's answer:** Commit it
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-48 Git workflow (Q-07)
- **Question asked:** "How should the build be committed while the plan executes?"
- **Options offered:** A feature branch, one commit per step (Recommended); A feature branch, one commit at the end; Commit straight to `main`; Don't commit
- **Recommendation and why (Claude):** each step is easy to review and revert
- **User's answer:** A feature branch, one commit per step (initial `.gitignore` commit on `main` first)
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-49 Team names in the question
- **Question asked:** "Gap: what happens when the analyst's question contains a real team name?"
- **Options offered:** Pseudonymize it on the way in (Recommended); Reject the question; Leave it as is
- **Recommendation and why (Claude):** keeps D-35's guarantee end to end; analysts can still ask about a specific team
- **User's answer:** Pseudonymize it on the way in
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final

## D-50 Details bundle
- **Question asked:** "The details bundle above"
- **Options offered:** Accept all 17 (Recommended); Edit some
- **Recommendation and why (Claude):** each item is a minor default derived from earlier decisions
- **User's answer:** Accept all 17. Items:
  1. layout;
  2. commands, Python 3.12, ruff, pytest;
  3. `~/multi-source-research/{reports,runs,logs}` and the file name;
  4. environment variable names;
  5. caps of 200 rows / about 2K tokens / 5 results / 200 KB;
  6. call limits of 40/20/12 and 3 plan revisions;
  7. budget thresholds and accounting;
  8. hard stop: no partial report, can't be resumed;
  9. SQL guard and 30 s timeout;
  10. fetch guard;
  11. pseudonym labels; logs pseudonymized only;
  12. per-request `zdr` and a 5-minute cache;
  13. context threshold and effort tuned in evals;
  14. 3 retries;
  15. 30-day cleanup at start;
  16. report sections;
  17. test database in Docker and CI; eval results path.
- **User's stated reason:** none given
- **Delegated:** no
- **Status:** Final
