# MacOS Quirks

On macOS (including Sequoia 15.3.2), files that start with a dot (.), like .env, are considered hidden by default in Finder. Even if VS Code sees them (because VS Code doesn’t care), Finder will still play hide-and-don't-seek unless you toggle it.

🛠️ To Show Hidden Files in Finder (dotfiles like .env)

Use this keyboard shortcut in any Finder window:

```text
Command + Shift + .
```

That toggles visibility of hidden files (dotfiles) on and off. It’s persistent between sessions too.

🧠 Bonus Tip: Want to permanently unhide just one file?

If you really want .env to be unhidden by default (always visible even without using the shortcut), you can run this in the Terminal:

```bash
chflags nohidden .env
```

But that might defeat the purpose of it being "secret-ish" 🤐 — your call.

🧽 If Finder still acts up...

Sometimes Finder needs a refresh. You can either:

Press Command + Option + Escape and restart Finder

Or run this in Terminal:

```bash
killall Finder
```
