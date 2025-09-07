# ADR-0003: Triggers via JSON Predicates + Python Action Registry

Date: 2025-08-21

Status: Accepted

Context: Lore-driven events must be data-first yet powerful; early need is clarity over expressiveness.

Decision: Represent triggers as JSON predicates with fields: when, scope, requires, weight, effects. Provide a minimal operator set (and/or/not, ==, !=, <, >, <=, >=, in, numeric ranges, distance, counts/aggregates). Map effects to a named Python action registry (string → callable). Evaluate during the Story phase; enqueue effects; apply at commit.

This ADR governs predicates used for triggers in the Story phase; not for UI conditions or infra checks.

## Consequences

Designers can author events in data; logic stays testable.

Complex conditions require composing small predicates, not embedding code.

Alternatives considered: Embedded Python scripting (powerful, mixes code/data), custom DSL (expressive, heavier parser/tooling).

Notes/Follow-ups: Log which predicates fired with inputs/outputs; version trigger schema; i18n message IDs live in data, not code.

## Tighten Review

Spell out evaluation order ( deterministic ).

Ban side‑effects inside predicates; actions handle side‑effects.

Include error taxonomy for predicate evaluation.
Actionables

Add 4–6 sample predicates with inputs/outputs (“truth tables”).

Unit tests for time/RNG/world‑reference edge cases.

## Amendments

- Predicate evaluation is deterministic (no hidden randomness).
- Randomized behaviors belong in actions or RNG systems, not predicates.
- Nested predicates are evaluated left-to-right.
- OK to use short-circuit semantics; stop once the result is determined.
- Predicates skipped due to short-circuit are not evaluated or logged.
- Predicates should carry a type or op field ("eq", "gt", "in", etc.).
- Add a version tag to the DSL so future grammar changes can co-exist.
- Every predicate evaluation should be logged with predicate_id, inputs, and result.
- Version tag: Add a concrete key: e.g. "dsl_version": 1 at the root.
- Error handling:
  - If a field is missing in the state: allow null-safe navigation with defaults if some fields are null/empty/falsey. If all fields are null, fail.
  - If a type mismatch occurs (string vs number), log and return false, include offending field in long
- Scope of state: predicates can “see” only snapshot state passed in
- Testing strategy:
  - Unit tests with JSON fixtures: input state + predicate JSON → boolean output.
  - Include edge cases (missing fields, wrong types, time comparisons).
  - At least 5 sample predicates with truth tables documented.
  - Tests that prove evaluation matches the truth tables.
  - A “bad predicate” example that is safely rejected with a clear error.

## Example predicate object

```json
{
  "type": "and",
  "predicates": [
    { "type": "eq", "field": "weather", "value": "rain" },
    { "type": "gt", "field": "population", "value": 100 }
  ]
}
```

Evaluation: true if the weather is “rain” AND population > 100.

---

## Appendix A — Operator Truth Tables

This appendix defines expected behavior for the minimal predicate operator set. All examples assume JSON predicates evaluated against a snapshot state.

👉 This appendix sets a **canonical reference** for implementing or debugging predicate evaluation.

### Equality (`eq`)

```json
{ "type": "eq", "field": "weather", "value": "rain" }
```

| Field value | Predicate | Result |
| ----------- | --------- | ------ |
| `"rain"`    | eq "rain" | true   |
| `"sun"`     | eq "rain" | false  |
| *missing*   | eq "rain" | false  |

---

### Greater Than (`gt`)

```json
{ "type": "gt", "field": "population", "value": 100 }
```

| Field value | Predicate | Result                              |
| ----------- | --------- | ----------------------------------- |
| 150         | gt 100    | true                                |
| 100         | gt 100    | false                               |
| 50          | gt 100    | false                               |
| `"abc"`     | gt 100    | false (type mismatch → log + false) |

---

### Less Than (`lt`)

```json
{ "type": "lt", "field": "population", "value": 100 }
```

