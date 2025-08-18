# Package installers

## apt, snap, curl, MacPorts, pip, direct .deb's and so on


Example. Considering which to use to install `gh` (github CLI) on Ubuntu Linux.

Trade-off between **apt** (stable, but older) and **snap** (fresher, but heavier).

### The specifics for `gh`

* `apt install gh` → version **2.45.0** (Ubuntu’s repo). Reliable, well-tested, but behind.
* `snap install gh` → version **2.74.0+** (much newer, from GitHub’s upstream channel). Includes bugfixes, new features (actions cache, improved `gh api`, etc.).

### Considerations

**apt**

* Integrates neatly with the rest of your system.
* Auto-updates with `apt upgrade`.
* But version lags until Ubuntu maintainers update it.

**snap**

* Ships current builds directly from upstream.
* Sandboxed, self-contained (no dependency conflicts).
* Background auto-updates.
* Downsides: startup a bit slower, uses snap infrastructure, more disk.

### Recommendation (for your use case)

In this case, since we’re using GitHub CLI for **labels, releases, and automation setup**, having the latest features is useful. GitHub keeps improving Actions/PR integration, and some examples in docs assume a recent `gh`.

👉 Recommend **snap for `gh`** (or direct install from GitHub’s `.deb` releases), not the old apt package.

If you dislike snap, you can also:

```bash
# Download latest .deb
curl -LO https://github.com/cli/cli/releases/latest/download/gh_$(dpkg --print-architecture).deb
sudo apt install ./gh_*.deb
```

That should give me the current version without snap overhead. (didn't work for me. problem with verification keys. I used snap.)



