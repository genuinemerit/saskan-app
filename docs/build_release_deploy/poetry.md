# Poetry 

## pyproject.toml notes

Flat layout: Keep __init__.py in each package dir you want importable (core, engine, …).

CLI: Create ui_cli/manage.py with a cli() entrypoint (Typer or Click).

DB: Default to SQLite via SQLAlchemy; enable Postgres with poetry install --with postgres.

Dev toolchain: black + isort + ruff + pytest + coverage + mypy wired via [tool.*] stanzas.

Heavy libs: Install on demand via extras, e.g., poetry install --with analytics.

If you later choose an async stack or a server framework, we’ll add the appropriate deps/extras and (optionally) a server extra.

## poetry basics

Here's how it works:

Creating a Virtual Environment:
When you run poetry install, it will create a virtual environment specifically for your project, install all the dependencies listed in your pyproject.toml, and handle isolation between your projects.

You don't need to manually create a virtual environment as you would with python -m venv, or through conda.

Running Your Project:
Poetry automatically uses the virtual environment when running your project, so you don’t need to manually activate it like you would with source venv/bin/activate or conda activate.

To run a command inside your Poetry-managed environment, you can just use:

poetry run <command>


Virtual Environment Location:
By default, Poetry stores the virtual environments in a cache location (not inside your project directory) to keep things clean, but you can configure it to create the environment inside your project folder if preferred.

Environment Management:
You can check which virtual environment Poetry is using with:

poetry env info


And you can manually activate it if you ever need to, using:

poetry shell

Key Benefits:

Poetry simplifies environment management by automatically handling it.

No need for additional tools like conda, mamba, or venv since Poetry does everything with a single command.

It also locks your dependencies with poetry.lock, ensuring reproducibility across different machines.

In short, Poetry offers a streamlined solution, so you can skip using conda/mamba unless you have very specific reasons to use them (like managing multiple Python versions). It's a more "Pythonic" solution and perfect for smaller-to-medium-sized projects .

---

## poetry refresh

Steps to “nuke and pave”

Check if Poetry sees an environment for this project

poetry env list


→ You’ll see something like:

/home/user/.cache/pypoetry/virtualenvs/saskantinon-abc123-py3.12 (Activated)


Remove the existing env

poetry env remove python


If multiple interpreters show up, you can pass the exact one:

poetry env remove /home/user/.cache/pypoetry/virtualenvs/saskantinon-abc123-py3.12


Confirm it’s gone

poetry env list


→ Should be empty for this project.

Reinitialize

From the project root (where pyproject.toml lives):

poetry install


This will:

Resolve dependencies from your new pyproject.toml

Create a new virtual environment

Generate a fresh poetry.lock

Activate the new env

Either:

poetry shell


Or, if you prefer the explicit path approach:

source $(poetry env info --path)/bin/activate

Notes

Since you’re treating this as an application, you should commit the new poetry.lock to the repo.

If you want to rebuild again later, just repeat steps 1–3 and run poetry install fresh.

---

## poetry shell

When you do:

poetry shell


You're activating the virtual environment Poetry created — which contains:

Your app dependencies (Flask, SQLAlchemy, etc.)

Dev/testing tools (pytest, pytest-flask, etc.)

The correct Python version (in your case, 3.12.x)

Alternative:

If you don’t want to activate the shell, you can also run:

poetry run pytest


Which runs the command inside the virtualenv without needing to activate it manually.

🧪 TL;DR: You can choose either:

✅ Activate shell: poetry shell → then pytest

✅ One-liner: poetry run pytest

---

Now, to use poetry shell...

As of Poetry 2.0, the poetry shell command is no longer included by default. Instead, the Poetry team recommends using the new:

poetry env use ...
poetry env activate ...


This aligns with their push for clearer, more modular tooling — but it does change workflows many people relied on.

✅ Recommended: Use env activate

You can do:

poetry env activate $(poetry env info --path)/bin/activate


Or, if you're just trying to use the correct Python inside your terminal session:

source $(poetry env info --path)/bin/activate


That gives you a shell with the Poetry environment active — the closest replacement for poetry shell.

🔁 Optional: Restore poetry shell

If you want the old poetry shell behavior back, you can install the shell plugin:

poetry self add poetry-plugin-shell


After that, poetry shell will work exactly as it did before.

🧠 My Advice

If you’re comfortable using `source $(poetry env info --path)/bin/activate`, stick with that — it’s more transparent and aligns with other Python tooling.

But if you liked poetry shell and want minimal typing, go ahead and add the plugin.

---

## poetry activate

Usage

Save a shell script to do the activate as tools/poetry_activate (or at repo root).

Make it executable: `chmod +x tools/poetry_activate`.

Important: use source so it affects your current shell:

`source tools/poetry_activate`


Could also make a short alias (e.g., `alias pa='source tools/poetry_activate'`) you could add to your .bashrc or .zshrc so you don’t even have to type the filename

---

## poetry deactivate

Is there any need to explicitly deactivate or exit from an activated poetry venv? 

ChatGPT said:

No special ceremony needed.

If you used poetry shell:
Just type exit or hit Ctrl-D → it drops you back to your system shell.

If you used source $(poetry env info --path)/bin/activate (or your helper script):
Use the standard `deactivate` command (built into venvs) → that resets PATH and related vars.

Either way:

Nothing persists in the project — the env just sits on disk under Poetry’s cache (~/.cache/pypoetry/virtualenvs/…).

You don’t need to deactivate before switching to another project. Running poetry run … or poetry shell in a different project auto-activates the correct env.

So: deactivation is only about cleaning up your current shell session, not about Poetry state.

## poetry refresh (install)

Don’t need to blow away the venv every time we edit `pyproject.toml`.

### Typical cases

* **Changed metadata only** (name, description, classifiers, package layout, includes):
  → Just keep working. No need to touch the venv, since installed deps haven’t changed.

* **Added/removed/updated dependencies**:
  → Run:

  ```bash
  poetry install
  ```

  This syncs the venv with the updated dependency list and refreshes `poetry.lock`.

* **Changed dev tool config only** (black/isort/pytest/mypy settings):
  → No action needed; those live in config, not in the environment.

* **Big cleanup / want to be sure**:

  ```bash
  poetry lock --no-update
  poetry install
  ```

  Ensures lockfile is regenerated and venv is synced.

Don’t need to deactivate.

`poetry install` works on the project’s virtualenv on disk, not on your currently active shell. Whether you’re “inside” the venv (`poetry shell` / `source …/activate`) or outside, the command does the same thing: it syncs that environment with your `pyproject.toml` and `poetry.lock`.

**Best practice:**

* Stay in your normal shell (no active venv) when running dependency management commands (`poetry install`, `poetry add`, `poetry update`).
* Drop into `poetry shell` (or use `poetry run …`) only when you want to execute code.

That way you avoid confusing yourself with nested or mismatched environments.


---

### Example

I only **renamed the project/package and adjusted package paths** in `pyproject.toml`:

* No need to nuke/re-init.
* Just run `poetry install` once, to let Poetry check that metadata + lock are in sync.



