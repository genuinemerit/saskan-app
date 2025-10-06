"""Generate hashed splash-image variants and update the shared manifest."""

from __future__ import annotations
from pathlib import Path
from PIL import Image
import argparse
import hashlib
import json
import os
import sys

# --- paths ---------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # .../saskan-app-alt
ASSETS = (REPO_ROOT / "assets").resolve()
OUT = ASSETS / "v0" / "images"
OUT.mkdir(parents=True, exist_ok=True)
MANIFEST = ASSETS / "manifest.json"
BASE_URL = os.getenv("SASKAN_ASSETS_BASE", "https://sfp.genuinemerit.org/saskan/assets")

# --- limits --------------------------------------------------------------
MAX_BYTES = 1_000_000  # 1 MiB budget
SPLASH_SIZES = [(1920, 1080), (960, 540), (480, 270)]
THUMB_SIZE = (320, 180)


# --- helpers -------------------------------------------------------------
def _hash_bytes(p: Path) -> str:
    """Return the first eight characters of the file's SHA-256 digest."""
    return hashlib.sha256(p.read_bytes()).hexdigest()[:8]


def _is_16_9(w: int, h: int) -> bool:
    """Check whether the width/height pair is within ~1% of a 16:9 aspect."""
    return abs((w / h) - (16 / 9)) < 0.01


def _ensure_manifest() -> dict:
    """Load ``manifest.json`` if readable; fall back to an empty mapping."""
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
    """Resize ``img`` to ``size``, enforce 1 MiB WebP budget, and return hashed name."""
    w, h = size
    variant = img.copy().resize((w, h), Image.LANCZOS)
    tmp = OUT / f"{base}.webp"
    q, sz = _webp_save_under_1mb(variant, tmp)
    tag = _hash_bytes(tmp)
    out = OUT / f"{base}.{tag}.webp"
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
                tmp = OUT / f"{base}.webp"
                tmp.write_bytes(src.read_bytes())
                tag = _hash_bytes(tmp)
                out = OUT / f"{base}.{tag}.webp"
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
    master = Image.open(OUT / one_x_name).convert("RGB")

    # ½ and ¼
    half_name = _save_variant(master, f"{base}.960x540", SPLASH_SIZES[1])
    quart_name = _save_variant(master, f"{base}.480x270", SPLASH_SIZES[2])

    # thumb
    thumb_name = _save_variant(master, f"{base}.thumb.320x180", THUMB_SIZE)

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
