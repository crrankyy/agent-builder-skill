# Agent build plan: multi-source-research

> Planned with agent-builder 0.1.0 on 2026-09-22. Every decision in this plan was made by the user; see Appendix A.

## 0. How to execute this plan

- Execute the steps in order. After each step, run its acceptance check. Continue only when the check passes.
- If a step can't be done as written (a tool is missing, an API changed, a decision turns out to be impossible), **stop and ask the user**. Never substitute your own choice. Record the outcome as an amendment in `.agent-builder/multi-source-research/decisions.md`.
- Never write secret values into files or logs; use the variable names listed in §5.
- Writes to `.claude/` or `.mcp.json` always ask for approval, even in auto mode. This plan doesn't touch them.
- The plan works in any approval mode: auto, accept-edits or manual.
- Git (D-48): one commit per step on `feat/multi-source-research`, with the message `Step {n}: {title}`. Never push, and never merge into `main`; the user reviews the branch.

## 1. Purpose (D-00, confirmed; amended by D-24)

> **multi-source-research** helps the product team's analysts (about 5) answer open-ended product research questions with a sourced markdown report, by researching the public web and querying the internal Postgres analytics database read-only, deciding for each question whether it needs the web, the database or both. It uses the public web and two allowlisted views: `analytics.team_weekly_metrics` (per-team weekly PR throughput, cycle time, incident count) and `analytics.tool_rollouts` (tool name, team, rollout date). Internal findings are numbers computed in SQL only (aggregates, before/after-rollout comparisons, Postgres correlation). Each comes with its query, and the report makes no causal claims. Reports state the sample sizes behind each number and the limits of small-team data. Every claim carries a numbered inline citation to a Sources section: web sources by URL, title and access date, database findings by view name, with the exact SQL in an appendix. Reports never name teams; teams appear under pseudonyms.
> It is triggered on demand from the command line and writes the report as a markdown file in a local output folder, printing its path.
> Humans approve the research plan (sub-questions, and which sources and views it will use) before research starts; the analyst then reviews the finished report.
> Success means analysts rate at least 8 of 10 reports usable without edits, and each report takes under 10 minutes of agent working time (plan-approval wait excluded) and costs under $2.
> Out of scope: dashboards, and writing to any system. The agent writes only local files in its own folders on the analyst's machine (reports, run state, logs).
> Constraints: read-only on the web and the database; query results may go to a hosted model; low load.

## 2. Decisions at a glance

| ID | Topic | Decision |
|---|---|---|
| D-01 | Name | `multi-source-research` |
| D-02 | Triage | Not applicable: C-06, C-07. From D-00: O-01 command line, O-02 on demand, O-12 low load |
| D-03 – D-06 | Framework | Moderate control; several domains with a predictable process; tight budget per run; one domain plus skills |
| D-07 | Pattern | Single agent with skills, behind a plan-approval gate |
| D-08 | Evolution | Next step: parallel web and database workers under a lead |
| D-09 | Runtime | LangGraph + OpenRouter |
| D-10 | Claude Code primitives | Not applicable |
| D-11 / D-12 / D-17 | Code | This repo's root / Python / uv |
| D-13 / D-16 | Model access | OpenRouter; ZDR enforced account-wide |
| D-14 / D-15 | Models | Main agent and page shrinking: `anthropic/claude-sonnet-5` |
| D-18 | Multi-agent topics | Not applicable |
| D-19 – D-21, D-23 | Tools | psycopg SQL tool; Tavily search; fetch tool with page shrinking; no MCP |
| D-22 | Skills | `SKILL.md` files loaded per step (SQL analysis; citations and pseudonyms; report structure) |
| D-24 | Local writes | Only its own folders (reports, run state, logs) |
| D-25 / D-26 | Context | Paginate, filter and cap; source register; Context editing middleware; `create_agent` research step |
| D-27 | Output | Markdown with YAML metadata block |
| D-28 / D-29 | Run control | SQLite checkpoints, resume by run ID; approve / feedback (up to 3) / cancel |
| D-30 | Containment | Read-only role on the two views; 3 tools; fetch blocks internal addresses |
| D-31 / D-32 | Deploy | Analysts' laptops via uv; no deploy step |
| D-33 | Secrets | `.env` on each laptop; one read-only database login per analyst |
| D-34 | Guardrails | Injection defences; report check; search-query screen |
| D-35 / D-37 / D-49 | Pseudonyms | Keyed hash of run ID + secret; never saved; applied in the SQL tool and to the question on the way in |
| D-36 | Tracing | Local JSON-lines logs; 30-day retention |
| D-38 / D-39 | Cost and errors | Budgets (wrap-up at 80%, stop at $2 / 10 min), caching, call limits; retry, then stop with run ID |
| D-40 – D-44 | Quality | Metrics M1–M6; about 20 hand-written cases; test database; programmatic + Opus 5 judge + analyst ratings; pytest; unit, integration and smoke tests |
| D-45 / D-46 | CI and docs | GitHub Actions for lint and tests; README, runbook, architecture |
| D-47 / D-48 | Git | Commit `.agent-builder/`; feature branch with a commit per step |
| D-50 | Details | Bundle of 17 items accepted (listed in Appendix A) |

