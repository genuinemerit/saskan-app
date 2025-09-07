# ADR-0006: Flat Maps (No World Wrap)

Date: 2025-08-18

Status: Accepted

Context: Hex grids can optionally “wrap” (toroidal topology) to simulate continuous worlds. In the Saskan Lands, enclosure and impassable borders are key to the lore. Earlier prototypes explored space maps, but planetary-scale navigation is deferred.

Decision: For initial releases, maps are flat (no wrap). The world has hard boundaries in all directions; neighbors at map edges are truncated.

Consequences:

Consistent with lore: the Enclosure defines borders.

Simplifies geometry: no wrap logic in hex distance, neighbors, or pathfinding.

Future exploration of the full planet (Gavor-Havorra) can revisit this decision and enable toroidal or spherical navigation if needed.

Alternatives considered:

Torus wrap: continuous edges; rejected for lore mismatch and complexity.

Spherical projection: realism; rejected as over-engineering for MVP.

Notes/Follow-ups: Document APIs (hex_distance, neighbors) as returning bounded results; systems must handle edge truncation gracefully.
