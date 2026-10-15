"""Samāsa-prakaraṇa (sūtras 162–196): compounds.

``compound(left, right, kind=None)`` returns every derivation of the compound of two
members. ``left`` may be given inflected (ತೊಱೆಯ, ನೀರಂ, ಪುಯ್ಯಲ್ಗೆ): its case ending and
augment are deleted first (162–163). ``kind`` restricts the compound type:
tatpurusha, karmadharaya, dvigu, bahuvrihi, dvandva, avyayibhava, kriya, gamaka,
amredita (repetition), vipsa (intensive), anyonya (reciprocal combat). With ``kind=None``
every rule whose lexical conditions hold is tried.

``check_arisamasa(left, right, kind)`` implements the prohibition of 174.
"""
from __future__ import annotations

from . import lexicon
from . import samjna as S
from . import varna as V
from .prakriya import Prakriya, Term, derive_all
from .sandhi import COMPOUND, junction

KINDS = ("tatpurusha", "karmadharaya", "dvigu", "bahuvrihi", "dvandva", "avyayibhava",
         "kriya", "gamaka", "amredita", "vipsa", "anyonya")

# 166 avyayībhāva first members
AVYAYIBHAVA = {"ಅಡಿ": "ಅಂ", "ಮೇಗು": "ಮೇಂ", "ಮುಂದು": "ಮುಂ", "ಪಿಂದು": "ಪಿಂ", "ಕೆೞಗು": "ಕಿೞ್",
               "ಕೆಳಗು": "ಕಿೞ್", "ಪೆಱಗು": "ಪಿಂತು"}
# 169 gamaka demonstratives
GAMAKA_DEM = {"ಅದು": "ಆ", "ಇದು": "ಈ", "ಉದು": "ಊ", "ಆವುದು": "ಆವ", "ಎಲ್ಲದು": "ಎಲ್ಲ"}
# 167: nouns whose bindu may not be dropped in kriyāsamāsa (meaning would be lost)
BINDU_REQUIRED = {"ಪಯಣ", "ಪಸರ", "ಗಡಣ", "ಕೆಲಸ", "ಕರಗ"}
# 177: lexical reductions of a first member
REDUCED_177 = {"ಏತರ್ಕೆ": "ಏ", "ಏನಂ": "ಏ", "ಕಳನಂ": "ಕಳ"}
# 181 before vowel / consonant
VOWEL_FORM_181 = {"ಕಡಿದು": "ಕಟ್", "ನಿಡಿದು": "ನಿಟ್", "ನಡು": "ನಟ್", "ಕಿಱಿದು": "ಕಿತ್", "ಕುಱು": "ಕುತ್",
                  "ಕಡು": "ಕಟ್", "ನಿಡು": "ನಿಟ್"}
CONS_FORM_181 = {"ಕಡಿದು": "ಕಡು", "ನಿಡಿದು": "ನಿಡು", "ನಡು": "ನಡು", "ಕಿಱಿದು": "ಕಿಱು", "ಕುಱು": "ಕುಱು",
                 "ಕಡು": "ಕಡು", "ನಿಡು": "ನಿಡು"}
# 182 colour words
COLOUR_182 = {"ಪಚ್ಚನೆ": ("ಪಂ", "ಪಸು", "ಪಚ್ಚ್"), "ಕೆಚ್ಚನೆ": ("ಕೆಂ", "ಕಿಸು", "ಕೇಸ್"),
              "ಬೆಚ್ಚನೆ": ("ಬೆಂ", "ಬಿಸು", None)}
# 184 substitutes
SUBST_184 = {"ಕಿಱಿದು": "ಕುಱು", "ಬೆಟ್ಟಿತು": "ಬಿಱು", "ಕೊಂಕು": "ಕುಡು"}
# 187–192 numerals
NUM_COMBINING = {"ಒಂದು": ["ಒರ್"], "ಎರಡು": ["ಇರ್", "ಎರೞ್"], "ನಾಲ್ಕು": ["ನಾಲ್"], "ಅಯ್ದು": ["ಅಯ್"],
                 "ಐದು": ["ಅಯ್"], "ಆಱು": ["ಅಱು"], "ಏೞು": ["ಏಲ್"], "ಎಂಟು": ["ಎಣ್"]}