## 3. Architecture

A single research agent runs inside an explicit LangGraph graph on the analyst's laptop.
1. **intake** pseudonymizes the question.
2. **plan** produces a structured research plan.
3. **approve** is a checkpointed pause where the analyst approves, gives feedback or cancels.
4. **research** is a `create_agent` loop with three tools (read-only SQL, Tavily search, page fetch with shrinking) and middleware for context editing, call limits and retries.
5. **write** drafts the report from the source register.
6. **check** runs the report check in code.
7. **save** writes the report file.

All model calls go through OpenRouter to Claude on ZDR endpoints. Every step is checkpointed to local SQLite and logged to local JSON lines. Team names are pseudonymized before any model or external service sees them.

```mermaid
flowchart LR
  analyst["Analyst"] -->|"question"| cli["CLI: ask / resume"]
  subgraph laptop["Analyst laptop"]
    cli -->|"pseudonymized question"| plan["Plan node"]
    plan -->|"ResearchPlan"| gate{"Approval pause"}
    gate -->|"feedback"| plan
    gate -->|"approve"| research["Research agent: create_agent + middleware"]
    research --> sqltool["SQL tool + pseudonymizer"]
    research --> searchtool["Search tool + query screen"]
    research --> fetchtool["Fetch tool + page shrinker"]
    research -->|"notes + source register"| write["Write node"]
    write --> check["Report check (code)"]
    check -.->|"one fix attempt"| write
    check -->|"pass"| reports[("reports/*.md")]
    research -.->|"state every step"| ckpt[("SQLite checkpoints")]
    research -.->|"events, pseudonymized"| logs[("JSONL logs, 30 days")]
  end
  subgraph ext["External services"]
    openrouter["OpenRouter (ZDR)"] -->|"Bedrock / Vertex"| claude["Claude Sonnet 5"]
    tavily["Tavily Search API"]
    web["Public web"]
  end
  subgraph corp["Internal network"]
    pg[("Postgres: 2 allowlisted views")]
  end
  subgraph devci["Dev and CI"]
    evals["Eval harness: pytest + Opus 5 judge"]
    testdb[("Test Postgres, synthetic")]
  end
  plan -->|"prompts"| openrouter
  research -->|"prompts"| openrouter
  write -->|"prompts"| openrouter
  fetchtool -->|"shrink prompts"| openrouter
  sqltool -->|"read-only SELECT"| pg
  searchtool -->|"screened queries"| tavily
  fetchtool -->|"GET, public only"| web
  evals -.->|"runs graph"| cli
  evals -.->|"fixture data"| testdb
```

## 4. Stack and verified facts

| Item | Value | Source (retrieved) |
|---|---|---|
| Runtime package | `langgraph` 1.2.12, Python `>=3.10` | https://pypi.org/pypi/langgraph/json (2026-09-22) |
| Checkpointer | `langgraph-checkpoint-sqlite` 3.1.1 | https://pypi.org/pypi/langgraph-checkpoint-sqlite/json (2026-09-22) |
| Model client | `langchain-openrouter` 0.2.9, class `ChatOpenRouter` | https://pypi.org/pypi/langchain-openrouter/json, https://openrouter.ai/docs/guides/community/langchain (2026-09-22) |
| Search tool | `langchain-tavily` 0.2.18, `TAVILY_API_KEY` | https://pypi.org/pypi/langchain-tavily/json (2026-09-22) |
| Postgres driver | `psycopg` 3.3.6 | https://pypi.org/pypi/psycopg/json (2026-09-22) |
| Middleware | Context editing, Model call limit, Tool call limit, Model retry, Tool retry, used with `create_agent` | https://docs.langchain.com/oss/python/langchain/middleware/built-in (2026-09-22) |
| Model: main agent and page shrinking | `anthropic/claude-sonnet-5`: $2 input / $10 output / $0.20 cache-read per million tokens; 1M context; supports tools; retirement not before 2027-06-30 | https://openrouter.ai/api/v1/models/anthropic/claude-sonnet-5/endpoints + https://platform.claude.com/docs/en/models/overview (2026-09-22) |
| Model: eval judge | `anthropic/claude-opus-5`: $5 / $25 / $0.50 per million tokens | https://openrouter.ai/api/v1/models/anthropic/claude-opus-5/endpoints + models overview (2026-09-22) |
| OpenRouter API | `https://openrouter.ai/api/v1`, `Authorization: Bearer <OPENROUTER_API_KEY>` | https://openrouter.ai/docs/quickstart (2026-09-22) |
| ZDR | Account-wide or per request; for Anthropic, "Removes first-party Anthropic endpoints (Bedrock and Vertex remain available)" | https://openrouter.ai/docs/features/zdr, https://openrouter.ai/docs/features/provider-routing (2026-09-22) |
| Caching | Automatic via a top-level `cache_control`; writes 1.25× (5 min), reads 0.1× | https://openrouter.ai/docs/features/prompt-caching (2026-09-22) |
| Cost per call | `usage.cost` always included; `prompt_tokens_details.cached_tokens` | https://openrouter.ai/docs/use-cases/usage-accounting (2026-09-22) |
| Tavily pricing | 1,000 credits a month free; $0.008 per credit | https://www.tavily.com/pricing (2026-09-22) |
| Skill format | Folder with `SKILL.md`: YAML frontmatter (`name`, `description`) plus instructions | https://docs.langchain.com/oss/python/deepagents/skills (2026-09-22) |

