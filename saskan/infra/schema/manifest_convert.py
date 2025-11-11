# saskan/infra/schema/manifest_convert.py
from __future__ import annotations
from typing import Dict, Any

from saskan.infra.schema.manifest_dto import (
    DefaultsDTO,
    MetaDTO,
    LicenseDTO,
    SourceDTO,
    SpriteDTO,
    TilesetDTO,
    CacheDTO,
    VariantDTO,
    ManifestDTO,
    AssetDTO
)


def _opt(d: Dict[str, Any], k: str):
    return d.get(k) if d.get(k) is not None else None


def _to_defaults(d: Dict[str, Any] | None) -> DefaultsDTO | None:
    if not d:
        return None
    return DefaultsDTO(
        _opt(d, "image_max_px"), _opt(d, "audio_bitrate_kbps"), _opt(d, "cache_control")
    )


def _to_meta(d: Dict[str, Any] | None) -> MetaDTO | None:
    if not d:
        return None
    return MetaDTO(_opt(d, "build_hash"), _opt(d, "git_commit"), dict(d.get("tool_versions") or {}))


def _to_license(d: Dict[str, Any] | None) -> LicenseDTO | None:
    if not d:
        return None
    return LicenseDTO(_opt(d, "name"), _opt(d, "url"), _opt(d, "attribution"))


def _to_source(d: Dict[str, Any] | None) -> SourceDTO | None:
    if not d:
        return None
    return SourceDTO(_opt(d, "provenance"), _opt(d, "original_link"))


def _to_sprite(d: Dict[str, Any] | None) -> SpriteDTO | None:
    if not d:
        return None
    return SpriteDTO(_opt(d, "frame_w"), _opt(d, "frame_h"), _opt(d, "frames"), _opt(d, "fps"))


def _to_tileset(d: Dict[str, Any] | None) -> TilesetDTO | None:
    if not d:
        return None
    return TilesetDTO(
        _opt(d, "tile_w"),
        _opt(d, "tile_h"),
        _opt(d, "columns"),
        _opt(d, "rows"),
        _opt(d, "margin"),
        _opt(d, "spacing"),
    )


def _to_cache(d: Dict[str, Any] | None) -> CacheDTO | None:
    if not d:
        return None
    return CacheDTO(_opt(d, "immutable"), _opt(d, "max_age_sec"))


def _to_variant(v: Dict[str, Any]) -> VariantDTO:
    return VariantDTO(
        format=v["format"],
        mime=v["mime"],
        url=v["url"],
        size_bytes=v["size_bytes"],
        hash=v["hash"],
        width=_opt(v, "width"),
        height=_opt(v, "height"),
        duration_sec=_opt(v, "duration_sec"),
        bitrate_kbps=_opt(v, "bitrate_kbps"),
        channels=_opt(v, "channels"),
        locale=_opt(v, "locale"),
        sprite=_to_sprite(v.get("sprite")),
        tileset=_to_tileset(v.get("tileset")),
        cache=_to_cache(v.get("cache")),
        created_at=_opt(v, "created_at"),
        notes=_opt(v, "notes"),
    )


def manifest_from_dict(m: Dict[str, Any]) -> ManifestDTO:
    assets: Dict[str, AssetDTO] = {}
    for aid, a in (m.get("assets") or {}).items():
        variants = {vid: _to_variant(v) for vid, v in (a.get("variants") or {}).items()}
        assets[aid] = AssetDTO(
            asset_type=a["asset_type"],
            purpose=_opt(a, "purpose"),
            title=_opt(a, "title"),
            description=_opt(a, "description"),
            locale=_opt(a, "locale"),
            tags=list(a.get("tags") or []),
            license=_to_license(a.get("license")),
            source=_to_source(a.get("source")),
            variants=variants,
        )
    return ManifestDTO(
        id=m["id"],
        generated_at=m["generated_at"],
        base_url=m["base_url"],
        world_id=_opt(m, "world_id"),
        defaults=_to_defaults(m.get("defaults")),
        meta=_to_meta(m.get("meta")),
        assets=assets,
    )


