# Runtimes

What each supported runtime is good at, how the patterns map onto it, and what
to look up live before recommending it. This file describes lasting concepts
only. Package names, versions, class and function names, and model IDs must come
from live lookup (`live-lookup.md`) at planning time.

Provider scope for this version of the skill:

- Claude-ecosystem runtimes use Claude models only, via the Anthropic API,
  Amazon Bedrock, Google Vertex AI or Microsoft Foundry.
- LangGraph plans use OpenRouter as the model gateway. The specific model on
  OpenRouter is a per-build question. Other LangGraph providers are on the
  roadmap and are out of scope for now; say so if the user asks.

## Claude Agent SDK (Python or TypeScript)

- **What it is.** The agent loop that powers Claude Code, packaged as a library.
  It comes with built-in tools (files, shell, search, web), custom tools, MCP
  integration, subagents, hooks, permission controls and session handling.
- **Best for.** Standalone agents in your own application or service that need a
  capable, general-purpose loop without writing one. Coding, research and
  operations agents in particular.
- **Weaknesses.** It's opinionated about the loop. Hosting, multi-tenancy and
  scaling are yours to build, and it ties you to Claude models.
- **Pattern mapping.** Single agent: the default loop. Hierarchical: subagents
  under a main agent. Parallel: concurrent subagents or concurrent queries.
  Sequential: chained queries, or subagents in a fixed order. Evaluator: a
  reviewer subagent or a second pass.
- **Human in the loop.** Permission callbacks and hooks can gate tool calls.
  Approval UI is yours to build.
- **Observability.** Hooks and message streams feed your tracing; check live
  which telemetry integrations exist.
- **Deployment shape.** A process or container you run: CLI, service, worker or
  scheduled job.
- **Look up live.** Current package names and versions, the query/client API,
  how custom tools and in-process MCP servers are declared, subagent
  configuration, permission modes, supported models.

## Claude API with a custom tool-use loop

- **What it is.** Direct calls to the Messages API with tool definitions. Your
  code runs the loop: send, execute the requested tools, return results, repeat.
- **Best for.** Maximum control and minimal dependencies, simple or narrow
  agents, strict latency or cost budgets, embedding in existing systems, and
  deterministic workflows where the loop is really a pipeline.
- **Weaknesses.** You build everything: retries, context management, tool
  execution, persistence, safety.
- **Pattern mapping.** Every pattern is hand-built, which suits sequential and
  parallel workflows well: calls wired by your code.
- **Features to consider.** Prompt caching, structured outputs, server-side
  tools, context-management features, batch processing, extended thinking. Check
  availability live.
- **Look up live.** SDK packages and versions, the tool-use request and response
  shape, current model IDs and pricing, and context-management features.

## Claude Code-native

- **What it is.** The agent lives inside Claude Code. It's assembled from
  subagents (`.claude/agents/`), skills, slash commands, hooks, MCP servers
  (`.mcp.json`), plugins, and headless runs (`claude -p`) for automation and CI.
- **Best for.** Developer-facing agents that work on a repository: review,
  migration, triage, docs, release chores. Also team workflows shared as
  plugins, and automation where a Claude Code install is acceptable.
- **Weaknesses.** Requires Claude Code to be installed and authenticated on
  every machine or runner. It isn't a multi-tenant server runtime. The
  interaction model is Claude Code's.
- **Pattern mapping.** Single agent: a skill or the main session. Hierarchical
  or parallel: subagents (and agent teams where available). Sequential: a skill
  that runs steps or subagents in order, or a headless pipeline. Evaluator: a
  reviewer subagent.
- **Human in the loop.** Permission modes, plan mode, hooks and questions to the
  user.
- **Operational caveats.** Writes to `.claude/` and `.mcp.json` are protected
  paths, so executing the plan triggers approval prompts there. Headless runs
  cannot ask questions interactively.
- **Look up live.** Current subagent and skill frontmatter fields, hook events
  and I/O, plugin manifest fields, headless flags, permission-mode behavior.

## LangGraph (Python or JavaScript) with OpenRouter

- **What it is.** A framework for building agents as graphs: nodes (steps or
  agents) connected by edges over shared state. It has built-in persistence
  (checkpointing), human-in-the-loop interrupts and streaming.
- **Best for.** Explicit, inspectable control flow. Long-running or resumable
  workflows. Complex branching, retries and human checkpoints. Teams already
  using the LangChain ecosystem.
- **Weaknesses.** More framework concepts to learn. Graph design effort up
  front. Version churn, so always check current APIs.
- **Pattern mapping.** Sequential: linear edges. Routing: conditional edges.
  Parallel: fan-out to several nodes with a join. Hierarchical: a supervisor node
  or subgraphs. Evaluator: a loop edge from critic back to generator with an
  iteration cap. Collaborative: shared state as a blackboard.
- **Model access.** Via OpenRouter's API, which is compatible with the OpenAI
  chat format. Look up live how the chosen LangGraph version connects to it, and
  which models, prices and tool-calling support OpenRouter currently lists.
- **Observability.** Check live for tracing integrations (LangSmith and
  OpenTelemetry-style options) and OpenRouter's usage reporting.
- **Look up live.** Package names and versions (Python and JS differ), graph and
  checkpointer APIs, the interrupt API, prebuilt agent helpers, the OpenRouter
  base URL, auth header and model slugs.

## Pattern × runtime fit

| Pattern | Agent SDK | API loop | Claude Code-native | LangGraph |
|---|---|---|---|---|
| Single agent | Strong | Good | Strong | Good |
| Sequential | Good | Strong | Good | Strong |
| Parallel | Good | Strong | Good (subagents) | Strong |
| Evaluator-optimizer | Good | Good | Good | Strong |
| Hierarchical | Strong (subagents) | Manual | Strong (subagents) | Strong (supervisor / subgraphs) |
| Collaborative | Manual | Manual | Limited | Good (shared state) |

"Strong" means native support; "Manual" means you build the coordination
yourself. This is guidance for the recommendation's *why*. It is never a reason
to skip the question.

## Choosing: signals

- The agent must run as a product or service for many users → Agent SDK, API
  loop or LangGraph, not Claude Code-native.
- It works on a code repository, used by developers → Claude Code-native or the
  Agent SDK.
- It needs explicit, resumable, inspectable control flow with human checkpoints
  → LangGraph (or the Agent SDK with hooks).
- Minimal dependencies, a tight budget or a strict latency target → API loop.
- The team already runs one of these → prefer it, and ask.