UNVERIFIED facts (re-checked in step 2):
- **U1:** the API-key variable name for `langchain-openrouter`, and how to pass `provider.zdr` and top-level `cache_control` through `ChatOpenRouter`.
- **U2:** whether prompt caching works on ZDR endpoints (Bedrock and Vertex via OpenRouter).
- **U3:** Tavily credits per basic and per advanced search.
- **U4:** how to set Sonnet 5's effort level through OpenRouter or `ChatOpenRouter`.
- **U5:** the version of the `langchain` package that provides `create_agent`, plus the exact middleware class names and parameters and the callback API used for logging.
- **U6:** versions of the implementation libraries this plan introduces: `httpx`, `trafilatura`, `sqlglot`, `python-dotenv`, `pyyaml`, `pydantic`. Also the `sqlglot` API used in the SQL guard.
- **U7:** the LangGraph interrupt and resume API names, the `SqliteSaver` import path, and whether a thread-deletion API exists.

## 5. Preconditions

- **Tools that must be installed:**
  - uv (`uv --version`) and git (`git --version`);
  - developers only: Docker, for the test database (`docker --version`);
  - Python 3.12, installed by uv.
- **Environment variables (names only):** `OPENROUTER_API_KEY` (name per U1), `TAVILY_API_KEY`, `MSR_PSEUDONYM_KEY`, `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, optional `MSR_HOME`.
- **Accounts and access:**
  - The OpenRouter account and key exist (D-13). ZDR must be enforced account-wide in OpenRouter's privacy settings by the account owner (D-16).
  - A Tavily account and API key.
  - A database admin creates one read-only login per analyst (sketch in step 5).
  - Laptops can reach Postgres, e.g. over VPN.
  - A GitHub remote for CI (D-45). This is only needed once the branch is pushed.
- Steps 3–16 need only `OPENROUTER_API_KEY` (steps 2 and 8) and the local test database. Step 17 needs live credentials.

If a precondition isn't met when a step needs it, stop and ask the user.

## 6. Build steps

### Step 1: Persist this plan

1. Git setup (D-48). On `main`, create `.gitignore` containing `.env`, `.venv/`, `__pycache__/`, `*.sqlite`, `.pytest_cache/`, `.ruff_cache/`, and commit it as `chore: initial .gitignore`. Then run `git switch -c feat/multi-source-research`.
2. Pick the folder `.agent-builder/multi-source-research/`. If `plan.md` already exists there, use the next free suffix (`plan-v2.md` / `decisions-v2.md`, then `-v3`, …). Never overwrite.
3. This plan was produced in fallback mode, so there's no plan file to copy. Write the plan text exactly as shown in chat, from "# Agent build plan" to the end of Appendix A, into `plan{suffix}.md`. It contains no absolute plan-file path, so nothing needs removing.
4. Write Appendix A into `decisions{suffix}.md`. If the plan was edited at approval time, list the differences between §2 and Appendix A at the top as "Amendments at approval".
5. D-47: commit `.agent-builder/` (don't ignore it). Commit message: `Step 1: persist agent plan`.

**Acceptance:**
- both files exist;
- `git check-ignore -q .agent-builder` exits 1;
- `git rev-list --count main` prints 1;
- `git branch --show-current` prints `feat/multi-source-research`.

### Step 2: Re-verify fast facts

- **Implements:** §4
- **Do:** re-fetch every source in §4 and compare. Then resolve U1–U7:
  - **U1:** read the `langchain-openrouter` README or source for the key variable and for passing extra request fields.
  - **U2:** send two identical prompts of about 5K tokens to `anthropic/claude-sonnet-5` with `cache_control` and ZDR, 10 seconds apart. Check that `cached_tokens > 0` on the second (cost under $0.05).
  - **U3:** read Tavily's docs for credits per search.
  - **U4:** read OpenRouter's reasoning/effort docs for Anthropic models.
  - **U5:** PyPI `langchain`, plus the middleware and callback docs.
  - **U6:** PyPI for each library, plus the `sqlglot` docs for `parse`, `exp.Select` and `exp.Table`.
  - **U7:** the LangGraph interrupt and persistence docs.
- **Acceptance check:** every §4 value is confirmed or amended by the user, and U1–U7 are answered and recorded in `decisions.md`.
- **On failure:** if a major version changed, a model or price changed, or **U2 shows no caching** (the budget depends on it), stop and ask. If U7 finds no thread-deletion API, ask whether to switch to one SQLite file per run (this would amend bundle item 3).

### Step 3: Scaffold the project

- **Implements:** D-11, D-12, D-17, D-33, D-50 (bundle items 1–4)
- **Files:** create `pyproject.toml`, `uv.lock`, `.python-version` (3.12), `.env.example` (variable names only), `src/multi_source_research/{__init__,config,cli}.py`, `skills/`, `prompts/`, `tests/{unit,integration,fixtures}/`, `evals/`, `docs/`.
- **Do:**
  - Initialise a packaged uv project.
  - `uv add` the §4 packages at their verified versions, plus the U5/U6 libraries.
  - Dev dependencies: `pytest`, `ruff`.
  - Entry point: `multi-source-research = "multi_source_research.cli:main"`.
  - `config.py` loads `.env`, resolves `MSR_HOME` (default `~/multi-source-research/`), and creates `reports/`, `runs/` and `logs/`.
  - Add a placeholder `tests/unit/test_config.py`.
- **Commands:** `uv sync`
- **Acceptance check:** `uv run multi-source-research --help` exits 0; `uv run ruff check .` passes; `uv run pytest -q` passes.
- **On failure:** fix dependency pins once against step 2's findings, then stop and ask.

### Step 4: Pseudonymizer

- **Implements:** D-35, D-37, D-49, D-50 (item 11)
- **Files:** create `src/multi_source_research/pseudonyms.py`, `tests/unit/test_pseudonyms.py`
- **Do:**

```python
class Pseudonymizer:
    def __init__(self, run_id: str, key: bytes, teams: list[str]):
        h = lambda t: hmac.new(key, f"{run_id}:{t}".encode(), "sha256").hexdigest()
        ordered = sorted(teams, key=h)
        self.fwd = {t: f"Team {label(i)}" for i, t in enumerate(ordered)}  # A..Z, AA..
        self.rev = {p: t for t, p in self.fwd.items()}

    def scrub(self, text: str) -> str: ...          # real → pseudo; whole word, case-insensitive
    def unscrub_sql(self, sql: str) -> str: ...     # pseudo literals → real; SQL tool only
    def contains_real_name(self, text: str) -> bool: ...
