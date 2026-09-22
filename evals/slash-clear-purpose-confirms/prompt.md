---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
tags: [purpose]
---

/agent-builder A research agent for our 6-person product team. When someone asks a question about a competitor in our team chat, it searches the public web and our internal product wiki, then replies in the same thread with a sourced summary within 5 minutes. It is read-only: it never edits the wiki and never posts anywhere except that thread. A run succeeds when the team rates the answer useful; we want 80% useful ratings. Out of scope: pricing analysis.
