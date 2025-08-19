# Plan: your first clean PR (adds `hello` CLI)

## 0) One-time GH setup (quick)

1. Ensure branches exist:

```bash
git checkout -b develop
git push -u origin develop
```

---

Notes on Step 1 
- 🗹 git add .
- git commit -m "..." threw a pre-commit error on one file, so
  - did 🗹 git add . again to pull in the fix
  - then could do the commit 🗹 
- git push -u origin develop -->
remote: error: GH006: Protected branch update failed for refs/heads/develop.
remote: 
remote: - Changes must be made through a pull request.
To github.com:genuinemerit/saskan-app.git
 ! [remote rejected] develop -> develop (protected branch hook declined)
error: failed to push some refs to 'github.com:genuinemerit/saskan-app.git'

which is expected due to previously having done Step 2! 

So, went into GitHub. Turned off "require PR".

still failed, same message (oddly). 

LOL! What was odd is that I had not SAVEd changes to "Branch protection rules" ... when I did then

 🗹 git push -u origin develop

---

2. In GitHub → *Settings → Branches*

   * Protect **main** (and optionally **develop**): require PR, require status checks (`lint`, `typecheck`, `test`, `CI`), allow **squash** merge only.

---

Notes on Step 2

Turned the branch protection rules back on for develop.

For the "require status checks"... we have the workflows, now we need to..

1. Find the exact workflow names

Go to your repo on GitHub → Actions tab.
Each workflow (from each .yml) has a display name at the top of the YAML:

name: Lint
on: [push, pull_request]


For example, your repo likely has:

Lint

Typecheck

Test

CI (the one that runs on develop)

These show up (along with others) on the left-hand side of the Actions page


Those names are what GitHub will offer in the branch protection UI.

2. Add them to branch protection

Go to Settings → Branches → Branch protection rules → edit the one for develop.

Check “Require status checks to pass before merging”.

> Turned that on.

You’ll get a list of checkboxes → pick the ones matching your workflows (e.g., Lint, Typecheck, Test, CI).

> This list did not show up. 

(see note below about Rulesets)

Save.

👉 From then on, every PR into develop must have all those checks green before the Merge button lights up.

3. (Optional, recommended) Disallow merging without them

Still in that same rule:

Check “Require branches to be up to date before merging” (ensures the PR branch is rebased/merged on latest develop so CI isn’t stale).

> This is ticked on now.

Allow only Squash merge (to keep history clean).

This is done in GitHub -> Settings -> General -> Pull Requests.

4. Alternative: Rulesets (new GitHub feature)

If your repo has Settings → Rules → Rulesets, you can do the same there. Rulesets are more powerful (org-wide, multi-branch). Same idea: add required status checks by name.

This worked. Add checks --> type in what you are looking for, pick the one from "Github Actions"

named the ruleset to "Branch Protection - develop" and set it to Active

---


## 1) Create a focused feature branch

```bash
git checkout develop
git pull
git switch -c feat/cli-hello
```

## 2) Add the minimal feature (+ test)

### a) Add a `hello` command  🗹

Create `saskan/ui_cli/commands/greet.py`:

```python
# saskan/ui_cli/commands/greet.py
from typing import Optional
import typer
from rich.console import Console

console = Console()

def hello(name: Optional[str] = typer.Option(
    None, "--name", "-n", help="Optional name to personalize the greeting."
)) -> None:
    who = name or "Saskan Lands"
    console.print(f"Hello {who}!")
```

Wire it into the Typer app by editing `saskan/ui_cli/manage.py`:

```python
# saskan/ui_cli/manage.py
import typer
from saskan.ui_cli.commands.greet import hello

app = typer.Typer()

@app.command("hello")
def hello_cmd(name: str | None = typer.Option(None, "--name", "-n")):
    """Print a friendly greeting."""
    hello(name)

def cli():
    app()
```

> Note: your `pyproject.toml` already maps a console script:
>
> ```
> [tool.poetry.scripts]
> saskan = "saskan.ui_cli.manage:cli"
> ```
>
> If Typer isn’t pinned yet, add it in step 3.

### b) Add tests (pytest)  🗹

Create `saskan/tests/test_cli_hello.py` (and the package dir):

```bash
mkdir -p saskan/tests
```

```python
# saskan/tests/test_cli_hello.py
from typer.testing import CliRunner
from saskan.ui_cli.manage import app

runner = CliRunner()

def test_hello_default():
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello Saskan Lands!" in result.stdout

def test_hello_named():
    result = runner.invoke(app, ["hello", "--name", "Phoenix"])
    assert result.exit_code == 0
    assert "Hello Phoenix!" in result.stdout
```

