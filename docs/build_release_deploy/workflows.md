# GitHub Workflows

## Use GitHub tooling to automate build, review, deploy tasks

See:

### `.github/release-drafter.yml`

- Config file = how to draft release notes.

and

### `.github/workflows/release-drafter.yml`

and 

### `.github/workflows/publish-release.yml`

- Workflow files = when and where to run Release Drafter.

- Future changes will mostly involve branch strategy, labels/categories, and versioning policy.

## Flow we’ll follow

- Merge features into develop → draft notes update automatically.

- Cut release/1.2.0 from develop → draft toggles to pre-release.

- Stabilize in release/1.2.0 (only fixes/docs).

- Merge release/1.2.0 → main, tag v1.2.0 (manually or via a workflow step).

- Pushing the tag triggers Publish Release → draft becomes official release with your tag.

## Hotfixes

- Branch hotfix/1.2.1 from main, fix, merge back to main, tag v1.2.1 → publish workflow fires.

- Also merge hotfix back into develop to keep lines in sync.

## Defining labels

Right — Release Drafter doesn’t invent categories by itself, it looks at **labels on PRs**. If those labels don’t exist in your repo, the categories you configured won’t populate. So you need to pre-define them once in GitHub.

---

## Why labels matter

* When you merge a PR, Release Drafter checks its labels.
* It sorts the PR into the right section (✨ Features, 🐛 Fixes, etc.).
* If no label matches, the PR might show up under “Other Changes” or be skipped.

---

## How to create labels

1. Go to your repo on GitHub.
2. Click **Issues** → **Labels** (or visit directly: `https://github.com/<org>/<repo>/labels`).
3. For each label, click **New label**.

   * Enter the **name** (must match exactly what’s in your `.github/release-drafter.yml`).
   * Optionally add a **description** (e.g., “New feature or enhancement”).
   * Pick a color (just to help scanning).
4. Save. Repeat until your label set is complete.

---

## Recommended label set (for GitFlow + Release Drafter)

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

## Example workflow

* You merge a PR labeled `feat` → Release Drafter puts it in the **Features** section.
* You merge a PR labeled `fix` → goes into **Fixes**.
* If you tag it `breaking-change` too → Release Drafter bumps **major version**.
* If you mark `skip-changelog` → it won’t show up in release notes at all.

---

Draft a **one-time script** (e.g., using GitHub CLI) that bulk-creates these labels in your repo, so you don’t have to click them in the UI one by one.

THe one-time bash script that bulk-creates (or updates) the labels via GitHub CLI (gh). It’s idempotent and supports a dry-run.

Prereqs

Install & auth: `gh auth login`

Set your repo: export SASKAN_REPO="<owner>/<repo>" (e.g., org/saskan-app) (in ~/.bash_aliases then source it)

Script: `saskan/tools/setup-labels.sh`

### Usage

bash setup-labels.sh                 # applies changes

or

DRY_RUN=1 bash setup-labels.sh       # preview only

Delete unused default labels from GitHub repo:

Script: `saskan/tools/remove-default-labels.sh`