# 171 verbal compounds without bindu
NO_BINDU_171 = {"ಸುಡುಗಾಡು", "ಇಡುಗಿಚ್ಚು", "ಅಡುಗೂೞ್", "ಉಡುಗೊಱೆ", "ಮಾಱುದಾಂಟು", "ಬಿಡುಗಣ್",
                "ಬಿಡುವಾಯ್", "ತುಡುಜೊಡರ್", "ಅಱುಗೆಱೆ"}
# 174 mixed compounds sanctioned by old poets (closed list) and exempt first members
SANCTIONED_MIXED = {"ಕಡುರಾಗಂ", "ಮೊಗರಾಗಂ", "ಅಱಿಕೆನಾಯಕಂ", "ಗುಣಕಱುಗೊಂಡಂ", "ಕಟ್ಟೇಕಾಂತಂ", "ಕೂರಸಿ",
                    "ಮಾರ್ಬಲಂ", "ಇರ್ಬಲಂ", "ಪೆರ್ಬಲಂ", "ಅಱಿಜನಂ", "ತುರುಗದಳಂ", "ಮಂಗಳವಸದನಂ",
                    "ಮಂಗಳವಱಲಕೆ", "ಅರಸುಗುಣಂ", "ಕಡುದರ್ಪಂ", "ಕಡುತಪಂ", "ಗಜದುೞಿ", "ರಾಯಕೋಳಾಹಳಂ",
                    "ಕಾರ್ಗಾಲಂ", "ಕಾರ್ಗ್ಗಾಲಂ"}
ARISAMASA_EXEMPT_FIRST = {"ಎಲ್ಲ", "ಎಲ್ಲಾ", "ಮಾ"}


def _vs(s: str) -> list[str]:
    return V.to_varnas(s)


# ---------------------------------------------------------------- 162–163: strip inflection
def strip_case(word: str) -> list[tuple[str, str]]:
    """Possible (stem, note) readings of an inflected first member (162–163)."""
    w = V.normalize(word)
    out = [(w, "uninflected")]
    def add(stem, note):
        if stem and (stem, note) not in out:
            out.append((stem, note))
    if w.endswith("ಂ") and len(w) > 2:
        add(w[:-1], "nom. -ṃ dropped")
        if w.endswith(("ನಂ", "ಮಂ")):
            add(w[:-2], "acc. -n/m-aṃ dropped")
        if w.endswith("ಯಂ"):
            add(w[:-2], "acc. -yaṃ dropped")
        base = _vs(w)[:-2]       # consonant stem + aṃ
        if base and V.is_consonant(base[-1]):
            add(V.from_varnas(base), "acc. -aṃ dropped")
            if len(base) > 1 and base[-1] == base[-2]:
                add(V.from_varnas(base[:-1]), "acc. -aṃ dropped (doubling undone)")
    for suf, note in (("ಯ", "gen. -ya dropped"), ("ದ", "gen. -da dropped"), ("ನ", "gen. -na dropped"),
                      ("ಿನ", "gen. -ina dropped"), ("ಱ", "gen. -aṟa dropped"), ("ಣ", "gen. -aṇa dropped"),
                      ("ಗೆ", "dat. -ge dropped"), ("ಕ್ಕೆ", "dat. -kke dropped"), ("ಂಗೆ", "dat. -ṃge dropped")):
        if w.endswith(suf) and len(w) > len(suf) + 1:
            stem = w[: -len(suf)]
            if suf == "ಿನ":
                add(stem + "ು", note)
            elif suf == "ಱ":
                add(stem[:-1] + "ು" if stem.endswith("ಱ") else stem, note)
                add(stem + "ು", note)
            else:
                add(stem, note)
                if suf in ("ದ", "ನ", "ಣ"):
                    add(stem + "ು", note)
    vs = _vs(w)
    if len(vs) > 2 and vs[-1] == "ಅ" and V.is_consonant(vs[-2]):
        add(V.from_varnas(vs[:-1]), "gen. -a dropped (consonant stem)")
    return out


