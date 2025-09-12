# ADR-0003: JSON Predicates & Python Action Registry

**Date:** 2025-08-21
**Status:** Accepted

## Context

Lore-driven events require a data-first approach with clarity prioritized over expressiveness.

## Decision

- **Triggers as JSON Predicates:** Use fields like `when`, `scope`, `requires`, `weight`, and `effects`.
- **Operators:** Support basic operators (`and`, `or`, `not`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `in`) and advanced ones (numeric ranges, distance, counts).
- **Action Mapping:** Map effects to a Python action registry.
- **Evaluation:** Conduct during the Story phase; enqueue effects for later application.

This ADR applies to predicates in the Story phase, excluding UI conditions or infrastructure checks.

## Consequences

- Events authored in data remain testable.
- Complex logic requires small predicate composition instead of embedded code.

### Alternatives Considered

- Embedded Python scripting: Powerful but mixes code/data.
- Custom DSL: Expressive but requires heavier tooling.

## Review Enhancements

- Define deterministic evaluation order.
- Prohibit side-effects within predicates.
- Include an error taxonomy for predicate evaluation.

## Amendments

- Evaluation is deterministic; no hidden randomness.
- Random behaviors belong in actions/RNG systems.
- Nested predicates evaluate left-to-right with short-circuit semantics.
- Log skipped predicates due to short-circuiting.
- Predicates should have a type field (e.g., "eq", "gt").
- Add a version tag to the DSL for future changes.
- Log each predicate evaluation with details.

## Testing Strategy

- Unit tests using JSON fixtures.
- Cover edge cases (missing fields, wrong types).
- Document at least five sample predicates with truth tables.
- Provide a "bad predicate" example for rejection testing.

## Example Predicate

```json
{
  "type": "and",
  "predicates": [
    { "type": "eq", "field": "weather", "value": "rain" },
    { "type": "gt", "field": "population", "value": 100 }
  ]
}
```

**Evaluation:** True if weather is "rain" AND population > 100.

---

## Appendix A — Operator Truth Tables

### Equality (`eq`)

```json
{ "type": "eq", "field": "weather", "value": "rain" }
```

| Field value | Result |
| ----------- | ------ |
| `"rain"`    | true   |
| `"sun"`     | false  |
| *missing*   | false  |

### Greater Than (`gt`)

```json
{ "type": "gt", "field": "population", "value": 100 }
```

| Field value | Result                              |
| ----------- | ----------------------------------- |
| 150         | true                                |
| 100         | false                               |
| 50          | false                               |
| `"abc"`     | false (log type mismatch)           |

### Less Than (`lt`)

```json
{ "type": "lt", "field": "population", "value": 100 }
```

| Field value | Result |
| ----------- | ------ |
| 50          | true   |
| 100         | false  |
| 150         | false  |

### In (`in`)

```json
{ "type": "in", "field": "region", "value": ["north", "east"] }
```

| Field value | Result |
| ----------- | ------ |
| `"north"`   | true   |
| `"east"`    | true   |
| `"west"`    | false  |
| *missing*   | false  |

### Not (`not`)

```json
{ "type": "not", "predicate": { "type": "eq", "field": "weather", "value": "rain" } }
```

| Field value | Result |
| ----------- | ------ |
| `"rain"`    | false  |
| `"sun"`     | true   |

### Boolean And (`and`)

```json
{ "type": "and", "predicates": [ P1, P2 ] }
```

| P1 | P2 | Result |
| -- | -- | ------ |
| T  | T  | true   |
| T  | F  | false  |
| F  | T  | false  |
| F  | F  | false  |

**Short-circuit:** If P1 is false, P2 is skipped.

### Boolean Or (`or`)

```json
{ "type": "or", "predicates": [ P1, P2 ] }
```

| P1 | P2 | Result |
| -- | -- | ------ |
| T  | T  | true   |
| T  | F  | true   |
| F  | T  | true   |
| F  | F  | false  |

**Short-circuit:** If P1 is true, P2 is skipped.

---

## Appendix B — Full Trigger Example

### Minimal Viable Trigger

```json
{
  "id": "trg.rain_market_boost.v1",
  "dsl_version": 1,
  "when": { "type": "eq", "field": "weather", "value": "rain" },
  "scope": "region",
  "requires": { "type": "gt", "field": "population", "value": 1000 },
  "weight": 1.0,
  "effects": ["market.adjust_prices_rainy_day"]
}
```

#### Evaluation

1. Evaluate `when`; if false, stop.
2. If `when` is true, evaluate `requires`; if true, enqueue `effects`.

#### Logging Example

```json
{
  "ts": "2025-08-21T10:12:00Z",
  "trigger_id": "trg.rain_market_boost.v1",
  "phase": "Story",
  "eval": {
    "when": { "result": true },
    "requires": { "result": true }
  },
  "enqueued_effects": ["market.adjust_prices_rainy_day"]
}
```

### Composite Predicates + Null-safe Navigation

```json
{
  "id": "trg.food_aid_threshold.v1",
  "dsl_version": 1,
  "when": {
    "type": "and",
    "predicates": [
      { "type": "lt", "field": "stocks.grain", "value": 500 },
      {
        "type": "or",
        "predicates": [
          { "type": "eq", "field": "season", "value": "late_autumn" },
          { "type": "eq", "field": "season", "value": "winter" }
        ]
      }
    ]
  },
  "scope": "region",
  "requires": { "type": "gt", "field": "population", "value": 2000 },
  "weight": 2.0,
  "effects": [
    "relief.enqueue_food_convoy",
    "council.notify@i18n.msg.food_aid_requested"
  ]
}
```

#### Notes

- Nested `and/or` with short-circuit.
- Effects include i18n message IDs resolved by actions.

### Distance / Aggregate Example

```json
{
  "id": "trg.bandit_patrol_alert.v1",
  "dsl_version": 1,
  "when": {
    "type": "and",
    "predicates": [
      { "type": "lt", "field": "distance(player.pos, patrol.pos)", "value": 3 },
      { "type": "gt", "field": "count(hostiles within 5 of player.pos)", "value": 0 }
    ]
  },
  "scope": "local",
  "requires": { "type": "eq", "field": "player.status", "value": "active" },
  "weight": 0.5,
  "effects": [
    "alerts.raise_bandit_patrol",
    "hud.flash_indicator@i18n.hud.hostiles_nearby"
  ]
}
```

### Invalid Trigger (for tests)

```json
{
  "id": "trg.invalid_demo.v1",
  "dsl_version": 1,
  "when": { "type": "eq", "field": "weather", "value": "rain" },
  "scope": "region",
  "requires": { "type": "gt", "field": "population", "value": "many" },
  "weight": "heavy",
  "effects": []
}
```

**Expected Outcome:** Log type mismatches; reject invalid triggers upfront.

### Action Registry Contract

- Effects resolve via a Python action registry.
- Format: `"<namespace>.<action>"` or `"<namespace>.<action>@<i18n_id>"`.
- Callables follow: `fn(context, scope_ref, **params) -> None`.
- Side-effects occur post-commit of the Story phase.
