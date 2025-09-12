# ADR-0008: Notification Taxonomy

**Date:** 2025-08-19
**Status:** Accepted

## Goal

Develop a scalable naming scheme for classifying handshake messages, starting with a minimal set for initial MVP.

## Intent

Create a stable taxonomy for messages and events that is both human and machine-friendly:

- Consistent namespaces (e.g., `system.*`, `net.*`, `game.*`, `hud.*`).
- Clear audience and severity semantics.
- Minimal set for initial feature; extensible for future needs.

## Context

The game communicates various information types to players, such as system status, story beats, and simulation outcomes. A structured notification taxonomy helps filter, prioritize, and present these messages appropriately in the UI.

## Summary of Decisions

Adopt an **initial high-level taxonomy** for player-facing notifications:

1. **Story & Lore**
   - Narrative events and scripted triggers.
   - Examples: refugees arrive, lore revelations.

2. **World Events**
   - Macro-scale simulation changes.
   - Examples: famine onset, natural disaster.

3. **Faction & Politics**
   - Diplomatic shifts and conflicts.
   - Examples: faction alliance declared.

4. **Economy & Marketplace**
   - Trade and resource updates.
   - Examples: "Wheat surplus drives prices down".

5. **Calendar & Time**
   - Turn progression and seasonal transitions.
   - Examples: "Mid-Selaron festival begins".

6. **Combat & Conflict**
   - Battles and raids.
   - Examples: "Border clash at Havara Isle".

7. **Actor / Player State**
   - Feedback about player's avatar or assets.
   - Examples: fatigue, health, morale.

8. **System & Monitoring**
   - Meta-level session messages.
   - Examples: "2 hours elapsed", "Autosave complete".

9. **Social / Chat** (future)
   - Player-to-player or NPC chat.
   - Examples: in-game guild chat.

## Decisions Taken

1. **Namespace & Kind Format**
   - Format: `<namespace>.<kind>` (lowercase, dot-separated).
   - Examples: `system.welcome`, `system.reject`.

2. **Audience & Severity**
   - Envelope fields: `audience` (user/operator/dev/all) and `severity` (info/warning/error).
   - Defaults for initial feature: user (welcome), error (reject).

3. **Localization Hook**
   - Optional `i18n_id` for UI messages.

4. **Retention & TTL Hints**
   - Handshake notifications are ephemeral; no retention.

5. **Backward Compatibility**
   - Append-only taxonomy; existing semantics remain unchanged.

## Consequences

- Provides a consistent schema field in notifications:

  ```json
  { "category": "economy", "level": "info", "text_id": "market_wheat_surplus", "payload": {...} }
  ```

- Enables UI grouping, filtering, and prioritization.
- Aligns with lore themes and supports future extensions.

## Alternatives Considered

- **Single Stream:** Simpler but unstructured.
- **Strict Pub/Sub Topics:** Too low-level for player-facing semantics.

## Validation Rules

- `name` must match `<namespace>.<kind>` regex.
- For initial feature, only allow `system.welcome` and `system.reject`.

## Logging Guidance (Server Side)

- Include name, audience, severity in logs.
- Examples:
  - `HELLO outcome=welcome name=system.welcome latency_ms=243`
  - `HELLO outcome=reject name=system.reject reason=protocol_version_unsupported`

## Notes / Follow-ups

- Add a `level` field for message importance.
- Allow configurable filters for message categories.
- Ensure localization IDs are tied to notifications.
- Extend with category-specific metadata as needed.

## Taxonomy Block for Initial Feature

### Allowed Set

- `system.welcome`: Successful handshake notification (severity info).
- `system.reject`: Handshake rejected with reason (severity error).

### Naming Rules

- Format: `<namespace>.<kind>`; lowercase; [a-z0-9_.-].
- Names are append-only; existing names’ semantics never change.

### Reserved Envelope Keys

- `audience`: user|operator|dev|all (default is `user`)
- `severity`: info|warning|error (default: `info` for welcome, `error` for reject)
- `i18n_id`: optional localization key
- `ttl_ms`: reserved for future use
