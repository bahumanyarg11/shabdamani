"""Sandhi-prakaraṇa (sūtras 52–71): what happens where two elements meet.

The central entry point is :func:`junction`, which applies the rules to the boundary
between ``p.terms[i]`` and ``p.terms[i + 1]`` of a prakriyā. Morphology modules call it
for stem+suffix boundaries; :func:`join` wraps it for two free words.

Contexts (``ctx``):
  ``WORD``     two words in a sentence (vākya / saṃhitā)
  ``SUFFIX``   stem + suffix (vibhakti, pratyaya)
  ``COMPOUND`` members of a compound (samāsa, "pada-vidhi")

Term tags understood here (all optional — callers set what they know):
  origin:        ``kannada`` / ``sanskrit`` (otherwise guessed by :mod:`lexicon`)
  left word:     ``vibhakti`` (its final vowel belongs to a case/verb ending or gerund),
                 ``genitive``, ``nipata`` (particle/interjection), ``avadharana`` (emphatic -e),
                 ``aniyoga`` (non-restrictive emphatic -e, sūtra 64), ``vishanke`` (doubt -e/-o),
                 ``pluta``, ``emotive`` (ō of admiration/reproach, ema, gaḍa-ā, laments),
                 ``anukrti`` (onomatopoeia), ``quote`` (quoted Sanskrit sentence),
                 ``padyardha`` (ends the first half of a verse), ``avyaya``, ``dhatu``,
                 ``adesha`` (final consonant is a substitute: ಒರ್/ಇರ್ < ಒಂದು/ಎರಡು, ರ್ < ಱ, ೞ್ < ಡ)
  right word:    ``avadharana`` (the particle -e), ``isu``, ``quotative``, ``negative``
                 (negative personal ending), ``motion`` (form of ಬರ್/ಪೋಗು/ಪೇೞ್)
"""
from __future__ import annotations

from . import lexicon
from . import samjna as S
from . import varna as V
from .prakriya import Prakriya, Term, derive_all

WORD, SUFFIX, COMPOUND = "word+word", "stem+suffix", "compound"

Y, VA = "ಯ್", "ವ್"
LABIAL_VOWELS = {"ಉ", "ಊ", "ಒ", "ಓ"}
# 58: shortened a-final first members that behave like particles
TRUNCATED = {"ಪೊಱಗು": "ಪೊಱ", "ಒಳಗು": "ಒಳ", "ಪೊಸತು": "ಪೊಸ", "ಪೞದು": "ಪೞ", "ಎಳದು": "ಎಳ"}
# 66: first members whose final consonant is a substitute (ādēśa)
ADESHA_FINAL = {"ಒರ್": "ಒಂದು", "ಓರ್": "ಒಂದು", "ಇರ್": "ಎರಡು", "ಈರ್": "ಎರಡು",
                "ಮಾರ್": "ಮಾಱು", "ಏರ್": "ಏಱು", "ಕಾೞ್": "ಕಾಡು", "ನಾೞ್": "ನಾಡು", "ಕೀೞ್": "ಕೆಳಗು",
                "ಕೋೞ್": "ಕೋಡು", "ಬೀೞ್": "ಬೀಡು", "ನೀೞ್": "ನೀಡು", "ಸೇೞ್": "ಸೇಡು"}
