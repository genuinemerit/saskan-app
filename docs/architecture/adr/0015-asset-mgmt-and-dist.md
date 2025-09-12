# ADR-0015: Asset Management & Distribution (First Draft)

* **Date:** 2025-08-20
* **Status:** Accepted

## Context

The game will use images, audio, and video resources that may be large in size. During prototyping, developer convenience is the priority; later, performance, scalability, and global distribution become important. The architecture must allow asset storage backends to change without breaking clients.

## Decision

**1. Access pattern**

* **Messages never embed media bytes.**
* Messages and manifests contain **metadata + URLs** (or URNs) pointing to assets.
* Metadata includes: `id`, `variants` (resolution/bitrate), `format`, `size`, `hash`, `url`.
* Clients fetch lazily on demand.

**2. Storage strategy (incremental)**

* **Stage 1 (Prototype / Hobby):**

  * Serve static files from existing developer Ubuntu server(s) over HTTPS.
  * Use a dedicated directory (e.g., `/srv/saskan-assets/`).
  * Checked-in **asset manifests** (JSON) point to these URLs.
* **Stage 2 (Early Deployment):**

  * Migrate to **DigitalOcean Spaces (S3-compatible)**.
  * Use Spaces’ CDN integration for performance.
  * Keep manifests the same; only `base_url` changes.
* **Stage 3 (Scale Up):**

  * Optionally migrate to **AWS S3 + CloudFront** or equivalent (GCS, Azure).
  * Add multi-region replication, finer IAM, or event-driven pipelines if needed.
  * Underlying store can change without client/server schema changes.

**3. Filenames & cache-busting**

* All assets named with **content hashes** (e.g., `hero.5c8e1a2.webp`).
* Old versions remain accessible; new versions always resolve to new filenames.
* Cache headers (`Cache-Control: immutable`) safe for long-term caching.

**4. Variants**

* For each asset, produce **multiple derivatives** (e.g., image sizes 256/512/1024; audio 64/128 kbps).
* Variant selection is driven by **client capability hints** (e.g., `image_max=1024`).
* Originals stored in cold storage; not shipped to runtime.

**5. Git / repo policy**

* Large binaries are **not committed**.
* Git repo holds:

  * **Manifests** (JSON with metadata/URLs).
  * **Thumbnails** or tiny exemplars only.
  * **Dev scripts** (`make assets-sync`) to pull down assets from storage.
* `.gitignore` excludes local `assets/local/` or similar.

## Consequences

* Developers can start quickly with files served over HTTPS, no infra required.
* Clients and server treat assets uniformly regardless of backend.
* Migration to DO Spaces or S3 is transparent to code (only manifests/base URLs change).
* Cache-busting prevents stale assets; hashed names provide integrity check.

## Alternatives considered

* **Database blobs:** rejected; DB is for metadata, not large media.
* **Git LFS:** useful for a few exemplars, but poor fit for bulk asset distribution.
* **Embedding assets in packages:** simplifies deployment, but explodes wheel size and blocks CDN usage.

## Notes / Follow-ups

* Define JSON schema for asset manifests (id, variants, metadata).
* Standardize on formats (WebP/AVIF for images, Opus/MP3 for audio, HLS/DASH for video).
* Add checksums (SHA256) in manifests for validation.
* Provide operator scripts to purge old, unreferenced hashed files in object storage.

---

## Manifest Structure Outline / Asset Manifest Contract Outline

Below is a **contract outline** for asset manifests. Architecture-level only; use it to guide docs and later schemas.

# Manifest: structure & semantics

## Top-level (one file per build/world pack)

* **`manifest_version`** *(required, string)* — semantic version for the manifest format (e.g., `"1.0"`).
* **`id`** *(required, string)* — manifest/package id (e.g., `"saskan-base-assets"`).
* **`world_id`** *(optional, string)* — tie to a specific world/seed if applicable.
* **`generated_at`** *(required, ISO8601Z string)* — creation timestamp.
* **`base_url`** *(required, string URL)* — prefix for asset URLs (can be CDN/object store or dev HTTPS).

  * Clients must treat `variants[*].url` as **absolute** if it starts with a scheme; otherwise join with `base_url`.
