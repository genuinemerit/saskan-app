# Repo/GitHub Set up Checklist

Things to do or verify before starting to code

1. 🗹 Set default branch to develop (so new PRs target it).

- Settings → Branches → Default branch → develop.

2. 🗹 Protect main and develop:

- Require PRs before merge.

- Allow squash merge only.

How to:

Browser (quick)

Allow only squash merges

Repo → Settings → General → Pull Requests → Merge button

- ✅ Enable Allow squash merging

- ⛔ Disable Allow merge commits and Allow rebase merging → Save

Protect main and develop

Repo → Settings → Branches → Branch protection rules → Add rule

- Branch name pattern: main (repeat for develop)

- ✅ Require a pull request before merging

- (Optional solo mode) set Required approvals = 0

- ✅ Require linear history (nice to keep history clean)

- (After CI exists) ✅ Require status checks to pass → select your job (e.g., ci-pr)

- ⛔ Allow force pushes off; ⛔ Allow deletions off

- ✅ Include administrators (so rules apply to you too)

Using gh...

squash-only:

```bash
# set once per repo
gh repo edit <OWNER/REPO> \
  --enable-squash-merge \
  --disable-merge-commit \
  --disable-rebase-merge
```

protect branches:

```bash
OWNER=<owner>; REPO=<repo>

# function to protect a branch
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
Add required status checks once your CI job exists (example uses a job named ci-pr):

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
- “Require PRs” is represented by the required_pull_request_reviews block (you can keep approvals at 0 for solo work and raise later).

- Status-check contexts should match your Actions job name(s). If unsure, merge one PR, look at the exact check name, then plug it in.

- You can repeat these commands any time to tighten rules (e.g., set approvals to 1 when collaborators arrive).


- 🗹 Require status checks to pass: ci-pr (we added a script for this).

- Solo mode: allow you to bypass or self-approve for now (see notes above).

3. 🗹 Create labels. Run `setup-labels.sh`

4. 🗹 Ensure templates exist:

- .github/PULL_REQUEST_TEMPLATE.md (done)

- CONTRIBUTING.rst (done)

- Optional: SECURITY.md, RELEASE.md <== ?

5. 🗹 CODEOWNERS

See: saskan-app/.github/CODEOWNERS

See: saskan-app/docs/meta/configs_and_envs.md

6. 🗹 Minimal CI

- Create .github/workflows/ci.yml to run on PRs into `develop` and on pushes to `develop` (fast feedback).

- See: .github/workflows/ci.yml

- Create .github/workflows/release-tag.yml so tags build artifacts that align with GitFlow releases/hotfixes

- See:  .github/workflows/release-tag.yml

- Create .pre-commit-config.yaml so that make hooks does something useful.

- See: saskan-app/.pre-commit-config.yaml

- And run it:  `make hooks`

7. 🗹 Versioning starting point

Set pyproject.toml version to 0.1.0.

Don’t tag main yet; your first real release will come from release/0.1.0.

---

# Start coding

1. Working pattern (start coding)

Branch off develop:

`git checkout -b feat/app-skeleton develop`


2. Add minimal skeleton:

`saskan/__init__.py (sets __version__)`

`saskan/cli.py` (argparse/typer entry)

`tests/test_cli.py`

3. Commit, push, open PR → target develop, fill template, self-review.

- Whenever I commit, pre-commit will run its linter-type checks and it will reformat anything that needs it.  Then just `git add` the changes and re-commit. This is the "auto-accept" cycle.

4. Merge via squash when CI is green.

# When we’re ready to ship an RC

```text
make start-release RELEASE=0.1.0
# stabilize; fixes only
make finish-release
# pushes tag v0.1.0; release workflow builds artifacts
```

That’s enough to start writing app code without over-complication. May want to ask ChatGPT to supply a tiny 'cli.py' + 'test_cli.py' scaffold so that the first PR is trivially green.

---

# git log

Nice, clean, easy version that graphically shows squash merges:

```bash
git log --oneline --graph --decorate --all
```

For pro goodness:

```bash
git config --global alias.lg "log --oneline --graph --decorate --all"

# then just type:
git lg
```

---

# git fetch

git fetch --prune --tags

Breaks down as:

git fetch → updates your local knowledge of what exists on the remote (branches, tags).

--tags → explicitly fetches tags as well (not just branches).

--prune → removes (prunes) any local references that no longer exist on the remote.

👉 Put together:

If you’ve deleted tags (or branches) on the remote (origin),

Running git fetch --prune --tags will clean up your local refs so they match.

---
