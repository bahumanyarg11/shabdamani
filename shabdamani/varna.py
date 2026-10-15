"""Varṇa (sound) layer: Kannada script <-> sequence of varṇas, and ISO 15919 transliteration.

Internally a word is a list of varṇas. A consonant varṇa is written as the consonant
letter plus virāma (``"ಕ್"``); a vowel varṇa is the independent vowel letter (``"ಅ"``);
``"ಂ"`` (anusvāra / bindu) and ``"ಃ"`` (visarga) are varṇas of their own.

    >>> to_varnas("ಮರಂ")
    ['ಮ್', 'ಅ', 'ರ್', 'ಅ', 'ಂ']
    >>> from_varnas(['ಪ್', 'ಏ', 'ೞ್'])
    'ಪೇೞ್'
"""
from __future__ import annotations

import unicodedata

VIRAMA = "್"
ANUSVARA = "ಂ"
VISARGA = "ಃ"
JIHVAMULIYA = "ೱ"
UPADHMANIYA = "ೲ"

# independent vowel -> dependent sign ('' for inherent a)
VOWEL_SIGNS = {
    "ಅ": "", "ಆ": "ಾ", "ಇ": "ಿ", "ಈ": "ೀ", "ಉ": "ು", "ಊ": "ೂ",
    "ಋ": "ೃ", "ೠ": "ೄ", "ಌ": "ೢ", "ೡ": "ೣ",
    "ಎ": "ೆ", "ಏ": "ೇ", "ಐ": "ೈ", "ಒ": "ೊ", "ಓ": "ೋ", "ಔ": "ೌ",
}
SIGN_TO_VOWEL = {s: v for v, s in VOWEL_SIGNS.items() if s}
VOWELS = tuple(VOWEL_SIGNS)

CONSONANT_LETTERS = (
    "ಕಖಗಘಙ" "ಚಛಜಝಞ" "ಟಠಡಢಣ" "ತಥದಧನ" "ಪಫಬಭಮ"
    "ಯರಲವಶಷಸಹಳ" "ಱೞ"
)
CONSONANTS = tuple(c + VIRAMA for c in CONSONANT_LETTERS)

_IGNORED = {"‌", "‍", "಼"}  # ZWNJ, ZWJ, nukta
# characters that are punctuation/space: kept as word boundaries by callers
_ISO_VOWELS = {
    "ಅ": "a", "ಆ": "ā", "ಇ": "i", "ಈ": "ī", "ಉ": "u", "ಊ": "ū", "ಋ": "r̥", "ೠ": "r̥̄",
    "ಌ": "l̥", "ೡ": "l̥̄", "ಎ": "e", "ಏ": "ē", "ಐ": "ai", "ಒ": "o", "ಓ": "ō", "ಔ": "au",
}
_ISO_CONS = dict(zip(
    CONSONANT_LETTERS,
    ["k", "kh", "g", "gh", "ṅ", "c", "ch", "j", "jh", "ñ", "ṭ", "ṭh", "ḍ", "ḍh", "ṇ",
     "t", "th", "d", "dh", "n", "p", "ph", "b", "bh", "m",
     "y", "r", "l", "v", "ś", "ṣ", "s", "h", "ḷ", "ṟ", "ḻ"],
))
_ISO_OTHER = {ANUSVARA: "ṁ", VISARGA: "ḥ", JIHVAMULIYA: "ẖ", UPADHMANIYA: "ḫ"}


def is_vowel(v: str) -> bool:
    return v in VOWEL_SIGNS


def is_consonant(v: str) -> bool:
    return len(v) == 2 and v[1] == VIRAMA and v[0] in CONSONANT_LETTERS


def normalize(text: str) -> str:
    """NFC-normalise and drop ZWNJ/ZWJ/nukta, which carry no grammatical information."""
    text = unicodedata.normalize("NFC", text)
    return "".join(ch for ch in text if ch not in _IGNORED)


