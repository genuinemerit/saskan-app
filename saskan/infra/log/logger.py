# saskan/infra/log/logger.py
from __future__ import annotations

import json
import logging
import logging.config
import os
import sys
from datetime import datetime, timezone
from logging import LogRecord
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, cast

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

    def __init__(self, *, include_exc: bool = True):
        super().__init__()
        self.include_exc = include_exc

    def format(self, record: LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "name": record.name,  # redundant but explicit
            "process": record.process,
            "thread": record.threadName,
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }

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
            payload[k] = v

        if self.include_exc and record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


# ---- Config ------------------------------------------------------------


def _default_handlers(log_dir: Optional[str]) -> Tuple[HandlersMap, FormatterConfig]:
    # Choose console in dev; add files if log_dir provided
    json_formatter: FormatterConfig = {
        "()": f"{__name__}.JSONFormatter",
        "include_exc": True,
    }

    handlers: HandlersMap = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "level": "TRACE",
            "formatter": "json",
            "filters": [],
        }
    }

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
    - In dev: console handler only (TRACE enabled).
    - If log_dir is provided: also write JSONL files per logger.
    """
    handlers, json_fmt = _default_handlers(log_dir)

    # In dev, show everything to console; in prod, INFO+ to console.
    console_level = "TRACE" if env == "dev" else "INFO"

    # Route: each named logger can have different handlers
    logger_to_handlers: Dict[str, list[str]] = {
        "saskan.server": ["console"] + (["server_file"] if "server_file" in handlers else []),
        "saskan.events": ["console"] + (["events_file"] if "events_file" in handlers else []),
        "saskan.debug": ["console"] + (["debug_file"] if "debug_file" in handlers else []),
    }

    handlers_cfg: HandlersMap = dict(handlers)
    handlers_cfg["console"] = {**handlers_cfg["console"], "level": console_level}

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
                "handlers": ["console"],
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
