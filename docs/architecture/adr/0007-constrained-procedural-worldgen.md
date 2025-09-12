# ADR-0007: Constrained Procedural World Generation

**Date:** 2025-08-19
**Status:** Accepted

## Context

To create a world map that is both organic and consistent with lore, a hybrid approach combining procedural generation with hand-authored geography is necessary. Purely procedural or purely hand-painted maps have limitations in realism and maintainability.

## Decision

Implement a **constrained procedural generation pipeline**:

- **Control Layers:** Hand-specified elements like ridges, valleys, coastlines, river sources.
- **Noise Fields:** Simplex/Perlin noise blended with control layers using influence masks.
- **River/Lake Construction:** Graph-based flow from sources to basins, rasterized into elevation fields.
- **Outputs:** Elevation, moisture, biome arrays per hex; river graph JSON.
- **Contract:** Deterministic function of controls and RNG seed for reproducibility.

## Consequences

- Designers set macro geography; system adds fine detail.
- Rivers and lakes align with elevation and lore.
- Supports iterative design through deterministic regeneration.
- Requires authoring `controls.json` and influence masks.

## Alternatives Considered

- **Noise-only Maps:** Simple but uncontrollable.
- **Hand-painted Maps:** High control but non-reproducible.
- **Raster Imports:** Realistic but may not match lore.

## Notes / Follow-ups

- Store values per hex (`q,r`) as floats [0,1].
- Keep geometry pure: generator reads control files, writes arrays.
- Plan for erosion/moisture models and editor tooling in future iterations.

---

## MVP Approach: Constrained Procedural Maps

### 1. Control Layers

Create hand-authored layers (vector/raster) for:

- Elevation anchors: mountains, valleys, coastlines.
- Hydrology seeds: river sources, lake basins.
- Region constraints: bounds for elevation/moisture.

Store as rasters or light vectors, then rasterize.

### 2. Constraint Fields

Derive continuous fields from controls:

- Distance fields: proximity to features like ridges.
- Influence masks: weights indicating adherence to controls.
- Slope hints: gradients for erosion modeling.

### 3. Noise with Masks

Generate base noise and shape it:

- **Elevation:** Blend authored elevation with fractal noise using influence masks.
- **Moisture:** Combine rainfall model with masked noise.

Use domain warping to avoid straight contours while respecting masks.

### 4. Rivers and Lakes

Construct rivers as graphs:

- Use hydrology seeds at high elevations, route via flow accumulation.
- Enforce downhill paths, snap to predefined corridors if needed.
- Rasterize and smooth channels; mark depressions for lakes.

### 5. Multi-resolution Composition

Work from coarse to fine:

- Start with a coarse author map.
- Upscale and add detail with noise under masks.
- Use brush tools for local adjustments.

### 6. Hex Integration

Store all fields per hex as floats [0,1]. Derive biomes from elevation × moisture bands. Precompute slope and drainage direction for gameplay mechanics.

### 7. Authoring Workflow

Begin with a "control canvas": greyscale elevation sketch, vector ridges/valleys, river seeds. Run the generator to produce outputs, iterating by editing control layers.

### Data Contracts

Store control data in `maps/<world_id>/controls.json`. Outputs include `elevation.npy`, `moisture.npy`, `biome.npy`, `river_graph.json`.

### Top Use Cases

- Macro geography defined by authors; generator fills details.
- Rivers/lakes follow natural flow patterns.
- Quick iteration by adjusting control layers.

### Patterns to Embrace

- Use soft constraints for natural transitions.
- Combine graph and field methods for cohesive results.
- Maintain pure functions for deterministic output.

### Anti-patterns to Avoid

- Avoid freehand painting for maintainability.
- Prefer blends over hard overwrites to prevent seams.
- Ensure rivers are constructed, not left to noise.

### Roadmap Hints

- Implement orographic rainfall for realistic moisture.
- Introduce lightweight erosion models.
- Develop an editor for control layer creation.
