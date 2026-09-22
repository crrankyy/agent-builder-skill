---
type: llm
---

The conversation so far: a planning skill asked four numbered questions (1-4) about a research agent. The user has
now answered only questions 1 and 3.
PASS if the reply records the answers to questions 1 and 3 and asks questions 2 and 4 again (or clearly lists them
as still open and asks for them), without choosing answers for 2 or 4 itself.
FAIL if the reply treats question 2 or 4 as answered, fills either in with a recommendation, or moves on to new
questions without asking for 2 and 4.
