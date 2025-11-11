# saskan/infra/schema/manifest_dto.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Literal

AssetType = Literal["image", "audio", "video", "sprite", "tileset", "document"]
Purpose = Literal["story", "hud", "map", "ui", "ambience", "music", "voice"]


@dataclass
class DefaultsDTO:
    image_max_px: Optional[int] = None
    audio_bitrate_kbps: Optional[int] = None
    cache_control: Optional[str] = None


@dataclass
class MetaDTO:
    build_hash: Optional[str] = None
    git_commit: Optional[str] = None
    tool_versions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LicenseDTO:
    name: Optional[str] = None
    url: Optional[str] = None
    attribution: Optional[str] = None


@dataclass
class SourceDTO:
    provenance: Optional[str] = None
    original_link: Optional[str] = None


@dataclass
class SpriteDTO:
    frame_w: Optional[int] = None
    frame_h: Optional[int] = None
    frames: Optional[int] = None
    fps: Optional[int] = None


@dataclass
class TilesetDTO:
    tile_w: Optional[int] = None
    tile_h: Optional[int] = None
    columns: Optional[int] = None
    rows: Optional[int] = None
    margin: Optional[int] = None
    spacing: Optional[int] = None


@dataclass
class CacheDTO:
    immutable: Optional[bool] = None
    max_age_sec: Optional[int] = None


@dataclass
class VariantDTO:
    format: str
    mime: str
    url: str
    size_bytes: int
    hash: str
    width: Optional[int] = None
    height: Optional[int] = None
    duration_sec: Optional[int] = None
    bitrate_kbps: Optional[int] = None
    channels: Optional[int] = None
    locale: Optional[str] = None
    sprite: Optional[SpriteDTO] = None
    tileset: Optional[TilesetDTO] = None
    cache: Optional[CacheDTO] = None
    created_at: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class AssetDTO:
    asset_type: AssetType
    purpose: Optional[Purpose] = None
    title: Optional[str] = None
    description: Optional[str] = None
    locale: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    license: Optional[LicenseDTO] = None
    source: Optional[SourceDTO] = None
    variants: Dict[str, VariantDTO] = field(default_factory=dict)


@dataclass
class ManifestDTO:
    id: str
    generated_at: str
    base_url: str
    world_id: Optional[str] = None
    defaults: Optional[DefaultsDTO] = None
    meta: Optional[MetaDTO] = None
    assets: Dict[str, AssetDTO] = field(default_factory=dict)
