# Capability questions

Asked in P5, after the foundation questions. Ask the tool questions first, then
context and memory, then the multi-agent details.

## C-01 Tool sources (multiSelect)

- **Header:** `Tools`
- **Question:** "How should the agent get its tools?"
- **Options:**
  - **Existing MCP servers.** Trade-off: fast; you depend on the server's
    quality and permissions.
  - **Custom MCP server.** Trade-off: reusable across agents; more to build.
  - **In-code function tools.** Trade-off: simplest; tied to this agent.
  - **Built-in or server-side tools** (web search, code execution, file tools).
    Trade-off: no code; less control.
- **Recommend when:** a maintained MCP server exists for a named system →
  existing MCP. A small one-off action → an in-code tool.
- **Applies when:** always.
- **Look up live:** the MCP registry for each named system; built-in tool
  availability for the runtime.
- **Ledger key:** `tools.sources`.

## C-02 Integration per system

- **Header:** the system's name (≤12 characters)
- **Question:** "How should the agent connect to `{system}`?" Ask once per
  system named in the purpose, batching up to 4 systems per round.
- **Options:** a specific existing MCP server (name and maintainer from the
  lookup) / a custom tool with the official API client / read-only export or
  file access / not needed for version 1.
- **Recommend when:** an official or well-maintained server exists → that one.
  Writes are needed → the option with the narrowest permission scope.
- **Applies when:** the purpose names external systems.
- **Look up live:** the server's existence, maintainer, auth method and required
  scopes.
- **Conflicts:** no human approval ↔ write scopes.
- **Ledger key:** `tools.integrations.{system}`.

## C-03 Tool response limits

- **Header:** `Tool output`
- **Question:** "How should tools keep responses small enough for the context?"
- **Options:**
  - **Paginate + filter + cap size** (a cap on the order of tens of thousands of
    tokens). Trade-off: more tool design work.
  - **Truncate with a notice.** Trade-off: simple; can hide data.
  - **No limits.** Trade-off: risks context overflow on large results.
- **Recommend when:** any tool can return large data → paginate, filter and cap.
- **Applies when:** a tool can return large data, or the pattern is
  multi-agent.
- **Ledger key:** `tools.limits`.

## C-04 Skills

- **Header:** `Skills`
- **Question:** "Should the agent use Agent Skills for domain knowledge or
  workflows?"
- **Options:**
  - **No skills.** Trade-off: simplest.
  - **Reuse existing skills** (name them). Trade-off: quick; check fit.
  - **Author new skills** (name the topics). Trade-off: consistent expertise;
    authoring effort.
- **Recommend when:** framework question 4 points to "single domain + skills",
  or there are repeatable procedures → author or reuse.
- **Applies when:** runtime supports skills (Agent SDK, API, Claude
  Code-native), or domain expertise matters.
- **Look up live:** how the chosen runtime loads skills.
- **Ledger key:** `skills`.

## C-05 Context management

- **Header:** `Context`
- **Question:** "How should the agent keep its context under control on long
  tasks?"
- **Options:**
  - **Clear stale tool results automatically** (context editing or compaction
    features). Trade-off: depends on runtime support.
  - **Summarize and hand off.** Trade-off: some detail is lost.
  - **Isolate work in sub-agents.** Only summaries return to the lead.
    Trade-off: more agents to run.
  - **Not needed.** Short tasks only.
- **Recommend when:** long-running work or big tool outputs → automatic clearing
  (if the runtime supports it) plus capped tools. Multi-agent → isolation.
- **Applies when:** tasks can run long, or the pattern is multi-agent.
- **Look up live:** context-management features for the chosen runtime and
  models.
- **Ledger key:** `context`.

## C-06 Memory

- **Header:** `Memory`
- **Question:** "What should the agent remember between runs?"
- **Options:**
  - **Nothing.** Each run is independent. Trade-off: simplest, most private.
  - **Session only.** Trade-off: no persistence risk.
  - **Persistent file or key-value memory.** Trade-off: learns over time; needs
    retention rules.
  - **Database or vector store.** Trade-off: scalable recall; more
    infrastructure.
