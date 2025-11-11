"""Generate hashed splash-image variants and update the shared manifest.
   Read from saskan/assets/local.
   Write to saskan/assets/[version]/images and /thumbs.
   Maintain an aspect ratio of 16:9

TODO:
- Consider the format of the manfest json.
  - It needs to have the higher-level metadata, not only the variants.
  - See ADR-15.
    - Top-level: One file per build/world-pack.
        - id (required, string) — manifest/package id (e.g., "saskan-base-assets").
        - world_id (optional, string) — tie to a specific world/seed if applicable.
        - generated_at (required, ISO8601Z string) — creation timestamp.
        - base_url (required, string URL) — prefix for asset URLs
          (can be CDN/object store or dev HTTPS). Clients must treat variants[*].url
           as absolute if it starts with a scheme; otherwise join with base_url.
        -defaults (optional, object) — default policy hints:
        - image_max_px (int), audio_bitrate_kbps (int), cache_control (string).
        - assets (required, array of Asset) — list of described assets (see below).
        - meta (optional, object) — arbitrary metadata (build hash, git commit, tool versions).
    - Asset (one entry per logical asset)
        - asset_id (required, string) — stable id used by game messages (e.g., "hero-splash-01").
        - type (required, enum) — "image" | "audio" | "video" | "sprite" | "tileset" | "document".
        - purpose (optional, enum/string) — "story" | "hud" | "map" | "ui" |
                "ambience" | "music" | "voice" | ....
        - title (optional, string) — human-friendly label.
        - description (optional, string) — short usage note.
        - locale (optional, BCP47 string) — e.g., "en". For localized variants, either
           duplicate assets per locale or set at variant level.
        - tags (optional, array) — free-form discoverability labels.
        - license (optional, object) — { name, url, attribution }.
        - source (optional, object) — provenance (e.g., prompt/tool, photographer,
            original link).
        - variants (required, array of Variant) — concrete files with properties below.
    - Variant (concrete file/encoding)
        - variant_id (required, string) — unique within the asset
           (e.g., "512w-webp", "128kbps-opus").
        - format (required, string) — "webp", "avif", "png", "opus", "mp3", "mp4", etc.
        - mime (required, string) — e.g., "image/webp", "audio/opus".
        - url (required, string) — absolute or relative to base_url.
        - size_bytes (required, integer) — file size for budgeting/preloading.
        - hash (required, string) — content hash (e.g., sha256:5c8e1a2…).
            Filename SHOULD embed the short hash for cache-busting.
        - width / height (optional, int) — for images/sprites/video frames.
        - duration_sec (optional, number) — for audio/video.
        - bitrate_kbps (optional, int) — for audio/video encodes.
        - channels (optional, int) — audio.
        - locale (optional, BCP47 string) — if the file is localized (e.g., narrated VO).
        - sprite (optional, object) — { frame_w, frame_h, frames, fps } for sprite sheets.
        - tileset (optional, object) — { tile_w, tile_h, columns, rows, margin, spacing }.
        - cache (optional, object) — CDN/browser hints
            (e.g., { immutable: true, max_age_sec: 31536000 }).
        - created_at (optional, ISO8601Z string) — variant build time.
        - notes (optional, string) — free-form.

    Minimalist example:
    {
    "manifest_version": "1.0",
    "id": "saskan-base-assets",
    "generated_at": "2025-08-21T14:00:00Z",
    "base_url": "https://assets.dev.saskan.example/",
    "assets": [
        {
        "asset_id": "hero-splash-01",
        "type": "image",
        "variants": [
            {
            "variant_id": "512w-webp",
            "format": "webp",
            "mime": "image/webp",
            "url": "img/hero-splash-01.5c8e1a2.webp",
            "size_bytes": 184322,
            "hash": "sha256:5c8e1a2d7c…",
            "width": 512,
            "height": 320
            }
        ]
        }
    ]
    }
- Review existing schemas in saskan/infra/schema and associated dtos.
  - Define a schema and dto for the manifest.json.
  - As needed, define additional tooling in saskan/tools/studio or /utils to
    assist with construction, maintenance and use of the manifest.json.
  - Note that the manifest.json itself can be version when a new world-build
    is produced. I am imagining that that could be either full build of the
    current saskan-app, or a variant of the entire game, for example, a game
    based on Aranzen rather than Saskantinon. May want to add some qualifiers
    to the name of the manifest.json anticipating this.

- Review the structure of the assets directories. Make sure it is what we want.
- Review the .gitignore setup. Verify that only thumbnails get added/committed.

- In push-assets.sh and on Digital Ocean,
  - Make sure remote structure matches the local structure. Avoid any confusion.
  - Should never be pushing assets directly from "local".
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image
import argparse
import hashlib
import json
import os
import sys

# --- paths ---------------------------------------------------------------
# Define the root directory of the repository, two levels up from this file's location
REPO_ROOT = Path(__file__).resolve().parents[2]  # .../saskan-app-alt

# Define the assets directory path
ASSETS = (REPO_ROOT / "assets").resolve()

# Get the assets version from environment variables, default to "v0" if not set
VERSION = os.getenv("SASKAN_ASSETS_VERSION", "v0")

# Get the world name from environment variables, default to "saskantinon" if not set
WORLD = os.getenv("SASKAN_ASSETS_WORLD", "saskantinon")

# Define the output directory for images, creating it if it doesn't exist
IMAGES_OUT = ASSETS / VERSION / "images"
IMAGES_OUT.mkdir(parents=True, exist_ok=True)

# Define the output directory for thumbnails, creating it if it doesn't exist
THUMBS_OUT = ASSETS / VERSION / "thumbs"
THUMBS_OUT.mkdir(parents=True, exist_ok=True)

# Define the manifest file path as a string
MANIFEST = str(ASSETS / WORLD) + ".manifest.json"

# Get the base URL for assets from environment variables, default to a specified URL if not set
BASE_URL = os.getenv("SASKAN_ASSETS_BASE", "https://sfp.genuinemerit.org/saskan/assets")

# --- limits --------------------------------------------------------------
# Set the maximum allowed bytes for some purpose, e.g., file size limit
MAX_BYTES = 1_000_000  # 1 MiB budget

# Define the dimensions for splash images
SPLASH_W_H = (1920, 1080)

# Define a list of splash image sizes, including half and quarter sizes
SPLASH_SIZES = [SPLASH_W_H,
                (int(SPLASH_W_H[0]/2), int(SPLASH_W_H[1]/2)),
                (int(SPLASH_W_H[0]/4), int(SPLASH_W_H[1]/4))]

# Define the thumbnail size for splash images
SPLASH_THUMB_SIZE = (int(SPLASH_W_H[0]/8), int(SPLASH_W_H[1]/8))

# Define the dimensions for tiles, marked as experimental
TILE_W_H = (64, 64)

# Define a list of sprite sizes based on tile dimensions
SPRITE_SIZES = [TILE_W_H,
                (int(TILE_W_H[0] * 2), int(TILE_W_H[1] * 2)),
                (int(TILE_W_H[0] * 4), int(TILE_W_H[1] * 4))]


# --- helpers -------------------------------------------------------------
def _hash_bytes(p: Path) -> str:
    """Return the first eight characters of the file's SHA-256 digest."""
    return hashlib.sha256(p.read_bytes()).hexdigest()[:8]


