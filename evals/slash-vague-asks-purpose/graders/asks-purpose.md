---
type: llm
---

The user asked a planning skill for "an agent for my team" with no other detail.
PASS if the reply asks the user clarifying questions about the agent's purpose (for example what job it does,
who uses it, what starts it, what it produces) and makes no architecture decisions.
FAIL if the reply recommends or selects a specific runtime, framework, SDK, model or architecture pattern as a
decision, presents a build plan, or writes code.