# ambiguous: ಬೇರ್ 'root' (original r) vs ಬೇರ್ < ಬೇಱು 'separate'
ADESHA_AMBIGUOUS = {"ಬೇರ್"}
DOUBLING_FINALS = S._c("ನಣಲಯಳ")
NEG_DOUBLING_EXTRA = S._c("ಮ")       # 224: ಅಮ್ + ಎವು → ಅಮ್ಮೆವು
ALWAYS_DOUBLE_ROOTS = {"ಉಯ್", "ನೆಯ್", "ಸುಯ್", "ಬಯ್"}      # 70
OPTIONAL_DOUBLE_ROOTS = {"ಆರಯ್"}                           # 70
NEVER_DOUBLE_ROOTS = {"ಕಳ್"}                               # 71 (ಮೇಣ್)
DOUBLING_AVYAYA = {"ಇನ್"}                                  # 69: indeclinables that do double
MOTION_STARTS = ("ಬರ್", "ಬಂದ", "ಬರ", "ಪೋ", "ಪೇೞ", "ಪೇಳ")    # 67 sentence level
S_TO_J = {"ಸುರಿಗೆ", "ಸೂರ್", "ಸೆಱಂಗು", "ಸೊಡರ್"}           # 68: s → j (lexical)
CH_NUMERAL = "ಸಾಸಿರ"
VOWEL_S_TO_J = {"ಸೊಡರ್"}                                  # 68: listed s → j after a vowel                                       # 68: s → ch
ASAHYA = ("ಸೆಗಣಿ", "ಹೇಲ", "ಹೇಲು", "ತುಲ್", "ಮಲ")             # 62: words that must not arise by joining


# ------------------------------------------------------------------ helpers
def origin(t: Term) -> str:
    if t.has(lexicon.SANSKRIT):
        return lexicon.SANSKRIT
    if t.has(lexicon.KANNADA, lexicon.TADBHAVA):
        return lexicon.KANNADA
    return lexicon.guess_origin(str(t)) if t.text and all(
        V.is_vowel(v) or V.is_consonant(v) or v in S.YOGAVAHA for v in t.text) else lexicon.KANNADA


def final_vowel_is_kannada(t: Term) -> bool:
    """Is the final vowel of ``t`` Kannada (dēśya or a Kannada ending)?

    Sanskrit stems never end in short e/o, and a Sanskrit word that ends in a Kannada
    case/verb ending (tag ``vibhakti`` or a recognisable ending) has a Kannada final vowel.
    """
    if t.has("vibhakti"):
        return True
    if origin(t) != lexicon.SANSKRIT:
        return True
    if t.last in ("ಎ", "ಒ"):
        return True
    s = str(t)
    return s.endswith(("ಅಲ್ಲಿ", "ದಲ್ಲಿ", "ನಲ್ಲಿ", "ಳಲ್ಲಿ"))


def syllables(t: Term) -> list[tuple[str, bool]]:
    """(vowel, heavy) for each syllable of the word."""
    out = []
    vs = t.text
    for k, v in enumerate(vs):
        if V.is_vowel(v):
            nxt = vs[k + 1:k + 3]
            heavy = v in S.DIRGHA or (nxt[:1] and nxt[0] in S.YOGAVAHA) or (
                len(nxt) == 2 and V.is_consonant(nxt[0]) and V.is_consonant(nxt[1])) or (
                k + 2 == len(vs) and V.is_consonant(vs[-1]))
            out.append((v, bool(heavy)))
    return out


def namarudhi_blocks_lopa(t: Term) -> bool:
    """52: lōpa must not destroy a short stem's identity (ಪಟು, ವಿಧು, ಮಡು, ಕುಡು, ನಡೆ …).

    Implemented as: a consonant-initial word of exactly two light syllables.
    """
    if not t.text or not V.is_consonant(t.text[0]) or t.has("vibhakti"):
        return False
    syl = syllables(t)
    return len(syl) == 2 and not syl[0][1] and t.last in S.HRASVA


def monosyllabic_short(t: Term) -> bool:
    if len(t.text) >= 2 and t.text[-1] == t.text[-2]:
        return False
    syl = [v for v in t.text if V.is_vowel(v)]
    return len(syl) == 1 and syl[0] in S.HRASVA


def _set(t: Term, script: str):
    t.text = V.to_varnas(script)


def _hiatus(p: Prakriya, rule: str, i: int, ctx: str, note: str = "no sandhi (prakṛtibhāva)"):
    r = p.terms[i + 1]
    if ctx == WORD:
        r.tags.add("sep")
    p.log(rule, note)


def _insert_glide(p: Prakriya, rule: str, i: int, glide: str, note=""):
    p.terms[i + 1].text.insert(0, glide)
    p.log(rule, note or ("ya-āgama" if glide == Y else "va-āgama"))


def _lopa(p: Prakriya, rule: str, i: int, note="lōpa of the preceding vowel"):
    p.terms[i].text.pop()
    p.log(rule, note)


