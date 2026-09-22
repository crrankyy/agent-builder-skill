# Foundation questions

Asked in P4, after the four framework questions and the pattern decision (see
`../decision-framework.md`). Ask them in the order listed here.

## F-01 Pattern

- **Header:** `Pattern`
- **Question:** "Which architecture pattern should the agent use?"
- **Options:** built from `../decision-framework.md`. Offer the recommendation,
  the runner-up, and a hybrid if one fits. Name any other viable patterns in the
  question text. With more than 4 candidates, ask the family first (single agent
  / workflow / multi-agent), then the variant.
- **Recommend when:** follow the four-question mapping and the tie-breakers.
  State which answers drove it.
- **Applies when:** always.
- **Conflicts:** control ↔ collaborative; budget ↔ multi-agent; backtracking ↔
  sequential; shared state ↔ parallel; real-time ↔ evaluator.
- **Ledger key:** `pattern`.

## F-02 Evolution target

- **Header:** `Evolution`
- **Question:** "Should the plan design for a later evolution beyond the first
  version?"
- **Options:**
  - **Yes: name the next step** (e.g. single agent → routing → specialists).
    Trade-off: small up-front cost for interfaces.
  - **No: build exactly this.** Trade-off: a later change may need refactoring.
  - **Hybrid now.** Combine patterns from the start (name which). Trade-off:
    more complexity on day one.
- **Recommend when:** a long-term initiative (framework question 3) → Yes. Time
  pressure → No, with a note.
- **Applies when:** always.
- **Ledger key:** `evolution`.

## F-03 Code location

- **Header:** `Location`
- **Question:** "Where should the agent's code live?"
- **Options:**
  - **This repository**, in a new folder. Trade-off: shares CI and
    dependencies.
  - **A new directory** next to this one. Trade-off: isolated, no shared
    tooling.
  - **A new git repository.** Trade-off: clean history, more setup.
- **Recommend when:** the scan shows a related codebase → this repository.
  Empty directory → a new directory or repository (ask).
- **Applies when:** always.
- **Ledger key:** `code_location`.

## F-04 Runtime family

- **Header:** `Runtime`
- **Question:** "Which runtime should the agent be built on?"
- **Options:**
  - **Claude Agent SDK.** Trade-off: fastest to a capable agent; Claude-only;
    you host it.
  - **Claude API tool-use loop.** Trade-off: full control and few dependencies;
    you build the loop.
  - **Claude Code-native** (subagents, skills, hooks, MCP, headless).
    Trade-off: great for repo-centric developer agents; needs Claude Code on
    every machine.
  - **LangGraph with OpenRouter.** Trade-off: explicit, resumable graphs;
    framework concepts and version churn.
- **Recommend when:** see "Choosing: signals" and the fit matrix in
  `../runtimes.md`. Always state the *why* against the chosen pattern.
- **Applies when:** always.
- **Look up live:** only if the user asks for current capabilities to decide.
- **Conflicts:** Claude Code-native ↔ multi-tenant service; offline ↔ hosted
  models.
- **Ledger key:** `runtime`.

## F-05 Language

- **Header:** `Language`
- **Question:** "Which language?"
- **Options** (by runtime):
  - Agent SDK: Python / TypeScript.
  - API loop: Python / TypeScript / other (name it).
  - LangGraph: Python / JavaScript.
  - Claude Code-native: Not applicable unless scripts, hooks or MCP servers are
    written. Then ask the scripting language.
- **Recommend when:** it matches the existing codebase or the team's stated
  language. Otherwise recommend Python for data or ML-heavy agents and
  TypeScript for web-service integration, and say so.
- **Applies when:** code is written.
- **Look up live:** whether the chosen runtime supports that language, with its
  current package name and version.
- **Conflicts:** language ↔ SDK availability.
- **Ledger key:** `language`.

## F-06 Claude Code primitives (multiSelect)

- **Header:** `Primitives`
- **Question:** "Which Claude Code building blocks should the agent use?"
- **Options:** Subagents / Skills / Hooks / MCP servers. Name slash commands,
  headless `claude -p`, plugin packaging and agent teams in the question text,
  and follow up if chosen.
- **Recommend when:** it follows from the pattern. Hierarchical or parallel →
  subagents. Domain knowledge → skills. Guardrails or automation → hooks.
  External systems → MCP.
- **Applies when:** runtime = Claude Code-native.
- **Look up live:** current frontmatter fields and hook events.
- **Ledger key:** `cc_primitives`.

## F-07 Model access

- **Header:** `Model access`
- **Question:** "How will the agent reach its models?"
- **Options:**
  - Claude runtimes: **Anthropic API** / **Amazon Bedrock** / **Google Vertex
    AI** / **Microsoft Foundry**.
  - LangGraph: **OpenRouter**. It's the only provider in scope for this skill
    version. Ask to confirm the account and API-key setup (the options are
    whether they have an OpenRouter key, or need to create one).
- **Recommend when:** the organization already uses a cloud provider → that
  provider. Otherwise the Anthropic API.
- **Applies when:** always.
- **Look up live:** feature and model availability differences on the chosen
  platform.
- **Conflicts:** data residency ↔ provider.
- **Ledger key:** `model_access`.

## F-08 Model per role

- **Header:** `Models`
- **Question:** "Which model tier should each role use?" Ask once per role
  (orchestrator, workers, evaluator, router…), batching up to 4 roles per round.
- **Options:**
  - **Most capable tier.** Trade-off: best reasoning; highest cost and latency.
  - **Balanced tier.** Trade-off: strong at lower cost.
  - **Fastest / cheapest tier.** Trade-off: great for routine, high-volume
    steps; weaker on hard reasoning.
- **Recommend when:** hard open-ended reasoning or orchestration → most
  capable. Workers on routine subtasks → balanced or fastest. Classification or
  routing → fastest.
- **Applies when:** always.
- **Look up live:** the **current model IDs, prices and context windows for
  each tier**, cited. On OpenRouter, current model slugs with tool-calling
  support and prices.
- **Conflicts:** tight budget ↔ most-capable tier everywhere.
- **Ledger key:** `models.{role}`.

## F-09 Package and environment manager

- **Header:** `Tooling`
- **Question:** "Which package or environment manager?"
- **Options:**
  - Python: **uv** / **pip + venv** / **poetry**.
  - JS/TS: **npm** / **pnpm** / **bun**.
- **Recommend when:** match whatever the repository already uses (from the
  scan). Otherwise recommend the most widely used default for the language, and
  say why.
- **Applies when:** code is written.
- **Ledger key:** `tooling`.