* **`defaults`** *(optional, object)* — default policy hints:

  * `image_max_px` *(int)*, `audio_bitrate_kbps` *(int)*, `cache_control` *(string)*.
* **`assets`** *(required, array of Asset)* — list of described assets (see below).
* **`meta`** *(optional, object)* — arbitrary metadata (build hash, git commit, tool versions).

## Asset (one entry per logical asset)

* **`asset_id`** *(required, string)* — stable id used by game messages (e.g., `"hero-splash-01"`).
* **`type`** *(required, enum)* — `"image" | "audio" | "video" | "sprite" | "tileset" | "document"`.
* **`purpose`** *(optional, enum/string)* — `"story" | "hud" | "map" | "ui" | "ambience" | "music" | "voice" | ...`.
* **`title`** *(optional, string)* — human-friendly label.
* **`description`** *(optional, string)* — short usage note.
* **`locale`** *(optional, BCP47 string)* — e.g., `"en"`. For localized variants, either duplicate assets per locale or set at `variant` level.
* **`tags`** *(optional, array<string>)* — free-form discoverability labels.
* **`license`** *(optional, object)* — `{ name, url, attribution }`.
* **`source`** *(optional, object)* — provenance (e.g., prompt/tool, photographer, original link).
* **`variants`** *(required, array of Variant)* — concrete files with properties below.

## Variant (concrete file/encoding)

* **`variant_id`** *(required, string)* — unique within the asset (e.g., `"512w-webp"`, `"128kbps-opus"`).
* **`format`** *(required, string)* — `"webp"`, `"avif"`, `"png"`, `"opus"`, `"mp3"`, `"mp4"`, etc.
* **`mime`** *(required, string)* — e.g., `"image/webp"`, `"audio/opus"`.
* **`url`** *(required, string)* — absolute or relative to `base_url`.
* **`size_bytes`** *(required, integer)* — file size for budgeting/preloading.
* **`hash`** *(required, string)* — content hash (e.g., `sha256:5c8e1a2…`). Filename SHOULD embed the short hash for cache-busting.
* **`width` / `height`** *(optional, int)* — for images/sprites/video frames.
* **`duration_sec`** *(optional, number)* — for audio/video.
* **`bitrate_kbps`** *(optional, int)* — for audio/video encodes.
* **`channels`** *(optional, int)* — audio.
* **`locale`** *(optional, BCP47 string)* — if the file is localized (e.g., narrated VO).
* **`sprite`** *(optional, object)* — `{ frame_w, frame_h, frames, fps }` for sprite sheets.
* **`tileset`** *(optional, object)* — `{ tile_w, tile_h, columns, rows, margin, spacing }`.
* **`cache`** *(optional, object)* — CDN/browser hints (e.g., `{ immutable: true, max_age_sec: 31536000 }`).
* **`created_at`** *(optional, ISO8601Z string)* — variant build time.
* **`notes`** *(optional, string)* — free-form.

## Relationships and reference model

* **Game messages** reference assets by `asset_id` and MAY suggest a variant class (e.g., needed width).
* Client **selects a variant** based on capability/profile (screen size, bandwidth) and `defaults`.
* Server and clients **must not** assume any particular storage backend; URLs + hashes are the contract.

---

# Examples (illustrative, not code to paste)

## Minimal manifest

```json
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
```

## Rich asset with multiple variants and localization

