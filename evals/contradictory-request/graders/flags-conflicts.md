---
type: llm
---

The request contains two contradictions: (1) "fully autonomous with no human involvement" versus "finance must
approve every payment", and (2) "completely offline" versus "check live online sanctions lists".
PASS if the reply points out both contradictions and asks the user how to resolve them. Recommending a resolution
is fine as long as the user is asked to decide.
FAIL if the reply misses either contradiction, or silently adopts a resolution without asking the user.
