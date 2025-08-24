"""
:module:   lookup.py
:author:   PQ

Find and set application language.
"""

# saskan/infra/i18n/lookup.py
import os
from functools import lru_cache
from importlib.resources import files
from typing import Mapping

import yaml

from saskan.infra.config import services as svc


def lang() -> str:
    """
    Get active language code, e.g. "en-US".
    Defaults to SASKAN_LANG env var or "en-US".
    """
    val = os.getenv("SASKAN_LANG", svc.DEFAULT_LANG)
    return val if val in svc.SUPPORTED_LANGS else svc.DEFAULT_LANG


@lru_cache(maxsize=4)
def _load_bundle(locale: str) -> Mapping[str, str]:
    """
    :param locale: Locale code, e.g. "en-US"
    Load locale bundle as a dict. Falls back to en-US if the requested
    bundle is missing or unreadable.
    :return: dict of i18n_id -> localized text
    """
    try:
        path = files("saskan.data.locales").joinpath(locale).joinpath("messages.yaml")
        with path.open("rb") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:
        if locale != "en-US":
            return _load_bundle("en-US")
        return {}


def get_text(i18n_id: str, fallback: str | None = None, locale: str | None = None) -> str:
    """
    :param i18n_id: Identifier for the localized text.
    :param fallback: Fallback text if i18n_id is not found.
    :param locale: Optional locale code to override active language.
    Lookup localized text by i18n_id. Fallback order:
      1) active locale
      2) en-US
      3) caller-provided fallback
      4) i18n_id (last resort)
    :return: Localized text.
    """
    loc = locale or lang()
    bundle = _load_bundle(loc)
    if i18n_id in bundle:
        return bundle[i18n_id]
    en = _load_bundle("en-US")
    if i18n_id in en:
        return en[i18n_id]
    return fallback or i18n_id
