# monkeypatch

## What `monkeypatch` can do

* **Patch environment variables** (`os.environ`).
* **Replace attributes** (functions, classes, constants) on modules.
* **Modify `sys.path` or `sys.modules`** for import tricks.
* **Undo itself** automatically after the test ends.

---

### In your i18n tests

Example:

```python
def test_lang_rejects_unknown(monkeypatch):
    monkeypatch.setenv("SASKAN_LANG", "xx-YY")
    assert lang() == "en-US"
```

Here’s what happens:

1. `monkeypatch.setenv("SASKAN_LANG", "xx-YY")` temporarily inserts that key/value into `os.environ`.
2. You call `lang()`, which reads `os.getenv("SASKAN_LANG", ...)`.
3. After the test finishes, pytest restores the environment to its original state — no risk of polluting other tests or your shell.

Another:

```python
monkeypatch.delenv("SASKAN_LANG", raising=False)
```

\= “pretend that `SASKAN_LANG` isn’t set.”

---

### Why not just use `os.environ`?

You could write:

```python
os.environ["SASKAN_LANG"] = "xx-YY"
```

But then you’d have to remember to clean it up manually at the end of the test. If you forget, later tests may fail because they see a different environment.

`monkeypatch` takes care of cleanup automatically. That’s why pytest provides it.

---

### Broader use

Besides env vars, you can patch any symbol:

```python
def test_fake_home(monkeypatch):
    monkeypatch.setenv("HOME", "/tmp/fakehome")

def test_replace_function(monkeypatch):
    monkeypatch.setattr("saskan.infra.i18n.lookup.lang", lambda: "es-ES")
    # Now calls to lang() return "es-ES"
```

---

✅ In short:

* **`monkeypatch` = pytest’s safe “temporary override” tool.**
* Perfect for tests where you want to simulate different environment settings or replace functions/constants.
* All changes are reverted automatically after the test.
