# environment variables

## Using **.env + `override=True`**

### Pros

* Self-contained: everything the app needs lives in one place (repo root). Easy for new devs — clone repo, run, it “just works.”
* Predictable: you know exactly which variables are being used because `.env` is right there.
* Good for **prototypes** and **local dev** — less friction, fewer “it works on my machine” mysteries.

### Cons

* Side effect at import time: simply importing your package loads `.env`, potentially overwriting values already set in the shell (or by the OS, or in CI/CD).
* Surprising for ops: if ops set `SASKAN_HOST` in the environment, but `.env` has a different value, `.env` wins silently. That breaks the principle “explicit env > defaults.”
* In production you usually *don’t want secrets in the repo* (even in `.env` if it gets copied around). CI/CD and container orchestration usually inject envs.

---

## Using **shell environment vars** (the “12-Factor App” model)

### Pros

* Clear precedence: the OS/process environment is the source of truth.
* Works with container orchestrators, systemd, CI/CD, Heroku, Kubernetes, etc. — all assume you provide secrets/config this way.
* Safer: secrets don’t live in the repo. You can rotate them without touching code.

### Cons

* More setup overhead for a new dev: they must export vars or source a script.
* Less discoverable: someone has to know what vars exist and their defaults (hence the need for docs or `.env.example`).
* Easy to misconfigure if you forget to export.

---

## Why to **move `.env` loading out of `__init__.py`**

* The risk isn’t `.env` itself — it’s the **global side effect on import** with `override=True`.
* Having `saskan/__init__.py` load `.env` means *any* tool that imports `saskan` (say, your test runner, or even a linter) will trigger dotenv and overwrite whatever environment was already set. That can lead to spooky bugs.
* The safer pattern is: load `.env` **only at entrypoints** (CLI main, dev server bootstrap). Then you get dev-friendly defaults, but production stays in control.

---

## Balanced approach many projects use

* Keep a `.env` for local dev, checked in as `.env.example` (no secrets).
* On dev machines, run `dotenv` or have our CLI load it at startup.
* On prod, **never load `.env`**; let the system environment be authoritative.
* Always treat `override=False` unless we explicitly want the `.env` to win.

---

### TL;DR

* For **prototypes/dev convenience**: `.env` + `load_dotenv()` is fine.
* For **production/ops sanity**: prefer OS/env injection; don’t let `.env` override.
* Recommendation to keep it out of `__init__.py` is to avoid **hidden global side effects** — not because `.env` is bad, but because we want control over *when* and *whether* it’s loaded.

---

To list all of your environment variables on macOS or Linux from the Terminal command line, you can use the following command:

```bash
printenv
```

This command will display all environment variables currently set for your shell session.

Alternatively, you can use:

```bash
env
```

Both commands will show a list of environment variables, but `printenv` is more focused specifically on printing the environment variables.

If you want to check a specific environment variable, you can use:

```bash
echo $VARIABLE_NAME
```

For example, to check the `PATH` variable:

```bash
echo $PATH
```
