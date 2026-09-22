---
max_turns: 8
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TodoWrite]
tags: [trigger, negative]
---

My LangGraph node crashes with KeyError: 'messages' on the second step. The node is:

```python
def summarize(state):
    return {"summary": state["messages"][-1]}
```

What is the likely cause?
