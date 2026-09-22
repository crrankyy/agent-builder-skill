# Operations questions

Asked in P5, after the capability questions.

## O-01 Interface

- **Header:** `Interface`
- **Question:** "How do people (or systems) interact with the agent?"
- **Options:**
  - **CLI or script.** Trade-off: simplest; developers only.
  - **Chat surface** (web UI, Slack, Teams…; name it). Trade-off: friendly;
    integration work.
  - **HTTP API or service.** Trade-off: other systems can call it; hosting
    needed.
  - **Inside Claude Code** (slash command or skill). Trade-off: zero UI work;
    Claude Code users only.
- **Recommend when:** follow the trigger and users (D-00). Developer tooling →
  CLI or Claude Code. End users → chat or API.
- **Applies when:** always.
- **Ledger key:** `interface`.

## O-02 Trigger

- **Header:** `Trigger`
- **Question:** "What starts a run?"
- **Options:**
  - **On demand** (a person asks). Trade-off: no automation.
  - **Schedule** (cron, or scheduled cloud agents). Trade-off: needs a runner.
  - **Event or webhook** (new ticket, PR, message). Trade-off: needs endpoint
    and auth.
  - **Queue or batch.** Trade-off: scalable; more infrastructure.
- **Recommend when:** follow D-00. This question confirms and details it.
- **Applies when:** always.
- **Ledger key:** `trigger`.

## O-03 Human approval level

- **Header:** `Approval`
- **Question:** "Where must a human approve before the agent proceeds?"
- **Options:**
  - **Approve every write or external action.** Trade-off: safest; slowest.
  - **Approve only risky actions** (name them: money, deletes, customer-facing
    messages). Trade-off: balance.
  - **Review outputs afterwards.** Trade-off: faster; errors reach reviewers.
  - **Fully autonomous, with alerts.** Trade-off: fastest; highest risk.
- **Recommend when:** any irreversible or external write → at least "risky
  actions". Read-only agents → review afterwards.
- **Applies when:** always.
- **Conflicts:** fully autonomous ↔ risky writes; high control ↔ no approval.
- **Ledger key:** `hitl`.

## O-04 Permissions, sandbox and network

- **Header:** `Sandbox`
- **Question:** "How is the agent contained?" (multiSelect)
- **Options:** Least-privilege tool allowlist / Container or VM sandbox /
  Read-only credentials where possible / Network egress allowlist.
- **Recommend when:** it executes code or shell → a container sandbox and
  allowlist. It touches production systems → read-only credentials plus an
  egress allowlist.
- **Applies when:** the agent writes, executes code, or reaches external
  systems.
- **Ledger key:** `sandbox`.

## O-05 Secrets

- **Header:** `Secrets`
- **Question:** "How are API keys and credentials provided?"
- **Options:**
  - **Environment variables from a local `.env`** (gitignored). Trade-off:
    simple; local only.
  - **A cloud secret manager.** Trade-off: secure and auditable; setup.
  - **CI or platform secrets.** Trade-off: fine for pipelines.
  - **OS keychain.** Trade-off: good for desktop tools.
- **Recommend when:** local prototype → `.env`. Deployed service → a secret
  manager.
- **Applies when:** any credential is needed (always for model access).
- **Note:** the plan must never contain secret values; only variable names.
- **Ledger key:** `secrets`.

## O-06 Guardrails (multiSelect)

- **Header:** `Guardrails`
- **Question:** "Which guardrails should the plan include?"
- **Options:**
  - **Prompt-injection defenses** (treat retrieved or tool content as data;
    constrain tools).
  - **PII detection or redaction.**
  - **Output validation** (schema checks, policy screening, possibly a parallel
    screening call).
  - **Topic or scope restrictions.**
- **Recommend when:** web or user-supplied content → injection defenses.
  Personal data → PII. User-facing output → validation.
- **Applies when:** untrusted input, personal data, or user-facing output.
- **Ledger key:** `guardrails`.

## O-07 Observability

- **Header:** `Tracing`
- **Question:** "How will you see what the agent did and why?"
- **Options:**
  - **Structured logs** (JSON lines per step). Trade-off: simplest.
  - **OpenTelemetry traces** to your backend. Trade-off: standard; needs a
    collector.
  - **A framework-native tracing service** (e.g. for LangGraph; name it after
    lookup). Trade-off: rich; vendor dependency.
  - **Provider dashboards and usage reports only.** Trade-off: minimal insight.
- **Recommend when:** always trace prompts, tool calls, decisions and token use.
  Multi-agent → real traces, not only logs.
- **Applies when:** always.
- **Look up live:** tracing integrations for the chosen runtime.
- **Ledger key:** `observability`.

## O-08 Cost controls (multiSelect)

- **Header:** `Cost`
- **Question:** "How should cost be controlled?"
- **Options:** Per-run token or cost budget / Cheaper models for routine roles /
  Prompt caching / Rate limits and concurrency caps.
- **Recommend when:** high volume or a tight budget → all of them. Low volume →
  budget plus caching.
- **Applies when:** always (low volume may reduce this to one question).
- **Look up live:** caching and batch support, and prices.
- **Ledger key:** `cost`.

## O-09 Error handling

- **Header:** `Errors`
- **Question:** "What happens when a step fails?"
- **Options:**
  - **Retry with backoff, then fail loudly.** Trade-off: simple.
  - **Retry, then fall back** (a smaller model or a degraded path). Trade-off:
    resilient; can mask problems.
  - **Escalate to a human.** Trade-off: safe; needs a channel.
  - **Dead-letter queue for later.** Trade-off: good for batch jobs.
- **Recommend when:** interactive use → retry then escalate. Batch → dead-letter
  queue.
- **Applies when:** always.
- **Ledger key:** `errors`.

## O-10 Deployment target

- **Header:** `Deploy`
- **Question:** "Where will the agent run?"
- **Options:**
  - **Local machine only.**
  - **Container** (name the platform).
  - **Serverless function or job.**
  - **CI runner or Claude Code** (a plugin or headless run).
- **Recommend when:** a prototype → local. Scheduled or event-driven → container
  or serverless. Repo automation → CI runner.
- **Applies when:** always.
- **Ledger key:** `deploy.target`.

## O-11 Does the plan run the deployment?

- **Header:** `Deploy step`
- **Question:** "Should executing the plan actually deploy, or stop at a tested,
  deployable artifact?"
- **Options:**
  - **Stop at a tested artifact** (Recommended default). Trade-off: you deploy
    by hand, reviewed.
  - **Deploy as the final step.** Trade-off: fully automated; auto mode may
    block unfamiliar infrastructure actions.
- **Applies when:** the deployment target isn't local.
- **Ledger key:** `deploy.in_plan`.

## O-12 Scale and rate limits

- **Header:** `Scale`
- **Question:** "What load must it handle?"
- **Options:** Low (one user or occasional runs) / Moderate (a team, daily) /
  High (many concurrent users or large batches; give numbers).
- **Recommend when:** follow D-00 constraints.
- **Applies when:** more than one user, or batch volume.
- **Look up live:** provider rate limits for the chosen access path.
- **Ledger key:** `scale`.
