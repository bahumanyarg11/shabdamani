"""Pūrva-prakaraṇa (sūtras 1–51): sound inventory, classes and orthographic alternations.

Classification helpers (6–17) and the few word-level alternations Kēśirāja teaches here:
5/16 kṣaḷa (Sanskrit ಲ written ಳ), 29 r/l metathesis (ಮರಲ್ ~ ಮಲರ್, ರ → ಣ), 46 loss of
final -ವು in six nouns, 47 ಅಲ್ಲದೆ → ಅಲ್ಲ and ಅಲ್ಲದು → ಅಲ್ತು.
"""
from __future__ import annotations

from . import samjna as S
from . import varna as V
from .prakriya import Prakriya, Term

VARGA_NAMES = ["ಕವರ್ಗ", "ಚವರ್ಗ", "ಟವರ್ಗ", "ತವರ್ಗ", "ಪವರ್ಗ"]
VU_LOSS_46 = {"ನರವು", "ನೆರವು", "ಬರವು", "ತೆರವು", "ಎಬ್ಬರವು", "ನೊಳವು"}


def classify(*varnas: str) -> set[str]:
    """Kēśirāja's class names that hold for the given sound(s)."""
    vs = [v if (V.is_vowel(v) or V.is_consonant(v)) else (v + V.VIRAMA if v in V.CONSONANT_LETTERS else v)
          for v in varnas]
    out = set()
    if len(vs) == 2 and all(V.is_vowel(v) for v in vs):
        a, b = vs
        if b in S.SAVARNA.get(a, "") or (a, b) in (("ಎ", "ಏ"), ("ಏ", "ಎ"), ("ಒ", "ಓ"), ("ಓ", "ಒ")) or a == b:
            out.add("ಸವರ್ಣ")                                            # 6–8
    if len(vs) == 1:
        v = vs[0]
        if v in S.HRASVA:
            out.add("ಹ್ರಸ್ವ")                                           # 9
        if v in S.DIRGHA:
            out.add("ದೀರ್ಘ")
        if v in S.NAMI:
            out.add("ನಾಮಿ")
        if v in S.SANDHYAKSHARA:
            out.add("ಸಂಧ್ಯಕ್ಷರ")
        if v in S.SAMANA:
            out.add("ಸಮಾನ")
    if vs and all(V.is_consonant(v) for v in vs):
        for name, g in zip(VARGA_NAMES, S.VARGA):                       # 13
            if all(v in g for v in vs):
                out.add(name)
        if all(v in S.AVARGIYA for v in vs):
            out.add("ಅವರ್ಗ")
    return out


def _mk(word, new, rule, note):
    p = Prakriya([Term.make(word)])
    p.terms = [Term.make(new)]
    p.log(rule, note)
    return p


def variants(word: str) -> list[Prakriya]:
    w = V.normalize(word)
    out = []
    if "ಲ" in w:                                                         # 5/16 kṣaḷa
        out.append(_mk(w, w.replace("ಲ", "ಳ"), "16", "Sanskrit ಲ written ಳ (kṣaḷa)"))
    vs = V.to_varnas(w)
    for k in range(len(vs) - 2):                                          # 29 r/l metathesis
        if vs[k] == "ರ್" and V.is_vowel(vs[k + 1]) and vs[k + 2] == "ಲ್":
            new = vs[:k] + ["ಲ್", vs[k + 1], "ರ್"] + vs[k + 3:]
            out.append(_mk(w, V.from_varnas(new), "29", "r … l → l … r"))
            new2 = vs[:k] + ["ಣ್"] + vs[k + 1:]
            out.append(_mk(w, V.from_varnas(new2), "29", "medial r → ṇ (bahula)"))
    if w in VU_LOSS_46:                                                   # 46
        out.append(_mk(w, w[:-2] + "ಂ", "46", "final -vu lost; nominative -ṃ"))
    if w.endswith("ಅಲ್ಲದೆ") or w.endswith("ನಲ್ಲದೆ") or w.endswith("ಲ್ಲದೆ"):     # 47
        out.append(_mk(w, w[:-2], "47", "ಅಲ್ಲದೆ → ಅಲ್ಲ (nirdhāraṇa)"))
    return out


def alla_tu(left: str) -> list[Prakriya]:
    """47: X + ಅಲ್ಲದು → X-ಅಲ್ತು."""
    from .sandhi import results
    return [_mk(left, r[:-len("ಅಲ್ಲದು")] + "ಅಲ್ತು" if False else r.replace("ಲ್ಲದು", "ಲ್ತು"), "47",
                "ಅಲ್ಲದು → ಅಲ್ತು") for r in results(left, "ಅಲ್ಲದು")]
