#!/usr/bin/env python3
"""Repository checks run in CI (and locally before a release).

  python3 scripts/check_repo.py

Checks:
  1. skills/*/SKILL.md frontmatter parses as YAML, has name + description, and
     uses only frontmatter keys Claude Code understands.
  2. description + when_to_use stay within Claude Code's 1,536-character
     listing budget (longer text is truncated when Claude decides to trigger).
  3. .claude-plugin/plugin.json "version" equals the newest CHANGELOG.md entry
     and the "skill version" stated in SKILL.md.

Requires PyYAML (pip install pyyaml). JSON syntax of the manifests is checked
separately in CI with jq.
"""

import glob
import json
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("check_repo.py needs PyYAML: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTING_BUDGET = 1536
KNOWN_KEYS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "allowed-tools", "disallowed-tools", "disable-model-invocation",
    "user-invocable", "model", "effort", "context", "agent", "background",
    "paths", "shell", "hooks", "metadata", "license", "compatibility",
}


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError("no YAML frontmatter block at the top of the file")
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def check_skills(errors):
    paths = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))
    if not paths:
        errors.append("no skills/*/SKILL.md found")
    for path in paths:
        rel = os.path.relpath(path, ROOT)
        try:
            fm = frontmatter(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append("%s: invalid frontmatter: %s" % (rel, exc))
            continue
        for key in ("name", "description"):
            if not fm.get(key):
                errors.append("%s: missing '%s'" % (rel, key))
        unknown = sorted(set(fm) - KNOWN_KEYS)
        if unknown:
            errors.append("%s: unknown frontmatter keys: %s" % (rel, ", ".join(unknown)))
        listing = (fm.get("description") or "") + " " + (fm.get("when_to_use") or "")
        size = len(listing.strip())
        status = "OK" if size <= LISTING_BUDGET else "TOO LONG"
        print("%s: description + when_to_use = %d / %d chars (%s)" % (rel, size, LISTING_BUDGET, status))
        if size > LISTING_BUDGET:
            errors.append("%s: description + when_to_use is %d chars (max %d)" % (rel, size, LISTING_BUDGET))
        lines = open(path, encoding="utf-8").read().count("\n")
        if lines > 500:
            errors.append("%s: %d lines; keep SKILL.md under 500 lines" % (rel, lines))


def check_version(errors):
    manifest = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8"))
    version = manifest.get("version")
    changelog = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
    m = re.search(r"^## \[(\d+\.\d+\.\d+[^\]]*)\]", changelog, re.M)
    top = m.group(1) if m else None
    print("plugin.json version %s; newest CHANGELOG entry %s" % (version, top))
    if not version:
        errors.append("plugin.json has no version")
    elif version != top:
        errors.append("plugin.json version %s != newest CHANGELOG entry %s" % (version, top))


def check_skill_version(errors):
    """SKILL.md states the version so plans can record it; keep it in sync."""
    manifest = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8"))
    text = open(os.path.join(ROOT, "skills", "agent-builder", "SKILL.md"), encoding="utf-8").read()
    m = re.search(r"skill version (\d+\.\d+\.\d+)", text)
    found = m.group(1) if m else None
    print("SKILL.md skill version %s" % found)
    if found != manifest.get("version"):
        errors.append("SKILL.md says skill version %s but plugin.json says %s" % (found, manifest.get("version")))


def main():
    errors = []
    check_skills(errors)
    check_version(errors)
    check_skill_version(errors)
    if errors:
        print("\nFAILED:")
        for e in errors:
            print("  - " + e)
        return 1
    print("\nAll repository checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
