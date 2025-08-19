# Security Policy

## Supported Versions
We release patches as needed. The following versions of **saskan-app** are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| main    | ✅ Always supported |
| < past releases > | ❌ Not supported |

---

## Reporting a Vulnerability
If you discover a security vulnerability, please **do not open a public issue**.
Instead, report it responsibly by emailing the project team at:

**genuinemerit [at] pm [dot] me**

Please include:
- A clear description of the vulnerability
- Steps to reproduce (if possible)
- Potential impact and severity assessment
- Any suggested fixes or mitigations

We will acknowledge receipt of your report within **5 business days**, and provide an update on progress within **10 business days**.

---

## Disclosure Policy
- Valid vulnerabilities will be investigated and fixed as quickly as possible.
- Once a fix is available, we will coordinate disclosure with the reporter.
- Public disclosure will not happen until a patch release is available, unless the reporter and project maintainers agree otherwise.

---

## Best Practices for Users
- Always update to the latest release before deploying to production.
- Review dependency updates regularly (`poetry update` or equivalent).
- Run automated security checks (e.g., `pip-audit`, `safety`, or GitHub Dependabot).
