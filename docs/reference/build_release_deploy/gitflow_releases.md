# GitFlow Release Pattern

GitFlow is a branching model suited to formal release trains and hardening cycles. Here’s the concise version:

## Core idea

Branches are used not just for features but to represent **where in the lifecycle** a change sits: new work, integration, hardening, or production.

## Primary branches

* **`main`** (formerly “master”)
  * Production‑ready code
  * Each release is tagged here

* **`develop`**
  * Integration branch
  * Features merge here first
  * Release branches are cut from here

## Supporting branches

* **Feature (`feature/<slug>`)**
  * From `develop`; one logical change; merge back into `develop`

* **Release (`release/x.y.z`)**
  * From `develop` to stabilize for a release
  * Bugfixes, version bumps, final QA
  * Merge into `main` to ship and back into `develop` to sync

* **Hotfix (`hotfix/x.y.z`)**
  * From `main` to patch production
  * Merge into `main` (release) and `develop` (sync)

## Tasks / cadence

1. **Start work:** branch off `develop` → `feature/foo`.
2. **Integrate:** merge features back into `develop`. CI ensures integration quality.
3. **Cut release:** branch `release/1.2.0` from `develop`
   * Freeze features; fixes/docs only
   * Bump versions here
4. **Ship:** merge `release/1.2.0` into `main`, tag it, cut the release.
5. **Sync:** also merge `release/1.2.0` back into `develop`.
6. **Patch:** for urgent issues, `hotfix/1.2.1` from `main`, then merge into both `main` and `develop`.

## Terms

* **Tag**: Immutable marker (usually `vX.Y.Z`) on `main` per release
* **Merge strategy**: Often squash for features; explicit merges for release/hotfix
* **Release candidate**: Code in a `release/*` branch being stabilized
* **Back‑merge**: Merging release/hotfix changes back into `develop`

---

## Strengths

* Clear separation of “production” vs. “work in progress.”
* Works well with formal release trains and QA hardening cycles.
* Easy mental model if you’re used to SDLC phases.

## Weaknesses

* Heavy for solo/hobby or CI/CD “continuous deploy” styles.
* Lots of merging → risk of conflicts, overhead.
* Requires discipline to not sneak features into release/hotfix branches.

## References

* [GitFlow (original blog)](https://nvie.com/posts/a-successful-git-branching-model/)
* [GitHub Flow (alternative)](https://docs.github.com/get-started/quickstart/github-flow)
* [Managing labels](https://docs.github.com/issues/using-labels-and-milestones-to-track-work/managing-labels)