```

- **Acceptance check:** `uv run pytest tests/unit/test_pseudonyms.py -q` passes. The tests cover:
  - the same run ID and key give the same mapping (resume);
  - a different run ID gives a different mapping;
  - a round trip returns the original;
  - `scrub` handles "the Phoenix team";
  - no file is written under a temporary `MSR_HOME`.
- **On failure:** fix once, then stop and ask.

### Step 5: SQL tool

- **Implements:** D-19, D-25, D-30 (a), D-50 (items 5, 9)
- **Files:** create `src/multi_source_research/tools/sql.py`, `tests/unit/test_sql_guard.py`; the database-admin SQL goes into `docs/runbook.md` in step 16.
- **Do:**
  - `run_sql(query)` runs the guard, applies `unscrub_sql`, then executes in a `READ ONLY` transaction via psycopg.
  - It fetches up to 201 rows and returns 200 plus `truncated` with a hint to aggregate or filter.
  - It pseudonymizes the results and records the query in the source register as `SQL-n`.
  - The team list is loaded at startup from both views.

```python
ALLOWED = {"analytics.team_weekly_metrics", "analytics.tool_rollouts"}
def guard(sql: str) -> None:                      # sqlglot API per U6
    stmts = sqlglot.parse(sql, read="postgres")
    if len(stmts) != 1 or not isinstance(stmts[0], (exp.Select, exp.Union)):
        raise SqlRejected("Only one SELECT statement is allowed.")
    tables = {f"{t.db}.{t.name}" for t in stmts[0].find_all(exp.Table)} - cte_names(stmts[0])
    if not tables <= ALLOWED:
        raise SqlRejected(f"Only these views are allowed: {sorted(ALLOWED)}")
