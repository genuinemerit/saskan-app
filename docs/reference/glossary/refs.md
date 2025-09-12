# Git Reference (ref)

A human‑readable name that points to a specific commit by hash.

- Types: branches (`refs/heads/main`), tags (`refs/tags/v1.0.0`), remotes (`refs/remotes/origin/main`), and special refs (e.g., `HEAD`).
- Location: stored under `.git/refs/` and updated by commit/checkout/fetch/push.
- Inspect: `git show-ref`.
