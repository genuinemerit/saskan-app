The usual software lifecycle, key terms:

* **Tag**
  A snapshot of the codebase, usually in source control (Git), labeled with a semantic version (`v1.2.0`) or milestone. It’s the marker that says “this commit = this version.”

* **Build**
  Transforming source into artifacts: binaries, containers, packages, etc. A build might embed metadata (commit hash, build number, timestamp). Reproducibility matters: building the same tag should always yield the same artifact.

* **Release**
  A build that’s been approved as “official” for use. In GitHub terms, a Release often references a tag and attaches build artifacts plus notes. In enterprise, a release may also include change logs, approvals, QA sign-off, and version bumping.

* **Deploy**
  The act of installing a release into a target environment: dev, staging, prod. Deployments can be manual, scripted, or automated (CI/CD). It’s where release artifacts meet infrastructure (VMs, k8s, Lambda, etc.).

In short:

* Tag = mark the code
* Build = turn code into artifact
* Release = certify and publish the artifact
* Deploy = put it into a running environment


Tight, repo-centric playbook for Git/GitHub, covering tag → build → release plus PR and automation practices. We’ll stage deploy-to-DO later.

# Branching & Versioning

* **Default:** `main` is always releasable. Feature work in short-lived branches: `feat/<slug>`, `fix/<slug>`.
* **Merge strategy:** Prefer **squash-merge** to keep a linear history. Enable *“Require linear history”* and *“Require PR”*.
* **Versioning:** **SemVer** (`MAJOR.MINOR.PATCH`) + **Conventional Commits** for messages. Example: `feat: add CLI --dry-run`.
* **Tagging:** Annotated tags on `main` (e.g., `v1.4.2`). Only CI should create tags for releases.

# Pull Requests (workflow & etiquette)

* **Small, scoped PRs.** Target ≤300 LOC net change.
* **One concern per PR.** No refactors mixed with features.
* **Draft early.** Convert to Ready when tests/docs are green.
* **Checklist in PR template:** tests added, docs updated, breaking changes called out.
* **Reviews:** At least 1 approver; 2 for risky changes. Author cannot self-approve.
* **Auto-merge:** Enable after checks pass for low-risk PRs (docs, chore, deps).
* **Blocking labels:** `do-not-merge`, `breaking-change`, `needs-product-signoff`.

# Repository hygiene files

Add these once and keep them strict:

* `CODEOWNERS` (directs reviews).
* `PULL_REQUEST_TEMPLATE.md` (checklist + risk note).
* `CONTRIBUTING.md` (branch names, commit style, how to run tests).
* `SECURITY.md` (vuln reporting).
* `RELEASE.md` (how we cut releases).
* `CHANGELOG.md` (auto-generated; see Release Drafter below).

# GitHub protection rules (recommended)

* Require PRs, reviews (1–2), status checks, and up-to-date branches before merge.
* Dismiss stale reviews on new commits.
* Restrict who can *push* to protected branches and who can *create tags matching* `v*`.
* Require signed commits (optional but good), and **enforce** for admins too.

# Automation (GitHub Actions) – minimal but effective

**On every PR:**

* Lint/format (fast fail).
* Unit tests (parallel if possible).
* Build artifact (if applicable) and run quick smoke tests.
* SCA + SAST: Dependabot (weekly) and CodeQL (scheduled + PR).
* License & size checks (block large files).

**On main push:**

* Build release candidate artifact(s).
* Store as workflow artifacts; stamp with commit SHA and short version.

**On tag `v*`:**

* Rebuild from tag (reproducibility).
* Create GitHub Release with notes.
* Attach build artifacts (checksums + SBOM).
* Optionally sign artifacts (Cosign) and generate provenance (SLSA v1.0 attestation).

### Example: minimal CI set (language-agnostic placeholders)

* `ci.yml` (PR): install deps → lint → test → build → upload artifact
* `release.yml` (tag): build from tag → generate notes → attach artifacts
* `codeql.yml` (security): CodeQL on PR + weekly
* `dependabot.yml`: ecosystems (npm/pip/poetry/go/mod/docker), weekly cadence

# Changelogs & Releases

* Use **Release Drafter** to auto-curate notes from labels + Conventional Commits.

  * Map labels to sections: Features, Fixes, Docs, Chore, Breaking.
* On tagging, publish a **GitHub Release**:

  * Title: version (e.g., `v1.4.2`), body from Release Drafter.
  * Attach: binaries/containers, **checksums (SHA256)**, **SBOM** (CycloneDX).

# Build artifacts (keep it simple)

* **Binaries:** embed `version`, `commit`, `builtAt`.
* **Containers:** pin base image by digest, `COPY` exact files, **no `latest`**.

  * Multi-arch (amd64, arm64) only if needed.
* **Package registries:**

  * Containers → GitHub Container Registry (`ghcr.io/org/app:1.4.2` and `:1.4`).
  * Libraries → publish to the ecosystem registry on tag.

# Secrets & environment

* Use **OpenID Connect** to cloud where possible; otherwise GitHub **Environments** with required reviewers to gate access.
* Store only non-prod secrets at repo level; prod secrets at org/environment with approvals.
* Never echo secrets in logs; mask patterns.

# Labels & PR automation

