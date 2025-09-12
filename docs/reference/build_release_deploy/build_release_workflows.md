# GitHub Workflows

Use GitHub Actions and Release Drafter to automate build, review, and release.

Key files:

- `.github/release-drafter.yml` — config for release notes
- `.github/workflows/release-drafter.yml` — when to update draft notes
- `.github/workflows/publish-release.yml` — build/publish on tag

Most tweaks live in labels/categories, version policy, and branch strategy.

## Example flow (GitFlow‑style)

- Merge features into `develop` → Release Drafter updates the draft
- Cut `release/1.2.0` from `develop` → mark as pre‑release in notes
- Stabilize in `release/1.2.0` (fixes/docs only)
- Merge `release/1.2.0` to `main`, create tag `v1.2.0` (manually or in workflow)
- The tag triggers publish workflow → draft becomes an official release

## Hotfixes

- Branch `hotfix/1.2.1` from `main`, fix, merge back to `main`, tag `v1.2.1` → publish fires
- Also merge the hotfix into `develop` to keep history in sync

## Defining labels

Release Drafter groups PRs by their labels. Pre‑define the label set in your repo so categories populate correctly.

---

## Why labels matter

- On merge, Release Drafter reads PR labels
- Labels route entries to sections (Features, Fixes, Docs, etc.)
- If no label matches, items may fall under “Other Changes” or be omitted

---

## How to create labels

1. In your repo, open Issues → Labels, or visit `https://github.com/<org>/<repo>/labels`
2. Click New label; name must match `.github/release-drafter.yml`
3. Optionally add a description; choose a color
4. Save; repeat for the full set

---

## Recommended label set (GitFlow + Release Drafter)

| Label             | Purpose                                | Suggested color |
| ----------------- | -------------------------------------- | --------------- |
| `feat`            | New features                           | bright green    |
| `fix`             | Bug fixes                              | red             |
| `hotfix`          | Emergency production fixes             | darker red      |
| `perf`            | Performance improvements               | orange          |
| `refactor`        | Internal code changes                  | purple          |
| `docs`            | Documentation updates                  | blue            |
| `chore`           | Maintenance, CI config, infra          | gray            |
| `build`           | Build system changes                   | dark gray       |
| `ci`              | Continuous integration changes         | light blue      |
| `dependencies`    | Dependency bumps (manual)              | light green     |
| `deps`            | Dependency bumps (Dependabot, etc.)    | pale green      |
| `security`        | Security fixes                         | dark red        |
| `breaking-change` | Backward-incompatible changes          | black           |
| `skip-changelog`  | Don’t include this PR in release notes | very light gray |

---

## Example behavior

- Merge a PR labeled `feat` → appears under Features
- Merge a PR labeled `fix` → appears under Fixes
- Add `breaking-change` → version resolver can bump major
- Mark `skip-changelog` → excluded from notes

---

Draft a one‑time script using GitHub CLI to bulk‑create labels.

Prereqs:

- Install/auth: `gh auth login`
- Set repo: `export SASKAN_REPO="<owner>/<repo>"` (e.g., `org/saskan-app`)
- Script(s): `saskan/tools/setup-labels.sh`, `saskan/tools/remove-default-labels.sh`

Usage:

```bash
bash setup-labels.sh               # apply changes
DRY_RUN=1 bash setup-labels.sh     # preview only
```

## Linter contracts

`import-linter` inspects the project’s import graph and enforces rules (“contracts”).

- Declare contracts in `importlinter.ini`
- Run `lint-imports` locally or in CI
- If rules are broken, the command exits non‑zero and the PR fails

---

Example `importlinter.ini`

```ini
[importlinter]
root_package = saskan

[contract: ui_may_depend_on_client_only]
name = UI may import only infra.net.client and infra.config
type = forbidden
modules = saskan.ui_cli
forbidden_modules =
    saskan.engine
    saskan.core
    saskan.infra.net.server
    saskan.infra.persistence

[contract: engine_must_not_import_infra_or_ui]
name = Engine may not import Infra or UI
type = forbidden
modules = saskan.engine
forbidden_modules =
    saskan.ui_cli
    saskan.infra.net
    saskan.infra.persistence

[contract: core_is_pure]
name = Core imports nothing outside itself
type = forbidden
modules = saskan.core
forbidden_modules =
    saskan.engine
    saskan.infra
    saskan.ui_cli
```

Each `[contract: …]` block defines a rule.

---

In CI (GitHub Actions)

Add a job step in `.github/workflows/lint.yml`:

```yaml
- name: Check import contracts
  run: poetry run lint-imports
```

`lint-imports` reads `importlinter.ini`, analyzes imports, and fails if rules are broken.

---

An import‑linter contract is a checked‑in rule definition. Running it in CI enforces layered design like other status checks (`black`, `mypy`, `pytest`).

## References

- [Release Drafter](https://github.com/release-drafter/release-drafter)
- [Labels (GitHub)](https://docs.github.com/issues/using-labels-and-milestones-to-track-work/managing-labels)
- [GitHub CLI](https://cli.github.com)
- [import-linter](https://github.com/seddonym/import-linter)
