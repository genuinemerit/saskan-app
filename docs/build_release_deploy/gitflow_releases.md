# GitFlow Release Pattern

GitFlow is familiar if you’ve lived in structured IT with release trains. Here’s the high-level summary, stripped to essentials:

---

## GitFlow Release Pattern

### Core Idea

Branches are used not just for features but to represent **where in the lifecycle** a change sits: new work, integration, hardening, or production.

### Primary Branches

* **`main` (a.k.a. master)**

  * Always represents production-ready code.
  * Each commit here corresponds to a release.
  * Tagged for version numbers.

* **`develop`**

  * Integration branch.
  * Features are merged here first.
  * From here, you cut release branches when preparing for a deployment.

### Supporting Branches

* **Feature branches (`feature/<slug>`)**

  * Spawned from `develop`.
  * Contain one logical feature or change.
  * Merged back into `develop` once complete.

* **Release branches (`release/x.y.z`)**

  * Spawned from `develop` when you’re ready to stabilize for a new release.
  * Bugfixes, version bumps, final QA happen here.
  * Merged into both `main` (for the release) and back into `develop` (to sync changes).

* **Hotfix branches (`hotfix/x.y.z`)**

  * Spawned from `main` to quickly patch production.
  * Merged into both `main` (for immediate release) and `develop` (to keep history consistent).

### Tasks / Cadence

1. **Start work:** branch off `develop` → `feature/foo`.
2. **Integrate:** merge features back into `develop`. CI ensures integration quality.
3. **Cut release:** branch `release/1.2.0` from `develop`.

   * Freeze features, fix only bugs and docs.
   * Bump version numbers here.
4. **Ship:** merge `release/1.2.0` into `main`, tag it, cut the release.
5. **Sync:** also merge `release/1.2.0` back into `develop`.
6. **Patch:** for urgent issues, `hotfix/1.2.1` from `main`, then merge into both `main` and `develop`.

### Defining Terms

* **Tag:** immutable marker (usually `vX.Y.Z`) applied to `main` for each release.
* **Merge strategy:** typically merge commits (to preserve branch structure) or squash for features; release/hotfix merges usually recorded explicitly.
* **Release candidate:** code in a `release/*` branch being stabilized.
* **Back-merge:** the act of merging release/hotfix changes back into `develop`.

---

### Strengths

* Clear separation of “production” vs. “work in progress.”
* Works well with formal release trains and QA hardening cycles.
* Easy mental model if you’re used to SDLC phases.

### Weaknesses

* Heavy for solo/hobby or CI/CD “continuous deploy” styles.
* Lots of merging → risk of conflicts, overhead.
* Requires discipline to not sneak features into release/hotfix branches.

---

Next: map this **GitFlow structure into a minimal GitHub repo config** (branch protections, workflow rules, naming) so we can ease into it solo without tripping over the “heavy” parts
