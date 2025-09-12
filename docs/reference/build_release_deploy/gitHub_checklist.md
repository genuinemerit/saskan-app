# Repo/GitHub Setup Checklist

Things to verify before you start coding (GitFlow‑style with `develop`).

1) Default branch

- Set default branch to `develop` so new PRs target it.
- GitHub: Settings → Branches → Default branch → `develop`.

1) Branch protection (for `main` and `develop`)

- Require PRs before merge; allow squash‑merge only
- Require linear history
- After CI exists: require status checks (e.g., `ci-pr`)
- Disallow force pushes and deletions; include administrators
- [Docs](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)

Using GitHub CLI (gh)

Enable squash‑only merges:

```bash
gh repo edit <OWNER/REPO> \
  --enable-squash-merge \
  --disable-merge-commit \
  --disable-rebase-merge
```

Protect branches:

```bash
OWNER=<owner>; REPO=<repo>
protect () {
  local BR=$1
  gh api -X PUT \
    repos/$OWNER/$REPO/branches/$BR/protection \
    -f required_pull_request_reviews.required_approving_review_count=0 \
    -f required_linear_history=true \
    -f enforce_admins=true \
    -f allow_force_pushes=false \
    -f allow_deletions=false
}
protect main
protect develop
```

Add required status checks once your job exists (example uses `ci-pr`):

```bash
for BR in main develop; do
  gh api -X PUT repos/$OWNER/$REPO/branches/$BR/protection \
    -f required_linear_history=true \
    -f enforce_admins=true \
    -f allow_force_pushes=false \
    -f allow_deletions=false \
    -f required_pull_request_reviews.required_approving_review_count=0 \
    -F required_status_checks.strict=true \
    -F required_status_checks.contexts[]=ci-pr
done
```

Notes

- “Require PRs” is in `required_pull_request_reviews` (approvals can be 0 for solo)
- Status‑check names must match your Actions job(s)

1) Labels

- Create the label set once (see `setup-labels.sh`)
- [Docs](https://docs.github.com/issues/using-labels-and-milestones-to-track-work/managing-labels)

1) Templates and docs

- `.github/PULL_REQUEST_TEMPLATE.md`
- `CONTRIBUTING.md`
- Optional: `SECURITY.md`, `RELEASE.md`
- `CODEOWNERS` (see `.github/CODEOWNERS`)

1) Minimal CI

- `.github/workflows/ci.yml` runs on PRs into `develop` and pushes to `develop`
- `.github/workflows/release-tag.yml` builds artifacts on tags (releases/hotfixes)
- `.pre-commit-config.yaml` + `make hooks`

1) Versioning starting point

- Set `pyproject.toml` version to `0.1.0`
- First release comes from `release/0.1.0`

---

## Start Coding

1) Branch off `develop`:

```bash
git checkout -b feat/app-skeleton develop
```

1) Minimal skeleton

- `saskan/__init__.py` (sets `__version__`)
- `saskan/cli.py` (Typer/Click entrypoint)
- `tests/test_cli.py`

1) Commit → push → open PR to `develop` → self‑review

- Pre‑commit will run and reformat; stage and re‑commit as needed

1) Merge via squash when CI is green

## Ship a release candidate (RC)

```bash
make start-release RELEASE=0.1.0
# stabilize; fixes only
make finish-release
# pushes tag v0.1.0; release workflow builds artifacts
```

---

## Git tips

Log with a compact graph:

```bash
git log --oneline --graph --decorate --all

# pro alias
git config --global alias.lg "log --oneline --graph --decorate --all"
git lg
```

Keep local refs in sync with remote deletions/tags:

```bash
git fetch --prune --tags
```

This updates remote refs, fetches tags, and prunes deleted refs locally.

---

References

- [Branch protection](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub CLI](https://cli.github.com)
