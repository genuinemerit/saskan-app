ABOUT DOCUMENTATION

Sphinx is overkill. GitHub renders `.md`/`.rst` well, gives you decent navigation, and you can keep everything in-repo without a docs toolchain. Add a site generator only when you *need* one.

This means I can use .md (markdown) and don't need to use .rst (re-structured text).

# Choose based on needs

Use **just GitHub + Markdown** if you:

* Have a small codebase and a handful of pages (README, CONTRIBUTING, RELEASE, a few guides).
* Don’t need API auto-docs, cross-references, or custom theming.
* Want zero build pipeline for docs.

Use **MkDocs** (with Material) if you:

* Want a simple, attractive docs site with search and sidebar, minimal config.
* Prefer Markdown, not reST.
* Don’t need heavy Sphinx extensions.
* Want trivial GitHub Pages publishing.

Use **Sphinx** if you:

* Need Python API autodoc/autosummary (pulling docstrings), intersphinx cross-linking, or nitpicky link checking.
* Have complex doc structures (many sections, indices, reference manuals).
* Already invested in reST and Sphinx extensions.

# Recommended “careful turtle” path

**Phase 0 (now): keep it simple**

* Put core docs in Markdown in the repo root and `docs/`:

  * `README.md` (top-level overview, quickstart)
  * `CONTRIBUTING.rst` is fine, but consider converting to `.md` for consistency
  * `RELEASE.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
  * A few topic pages in `docs/` (architecture.md, style.md, faq.md)
* Link them together via the README.

**Phase 1 (only if/when you want a site) — pick MkDocs**

* Add `mkdocs.yml` + `docs/` (Markdown).
* Publish via GitHub Pages using a tiny GitHub Action.
* Convert any `.rst` to `.md` (keeps the stack uniform).

**Phase 2 (only if you need Python API docs/cross-refs) — Sphinx**

* Keep existing Markdown guides; Sphinx can read Markdown via `myst-parser`.
* Add API autodoc and intersphinx.
* Publish to Pages with a Sphinx build Action.

# Minimal configs (for later reference)

**MkDocs (Material)**

```yaml
# mkdocs.yml
site_name: Saskan App Docs
theme:
  name: material
nav:
  - Home: index.md
  - Contributing: contributing.md
  - Release: release.md
  - Architecture: architecture.md
```

**Sphinx (bare minimum)**

```python
# docs/conf.py
project = "Saskan App"
extensions = ["myst_parser"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
html_theme = "sphinx_rtd_theme"
```

# Practical advice for a solo repo today

* Standardize on **Markdown** for now. GitHub is your doc host.
* Keep a single `docs/` folder and link from the README.
* Defer any site generator until you feel pain: “I can’t find pages,” “I need API docs,” or “I want a real sidebar/search.”

If you want, I’ll convert the `.rst` snippets we made into `.md` and lay out a minimal `docs/` tree you can drop in immediately.

