# Examples

> **Illustrative, as of 2026-09-22.** Model IDs, prices and package versions in
> these plans were looked up live on that date and will go stale. That's
> expected: every plan re-verifies its facts in step 2 before building anything.

Two real agent-builder 0.1.0 planning sessions for the same agent: a
**multi-source research agent**. For a product team's analysts, it answers
research questions from the public web and a read-only Postgres analytics
database, and writes a sourced markdown report.

| Folder | Runtime | What's interesting |
|---|---|---|
| [`claude-agent-sdk/`](multi-source-research-agent/claude-agent-sdk/) | Claude Agent SDK (Python), Anthropic API, Sonnet 5 | The skill recommended the Agent SDK and the user accepted. The interview also surfaced two issues nobody raised: the SDK loads the user's `~/.claude` settings by default, and it writes run transcripts. Both conflicted with the confirmed purpose and were resolved as decisions. |
| [`langgraph/`](multi-source-research-agent/langgraph/) | LangGraph (Python) via OpenRouter, Sonnet 5 | The user **overrode** the runtime recommendation and picked LangGraph. The rest of the interview adapted: OpenRouter data-retention routing, a SQLite checkpointer for the approval pause, and a pseudonym-versus-resume conflict caught by the consistency pass. |

Each folder holds what step 1 of the plan writes into a project:

- `plan.md`: the approved plan, including a Mermaid diagram, cited stack facts,
  ordered build steps with acceptance checks, an eval plan, risks and Appendix A.
- `decisions.md`: every question as asked, the options, the recommendation and
  why, the user's answer, and whether it was delegated.

## How these were produced

- Both sessions ran headless (`claude -p … --continue`), so the skill used its
  plain-text **fallback mode**. The maintainer answered each round as the
  analyst team would. The answers were mostly the recommended options, with
  deliberate overrides and some free-text details.
- The two sessions share the interview up to the runtime question. The LangGraph
  session was forked from that point.
- The files are lightly curated: session IDs were replaced, and one risk line
  about the maintainer's temporary working folder was removed. Nothing else was
  edited.
- The skill never reads this folder. It exists for people deciding whether
  agent-builder fits their workflow.