def check_arisamasa(left: str, right: str, kind: str | None = None, result: str | None = None) -> str | None:
    """174: a compound must not mix a Kannada and a Sanskrit member, except kriyāsamāsa,
    gamaka, titles, ಎಲ್ಲ/ಮಾ, and the compounds sanctioned by earlier poets."""
    if kind in ("kriya", "gamaka") or left in ARISAMASA_EXEMPT_FIRST:
        return None
    if result and (result in SANCTIONED_MIXED or result.rstrip("ಂ") + "ಂ" in SANCTIONED_MIXED):
        return None
    lo, ro = lexicon.guess_origin(left), lexicon.guess_origin(right.rstrip("ಂ"))
    if {lo, ro} == {lexicon.KANNADA, lexicon.SANSKRIT}:
        return f"arisamāsa: {left} ({lo}) + {right} ({ro})"
    return None


# ---------------------------------------------------------------- left-member variants
def _left_variants(left: str, right: str, kind: str | None):
    """Yield (rule, new_left, note, extra_tags) for the first member."""
    r_vowel = V.is_vowel(_vs(right)[0])
    yield ("162", left, "first member as stem", set())
    if left in AVYAYIBHAVA and kind in (None, "avyayibhava"):
        new = AVYAYIBHAVA[left]
        if left in ("ಕೆೞಗು", "ಕೆಳಗು") and right.startswith("ನ"):
            new = "ಕಿನ್"
        yield ("166", new, "avyayībhāva first member", set())
    if left in ("ಪೆಱಗು",):
        yield ("173", "ಪೆಡಂ", "ಪೆಱಗು → ಪೆಡಂ", set())
        yield ("173", "ಪೆಡ", "ಪೆಱಗು → ಪೆಡ (without bindu)", set())
    if left in GAMAKA_DEM and kind in (None, "gamaka"):
        yield ("169", GAMAKA_DEM[left], "demonstrative in gamaka", {"sep"})
    if left.endswith("ಿದು") and kind in (None, "gamaka"):
        yield ("168", V.from_varnas(_vs(left)[:-2] + ["ಯ್", "ಅ"]), "gamaka: quality word + ia", {"sep"})
    if left in VOWEL_FORM_181:
        yield ("181", VOWEL_FORM_181[left] if r_vowel else CONS_FORM_181[left], "181 form", set())
        if left == "ಕಿಱಿದು" and r_vowel:
            yield ("181", "ಕುತ್", "ಕಿಱಿದು → ಕುಱು → ಕುತ್ before a vowel", set())
    if left in REDUCED_177:
        yield ("177", REDUCED_177[left], "first member reduced (lexical)", set())
    for num, forms in NUM_COMBINING.items():           # numeral at the end of a numeral compound
        if left.endswith(num) and left != num:
            for f in forms:
                yield ("189", left[: -len(num)] + f, "final numeral in combining form", set())
    if left in SUBST_184 and not r_vowel:
        yield ("184", SUBST_184[left], "ādēśa", set())
    if left in COLOUR_182:
        m, su, pre_v = COLOUR_182[left]
        if r_vowel and pre_v:
            yield ("182", pre_v, "colour word before a vowel", set())
        elif not r_vowel:
            yield ("182", m, "colour word: -ccane → bindu", set())
            yield ("182", su, "colour word: -su form", set())
            if left == "ಕೆಚ್ಚನೆ":
                yield ("182", "ಚೆಂ", "ಕೆಚ್ಚನೆ → ಚೆಂ", set())
            if su == "ಪಸು":
                yield ("182", "ಪಸುಂ", "ಪಸು with bindu", set())
    if left in NUM_COMBINING:
        for f in NUM_COMBINING[left]:
            if r_vowel and f in ("ಒರ್", "ಇರ್"):
                yield ("180", {"ಒರ್": "ಓರ್", "ಇರ್": "ಈರ್"}[f], "numeral lengthened before a vowel", set())
            yield ("187" if left in ("ಒಂದು", "ಎರಡು") else "189", f, "numeral combining form", set())
    if left == "ಮೂಱು":
        if r_vowel:
            yield ("188", "ಮುಯ್", "ಮೂಱು → ಮುಯ್ before a vowel", set())
        else:
            yield ("188", "ಮೂ", "ಮೂಱು → ಮೂ", set())
            yield ("188", "ಮು", "ಮೂಱು → ಮು + doubling", {"geminate"})
    if left == "ಒಂಬತ್ತು":
        if right.startswith("ಪತ್ತು"):
            yield ("190", "ತೊಂ", "ಒಂಬತ್ತು → ತೊಂ", set())
        elif right.startswith(("ನೂಱು", "ಸಾಸಿರ")):
            yield ("190", "ಒಂಬಯ್", "ಒಂಬತ್ತು → ಒಂಬಯ್", set())
    if left == "ಪತ್ತು":
        if right.startswith("ಸಾಸಿರ"):
            yield ("191", "ಪಯಿಂ", "ಪತ್ತು → ಪಯಿನ್", set())
        elif right in ("ಒಂದು", "ಎರಡು"):
            yield ("192", "ಪನ್ನ್", "ಪತ್ತು → ಪನ್", set())
        elif right in ("ಮೂಱು", "ನಾಲ್ಕು"):
            yield ("192", "ಪದಿ", "ಪತ್ತು → ಪದಿ", set())
        elif r_vowel and right != "ಒಂಬತ್ತು":
            yield ("192", "ಪದಿನ್", "ಪತ್ತು → ಪದಿ + n", set())
    if left in ("ನೂಱು", "ಸಾಸಿರ"):
        yield ("191", left[:-1] + "ರ್" if left == "ನೂಱು" else "ಸಾಸಿರ್", "final vowel lost (rare)", set())
    if left in ("ಎಲ್ಲ",):
        yield ("175", "ಎಲ್ಲಾ", "ಎಲ್ಲ lengthened", {"sep"})
        yield ("175", "ಎಲ್ಲ", "ಎಲ್ಲ before a noun", {"sep"})
    if left in ("ಮಹತ್", "ಮಹಾ"):
        yield ("175", "ಮಾ", "mahat → ಮಾ", set())
    # 179 adjective truncation (-ಇತು/-ಇದು/-ಇತ್ತು): from the penultimate vowel onward
    lv = _vs(left)
    if left.endswith(("ಿತು", "ಿದು", "ಿತ್ತು")) and left not in VOWEL_FORM_181:
        k = len(lv) - 1
        while k >= 0 and not V.is_vowel(lv[k]):
            k -= 1
        k -= 1
        while k >= 0 and not V.is_vowel(lv[k]):
            k -= 1
        root = lv[:k]
        if root and V.is_consonant(root[-1]):
            # geminate root-final consonant simplifies before a consonant (ಒಳ್ಳಿತು → ಒಳ್)
            if len(root) > 1 and root[-1] == root[-2] and not r_vowel:
                root = root[:-1]
            yield ("179", V.from_varnas(root), "adjective truncated", set())
            if root[1:2] == ["ಇ"] or root[:1] == ["ಇ"]:
                alt = list(root)
                idx = alt.index("ಇ")
                alt[idx] = "ಎ"
                yield ("179", V.from_varnas(alt), "adjective truncated, i → e (bahula)", set())
                if r_vowel:
                    alt2 = list(alt)
                    alt2[idx] = "ಏ"
                    yield ("180", V.from_varnas(alt2), "first vowel lengthened before a vowel", set())
            if left == "ಇನಿದು":
                yield ("180", "ಈಂ", "ಇನಿದು → ಈಂ (lengthened)", set())
            # 178: karmadhāraya medial a (ಬಟ್ಟಿತ್ತು → ಬಟ್ಟ); 176 with bindu (ಕಮ್ಮಿತು → ಕಮ್ಮಂ)
            full = lv[:k]
            yield ("178", V.from_varnas(full + ["ಅ"]), "karmadhāraya: medial a", set())
            if not r_vowel:
                yield ("176", V.from_varnas(full + ["ಅ", V.ANUSVARA]), "adjective + a + bindu", set())

    # gamaka (168): verbal participles before a noun
    if kind in (None, "gamaka") and not r_vowel:
        try:
            from .akhyata import participles
            for part, note in participles(left):
                yield ("168", part, f"gamaka: {note}", {"sep"})
        except Exception:
            pass
    # 183 final ḍu → ḻ, ṟu → r before a consonant
    if not r_vowel and len(lv) > 2 and V.is_vowel(lv[-1]) and lv[-2] in ("ಡ್", "ಱ್"):
        yield ("183", V.from_varnas(lv[:-2] + (["ೞ್"] if lv[-2] == "ಡ್" else ["ರ್"])),
               "final ḍu → ḻ / ṟu → r", {"adesha"})
    # 176/177: final syllable elision (+ optional bindu); ನಡು → ನಟ್ಟೆ
    if len(lv) >= 3 and V.is_vowel(lv[-1]) and V.is_consonant(lv[-2]):
        trunc = lv[:-2]
        yield ("176", V.from_varnas(trunc), "final syllable elided (bahula)", set())
        if V.is_vowel(trunc[-1]):
            yield ("176", V.from_varnas(trunc + [V.ANUSVARA]), "final syllable elided + bindu", set())
    if left == "ನಡು":
        yield ("176", "ನಟ್ಟೆ", "ನಡು → ನಟ್ಟೆ", set())
    if left.endswith("ಣ") and len(left) > 2:      # ತೆಂಕಣ → ತೆಂ (176)
        yield ("176", left[:-2] if left.endswith("ಕಣ") else left[:-1], "augment and final elided", set())
    # 167/170/172 bindu on the first member
    if V.is_vowel(lv[-1]) and lv[-1] in ("ಅ", "ಉ") and not r_vowel:
        yield ("167", left + "ಂ", "bindu on the first member", set())
    if lv[-1] == "ಇ" and not r_vowel:
        yield ("170", left + "ಯುಂ", "i-final verbal stem + uṃ", set())
    if lv[-1] in ("ನ್", "ಣ್") and not r_vowel:
        yield ("172", V.from_varnas(lv + ([lv[-1]] if lv[-1] == "ಣ್" else []) + ["ಅ", V.ANUSVARA]),
               "n/ṇ-final + a + bindu", set())
    if lv[-1] == "ಳ್" and not r_vowel:
        yield ("172", V.from_varnas(lv + ["ಳ್", "ಉ", V.ANUSVARA]), "ḷ-final + u + bindu", set())
    # 180 doubling of ಣ್ ಟ್ ಳ್ ನ್ ತ್ before a vowel
    if r_vowel and lv[-1] in ("ಣ್", "ಟ್", "ಳ್", "ನ್", "ತ್") and (len(lv) < 2 or lv[-2] != lv[-1]):
        yield ("180", V.from_varnas(lv + [lv[-1]]), "final consonant doubled before a vowel", set())


