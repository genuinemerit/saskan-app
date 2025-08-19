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

## 5) Commit with a clean history

Keep it tiny: one or two commits max.

```bash
git add -A
git commit -m "feat(cli): add `hello` command to Typer app"
git push -u origin feat/cli-hello
```

## 6) Open the PR → `feat/cli-hello` → `develop`

* Use the existing **PR template**.
* Title (Conventional Commits): `feat(cli): add hello command`
* “Testing Evidence”: paste your `make` outputs (OK to summarize).
* Keep scope: 1 feature + 1 test, nothing else.

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

