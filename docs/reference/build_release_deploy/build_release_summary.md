Software lifecycle: quick glossary

- **Tag**: A VCS snapshot labeled with a version (e.g., `v1.2.0`). “This commit = this version.”
- **Build**: Turn source into artifacts (binaries, images, packages). Embed metadata (commit, build number, timestamp). Rebuilds from the same tag should be identical.
- **Release**: A vetted build published for consumption. In GitHub, a Release references a tag and attaches notes and artifacts.
- **Deploy**: Install a release into an environment (dev/stage/prod) via manual steps or CI/CD.

In short:

- Tag = mark the code
- Build = produce artifact
- Release = publish the artifact
- Deploy = run it somewhere

This is a compact, repo‑centric playbook for Git/GitHub: tag → build → release, with PR and automation practices. Deployment specifics can layer on later.

# Branching & Versioning

- **Default**: `main` is always releasable. Feature work in short‑lived branches: `feat/<slug>`, `fix/<slug>`.
- **Merge strategy**: Prefer squash‑merge for a linear history. Enable “Require PR” and “Require linear history”.
- **Versioning**: SemVer (`MAJOR.MINOR.PATCH`) + Conventional Commits (e.g., `feat: add CLI --dry-run`).
- **Tagging**: Annotated tags on `main` (e.g., `v1.4.2`). Prefer CI to create release tags.

# Pull Requests

- **Small, scoped PRs**: Aim for ≤300 net LOC.
- **One concern**: Don’t mix refactors with features.
- **Draft early**: Convert to ready when tests/docs pass.
- **Template checklist**: Tests, docs, breaking changes.
- **Reviews**: ≥1 approver (2 for risky PRs). Author shouldn’t self‑approve.
- **Auto‑merge**: Enable for low‑risk PRs (docs/chore/deps) after checks.
- **Blocking labels**: `do-not-merge`, `breaking-change`, `needs-product-signoff`.

# Repository Hygiene

Add these once and keep them strict:

- `CODEOWNERS` (review routing)
- `PULL_REQUEST_TEMPLATE.md` (checklist + risk note)
- `CONTRIBUTING.md` (branch names, commit style, test instructions)
- `SECURITY.md` (vulnerability reporting)
- `RELEASE.md` (how to cut releases)
- `CHANGELOG.md` (auto‑generated; see Release Drafter)

# Branch Protection (recommended)

- Require PRs, reviews (1–2), status checks, and up‑to‑date branches.
- Dismiss stale reviews on new commits.
- Restrict who can push to protected branches and who can create tags `v*`.
- Optionally require signed commits; enforce for admins too.

# Automation (GitHub Actions)

On every PR:

- Lint/format (fast fail)
- Unit tests (parallel if possible)
- Build artifact (if applicable) + quick smoke tests
- SCA + SAST: Dependabot (weekly) and CodeQL (scheduled + PR)
- License/size checks (block large files)

On push to `main`:

- Build release‑candidate artifact(s)
- Store as workflow artifacts; stamp with commit SHA and short version

On tag `v*`:

- Rebuild from tag (reproducibility)
- Create a GitHub Release with notes
- Attach artifacts (checksums + SBOM)
- Optionally sign artifacts (Cosign) and add SLSA provenance

Example: minimal CI set (language‑agnostic placeholders)

- `ci.yml` (PR): install deps → lint → test → build → upload artifact
- `release.yml` (tag): build from tag → generate notes → attach artifacts
- `codeql.yml` (security): CodeQL on PR + weekly
- `dependabot.yml`: ecosystems (npm/pip/poetry/go/mod/docker), weekly

# Changelogs & Releases

- Use Release Drafter to auto‑curate notes from labels + Conventional Commits.
  - Map labels to sections: Features, Fixes, Docs, Chore, Breaking
- When tagging, publish a GitHub Release:
  - Title: version (e.g., `v1.4.2`), body from Release Drafter
  - Attach: binaries/containers, checksums (SHA256), SBOM (CycloneDX)

# Build Artifacts (keep it simple)

- Binaries: embed `version`, `commit`, `builtAt`
- Containers: pin base by digest; `COPY` exact files; avoid `latest`
  - Multi‑arch (amd64/arm64) only if needed
- Package registries:
  - Containers → GHCR (`ghcr.io/org/app:1.4.2` and `:1.4`)
  - Libraries → publish to the ecosystem registry on tag

# Secrets & Environment

- Prefer OpenID Connect to cloud providers; otherwise use GitHub Environments with reviewers.
- Keep only non‑prod secrets at repo level; store prod secrets at org/environment level with approvals.
- Never echo secrets in logs; mask patterns.

# Labels & PR Automation

