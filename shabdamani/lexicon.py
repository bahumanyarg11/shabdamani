"""Lexicon helpers: word origin (dēśya / tatsama / tadbhava) and root lookup.

Many Śabdamaṇidarpaṇa rules depend on whether a word is Kannada (dēśya) or Sanskrit
(tatsama): Sanskrit sandhi applies only between Sanskrit words, arisamāsa forbids mixing
them in a compound, and so on. When the lexicon does not know a word, :func:`guess_origin`
applies phonological evidence (Sanskrit-only sounds vs. Kannada-only sounds).
"""
from __future__ import annotations

from functools import lru_cache

from . import samjna as S
from . import varna as V
from .sutras import dhatupatha, prayogasara

KANNADA, SANSKRIT, TADBHAVA, UNKNOWN = "kannada", "sanskrit", "tadbhava", "unknown"

# sounds that occur only in Sanskrit loans
_SANSKRIT_ONLY = (S.MAHAPRANA - S._c("ಸಹ")) | S._c("ಶಷಙಞ") | {"ಋ", "ೠ", "ಌ", "ೡ", "ಃ"}
# sounds that occur only in Kannada words
_KANNADA_ONLY = S.SHAKATA_REPHA | S.KULA | {"ಎ", "ಒ"}

# Sanskrit words that phonology alone cannot identify (short, no Sanskrit-only sounds)
_BUILTIN = {w: "sanskrit" for w in (
    "ಗೋ", "ನೌ", "ಗ್ಲೌ", "ಶ್ರೀ", "ಸ್ತ್ರೀ", "ಮನು", "ವಿಭು", "ವಿಧು", "ವಧು", "ಮಧು", "ದಧಿ", "ನದಿ", "ಪಟು",
    "ಗುರು", "ಸುರಗುರು", "ಮೇರು", "ಪಶು", "ತನು", "ಶಿಶು", "ರಿಪು", "ಭಾನು", "ಧೇನು", "ಸೇತು", "ಬಂಧು", "ಸಿಂಧು", "ಕವಿ", "ಮುನಿ", "ಬಲಿ", "ದೇವ", "ಗುಣ", "ಕಾಲ", "ಪ್ರಿಯ", "ಧನ", "ರಂಗ", "ದೇಶ", "ಕೋಶ", "ಪಾಶ", "ಮದ", "ರಾಗ", "ಕುಲ", "ಬಲ", "ಬುಧ", "ರಾಮ", "ಕಮಲ", "ಜಲ", "ವನ")}
_user_lexicon: dict[str, str] = dict(_BUILTIN)


def register(word: str, origin: str) -> None:
    """Tell the engine the origin of a word (overrides heuristics)."""
    _user_lexicon[V.normalize(word)] = origin


@lru_cache(maxsize=1)
def _sanskrit_from_grammar() -> frozenset:
    """Words the Śabdamaṇidarpaṇa itself cites as Sanskrit (tatsama) stems."""
    from .sutras import load
    out = set()
    for r in load().records:
        if r.get("word_class") != "sanskrit" or r.get("chapter") not in ("nama", "sandhi"):
            continue
        for e in r.get("examples") or []:
            for w in (e.get("input") or [])[:1] + [e.get("output")]:
                if isinstance(w, str) and " " not in w and len(w) > 1:
                    try:
                        V.to_varnas(w)
                        out.add(V.normalize(w).rstrip("ಂ"))
                    except ValueError:
                        pass
    return frozenset(out)


def guess_origin(word: str) -> str:
    w = V.normalize(word)
    if w in _user_lexicon:
        return _user_lexicon[w]
    if w in _sanskrit_from_grammar() or w.rstrip("ಂ") in _sanskrit_from_grammar():
        return SANSKRIT
    if w in _roots():
        return KANNADA
    vs = V.to_varnas(w)
    if any(v in _KANNADA_ONLY for v in vs):
        return KANNADA
    if any(v in _SANSKRIT_ONLY for v in vs):
        return SANSKRIT
    # Sanskrit-style conjuncts of two different stops (e.g. kt, pt, gdh) or with r/y/v as 2nd
    for a, b in zip(vs, vs[1:]):
        if a in S.VYANJANA and b in S.VYANJANA and a != b:
            if b in S._c("ಯರವ") and a not in S._c("ರ"):
                return SANSKRIT
            if a in S.VARGIYA and b in S.VARGIYA and S.varga_of(a) is not S.varga_of(b) and a not in S.ANUNASIKA:
                return SANSKRIT
    return KANNADA


@lru_cache(maxsize=1)
def _roots() -> dict[str, dict]:
    out = {}
    for r in dhatupatha():
        root = r.get("root")
        if root:
            out.setdefault(V.normalize(root), r)
    return out


def root_info(root: str) -> dict | None:
    return _roots().get(V.normalize(root))


def roots() -> list[str]:
    return list(_roots())


@lru_cache(maxsize=1)
def glossary() -> dict[str, dict]:
    return {V.normalize(e["word"]): e for e in prayogasara() if e.get("word")}