| Field value | Predicate | Result |
| ----------- | --------- | ------ |
| 50          | lt 100    | true   |
| 100         | lt 100    | false  |
| 150         | lt 100    | false  |

---

### In (`in`)

```json
{ "type": "in", "field": "region", "value": ["north", "east"] }
```

| Field value | Predicate | Result |
| ----------- | --------- | ------ |
| `"north"`   | in list   | true   |
| `"east"`    | in list   | true   |
| `"west"`    | in list   | false  |
| *missing*   | in list   | false  |

---

### Not (`not`)

```json
{ "type": "not", "predicate": { "type": "eq", "field": "weather", "value": "rain" } }
```

| Field value | Predicate     | Result |
| ----------- | ------------- | ------ |
| `"rain"`    | not eq "rain" | false  |
| `"sun"`     | not eq "rain" | true   |

---

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

**Evaluation order:** left-to-right, **short-circuit enabled**.

- If P1 is false, P2 is skipped.
- Log skipped predicates as `{ skipped:true }` for traceability.

---

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

**Evaluation order:** left-to-right, **short-circuit enabled**.

- If P1 is true, P2 is skipped.
- Log skipped predicates as `{ skipped:true }`.

---

## Appendix B — Full Trigger Example

This appendix shows a complete trigger object using `when, scope, requires, weight, effects`, with `dsl_version`, short‑circuit behavior, and logging expectations.

### B.1 Minimal Viable Trigger

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

#### B.1 Notes

- `id`: stable identifier for logs/tests.
- `dsl_version`: grammar version gate.
- `scope`: domain for lookups/side‑effects (engine interprets `"region"`).
- `requires`: additional guard; evaluated after `when`.
- `weight`: baseline selection weight if multiple triggers fire.
- `effects`: names resolved by the Python action registry (string → callable).

#### Evaluation

1. Evaluate `when`; if false → stop (no `requires`, no effects).
2. If `when` is true, evaluate `requires`; if true → enqueue `effects`.
3. Short‑circuit applies to nested boolean ops per Appendix A.

#### Logging (example)

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

---

### B.2 Composite Predicates + Null‑safe Navigation

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

#### B.2 Notes

- Nested `and/or` with **short‑circuit** (left‑to‑right).
- `stocks.grain` uses dotted path; missing path → false (logged), per ADR error rules.
- Effects can include i18n message IDs (`council.notify@i18n.msg.food_aid_requested`), resolved by actions.

- Possible log with short‑circuit “skipped” marks

```json
{
  "trigger_id": "trg.food_aid_threshold.v1",
  "eval": {
    "when": {
      "type": "and",
      "children": [
        { "field": "stocks.grain", "op": "lt", "value": 500, "result": true },
        {
          "type": "or",
          "children": [
            { "field": "season", "op": "eq", "value": "late_autumn", "result": false },
            { "field": "season", "op": "eq", "value": "winter", "result": true }
          ],
          "result": true
        }
      ],
      "result": true
    },
    "requires": { "field": "population", "op": "gt", "value": 2000, "result": true }
  }
}
```

---

### B.3 Distance / Aggregate Example

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

#### B.3 Notes

- Distance/aggregate operators are admitted by ADR decision.
- Engine must provide resolvers for pseudo‑fields like `distance(...)` / `count(...)`.
- If resolver fails or type mismatches → log + false.

---

### B.4 Invalid Trigger (for tests)

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

### Expected validator outcome

- Type mismatch: `requires.value` should be number.
- Type mismatch: `weight` should be number (float).
- ADR rule: log and treat predicate as false; reject at load time if you validate triggers upfront.

---

### B.5 Action Registry Contract (reference)

- Effects resolve via a Python action registry:

  - Key format: `"<namespace>.<action>"` or `"<namespace>.<action>@<i18n_id>"`.
  - Registry lookup returns a callable signature like:
    `fn(context, scope_ref, **params) -> None`
- Side‑effects occur **after commit** of the Story phase (enqueued then applied).

---
