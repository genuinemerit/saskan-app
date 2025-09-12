# Linters and Typechecks

Question -- When I get errors from the linter (make lint or make check) do I need to go fix them manually now, or just wait to run pre-commit and then accept all the fixes with `git add .`?

## 1. **Auto-fixable issues (formatting, imports, whitespace, etc.)**

* Tools like **black**, **isort**, **trim trailing whitespace**, **end-of-file fixer** will happily rewrite files for you.
* If you run `make lint` (or `pre-commit run --all-files`) locally, they’ll auto-apply the changes.
* Then you just stage them:

  ```bash
  git add .
  git commit --amend  # or new commit if you prefer
  ```

* This is the smooth “let the tools do the fixing” path.

## 2. **Non-auto-fixable issues (logic, style, typing, etc.)**

* Some checks (like **flake8 errors**, **mypy type errors**, or certain lint rules) can’t be auto-fixed.
* For those, you’ll have to change the code manually until the linter/typechecker is happy.

## 3. **In practice (good habit)**

* Run `make check` before committing → it runs the full gate (lint, typecheck, tests).
* If it fails on auto-fixable stuff, just re-run `pre-commit run --all-files` and stage the changes.
* If it fails on non-auto-fixable stuff, fix the code manually.
* Then re-run `make check` to confirm everything is green.

---

👉 Summary:

* **Auto-fixable?** Pre-commit will fix it → just `git add .`.
* **Not auto-fixable?** You have to fix it yourself.

Would you like me to add a tiny “decision flow” diagram/checklist you could drop into your skunkworks doc — like *“Linter fails → auto-fix? yes → re-add; no → fix manually”*?
