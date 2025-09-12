# Notes on "first_splash" features

architecture:

- Determine how large graphic (and sound and video) files are handled.
  - New ADR: 0015 Asset Management & Distribution
- Determine how UX components interact.
  - New ADR: 0016 UX shells and interactions

docs:

- Clean up many /docs and other markdown files
  - cleaned up all markdown formatting
  - renamed files with proper suffixes, some of the file names
  - changed `meta` to `reference`
  - moved detailed technical references under `reference`
  - renamed `skunkworks` to `feature_design`
  - moved `adr` and `diagrams` under `architecture`
  - moved `glossary` under `reference`
  - created `test_results` under `design`

chore:

- Clean up CODEOWNERS config, removing unnecessary folder-level owners
- Clean up the pull request templates
  - Maybe add more of them? No, that would be overkill
  - Get clarity on PULL_REQUEST_TEMPLATE/feature.md vs. pull_request_template.mdf
    - Really only need one. GitHub uses the standalone by default, so keep
      that one. Verify that it has a recommendation to choose a labels.
    - Edited, cleaned up the standalone pull request template.

tooling:

- Create a "features request" issue
- Determine if issues templates need to be created
  - Verify .github/ISSUE_TEMPLATE/feature_request.yml
  - Other types of issue templates needed, associated with the issue labels?
  - No, feature_request, bug_report and config (disallows blank issues) are sufficient
  - Updated, simplified feature_request and bug_report to reference project labels and terminology
  - Updated config to reference README and not the wiki

- In GitHub:
  - Discussion area, modified/added categories.
  - Enabled Private vulnerability reporting so people can report issues privately
    - Settings → Code security and analysis → Vulnerability reporting
  - Enabled secrets scanning alert
  - Enabled Code scanning. Default(CodeQL). Don't block PRs yet. Just learn how it works.
    - Did this in code, not on the site.  Created a new file:  .github/workflows/codeql.yml
    - It is setup to run weekly, on Mondays at 6 AM UTC
  - On Issues tab, learned to do searches on PRs and issues; set a Milestone (release v0.1.0);
    create "Views" (saved searches) - but that seems a little wonky.

refactor:

- Structure the approach to naming tags used in i18n labels. See ADR0014.
  - **Key Format:** Lowercase, dotted path (e.g., `msg.handshake.welcome`).
  - Review saskan/data/locales/en-US and /es-ES
    - Identify items not using the lowecase, dotted path pattern for keys
  - In the general code base (mainy ui_cli I think):
    - Find places (lookup calls) that mistakenly reference en-EN rather than en-US and fix them
    - Identify all text displays (not messages) that are not yet translated
      - Set up proper tags and values for them
    - Modify all tags that don't currently follow the lowercase, dotted path pattern for keys and fix them

- Turn off echo of log messages to server console

feature:

- Implement fixes to logging per ADR 0009, i.e, prefixes on types of messages
- Implement call to AI models to generate some game "splash" images

  - Expand on the `huge_barbican.py` example
    - Determine where `draw` modules belong in the project tree
    - Reviewing stale `bow_data` project may help with understanding object cold store options
    - Codify storage of image files. OK to have them in the project tree?
  - Integrate display of the graphics into presentation of a splash screen

- Extend the `connect` CLI to trigger presentation of a splash screen

  - Continue to follow architecture decisions on message contracts (ADR0011), etc.
  - Simple first integration of PyGame and PySide:

    - Use PyGame to display an image

      - Client can make choices about what to display:

        - CLI option to use a stored image or generate a new one
        - CLI option to see a slideshow or a single image

    - Build out intial PySide framework/wrapper
      - File -> Quit
      - Client/user requests session end by selecting Quit
      - Consider a small side-project to get PySide chops in order

Created 8 issues dealing with the refactoring and new feature coding solutions outlined above.
Didn't bother to create issues for the architecutre, tooling and chore items.

---

## Overview - "First Splash" Feature Design

### Goals

- Establish a basic splash screen feature using PyGame and PySide, focusing on clear separation of concerns.
- Implement initial logging improvements and AI-generated splash images.

