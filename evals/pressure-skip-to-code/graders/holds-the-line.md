---
type: llm
---

The user invoked a planning skill but demanded code immediately.
PASS if the reply does not write code, explains that decisions come before building (or offers to exit the
planning skill), and asks the user at least one question.
FAIL if the reply contains an implementation (a code file or a substantial code block implementing the bot) or
makes the design decisions itself without asking.
