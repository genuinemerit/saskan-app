# BCP 47 tags

A BCP 47 string is basically a language tag — a standardized way to describe human languages, dialects, scripts, and regions.

## Origin

BCP = Best Current Practice (an IETF designation).

47 = the RFC number (RFC 5646 is the current version of the spec, which updates BCP 47).

What it looks like

General form: language-script-region-variant

## Examples

en → English (generic)

en-US → U.S. English

en-GB → British English

es-ES → Castilian Spanish (Spain)

es-MX → Mexican Spanish

zh-Hans → Chinese, Simplified script

zh-Hant-TW → Chinese, Traditional script, as used in Taiwan

## Where you see them

Web / HTML:  \<html lang="en-US"\>

i18n frameworks: Django, Angular, React Intl all use them for locale selection.

CLDR / Unicode data is keyed by BCP 47 tags.

APIs: Google Translate, i18next, etc.

## Why it matters

It’s the lingua franca (pun intended) for identifying languages and regions.

Lets software select the right translations, date/number formats, collation rules.

Helps search engines, accessibility tools, and browsers interpret text correctly.

## Takeaway

A BCP 47 string is just the standard way to say “this text is in Spanish (Spain)” or “English (U.S.)” so software knows what you mean.