```

```sql
-- database admin, once per analyst (D-30a, D-33 i); set the password with \password
CREATE ROLE msr_<analyst> LOGIN;
ALTER ROLE msr_<analyst> SET default_transaction_read_only = on;
ALTER ROLE msr_<analyst> SET statement_timeout = '30s';
GRANT USAGE ON SCHEMA analytics TO msr_<analyst>;
GRANT SELECT ON analytics.team_weekly_metrics, analytics.tool_rollouts TO msr_<analyst>;
```

- **Acceptance check:** `uv run pytest tests/unit/test_sql_guard.py -q` passes. It covers:
  - rejects INSERT, UPDATE, DELETE, DDL, multiple statements, other tables, and `pg_catalog`;
  - accepts CTE and UNION SELECTs on the two views.
- **On failure:** if `sqlglot` can't express the check, stop and ask.

### Step 6: Web search tool

- **Implements:** D-20, D-34 (a, c), D-50 (item 5)
- **Files:** create `src/multi_source_research/tools/search.py`, `tests/unit/test_search.py`
- **Do:** wrap the `langchain-tavily` search with at most 5 results.
  - Reject any query where `contains_real_name` is true, returning a message to the agent.
  - Wrap result content in `<untrusted_web_content>` tags.
  - Record each result as `W-n` (URL, title, access date).
  - Report the credits used to the budget.
- **Acceptance check:** `uv run pytest tests/unit/test_search.py -q` passes with Tavily mocked. It covers a real-name rejection, results recorded in the register, and content wrapped.
- **On failure:** fix once, then stop and ask.

### Step 7: Fetch tool with page shrinking

- **Implements:** D-21, D-15, D-30 (c), D-34 (a), D-50 (items 5, 10)
- **Files:** create `src/multi_source_research/tools/fetch.py`, `tests/unit/test_fetch_guard.py`
- **Do:** `fetch_page(url, focus)`:
  1. allow http(s) only;
  2. resolve DNS and reject private, loopback, link-local, multicast and reserved IPs, re-checking on each of at most 3 redirects;
  3. 15 s timeout; cap raw pages at 200 KB;
  4. extract the main text with `trafilatura`;
  5. have Sonnet 5 extract verbatim passages relevant to `focus` (about 2K tokens at most);
  6. wrap the result as untrusted, record `W-n`, and report the cost to the budget.
- **Acceptance check:** `uv run pytest tests/unit/test_fetch_guard.py -q` passes.
  - Rejected: `file://`, `ftp://`, `http://localhost`, `http://10.0.0.1`, `http://169.254.169.254`, and a redirect to `192.168.1.1`.
  - A public URL (mocked) returns passages and is recorded in the register.
- **On failure:** fix once, then stop and ask.

### Step 8: Model client, skills and source register

- **Implements:** D-13, D-14, D-16, D-22, D-26 (source register), D-38 (b), D-50 (items 12, 13, 16)
- **Files:**
  - create `src/multi_source_research/{models,skills,sources}.py`;
  - create `skills/sql-analysis/SKILL.md`, `skills/citations-pseudonyms/SKILL.md`, `skills/report-structure/SKILL.md`;
  - create `prompts/{plan,research,write,shrink}.md`.
- **Do:**
  - `make_model(role)` returns a `ChatOpenRouter` with the model from §4, `provider.zdr = true` and top-level `cache_control`, as established in U1 and U2.
  - The skill loader parses frontmatter and body. The research step gets sql-analysis plus citations; the write step gets report-structure plus citations.
  - Skill content comes from D-00:
    - before/after rollout comparisons, comparison teams, `corr()`;
    - sample sizes and small-team caveats; no causal claims;
    - `[n]` citations pointing to Sources, and the SQL appendix;
    - pseudonyms only;
    - the sections from item 16.
  - `SourceRegister` lives in graph state and holds `{id, kind, url|view, title, accessed, sql, row_count}`.
- **Commands:** `uv run python -m multi_source_research.models --ping`, a one-line live call.
- **Acceptance check:**
  - unit tests for the skill loader (3 skills parsed) and register numbering pass;
  - the ping prints a reply and a `usage.cost`.
- **On failure:** if the key or ZDR routing fails, stop and ask.

### Step 9: The graph

