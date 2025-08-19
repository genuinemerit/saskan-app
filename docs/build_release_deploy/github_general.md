# GitHub Notes

## Using a Passkey with SSH

If encountering issues with your SSH connection to GitHub after enabling a passkey. Here are some steps to troubleshoot and resolve the issue:

### 1. **Check SSH Configuration**

Make sure your SSH configuration is still set up correctly. Verify that your `~/.ssh/config` file (if it exists) includes an entry for GitHub:

```plaintext
Host github.com
  User git
  IdentityFile ~/.ssh/id_rsa  # or your specific private key file
```

### 2. **Verify Your Public Key**

Double-check that your SSH public key is still correctly added to your GitHub account. You can verify this by going to **Settings > SSH and GPG keys** on GitHub and ensuring your public key is listed there.

### 3. **Test SSH Connection**

Run the following command to test your SSH connection to GitHub:

```bash
ssh -T git@github.com
```

If it’s set up correctly, you should see a message like:

```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

If you get an error or a timeout, there may be a network issue or a firewall blocking your connection.

### 4. **Network Configuration**

Since you mentioned a timeout, check if your network configuration has changed:

* **Firewall Settings**: Ensure that port 22 (used for SSH) is open in your firewall settings.
* **VPN/Proxy**: If you're using a VPN or proxy, try disconnecting from it and test again.

### 5. **Use HTTPS as a Workaround**

If you're unable to resolve the SSH issues, consider switching to HTTPS for pushing to your repository temporarily. You can change the remote URL using:

```bash
git remote set-url origin https://github.com/username/repository.git
```

### 6. **Revisit Passkey Configuration**

If the issue arose after setting up a passkey, ensure that the passkey configuration did not inadvertently alter your SSH settings.

### 7. **Regenerate SSH Keys**

As a last resort, you can regenerate your SSH keys:

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

Then add the new public key to your GitHub account.

### Summary

1. Check SSH configuration and public key.
2. Test your SSH connection.
3. Verify network settings.
4. Temporarily switch to HTTPS if needed.
5. Consider regenerating your SSH keys.

By following these steps, you should be able to diagnose and resolve the SSH connection issue with GitHub. If the problem persists, please provide any error messages or additional context for further assistance.

It turned out that the problem was with Network Configuration. We had increased the Firewall Setting to "Maximum", which evidently blocked apps communicating on port 22 or using SSH (not sure which). As soon as I throttled it back down to "Medium" then the git command worked properly over ssh.

---

# GitHub CLI (gh)

The **GitHub CLI (`gh`)** is a command-line tool for working with GitHub (repos, issues, PRs, releases, labels) without clicking around in the web UI.

Also see: [docs/meta/package_installers.md](docs/meta/package_installers.md)

It gives an example of how to install `gh`

Running:

```bash
gh auth login
```

does two things:

1. **Install credentials** – it links your local `gh` tool with your GitHub account by creating a secure authentication token. That way, when you run commands like `gh label create` or `gh pr create`, GitHub knows *who* you are and what permissions you have.

2. **Set context** – it lets you pick default settings (HTTPS vs SSH for git clone, which account/org to use, etc.) so subsequent `gh` commands don’t need extra flags.

**Purpose in Saskan workflow setting up release labels:**

* The label setup script (and later scripts for PRs, releases, etc.) calls GitHub APIs under the hood. Without logging in, `gh` has no authorization.
* Once you’ve authenticated once with `gh auth login`, your local machine can securely run commands against your repos.

Think of it as the handshake that makes the GitHub CLI a first-class, logged-in client — like `git` for code, but `gh` for GitHub itself.


## gh auth status

Normally don’t need to repeat it.

When you run `gh auth login`, the CLI:

* Exchanges that one-time browser code for a **personal access token (PAT)**.
* Stores it in a config file on disk:

  * `~/.config/gh/hosts.yml` (on Linux).
* That token is re-used automatically by `gh` every time you open a new shell.

### Expiry / re-login cases

* **Browser login**: the PAT `gh` gets does not expire quickly. It stays valid until you revoke it manually, or if GitHub rotates tokens.
* **If you revoke the token** in GitHub settings → you’ll need to run `gh auth login` again.
* **If you change machines** → repeat once on the new machine.
* **Multiple accounts** → `gh auth login --hostname github.com --scopes ...` per account, then pick which is default.

So: you should only need to log in once per machine, not per terminal session.

Command to check current login status is `gh auth status`.

# Types of merges

merge commits, squash merging, rebase merging

---

# git add -A vs. git add .

Great question 👍 — they *look* similar, but there’s a subtle difference in what they stage:

---

## `git add -A`

* Stages **all changes** in the repo:

  * new files
  * modified files
  * deleted files
* It’s shorthand for “add **all tracked/untracked changes, anywhere**.”
* Doesn’t matter what directory you’re in — it covers the whole repo.

---

## `git add .`

* Stages changes in the **current directory and below**.
* It stages:

  * new files
  * modified files
* ❌ It does **not** stage file deletions (unless you add `-u` too).
* And it ignores stuff outside your current directory.
  Example: if you run `git add .` inside `tests/`, it won’t stage a new file in `saskan/ui_cli/`.

---

## Practical rules of thumb

* **`git add -A`**: “Stage everything everywhere (adds, mods, deletes).”
  👉 Good for “commit all my work.”
* **`git add .`**: “Stage what’s new/changed under here.”
  👉 Good for partial commits when you’re working in one subdir.

If we ever want “stage *all modifications/deletions*, but not new untracked files,” use `git add -u`.

---

✅ Most teams just standardize on `git add -A` for simplicity — less surprise, especially with deletions.