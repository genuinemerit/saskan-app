# saskan/infra/log/logger.py
from __future__ import annotations

import json
import logging
import logging.config
import os
import sys
from datetime import datetime, timezone
from logging import LogRecord
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

# Type aliases for clarity

HandlerConfig = Dict[str, Any]  # single handler config dict
HandlersMap = Dict[str, HandlerConfig]  # name -> handler config
FormatterConfig = Dict[str, Any]  # single formatter config dict

# ---- Level: TRACE ------------------------------------------------------

TRACE = 5
logging.addLevelName(TRACE, "TRACE")


def trace(self: logging.Logger, msg, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, msg, args, **kwargs)


logging.Logger.trace = trace  # type: ignore[attr-defined]

# ---- Filters -----------------------------------------------------------


class LevelRangeFilter(logging.Filter):
    """Admit records with min_level <= levelno <= max_level (inclusive)."""

    def __init__(self, min_level: int = TRACE, max_level: int = logging.CRITICAL):
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record: LogRecord) -> bool:
        return self.min_level <= record.levelno <= self.max_level


# ---- JSON Formatter ----------------------------------------------------


class JSONFormatter(logging.Formatter):
    """
    Minimal, fast JSON formatter.
    - ISO8601 UTC timestamps
    - merges record.extra
    - stable keys for easy parsing
    """

    base_fields: Iterable[str] = (
        "ts",
        "level",
        "logger",
        "message",
        "name",
        "process",
        "thread",
        "module",
        "funcName",
        "lineno",
    )

    # def __init__(self, *, include_exc: bool = True):
    def __init__(
        self,
        *,
        include_exc: bool = True,
        include_debug_meta: Optional[bool] = None,
        payload_max_bytes: int = 4096,
        payload_preview_chars: int = 256,
        redact_keys: Optional[Sequence[str]] = None,
    ):
        super().__init__()
        self.include_exc = include_exc
        # Default debug metadata policy: auto → on in dev, off otherwise
        env = os.getenv("SASKAN_ENV", "dev").lower()
        if include_debug_meta is None:
            meta_mode = os.getenv("SASKAN_LOG_DEBUG_META", "auto").lower()
            include_debug_meta = (
                True if (meta_mode == "on" or (meta_mode == "auto" and env == "dev")) else False
            )
        self.include_debug_meta = include_debug_meta

        self.payload_max_bytes = int(os.getenv("SASKAN_LOG_PAYLOAD_MAX", str(payload_max_bytes)))
        self.payload_preview_chars = int(
            os.getenv("SASKAN_LOG_PAYLOAD_PREVIEW", str(payload_preview_chars))
        )
        rk = os.getenv("SASKAN_LOG_REDACT_KEYS", "")
        self.redact_keys = set(
            x.strip().lower()
            for x in (list(redact_keys or []) + ([k for k in rk.split(",") if k.strip()]))
            if x
        )

    def format(self, record: LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if self.include_debug_meta:
            payload.update(
                {
                    "name": record.name,  # redundant but explicit
                    "process": record.process,
                    "thread": record.threadName,
                    "module": record.module,
                    "funcName": record.funcName,
                    "lineno": record.lineno,
                    # add pathname only in deep debug sessions if ever needed
                    # "pathname": record.pathname,
                }
            )

        # Bring in "extra" keys (anything user attached to the record)
        for k, v in record.__dict__.items():
            if k.startswith("_"):
                continue
            if k in payload:
                continue
            # Skip built-in logging keys that we already mapped or don't want
            if k in (
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "levelno",
                "levelname",
                "msecs",
                "msg",
                "relativeCreated",
                "stack_info",
            ):
                continue
            # Handle payload specially: redact + truncate if oversized
            if k == "payload":
                payload[k] = self._process_payload(v)
            else:
                payload[k] = v

        if self.include_exc and record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    # --- helpers --------------------------------------------------------
    def _process_payload(self, obj: Any) -> Any:
        try:
            redacted = self._redact(obj)
            blob = json.dumps(redacted, ensure_ascii=False, separators=(",", ":"))
            size = len(blob.encode("utf-8", errors="replace"))
            if size <= self.payload_max_bytes:
                return redacted
            # too big → return preview wrapper
            return {
                "truncated": True,
                "size_bytes": size,
                "preview": blob[: self.payload_preview_chars],
            }
        except Exception:
            # never fail logging due to payload processing
            return {"truncated": True, "error": "payload_process_failed"}

    def _redact(self, obj: Any) -> Any:
        # recursive redaction for dict/list; pass-through otherwise
        if isinstance(obj, Mapping):
            out = {}
            for k, v in obj.items():
                if k and str(k).lower() in self.redact_keys:
                    out[k] = "***"
                else:
                    out[k] = self._redact(v)
            return out
        if isinstance(obj, list):
            return [self._redact(v) for v in obj]
        return obj


# ---- Config ------------------------------------------------------------


def _default_handlers(log_dir: Optional[str]) -> Tuple[HandlersMap, FormatterConfig]:
    # Build file handlers if log_dir is set; console is attached conditionally in configure()
    # Configure formatter with env-aware knobs (ADR-0017)
    debug_meta_env = os.getenv("SASKAN_LOG_DEBUG_META", "auto").lower()
    include_debug_meta = (
        True
        if (
            debug_meta_env == "on"
            or (debug_meta_env == "auto" and os.getenv("SASKAN_ENV", "dev") == "dev")
        )
        else False
    )
    json_formatter: FormatterConfig = {
        "()": f"{__name__}.JSONFormatter",
        "include_exc": True,
        "include_debug_meta": include_debug_meta,
        # payload knobs are also read inside JSONFormatter, but pass defaults here for clarity
        "payload_max_bytes": int(os.getenv("SASKAN_LOG_PAYLOAD_MAX", "4096")),
        "payload_preview_chars": int(os.getenv("SASKAN_LOG_PAYLOAD_PREVIEW", "256")),
        "redact_keys": [
            k.strip()
            for k in os.getenv(
                "SASKAN_LOG_REDACT_KEYS", "token, authorization, auth, secret, password"
            ).split(",")
            if k.strip()
        ],
    }

    handlers: HandlersMap = {}

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

        def file_handler(filename: str, level: str, min_lvl: int, max_lvl: int) -> HandlerConfig:
            return {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(log_dir, filename),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
                "level": level,
                "formatter": "json",
                "filters": [f"range_{min_lvl}_{max_lvl}"],
            }

        handlers.update(
            {
                "server_file": file_handler("server.jsonl", "INFO", TRACE, logging.CRITICAL),
                "events_file": file_handler("events.jsonl", "INFO", logging.INFO, logging.CRITICAL),
                "debug_file": file_handler("debug.jsonl", "TRACE", TRACE, logging.DEBUG),
            }
        )

    return handlers, json_formatter


def _range_filters() -> Dict[str, Any]:
    def key(min_lvl: int, max_lvl: int) -> str:
        return f"range_{min_lvl}_{max_lvl}"

    return {
        key(TRACE, logging.DEBUG): {
            "()": f"{__name__}.LevelRangeFilter",
            "min_level": TRACE,
            "max_level": logging.DEBUG,
        },
        key(logging.INFO, logging.CRITICAL): {
            "()": f"{__name__}.LevelRangeFilter",
            "min_level": logging.INFO,
            "max_level": logging.CRITICAL,
        },
        key(TRACE, logging.CRITICAL): {
            "()": f"{__name__}.LevelRangeFilter",
            "min_level": TRACE,
            "max_level": logging.CRITICAL,
        },
    }


def configure(
    *,
    env: str = os.getenv("SASKAN_ENV", "dev"),
    log_dir: Optional[str] = os.getenv("SASKAN_LOG_DIR"),
    root_level: str = "INFO",
) -> None:
    """
    Call once at process start (CLI entrypoint, server bootstrap).
    Console echo is OFF by default. Opt-in via env SASKAN_SHOW_LOG=1.
    If log_dir is provided: write JSONL files per named logger.
    """
    handlers, json_fmt = _default_handlers(log_dir)

    # Console echo is opt-in only via env var
    show_console = os.getenv("SASKAN_SHOW_LOG", "").lower() in ("1", "true", "yes", "on")
    console_level = "TRACE" if env == "dev" else "INFO"

    # Route: each named logger can have different handlers
    logger_to_handlers: Dict[str, list[str]] = {
        "saskan.server": (["server_file"] if "server_file" in handlers else []),
        "saskan.events": (["events_file"] if "events_file" in handlers else []),
        "saskan.debug": (["debug_file"] if "debug_file" in handlers else []),
    }

    handlers_cfg: HandlersMap = dict(handlers)
    if show_console:
        handlers_cfg["console"] = {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "level": console_level,
            "formatter": "json",
            "filters": [],
        }
        # Mirror console to each named logger
        for hs in logger_to_handlers.values():
            hs.insert(0, "console")

    # broad value type avoids invariance issues
    formatters_cfg: Dict[str, Any] = {"json": json_fmt}

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters_cfg,
            "filters": _range_filters(),
            "handlers": handlers_cfg,
            "loggers": {
                name: {
                    "handlers": hs,
                    "level": "TRACE",  # let filters/handlers enforce final level
                    "propagate": False,
                }
                for name, hs in logger_to_handlers.items()
            },
            "root": {
                "level": root_level,
                "handlers": ["console"] if show_console else [],
            },
        }
    )


# ---- Convenience -------------------------------------------------------


def get_logger(name: str) -> logging.Logger:
    """
    Canonical accessor. Use:
        log = get_logger("saskan.server")
        log = get_logger("saskan.events")
        log = get_logger("saskan.debug")
    """
    return logging.getLogger(name)


def bind_context(logger: logging.Logger, **context) -> logging.LoggerAdapter:
    """Attach persistent context fields (e.g., session_id, player_id)."""
    return logging.LoggerAdapter(logger, extra=context)