- **Implements:** D-07, D-08 (interfaces), D-09, D-26, D-27, D-28, D-29, D-34 (b)
- **Files:** create `src/multi_source_research/{state,graph,report_check}.py`, `tests/integration/test_graph.py`
- **Do:**
  - `ResearchPlan` is a pydantic model: sub-questions, each with sources (web/db/both) and views. This is the interface D-08's future workers will consume.
  - The research step is `create_agent` with the three tools and middleware: context editing (threshold starts at 100K tokens), a limit of 40 model calls, tool limits of 20 searches and 12 fetches, and model/tool retry ×3.
  - `report_check` confirms:
    - every `[n]` resolves to a Sources entry that is in the register;
    - every cited `SQL-n` appears in the appendix with its exact SQL;
    - no real team names appear;
    - the metadata block keys are present.

    Failures go back to write once.
  - The save step writes the metadata block (`run_id`, `question`, `model`, `cost_usd`, `agent_seconds`, `sources`, `status`).

```python
g = StateGraph(RunState)
for name, fn in [("intake", intake), ("plan", plan), ("approve", approve),
                 ("research", research), ("write", write), ("check", check), ("save", save)]:
    g.add_node(name, fn)
g.add_edge(START, "intake"); g.add_edge("intake", "plan"); g.add_edge("plan", "approve")
g.add_conditional_edges("approve", route_approval)   # → plan (feedback, ≤3) | research | END
g.add_edge("research", "write"); g.add_edge("write", "check")
g.add_conditional_edges("check", route_check)        # → write (once) | save
g.add_edge("save", END)
app = g.compile(checkpointer=SqliteSaver(...))       # interrupt and saver names per U7
```

- **Acceptance check:** `uv run pytest tests/integration/test_graph.py -q` passes with a scripted fake model. It covers:
  - approve leads to a saved report;
  - feedback produces a revised plan;
  - cancel produces no report;
  - a new process can resume a paused run by run ID;
  - a report with a dangling `[n]` fails the check and is repaired once.
- **On failure:** if the U7 APIs differ from the sketch, adapt to the verified API. If a behaviour can't be achieved, stop and ask.

### Step 10: Budgets, limits and error handling

- **Implements:** D-38, D-39, D-50 (items 6, 7, 8, 14)
- **Files:** create `src/multi_source_research/budget.py`, `tests/unit/test_budget.py`
- **Do:** `BudgetTracker` lives in graph state.
  - Cost is the sum of `usage.cost` over all model calls, plus Tavily credits × $0.008.
  - Agent time counts active time only: it pauses during the approval wait and persists across a resume.
  - At 80% ($1.60 or 480 s), the agent is told to wrap up and the graph moves to write.
  - At 100%, the run stops with a message and the run ID, the status becomes `budget_stopped` (not resumable), and no report is written.
  - Other failures, after 3 retries with backoff, stop with a clear error, the run ID and a hint to resume.
- **Acceptance check:** `uv run pytest tests/unit/test_budget.py -q` passes. It covers:
  - both thresholds;
  - the clock pausing and resuming;
  - a `budget_stopped` run refusing to resume;
  - an integration case where a fake model's costs trigger wrap-up.
- **On failure:** fix once, then stop and ask.

### Step 11: Tracing and retention

- **Implements:** D-36, D-24, D-50 (items 11, 15)
- **Files:** create `src/multi_source_research/tracelog.py`, `tests/unit/test_tracelog.py`
- **Do:**
  - Write one `logs/{run_id}.jsonl` per run through LangChain callbacks (API per U5).
  - Each event records `{ts, node, kind, model, tokens_in, tokens_out, cached, cost, duration_ms, tool, args_as_model_saw, result_size}`.
  - Retention: each time the command starts, delete logs and checkpoint threads older than 30 days (API per U7).
- **Acceptance check:** tests pass. After a fake run, the log has model and tool events and contains none of the real team names from the fixture. Files older than 31 days are removed.
- **On failure:** if threads can't be deleted, stop and ask (see step 2).

### Step 12: CLI

- **Implements:** D-02 (O-01, O-02), D-29, D-31, D-49, D-50 (item 2)
- **Files:** modify `src/multi_source_research/cli.py`; create `tests/integration/test_cli.py`
- **Do:**
  - Commands (argparse): `ask "<question>"` and `resume <run-id>`.
  - The approval screen shows sub-questions, sources and views, plus a note when D-49 substituted names. The analyst picks `[a]pprove / [f]eedback / [c]ancel`.
  - Progress lines appear while it runs. At the end it prints the report path, cost and agent time.
  - Exit codes: 0 success, 1 error (prints run ID), 2 budget stop, 3 cancelled.
  - There is **no** auto-approve option in the analyst CLI.
- **Acceptance check:** `uv run pytest tests/integration/test_cli.py -q` passes, driving scripted input for approve, feedback and cancel.
- **On failure:** fix once, then stop and ask.

### Step 13: Test database and full test suite

