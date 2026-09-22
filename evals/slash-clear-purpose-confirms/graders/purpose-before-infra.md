---
type: llm
---

The user gave a detailed description of a research agent to a planning skill.
PASS if the reply either presents a purpose statement and asks the user to confirm or edit it, or asks only about
remaining gaps in the purpose (such as the chat platform, the wiki system, or approval points).
FAIL if, before the purpose is confirmed, the reply asks infrastructure questions (runtime, framework, model,
database, hosting), states infrastructure decisions, or presents a build plan.
