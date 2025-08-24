# ADR-0008: Notification Taxonomy

* **Date:** 2025-08-19
* **Status:** Accepted

## Goal

A small, durable naming scheme that cleanly classifies handshake messages now and scales later.

## Intent

rovide a stable, human‑and‑machine friendly taxonomy for classifying messages and events:

Consistent namespaces (e.g., system.*, net.*, game.*, hud.*).

Clear audience and severity semantics.

Minimal set for PR‑2 (initial MVP handshake feature); extensible for later features.

## Context

The game must communicate many types of information to the player: system status, story beats, simulation outcomes, social exchanges. A flat stream of mixed messages would overwhelm or confuse players. An explicit notification taxonomy supports filtering, prioritization, and appropriate presentation in UI (CLI, HUD, log, story recap).

Past prototypes included narrow “topics” such as market-day transactions. Lore also emphasizes calendars, lore events, and long-running stories — suggesting categories that align with RPG conventions (story, world events, faction politics, economy, combat).

## Summary of Decisions to make

Adopt an **initial high-level taxonomy** of player-facing notification categories:

1. **Story & Lore**

   * Canonical narrative events, scripted triggers, cut-scene style beats.
   * Examples: refugees arrive, agency interference, lore revelations.

2. **World Events**

   * Simulation-driven changes visible at the macro scale.
   * Examples: famine onset, ecological collapse, natural disaster, pollinator return.

3. **Faction & Politics**

   * Diplomatic shifts, treaties, conflicts, legitimacy changes.
   * Examples: faction alliance declared, rebellion triggered.

4. **Economy & Marketplace**

   * Trade, price changes, production yields, resource shortages.
   * Examples: “Wheat surplus drives prices down”, “Iron trade route disrupted”.

5. **Calendar & Time**

   * Turn progression, seasonal transitions, festival/ritual reminders.
   * Examples: “Mid-Selaron festival begins”, “Year 142, Winter season”.

6. **Combat & Conflict**

   * Battles, skirmishes, raids.
   * Examples: “Border clash at Havara Isle”, “Bandits attack caravan”.

7. **Actor / Player State**

   * Direct feedback about the player’s avatar, party, or controlled assets.
   * Examples: fatigue, health, morale, skill gain.

8. **System & Monitoring**

   * Meta-level messages about session, runtime, playtime hints.
   * Examples: “2 hours elapsed”, “Autosave complete”.
   * Note: may include developer-facing logging that can be surfaced to players via “story so far” reports.

9. **Social / Chat** (future)

   * Player-to-player or NPC-to-player chat/messages.
   * Examples: in-game guild chat, NPC whisper.

## Decisions Taken

1. Namespace & kind format

Field name: name (already in envelope)

Format: `<namespace>.<kind>` (lowercase, dot‑separated)

Allowed chars: [a-z0-9_.-]

Examples (PR‑2):

`system.welcome` (on successful handshake)

`system.reject` (on handshake failure)

1. Audience & severity (optional in PR‑2)

Add envelope fields (reserved keys):

audience: "user" | "operator" | "dev" | "all"

PR‑2 defaults: user (welcome), user (reject)

severity: "info" | "warning" | "error"

PR‑2: info (welcome), error (reject)

These guide logging/UX, but don’t affect protocol correctness.

1. Localization hook

If a message is meant for UI, payload MAY include i18n_id (string).

PR‑2: we keep motd as plain text; i18n_id optional for later.

1. Retention & TTL hints

Handshake notifications are ephemeral; no retention.

Optional envelope key ttl_ms reserved for future use (not used in PR‑2).

1. Backward compatibility

Taxonomy is append‑only. Never change semantics of existing `<namespace>.<kind>`; add new kinds or new namespaces as features grow.

## Consequences

* Provides a consistent **schema field** in notifications:

  ```json
  { "category": "economy", "level": "info", "text_id": "market_wheat_surplus", "payload": {...} }
  ```

* UI can group, filter, and prioritize (HUD vs log vs recap).
* Aligns with lore themes: ecological crises, agency interventions, political fractures.
* Flexible: additional categories can be added later; sub-categories possible if granularity needed.

## Alternatives considered

* **Single stream**: simpler, but noisy and unstructured.
* **Strict pub/sub topics** only: good for messaging infra, but too low-level for player-facing semantics.

## Validation Rules

* `name` MUST be known or match `<namespace>.<kind>` regex.
* For PR‑2, allow only `system.welcome` and `system.reject`.
* If an unknown name arrives in PR‑2, treat as invalid_contract.

## Logging guidance (server side)

* Include name, audience, severity in log line/JSON.

* Examples
  * HELLO outcome=welcome name=system.welcome latency_ms=243
  * HELLO outcome=reject name=system.reject reason=protocol_version_unsupported

## Notes / Follow-ups

* Add a `level` field (info/warning/critical) orthogonal to category.
* Allow configurable filters (e.g., suppress economy chatter, highlight story).
* Ensure **i18n IDs** are tied to each notification for localization.
* Extend later with category-specific metadata (e.g., combat events include participants, outcome).
* Explicitly reserve audience, severity, i18n_id, ttl_ms in the envelope’s reserved fields section.
* Document allowed characters and the exact `<namespace>.<kind>` grammar.

## Taxonomy Block for PR-2, feat(first_handshake)

### Allowed Set

* `system.welcome`: Successful handshake notification to the user (severity info).
* `system.reject`: Handshake rejected; includes a reason enum in payload (severity error).

### Naming rules

* name = `<namespace>.<kind>`; lowercase; [a-z0-9_.-].
* Names are append‑only; existing names’ semantics never change.

### Reserved envelope keys

* audience: user|operator|dev|all (default is `user` in PR‑2)
* severity: info|warning|error (PR‑2: `info` for welcome, `error` for reject)
* i18n_id: optional localization key (not required in PR‑2)
* ttl_ms: reserved for future, not used in PR‑2