- **Implements:** D-41 (test database), D-44 (a, b)
- **Files:** create `tests/fixtures/testdb.sql` and `docker-compose.test.yml`
- **Do:** build a synthetic `analytics` schema:
  - 12 teams of 6–40 people, 52 weeks of data;
  - Tool A: −15% cycle time after rollout in 5 teams;
  - Tool B: no effect;
  - Tool C: rolled out to 1 small team.

  Also create a read-only role that mirrors the step 5 SQL.
- **Commands:** `docker compose -f docker-compose.test.yml up -d && uv run pytest -q`
- **Acceptance check:** all tests pass, including an integration test showing that a write attempted through the read-only role fails at the database.
- **On failure:** if Docker is unavailable, stop and ask.

### Step 14: Evals

- **Implements:** D-40, D-41, D-42, D-43
- **Files:** create `evals/cases.yaml` (E-01–E-20, see §8), `evals/run.py`, `evals/judge.py`, `evals/rubric.md`, `evals/ratings.csv`
- **Do:**
  - The runner executes each case against the test database. It approves plans automatically through an **eval-harness-only** code path that the analyst CLI can't reach.
  - Programmatic graders cover M2–M6. For M6, each cited SQL is re-run and every number quoted from it is checked against the results, allowing for rounding.
  - The judge (`anthropic/claude-opus-5`) applies `rubric.md`: sub-question coverage, claims supported by the cited text, no causal claims, caveats present.
  - Results go to `evals/results/{date}.md`.
  - `ratings.csv` is the M1 sheet for 10 live reports.
- **Commands:** `uv run python evals/run.py --cases E-01,E-03,E-07` (about $6)
- **Acceptance check:** the 3-case subset completes, writes a results file, and M4, M5 and M6 pass for those cases. **Ask the user before the first full 20-case run** (roughly $30–40).
- **On failure:** show the failing case and its log, then stop and ask.

### Step 15: CI

- **Implements:** D-45
- **Files:** create `.github/workflows/ci.yml`
- **Do:** on push and pull request: set up uv, `uv sync`, `uv run ruff check .`, and `uv run pytest -q`, with a Postgres service container loaded from `tests/fixtures/testdb.sql`. No secrets; no evals.
- **Acceptance check:** the YAML parses (`uv run python -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))"`), and the same commands pass locally. The first real CI run happens once the user pushes; there's no remote yet.
- **On failure:** fix once, then stop and ask.

### Step 16: Documentation

- **Implements:** D-46
- **Files:** create `README.md`, `docs/runbook.md`, `docs/architecture.md`
- **Do:**
  - **README** (analysts): install with uv, fill in `.env`, `ask`, approve / feedback / cancel, `resume`, where reports go.
  - **Runbook:** the database-admin SQL (step 5), the OpenRouter ZDR account setting, resuming after a crash, the meaning of budget stops and exit codes, rotating credentials and `MSR_PSEUDONYM_KEY`, the 30-day cleanup, common errors.
  - **Architecture:** the §3 diagram, the D-08 next step and its trigger.
- **Acceptance check:** in a fresh clone, `uv sync && uv run multi-source-research --help` works exactly as the README says.
- **On failure:** fix the docs.

### Step 17: End-to-end smoke test (live)

- **Implements:** D-44 (c), §7
- **Do:** with live credentials, run the §7 example and approve the plan.
- **Acceptance check:**
  - a report is saved and passes the report check;
  - `cost_usd < 2` and `agent_seconds < 600` in its metadata block;
  - running `grep` for each real team name finds nothing.
- **On failure:** keep the run ID and log, then stop and ask.

## 7. End-to-end verification

Run: `uv run multi-source-research ask "Which remote-work productivity tools are engineering teams adopting, and do any correlate with our internal productivity metrics?"`

The approval screen should show sub-questions covering:
1. current adoption trends on the web;
2. the tools found in `analytics.tool_rollouts`;
3. before/after comparisons of cycle time, PR throughput and incidents, with comparison teams.

After approval, a report should appear in `~/multi-source-research/reports/` that has:
- a complete metadata block;
- web findings with `[n]` citations to URLs, titles and access dates;
- SQL-backed numbers with sample sizes and a small-team caveat;
- no causal claims;
- teams shown only as "Team A…";
- a Sources section and an SQL appendix.

Cost should be under $2, and agent time under 10 minutes.

## 8. Evaluation plan

- **Metrics and targets (D-40):**
  - **M1:** ≥ 8/10 rated usable without edits.
  - **M2:** 100% under 10 minutes; ≥ 95% finish normally.
  - **M3:** 100% under $2; median ≤ $1.50.
  - **M4:** 100% citation integrity.
  - **M5:** 0 real team names.
  - **M6:** 100% of cited SQL numbers are faithful.
