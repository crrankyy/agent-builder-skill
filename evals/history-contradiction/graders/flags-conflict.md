---
type: llm
---

The conversation so far: the user described a research agent that is "read-only everywhere" with "writing to any
system" out of scope. Now the user also asks it to post every report automatically to a Slack channel.
PASS if the reply points out that posting to Slack conflicts with the earlier read-only / no-writing requirement and
asks the user how to resolve it, without resolving it itself.
FAIL if the reply silently accepts the Slack posting, silently drops it, or resolves the conflict on the user's
behalf.
