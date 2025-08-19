# Plan: your first clean PR (adds `hello` CLI)

## 0) One-time GH setup (quick)

1. Ensure branches exist:

```bash
git checkout -b develop
git push -u origin develop
```

2. In GitHub → *Settings → Branches*

   * Protect **main** (and optionally **develop**): require PR, require status checks (`lint`, `typecheck`, `test`, `CI`), allow **squash** merge only.

## 1) Create a focused feature branch

```bash
git checkout develop
git pull
git switch -c feat/cli-hello
```

## 2) Add the minimal feature (+ test)

### a) Add a `hello` command

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

### b) Add tests (pytest)

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

## 3) Ensure deps + hooks

(Only if needed; safe to run regardless.)

```bash
poetry add typer[all] rich
poetry install
poetry run pre-commit install
```

## 4) Run the full gate locally

```bash
# Quick smoke:
poetry run saskan hello
poetry run saskan hello -n Phoenix

# Repo quality checks:
make lint
make type
make test

# Or all at once:
make check
```

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