def _emit(out: Dict[str, Any], k: str, v):
    if v is not None:
        out[k] = v


def _maybe(d: Dict[str, Any] | None) -> Dict[str, Any] | None:
    return d if d and any(v is not None and v != {} and v != [] for v in d.values()) else None


def _license_to_dict(x: LicenseDTO | None) -> Dict[str, Any] | None:
    if not x:
        return None
    d: Dict[str, Any] = {}
    _emit(d, "name", x.name)
    _emit(d, "url", x.url)
    _emit(d, "attribution", x.attribution)
    return _maybe(d)


def _source_to_dict(x: SourceDTO | None) -> Dict[str, Any] | None:
    if not x:
        return None
    d: Dict[str, Any] = {}
    _emit(d, "provenance", x.provenance)
    _emit(d, "original_link", x.original_link)
    return _maybe(d)


def _sprite_to_dict(x: SpriteDTO | None) -> Dict[str, Any] | None:
    if not x:
        return None
    d: Dict[str, Any] = {}
    for k in ("frame_w", "frame_h", "frames", "fps"):
        _emit(d, k, getattr(x, k))
    return _maybe(d)


def _tileset_to_dict(x: TilesetDTO | None) -> Dict[str, Any] | None:
    if not x:
        return None
    d: Dict[str, Any] = {}
    for k in ("tile_w", "tile_h", "columns", "rows", "margin", "spacing"):
        _emit(d, k, getattr(x, k))
    return _maybe(d)


def _cache_to_dict(x: CacheDTO | None) -> Dict[str, Any] | None:
    if not x:
        return None
    d: Dict[str, Any] = {}
    _emit(d, "immutable", x.immutable)
    _emit(d, "max_age_sec", x.max_age_sec)
    return _maybe(d)


def _variant_to_dict(v: VariantDTO) -> Dict[str, Any]:
    d: Dict[str, Any] = {
        "format": v.format,
        "mime": v.mime,
        "url": v.url,
        "size_bytes": v.size_bytes,
        "hash": v.hash,
    }
    _emit(d, "width", v.width)
    _emit(d, "height", v.height)
    _emit(d, "duration_sec", v.duration_sec)
    _emit(d, "bitrate_kbps", v.bitrate_kbps)
    _emit(d, "channels", v.channels)
    _emit(d, "locale", v.locale)
    _emit(d, "sprite", _sprite_to_dict(v.sprite))
    _emit(d, "tileset", _tileset_to_dict(v.tileset))
    _emit(d, "cache", _cache_to_dict(v.cache))
    _emit(d, "created_at", v.created_at)
    _emit(d, "notes", v.notes)
    return d


def manifest_to_dict(m: ManifestDTO) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "id": m.id,
        "generated_at": m.generated_at,
        "base_url": m.base_url,
        "assets": {},
    }
    _emit(out, "world_id", m.world_id)
    if m.defaults:
        dd: Dict[str, Any] = {}
        _emit(dd, "image_max_px", m.defaults.image_max_px)
        _emit(dd, "audio_bitrate_kbps", m.defaults.audio_bitrate_kbps)
        _emit(dd, "cache_control", m.defaults.cache_control)
        if dd:
            out["defaults"] = dd
    if m.meta:
        md: Dict[str, Any] = {}
        _emit(md, "build_hash", m.meta.build_hash)
        _emit(md, "git_commit", m.meta.git_commit)
        if m.meta.tool_versions:
            md["tool_versions"] = dict(m.meta.tool_versions)
        if md:
            out["meta"] = md
    for aid, a in m.assets.items():
        ad: Dict[str, Any] = {"asset_type": a.asset_type, "variants": {}}
        _emit(ad, "purpose", a.purpose)
        _emit(ad, "title", a.title)
        _emit(ad, "description", a.description)
        _emit(ad, "locale", a.locale)
        if a.tags:
            ad["tags"] = list(a.tags)
        _emit(ad, "license", _license_to_dict(a.license))
        _emit(ad, "source", _source_to_dict(a.source))
        for vid, v in a.variants.items():
            ad["variants"][vid] = _variant_to_dict(v)
        out["assets"][aid] = ad
    return out