# ---------------------------------------------------------------- main
def compound(left: str, right: str, kind: str | None = None, left_origin: str | None = None,
             right_origin: str | None = None, allow_arisamasa: bool = False) -> list[Prakriya]:
    left, right = V.normalize(left), V.normalize(right)
    if " " in left:                      # a phrase: compound with its last word
        prefix, last = left.rsplit(" ", 1)
        out = compound(last, right, kind, left_origin, right_origin, allow_arisamasa)
        for p in out:
            p.terms.insert(0, Term.make(prefix.replace(" ", "")))
            p.terms[1].tags.add("sep")
        return out
    if right == "ಕೊಲ್ವ":                 # 186: -ಕೊಲ್ವ → -ಕುಲಿ in bahuvrīhi
        right = "ಕುಲಿ"
    results: list[Prakriya] = []
    seen = set()
    if "ೆಯ್" in right and not right.endswith("ೆಯ್"):          # 157: ay → ai in the second member
        results.extend(compound(left, right.replace("ೆಯ್", "ೈ", 1), kind, left_origin, right_origin,
                                allow_arisamasa))
    # special whole-compound patterns
    if left == right or (kind in ("vipsa", "anyonya", "amredita")):
        results.extend(_repetition(left, right, kind))
    for stem, snote in strip_case(left):
        for rule, new_left, note, tags in _left_variants(stem, right, kind):
            key = (new_left, tuple(sorted(tags)))
            if key in seen:
                continue
            seen.add(key)
            results.extend(derive_all(_build, left, stem, snote, rule, new_left, note, tags, right, kind))
    # 167/171: bindu constraints
    plain = {p.result() for p in results if "167" not in [h.rule for h in p.history]}
    if plain & NO_BINDU_171:
        results = [p for p in results if not any(h.rule in ("167", "170", "172") for h in p.history)]
    stems = {s for s, _ in strip_case(left)}
    if kind == "kriya" and (stems & BINDU_REQUIRED or any(
            lexicon.guess_origin(s) == lexicon.SANSKRIT and s.endswith(("ಅ",) ) or
            (lexicon.guess_origin(s) == lexicon.SANSKRIT and V.to_varnas(s)[-1] == "ಅ") for s in stems)):
        results = [p for p in results if V.ANUSVARA in p.terms[0].text or not V.is_vowel(p.terms[0].text[-1] if p.terms[0].text else "ಅ")]
    # 186: bahuvrīhi endings
    if kind == "bahuvrihi":
        extra = []
        for p in results:
            for q in bahuvrihi(p.result().replace(" ", "")):
                q.history = p.history + q.history
                extra.append(q)
        results = results + extra
    # 105: a-final compounds also in their nominative citation form
    for p in list(results):
        if p.terms and p.terms[-1].text and p.terms[-1].last == "ಅ" and not p.terms[-1].has("sep"):
            q = Prakriya(path=[])
            q.terms = [t.copy() for t in p.terms] + [Term.make("ಂ")]
            q.history = list(p.history)
            q.log("105", "nominative singular -ṃ")
            results.append(q)
    if not allow_arisamasa:
        kept = []
        for p in results:
            bad = check_arisamasa(_first(p), right, kind or ("gamaka" if p.has_tag("gamaka") else None),
                                  p.result())
            if bad and not p.terms[-1].has("sep"):
                continue
            kept.append(p)
        results = kept
    return results


