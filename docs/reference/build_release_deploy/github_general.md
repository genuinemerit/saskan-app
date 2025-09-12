# GitHub Notes

## SSH and GitHub

Troubleshooting SSH to GitHub:

1) Check SSH config (`~/.ssh/config`)

```text
Host github.com
  User git
  IdentityFile ~/.ssh/id_rsa   # or your specific key
```

1) Verify your public key is added to GitHub

- GitHub → Settings → SSH and GPG keys
- [Docs](https://docs.github.com/authentication/connecting-to-github-with-ssh)

1) Test the connection

```bash
ssh -T git@github.com
```

Expected: “Hi `<user>`! You've successfully authenticated, but GitHub does not provide shell access.”

1) Network checks

- Ensure port 22 is open (or use SSH over HTTPS: `ssh -T -p 443 git@ssh.github.com`)
- Disable VPN/proxy to test
- [Docs](https://docs.github.com/authentication/troubleshooting-ssh/using-ssh-over-the-https-port)

1) HTTPS fallback

```bash
git remote set-url origin https://github.com/<user>/<repo>.git
```

Note: Passkeys affect web auth; they don’t change SSH. A prior timeout here was resolved by lowering a firewall setting that blocked SSH.

---

## GitHub CLI (gh)

The GitHub CLI lets you work with repos, PRs, releases, and labels from the terminal.

- Install: see `docs/reference/package_installers.md` or [cli.github.com](https://cli.github.com)
- Login: `gh auth login` (stores a PAT in `~/.config/gh/hosts.yml` on Linux)
- Status: `gh auth status`

What `gh auth login` does

- Creates credentials (a token) and sets defaults (HTTPS vs SSH, account/org)
- Enables scripts (labels/releases) to call GitHub APIs securely

---

## Merge strategies

- Merge commit: preserves branch history
- Squash merge: single commit; keeps `main` clean
- Rebase merge: linearizes feature branch onto target

[Docs](https://docs.github.com/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-merge-methods-on-github)

---

## `git add -A` vs `git add .`

`git add -A`

- Stages all changes repo‑wide (adds, modifications, deletions)

`git add .`

- Stages adds/modifications under the current directory (no deletions)

Tip: use `git add -u` for modifications/deletions without new files.

Most teams standardize on `git add -A` to avoid missing deletions.
