# GitHub Secrets

Store sensitive values in GitHub Secrets (repo, org, or environment scope).

Example (repo → Settings → Secrets and variables → Actions → New repository secret):

| Name            | Value (example)                 |
| ----------------| --------------------------------|
| `DROPLET_HOST`  | `gmerit-nyc2`                   |
| `SSH_PRIVATE_KEY` | contents of your deploy key    |

Notes

- Prefer OpenID Connect for cloud access where possible
- Use environment‑scoped secrets + required reviewers for production
- Avoid printing secrets; mask patterns in logs

Docs

- [Encrypted secrets](https://docs.github.com/actions/security-guides/encrypted-secrets)
- [OIDC for Actions](https://docs.github.com/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