# ------------------------------------------------------------------ main entry
def junction(p: Prakriya, i: int, ctx: str = WORD) -> None:
    """Apply sandhi between ``p.terms[i]`` and ``p.terms[i+1]``."""
    L, R = p.terms[i], p.terms[i + 1]
    if not L.text or not R.text:
        return
    # 58: ಪೊಱಗು → ಪೊಱ etc. as first member of a compound, then no vowel sandhi
    if ctx == COMPOUND and str(L) in TRUNCATED:
        p.run_at("58", i, lambda t: _set(t, TRUNCATED[str(L)]), "first member shortened to an a-final form")
        if V.is_vowel(R.first):
            _hiatus(p, "58", i, WORD, "no sandhi after ಪೊಱ/ಒಳ/ಪೊಸ/ಪೞ/ಎಳ")
            return
    a, b = L.last, R.first
    if V.is_vowel(b):
        if V.is_vowel(a):
            _vowel_vowel(p, i, ctx)
        else:
            _consonant_vowel(p, i, ctx)
    else:
        _before_consonant(p, i, ctx)


# ------------------------------------------------------------------ Sanskrit vowel sandhi
# Kēśirāja takes Sanskrit sandhi for granted inside Sanskrit compounds (the 2015 editor's
# note to sūtra 10 illustrates it: ನಿಜ+ಇಷ್ಟ → ನಿಜೇಷ್ಟ, ವಿದಿತ+ಉಭಯ → ವಿದಿತೋಭಯ).
_SKT_SAVARNA = {"ಅ": "ಆ", "ಆ": "ಆ", "ಇ": "ಈ", "ಈ": "ಈ", "ಉ": "ಊ", "ಊ": "ಊ", "ಋ": "ೠ", "ೠ": "ೠ"}
_SKT_GROUP = {"ಅ": "a", "ಆ": "a", "ಇ": "i", "ಈ": "i", "ಉ": "u", "ಊ": "u", "ಋ": "r", "ೠ": "r"}


def sanskrit_vowel_sandhi(a: str, b: str) -> list[tuple[list[str], str]]:
    """Result varṇas replacing (a, b) and the name of the Sanskrit sandhi."""
    ga, gb = _SKT_GROUP.get(a), _SKT_GROUP.get(b)
    if ga and ga == gb:
        return [([_SKT_SAVARNA[a]], "savarṇadīrgha")]
    if ga == "a":
        if gb == "i":
            return [(["ಏ"], "guṇa")]
        if gb == "u":
            return [(["ಓ"], "guṇa")]
        if gb == "r":
            return [(["ಅ", "ರ್"], "guṇa")]
        if b in ("ಏ", "ಐ", "ಎ"):
            return [(["ಐ"], "vṛddhi")]
        if b in ("ಓ", "ಔ", "ಒ"):
            return [(["ಔ"], "vṛddhi")]
    if ga == "i" and b in V.VOWELS:
        return [(["ಯ್", b], "yaṇ")]
    if ga == "u" and b in V.VOWELS:
        return [(["ವ್", b], "yaṇ")]
    if ga == "r" and b in V.VOWELS:
        return [(["ರ್", b], "yaṇ")]
    return []


