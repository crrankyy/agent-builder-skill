# Purpose clarity checklist

Use this in phase P2. The goal is a purpose statement the user explicitly
confirms. Every dimension below must be **Clear** before the gate passes.
Nothing may be filled in by assumption.

## Status per dimension

Track each dimension in the plan-file ledger with one of:

- **Clear**: the user stated it, or confirmed your restatement.
- **Partial**: some of it is known; name the missing part.
- **Missing**: not mentioned yet.
- **Conflicting**: two statements disagree; ask which holds.
- **Inferred**: you believe it from context or the project scan but the user
  hasn't confirmed it. It counts as not Clear until confirmed.

## Required dimensions

| # | Dimension | Clear when… | Example probes (turn into 2–4 options where possible) |
|---|---|---|---|
| 1 | **Outcome** | The deliverable is concrete: what exists or has changed when a run succeeds | "What does a successful run produce: a report, an action taken, an answer, a changed record?" |
| 2 | **Users and trigger** | You know who uses it and what starts a run | "Who uses it: you, your team, customers, another system?" / "What starts it: a chat message, a schedule, an event or webhook, a CLI call?" |
| 3 | **Inputs and sources** | Every data source and system is named | "Which systems does it read: repos, tickets, databases, the web, documents?" (ask for names, not categories) |
| 4 | **Actions and side effects** | You know what it may change, and whether each change is read-only or a write | "Does it only read and report, or does it also act: write files, send messages, update records, spend money?" |
| 5 | **Autonomy and human approval** | The points where a human must approve are explicit | "Where must a human approve before it proceeds?" |
| 6 | **Success criteria** | At least one observable, preferably measurable, criterion | "How will you judge it works: accuracy target, time saved, resolution rate, reviewer sign-off?" |
| 7 | **Non-goals** | At least one explicit out-of-scope item, or the user confirms "none" | "Anything it must NOT do or that's out of scope for the first version?" |

## Conditional dimensions (ask when relevant)

| Dimension | Ask when | Probe |
|---|---|---|
| Constraints | Always consider; ask if any hint exists | Budget per run or month, latency, compliance (e.g. financial, health, privacy), data residency, offline requirements |
| Scale | The agent serves many users or runs often | Runs per day, concurrent users, data volume |
| Existing assets | The project scan found relevant code or config | "The scan found X. Should the agent build on it, sit beside it, or ignore it?" |

## Ambiguity red flags

Any of these in the request means a follow-up question is required:

- Vague verbs: "handle", "manage", "deal with", "take care of", "optimize",
  "automate stuff".
- Unnamed systems: "our data", "the database", "our tools", "the usual sources".
- Open lists: "etc.", "and so on", "things like".
- Superlatives with no target: "fast", "accurate", "cheap", "the best".
- Implied writes: "fix", "update", "respond to", "clean up" (does it act or only
  suggest?).
- More than one goal in one sentence: split them and ask which is primary.
- Constraints that fight each other: "fully autonomous" with "approve
  everything", "offline" with "live web data".
- Unclear audience: "users", "people", "the team".

## Running the rounds

1. Restate the request in one neutral sentence. Don't interpret it yet.
2. Score every dimension, and list the gaps in the plan-file ledger.
3. Ask the gaps in themed rounds of up to 4 questions. For example: outcome,
   users and trigger together; then inputs and actions; then autonomy, success
   and non-goals. Offer concrete options drawn from the request, plus the
   automatic "Other". Where no sensible options exist (e.g. "name the systems"),
   ask in plain text.
4. After each round, update the statuses. Follow up any "Other" free text that
   is still ambiguous: restate your reading and ask for confirmation.
5. Repeat until all required dimensions are Clear and none is Conflicting.

## Purpose statement template

> `{agent name}` helps `{users}` achieve `{outcome}` by `{core actions}`,
> using `{inputs and systems}`. It is triggered by `{trigger}`. Humans approve
> `{approval points}`. Success means `{criteria}`. Out of scope: `{non-goals}`.
> Constraints: `{constraints, or "none stated"}`.

Present it in a question (header `Purpose`) with options:

- **Confirm purpose** (Recommended). Every dimension is marked Clear.
- **Edit it.** Say what to change (follow up in plain text).
- **Keep clarifying.** Something important is still missing.

Only **Confirm** passes the gate. Log the confirmed text verbatim as decision
`D-00`. Next, ask for the agent-name slug used for `.agent-builder/{agent-name}/`.
Recommend a short kebab-case name derived from the purpose; the user may pick
another.
