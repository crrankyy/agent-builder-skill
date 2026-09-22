# Fallback mode

Use this when plan mode or the question dialog isn't available. Examples:
headless `claude -p` runs, Agent SDK hosts, sessions where AskUserQuestion or
EnterPlanMode is denied or missing. The rules don't change: the user still
decides everything and nothing is written before approval. Only the mechanics
change.

## Load the references first

Tool pre-approvals from the skill end as soon as the user replies. In this mode
every answer is a new message, so read all reference files in the first turn,
before the first round (see SKILL.md P0). If a later read is denied anyway, tell
the user what's missing. Offer to continue from what's already loaded, or have
them allow reads of the skill folder. Never reconstruct a reference from memory
without saying so.

Live lookups (WebFetch, WebSearch) are affected the same way. When a lookup is
denied in a later turn, mark the fact UNVERIFIED and ask as usual. In a headless
run, tell the user they can allow lookups when continuing, for example
`claude -p --continue "{answers}" --allowedTools "Read,WebFetch,WebSearch"`.

## Announce it

Say once, at the start:

> Plan mode or the question dialog isn't available here, so I'll ask in plain
> text and show the plan in chat. Nothing will be written until you reply with
> the exact approval phrase.

## Asking questions

Number every question and its options, and put the recommended option first.
Answers are given by number, for example `1b, 2a`:

```text
Round 3: Operations (answer like "1b, 2a")

1. Where must a human approve before the agent proceeds?
   a) Approve only risky actions (Recommended). Why: … Trade-off: …
   b) Approve every write or external action. Trade-off: …
   c) Review outputs afterwards. Trade-off: …
   d) Something else (describe it)

2. …
```

- At most 4 questions per round, as in normal mode.
- Stop after each round and wait for the reply.
- An unanswered or partially answered round stays open. Re-ask the missing
  questions and never fill them in.
- In a single-shot run that can't receive a reply (such as `claude -p` without
  a follow-up), ask the first round. Explain that the conversation must continue
  (for example with `claude -p --continue` or `--resume`) to answer it. Stop
  there.

## Plan and approval

1. Keep the ledger in the conversation (a compact decisions table after each
   round), because there's no plan file.
2. At the end, show the full plan in chat using `plan-template.md`.
3. Ask for approval with this exact phrase:

   > To approve, reply exactly: **approve agent plan**
   > To change something, reply with what to change.

4. Treat anything other than the exact phrase as "keep planning".
5. When the user types the exact phrase, the plan guard lifts itself (its
   prompt hook recognizes the phrase). If writes are still blocked, run the
   guard's `stop` command (see SKILL.md P0). Then execute step 1. Step 1 writes
   the plan and decisions log to `.agent-builder/{agent-name}/`, using the text
   shown in chat.
