# Live lookup of fast-changing facts

Model IDs, SDK and framework APIs, package versions, pricing and MCP server
availability change often. Never state them from memory. Look them up while
planning, cite them, and have the plan re-verify them at execution time.

## What counts as a fast fact

- Model names and IDs, context windows, pricing, and which features a model
  supports.
- Package names and latest versions (PyPI, npm).
- SDK and framework APIs: class and function names, parameters, configuration
  fields.
- Claude Code configuration surface: subagent and skill frontmatter, hook events,
  plugin manifest fields, CLI flags.
- MCP servers: existence, maintainer, install command, auth needs.
- OpenRouter: model slugs, prices, tool-calling support, API base URL and auth
  header.
- Third-party provider APIs (Gmail, Slack, Stripe, …): endpoint and method
  names, OAuth scopes, rate limits and quotas, batch sizes.

## Canonical sources

Use these final URLs directly. WebFetch doesn't follow redirects to another
host.

| Topic | Source |
|---|---|
| Claude models | `https://platform.claude.com/docs/en/models/overview` and `https://platform.claude.com/docs/en/about-claude/models/choosing-a-model` |
| Claude API and platform docs index | `https://platform.claude.com/llms.txt` |
| Claude Agent SDK | `https://code.claude.com/docs/en/agent-sdk/overview` |
| Claude Code docs index | `https://code.claude.com/docs/llms.txt` |
| LangGraph (Python / JS) | `https://docs.langchain.com/oss/python/langgraph/overview`, `https://docs.langchain.com/oss/javascript/langgraph/overview`, index `https://docs.langchain.com/llms.txt` |
| OpenRouter | `https://openrouter.ai/docs/quickstart`; model catalog JSON `https://openrouter.ai/api/v1/models` |
| Python packages | `https://pypi.org/pypi/{package}/json` (`info.version`, `info.requires_python`) |
| npm packages | `https://registry.npmjs.org/{package}/latest` (`version`) |
| MCP servers | `https://registry.modelcontextprotocol.io/`, `https://github.com/modelcontextprotocol/servers`, `https://modelcontextprotocol.io/` |
| Third-party provider APIs | The vendor's own API reference. It isn't pre-approved, so fetching it asks the user for permission; if they decline, the fact is UNVERIFIED |

If the `claude-api` skill is available in the session, prefer it for Claude
model IDs and API usage, and still cite it.

## How to look things up reliably

1. **Prefer structured endpoints.** Registry JSON and the OpenRouter models
   endpoint give exact values. Read the field; don't paraphrase it. Cite only
   what the command printed: a field it didn't output isn't verified. A capped
   query (`limit=20`, the first page) never becomes a count or a "none exists"
   claim.
2. **Ask WebFetch for verbatim quotes.** WebFetch answers through a summarizing
   model that can invent details. Phrase prompts as "Quote verbatim the lines
   that state X". Don't trust a summary that has no quote.
3. **Cross-check model IDs.** Confirm a model ID in two places (for example, the
   models overview and the API reference or the `claude-api` skill) before it
   goes into a plan.
4. **Look up only what the next round's options depend on.** Don't prefetch
   everything.
5. **Cite every fact** in the plan as `{fact} (source: {URL}, retrieved
   {YYYY-MM-DD})`.

## Names you didn't look up

Build steps name classes, functions, scopes and endpoints. Any of these that
wasn't fetched in this session (an SDK class, a checkpointer, a provider's
OAuth scope or method) is **UNVERIFIED**: add it to §4's UNVERIFIED list. Build
step 2 then checks it, against the installed package where there is one. Don't
fetch docs for every name while planning.

## When a lookup fails

The fetch may be denied, time out, or give contradictory answers. In any of
these cases:

1. Mark the fact **UNVERIFIED** in the ledger.
2. Tell the user what couldn't be verified and why. Any option whose text
   quotes the fact says UNVERIFIED next to it.
3. Don't ask per fact. At P6, one question (header `Unverified`) lists every
   UNVERIFIED fact with these options: *Verify now* (retry the lookups), *Defer
   to build step 2*, or *I'll supply values*. Recommend deferring when no
   decision depends on the exact value. Never substitute a remembered value
   silently.
4. Every UNVERIFIED fact must appear in the plan's step 2 (re-verify facts), with
   the exact check to run.

## Research beyond a quick lookup

If a decision can't be framed without deeper research (for example, comparing
three MCP servers for a system the user named), follow rule R10. First ask the
user, stating what would be researched and the rough cost. Only then launch one
research subagent. It returns findings and sources, never a decision.