## 3) Ensure deps + hooks  🗹

(Only if needed; safe to run regardless.)

```bash
poetry add typer[all] rich
poetry install
poetry run pre-commit install
```

## 4) Run the full gate locally 🗹

```bash
# Quick smoke:  🗹
poetry run saskan hello
poetry run saskan hello -n Phoenix

---

Notes 

(saskan-py3.12) saskan-app$ saskan hello
Usage: saskan [OPTIONS]
Try 'saskan --help' for help.
╭─ Error ─────────────────────────────────────────────────────────────────────────────────────────────╮
│ Got unexpected extra argument (hello)                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
(saskan-py3.12) saskan-app$ saskan
Hello Saskan Lands!
(saskan-py3.12) saskan-app$ saskan -n Phoenix
Hello Phoenix!
(saskan-py3.12) saskan-app$ 

There was a problem found in the smoke test. Something about
how Typer.main ("root") inserts a callback that overrides our attempt
at defining a subcommand named `hello`.

As a result, typing just `saskan` executed the greeting CLI
interaction, but `saskan hello` failed. ChatGPT eventually
figured it out and made a modification to manage.py.
Evidently the combo of the `no_args_is_help=True` param and
defining an "empty" @app.callback() is what finally fixed it.

ChatGPT also added the execution of app() from "__main__".

```python
import typer
from saskan.ui_cli.commands.greet import hello

app = typer.Typer(help="Saskan CLI", no_args_is_help=True)  # show help if no subcommand


@app.callback()
def main():
    """Saskan CLI."""
    # No params here → no root options leak into help
    pass


# Register subcommand
app.command("hello")(hello)


def cli():
    app()


if __name__ == "__main__":
    app()
```

Clean smoke test result:

```bash
(saskan-py3.12) saskan-app$ saskan hello
Hello Saskan Lands!
(saskan-py3.12) saskan-app$ saskan hello -n Dave
Hello Dave!
(saskan-py3.12) saskan-app$
```

---

# Repo quality checks:
make lint
make type
make test

# Or all at once:
make check

---

Notes:

- Trying each of them just for the experience.

```bash
(saskan-py3.12) saskan-app$ make lint

==> isort

==> --check-only
poetry run isort . --check-only
ERROR: /home/dave/Dropbox/GitHub/saskan-app/tests/conftest.py Imports are incorrectly sorted and/or formatted.
ERROR: /home/dave/Dropbox/GitHub/saskan-app/saskan/ui_cli/manage.py Imports are incorrectly sorted and/or formatted.
ERROR: /home/dave/Dropbox/GitHub/saskan-app/saskan/ui_cli/commands/greet.py Imports are incorrectly sorted and/or formatted.
Skipped 1 files
make: *** [Makefile:63: lint] Error 1
(saskan-py3.12) saskan-app$
```

These are lint items so will get auto-fixed on `git add` after the pre-commit runs.

```bash
(saskan-py3.12) saskan-app$ make type

==> mypy
poetry run mypy
Success: no issues found in 44 source files
(saskan-py3.12) saskan-app$
```

For make test, I got an error because pyproject.toml identified the path as `/saskan/tests`, when I actually have them located, by design, at just `/tests`.
(saskan-py3.12) saskan-app$ make test

```bash
==> pytest
poetry run pytest -q
..                                                                                                                                                 [100%]
(saskan-py3.12) saskan-app$
```

Woo-hoo!

Had some small glitches in the Makefile. If I am understanding, when a target
is executing other targets, then the other target names have to be listed on
the same line, right after the colon,
like `check: lint type test`
not on the next line.

To verify what a make target is going to do, `make -n ...`:

```bash
(saskan-py3.12) saskan-app$ make -n check
printf "\n\033[1;34m==> %s\033[0m\n" isort
poetry run isort .
printf "\n\033[1;34m==> %s\033[0m\n" Black
poetry run black .
printf "\n\033[1;34m==> %s\033[0m\n" isort --check-only
poetry run isort . --check-only
printf "\n\033[1;34m==> %s\033[0m\n" Black --check
poetry run black . --check
printf "\n\033[1;34m==> %s\033[0m\n" mypy
poetry run mypy
printf "\n\033[1;34m==> %s\033[0m\n" pytest
poetry run pytest -q

```

```bash
(saskan-py3.12) saskan-app$ make check

==> isort
poetry run isort .
Fixing /home/dave/Dropbox/GitHub/saskan-app/tests/conftest.py
Fixing /home/dave/Dropbox/GitHub/saskan-app/saskan/ui_cli/manage.py
Fixing /home/dave/Dropbox/GitHub/saskan-app/saskan/ui_cli/commands/greet.py
Skipped 2 files

