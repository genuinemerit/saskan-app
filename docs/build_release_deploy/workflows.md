# GitHub Workflows

## Use GitHub tooling to automate build, review, deploy tasks

See:

### `.github/release-drafter.yml`

and

### `.github/workflows/release-drafter.yml`

- Config file = how to draft release notes.

- Workflow file = when and where to run Release Drafter.

- Future changes mostly involve branch strategy, labels/categories, and versioning policy.

## How the two files work

.github/release-drafter.yml (the config)

Defines how Release Drafter should structure draft release notes.

Groups merged PRs by label (Features, Bug Fixes, etc.).

Controls version bumping (major/minor/patch) based on labels.

Skips PRs with skip-changelog.

Can even auto-label PRs by title or file path.

→ Think of it as the rulebook for how release notes are generated.

.github/workflows/release-drafter.yml (the workflow)

A GitHub Action triggered on PR activity and pushes to main.

Runs the Release Drafter app with your config.

Updates or creates a draft release in GitHub’s “Releases” section automatically.

→ Think of it as the automation that enforces the rulebook.

## What might change later

Branching model:
If you switch from a simple main-only workflow to main + develop or release branches, you’ll need to update the workflow triggers (on: push: branches:).

Versioning strategy:
Right now, version bumps are inferred from PR labels. If you adopt semantic-release, manual tagging, or a different scheme, you’d adjust the version-resolver or disable it.

Labels & categories:
You may add new categories (performance, infra, dependencies) or refine existing ones as more contributors join.

Autolabeler rules:
If you standardize commit message conventions (Conventional Commits), you can simplify the autolabeler or even drop it.

Security/Private repos:
If you go private or handle sensitive changes, you might exclude certain categories from public notes.

### Notes / usage

* Label your PRs (`enhancement`, `bug`, `docs`, `chore`, `breaking`) to drive both **section grouping** and **version bumping**.
* Add `skip-changelog` to any PR you don’t want listed.
* When you’re ready to cut a release, go to **Releases → Draft**; the notes will be pre-filled and version set per `version-resolver`.
* This pairs cleanly with your `CHANGELOG.md`—you can copy the generated notes into it or keep both.

## Moving to a "Gitflow" feature -> develop -> main -> tagged-release schedule

Here’s a compact “Gitflow-ready” plan.

# What changes under Gitflow

* **Branches**

  * `feature/*` → PR → `develop` (integration)
  * `release/*` → hardening → PR → `main` (final)
  * `hotfix/*` → PR → `main` (urgent fix), then back-merge to `develop`
* **Draft notes behavior**

  * Keep a **rolling prerelease draft** on `develop` (preview next version).
  * Keep a **final release draft** on `main` (what ships).
* **Versioning**

  * On `develop`: preview tags like `vX.Y.Z-rc.N` (or just leave untagged).
  * On `main`: normal `vX.Y.Z`, resolved from labels.

# Config setup

Use **two configs** so each branch can format notes differently.

## `.github/release-drafter.yml` (final, for `main`)

* Same as the one we drafted earlier (sections, labels, version-resolver).
* Normal tags: `v$NEXT_PATCH_VERSION`.

```yaml
# .github/release-drafter.yml
name-template: 'v$NEXT_PATCH_VERSION'
tag-template: 'v$NEXT_PATCH_VERSION'
# … categories, change-template, exclude-labels, version-resolver, autolabeler …
```

## `.github/release-drafter-prerelease.yml` (for `develop`)

* Mark as prerelease; optional RC-style names.
* Keep categories identical so wording stays consistent.

```yaml
# .github/release-drafter-prerelease.yml
name-template: 'v$NEXT_PATCH_VERSION-rc'
tag-template: 'v$NEXT_PATCH_VERSION-rc'
prerelease: true
# (reuse the same categories, change-template, exclude-labels, version-resolver, autolabeler)
```

# Workflow changes

Run the Action on both branches, selecting the right config.

```yaml
# .github/workflows/release-drafter.yml
name: Release Drafter

on:
  push:
    branches: [ main, develop, 'release/*', 'hotfix/*' ]
  pull_request:
    types: [opened, edited, reopened, synchronize, labeled, unlabeled, closed]
    branches: [ main, develop ]
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: read

jobs:
  draft_on_develop:
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        with:
          config-name: release-drafter-prerelease.yml
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  draft_on_main:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        with:
          config-name: release-drafter.yml
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  draft_on_release_branches:
    if: startsWith(github.ref, 'refs/heads/release/')
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        with:
          # show prerelease notes while hardening on release/* (optional)
          config-name: release-drafter-prerelease.yml
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  draft_on_hotfix_branches:
    if: startsWith(github.ref, 'refs/heads/hotfix/')
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v6
        with:
          # hotfixes typically go to main → use final template
          config-name: release-drafter.yml
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

# Labeling & version bumps

* Keep using PR labels to drive **version-resolver** (e.g., `breaking` → major, `enhancement` → minor, `bug` → patch).
* Enforce label usage via branch protection or a PR checklist.

# Cutting releases

* When `release/*` merges to `main`, the **main draft** is already populated → click “Publish release” (or add an auto-tagging job if you prefer).
* After publishing, **back-merge `main` into `develop`** so version history stays aligned.

# What you might tweak later

* **Tag style on `develop`**: switch between `-rc` tags or untagged prereleases.
* **Triggers**: if you add `support/*` or `maintenance/*` branches, include them.
* **Categories**: add `Dependencies` if you rely on Dependabot, or split `Maintenance` into `CI`/`Refactor`.
* **Automated tagging**: add a separate workflow to create tags when you publish (or use a “Release please” style flow instead of labels).

This gives you clean previews on `develop`, production-ready notes on `main`, and scales as collaborators and branches multiply.
