# Config and env files

Describe the purpose of various standard config and env files

- .python-version
- .env{.example}

## Purpose / Advantage of `.python-version`

The `.python-version` file is a **convention** used by tools like **pyenv**, **asdf**, and some editors/IDEs:

* Declares the **Python version expected** for this project.
* Ensures contributors, CI, and local shells pick the same interpreter.
* Avoids “works on my machine” mismatches if someone is on 3.10 while the project requires 3.12.
* Plays well with Poetry: Poetry itself reads the `python = ">=…"` constraint in `pyproject.toml`, but if you also use `pyenv` or `asdf`, `.python-version` makes them auto-activate the right interpreter when you `cd` into the repo.

Think of it as **pinning the Python runtime** the same way `poetry.lock` pins packages.

---

### What it should contain

A single line with the version string:

```text
3.12.4
```

(or whatever exact Python you standardize on).

* If you want to allow *any* 3.12.x, you’d still put one concrete version in `.python-version`, because `pyenv` needs a specific install target.
* This file doesn’t support ranges (`>=3.12,<3.13`) — that’s for `pyproject.toml`.
* It can also include an alias like `3.12` if your team uses `pyenv global 3.12` pointing to the latest patch.

---

### Summary

* `.python-version` = hint for **pyenv/asdf/IDE**, ensures devs/CI boot into the right Python.
* `pyproject.toml` = authoritative constraint for **Poetry**.
* Together they keep both **runtime** and **dependencies** aligned.

### Purpose of `.env.*` files

`.env` files are simple **key=value** configuration files used to inject environment variables into your app.

They let you:

* Keep **secrets and config** out of code (`DB_PASSWORD`, `OPENAI_API_KEY`).
* Support **different environments** (dev, test, staging, prod) without editing code.
* Work smoothly with tools that auto-load them (`python-dotenv`, `Django`, `Flask`, Docker Compose, GitHub Actions).
* Avoid cluttering your global shell profile with project-specific variables.

---

### Common variants and examples

#### `.env` (default, local development)

```env
# Flask/Django dev settings
DEBUG=true
DATABASE_URL=sqlite:///./saskan_dev.db
OPENAI_API_KEY=sk-xxxx
```

#### `.env.local` (overrides for your personal machine)

```env
DATABASE_URL=postgresql://me:secret@localhost/saskan_dev
```

Often **gitignored**, so each dev can set their own.

#### `.env.test` (used when running tests)

```env
DATABASE_URL=sqlite:///:memory:
DEBUG=false
```

#### `.env.staging` (deploy preview / pre-prod)

```env
DATABASE_URL=postgresql://saskan_staging_user:staging_pass@staging-db/saskan
DEBUG=false
```

#### `.env.prod` (production deployment)

```env
DATABASE_URL=postgresql://saskan_prod_user:${PROD_DB_PASS}@prod-db/saskan
DEBUG=false
```

Normally injected via CI/CD or secrets manager rather than stored in git.

---

### Best practices

* **Never commit secrets** (`.env`, `.env.local`, `.env.prod`) — add them to `.gitignore`.
* **Commit sample templates** (`.env.example`, `.env.template`) so others know which variables are expected:

  ```env
  DATABASE_URL=<fill-me-in>
  OPENAI_API_KEY=<your-api-key>
  ```
* Use **different suffixes** (`.env.test`, `.env.prod`) if your tooling auto-loads based on environment.
* Document in `CONTRIBUTING.md` which `.env.*` files are required and how to populate them.

---

### Summary

`.env.*` files externalize runtime config. You keep a **committed template** to guide contributors, but your **real secrets** live in local `.env` files or CI/CD secrets — never in the repo.

See: saskan-app/.env.example for a generic example tailored to the Saskan app

Notes

Commit the example file ONLY (not the real ones) so contributors/CI know which variables are expected.

Never commit your real .env with secrets.

Use SQLite as the default (no setup friction), and document Postgres as the production option.

For production, override in .env.prod or via CI/CD secret management.

---

# .pre-commit-config.yaml

## Purpose