def _first(p: Prakriya) -> str:
    return p.history[0].result.split(" + ")[0] if p.history else ""


def _build(p: Prakriya, orig, stem, snote, rule, new_left, note, tags, right, kind):
    L = Term.make(orig, "kannada" if lexicon.guess_origin(stem) != lexicon.SANSKRIT else "sanskrit")
    R = Term.make(right)
    p.terms = [L, R]
    p.log("start")
    if stem != orig:
        L.text = _vs(stem)
        p.log("162", f"case ending removed ({snote})")
    if rule != "162" or new_left != stem:
        L.text = _vs(new_left)
        p.log(rule, note)
    if rule in ("168", "169"):
        p.tags.add("gamaka")
    if "adesha" in tags or (rule in ("187",) and V.is_consonant(L.last)):
        L.tags.add("adesha")
    if "sep" in tags:
        R.tags.add("sep")
        return
    if "geminate" in tags and V.is_consonant(R.first):
        R.text.insert(0, R.first)
        p.log("188", "following consonant doubled")
        return
    # 180: ṇ ṭ ḷ n t doubled before a vowel (obligatory after the 181 forms)
    if R.text and V.is_vowel(R.first) and L.last in ("ಣ್", "ಟ್", "ಳ್", "ನ್", "ತ್") and \
            (len(L.text) < 2 or L.text[-2] != L.last) and (rule == "181" or p.decide("180") is False):
        L.text.append(L.last)
        p.log("180", "final consonant doubled before a vowel")
    # 161/189: nasal assimilation (ನ್/ಂ + ಮ → ಮ್ಮ; ಣ್ + ದ → ಣ್ಣ)
    if R.text and R.first == "ಮ್" and L.last in ("ನ್", V.ANUSVARA):
        L.text[-1] = "ಮ್"
        p.log("161", "nasal assimilated before m")
    elif R.text and R.first == "ದ್" and L.last == "ಣ್":
        R.text[0] = "ಣ್"
        p.log("189", "d assimilated to ṇ")
        return
    # 184: consonant after ರ್ doubled (optional orthography)
    junction(p, 0, COMPOUND)
    # 161: final m/n of the first member written as anusvāra before a consonant
    if L.text and L.last in ("ನ್", "ಮ್") and R.text and V.is_consonant(R.first) and R.first not in ("ನ್", "ಮ್") \
            and not (len(L.text) > 1 and L.text[-2] == L.last):
        L.text[-1] = V.ANUSVARA
        p.log("161", "final m/n written as anusvāra")
        if R.first in ("ಕ್", "ತ್", "ಪ್") and p.decide("65"):
            R.text[0] = S.VOICED_OF[R.first]
            p.log("65", "voicing after the anusvāra")
    if L.last == "ರ್" and R.text and V.is_consonant(R.first) and R.first != "ರ್" and p.decide("184") is False:
        R.text.insert(0, R.first)
        p.log("184", "consonant after rēpha doubled")