```json
{
  "asset_id": "intro-narration-01",
  "type": "audio",
  "purpose": "story",
  "title": "Prologue: The Enclosure",
  "license": { "name": "Saskan CC-BY", "url": "https://example.org/license" },
  "variants": [
    {
      "variant_id": "opus-96",
      "format": "opus",
      "mime": "audio/opus",
      "url": "audio/intro-narration-01.a1b2c3.opus",
      "size_bytes": 1456320,
      "hash": "sha256:a1b2c3d4…",
      "duration_sec": 62.4,
      "bitrate_kbps": 96,
      "locale": "en"
    },
    {
      "variant_id": "mp3-128-es",
      "format": "mp3",
      "mime": "audio/mpeg",
      "url": "audio/intro-narration-01.es.9f8e7d.mp3",
      "size_bytes": 2310048,
      "hash": "sha256:9f8e7d6c…",
      "duration_sec": 62.4,
      "bitrate_kbps": 128,
      "locale": "es"
    }
  ]
}
```

## Sprite/tileset example

```json
{
  "asset_id": "unit-mercator-sprites",
  "type": "sprite",
  "purpose": "map",
  "variants": [
    {
      "variant_id": "sheet-1x",
      "format": "webp",
      "mime": "image/webp",
      "url": "sprites/unit-mercator.3e4f55.webp",
      "size_bytes": 322144,
      "hash": "sha256:3e4f55…",
      "width": 1024,
      "height": 512,
      "sprite": { "frame_w": 64, "frame_h": 64, "frames": 128, "fps": 12 }
    }
  ]
}
```

---

# Constraints & guidance (non-executable)

* **IDs**: `asset_id` and `variant_id` are case-insensitive ASCII; avoid spaces; use `-` or `_`.
* **Hashing**: use `sha256:` prefix; filenames SHOULD include a short hash for cache-busting.
* **Immutability**: once published, a variant URL must be immutable; publish new variants for content changes.
* **Sizing policy**: aim for 2–3 image sizes (e.g., 256/512/1024) and 1–2 audio bitrates initially.
* **Localization**: prefer variant-level `locale` for media with language (VO, subtitles, text-in-image).
* **Backends**: `base_url` can point to dev HTTPS, DO Spaces, or S3+CDN without changing the manifest shape.
* **Integrity**: clients SHOULD verify size/hash when feasible before caching locally.

---

## Initial Discussion

Here’s an architecture-first take.

# Where large assets live

## During development

* **Don’t commit big binaries to `git`.**

  * Use **Git LFS** only if you *must* keep a few exemplar assets in-repo (remember LFS quotas).
  * Better: **`.gitignore`** a local folder like `assets/local/` and fetch from remote storage via a dev script.
* **Project tree layout (suggested):**

  ```text
  saskan/
    data/                   # small JSON configs, seeds, story text (OK in git)
    assets/                 # pointers, manifests, thumbnails (OK in git)
      manifest.json         # metadata (id, variant, hash, size, URLs)
      thumbs/               # tiny previews checked in
    # DO NOT commit raw/original large media here
  ```

* **Dev workflow:** `make assets-sync` pulls originals/derivatives from object storage (see below).

## In deployed environments

* **Object storage + CDN is the default.**

  * S3/GCS/Azure Blob behind a CDN (CloudFront/Cloud CDN/Azure CDN).
  * Store multiple **variants** (e.g., `hero@512.webp`, `hero@2k.webp`, `hero.flac`, `hero.mp3`).
  * Use **content hashes in filenames** for cache busting: `hero.5c8e1a2.webp`.
* **DB blobs:** avoid for large media. Databases are for metadata, not bulk media. Store **URLs + checksums** in DB; keep bytes in object storage.
* **Server messages:** pass **references** (ids/URLs + width/height/duration/mime/size), not payloads. Clients fetch lazily.

## Best practices to adopt now

* **Asset manifest (in git):**
  A small JSON per world/build listing each asset’s id, purpose, variants, URLs, checksum, size, and licensing/source.
* **Derivatives pipeline:**
  Build step (local or CI) produces right-sized variants (e.g., 256/512/1024 WebP; Opus/MP3 for audio). Never check in derived files; publish to object storage.
* **Resolution negotiation:**
  Client declares capability/network (e.g., `image_max=1024, audio_bitrate=96k`); server or client selects matching variant.
* **Lazy load & caching:**
  Thumbnails first; full asset on demand. Strong cache headers on CDN; immutable assets via hashed names.