* Labels drive notes & routing: `feat`, `fix`, `docs`, `chore`, `breaking-change`, `infra`, `security`, `dependencies`.
* Autolabel by path (e.g., `ui/`, `cli/`, `infra/`), and auto-assign **CODEOWNERS**.
* Autoclose stale PRs after 30–45 days *without* activity (comment before closure).

# Monorepo vs multi-repo (since you have related repos)

* If **monorepo**: path-filtered workflows (only run what changed), per-package versioning (e.g., Changesets).
* If **multi-repo**:

  * Use **Release-please** or Release Drafter per repo.
  * Trigger downstream builds via repository dispatch/webhooks when a library publishes.

# Minimal viable workflow you can adopt this week

1. **Enforce branch protections** on `main` + squash-merge only.
2. **Add templates and CODEOWNERS.**
3. **Wire PR CI**: lint → test → build.
4. **Turn on Dependabot** + **CodeQL**.
5. **Release flow**: merge to `main` → CI passes → create GitHub Release draft via Release Drafter → push tag `vX.Y.Z` (or let release action tag) → `release.yml` builds and publishes artifacts.

# Example skeletons (trimmed)

**`.github/release-drafter.yml`**

```yaml
name-template: 'v$RESOLVED_VERSION'
tag-template: 'v$RESOLVED_VERSION'
categories:
  - title: '✨ Features'
    labels: ['feat']
  - title: '🐛 Fixes'
    labels: ['fix']
  - title: '🧰 Maintenance'
    labels: ['chore', 'dependencies']
  - title: '📚 Docs'
    labels: ['docs']
change-template: '- $TITLE (#$NUMBER) by @$AUTHOR'
version-resolver:
  major:
    labels: ['breaking-change']
  minor:
    labels: ['feat']
  patch:
    labels: ['fix', 'chore', 'docs', 'dependencies']
```

**PR template (`.github/PULL_REQUEST_TEMPLATE.md`)**

```markdown
## Summary
[What/why in 1–3 sentences]

## Changes
- 

## Checklist
- [ ] Tests added/updated
- [ ] Docs/CHANGELOG updated
- [ ] Breaking change noted (label)
```

# Reproducibility & provenance (nice-to-have)

* **Lockfiles** committed; deterministic builds (no floating deps).
* **Checksum + SBOM** per artifact.
* Optional: **Cosign** sign images and attach **SLSA** attestations.

# Readying for DigitalOcean (later deploy)

Keep these now so deployment is trivial later:

* Build container images on tag and push to `ghcr.io`.
* Parameterize runtime config via env/secret files (works on DO App Platform, Droplets, or Kubernetes).
* Health endpoint (`/healthz`) and simple smoke test in CI to reuse in deploy gates.


Approach this like a solo dev building scaffolding for a team that may come later. Think of it as setting up a “tiny but professional” shop: minimal guardrails, but with the same shape as a larger team. That way you can self-review, test, and adjust without friction, while knowing the system will scale when collaborators arrive.

---

### Guiding principles for a solo-dev setup

1. **Keep the full lifecycle visible**
   Even if you self-approve PRs, go through the motions: open a branch, open a PR, run CI, merge into `main`. This builds muscle memory.

2. **Allow pragmatic exceptions**

   * Enable *“require PRs for merge”*, but permit self-reviews (for now).
   * Use squash merges to keep history tidy.
   * Tagging and release creation can stay manual until you’re comfortable automating.

3. **Simulate a team if useful**

   * Yes, you can use multiple GitHub accounts or even just separate git configs (`user.name`, `user.email`) on different clones to simulate “colleagues.”
   * Another option: treat your second machine as “reviewer” and force yourself to read PRs with fresh eyes.

4. **Automate only the essentials**

   * Don’t try to wire up every possible GitHub Action yet.
   * Start with: lint + tests on PR, build on tag, draft release.
   * Add bells and whistles (Dependabot, CodeQL, container pushes) later.

5. **Deploy can wait**
   For now, just ensure build artifacts are reliable and tagged. Once that’s solid, deploy to DigitalOcean will be a smoother step.

---

### Suggested rollout pace

**Phase 1 – Repo hygiene**

* Add `README.md`, `CONTRIBUTING.md`, PR template.
* Protect `main` branch, but allow self-reviews.
* Adopt branch naming convention.

**Phase 2 – CI basics**

* Add GitHub Action workflow for PRs: run tests + lint.
* Fail fast if tests break.

**Phase 3 – Releases**

* Introduce annotated tags (`v0.1.0`, etc.).
* Manual GitHub Release with notes, attach artifact (optional).
* Later: add Release Drafter to auto-generate notes.

**Phase 4 – Automation polish**

* Let Actions trigger on tags: build + publish artifact.
* Add Dependabot for updates.
* Add CodeQL security scan.

**Phase 5 – Ready for collaborators**

* Enforce two-review rule (when you actually have two).
* Restrict tag creation to Actions only.
* Require signed commits if desired.

---

Take it step by step. Test each part before layering the next.

---

## YAML naming standard

**YAML file naming**: This project standardizes on the `.yaml` extension for configuration files we author (e.g. `.pre-commit-config.yaml`), while third-party defaults like GitHub Actions may continue using `.yml`.

