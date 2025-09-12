# Bundle (i18n)

A bundle is the set of localized messages for a single locale (one file per locale).

- Use: load a locale’s bundle (e.g., `en-US/messages.yaml`) into memory and look up message keys like `msg.handshake.welcome`.
- Notes: format is YAML in this project; loading produces a dictionary of keys → translated strings.
- See also: [Internationalization](i18n.md)
