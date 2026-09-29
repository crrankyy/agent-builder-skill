# Question bank: index

The infrastructure questions asked in phases P4–P6, grouped into four
categories. Each entry lists the options and the signals for recommending one.
The user always decides.

| Category | File | Asked in |
|---|---|---|
| Foundation: code location, runtime, language, models | `question-bank/foundation.md` | P4 (after the pattern) |
| Capabilities: tools, MCP, skills, context, memory, multi-agent details, reporting period | `question-bank/capabilities.md` | P5 |
| Operations: interface, triggers, human approval, security, observability, cost, deployment | `question-bank/operations.md` | P5 |
| Quality: metrics, evals, tests, CI, git workflow, docs | `question-bank/quality.md` | P5 and P6 |

## Triage (phase P3)

Before the infrastructure rounds, build a triage table from each entry's
**Applies when** rule. One row per entry, grouped by category:

| ID | Topic | Proposed status | Reason |
|---|---|---|---|
| C-06 | Memory | Not applicable | Purpose says every run is independent (D-00) |

Statuses are **Decide now**, **Not applicable** and **Defer**. Defer means an
explicit open item in the plan with an owner and a trigger; use it sparingly.

**Small-scope defaults.** When D-00 describes one user on one machine (no
deployment, no other users), propose these rows as Not applicable, even where
an entry says "Applies when: always". Their defaults go on the derived-details
list for P6:

- O-07 Observability (default: JSON-lines logs to a local file);
- O-10 and O-11 Deployment (default: runs on the local machine only);
- O-12 Scale, and the multi-agent-only entries unless the pattern is
  multi-agent.

Show the table in your reply text. Don't give it a round of its own. Add this
question (header `Triage`) to the first later round that has room:

- **Accept triage** (Recommended). Why: every row has a stated reason.
- **Change some rows.** Say which (follow up in plain text).
- **Explain first.** Show the reasoning per row, then ask again.

Every Not-applicable and Defer row is logged as a decision.

## Composing rounds

- At most 4 questions per round, each with 2–4 options. The tool adds "Other"
  automatically.
- Group questions that depend on each other into the same or consecutive
  rounds, in the order listed in each file. Never ask a question whose options
  depend on an answer not yet given.
- Run the live lookups that the round's options depend on *before* asking.
- If an entry has more than 4 viable options, ask the family first, then the
  variant. Name every viable option in the question text.
- Format options per R6 in SKILL.md. Decisions put the recommended option
  first, labelled "(Recommended)", with "Why: … Trade-off: …". In a multiSelect
  decision, every recommended option carries its own label and Why. Fact and
  confirm questions carry no recommendation.
- **Derived details** (file and folder names, minor defaults) aren't asked one
  by one. Collect them for the P6 bundle.

## Entry format

Each entry in the category files has:

- **ID and topic.**
- **Header:** the ≤12-character header used in AskUserQuestion.
- **Question:** the question text.
- **Options:** up to 4 options, each with its trade-off.
- **Recommend when:** signals from the confirmed purpose, earlier decisions or
  the project scan.
- **Applies when:** the triage rule.
- **Look up live:** facts needed before asking.
- **Conflicts:** pairs to check in `consistency-checks.md`.
- **Ledger key:** the field name in the decisions log.
