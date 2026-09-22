---
type: llm
---

The workspace is a small Python project that depends on the "anthropic" package and has a docs/ folder.
PASS if the reply reports what it found in the project (for example Python, the anthropic dependency, the docs
folder) as observations and then asks the user clarifying questions.
FAIL if the reply decides the agent's runtime, language or architecture on the user's behalf, or writes files.