.pre-commit-config.yaml defines Git hooks run before a commit (and optionally on push). It enforces code quality automatically—formatting, linting, type checks—so what lands in main already matches your standards. In a Poetry setup, we’ll either (a) let pre-commit manage tool envs, or (b) call tools via poetry run to use your project’s pinned dev deps. Ours uses both: pre-commit-managed for formatters/linters, and a local hook invoking `poetry run mypy` so it uses your project config and stubs.

See:  saskan-app/.pre-commit-config.yaml

## Notes / rationale

- Order matters: isort → black → ruff keeps imports sorted, code formatted, then linted. (You can eventually let Ruff handle import sorting/formatting and drop isort/black; for now we keep the classic trio.)

- mypy via Poetry: the local hook runs poetry run mypy, ensuring it uses your pinned version and the config in pyproject.toml.

- exclude: avoids linting binary docs/assets; adjust as the repo grows.

- pre-push tests: leave commented until the test suite is consistently fast.

## Common uses

```bash
poetry add --group dev pre-commit
poetry run pre-commit install
poetry run pre-commit run --all-files
```

Then w can wrap these into a Makefile (make lint, make format, make type, make check) so contributors don't need to recall the long commands.

# .editorconfig

## Purpose of .editorconfig

.editorconfig is a cross-editor configuration file that enforces consistent coding style across IDEs and editors. It doesn’t replace formatters like Black, but it prevents nuisance diffs from things like tabs vs. spaces, line endings, and final newlines. Many editors (VSCode, PyCharm, Vim, etc.) support it natively or via plugin.

See:  saskan-app/.editorconfig

Notes

- Python: 4-space indents (PEP 8).

- Config files: 2 spaces for YAML/TOML/JSON, aligns with ecosystem norms.

- Markdown: don’t auto-trim spaces, since they can be meaningful for line breaks.

- Makefile: tabs required by make.

- Line length set to 100 across editors; authoritative values still live in pyproject.toml for Black/isort/Ruff.

- If an editor disagrees with formatters, the formatter wins on commit (via pre-commit).

This file lives in repo root so all editors honor the same baseline style.

# CODEOWNERS

CODEOWNERS is simple once you see what it does.

---

## Purpose of CODEOWNERS

* It’s a special file (`.github/CODEOWNERS`) that tells GitHub:
  *“Whenever a PR touches these paths, request reviews from these people/teams.”*
* It doesn’t block merging by itself — but if branch protection is set to **“Require review from Code Owners”**, then at least one of those owners must approve before merge.
* For solo mode: you can set yourself as the owner so all PRs auto-request you (nice for discipline and history). Later, if you add collaborators, you can divide responsibility by directory.

---

## Format

Each line: `<pattern> <owner(s)>`

Examples:

```text
# Everything in the repo
*       @phoenix-quinn

# Docs go to a docs team
/docs/  @phoenix-quinn @docs-team

# Python package code to a dev team
/saskan/ @phoenix-quinn @backend-team
```

Owners can be:

* Individual GitHub usernames (`@phoenix-quinn`)
* Teams within an org (`@myorg/devs`)

---

## What to do now (solo)

Add a minimal file at `.github/CODEOWNERS`:

```text
# Default owner for all files
*   @your-username
```

Replace `@your-username` with your actual GitHub handle (which is `@genuinemerit`)

That way:

* Every PR auto-assigns you as reviewer.
* In branch protection you can later tick **Require review from Code Owners** to enforce it (today you can leave that off if you don’t want the extra click).

---

👉 For you right now: just put the file in place with your username. Later, when you grow the project, you can slice responsibility by directories (e.g. `/docs/`, `/infra/`, `/saskan/`).

Would you like me to show you the **exact GitHub browser steps** to add CODEOWNERS (since you can’t create `.github/CODEOWNERS` through the UI directly), or are you comfortable just making the file in your repo and committing it?

# RELEASE.md

Purpose of RELEASE.md

A RELEASE.md is a lightweight, human-readable guide to the release process for your repo.

It complements automation (release-drafter, Makefile release, CI/CD workflows).

Documents how maintainers should cut, tag, and publish a release.

Ensures consistency when more contributors join.

Helps “future you” remember the agreed steps in 6 months.

It’s not a changelog (that’s CHANGELOG.md). Instead, it’s a playbook for producing a release.

See: saskan-app/RELEASE.md