* **Retention:**
  Originals in a cold bucket; ship only derivatives. Garbage-collect unreferenced hashes periodically (scripted, not manual).

## Formats & size targets (pragmatic)

* **Images:** WebP/AVIF for display; keep **< 300–500 KB** per on-screen image at 1080p; provide 2–3 resolutions.
* **Audio:** Opus/MP3 at 64–128 kbps for in-game loops; keep loops **< 2–5 MB**.
* **Video (later):** HLS/DASH with 2–4 renditions; never embed raw MP4 in messages.

## GitHub limits (what will bite you)

* **Hard reject at 100 MB per file.**
* **Warning at 50 MB** per file on push.
* Repos **>1 GB** total raise eyebrows; **>5 GB** becomes painful.
* **Git LFS**: starts with **\~1 GB storage / 1 GB bandwidth per month** per account/org; you can buy more. Don’t rely on LFS for lots of large media—use object storage.

## How this fits our client-server ADRs

* **ADR-0009/0010/0011:** messages carry **metadata + URLs**, not bytes.
* **ADR-0012:** broadcast “asset available” events by `topic=story|world` if needed; clients decide to fetch.
* **ADR-0013:** no queues for media; CDN handles delivery.
* Add one new ADR when you’re ready: **“Asset Management & Distribution”** (object storage + CDN, manifest format, variant policy, hashing, and cache strategy).

## Minimal next steps for your upcoming PR

1. Add `saskan/assets/manifest.json` (tiny, in git) with a couple of image IDs and **dev URLs**.
2. Add `assets/local/` to **.gitignore** and a `make assets-sync` stub (even if it’s a no-op now).
3. Extend handshake reply to include an **`assets_base_url`** and **client capability hints** (max image size).
4. In CLI, fetch and display a **thumbnail** only; log the URL for full-res.

---

**DigitalOcean Spaces is a solid fit for a hobby-mode asset bucket** (images/audio now; video later).

**Why it fits**

* **S3-compatible** API → use standard S3 clients/SDKs. ([DigitalOcean Docs][1])
* **Simple pricing** that’s predictable for experiments: **\~\$5/mo includes \~250 GiB storage + \~1 TiB egress**, then low overages. (Verify current rates.) ([DigitalOcean][2], [CloudZero][3])
* **Built-in CDN** option for faster delivery; easy to enable later. ([DigitalOcean Docs][4])

**How I’d use it (now)**

* Create one **Space per environment** (e.g., `saskan-dev`, later `saskan-prod`).
* Store **derivative variants** only (e.g., `@512.webp`, `@1024.webp`, audio at 96–128 kbps). Keep originals out of the runtime path.
* Name files with **content hashes** for immutable caching (`hero.5c8e1a2.webp`).
* Keep **only metadata in your DB** (id, URL, width/height, checksum). Don’t blob media in SQLite.
* In messages, send **URLs + metadata**, *never* the bytes. (Matches our ADRs.)
* Add a tiny **asset manifest** in git; fetch real files from Spaces at build/deploy.

**When to reconsider**

* If you need **global edge uploads/acceleration** or enterprise IAM, S3 wins. (Spaces is S3-compatible but lacks some AWS extras.) ([Reddit][5])
* If bandwidth/size spikes beyond hobby levels, compare total cost vs alternatives (e.g., B2 + CDN). ([AIMultiple][6])

**GitHub angle**

* GitHub warns on files **>50 MB**, hard-blocks **>100 MB**. Use **Git LFS** sparingly or, better, keep big binaries **out of git** and in Spaces. ([DigitalOcean][7])

If you want, I’ll draft a brief **Asset Management & Distribution** ADR that codifies: Spaces + CDN, hashed filenames, variants policy, and how clients negotiate which variant to load.

