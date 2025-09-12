# PySide QT

Using PySide6 -- Notes, Discussion

Qt is the C++ framework, PySide is the official Python binding (maintained by Qt for Python project, under The Qt Company). PyQt is the alternative maintained by Riverbank Computing. Both wrap the same underlying Qt libraries, so they’re functionally close.

Both PyQt6 and PySide6 are healthy, modern, and track Qt 6 closely. Day-to-day API parity is \~99%; the practical differences are licensing, release cadence, and tooling polish.

## Snapshot (2025)

* **Release pace / coverage.** PyQt6 shipped support for Qt 6.8 and 6.9 promptly (add-ons too: Charts, 3D, WebEngine, Graphs, etc.). ([riverbankcomputing.com][1])
  PySide6 (Qt for Python) likewise tracks current Qt, with 6.9.0 release notes showing ongoing fixes and new platform targets (e.g., Windows ARM64 tech preview). ([Qt Documentation][2])

* **Licensing.**
  **PyQt6**: GPL/commercial from Riverbank. **PySide6**: LGPL/commercial from The Qt Company. For closed-source without a commercial license, LGPL (PySide6) is usually easier to satisfy than GPL (PyQt) — but do review your obligations for dynamic linking, reverse-engineering allowances, etc. ([Python GUIs][3])

* **Ecosystem direction.**
  Qt Group is investing in broader language bridges and modern tooling (e.g., Qt 6.9, “Qt Bridges”), which flows into PySide6 first as it’s the official binding. ([qt.io][4], [DEVOPSdigest][5], [TechRadar][6])

* **Tooling & deployment.**
  PySide6 ships **pyside6-deploy** (wrapper around Nuitka) to produce stand-alone apps; PyInstaller is also supported. WebEngine and platform antivirus quirks can still require tweaks, but nothing show-stopping. ([Qt Documentation][7], [pyinstaller.org][8], [GitHub][9])

* **Under the hood.**
  PySide6 uses **Shiboken6** for binding generation; recent notes show ongoing C++/Python interop improvements (smart pointers, enums, crash fixes). ([Qt Documentation][10])

Given our open-source lean and desire to avoid license friction, **PySide6** is the sensible default. It’s LGPL, officially backed, tracks Qt features, and includes first-party deploy tooling.

## Practical tiebreakers

* **License posture:** want permissive OSS use without buying a commercial license → **PySide6**. ([Python GUIs][3])
* **Docs & examples you prefer:** many community tutorials skew PyQt; official Qt docs/examples match PySide. Pick the ecosystem that “reads” better to you. ([Python GUIs][11])
* **Deployment workflow:** happy with Qt’s **pyside6-deploy**/Nuitka path → **PySide6**; if your team is already standardized on PyInstaller, both are fine. ([Qt Documentation][7])
* **Edge modules (WebEngine, 3D, Graphs):** check the exact Qt 6.x you’ll ship with — both bindings publish matching wheels, but verify your target OS/CPU (e.g., Win ARM64 is still labeled preview on PySide6 6.9). ([riverbankcomputing.com][1], [Qt Documentation][2])

Bottom line: pick one and stick to it. For a new project with an open-source tilt, **PySide6**. If we later change our mind, porting between the two is mostly search-and-replace plus a few import/Signal syntax nits.

[1]: https://riverbankcomputing.com/?utm_source=chatgpt.com "Riverbank Computing | News"
[2]: https://doc.qt.io/qtforpython-6/release_notes/pyside6_release_notes.html?utm_source=chatgpt.com "PySide6 - Qt for Python"
[3]: https://www.pythonguis.com/faq/pyqt6-vs-pyside6/?utm_source=chatgpt.com "PyQt6 vs PySide6: What's the difference between the two ..."
[4]: https://www.qt.io/press/qt-group-unveils-expansion-plans-for-technology-agnostic-qt-ecosystem?utm_source=chatgpt.com "Qt Group unveils expansion plans for technology-agnostic ..."
[5]: https://www.devopsdigest.com/qt-group-unveils-expansion-plans-for-technology-agnostic-qt-ecosystem?utm_source=chatgpt.com "Qt Group Unveils Expansion Plans for Technology- ..."
[6]: https://www.techradar.com/pro/qt-is-everywhere-the-development-framework-secretly-featuring-on-billions-of-devices?utm_source=chatgpt.com "\"Qt is everywhere\" - we hear about the development framework secretly featuring on billions of devices across the world"
[7]: https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html?utm_source=chatgpt.com "pyside6-deploy: the deployment tool for Qt for Python"
[8]: https://pyinstaller.org/en/stable/CHANGES.html?utm_source=chatgpt.com "Changelog for PyInstaller"
[9]: https://github.com/pyinstaller/pyinstaller/issues/6387?utm_source=chatgpt.com "frozen file having PySide6.QtWebEngineCore does not be ..."
[10]: https://doc.qt.io/qtforpython-6/release_notes/shiboken6_release_notes.html?utm_source=chatgpt.com "Shiboken6 - Qt for Python"
[11]: https://www.pythonguis.com/pyqt6-tutorial/?utm_source=chatgpt.com "PyQt6 Tutorial 2025, Create Python GUIs with Qt"

