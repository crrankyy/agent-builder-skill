# Consistency checks

Run this pass after every question round, and once more at the review gate
(P6). It compares the new answers with the confirmed purpose (D-00) and every
earlier decision. A conflict is never resolved by Claude. Show it, then ask.

## Conflict pairs

| If … | … and also … | Why it conflicts |
|---|---|---|
| Tight budget or token limits | Multi-agent, collaborative swarm, or evaluator loops without caps | Multi-agent systems cost roughly an order of magnitude more tokens; loops multiply calls |
| Real-time or low-latency responses | Evaluator-optimizer or multi-agent orchestration | Iteration and coordination add latency |
| High control or auditability | Collaborative or peer-to-peer pattern | Emergent behavior is hard to trace and explain |
| Agents share mutable state or the same external system | Parallel workflow | Concurrent writes can corrupt state or double-act |
| The process needs backtracking or iteration | Sequential workflow | Pipelines move one way |
| Offline or air-gapped | Web tools, hosted models, remote MCP servers | Requires network access |
| Claude Code-native runtime | A multi-tenant service for end users | Claude Code isn't a server runtime |
| Chosen language | A runtime without an SDK for that language | Can't build as specified |
| Fully autonomous (no approval) | Irreversible or external writes (money, deletes, customer messages) | Unreviewed high-impact actions |
| Data-residency or compliance constraint | A model access path or memory store outside that boundary | Violates the constraint |
| Success criteria not measurable | Evaluator-optimizer | The evaluator has nothing concrete to check |
| Privacy constraint | Persistent memory or logging of raw inputs | Retains sensitive data |
| "Ship fast" | Hybrid or multi-agent first version | Months, not weeks |
| LangGraph runtime | A provider other than OpenRouter | Out of scope for this skill version |

## How to raise a conflict

Ask one question per conflict (header `Conflict`). State both sides with their
decision IDs, then offer:

- **Keep both, accept the risk.** Record the risk in the plan's Risks section.
- **Change `{decision A}`** (and re-ask it).
- **Change `{decision B}`** (and re-ask it).
- **Add a mitigation** (for example a budget cap or an approval gate; follow up).

Recommend the option that preserves the user's explicit hard requirements, and
say why. Log the resolution as its own decision, linked to both IDs.

## Other checks in the pass

- Every decision still has a user answer. Nothing is "assumed".
- No option chosen earlier has been invalidated by a later lookup. If one has,
  ask.
- Every "Other" answer has been restated and confirmed.
- Delegated decisions ("you decide") are marked as delegated, with their scope.