def _is_16_9(w: int, h: int) -> bool:
    """Check whether the width/height pair is within ~1% of a 16:9 aspect."""
    return abs((w / h) - (16 / 9)) < 0.01


def _ensure_manifest() -> dict:
    """Load ``?.manifest.json`` if readable; fall back to an empty mapping."""
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text())
        except Exception:
            pass
    return {}


def _write_manifest(m: dict) -> None:
    """Persist the manifest mapping to disk with stable formatting."""
    MANIFEST.write_text(json.dumps(m, indent=2))


def _webp_save_under_1mb(
    img: Image.Image, dst: Path, start_q=85, min_q=50, step=5
) -> tuple[int, int]:
    """Save ``img`` to WebP at ``dst``, lowering quality until it fits under 1 MiB."""
    q = start_q
    tmp = dst.with_suffix(".tmp.webp")
    while q >= min_q:
        img.save(tmp, format="WEBP", quality=q, method=6)
        size = tmp.stat().st_size
        if size <= MAX_BYTES:
            tmp.replace(dst)
            return q, size
        q -= step
    # as last resort try 40
    img.save(tmp, format="WEBP", quality=40, method=6)
    size = tmp.stat().st_size
    if size <= MAX_BYTES:
        tmp.replace(dst)
        return 40, size
    tmp.unlink(missing_ok=True)
    raise RuntimeError(
        f"{dst.name} exceeds 1MB even at low quality;" + " consider using a smaller/cleaner source."
    )


