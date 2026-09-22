## What and why

<!-- What does this change, and why? Link any issue. -->

## Checklist

- [ ] Keeps the core contract: Claude recommends, the user decides every question; nothing is assumed or built before approval
- [ ] No fast-changing facts (model IDs, versions, API names, prices) added to `skills/agent-builder/references/`
- [ ] Reference text is in our own words, with links to sources
- [ ] `python3 -m unittest discover -s tests -v` passes
- [ ] `python3 scripts/check_repo.py` passes
- [ ] `claude plugin validate . --strict` passes
- [ ] `CHANGELOG.md` updated under Unreleased (and version bumped if this is a release)

## Eval results

<!-- If SKILL.md or behavior-relevant references changed, paste the `claude plugin eval` summary table. -->