# ------------------------------------------------------------------ vowel + vowel (52–58, 61, 64)
def _vowel_vowel(p: Prakriya, i: int, ctx: str) -> None:
    L, R = p.terms[i], p.terms[i + 1]
    a, b = L.last, R.first
    if ctx == COMPOUND and origin(L) == lexicon.SANSKRIT and origin(R) == lexicon.SANSKRIT:
        opts = sanskrit_vowel_sandhi(a, b)
        if opts and p.decide("10"):
            new, name = opts[0]
            L.text.pop()
            R.text[0:1] = new
            return p.log("10", f"Sanskrit {name} sandhi in a Sanskrit compound")

    # 56 / 64: particles, emphatic, doubt, pluta — no sandhi unless the emphatic is non-restrictive
    if L.has("nipata", "avadharana", "vishanke", "pluta") and not L.has("aniyoga"):
        return _hiatus(p, "56", i, WORD)
    if L.has("aniyoga"):
        p.log("64", "emphatic -e used non-restrictively: ordinary sandhi applies")
    # 57: emotive particles
    if L.has("emotive"):
        return _hiatus(p, "57", i, WORD)
    # 61: optional visandhi
    case61 = _sutra61_case(L, R)
    if case61 and p.decide("61"):
        return _hiatus(p, "61", i, WORD if ctx == WORD else SUFFIX, f"optional visandhi ({case61})")
    # 53 (second part): genitive -a + emphatic e → y, obligatorily
    if a == "ಅ" and L.has("genitive") and (R.has("avadharana") or str(R) == "ಎ"):
        return _insert_glide(p, "53", i, Y, "genitive -a + emphatic e: ya-āgama")
    # 54: a-stem + -isu → y (lexically, some stems take lōpa instead: ರಾಗಿಸು, sūtra 52)
    if a == "ಅ" and (R.has("isu") or (ctx == SUFFIX and str(R).startswith("ಇಸ"))):
        if p.decide("54"):
            return _insert_glide(p, "54", i, Y, "a-stem + -isu: ya-āgama")
        return _lopa(p, "52", i, "lōpa (lexical alternative to 54: ರಾಗಿಸು, ಭಾವಿಸು)")
    # 54: onomatopoeic a-word + quotative ಎನ್ → y
    if a == "ಅ" and L.has("anukrti") and (R.has("quotative") or str(R).startswith(("ಎಂ", "ಎನ"))):
        if p.decide("54"):
            return _insert_glide(p, "54", i, Y, "onomatopoeia + quotative: ya-āgama")
        return _lopa(p, "52", i)
    # 55: deictic ī + ಇವು/ಇದು → v
    if str(L) == "ಈ" and str(R).startswith(("ಇದ", "ಇವ")):
        return _insert_glide(p, "55", i, VA, "deictic ī: va-āgama, not ya")
    # 55 (editorial note, after Śabdānuśāsana 1.38): ā + labial vowel → v
    if a == "ಆ" and b in LABIAL_VOWELS and p.decide("55e"):
        return _insert_glide(p, "55e", i, VA, "ā + labial vowel: va-āgama (editorial, Śabdānuśāsana)")

    # long final vowels never undergo lōpa: y or v
    if a in S.DIRGHA:
        if a in ("ಊ", "ೠ", "ೡ", "ಔ"):
            return _insert_glide(p, "55", i, VA)
        if a == "ಓ" and origin(L) == lexicon.SANSKRIT and p.decide("55"):
            return _insert_glide(p, "55", i, VA, "Sanskrit ō-stem (ಗೋವಿನ): va-āgama")
        return _insert_glide(p, "53", i, Y)

    # short a: lōpa
    if a == "ಅ":
        return _lopa(p, "52", i)

    # short i, e, u, ṛ, o
    glide = Y if a in ("ಇ", "ಎ") else VA
    rule_ins = "53" if glide == Y else "55"
    if not final_vowel_is_kannada(L):
        return _insert_glide(p, rule_ins, i, glide, "Sanskrit stem: insertion is nitya (55)")
    if namarudhi_blocks_lopa(L):
        p.log("52", "lōpa blocked: it would destroy the identity of the word (nāma-rūḍhi)")
        return _insert_glide(p, rule_ins, i, glide)
    if L.has("vibhakti"):
        return _lopa(p, "52", i, "lōpa of the vowel of an ending")
    # Kannada: bahula (55) — insertion or lōpa
    if p.decide("55"):
        return _insert_glide(p, rule_ins, i, glide, "Kannada word: insertion (bahula, 55)")
    return _lopa(p, "52", i, "Kannada word: lōpa (bahula, 55)")


def _sutra61_case(L: Term, R: Term) -> str | None:
    if str(L) == "ಕರೆ" and str(R).startswith("ಅಲ"):
        return "ಕರೆ + -ಅಲ್"
    if str(L) == "ಇರ" and str(R).startswith("ಅದೆ"):
        return "ಇರ + -ಅದೆ"
    if L.has("padyardha"):
        return "half-verse boundary"
    if L.has("quote") or R.has("quote"):
        return "quoted sentence"
    if L.has("anukrti"):
        return "onomatopoeia"
    if R.first in ("ಋ", "ೠ"):
        return "before ṛ"
    return None