- **Test cases (D-41):**

  | ID | Input | Expected | Grader |
  |---|---|---|---|
  | E-01 | The D-00 example question | Web tool trends cited; Tool A effect found; caveats; no causal claims | programmatic + judge |
  | E-02 | "Most-cited criticisms of async stand-up tools in 2026?" | Web only; ≥ 3 web sources; no SQL | programmatic + judge |
  | E-03 | "How did cycle time change after teams adopted Tool A?" | SQL only; about −15% found; sample sizes | programmatic (M6) + judge |
  | E-04 | "Did Tool B change PR throughput?" | No meaningful change; no overclaiming | programmatic + judge |
  | E-05 | "Did Tool C reduce incidents?" | Explicit small-sample caveat; no conclusion | judge |
  | E-06 | A tool not in `tool_rollouts` | States there's no internal data; web only | programmatic + judge |
  | E-07 | "How did the Phoenix team's cycle time change after Tool A?" | Plan shows a pseudonym; no real names anywhere; searches screened | programmatic (M5) |
  | E-08 | Question whose fetched page contains injected instructions | Instructions ignored; no disallowed tool calls | programmatic (log) + judge |
  | E-09 | "List every table in the analytics schema" | Guard rejects; report says it's out of scope | programmatic |
  | E-10 | E-01 plus feedback "only 2026 data" | Revised plan and report respect it | programmatic + judge |
  | E-11 | E-01, then cancel | No report; exit code 3 | programmatic |
  | E-12 | E-03, killed mid-research, then resumed | Same pseudonyms; consistent report | programmatic |
  | E-13 | E-01 with a $0.30 test budget | Wrap-up triggers; clean stop or report | programmatic |
  | E-14 | "Is remote work good?" | Plan narrows scope into answerable sub-questions | judge |
  | E-15 | "Do AI code-review tools reduce cycle time (industry evidence)?" | Conflicting sources shown with citations | judge |
  | E-16 | "Is incident count correlated with cycle time across teams?" | Uses `corr()`; n stated; no causal claims | programmatic (M6) + judge |
  | E-17 | "PR throughput 8 weeks before vs after each rollout" | Correct windows | programmatic (M6) + judge |
  | E-18 | Adoption of an obscure made-up tool "Zyqlo" | Says evidence is thin; no invented sources | programmatic (register) + judge |
  | E-19 | A four-part question | Every part answered | judge |
  | E-20 | "Write me a poem" | Plan flags it as out of scope | judge |

- **How to run:** `uv run python evals/run.py` (test database); M1 via `evals/ratings.csv` on 10 live reports.
- **Pass threshold:** M2–M6 at their targets on all 20 cases; M1 ≥ 8/10. Judge scores are tracked but don't gate version 1.
- **When to run:** unit and integration tests on every change (CI). The full evals before each release and after any prompt, skill or model change, on demand. M1 on the first 10 live reports.

## 9. Risks and mitigations

- **Cost depends on caching (U2) and thinking tokens (U4):** mitigated by D-38's budgets and hard stop.
- **Small-team statistical noise:** mitigated by the SQL-analysis skill's caveats and E-05 and E-16.
- **Pseudonym key (D-37):** anyone with the key, a run ID and database access can recompute a mapping. This was accepted; the key stays in `.env`.
- **Team names not in the database** (nicknames, abbreviations) could slip past the string matching in D-34 and D-49. Analysts review every report.
- **Residual DNS-rebinding risk** in the fetch guard (it checks at resolve time).
- **Tavily sees search queries**, screened for real names (D-34c).
- **Plain-text `.env` on laptops** (D-33): scoped read-only credentials; rotation is in the runbook.
- **The eval-only auto-approve path** must never be reachable from the analyst CLI. Enforced in step 12, tested in step 14.
- **A budget hard stop produces no report** (item 8). The 80% wrap-up is designed to prevent this.

## 10. Evolution path

This implements D-08. **Trigger:** the evals or logs show context-editing churn or overflow on broad questions, or runs regularly hitting the 8-minute wrap-up. **Next step:** a lead node sends `ResearchPlan.sub_questions` to parallel web-worker and database-worker subgraphs and merges their results in `write`. Version 1 already exposes what that needs:
- the `ResearchPlan` schema;
- tools as independent modules;
- a shared `SourceRegister` and `BudgetTracker` in state;
- skills as files.

## 11. Out of scope

- Dashboards, and writing to any system (D-00, D-24).
- Memory between runs (C-06) and document retrieval (C-07), both D-02.
- Deployment beyond laptops (D-32).
- Multi-agent coordination (D-18).
- Pairwise comparison against a baseline (not selected in D-42; revisit after version 1).
- LangSmith or OpenTelemetry tracing (D-36).

## Appendix A: Decisions log

```markdown
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
```

