# Architecture patterns

Lasting guidance on how agents are structured. Use it to explain options and
trade-offs to the user. It never replaces the user's decision. Version-specific
facts (model names, SDK calls) are not here; look those up live (see
`live-lookup.md`).

## Design principles

1. **Start with the simplest thing that can work.** A single, well-scoped agent
   is cheaper to run, easier to debug and easier to reason about than a system of
   agents. Add structure only when a measured limitation demands it.
2. **Match the model to the job.** Every role balances capability, speed and
   cost. Hard, open-ended reasoning justifies a top-tier model. High-volume,
   routine steps (classification, extraction, simple support replies) usually run
   as well and far cheaper on a smaller, faster model. Costs compound with volume,
   so decide per role, not once for the whole system.
3. **Design for modularity.** Keep prompts in configuration rather than code.
   Make tools discrete, reusable modules. Compose an agent from the prompts, tools
   and resources its task needs. Then new capabilities can be added without
   re-architecting.
4. **Extend with skills before adding agents.** Packaged domain knowledge and
   workflows (Agent Skills) often let a single agent handle work that would
   otherwise need several specialists. Skills can call other skills, which keeps
   capability composable.
5. **Build observability in from day one.** Agents are non-deterministic and
   their reasoning is opaque. Trace prompt chains, tool calls, decisions,
   retrieved context and token use, so a failure can be explained, not just
   observed.

## Single agent

One model with a system prompt, tools, optional skills and optional memory,
running a loop: understand the task, plan, act with tools, observe results,
adjust. It repeats until the goal is met or a stop condition (such as "ask a
human") triggers.

- **Use when** the path to the answer isn't known in advance. The number of
  steps and the obstacles emerge along the way.
- **Avoid when** you need maximum accuracy on the first attempt for complex,
  multi-faceted work, or the work spans several unrelated domains. First check
  whether adding skills closes the gap.

## Multi-agent systems

Several specialized agents divide a problem, work on the parts (often in
parallel), and their results are combined. They shine on breadth-first work:
pursuing many independent directions, investigations that fan out, and tasks
whose context would overwhelm one agent. The trade-off is cost and complexity.
They consume many times more tokens than a single agent (roughly an order of
magnitude), so reserve them for high-value tasks where the gain pays for it.
Observability matters even more here, because failures hide in the interactions
between agents.

### Centralized: hierarchical or supervisor

A supervisor (orchestrator or router) analyzes the request, delegates to
specialist agents, often exposed to it as tools, and synthesizes their outputs.
Specialists can have their own sub-agents. This is a clear chain of
responsibility, similar to a well-run team.

- **Variants.** *Full orchestration*: the supervisor owns the whole user
  interaction. *Routing-focused*: the supervisor mainly picks the specialist and
  may hand the conversation over. *Hybrid*: the supervisor is involved only when
  complexity requires it.
- **Key challenge: context management.** The orchestrator's context can grow
  past what it can use well. Mitigations:
  - clear stale tool results automatically (context editing);
  - give agents memory outside the context window, such as file-based memory
    that persists across sessions;
  - make tools return bounded, paginated and filtered responses, with sensible
    defaults and a size cap on the order of tens of thousands of tokens.

### Decentralized: collaborative or peer-to-peer

Autonomous agents coordinate as peers. Coordination emerges from their
interaction rather than from a central controller.

- **Mechanisms.** *Group chat*: agents discuss in a shared thread. *Event-driven*:
  agents publish and consume structured events. *Blackboard*: a shared knowledge
  store that every agent reads and writes.
- **Key challenge: communication cost and emergent behavior.** Chatty agents
  multiply cost, and small prompt changes can shift system behavior
  unpredictably. Mitigations:
  - define a clear division of labor and give each agent an effort budget;
  - prevent tasks bouncing between agents indefinitely;
  - design an explicit conflict-resolution rule.

## Agentic workflows

A workflow fixes the structure in advance: which agent runs when, what it hands
off, and how results combine. Compared with free-running agents, workflows trade
flexibility for predictability.

### Sequential

A fixed pipeline of stages, each consuming the previous stage's output. Stage
transitions can be decided by code (a condition on state) or by a model
(content-based routing).

- **Use when** the work decomposes cleanly into ordered subtasks with clear
  dependencies. Examples: document approval chains, compliance checks, data
  transformation, draft → review → polish. It's also the choice when each stage
  must be auditable. It trades latency for accuracy, because each call does one
  focused thing.
- **Avoid when** a single agent could do it in a few steps, agents need to
  collaborate rather than hand off, or the process needs backtracking and
  iteration.

### Parallel (fan-out / fan-in)

Independent subtasks run at the same time and their results are aggregated.
Aggregation is optional. Two common shapes: *sectioning*, where each agent takes
a different aspect, and *voting*, where several agents attempt the same task and
their answers are compared.

- **Use when** subtasks are genuinely independent and speed matters, or several
  perspectives raise confidence. Examples: guardrails that screen input while
  another call answers it, multi-aspect evaluations, vote-based review for
  vulnerabilities or content policy.
- **Avoid when** agents must build on each other's work, order matters, results
  must be deterministic, agents would change shared state or external systems
  concurrently, there's no rule for resolving contradictory results, or
  aggregation logic is too complex to trust.

### Evaluator-optimizer

A generator produces output. An evaluator scores it against explicit criteria
and returns actionable feedback. The loop repeats until the criteria are met or
an iteration cap is hit.

- **Use when** evaluation criteria are clear and iteration demonstrably improves
  results. Examples: nuanced writing or translation, security-sensitive code,
  documentation checked against source.
- **Avoid when** a first attempt is already good enough, criteria are subjective
  or unmeasurable, responses must be real-time, budgets are tight, a
  deterministic check exists, or the evaluator lacks the domain knowledge to give
  useful feedback.

## Emerging patterns (experimental)

These are never the default recommendation. Present them only if the user raises
them or the requirements clearly point there, and label them experimental.

- **Dynamic agent generation.** Agents are assembled at runtime from libraries of
  prompts, tools and configuration, then discarded. Promising for resource use,
  but context management, emergent behavior and creation overhead are unsolved
  problems.
- **Network / peer-to-peer.** Many-to-many communication with no supervisory
  bottleneck. Early benchmarks show it can edge out supervisor designs, but it is
  harder to control.

## Hybrids and evolution

Production systems often combine patterns:

- **Hierarchy with parallel work.** A supervisor delegates to specialists that
  each run parallel analyses in their own domain.
- **Sequential with dynamic routing.** A classification stage routes each case to
  a simple resolver or a more complex team.
- **Single agent with escalation.** A single agent handles routine work and
  escalates edge cases to a multi-agent system.

A typical evolution path:

1. A single agent for the core task.
2. Routing that splits a few request types.
3. Specialized agents with shared context.
4. A multi-agent system coordinating several back-end domains.
5. Evaluator agents for quality assurance.

The lesson: start simple, measure, and add complexity only when it pays for
itself. A well-designed first version exposes interfaces that let more agents be
added later.

## Further reading (Anthropic, public)

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Managing context on the Claude Developer Platform](https://www.anthropic.com/news/context-management)
