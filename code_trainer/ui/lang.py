import re
import unicodedata

import streamlit as st

try:
    from deep_translator import GoogleTranslator
except Exception:
    GoogleTranslator = None


def strip_number_prefix(title: str) -> str:
    t = (title or "").strip()
    t = re.sub(r"^\s*\d+\s*[\.:]\s*", "", t)
    return t


def strip_garumzimes_accents(text: str) -> str:
    if not text:
        return ""
    s = str(text)
    decomposed = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def translate_to_lv(text: str) -> str:
    txt = (text or "").strip()
    if not txt:
        return ""
    if GoogleTranslator is None:
        return strip_garumzimes_accents(txt)
    try:
        cache = st.session_state.setdefault("lv_translate_cache", {})
        if txt in cache:
            return cache[txt]
        translated_raw = GoogleTranslator(source="auto", target="lv").translate(txt)
        translated = strip_garumzimes_accents(translated_raw or txt)
        cache[txt] = translated
        return translated
    except Exception:
        return strip_garumzimes_accents(txt)