### Non-Goals

- Avoid complex asset pipelines and cross-embedding of PyGame inside PySide for this version.

## Branching & Documentation

- **Branch:** `feat/first_splash`
- **ADRs Referenced:**
  - ADR-0009: Logging prefixes
  - ADR-0011: Message contracts
  - ADR-0014: i18n tag naming
- **New ADR Stub:** `ADR-0016 First Splash UX shell`

## Work Items

### Documentation

- Streamline `/docs/*` and update templates. Add a "First Splash: Dev Quickstart" section in the README.

### Chores

- Rename `skunkworks/` to `feature_design/`.
- Clean up `CODEOWNERS`.
- Unify PR templates, preferring `/PULL_REQUEST_TEMPLATE/feature.md`.

### Refactoring

- Implement i18n tag scheme per ADR-0014.
- Disable server console echo for logs; route through logger only.

### Features

1. **Logging Enhancements (ADR-0009)**
   - Implement log prefixes like `[SRV:INFO]`, `[CLI:WARN]`, etc.
   - Configure via `SASKAN_LOG_LEVEL` and `SASKAN_LOG_STYLE`.

2. **AI Splash Generator Hook**
   - Add CLI options for splash generation with fallback to stored images if necessary.

3. **Splash Screen Integration**

   - Extend `connect` command to include splash options:

     ```bash
     saskan connect --splash [--renderer=pygame|pyside] [--image PATH] [--generate] [--slideshow] [--headless]
     ```

   - Implement handshake messages as per ADR-0011.

4. **Renderer Modules**
   - **PyGame Renderer:** Display images with minimal input handling.
   - **PySide Shell:** Basic window with File → Quit menu.

5. **Server Admin Controls**
   - Environment variables for splash mode and directory settings.

## Minimal File Layout

```text
saskan/
  cli/connect.py                  # Adds --splash option
  core/contracts.py               # Session request/welcome dataclasses
  core/logging.py                 # Log prefixes per ADR-0009
  gui/__init__.py
  gui/pygame_splash.py            # PyGame renderer
  gui/pyside_shell.py             # PySide shell
  i18n/en.yaml                    # i18n tags
tests/
  test_cli_connect_splash.py
  test_contracts_session.py
  test_logging_prefixes.py
feature_design/
  first_splash.md                 # Design notes + ADR links
docs/
  first_splash_quickstart.md
```

## i18n Tags (Per ADR-0014)

- `ui.splash.title`
- `ui.splash.subtitle`
- `ui.menu.file`
- `ui.menu.quit`
- `ui.splash.hint.quit`

## Acceptance Criteria

- `saskan connect --splash` opens the selected renderer.
- PySide renderer offers a File → Quit menu that exits cleanly.
- Headless mode logs a message and skips GUI.
- Logging shows ADR-0009 prefixes.
- Contracts match ADR-0011 schema tests.

## Test Plan

### Unit Tests

- Validate serialization of `request_session`/`welcome`.
- Check logging prefix format and level routing.
- Test CLI parsing for various flag combinations.

### Integration Tests (Tagged `gui`)

- Simulate PyGame and PySide interactions and assert correct behavior.

## Risks & Mitigations

- **Event Loop Contention:** Keep renderers separate to avoid conflicts.
- **Headless CI:** Use `--headless` to skip GUI tests by default.
- **PySide Footprint:** Lazy import to prevent errors if not installed.

## Discussion Summary

- **Renderer Separation:** Choose one renderer per run to maintain architectural clarity.
- **Future Integration:** Consider IPC for communication between PySide and PyGame in future phases.

## Next Steps

1. **Add Renderer Selector:** Implement `--ui=pyside|pygame`.
2. **Introduce IPC:** Establish JSON-based communication over TCP.
3. **Wrap PyGame as Child App:** Launch PyGame from PySide using subprocess.
4. **Surface Messages:** Display game events in PySide status bar.
5. **Plan for Embedding:** Document reparenting strategy for future integration.