## Clean up and install

Don’t rip out system Qt. Keep OS packages; isolate Python Qt in venvs. That gives us stability and zero cross-contamination.

## What’s safe vs risky

* **Risky to remove:** Qt runtime libs installed by `apt` (Qt5/Qt6). Many desktop apps depend on them (KDE bits, OBS, VLC UIs, Calibre, even some drivers/tools). Purging can break apps.
* **Safe to remove (if you knowingly installed them):** dev tooling and headers (e.g., `qtcreator`, `qt*-dev`, `qt6-tools-dev-tools`, `qt5-default`). These aren’t needed to *use* PySide; they’re for C++/Designer/QML dev.

## Why venv-only for Python bindings

* **PySide6 wheels bundle Qt** on Linux. You don’t need system Qt to run PySide apps. Mixing `apt` Qt with `pip` PySide causes path/plugin confusion.
* Keeping PySide inside a Poetry venv avoids ABI/plugin clashes and makes packaging predictable (`pyside6-deploy`/PyInstaller).

## A clean, minimal plan

1. **Audit what’s there (don’t delete yet):**

   ```bash
   dpkg -l | grep -E '^ii\s+qt' | awk '{print $2}'
   apt-cache rdepends --installed libqt6core6 | head
   ```

   If you see apps you use in the reverse-deps, keep the runtimes.

2. **Optionally trim dev tools:**

   ```bash
   sudo apt purge qtcreator qt5-default qtbase5-dev qtbase5-dev-tools \
                   qt6-base-dev qt6-tools-dev qt6-tools-dev-tools
   sudo apt autoremove
   ```

   Only purge packages you recognize installing for dev.

3. **Project isolation with Poetry:**

   ```bash
   poetry new my_qt_sandbox
   cd my_qt_sandbox
   poetry env use python3.12   # or your target
   poetry add pyside6
   # add extras only if needed later:
   # poetry add pyside6-addons pyside6-essentials pyside6-qtads pyside6-qtmultimedia pyside6-webengine
   ```

   Test:

   ```bash
   poetry run python -c "from PySide6 import QtCore, QtWidgets; print(QtCore.__version__)"
   ```

4. **Keep your environment “quiet”:**

   * Don’t set global `QT_PLUGIN_PATH`, `QT_QPA_PLATFORM`, or `LD_LIBRARY_PATH`.
   * Don’t install PyQt alongside PySide in the same venv.

5. **Designer/QML (optional, system tools):**
   If you want the official Designer binary:

   ```bash
   sudo apt install qt6-tools-dev-tools  # provides designer-qt6
   ```

   Using system Designer is fine; it won’t interfere with PySide in your venv.

6. **Packaging sanity check early:**

   ```bash
   poetry add pyside6-deploy
   poetry run pyside6-deploy --init main.py
   ```

   or use PyInstaller:

   ```bash
   poetry add pyinstaller
   poetry run pyinstaller -F main.py
   ```

### Bottom line

* Leave system Qt alone (it’s for your desktop apps).
* Do PySide purely in venvs via Poetry.
* Trim only unneeded dev packages you knowingly installed.
* Avoid global Qt env vars; test deployment early to catch plugin/path issues.

## What is Pyinstaller?

PyInstaller is a Python packager: it takes script(s), virtual environment’s packages, and the Python interpreter itself, and bundles them into a single folder (or optionally one big executable) that we can hand to someone who doesn’t have Python installed.

### Core ideas

* **Freezes the app**: It analyzes the imports in our Python code, copies the relevant `.py` files, extension modules, and libraries into a build folder.
* **Includes a Python runtime**: The target machine doesn’t need Python — the exe contains it.
* **Supports multiple modes**:

  * *One-folder mode*: creates a dist/ directory with the exe + all the DLLs/so files. Easier to debug.
  * *One-file mode*: wraps everything into a single giant executable. Users like this, but startup can be slower.

### Why relevant for PySide

Qt apps rely on plugins (platform backends, image codecs, etc.). PyInstaller has built-in “hooks” that know how to grab Qt/PySide’s plugins so the app actually runs on another machine. Without that, our binary would crash on startup with “could not load platform plugin xcb”.

### Workflow

From inside the Poetry venv:

```bash
poetry add pyinstaller
poetry run pyinstaller -F main.py
```

This creates:

* `dist/main` → our distributable binary
* `build/` → scratch files
* `main.spec` → build recipe we can edit (add data files, tweak options)

We can customize with flags:

* `-F` → one-file exe
* `-w` → windowed (no console window, for GUIs)
* `--add-data` → include extra files (images, translations, configs)

### Cross-platform limits

* PyInstaller builds **for the platform it runs on**. We can’t build a Windows exe on Linux, or macOS app on Windows, unless we use a VM/CI runner for that OS.
* Works well for Linux, macOS, Windows.

### Alternatives

* **pyside6-deploy** (official Qt for Python deploy tool) wraps Nuitka, does more optimization, can generate smaller binaries.
* **cx\_Freeze** and **Briefcase** are other options.

PyInstaller is still the most widely used and battle-tested. Its big advantage is that the Qt hooks “just work” for most PySide projects.