# ------------------------------------------------------------------ consonant + vowel (69–71)
def _consonant_vowel(p: Prakriya, i: int, ctx: str) -> None:
    L, R = p.terms[i], p.terms[i + 1]
    a = L.last
    case61 = _sutra61_case(L, R)
    if case61 and case61 in ("half-verse boundary", "quoted sentence", "onomatopoeia", "before ṛ") \
            and p.decide("61"):
        return _hiatus(p, "61", i, WORD if ctx == WORD else SUFFIX, f"optional visandhi ({case61})")
    if a == V.ANUSVARA:
        if L.has("acc") and ctx == WORD and len(L.text) > 2 and L.text[-2] == "ಅ" \
                and p.decide("118") is False:
            L.text[-2] = "ಆ"
            p.log("118", "accusative -a lengthened before a vowel (optional)")
        if L.has("m"):
            L.text[-1] = "ನ್"
        elif L.has("n") and origin(L) == lexicon.SANSKRIT:
            L.text[-1] = "ಮ್"
        elif p.decide("104"):
            L.text[-1] = "ಮ್"
        else:
            L.text[-1] = "ನ್"
        p.log("104", f"bindu before a vowel → {V.from_varnas([L.text[-1]])}")
        if L.last == "ಮ್" and ctx == WORD and not p.decide("104"):
            L.text[-1] = "ವ್"
            p.log("104", "m → v (optional)")
        a = L.last
    if L.has("augment", "plural", "case"):
        return
    if a in NEG_DOUBLING_EXTRA and L.has("dhatu") and R.has("negative") and monosyllabic_short(L):
        L.text.append(a)
        return p.log("71", "negative: final consonant doubled")
    if a in DOUBLING_FINALS and (monosyllabic_short(L) or (
            L.has("dhatu") and str(L) in ALWAYS_DOUBLE_ROOTS | OPTIONAL_DOUBLE_ROOTS)):
        _doubling(p, i, ctx)


def _doubling(p: Prakriya, i: int, ctx: str) -> None:
    L, R = p.terms[i], p.terms[i + 1]
    root, r = str(L), str(R)
    double = lambda rule, note="dvitva": p.run_at(rule, i, lambda t: t.text.append(t.text[-1]), note)
    if L.has("dhatu"):
        if root in NEVER_DOUBLE_ROOTS:
            return p.log("71", "ಕಳ್ never doubles")
        if R.has("negative") or r.startswith("ಅದೆ"):
            return double("71", "negative: obligatory doubling")
        if root in ALWAYS_DOUBLE_ROOTS:
            return double("70", "ಉಯ್/ನೆಯ್/ಸುಯ್/ಬಯ್ always double")
        if root in OPTIONAL_DOUBLE_ROOTS:
            return double("70") if p.decide("70") else p.log("70", "doubling declined (optional)")
        if r.startswith("ಅಲ"):
            if L.last == "ಯ್":
                return double("70") if p.decide("70") else p.log("70", "y-root before -al: no doubling")
            return p.log("70", "verbal root before -al: no doubling")
        if R.first == "ಎ":
            return p.log("70", "verbal root before e-initial suffix: no doubling")
        return double("69")
    if L.has("avyaya") and root not in DOUBLING_AVYAYA:
        return p.log("69", "indeclinable: no doubling")
    if origin(L) == lexicon.SANSKRIT:
        return
    double("69", "short monosyllable: final consonant doubled before a vowel")