def _repetition(left: str, right: str, kind) -> list[Prakriya]:
    out = []
    lv, rv = _vs(left), _vs(right)

    def mk(rule, text, note):
        p = Prakriya([Term.make(left), Term.make(right)])
        words = text.split(" ")
        p.terms = [Term.make(w) for w in words]
        for t in p.terms[1:]:
            t.tags.add("sep")
        p.log(rule, note)
        out.append(p)
    # 185 reciprocal combat: X-ā-X-i
    if left == right and V.is_vowel(lv[-1]) or (left == right and V.is_consonant(lv[-1])):
        a = lv[:-1] + ["ಆ"] if V.is_vowel(lv[-1]) else lv + ["ಆ"]
        b = rv[:-1] + ["ಇ"] if V.is_vowel(rv[-1]) else rv + ["ಇ"]
        mk("185", V.from_varnas(a + b), "reciprocal-combat bahuvrīhi")
    # 193 intensive: -ನೆ dropped in the first copy; ನಡು/ಕಡೆ → ನಟ್ಟ/ಕಟ್ಟ
    if left == right and left.endswith("ನೆ"):
        mk("193", left[:-2] + right, "intensive: first -ne dropped")
    if left == right and left in ("ನಡು", "ಕಡೆ"):
        mk("193", {"ನಡು": "ನಟ್ಟ", "ಕಡೆ": "ಕಟ್ಟ"}[left] + right, "intensive: ḍ → ṭṭ")
    # 194 ತುದಿ, ಮೊದಲ್
    if left == right and left in ("ತುದಿ", "ಮೊದಲ್"):
        mk("194", {"ತುದಿ": "ತುತ್ತ", "ಮೊದಲ್": "ಮೊತ್ತ"}[left] + right, "emphatic repetition")
    # 177 ತಮ್ಮ ತಮ್ಮ → ತಂತಮ್ಮ
    if left == right and left == "ತಮ್ಮ":
        mk("177", "ತಂತಮ್ಮ", "first copy reduced to bindu")
    # 195 repetition with ordinary sandhi (or simply juxtaposed)
    from .sandhi import join, WORD
    mk("195", left + " " + right, "repetition, words kept apart")
    for p in join(left, right, context=WORD):
        p.history.append(type(p.history[0])("195", p.result(), "repetition (āmreḍita)"))
        out.append(p)
    return out


def bahuvrihi(stem: str) -> list[Prakriya]:
    """186: bahuvrīhi endings -a / -i; -ಇಲ್ಲ → -ಇಲಿ; -ಕೊಲ್ವ → -ಕುಲಿ."""
    out = []
    v = _vs(stem)

    def mk(rule, text, note):
        p = Prakriya([Term.make(stem)])
        p.terms = [Term.make(text)]
        p.log(rule, note)
        out.append(p)
    if V.is_consonant(v[-1]):
        dbl = v + [v[-1]] if len([x for x in v if V.is_vowel(x)]) and v[-2] in S.HRASVA else v
        mk("186", V.from_varnas(dbl + ["ಅ", V.ANUSVARA]), "bahuvrīhi: final a (+ nom.)")
        mk("186", V.from_varnas(v + ["ಇ"]), "bahuvrīhi: final i")
    else:
        mk("186", V.from_varnas(v[:-1] + ["ಇ"]), "bahuvrīhi: final i")
        mk("186", V.from_varnas(v + (["ಯ್"] if v[-1] in ("ಎ", "ಇ") else []) + ["ಅ", V.ANUSVARA]),
           "bahuvrīhi: final a (+ nom.)")
    return out
