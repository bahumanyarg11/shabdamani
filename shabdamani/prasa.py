"""Prāsa (second-syllable consonant rhyme) and sūtra 5: la, kuḷa and kṣaḷa.

Sūtra 5 with its vṛtti, as read by T. V. Veṅkaṭācalaśāstrī (*Darpaṇavivaraṇe*, pp. 189–190):
ಲ (la) and ಳ (ḷa) do not rhyme. In a verse whose prāsa letter is ಳ, a Sanskrit word in the
prāsa position must keep its ಳ (kṣaḷa) form; the optional ಲ of sūtra 16 is not allowed there
(ಕಿಳಿಱ್ – ಜಳದ is a correct prāsa, ಕಿಳಿಱ್ – ಜಲದ is not). In a verse whose prāsa letter is ಲ,
a Sanskrit word keeps ಲ and kuḷa is avoided. kuḷa (native ಳ) and kṣaḷa (ಳ for Sanskrit ಲ)
rhyme with each other, being the same letter.

The checker compares letters only. It cannot tell kuḷa from kṣaḷa without a lexicon, and it
does not encode the other prāsa rules, so a mismatch that is not an l/ḷ swap is reported as
"other" rather than as a fault.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from . import varna as V

L, LL = "ಲ್", "ಳ್"


def prasa_letter(pada: str) -> str | None:
    """The consonant cluster between the first and second vowel of a pāda, in script.
    Anusvāra after the first vowel counts as part of the cluster (ಚಂಡ → ಂಡ)."""
    text = "".join(ch for ch in V.canonical(pada) if "\u0c80" <= ch <= "\u0cff")
    vs = [v for v in V.to_varnas(text) if V.is_vowel(v) or V.is_consonant(v) or v == V.ANUSVARA]
    i = next((k for k, v in enumerate(vs) if V.is_vowel(v)), None)
    if i is None:
        return None
    cl = []
    for v in vs[i + 1:]:
        if V.is_vowel(v):
            break
        cl.append(v)
    if not cl or len(cl) == len(vs) - i - 1:          # pāda ends before a second vowel
        return None
    return "".join(V.ANUSVARA if v == V.ANUSVARA else v for v in cl)


def _l_swap(a: str, b: str) -> bool:
    """a and b are the same cluster except that ಲ stands where the other has ಳ."""
    return a != b and a.replace(LL, L) == b.replace(LL, L)


@dataclass
class PrasaFinding:
    pada: int            # 0-based
    letter: str | None
    expected: str
    kind: str            # "sutra5" | "other"
    message: str


def check_prasa(padas: list[str]) -> tuple[str | None, list[PrasaFinding]]:
    """Return (prāsa letter of the verse, findings). The verse's letter is the majority one."""
    letters = [prasa_letter(p) for p in padas]
    counts = Counter(x for x in letters if x)
    if not counts:
        return None, []
    ref = counts.most_common(1)[0][0]
    out = []
    for k, x in enumerate(letters):
        if x is None or x == ref:
            continue
        if _l_swap(x, ref):
            if LL in ref:
                msg = (f"pāda {k + 1}: ಲ where the verse's prāsa is ಳ; a Sanskrit word here must "
                       f"take its kṣaḷa form ಳ (sū. 5)")
            else:
                msg = (f"pāda {k + 1}: ಳ where the verse's prāsa is ಲ; la does not rhyme with ḷa, "
                       f"so neither kṣaḷa nor kuḷa may stand here (sū. 5)")
            out.append(PrasaFinding(k, x, ref, "sutra5", msg))
        else:
            out.append(PrasaFinding(k, x, ref, "other",
                                    f"pāda {k + 1}: prāsa {V.to_iso(V.to_varnas(x))} vs "
                                    f"{V.to_iso(V.to_varnas(ref))} (not a sūtra-5 case)"))
    return ref, out