[1]: https://docs.digitalocean.com/products/spaces/?utm_source=chatgpt.com "Spaces Object Storage | DigitalOcean Documentation"
[2]: https://www.digitalocean.com/products/spaces?utm_source=chatgpt.com "DigitalOcean Spaces | S3-Compatible Object Storage"
[3]: https://www.cloudzero.com/blog/cloud-storage-pricing/?utm_source=chatgpt.com "The 2025 Cloud Storage Pricing Guide"
[4]: https://docs.digitalocean.com/products/spaces/details/features/?utm_source=chatgpt.com "Spaces Features | DigitalOcean Documentation"
[5]: https://www.reddit.com/r/digital_ocean/comments/1j61gu3/does_digital_oceans_space_have_equivalent_s3/?utm_source=chatgpt.com "Does Digital Ocean's Space have equivalent S3 Transfer ..."
[6]: https://research.aimultiple.com/s3-compatible-object-storage/?utm_source=chatgpt.com "S3 Compatible Cloud Object Storage Benchmark"
[7]: https://www.digitalocean.com/pricing?utm_source=chatgpt.com "Budget-Friendly Cloud Server Pricing"

---

I suppose for quick and dirty prototyping, I could even use my existing DO Ubuntu server(s) to simply host directories of resources available over https?

---

Exactly. For **quick-and-dirty prototyping**, serving static files directly from your existing DO Ubuntu box is totally fine:

* **Pros**

  * Immediate: just drop files under `/var/www/html/saskan/` (or wherever your Nginx/Apache root is).
  * HTTPS already in place if you’re terminating TLS with Let’s Encrypt.
  * No extra cost/complexity.
  * Good enough for a handful of MB-sized assets and a couple of test clients.

* **Cons**

  * **No CDN**: slower outside your server’s region; all traffic hits your droplet.
  * **Scaling**: you’re limited by droplet bandwidth & storage.
  * **Ops overhead**: you need to manage permissions, logs, TLS cert renewals.
  * **No versioned buckets**: you’ll have to roll your own cache-busting (e.g., hashed filenames).

* **Practical advice for your hobby mode**

  * Keep assets under a dedicated directory (`/srv/saskan-assets/`), serve read-only.
  * Use a manifest JSON in git (`assets/manifest.json`) that points to these URLs.
  * Bake in **hashed filenames** (`hero.abc123.webp`) so you can overwrite safely without cache confusion.
  * Treat it as **temporary scaffolding**. When you’re ready to think about real distribution (CDN, multiple variants, bigger storage), you can move to Spaces/S3 without changing your client–server contract — URLs + metadata stay the same.

Would you like me to sketch how we’d capture this “scaffolding now, object storage later” approach in a lightweight ADR so it doesn’t get forgotten once you move beyond hobby stage?

---

**Cache-busting** = a trick to make sure clients (browsers, CDNs, proxies) don’t keep showing an **old copy** of a file after you update it.

Why it matters:

* Browsers aggressively cache static assets (images, CSS, JS) based on filename + headers.
* If you overwrite `hero.png` with a new version, many clients will still serve the stale cached file until cache expiry.

How to bust the cache:

1. **Change the filename when the content changes**

   * Common: add a version or hash:

     * `hero.png` → `hero.v2.png`
     * `hero.5c8e1a2.webp` (hash of file contents)
   * Any URL change makes caches treat it as a new file.
2. **Query string hacks (less ideal)**

   * Append `?v=2` or `?t=20250820`. Works, but some CDNs ignore query strings for caching.
3. **HTTP headers**

   * Set `Cache-Control: max-age=31536000, immutable` for hashed files → clients keep them forever, safe because filename changes when file changes.
   * For dev/testing, you can use `Cache-Control: no-cache` or `must-revalidate`.

**Best practice for games/apps**

* Use **content hashes in filenames** (`asset.<hash>.ext`).
* Reference those hashed URLs in your **asset manifest**.
* That way:

  * New content = new hash = new URL.
  * Old URLs still resolve if someone’s cache lingers.
  * You can tell instantly if a file has changed by its name.

Would you like me to fold this into the planned **Asset Management & Distribution ADR**, so the policy is explicitly: “All large static resources are cache-busted via hashed filenames”?

---

