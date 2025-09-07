# ADR-0001: Hex Grid

Date: 2025-08-17

Status: Accepted

Context: We need a uniform spatial model for movement, range, and simulation. Prior work used a 40×30 orthogonal grid; hex provides better neighbor symmetry.

Decision: Use pointy-top axial coordinates (q, r) for domain logic; convert to cube internally for distance/lerp; offset/pixel math is isolated in renderer helpers. Initial wrap policy: none (no torus).

Consequences:

Deterministic neighbors (6 axial deltas).

Single hex_distance(a,b); rings/ranges/lines derived.

UI must respect pointy-top projection formulas.

Alternatives considered: Orthogonal grid (simpler, poorer movement), flat-top hex (UI tradeoffs), toroidal wrap (post-MVP complexity).

Notes/Follow-ups: Define chunk size; document axial↔cube and axial↔pixel contracts.
