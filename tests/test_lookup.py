# tests/test_lookup.py
"""
Tests for saskan.infra.i18n.lookup
"""

from saskan.infra.i18n.lookup import get_text, lang


def test_lang_defaults_to_en_us(monkeypatch):
    monkeypatch.delenv("SASKAN_LANG", raising=False)
    assert lang() == "en-US"


def test_lang_rejects_unknown(monkeypatch):
    monkeypatch.setenv("SASKAN_LANG", "xx-YY")
    assert lang() == "en-US"


def test_get_text_es_es(monkeypatch):
    monkeypatch.setenv("SASKAN_LANG", "es-ES")
    # assumes bundle contains the key
    assert get_text("msg.handshake.welcome") != "msg.handshake.welcome"


def test_get_text_fallback_to_en():
    # force a locale with no bundle
    assert (
        get_text("msg.handshake.welcome", locale="fr-FR").lower() != "msg.handshake.welcome".lower()
    )


def test_get_text_final_fallback():
    assert get_text("nonexistent.key", fallback="Welcome!") == "Welcome!"


def test_en_welcome_default(monkeypatch):
    monkeypatch.setenv("SASKAN_LANG", "en-EN")
    assert get_text("msg.handshake.welcome") == "Welcome to the Saskan Lands"


def test_es_welcome(monkeypatch):
    monkeypatch.setenv("SASKAN_LANG", "es-ES")
    assert get_text("msg.handshake.welcome") == "Bienvenido a las Tierras Saskan"


def test_fallback_to_en(monkeypatch):
    monkeypatch.setenv("SASKAN_LANG", "fr-FR")
    assert get_text("msg.handshake.welcome") == "Welcome to the Saskan Lands"


def test_fallback_to_id_if_missing(monkeypatch):
    monkeypatch.setenv("SASKAN_LANG", "en-US")
    assert get_text("nonexistent.key") == "nonexistent.key"