- Labels drive notes & routing: `feat`, `fix`, `docs`, `chore`, `breaking-change`, `infra`, `security`, `dependencies`.
- Auto‑label by path (e.g., `ui/`, `cli/`, `infra/`), and auto‑assign CODEOWNERS.
- Auto‑close stale PRs after 30–45 days without activity (comment before closure).

# Monorepo vs Multi‑repo

- If monorepo: use path‑filtered workflows and per‑package versioning (e.g., Changesets).
- If multi‑repo:
  - Use release‑please or Release Drafter per repo
  - Trigger downstream builds via repository dispatch/webhooks when a library publishes

# Minimal viable workflow (this week)

1. Enforce branch protections on `main`; squash‑merge only.
2. Add templates and CODEOWNERS.
3. Wire PR CI: lint → test → build.
4. Turn on Dependabot + CodeQL.
5. Release flow: merge to `main` → CI passes → Release Drafter prepares notes → tag `vX.Y.Z` (manually or via workflow) → `release.yml` builds and publishes artifacts.

Example skeletons (trimmed)

`.github/release-drafter.yml`

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

PR template (`.github/PULL_REQUEST_TEMPLATE.md`)

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

# Reproducibility & Provenance (nice‑to‑have)

- Commit lockfiles; deterministic builds (no floating deps)
- Checksum + SBOM per artifact
- Optional: sign images (Cosign) and attach SLSA attestations

# Readying for DigitalOcean (later deploy)

Keep these now so deployment is trivial later:

- Build container images on tag and push to `ghcr.io`.
- Parameterize runtime config via env/secret files (works on DO App Platform, Droplets, or Kubernetes).
- Provide a health endpoint (`/healthz`) and a smoke test in CI for deploy gates.

Approach this like a solo dev building scaffolding for a future team: minimal guardrails, but the same shape as larger setups. You can self‑review and iterate now, then scale when collaborators arrive.

---

Guiding principles for a solo‑dev setup

1. Keep the full lifecycle visible
   Even if you self‑approve PRs, still branch → PR → CI → merge into `main` to build muscle memory.

2. Allow pragmatic exceptions
   - Require PRs for merge, but permit self‑reviews (for now)
   - Use squash merges to keep history tidy
   - Keep tagging/release creation manual until you’re ready to automate

3. Simulate a team if useful
   - Use multiple GitHub accounts or separate git configs on different clones to simulate “colleagues”
   - Alternatively, treat a second machine as “reviewer” for fresh eyes

4. Automate only the essentials
   - Start with: lint + tests on PR, build on tag, draft release
   - Add Dependabot, CodeQL, and container pushes later

5. Deploy can wait
   First, make builds reliable and tagged; then add DigitalOcean deployment.

---

Suggested rollout pace

Phase 1 – Repo hygiene

- Add `README.md`, `CONTRIBUTING.md`, PR template
- Protect `main` branch, but allow self‑reviews
- Adopt a branch naming convention

Phase 2 – CI basics

- Add a PR workflow: run lint + tests
- Fail fast if tests break

Phase 3 – Releases

- Introduce annotated tags (`v0.1.0`, etc.)
- Create a GitHub Release with notes; attach artifact(s)
- Later: add Release Drafter to auto‑generate notes

Phase 4 – Automation polish

- Trigger on tags: build + publish artifacts
- Add Dependabot for updates
- Add CodeQL code scanning

Phase 5 – Ready for collaborators

- Enforce two‑review rule (once applicable)
- Restrict tag creation to Actions only
- Require signed commits if desired

---

Take it step by step. Test each part before layering the next.

---

## YAML naming

Use the `.yaml` extension for config files we author (e.g., `.pre-commit-config.yaml`). Third‑party defaults (e.g., GitHub Actions) may continue using `.yml`.

## References

To fix the 'no bare HTML' markdown warning, you can convert the URLs into markdown links. Here's how you can do it:

- [Semantic Versioning](https://semver.org)
- [Conventional Commits](https://www.conventionalcommits.org)
- [Release Drafter](https://github.com/release-drafter/release-drafter)
- [GitHub Releases](https://docs.github.com/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Branch protection rules](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Actions](https://docs.github.com/actions)
- [GitHub Container Registry](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Dependabot](https://docs.github.com/code-security/dependabot)
- [CodeQL](https://codeql.github.com/docs/)
- [CycloneDX SBOM](https://cyclonedx.org)
- [SLSA provenance](https://slsa.dev)
- [Cosign (sigstore)](https://github.com/sigstore/cosign)
- [Changesets (monorepos)](https://github.com/changesets/changesets)
- [release-please](https://github.com/googleapis/release-please)