def _save_variant(img: Image.Image, base: str, size: tuple[int, int]) -> str:
    """Resize ``img`` to ``size``, enforce 1 MiB WebP budget, and return hashed name.
    If the base name includes the string `thumb`, then set destination for thumbs.
    """
    w, h = size
    variant = img.copy().resize((w, h), Image.LANCZOS)
    tmp = IMAGES_OUT / f"{base}.webp"
    q, sz = _webp_save_under_1mb(variant, tmp)
    tag = _hash_bytes(tmp)
    out = IMAGES_OUT / f"{base}.{tag}.webp"
    tmp.replace(out)
    return out.name


def _copy_or_reencode_1x(src: Path, base: str) -> str:
    """Return the hashed 1920×1080 splash variant, reusing or re-encoding ``src``."""
    try:
        if src.suffix.lower() == ".webp" and src.stat().st_size <= MAX_BYTES:
            with Image.open(src) as im:
                w, h = im.size
            if (w, h) == SPLASH_SIZES[0]:
                # reuse: copy → hash-name
                tmp = IMAGES_OUT / f"{base}.webp"
                tmp.write_bytes(src.read_bytes())
                tag = _hash_bytes(tmp)
                out = IMAGES_OUT / f"{base}.{tag}.webp"
                tmp.replace(out)
                return out.name
    except Exception:
        pass  # fall through to re-encode path

    # Re-encode path
    with Image.open(src) as im:
        im = im.convert("RGBA").convert("RGB")  # drop alpha for splash
        if not _is_16_9(*im.size):
            print(
                f"warn: source aspect {im.size} not 16:9; resizing will distort.", file=sys.stderr
            )
        return _save_variant(im, base, SPLASH_SIZES[0])


# --- build ---------------------------------------------------------------
def build_splash(src: Path, logical_id: str = "splash.bg") -> None:
    """Create splash derivatives from ``src`` and register them in the manifest."""
    if not src.exists():
        raise FileNotFoundError(src)

    base = "splash.default.v0"

    # 1× (1920x1080): reuse optimized WebP if qualifies, else re-encode
    one_x_name = _copy_or_reencode_1x(src, f"{base}.1920x1080")

    # Open the *1×* product as the master for downscales (avoids re-reading src)
    master = Image.open(IMAGES_OUT / one_x_name).convert("RGB")

    # ½ and ¼
    half_name = _save_variant(master, f"{base}.960x540", SPLASH_SIZES[1])
    quart_name = _save_variant(master, f"{base}.480x270", SPLASH_SIZES[2])

    # thumb
    thumb_name = _save_variant(master, f"{base}.thumb.320x180", SPLASH_THUMB_SIZE)

    # manifest
    m = _ensure_manifest()
    m[logical_id] = f"{BASE_URL}/v0/images/{one_x_name}"
    m[logical_id + ".960"] = f"{BASE_URL}/v0/images/{half_name}"
    m[logical_id + ".480"] = f"{BASE_URL}/v0/images/{quart_name}"
    m[logical_id + ".thumb"] = f"{BASE_URL}/v0/images/{thumb_name}"
    _write_manifest(m)

    print("✔ splash variants:")
    print("  1920:", one_x_name)
    print("   960:", half_name)
    print("   480:", quart_name)
    print(" thumb:", thumb_name)
    print("manifest updated:", MANIFEST)


# --- cli ----------------------------------------------------------------
def parse_args():
    """Configure and return the CLI arguments for the asset builder."""
    p = argparse.ArgumentParser(description="Build splash assets and update manifest.")
    # Option A: explicit source path
    p.add_argument("--src", type=Path, help="Path to source image (any format readable by Pillow).")
    # Option B: just a name under assets/local/
    p.add_argument("--name", type=str, help="Filename under assets/local/ (e.g., splash.webp)")
    p.add_argument(
        "--logical-id", default="splash.bg", help="Manifest logical id (default: splash.bg)"
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.src and args.name:
        print("error: use either --src or --name, not both.", file=sys.stderr)
        sys.exit(2)
    if not (args.src or args.name):
        print("error: provide --src PATH or --name FILE under assets/local/.", file=sys.stderr)
        sys.exit(2)

    if args.src:
        source = args.src
    else:
        source = (ASSETS / "local" / args.name).resolve()

    build_splash(source, logical_id=args.logical_id)