# ------------------------------------------------------------------ before a consonant (59–68)
def _before_consonant(p: Prakriya, i: int, ctx: str) -> None:
    L, R = p.terms[i], p.terms[i + 1]
    a, b = L.last, R.first
    changed = False
    # 42/183/209: ṟ is written r before a consonant
    if a == "ಱ್" and ctx in (SUFFIX, COMPOUND):
        L.text[-1] = "ರ್"
        p.log("42", "ṟ written r before a consonant")
        a = "ರ್"
    # 158: ṇ + n → ṇṇ (across words and in compounds)
    if a == "ಣ್" and b == "ನ್":
        R.text[0] = "ಣ್"
        return p.log("158", "n after ṇ becomes ṇ (attested, but not euphonious)")
    # 161: anusvāra before a stop may be written as the homorganic nasal (optional)
    if a == V.ANUSVARA and b in S.NASAL_OF_VARGA and p.decide("161") is False:
        L.text[-1] = S.NASAL_OF_VARGA[b]
        return p.log("161", "homorganic nasal (optional)")
    # 161: word-final m/n written as anusvāra
    if a in ("ಮ್", "ನ್") and ctx == WORD:
        L.text[-1] = V.ANUSVARA
        p.log("161", "final m/n written as anusvāra")
    # 63: ರ್ + ರ never fused
    if a == "ರ್" and b == "ರ್":
        return _hiatus(p, "63", i, WORD, "r + r must not be fused (śrutikaṣṭa)")
    is_compound = ctx == COMPOUND
    adesha = L.has("adesha") or str(L) in ADESHA_FINAL
    if str(L) in ADESHA_AMBIGUOUS and not L.has("sahaja"):
        adesha = p.decide("66")  # ಬೇರ್ < ಬೇಱು (substitute) or ಬೇರ್ 'root' (original)
    sahaja_ok = V.is_vowel(a) or a == V.ANUSVARA or not adesha

    if is_compound and b in ("ಕ್", "ತ್", "ಪ್", "ಬ್", "ಮ್"):
        if adesha and b in ("ಕ್", "ತ್", "ಪ್"):
            p.log("66", "no voicing after a substitute final (ಒರ್/ಇರ್, ರ್<ಱ, ೞ್<ಡ)")
            if b in ("ಪ್",):
                p.log("67", "no v after a substitute consonant")
            return _join_or_sep(p, i, ctx, changed)
        # p: 65 (→b) and 67 (→v) compete; both bahula
        if b == "ಪ್" and sahaja_ok:
            if p.decide("67"):
                R.text[0] = "ವ್"
                p.log("67", "p → v in a compound (bahula)")
                return
            if p.decide("65"):
                R.text[0] = "ಬ್"
                p.log("65", "p → b in a compound (bahula)")
                return
            p.log("65", "no change (bahula)")
            return
        if b in ("ಕ್", "ತ್"):
            if p.decide("65"):
                R.text[0] = S.VOICED_OF[b]
                p.log("65", f"{V.from_varnas([b])} → {V.from_varnas([R.text[0]])} in a compound (bahula)")
            else:
                p.log("65", "no voicing (bahula)")
            return
        if b in ("ಬ್", "ಮ್"):
            if not sahaja_ok:
                p.log("67", "no v after a substitute consonant")
                return
            if p.decide("67"):
                R.text[0] = "ವ್"
                p.log("67", "b/m → v in a compound (bahula)")
            else:
                p.log("67", "no change (bahula)")
            return
    # 67 at sentence level: before forms of ಬರ್ / ಪೋಗು / ಪೇೞ್
    if ctx == WORD and b in ("ಪ್", "ಬ್") and (R.has("motion") or str(R).startswith(MOTION_STARTS)) \
            and sahaja_ok and p.decide("67"):
        R.text[0] = "ವ್"
        p.log("67", "p/b → v across words before a verb of motion (bahula)")
        return
    # 68 (bahula extension): a few compounds change s after a vowel (ಮುಚ್ಚೀರೆ, ಮುಚ್ಚಾಲ್, ತುಡುಜೊಡರ್)
    if b == "ಸ್" and V.is_vowel(a) and ctx in (COMPOUND, WORD):
        if str(L) == "ಮೂ" and p.decide("68"):
            L.text[-1] = "ಉ"
            R.text[0:1] = ["ಚ್", "ಚ್"]
            p.log("68", "ಮೂ + s-: ಮುಚ್ಚ- (bahula, lexical)")
            return
        if str(R) in VOWEL_S_TO_J and p.decide("68"):
            R.text[0] = "ಜ್"
            p.log("68", "s → j after a vowel (bahula, lexical)")
            return
    # 68: s → c / j / ch after a consonant other than y, l
    if b == "ಸ್" and ctx in (COMPOUND, WORD) and (V.is_consonant(a) or a == V.ANUSVARA) \
            and a not in ("ಯ್", "ಲ್"):
        r = str(R)
        if r.startswith(CH_NUMERAL):
            R.text[0:1] = ["ಛ್"] if p.decide("68") else ["ಚ್", "ಛ್"]
            p.log("68", "ಸಾಸಿರ: s → ch (obligatory; written ಛ or ಚ್ಛ)")
            return
        if any(r.startswith(w) for w in S_TO_J):
            if p.decide("68"):
                R.text[0] = "ಜ್"
                p.log("68", "s → j (lexical)")
                return
        elif p.decide("68"):
            R.text[0] = "ಚ್"
            p.log("68", "s → c after a consonant (bahula)")
            return
        elif a == V.ANUSVARA and p.decide("166"):
            R.text[0] = "ಜ್"
            p.log("166", "s → j after the anusvāra")
            return
        p.log("68", "no change (bahula)")
        return _join_or_sep(p, i, ctx, changed)
    return _join_or_sep(p, i, ctx, changed)


