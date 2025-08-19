---
name: Bug fix
about: Fix a defect
title: "fix: <short summary>"
labels: bug
---
## Root cause

## Repro

## Fix approach

## Tests added

## Summary
One-liner of what this PR does.

## Context
Fixes #<issue>. Why now? Any related ADRs/Docs?

## Changes
- Bullet 1
- Bullet 2

## Testing Evidence
- Local: `make lint`, `make type`, `make test` (paste key output if helpful)
- Manual: curl/CLI/screenshots
- CI: all checks green (link if needed)

## Risk & Rollout
- Breaking changes? Migrations/config?
- User-facing docs updated? (README/RELEASE.md)
- Backout plan (if any)

## Checklist
- [ ] Title follows Conventional Commits (e.g., `feat: …`, `fix: …`)
- [ ] Issue linked (`Fixes #…`)
- [ ] Small, single-purpose PR
- [ ] Tests added/updated
- [ ] `make lint` passes (isort/black check)
- [ ] `make type` passes (mypy)
- [ ] `make test` passes (pytest)
- [ ] Docs updated if user-facing