==> Black
poetry run black .
reformatted /home/dave/Dropbox/GitHub/saskan-app/saskan/ui_cli/commands/greet.py
reformatted /home/dave/Dropbox/GitHub/saskan-app/tests/test_cli_hello.py

All done! ✨ 🍰 ✨
2 files reformatted, 13 files left unchanged.

==> isort

==> --check-only
poetry run isort . --check-only
Skipped 2 files

==> Black

==> --check
poetry run black . --check
All done! ✨ 🍰 ✨
15 files would be left unchanged.

==> mypy
poetry run mypy
Success: no issues found in 44 source files

==> pytest
poetry run pytest -q
..                                                                                                                              [100%]
(saskan-py3.12) saskan-app$
```

- Makefile gotcha: target deps (:) vs. shell recipes (indented).

- Lint failures stop the gate: use make fix or make format to auto-correct, then re-run.

- Green path: make check runs format → lint → type → test, and you’re CI-ready.
---

## 5) Commit with a clean history 🗹

Keep it tiny: one or two commits max.

```bash
git add -A
git commit -m "feat(cli): add `hello` command to Typer app"
git push -u origin feat/cli-hello
```

---
Notes on commit..

note to self: don't use back-ticks in commit message texts

```bash
(saskan-py3.12) saskan-app$ git add -A
(saskan-py3.12) saskan-app$ git commit -m "feat(cli): add `hello` command to Typer app"
Command 'hello' not found, but can be installed with:
sudo snap install hello              # version 2.10, or
sudo apt  install hello              # version 2.10-3
sudo apt  install hello-traditional  # version 2.10-6
See 'snap info hello' for additional versions.
check yaml...........................................(no files to check)Skipped
check toml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
check for added large files..............................................Passed
detect private key.......................................................Passed
isort....................................................................Passed
black....................................................................Passed
mypy (poetry)............................................................Passed
[feat/cli-hello 5771a3e] feat(cli): add  command to Typer app
 14 files changed, 671 insertions(+), 12 deletions(-)
 create mode 100644 docs/glossary/fullgate.md
 create mode 100644 docs/glossary/merges
 create mode 100644 docs/meta/linters_and_typechecks.md
 create mode 100644 docs/meta/pytest.md
 create mode 100644 saskan/ui_cli/commands/__init__.py
 create mode 100644 saskan/ui_cli/commands/greet.py
 create mode 100644 tests/conftest.py
 create mode 100644 tests/test_cli_hello.py
(saskan-py3.12) saskan-app$ git push -u origin feat/cli-hello
Enumerating objects: 38, done.
Counting objects: 100% (38/38), done.
Delta compression using up to 8 threads
Compressing objects: 100% (24/24), done.
Writing objects: 100% (24/24), 11.72 KiB | 11.72 MiB/s, done.
Total 24 (delta 9), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (9/9), completed with 9 local objects.
remote:
remote: Create a pull request for 'feat/cli-hello' on GitHub by visiting:
remote:      https://github.com/genuinemerit/saskan-app/pull/new/feat/cli-hello
remote:
To github.com:genuinemerit/saskan-app.git
 * [new branch]      feat/cli-hello -> feat/cli-hello
