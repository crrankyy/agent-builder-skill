# Decision framework: choosing the pattern

Four questions turn a confirmed purpose into a pattern recommendation. Ask them
as one themed round (phase P4, round A). Pre-select a recommendation for each
from the confirmed purpose, and still let the user choose. Then recommend a
pattern (round B) using the mapping below, and explain which answers drove it.

## The four questions

### 1. How much control and auditability do you need?

| Signal in the purpose | Points toward |
|---|---|
| High control: regulated domain, financial or safety-critical actions, decisions that must be explained to auditors | Single agent or sequential workflow (predictable, traceable) |
| Moderate control: support, content, analysis with human review | Hierarchical multi-agent (a supervisor enforces rules while specialists handle depth) |
| Low control: research, brainstorming, exploration | Collaborative multi-agent (unpredictability becomes a feature) |

Template (header `Control`):

- **High: every decision traceable** (Recommended when regulated, financial or
  safety-critical). Why: you can explain exactly why the agent acted.
  Trade-off: less flexibility on novel cases.
- **Moderate: oversight on key steps.** Why: rules enforced centrally while
  specialists adapt. Trade-off: more moving parts.
- **Low: exploration is the point.** Why: agents can follow unexpected leads.
  Trade-off: behavior is harder to predict and audit.

### 2. How complex is the problem domain?

| Signal | Points toward |
|---|---|
| One domain, straightforward repeatable tasks (answering product questions, processing returns, generating reports) | Single agent |
| Several domains but a predictable process (onboarding, compliance workflows, standard analyses) | Sequential or parallel workflow |
| Complex and open-ended (strategic analysis, research projects, system troubleshooting) | Multi-agent architecture |

Template (header `Complexity`): single domain / multi-domain but predictable /
open-ended. Each option describes one row above, with its trade-off.

### 3. What are the resource constraints?

| Signal | Points toward |
|---|---|
| Tight budget or token limits | Single agent, or a carefully bounded parallel workflow. Multi-agent systems use roughly an order of magnitude more tokens. |
| Time-to-market pressure | Start with a single agent and plan an evolution path. A single agent ships in weeks; multi-agent systems take months to get right. |
| Long-term strategic initiative | Design for modular evolution: a first agent with interfaces that let more agents be added later |

Template (header `Resources`): tight budget / ship fast / long-term platform /
no hard constraint. The last option must be offered too.

### 4. Does it need deep expertise in one domain or many?

| Signal | Points toward |
|---|---|
| One domain with established workflows | Single agent with specialized skills. Try this before going multi-agent. |
| Several distinct domains that must coordinate (e.g. legal review with financial analysis) | Multi-agent system where each agent carries its own skills |

Template (header `Expertise`): one domain, add skills / several coordinating
domains / not sure yet (triggers a follow-up question, never a guess).

## From answers to a pattern

1. Count which pattern each answer points to. When they agree, recommend that
   pattern.
2. When they disagree, apply these tie-breakers in order and **say which one
   decided it**:
   1. The simplest pattern that meets every *hard* requirement.
   2. The most reversible choice. It should be easy to evolve from the
      recommendation to the alternative later.
   3. Skills before more agents.
   4. The lowest cost at the stated volume.
3. If a hybrid fits better than any pure pattern (see
   `architecture-patterns.md`), offer it as its own option and name the parts.
4. Always offer the runner-up as an option, and name any other viable patterns
   in the question text so nothing is hidden.

## Pattern selection guide (quick reference)

| Pattern | Typical fits |
|---|---|
| Single agent | Customer service for well-defined products; document processing with clear rules; code review and routine development; routine analysis and reporting |
| Sequential | Multi-step approvals; content pipelines (draft → review → publish); data transformation and validation; compliance checks against multiple criteria |
| Parallel | Several perspectives improve quality; independent analyses can run at once; speed matters more than coordination overhead; risk assessment needing diverse viewpoints |
| Multi-agent | Complex problem-solving across diverse expertise; research and analysis projects; dynamic interactions spanning several systems; strategic planning and decision support |
| Evaluator-optimizer | Clear quality criteria plus iterative improvement: translation, security-sensitive code, technical documentation |

## Anti-patterns to flag (as questions, not refusals)

- Multi-agent for single-domain, routine work: cost with no gain.
- Parallel agents writing the same shared state or external system.
- Evaluator loops where responses must be real-time or budgets are strict.
- A sequential pipeline for work that needs backtracking.
- Collaborative swarms where the user needs high control or auditability.
- Emerging patterns (dynamic generation, peer-to-peer) as a first version.

When a user's choice matches an anti-pattern, record their choice and ask one
question. It offers keeping the choice and accepting the risk, adjusting it, or
adding a mitigation. The user decides.
