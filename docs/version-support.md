# Version Support

## Current Upstream Anchor

As checked on 2026-04-01:

- Local upstream clone path: `./pretext/`
- Local upstream branch: `main`
- Local upstream commit: `a8d1e35d3973a0f63c007f7645f4a8918135a57b`
- Local upstream HEAD subject: `Keep correctness browser automation in background`
- Local `pretext/package.json` version: `0.0.3`
- Latest published npm version from `npm view @chenglou/pretext version`: `0.0.3`
- Local clone `origin/HEAD` currently resolves to the same commit as the local clone head

## What This Skill Currently Targets

The skill should treat version support as two linked but distinct anchors:

1. Published package anchor:
   - the latest published npm version currently verified here is `0.0.3`
2. Source-tree anchor:
   - the local upstream clone currently corresponds to commit `a8d1e35d3973a0f63c007f7645f4a8918135a57b`

When answering package-consumer questions, prefer the published package anchor first.
When answering upstream-source or internal-architecture questions, prefer the source-tree anchor first.

## Update Procedure

When refreshing to a newer upstream version, do all of these:

1. Check the published package version:
   - `npm view @chenglou/pretext version time --json`
2. Check the local and remote source anchors:
   - `git -C pretext rev-parse HEAD`
   - `git -C pretext ls-remote origin HEAD`
   - `Get-Content -Raw pretext/package.json`
3. Update this document with:
   - check date
   - local commit
   - local package version
   - latest published npm version
   - whether local `origin/HEAD` matches the checked-out clone
4. Update `docs/project-memory.md` with the new version-support snapshot
5. Re-run at least:
   - `python <codex-home>/skills/.system/skill-creator/scripts/quick_validate.py skills/pretext`
   - `python skills/pretext/scripts/check_layout_api_sync.py`
   - `python skills/pretext/scripts/check_pretext_eval_coverage.py`
6. If API shape, taxonomy, or harness surfaces changed:
   - update `reference/`
   - update selector scripts
   - update eval coverage

## Decision Rule

- If npm and source commit disagree about what is "latest", do not collapse them into one number.
- Record both anchors explicitly.
- Do not silently claim support for a newer published version until this document and `project-memory.md` are updated.