branch 'feat/cli-hello' set up to track 'origin/feat/cli-hello'.
(saskan-py3.12) saskan-app$
```

---

## 6) Open the PR → `feat/cli-hello` → `develop`

* Use the existing **PR template**.
* Title (Conventional Commits): `feat(cli): add hello command`
* “Testing Evidence”: paste your `make` outputs (OK to summarize).
* Keep scope: 1 feature + 1 test, nothing else.

step-by-step:

Heck yeah—let’s do the PR together. Here’s the exact click-by-click + what to type.

# Step-by-step: open your first PR

1. **Start from GitHub (your repo).** 🗹
   Click **Pull requests**.

2. **Choose how to start the PR.** 🗹

   * If you see the banner “**feat/cli-hello had recent pushes**” → click **Compare & pull request**.
   * Otherwise click **New pull request**.

>> clicked it

. How to phrase in PR

Instead of lumping them under “fix”, you can list multiple commit scopes/types in one PR body:

PR Title (main thing):

feat(cli): add hello subcommand


Body / description:

Also includes:
- fix(cli): correct Typer entrypoint in manage.py
- build(pyproject): correct tests path
- chore(makefile): fix check target order


That way, the squash commit still reads cleanly (main feature), but the PR description records the smaller corrections.

3. **Set branches (important).** 🗹

   * **Base**: `develop`
   * **Compare**: `feat/cli-hello`
     Double-check the arrow shows `genuinemerit/saskan-app:develop ← genuinemerit/saskan-app:feat/cli-hello`.

>> verified (at top of the PR page) that we are pointing the feat branch to the develop branch

4. **Create as a Draft (nice solo workflow).**
   Next to the green button, open the dropdown and choose **Create draft pull request**. (You can mark it “Ready for review” once checks pass.)

>> Changed it to Draft Pull request

5. **Title (Conventional Commits).** 🗹

   ```
   feat(cli): add hello subcommand
   ```
>> title is: feat(cli): add hello command to Typer app


6. **Description — fill your PR template.** If it doesn’t auto-insert, click **“Choose a template”** (if you have multiple) or just paste this structure: 🗹

   * **Summary:** Adds `saskan hello [-n NAME]` CLI subcommand; shows help at root.
   * **Changes:**

     * `saskan/ui_cli/commands/greet.py` – implement `hello`
     * `saskan/ui_cli/manage.py` – Typer app, register subcommand, empty root callback with `no_args_is_help=True`
     * `tests/` – `conftest.py`, `test_cli_hello.py`
     * Makefile – `check` runs format → lint → type → test
     * `pyproject.toml` – confirm `scripts` entry `saskan = "saskan.ui_cli.manage:cli"`
   * **How I tested (evidence):**

     ```text
     poetry run saskan --help   # shows 'hello' as subcommand
     poetry run saskan hello
     poetry run saskan hello -n Phoenix
     make check                 # format/lint/type/tests all green
     ```
   * **Checklist:** 🗹

     * [x] Lint/type/tests pass locally (`make check`)
     * [x] Small, focused PR; includes tests
     * [x] No unrelated changes

7. **Labels / projects / reviewers (optional).** 🗹
   Add a `feature`/`cli` label if you use them. As a solo dev, reviewers are optional.

8. **Create the PR.**🗹
   Click **Create draft pull request** (or **Create pull request** if you skipped draft).

>> On GitHub it shows draft PR submitted

# Let CI run & make it green

9. **Watch checks.**
   On the PR, scroll to **Checks**. You should see the required ones: `ci-pr`, `lint`, `typecheck` (mypy), `test` (pytest).

   * If a check fails, fix locally → `make check` → commit & push to `feat/cli-hello`. The PR updates automatically.
   * If formatting fails: `make format` or `make fix` (pre-commit), then commit/push.

>> several required checks passed right away
>> test and testcheck are pending, seem to be taking a while
>> it shows `push` and `pull_request` in failed state

10. **Keep branch up to date (if required).**
    If GitHub says “Out of date with base branch,” click **Update branch** or do:

    ```bash
    git switch feat/cli-hello
    git fetch origin
    git rebase origin/develop
    git push --force-with-lease
    ```

11. **Mark Ready & merge.**
    When all checks are ✅, click **Ready for review** (if it’s a draft), then use the green **Squash and merge**.

    * Edit the squash commit message to something like:

      ```
      feat(cli): add hello subcommand

      - add `saskan hello [-n NAME]`
      - root shows help; no_args_is_help=True
      - tests for default and named greeting
      ```
    * Click **Confirm squash and merge**.
    * **Delete branch** (GitHub offers a button).

# Post-merge cleanup (local)

12. **Sync your local `develop`, remove the feature branch.**

```bash
git switch develop
git pull
git branch -d feat/cli-hello
```

That’s it—you’ve done the full, grown-up PR flow with protections and required checks. Next time it’ll feel automatic.


CI should run: `lint`, `typecheck`, `test`, and `CI` workflow on **develop** PRs.

## 7) Review → squash-merge → done

* Resolve any feedback.
* Squash-merge into `develop`.
* Release-drafter will update draft notes on pushes to `develop`.

---

## (Optional) Tag a first release when ready

If you want to see your release workflows work end-to-end:

```bash
# From main after promoting develop (later):
git checkout main
git merge --no-ff develop
git push

git tag v0.1.0
git push origin v0.1.0
```

This triggers `release-tag.yml` (build) and `Publish Release (on tag)` to finalize notes.

---

# What this PR exercises (by design)

* Branching & naming (GitFlow-friendly).
* Pre-commit, lint, typecheck, tests (green locally and in CI).
* PR template discipline & small, single-purpose scope.
* Console entry point is validated end-to-end (`poetry run saskan hello`).

If you want, I can turn the snippets above into a ready-to-apply patch next.