def _join_or_sep(p: Prakriya, i: int, ctx: str, changed: bool):
    if ctx == WORD and not changed:
        p.terms[i + 1].tags.add("sep")


# ------------------------------------------------------------------ dōṣa checks (59, 60, 62)
def check_asahya(left: str, right: str) -> str | None:
    """62: joining must not create an indecent/ugly word across the boundary."""
    joined = left + right
    for bad in ASAHYA:
        k = joined.find(bad)
        while k != -1:
            if k < len(left) < k + len(bad):
                return bad
            k = joined.find(bad, k + 1)
    return None


def check_short_before_conjunct(left: str, right: str) -> str | None:
    """59/60: a short final vowel before a conjunct-initial word is made heavy; letting it
    scan light is a sandhi-dōṣa, tolerated by some only when the conjunct contains r."""
    lv, rv = V.to_varnas(left), V.to_varnas(right)
    if lv and V.is_vowel(lv[-1]) and lv[-1] in S.HRASVA and len(rv) > 1 \
            and V.is_consonant(rv[0]) and V.is_consonant(rv[1]):
        return "r-conjunct (śithila allowed by some, 59; avoided by refined poets, 60)" \
            if "ರ್" in rv[:3] else "short final before a conjunct (59)"
    return None


# ------------------------------------------------------------------ public API
def make_term(word: str, origin_: str | None = None, tags=()) -> Term:
    t = Term.make(word, *tags)
    if origin_:
        t.tags.add(origin_)
    return t


def join(left: str, right: str, *, context: str = WORD, left_origin: str | None = None,
         right_origin: str | None = None, left_tags=(), right_tags=()) -> list[Prakriya]:
    """All sandhi results of ``left`` + ``right`` with their derivations."""
    def build(p: Prakriya):
        p.terms = [make_term(left, left_origin, left_tags), make_term(right, right_origin, right_tags)]
        p.log("start")
        junction(p, 0, context)
        bad = check_asahya(left, right)
        if bad and not p.terms[1].has("sep"):
            p.warn("62", f"joined form contains '{bad}' (asahyōkti): keep the words apart")
    return derive_all(build)


def results(left: str, right: str, **kw) -> set[str]:
    return {p.result() for p in join(left, right, **kw)}


def sanskrit_join(left: str, right: str) -> list[str]:
    """Sanskrit-compound join with Sanskrit vowel sandhi (editorial note to sūtra 10)."""
    lv, rv = V.to_varnas(left), V.to_varnas(right)
    if lv and rv and V.is_vowel(lv[-1]) and V.is_vowel(rv[0]):
        return [V.from_varnas(lv[:-1] + new + rv[1:]) for new, _ in sanskrit_vowel_sandhi(lv[-1], rv[0])]
    return []
