# ADR-0007: Constrained Procedural World Generation

* **Date:** 2025-08-19
* **Status:** Accepted

## Context

The world map must look organic but also respect hand-authored geography (mountains, valleys, rivers, bays). Purely procedural noise produces unrealistic or lore-inconsistent results; purely hand-painted maps are unmaintainable and non-reproducible. A hybrid approach is needed for MVP and beyond.

## Decision

Adopt a **constrained procedural generation pipeline**:

* **Authoritative control layers** (hand-specified ridges, valleys, coastlines, river sources, elevation/ moisture masks).
* **Noise fields** (Simplex/Perlin fractal) blended with controls via influence masks.
* **River/lake graph construction** from sources → downhill flow accumulation → rasterization into elevation field.
* **Outputs**: elevation, moisture, biome arrays per hex; river graph JSON.
* **Contract**: deterministic function of (controls, RNG seed) → reproducible maps.

## Consequences

* Designers define macro geography; system fills fine detail.
* Rivers and lakes guaranteed coherent with elevation and lore.
* Deterministic regeneration supports iteration (tweak control → regenerate).
* Requires authoring of `controls.json` + masks; generator complexity > noise-only.

## Alternatives considered

* **Noise-only maps**: simple, organic but uncontrollable.
* **Hand-painted maps**: maximal control but brittle, no reproducibility.
* **Raster imports**: realistic (DEM), but mismatched to lore and heavier data pipeline.

## Notes / Follow-ups

* Store all values per hex (`q,r`) as floats \[0,1].
* Keep geometry pure: generator has no I/O beyond reading control files and writing arrays.
* Add lightweight erosion/moisture models later.
* Provide editor tooling (PySide painter) to author control layers in future iterations.

---

More background on this topic...

MVP approach: constrained procedural maps

1. Control layers (authoritative inputs)

Create explicit layers you hand-author (vector or raster):

Elevation anchors (points/lines/polygons): mountain ridges, valleys, plateaus, coastlines.

Hydrology seeds: river sources/springs, lake basins, coastline/bays.

Forbidden/required regions: where elevation/moisture must stay within bounds.

Store as simple rasters in data/maps/ (same hex extent) or light vector (GeoJSON-like) then rasterize.

2. Constraint fields (derived from control layers)

From the controls, build continuous fields that guide noise:

Distance fields: signed distance to ridge lines, coastlines, valleys.

Influence masks: weights (0–1) indicating “how strongly to follow the control here”.

Slope direction hints: gradient vectors along ridges/valleys for erosion pass.

3. Noise with masks (fill, don’t fight)

Generate base Simplex/Perlin noise, then shape it:

Elevation:
elev = blend( author_elev, fractal_noise, influence_mask )
where author_elev is your coarse painted elevation (e.g., mountains=0.85), fractal_noise is multi-octave noise, and blend is e.g., author*mask + noise*(1-mask), optionally with curve remapping.

Moisture:
Combine rainfall model (prevailing wind + orographic lift from elevation) with masked noise: moist = rain_model(elev, wind) ⊕ masked_noise.

Use domain warping (noise sampling coords offset by low-frequency noise) to avoid straight contours while still respecting masks.

4. Rivers and lakes (graph-first, raster-second)

Rivers should be constructed, not left to noise:

Create a river graph: pick sources (your hydrology seeds at high elevation), route via flow accumulation on the (smoothed) elevation field to basins/coast.

Enforce monotonic downhill paths; snap to your pre-defined corridors if needed.

Rasterize the graph to the grid; carve shallow channels (lower elevation a bit along the path), then re-smooth locally.

Lakes: mark depressions; if closed basins exceed threshold, set lake mask and flatten elevation within shoreline.

5. Multi-resolution composition

Work coarse→fine:

Coarse author map (e.g., 64×64) with mountains/valleys/coast.

Upscale (sinc/bicubic), then add detail with mid/high-frequency noise under masks.

Local polish: brush tools to nudge shorelines, inlets, passes.

6. Hex integration

Keep all fields (elevation, moisture, masks) stored per-hex (q,r) float values in [0,1].

Derive biomes from a 2D lookup (elevation × moisture bands).

Precompute slope and drainage direction per hex for movement cost and agriculture.

7. Authoring workflow (practical)

Start with a “control canvas”: greyscale elevation sketch + vector ridges/valleys + river seeds.

Run a generator pass that: rasterizes controls → builds masks → generates noise → blends → carves rivers/lakes → outputs elevation/moisture arrays and derived biome layer.

Inspect in CLI/preview; iterate by editing control layers, not the generator.

Data contracts (suggested, JSON-friendly)

maps/<world_id>/controls.json

{
  "size": {"width": 128, "height": 96, "hex": "pointy"},
  "ridges": [{"polyline":[[q,r],...], "strength":0.9}],
  "valleys": [{"polyline":[[q,r],...], "strength":0.8}],
  "coastline": [{"polygon":[[q,r],...]}],
  "river_sources": [[q,r], ...],
  "elev_painted": [{"polygon":[[q,r],...], "elev":0.85}],
  "masks": [{"polygon":[[q,r],...], "elev_weight":1.0, "moist_weight":0.2}]
}

Outputs (stored alongside): elevation.npy, moisture.npy, biome.npy, river_graph.json.

Top use cases (MVP)

Author dictates macro geography (mountain arcs, bays); generator fills detail convincingly.

Place guaranteed rivers/lakes that obey downhill flow yet feel organic.

Iterate fast: tweak a ridge or bay polygon → regenerate in seconds without hand-editing the whole map.

Patterns to embrace

Constraints as weights: use soft masks (0–1), not hard clamps, for natural transitions.

Graph + field hybrid: rivers via graphs; landforms via fields; let them inform each other.

Coarse-to-fine: author at low frequency, synthesize high frequency.

Pure functions: generator takes controls + seed → maps; deterministic with RNG seed.

Anti-patterns to avoid

Freehand painting everything (unmaintainable; no reproducibility).

Hard overwrites (binary masks) that create ugly seams; prefer blends and local relax/smooth passes.

Letting noise decide rivers (yields nonsense drainage).

Leaking pixel/offset math into the core; keep hex indices as the only domain coordinate.

Roadmap hints

Orographic rainfall (wind + uplift over elevation) for believable moisture.

Erosion pass (cheap): thermal or hydraulic-lite along flow lines to shape valleys.

Editor later: a simple PySide “map control painter” (polylines/polygons) that writes `controls.json`.