def to_varnas(text: str) -> list[str]:
    """Split a single word written in Kannada script into varṇas.

    Non-Kannada characters raise ValueError: split sentences into words first.
    """
    text = normalize(text)
    out: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in CONSONANT_LETTERS:
            out.append(ch + VIRAMA)
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if nxt == VIRAMA:
                i += 2
                continue
            if nxt in SIGN_TO_VOWEL:
                out.append(SIGN_TO_VOWEL[nxt])
                i += 2
                continue
            out.append("ಅ")
            i += 1
        elif ch in VOWEL_SIGNS:
            out.append(ch)
            i += 1
        elif ch in (ANUSVARA, VISARGA, JIHVAMULIYA, UPADHMANIYA):
            out.append(ch)
            i += 1
        elif ch in SIGN_TO_VOWEL:  # stray vowel sign (OCR noise): treat as vowel
            out.append(SIGN_TO_VOWEL[ch])
            i += 1
        else:
            raise ValueError(f"not a Kannada letter: {ch!r} (U+{ord(ch):04X}) in {text!r}")
    return out


def from_varnas(varnas: list[str] | tuple[str, ...]) -> str:
    """Join varṇas back into Kannada script."""
    out: list[str] = []
    i = 0
    n = len(varnas)
    while i < n:
        v = varnas[i]
        if is_consonant(v):
            nxt = varnas[i + 1] if i + 1 < n else None
            if nxt is not None and is_vowel(nxt):
                out.append(v[0] + VOWEL_SIGNS[nxt])
                i += 2
                continue
            out.append(v)
        else:
            out.append(v)
        i += 1
    return "".join(out)


def to_iso(text_or_varnas) -> str:
    """ISO 15919 transliteration of a word (script string or varṇa list)."""
    varnas = to_varnas(text_or_varnas) if isinstance(text_or_varnas, str) else text_or_varnas
    parts = []
    for v in varnas:
        if is_consonant(v):
            parts.append(_ISO_CONS[v[0]])
        elif is_vowel(v):
            parts.append(_ISO_VOWELS[v])
        else:
            parts.append(_ISO_OTHER.get(v, v))
    return "".join(parts)


def iso_text(text: str) -> str:
    """Transliterate running text, leaving non-Kannada characters as they are."""
    out, word = [], []
    for ch in normalize(text):
        if ch in CONSONANT_LETTERS or ch in VOWEL_SIGNS or ch in SIGN_TO_VOWEL or ch in (
                VIRAMA, ANUSVARA, VISARGA, JIHVAMULIYA, UPADHMANIYA):
            word.append(ch)
        else:
            if word:
                out.append(to_iso("".join(word)))
                word = []
            out.append(ch)
    if word:
        out.append(to_iso("".join(word)))
    return "".join(out)


def first(varnas):
    return varnas[0] if varnas else None


def last(varnas):
    return varnas[-1] if varnas else None


_HOMORGANIC = {"ಙ": "ಕಖಗಘ", "ಞ": "ಚಛಜಝ", "ಣ": "ಟಠಡಢ", "ನ": "ತಥದಧನ", "ಮ": "ಪಫಬಭಮ"}


def canonical(text: str) -> str:
    """Orthographic canonical form (sūtra 161): a nasal before a homorganic stop and a
    word-final ಮ್/ನ್ are written as anusvāra. Used to compare forms written either way."""
    t = normalize(text)
    out = []
    i = 0
    while i < len(t):
        ch = t[i]
        if ch in _HOMORGANIC and i + 2 < len(t) + 1 and t[i + 1:i + 2] == VIRAMA and \
                i + 2 < len(t) and t[i + 2] in _HOMORGANIC[ch]:
            out.append(ANUSVARA)
            i += 2
            continue
        out.append(ch)
        i += 1
    s = "".join(out)
    words = []
    for w in s.split(" "):
        if w.endswith(("ನ್", "ಮ್")) and len(w) > 2:
            w = w[:-2] + ANUSVARA
        words.append(w)
    return " ".join(words)