- **Recommend when:** a user preference or history matters → persistent memory.
  Privacy constraints → nothing or session only.
- **Applies when:** multi-session use, or personalization is implied.
- **Conflicts:** privacy or residency constraints ↔ persistent memory.
- **Ledger key:** `memory`.

## C-07 Retrieval and knowledge

- **Header:** `Knowledge`
- **Question:** "How should the agent find information in documents or
  knowledge bases?"
- **Options:**
  - **Agentic search over files** (grep or glob style tools). Trade-off: no
    index; slower on huge corpora.
  - **Vector retrieval (RAG).** Trade-off: fast semantic recall; needs an index
    pipeline.
  - **A search API or connector.** Trade-off: depends on an external service.
  - **Not needed.**
- **Recommend when:** a modest corpus → agentic search. A large corpus that
  changes rarely → vector retrieval.
- **Applies when:** the purpose involves documents or knowledge bases.
- **Ledger key:** `retrieval`.

## C-08 Checkpointing and resumability

- **Header:** `Resume`
- **Question:** "Must a run survive crashes or pauses and resume where it left
  off?"
- **Options:**
  - **Yes: checkpoint every step.** Trade-off: storage and complexity.
  - **Only at human-approval points.** Trade-off: a partial redo on crash.
  - **No: rerun from the start.**
- **Recommend when:** long runs or human approval mid-run → checkpoints. This is
  natural in LangGraph.
- **Applies when:** runs are long, involve human approval mid-run, or the
  runtime is LangGraph.
- **Ledger key:** `checkpointing`.

## C-09 Agent roles (multi-agent only)

- **Header:** `Roles`
- **Question:** propose the concrete list of roles derived from the purpose (for
  example lead researcher, web searcher, database analyst, synthesizer) and ask:
  - **Accept roles.**
  - **Edit roles** (say which).
  - **Fewer agents** (merge; say which).
- **Applies when:** the pattern is hierarchical, collaborative or parallel with
  agents.
- **Ledger key:** `agents.roles`.

## C-10 Delegation and communication (multi-agent only)

- **Header:** `Coordination`
- **Question:** "How do agents coordinate?"
- **Options:**
  - **Supervisor calls agents as tools.** Trade-off: clear control; the
    supervisor's context grows.
  - **Hand-offs between agents.** Trade-off: lighter; harder to trace.
  - **Shared state or blackboard.** Trade-off: flexible; needs conflict rules.
  - **Events.** Trade-off: decoupled; more infrastructure.
- **Recommend when:** hierarchical → supervisor-as-tools. Collaborative → shared
  state or events.
- **Applies when:** multi-agent.
- **Ledger key:** `agents.coordination`.

## C-11 Budgets and stop conditions (multi-agent or evaluator)

- **Header:** `Limits`
- **Question:** "What limits keep runs bounded?" (multiSelect)
- **Options:** Max parallel agents / Max iterations or turns per agent / Token or
  cost budget per run / Explicit stop condition or "done" criteria. Ask for the
  numbers in a follow-up.
- **Recommend when:** always pick at least an iteration cap and a budget for
  evaluator loops and multi-agent systems.
- **Applies when:** multi-agent or evaluator-optimizer.
- **Ledger key:** `limits`.

## C-12 Output format

- **Header:** `Output`
- **Question:** "What form should the agent's output take?"
- **Options:**
  - **Structured JSON matching a schema.** Trade-off: machine-checkable; less
    prose.
  - **Markdown report.** Trade-off: readable; harder to validate.
  - **Actions only** (the side effects are the output). Trade-off: needs good
    logs.
  - **Mixed.** Name which parts.
- **Recommend when:** a downstream system consumes it → structured. A human
  reads it → markdown with an optional JSON summary.
- **Applies when:** always.
- **Look up live:** structured-output support in the chosen runtime and model.
- **Ledger key:** `output_format`.
