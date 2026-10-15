"""Ākhyāta-prakaraṇa (sūtras 216–251a): verbs.

Main entry points
-----------------
``conjugate(root, form, person=3, number="sg", gender="m")`` → list[Prakriyā]
    form ∈ past, present, future, negative, aorist (-guṃ/-kuṃ), vidhi (imperative /
    optative), precative (-udu), prohibitive (-al), infinitive, gerund_past,
    gerund_present, conditional (-oḍe), sati (sati-saptamī -e and substitutes),
    action_noun (-udu), passive (-al + paḍu).
``tense_stem(root, tense)`` → [(stem, rule, note)] past/present/future stems.
``participles(root)`` → relative participles for gamaka compounds (ಪಾಡುವ, ಆಡಿದ).
``paradigm(root)`` → {(form, person, number, gender): [Prakriyā]}
``derive_parts(parts)`` → set of surface forms for a morpheme sequence as Kēśirāja
    writes it (e.g. ["ಮಾಡು", "ಇದ", "ಅಂ"]) — used by the test harness and the analyzer.
"""
from __future__ import annotations

from . import lexicon
from . import samjna as S
from . import varna as V
from .prakriya import Prakriya, Term, derive_all
from .sandhi import SUFFIX, junction

# ---------------------------------------------------------------- personal endings (217, 225, 226)
ENDINGS = {
    (3, "sg", "m"): "ಅಮ್", (3, "sg", "f"): "ಅಳ್", (3, "sg", "n"): "ಉದು",
    (3, "pl", "m"): "ಅರ್", (3, "pl", "f"): "ಅರ್", (3, "pl", "n"): "ಉವು",
    (2, "sg", None): "ಅಯ್", (2, "pl", None): "ಇರ್",
    (1, "sg", None): "ಎನ್", (1, "pl", None): "ಎವು",
}
NEG_NEUTER = {"sg": "ಅದು", "pl": "ಅವು"}          # 244

# ---------------------------------------------------------------- lexical root classes
IRREG_PAST_237 = {"ಮೀ": "ಮಿನ್", "ತರ್": "ತನ್", "ಬರ್": "ಬನ್", "ಕೊಲ್": "ಕೊನ್", "ಸಲ್": "ಸನ್"}
NIL_OPTIONAL = {"ನಿಲ್": "ನಿನ್"}
NO_BE_233 = {"ನೋ": "ನೊನ್", "ಬೇ": "ಬೆನ್"}
SHORTEN_240 = {"ಕಾಣ್": "ಕಣ್", "ಏೞ್": "ಎೞ್", "ಬೀೞ್": "ಬಿೞ್", "ಆೞ್": "ಅೞ್"}
T_ADDED_240 = {"ಸಾ": "ಸತ್", "ಈ": "ಇತ್", "ಸಾಯ್": "ಸತ್", "ಮೂ": "ಮುತ್"}
ROOT_VARIANTS = {"ಕೆಯ್": ["ಗೆಯ್"], "ಗೆಯ್": ["ಕೆಯ್"]}
RR_T_240 = {"ಪೆಱು", "ತಿಱು", "ಕಿಱು", "ಗಿಱು", "ಪೊಱು", "ತೆಪ್ಪಱು", "ಆಸಱು", "ಬೇಸಱು"}
RR_R_240 = {"ಅಱು", "ಆಱು"}
# 238/239: short-initial disyllabic roots whose final stop is devoiced and geminated
DEVOICE_239 = {"ಪುಗು", "ನಗು", "ಉಗು", "ಮಿಗು", "ತಗು", "ಅಡು", "ಸುಡು", "ಕುಡು", "ತುಡು", "ಬಿಡು",
               "ಉಡು", "ನಡು", "ಪಡು", "ಇಡು", "ಕಿಡು", "ಮಡು", "ಮುದು", "ಇಸು", "ಬಿಸು", "ಪಸು"}
LOWER_ALWAYS_238 = {"ಕುಡು", "ತುಡು", "ಕಿಡು", "ಇಸು", "ಬಿಸು", "ಉಗು", "ಪುಗು", "ಗಿಱು", "ತಿಱು", "ಕಿಱು"}
# 241: kavalādi roots: past d → t
KAVALADI = {"ಕವಲ್", "ಮಡಲ್", "ಬಲ್", "ಕಲ್", "ಪೋಲ್", "ಸಾಲ್", "ಸೋಲ್", "ಪೇಲ್", "ನೂಲ್", "ಕೂರ್", "ಕಸರ್",
            "ಕನರ್", "ಕೊನರ್", "ತಳಿರ್", "ಬೆಳರ್", "ಚಿಗುರ್", "ಬೆಮರ್", "ಅೞ್", "ಉಲ್", "ಕೀೞ್", "ಚಳಿ",
            "ಮೊಳೆ", "ಅಱ್", "ಮಱ್", "ಕುಱ್", "ಬಾ", "ಕೀ", "ಪೂ", "ಬೀ", "ಓ", "ಕೂನ್", "ಸೀನ್", "ಪೇನ್",
            "ಆನ್", "ನೋನ್", "ಈನ್", "ನಿಲ್"}
GA_SA_DROP_232 = True
DA_TO_ZHA = {"ಮಾಡು", "ನೋಡು", "ಬೇಡು", "ಬಿಸುಡು", "ಬೆಗಡು", "ಕಾಡು", "ತೀಡು", "ಕೂಡು", "ಪಾಡು", "ನೀಡು"}


def _t(s: str, *tags) -> Term:
    return Term.make(s, *tags)


def _vs(s: str) -> list[str]:
    return V.to_varnas(s)


def _short_initial_disyllabic(root: str) -> bool:
    """(C)V̆CU: two syllables, the first light (short vowel + single consonant)."""
    vs = _vs(root)
    vowels = [k for k, v in enumerate(vs) if V.is_vowel(v)]
    return (len(vowels) == 2 and vs[vowels[0]] in S.HRASVA and vs[-1] == "ಉ"
            and vowels[1] - vowels[0] == 2)


# ---------------------------------------------------------------- tense stems (221, 232–245)
def tense_stem(root: str, tense: str) -> list[tuple[str, str, str]]:
    """Possible tense stems (ending in -a) of ``root`` for past / present / future."""
    r = V.normalize(root)
    vs = _vs(r)
    out: list[tuple[str, str, str]] = []
    if tense in ("past", "present"):
        pasts = _past_stems(r, vs)
        if tense == "past":
            return pasts
        for st, rule, note in pasts:
            out.append((st + "ಪ", "221", f"present -dapa ({note})"))
            out.append((st + "ಪ್ಪ", "233", f"present -dappa ({note})"))
        return out
    if tense == "future":
        return _future_stems(r, vs)
    raise ValueError(tense)


def _past_stems(r: str, vs: list[str]) -> list[tuple[str, str, str]]:
    out = []
    # compound verbs ending in a special root (ದೆಸೆಗೆಡು → ದೆಸೆಗೆಟ್ಟ): use the last root
    for base in sorted(DEVOICE_239 | set(IRREG_PAST_237) | RR_T_240, key=len, reverse=True):
        if r.endswith(base) and r != base and len(r) > len(base) + 1 and \
                _vs(r[: -len(base)])[-1:] and (V.is_vowel(_vs(r[: -len(base)])[-1]) or base in IRREG_PAST_237):
            prefix = r[: -len(base)]
            pre_alt = prefix
            if base.startswith("ಕ"):
                pre_alt = prefix   # voicing of the second member is the compound's business
            return [(pre_alt + st, rule, note) for st, rule, note in _past_stems(base, _vs(base))] + [
                ((prefix[:-1] if False else prefix) + st.replace("ಕ", "ಗ", 1), rule, note + "; compound voicing")
                for st, rule, note in _past_stems(base, _vs(base)) if st.startswith("ಕ")]
    if r in IRREG_PAST_237:
        return [(IRREG_PAST_237[r] + "ದ", "237", "n-substitution before past d")]
    if r in NIL_OPTIONAL:
        return [(NIL_OPTIONAL[r] + "ದ", "237", "ನಿಲ್ → ನಿನ್ (optional)"), (r + "ದ", "237", "ನಿಲ್ unchanged"),
                (r + "ತ", "241", "kavalādi: d → t")]
    if r in NO_BE_233:
        return [(NO_BE_233[r] + "ದ", "233", "ನೋ/ಬೇ → ನೊನ್/ಬೆನ್")]
    if r in ("ಪೋಗು", "ಆಗು"):
        return [(r[:-2] + "ದ", "242", "-gu lost before past d")]
    if r == "ಕೊಳ್":
        return [("ಕೊಂಡ", "245", "koḷ → koṇ; d → ḍ")]
    if r == "ಉಣ್":
        return [("ಉಂಡ", "241", "after ṇ: d → ḍ")]
    if r == "ಕೀೞ್":
        return [("ಕಿೞ್ತ", "241", "kavalādi: d → t, vowel shortened"), ("ಕೀೞ್ತ", "241", "d → t"),
                ("ಕೀೞ್ದ", "241", "d retained (optional)")]
    if r in SHORTEN_240:
        st = SHORTEN_240[r]
        if st.endswith("ಣ್"):
            return [(st[:-2] + "ಂಡ", "240", "long vowel shortened; d → ḍ after ṇ (241)")]
        return [(st + "ದ", "240", "long vowel shortened")]
    if r in T_ADDED_240:
        return [(T_ADDED_240[r] + "ತ", "240", "t added, vowel shortened; d → t (241)")]
    if r == "ತವು":
        return [("ತಪ್ಪ", "240", "v → p; d → p (241)")]
    if r in RR_T_240 or (vs[-1] == "ಉ" and len(vs) >= 2 and vs[-2] == "ಱ್" and r not in RR_R_240):
        base = vs[:-2]
        lowered = _lower(base, r)
        out = [(V.from_varnas(lowered + ["ತ್", "ತ್", "ಅ"]), "240", "ṟ → t; d → t (241)")]
        if r not in RR_T_240:
            out.append((V.from_varnas(base + ["ರ್", "ತ್", "ಅ"]), "240", "ṟ → r (optional)"))
            out.append((V.from_varnas(base + ["ಱ್", "ತ್", "ಅ"]), "240", "ṟ kept"))
        return out
    if r in RR_R_240:
        base = vs[:-2]
        return [(V.from_varnas(base + ["ರ್", "ತ್", "ಅ"]), "240", "ṟ → r"),
                (V.from_varnas(base + ["ಱ್", "ತ್", "ಅ"]), "240", "ṟ kept (optional)")]
    if r in DEVOICE_239 or (_short_initial_disyllabic(r) and vs[-2] in ("ಗ್", "ಡ್", "ದ್", "ಸ್")):
        c = vs[-2]
        dev = {"ಗ್": "ಕ್", "ಡ್": "ಟ್", "ದ್": "ತ್", "ಸ್": "ಚ್"}[c]
        base = vs[:-2]
        res = []
        for b, note in ((_lower(base, r), "initial i/u lowered (238)"), (base, "no lowering")):
            st = V.from_varnas(b + [dev, dev, "ಅ"])
            if (st, ) not in [(x[0],) for x in res]:
                res.append((st, "239", f"devoiced and geminated (241); {note}"))
            if r in LOWER_ALWAYS_238:
                break
        if r in ("ಇಡು", "ಉಡು", "ಸುಡು", "ಬಿಡು", "ಮಿಗು", "ಮುದು", "ನಗು", "ತಗು", "ಅಡು", "ನಡು", "ಪಡು", "ಮಡು", "ಪಸು"):
            res = [x for x in res if "no lowering" in x[2]] or res
        return res
    # regular (221): u-final → -ida; e/i/consonant-final → -da
    if vs[-1] == "ಉ":
        out.append((V.from_varnas(vs[:-1] + ["ಇ", "ದ್", "ಅ"]), "221", "u-final root: augment -i- before -da"))
        return out
    if V.is_consonant(vs[-1]):
        if vs[-1] == "ಣ್":
            out.append((V.from_varnas(vs[:-1]) + "ಂಡ", "241", "after ṇ: d → ḍ"))
            if any(v in S.DIRGHA for v in vs if V.is_vowel(v)):
                out.append((V.from_varnas(vs + ["ದ್", "ಅ"]), "241", "d retained (mēṇ)"))
            return out
        if r in KAVALADI:
            out.append((r + "ತ", "241", "kavalādi: d → t"))
        out.append((V.from_varnas(vs + ["ದ್", "ಅ"]), "221", "consonant-final root + -da"))
        return out
    if r in KAVALADI:
        out.append((r + "ತ", "241", "kavalādi: d → t"))
    out.append((V.from_varnas(vs + ["ದ್", "ಅ"]), "221", "vowel-final root + -da"))
    return out


def _lower(base: list[str], root: str) -> list[str]:
    b = list(base)
    for k, v in enumerate(b):
        if V.is_vowel(v):
            if v == "ಇ":
                b[k] = "ಎ"
            elif v == "ಉ":
                b[k] = "ಒ"
            break
    return b


def _future_stems(r: str, vs: list[str]) -> list[tuple[str, str, str]]:
    out = []
    last = vs[-1]
    if r in ("ಪೋಗು", "ಆಗು"):
        return [(r[:-2] + "ಪ", "242", "-gu lost; v → p"), ("ಅಪ್ಪ" if r == "ಆಗು" else "ಪೋಪ", "232", "")]
    if r == "ಉಳ್":
        return [("ಉಳ್ಳ", "245", "")]
    if last == "ಉ" and len(vs) > 2 and vs[-2] in ("ಗ್", "ಸ್"):
        out.append((V.from_varnas(vs[:-2] + ["ಪ್", "ಅ"]), "232", "-gu/-su lost; v → p"))
        out.append((V.from_varnas(vs[:-2] + ["ಪ್", "ಪ್", "ಅ"]), "232", "-gu/-su lost; v → pp (optional)"))
        out.append((V.from_varnas(vs + ["ವ್", "ಅ"]), "221", "future -va (attested variant)"))
        return out
    if last == "ಉ" and len(vs) > 2 and vs[-2] == "ಡ್" and (r in DA_TO_ZHA or len(vs) > 3):
        out.append((V.from_varnas(vs[:-2] + ["ೞ್", "ಪ್", "ಅ"]), "232", "ḍu → ḻ; v → p"))
        out.append((V.from_varnas(vs + ["ವ್", "ಅ"]), "221", "future -va"))
        return out
    if last in ("ರ್", "ಱ್", "ೞ್") or last == "ಓ":
        out.append((V.from_varnas(vs + ["ಪ್", "ಅ"]), "232", "v → p"))
        out.append((V.from_varnas(vs + ["ಪ್", "ಪ್", "ಅ"]), "232", "v → pp (optional)"))
        if last == "ೞ್":
            out.append((V.from_varnas(vs + ["ವ್", "ಅ"]), "221", "future -va (attested in quotations)"))
        return out
    if last == "ನ್":
        long = any(v in S.DIRGHA for v in vs if V.is_vowel(v))
        out.append((V.from_varnas(vs[:-1]) + "ಂಬ", "232", "n-final: v → b"))
        if long:
            out.append((V.from_varnas(vs[:-1]) + "ಂಪ", "232", "n-final (long vowel): v → p"))
        return out
    if last == "ಣ್":
        out.append((V.from_varnas(vs + ["ಬ್", "ಅ"]), "232", "ṇ-final: v → b"))
        return out
    if last == "ಉ":
        out.append((V.from_varnas(vs + ["ವ್", "ಅ"]), "221", "future -va (u retained)"))
        return out
    if V.is_consonant(last):
        out.append((V.from_varnas(vs + ["ವ್", "ಅ"]), "221", "future -va"))
        return out
    out.append((V.from_varnas(vs + ["ವ್", "ಅ"]), "221", "future -va"))
    return out


# ---------------------------------------------------------------- junctions
def _attach(p: Prakriya, stem: str, ending: str, rule: str, note: str, root: str | None = None):
    """Append ``ending`` to an a-final tense stem (a merges with the ending vowel)."""
    st = _t(stem, "dhatu" if root == stem else "tense_stem")
    en = _t(ending, "vibhakti")
    p.terms = [st, en]
    p.log(rule, note)
    if V.is_vowel(en.first) and st.last == "ಅ":
        st.text.pop()
        p.log("217", "final a of the tense stem merges with the ending")
    _final(p)


def _root_plus(p: Prakriya, root: str, suffix: str, rule: str, note: str, negative=False):
    """Root + vowel- or consonant-initial suffix (no tense marker)."""
    rt = _t(root, "dhatu", lexicon.KANNADA)
    sf = _t(suffix, "vibhakti")
    if negative:
        sf.tags.add("negative")
    p.terms = [rt, sf]
    p.log(rule, note)
    if V.is_vowel(sf.first):
        last = rt.last
        if last == "ಉ" and len(rt.text) > 2:
            rt.text.pop()
            p.log("52", "root-final u elided before a vowel")
        elif V.is_vowel(last):
            sf.text.insert(0, "ಯ್")
            p.log("53", "ya-āgama after a vowel-final root")
        else:
            junction(p, 0, SUFFIX)
    _final(p)


def _final(p: Prakriya):
    from .nama import finalize
    finalize(p)


# ---------------------------------------------------------------- conjugation
FORMS = ("neg_participle", "past", "present", "future", "negative", "aorist", "vidhi", "precative", "prohibitive",
         "infinitive", "gerund_past", "gerund_present", "conditional", "sati", "action_noun",
         "passive", "participle_past", "participle_future")


def conjugate(root: str, form: str, person: int = 3, number: str = "sg", gender: str | None = "m",
              tense: str = "past") -> list[Prakriya]:
    root = V.normalize(root)
    g = gender if person == 3 else None
    out: list[Prakriya] = []

    def single(rule, text, note):
        p = Prakriya([_t(root)])
        p.terms = [_t(text)]
        p.log(rule, note)
        out.append(p)

    if form in ("past", "present", "future"):
        if root == "ಉಳ್" and form == "past":       # 245: oḷaṃ … without tense marker
            end = ENDINGS[(person, number, g)]
            if (person, number, g) == (3, "sg", "n"):
                single("244", "ಉಂಟು", "uḷ + udu → uṇṭu")
                return out
            if (person, number, g) == (3, "pl", "n"):
                end = "ಅವು"
            p = Prakriya()
            _attach(p, "ಒಳ", end, "245", "uḷ: personal endings without tense marker, u → o")
            out.append(p)
            return out
        for stem, rule, note in tense_stem(root, form):
            endings = [ENDINGS[(person, number, g)]]
            if (person, number, g) == (3, "sg", "n") and form == "past":
                endings += ["ಅತ್ತು"]
            if person == 1 and number == "pl":
                endings += ["ಎಮ್"]          # 220: -evu → -eṃ
            for end in endings:
                p = Prakriya()
                _attach(p, stem, end, rule, f"{form} stem: {note}")
                out.append(p)
            if person in (1, 2) and number == "pl":   # 220: -ar- before -ir / -evu
                p = Prakriya()
                _attach(p, stem + "ರ", ENDINGS[(person, number, g)], rule, f"{form}; -ar- inserted (220)")
                out.append(p)
        if form == "past" and (person, number, g) == (3, "sg", "n"):
            vs = _vs(root)
            if root in ("ಪೋಗು", "ಆಗು"):
                single("242", root[:-2] + "ಯ್ತು", "past neuter -tu; d → y")
            else:
                for end in ("ಇತು", "ಇತ್ತು"):
                    p = Prakriya()
                    _root_plus(p, root, end, "226", "neuter past -itu/-ittu")
                    out.append(p)
        return out
    if form == "negative":
        end = NEG_NEUTER[number] if (person == 3 and g == "n") else ENDINGS[(person, number, g)]
        r = root
        if root in ("ತರ್", "ಬರ್"):
            r = root[0] + "ಾ" + root[1:]
        p = Prakriya()
        _root_plus(p, r, end, "222", "negative: root + ending, no tense marker", negative=True)
        if r != root:
            p.log("238", "ತರ್/ಬರ್ lengthened in the negative")
        out.append(p)
        return out
    if form == "aorist":
        return _aorist(root)
    if form == "vidhi":
        return _vidhi(root, person, number)
    if form == "precative":
        for stem, rule, note in tense_stem(root, "future"):
            p = Prakriya()
            _attach(p, stem, "ಉದು", "225", "precative -udu on the future stem")
            out.append(p)
        return out
    if form == "action_noun":
        for stem, rule, note in tense_stem(root, "future") + tense_stem(root, "past"):
            p = Prakriya()
            _attach(p, stem, "ಉದು", "225", "action noun -udu")
            out.append(p)
        return out
    if form == "neg_participle":                       # 71: -ade 'without …-ing'
        p = Prakriya()
        _root_plus(p, root, "ಅದೆ", "71", "negative participle -ade", negative=True)
        out.append(p)
        return out
    if form == "prohibitive":
        p = Prakriya()
        _root_plus(p, root, "ಅಲ್" if number == "sg" else "ಅಲಿಂ", "234", "prohibitive -al / -aliṃ")
        out.append(p)
        return out
    if form == "infinitive":
        for suf, rule, note in (("ಅಲ್", "234", "infinitive -al"), ("ಅಲ್ಕೆ", "235", "infinitive -alke"),
                                ("ಅ", "235", "infinitive -a (l dropped)"), ("ಅಲುಂ", "234", "-al + uṃ")):
            p = Prakriya()
            _root_plus(p, root, suf, rule, note)
            out.append(p)
        return out
    if form == "gerund_past":
        for stem, rule, note in tense_stem(root, "past"):
            p = Prakriya()
            _attach(p, stem, "ಉ", "236", f"past gerund -u on the past stem ({note})")
            out.append(p)
        if _vs(root)[-1] == "ಉ" or V.is_consonant(_vs(root)[-1]):
            p = Prakriya()
            _root_plus(p, root, "ಇ", "236", "past gerund -i on the root")
            out.append(p)
        return out
    if form == "gerund_present":
        for suf in ("ಉತುಂ", "ಉತ್ತುಂ", "ಉತ್ತೆ", "ಉತೆ"):
            p = Prakriya()
            _root_plus(p, root, suf, "236", f"present gerund -{suf[1:]}")
            out.append(p)
        return out
    if form == "conditional":
        stems = tense_stem(root, "past") + tense_stem(root, "future") + tense_stem(root, "present")
        for stem, rule, note in stems:
            p = Prakriya()
            _attach(p, stem, "ಒಡೆ", "250", "conditional -oḍe")
            out.append(p)
        if root == "ಉಳ್":
            single("250", "ಉಳ್ಳೊಡೆ", "conditional of uḷ")
        return out
    if form == "sati":
        p = Prakriya()
        _root_plus(p, root, "ಎ", "246", "sati-saptamī -e")
        out.append(p)
        for stem, rule, note in tense_stem(root, "future"):
            for suf in ("ಇನೆಗಂ", "ಇನಂ", "ಅನ್ನಂ", "ಅನ್ನೆಗಂ", "ಉದುಂ"):
                q = Prakriya()
                _attach(q, stem, suf, "246", f"sati-saptamī substitute {suf}")
                out.append(q)
        for suf in ("ಅಲೊಡಂ", "ಅಲೊಡನೆ"):
            q = Prakriya()
            _root_plus(q, root, suf, "246", f"sati-saptamī {suf}")
            out.append(q)
        return out
    if form in ("participle_past", "participle_future"):
        for stem, rule, note in tense_stem(root, "past" if form == "participle_past" else "future"):
            single(rule, stem, f"relative participle (kṛt stem, 73): {note}")
        return out
    if form == "passive":
        for linker in ("ಅಲ್", "ಎ"):
            p = Prakriya()
            _root_plus(p, root, linker, "251a", f"passive: root + -{linker[1:] or 'e'}")
            base = p.result()
            for q in conjugate("ಪಡು", tense if tense in ("past", "present", "future") else "past",
                               person, number, gender):
                single("251a", base + q.result(), "passive: + paḍu conjugated")
        return out
    raise ValueError(f"unknown form {form!r}")


def _aorist(root: str) -> list[Prakriya]:
    """227–228, 243: -guṃ / -kuṃ."""
    out = []
    vs = _vs(root)

    def mk(rule, text, note):
        p = Prakriya([_t(root)])
        p.terms = [_t(text)]
        p.log(rule, note)
        out.append(p)
    if root == "ಪೋಗು":
        return [mk("243", "ಪೋಕುಂ", "pōgu: gu lost before -kuṃ")] and out
    if root == "ಆಗು":
        return [mk("243", "ಅಕ್ಕುಂ", "āgu → akk-")] and out
    if root.endswith("ಇಸು") or root.endswith("ಿಸು"):
        mk("227", root + "ಗುಂ", "-guṃ")
        mk("228", root[:-2] + "ಕುಂ", "-su lost before -kuṃ")
        mk("228", root[:-2] + "ಕ್ಕುಂ", "-su lost; k doubled (some poets)")
        return out
    last = vs[-1]
    if last in ("ರ್", "ಱ್", "ೞ್", "ಲ್"):
        mk("227", root + "ಕುಂ", "-kuṃ after r/ḻ/l")
        if last == "ಲ್":
            mk("227", root + "ಗುಂ", "-guṃ")
        return out
    mk("227", root + "ಗುಂ" if not V.is_consonant(last) else root + "ಗುಂ", "-guṃ")
    if last == "ಉ" and len(vs) > 2 and vs[-2] == "ಡ್":
        mk("227", V.from_varnas(vs[:-2] + ["ೞ್"]) + "ಕುಂ", "ḍu → ḻ + -kuṃ")
    if last == "ಉ" and len(vs) > 2 and vs[-2] == "ಗ್":
        mk("227", V.from_varnas(vs[:-2]) + "ಕುಂ", "-gu lost + -kuṃ")
    return out


def _vidhi(root: str, person: int, number: str) -> list[Prakriya]:
    """229–230, 237: imperative / optative."""
    out = []
    vs = _vs(root)

    def mk(rule, text, note):
        p = Prakriya([_t(root)])
        p.terms = [_t(text)]
        p.log(rule, note)
        out.append(p)
    if person == 2 and number == "sg":
        mk("230", "ಇರು" if root == "ಇರ್" else root, "2sg imperative: bare root")
        if vs[-1] == "ಉ":
            mk("125", V.from_varnas(vs[:-1] + ["ಅ"]), "imperative + -a")
        elif V.is_consonant(vs[-1]):
            mk("125", root + "ಅ" if False else V.from_varnas(vs + ["ಅ"]), "imperative + -a")
            if root in ("ಬರ್", "ತರ್"):
                mk("238", root[0] + "ಾರ", "ಬಾರ/ತಾರ")
        return out
    if person == 2 and number == "pl":
        if root in ("ತರ್", "ಬರ್"):
            mk("237", root[0] + "ನ್ನಿಂ", "tar/bar → tan/ban before -iṃ")
            return out
        p = Prakriya()
        _root_plus(p, root, "ಇಮ್", "229", "2pl vidhi -iṃ")
        out.append(p)
        return out
    if person == 1:
        for stem, rule, note in tense_stem(root, "future"):
            p = Prakriya()
            _attach(p, stem, "ಅಮ್" if number == "pl" else "ಎನ್", "229", "1st person vidhi on the future stem")
            out.append(p)
        return out
    # 3rd person: -ge / -ke (229, 243)
    if root == "ಪೋಗು":
        mk("243", "ಪೋಕೆ", "pōgu → pō- + ke")
        return out
    if root == "ಆಗು":
        mk("243", "ಅಕ್ಕೆ", "āgu → akke")
        return out
    if root.endswith("ಿಸು"):
        mk("229", root[:-2] + "ಕೆ", "-su lost before -ke")
        mk("229", root[:-2] + "ಕ್ಕೆ", "-su lost; k doubled")
        mk("229", root + "ಗೆ", "-ge")
        return out
    if vs[-1] in ("ರ್", "ಱ್", "ೞ್"):
        mk("229", root + "ಕೆ", "-ke after r/ṟ/ḻ")
        return out
    mk("229", root + "ಗೆ", "-ge")
    if vs[-1] == "ಉ" and len(vs) > 2 and vs[-2] == "ಡ್":
        mk("229", V.from_varnas(vs[:-2] + ["ೞ್"]) + "ಕೆ", "ḍu → ḻ + -ke")
    for stem, rule, note in tense_stem(root, "future"):
        p = Prakriya()
        _attach(p, stem, "ಉದು", "225", "vidhi -udu on the future stem")
        out.append(p)
    return out


def causative(root: str) -> list[str]:
    """231: root + -isu (Sanskrit a/ā-stems drop the vowel or take y, 52/54)."""
    vs = _vs(V.normalize(root))
    if vs[-1] in ("ಅ", "ಆ"):
        return [V.from_varnas(vs[:-1] + ["ಇ", "ಸ್", "ಉ"]), V.from_varnas(vs + ["ಯ್", "ಇ", "ಸ್", "ಉ"])]
    if vs[-1] == "ಉ":
        return [V.from_varnas(vs[:-1] + ["ಇ", "ಸ್", "ಉ"])]
    if V.is_vowel(vs[-1]):
        return [V.from_varnas(vs + ["ಯ್", "ಇ", "ಸ್", "ಉ"])]
    if vs[-1] == "ಅ":
        return [V.from_varnas(vs[:-1] + ["ಇ", "ಸ್", "ಉ"]), V.from_varnas(vs + ["ಯ್", "ಇ", "ಸ್", "ಉ"])]
    return [V.from_varnas(vs + ["ಇ", "ಸ್", "ಉ"])]


def participles(root: str) -> list[tuple[str, str]]:
    """Relative participles used as first members of gamaka compounds (168)."""
    r = V.normalize(root)
    try:
        vs = _vs(r)
    except ValueError:
        return []
    if not vs or (not V.is_vowel(vs[-1]) and vs[-1] not in S.VYANJANA):
        return []
    out = []
    for stem, rule, note in tense_stem(r, "future"):
        out.append((stem, "present/future participle"))
    for stem, rule, note in tense_stem(r, "past")[:2]:
        out.append((stem, "past participle"))
    return out


def paradigm(root: str) -> dict:
    out = {}
    for form in ("past", "present", "future", "negative"):
        for person, number, gender in ((3, "sg", "m"), (3, "sg", "f"), (3, "sg", "n"), (3, "pl", "m"),
                                       (3, "pl", "n"), (2, "sg", None), (2, "pl", None),
                                       (1, "sg", None), (1, "pl", None)):
            key = (form, f"{person}{number}", gender or "")
            out[key] = conjugate(root, form, person, number, gender)
    for form in ("aorist", "infinitive", "gerund_past", "gerund_present", "conditional",
                 "participle_past", "participle_future"):
        out[(form, "", "")] = conjugate(root, form)
    out[("vidhi", "2sg", "")] = conjugate(root, "vidhi", 2, "sg")
    out[("vidhi", "2pl", "")] = conjugate(root, "vidhi", 2, "pl")
    out[("vidhi", "3", "")] = conjugate(root, "vidhi", 3, "sg")
    return out


# ---------------------------------------------------------------- morpheme-sequence interface
_ENDING_PN = {"ಅಂ": [(3, "sg", "m")], "ಅಮ್": [(3, "sg", "m")], "ಅನ್": [(3, "sg", "m")],
              "ಅಳ್": [(3, "sg", "f")], "ಉದು": [(3, "sg", "n")], "ಅರ್": [(3, "pl", "m")],
              "ಉವು": [(3, "pl", "n")], "ಅಯ್": [(2, "sg", None)], "ಇರ್": [(2, "pl", None)],
              "ಎನ್": [(1, "sg", None)], "ಎಂ": [(1, "sg", None), (1, "pl", None)], "ಎವು": [(1, "pl", None)]}
_MARKER_TENSE = {"ದ": "past", "ಇದ": "past", "ದಪ": "present", "ಇದಪ": "present", "ವ": "future", "ಪ": "future",
                 "ಉವ": "future", "ಬ": "future"}
_MARKERS = set(_MARKER_TENSE) | set(_ENDING_PN) | {
    "ಅದು", "ಅವು", "ಗುಂ", "ಕುಂ", "ಗೆ", "ಕೆ", "ಇಂ", "ಇಮ್", "ಅ", "ಅಲ್", "ಅಲುಂ", "ಅಲ್ಕೆ", "ಉ", "ಇ", "ಉತುಂ",
    "ಉತ್ತುಂ", "ಉತ್ತೆ", "ಉತೆ", "ಎ", "ಅಲೊಡಂ", "ಒಡೆ", "ಇತು", "ಇತ್ತು", "ಇಸು", "ಎಲೆ", "ಎಂದು", "ವರಂ",
    "ವರೆಗಂ", "ಮುಟ್ಟೆ", "ತು", "ಅತ್ತು"}


def derive_parts(parts: list[str], _variants: bool = True) -> set[str]:
    """All forms the engine derives for a morpheme sequence written in Kēśirāja's style."""
    res = _derive_parts(parts)
    if _variants and parts:
        for alt in ROOT_VARIANTS.get(V.normalize(parts[0]), []):
            res |= _derive_parts([alt] + list(parts[1:]))
    return res


def _derive_parts(parts: list[str]) -> set[str]:
    parts = [V.normalize(x) for x in parts if x]
    if not parts:
        return set()
    root, rest = parts[0], parts[1:]
    out: set[str] = set()
    # 248: limit words
    if rest and rest[0] in ("ವರಂ", "ವರೆಗಂ"):
        left = root[:-2] if root.endswith(("ನ್ನೆಗಂ",)) else root
        return {left + rest[0]}
    if rest and rest[0] == "ಮುಟ್ಟೆ":
        return {root + "ಮುಟ್ಟೆ"}
    # 230: imperative + vocative ಎಲೆ; reduplicated imperative + ಎಂದು
    if rest == ["ಎಲೆ"]:
        p = Prakriya()
        _root_plus(p, root, "ಎಲೆ", "230", "imperative + ಎಲೆ")
        return {p.result()}
    if len(rest) == 2 and rest[0] == root and rest[1] == "ಎಂದು":
        from .sandhi import WORD, results
        if V.is_consonant(_vs(root)[-1]):
            return {root + f for f in results(root, "ಎಂದು", context=WORD)}
        p = Prakriya()
        _root_plus(p, root, "ಎಂದು", "230", "reduplicated imperative + ಎಂದು")
        return {root + p.result()}
    # compound verbs: X + root + endings (ದೆಸೆ+ಕಿಡು, ಬೆನ್+ಈ, ಪಾಱಿ+ಪೋಗು, ಕೆಯ್+ಕೊಳ್)
    if len(rest) >= 2 and rest[0] not in _MARKERS:
        from .sandhi import COMPOUND, results
        firsts = {root, "ಕೈ"} if root == "ಕೆಯ್" else {root}
        for f in derive_parts(rest):
            for first in firsts:
                out.add(first + f)
                out |= results(first, f, context=COMPOUND)
        return out
    if root == "ಉಳ್" and len(rest) == 1 and rest[0] in _ENDING_PN:
        for pn in _ENDING_PN[rest[0]]:
            out |= {p.result() for p in conjugate(root, "past", *pn)}
        return out
    if rest and rest[0] == "ಉವು" and root == "ಉಳ್":
        return {"ಒಳವು"}
    if rest == ["ಅಲೊಡಂ", "ಎ"]:
        return {p.result() for p in conjugate(root, "sati")}
    # 219–220: a-final nominal stems (adjectives, pronouns, numerals) take personal endings
    if _vs(root)[-1] == "ಅ" and rest and rest[-1] in _ENDING_PN and all(
            x in ("ಅರ್", "ನ್") for x in rest[:-1]):
        stem = root + "".join({"ಅರ್": "ರ", "ನ್": "ನ"}[x] for x in rest[:-1])
        p = Prakriya()
        _attach(p, stem, rest[-1] if rest[-1] != "ಅಂ" else "ಅಮ್", "219", "personal ending on a nominal stem")
        out.add(p.result())
        if rest[-1] == "ಎನ್":
            q = Prakriya()
            _attach(q, root + "ನ", "ಎನ್", "220", "-n- before 1sg -en")
            out.add(q.result())
        if len(rest) == 1 and rest[0] in ("ಅಂ", "ಅಮ್", "ಅರ್", "ಅಳ್") and root.endswith(("ದ", "ವ", "ಪ")):
            pass
        else:
            return out
    # causative -isu inside the sequence
    if rest and rest[0] == "ಇಸು":
        return {f for c in causative(root) for f in derive_parts([c] + rest[1:])}
    if rest and rest[0] == "ಅಲ್" and len(rest) >= 2 and rest[1] == "ಪಡು":      # passive
        tail = rest[2:]
        bases = {p.result() for p in conjugate(root, "infinitive") if p.result().endswith("ಲ್")}
        for b in bases:
            for f in derive_parts(["ಪಡು"] + tail):
                out.add(b + f)
        return out
    if rest and rest[0] == "ಎ" and len(rest) >= 2 and rest[1] == "ಪಡು":
        for f in derive_parts(["ಪಡು"] + rest[2:]):
            out |= {p.result() + f for p in conjugate(root, "sati")[:1]}
        return out
    if not rest:
        return {p.result() for p in conjugate(root, "vidhi", 2, "sg")}
    if len(rest) == 1:
        e = rest[0]
        # fused marker+ending (ದಂ, ದರ್, ದಪಂ, ವಂ, ದುದು ...)
        for mk in ("ದಪ", "ದ", "ವ", "ಪ"):
            if e.startswith(mk) and len(e) > len(mk):
                tail = "ಅ" + e[len(mk):] if e[len(mk)] in "ಂರ" else None
                tail_map = {"ಂ": "ಅಂ", "ರ್": "ಅರ್", "ಯ್": "ಅಯ್", "ಳ್": "ಅಳ್", "ನ್": "ಅನ್", "ುದು": "ಉದು",
                            "ುವು": "ಉವು", "ಿರ್": "ಇರ್", "ೆಂ": "ಎಂ", "ೆನ್": "ಎನ್", "ೆವು": "ಎವು", "ವರ್": "ಅರ್"}
                t = e[len(mk):]
                if t in tail_map:
                    out |= derive_parts([root, mk, tail_map[t]])
        if e in _ENDING_PN:
            for pn in _ENDING_PN[e]:
                out |= {p.result() for p in conjugate(root, "negative", *pn)}
        if e in ("ಅದು", "ಅವು"):
            out |= {p.result() for p in conjugate(root, "negative", 3, "sg" if e == "ಅದು" else "pl", "n")}
        if e in ("ಗುಂ", "ಕುಂ"):
            out |= {p.result() for p in conjugate(root, "aorist")}
        if e in ("ಗೆ", "ಕೆ"):
            out |= {p.result() for p in conjugate(root, "vidhi", 3, "sg")}
        if e in ("ಇಂ", "ಇಮ್"):
            out |= {p.result() for p in conjugate(root, "vidhi", 2, "pl")}
        if e == "ಅ":
            out |= {p.result() for p in conjugate(root, "vidhi", 2, "sg")}
            out |= {p.result() for p in conjugate(root, "infinitive")}
        if e in ("ಅಲ್", "ಅಲುಂ", "ಅಲ್ಕೆ"):
            out |= {p.result() for p in conjugate(root, "infinitive")}
        if e in ("ಉ", "ಇ"):
            out |= {p.result() for p in conjugate(root, "gerund_past")}
        if e in ("ಉತುಂ", "ಉತ್ತುಂ", "ಉತ್ತೆ", "ಉತೆ"):
            out |= {p.result() for p in conjugate(root, "gerund_present")}
        if e in ("ಎ", "ಅಲೊಡಂ", "ಅಲೊಡನೆ"):
            out |= {p.result() for p in conjugate(root, "sati")}
        if e in ("ಒಡೆ",):
            out |= {p.result() for p in conjugate(root, "conditional")}
        if e in ("ಇತು", "ಇತ್ತು"):
            out |= {p.result() for p in conjugate(root, "past", 3, "sg", "n")}
        if e.startswith("ದವ") or e.startswith("ಇದವ"):      # participial noun ಪೊಕ್ಕವರ್
            for stem, rule, note in tense_stem(root, "past"):
                out.add(stem + e[e.index("ವ"):])
        if e in ("ವ", "ಪ", "ದ", "ಇದ"):
            out |= {p.result() for p in conjugate(root, "participle_future" if e in ("ವ", "ಪ") else "participle_past")}
        return out
    mk, e = rest[0], rest[1]
    if len(rest) == 3 and rest[1] == "ಅಲ್" and rest[2] == "ಕೆ":
        return {p.result() for p in conjugate(root, "infinitive")}
    if mk == "ಅಲ್" and e in ("ಇಂ", "ಕೆ"):
        return {p.result() for p in conjugate(root, "prohibitive", 2, "pl")} | \
            {p.result() for p in conjugate(root, "infinitive")}
    tense = _MARKER_TENSE.get(mk)
    if tense:
        if e in _ENDING_PN:
            for pn in _ENDING_PN[e]:
                out |= {p.result() for p in conjugate(root, tense, *pn)}
        if e == "ಉದು":
            out |= {p.result() for p in conjugate(root, "action_noun")}
            out |= {p.result() for p in conjugate(root, "precative")}
        if e in ("ಅತ್ತು", "ತು"):
            out |= {p.result() for p in conjugate(root, "past", 3, "sg", "n")}
        if e == "ಉ":
            out |= {p.result() for p in conjugate(root, "gerund_past")}
        if e == "ಒಡೆ":
            out |= {p.result() for p in conjugate(root, "conditional")}
        if e in ("ಇನೆಗಂ", "ಇನಂ", "ಅನ್ನಂ", "ಅನ್ನೆಗಂ", "ಉದುಂ"):
            out |= {p.result() for p in conjugate(root, "sati")}
        if e == "ಅಂ" and tense == "future":
            out |= {p.result() for p in conjugate(root, "vidhi", 1, "pl")}
        if e == "ಎನ್" and tense == "future":
            out |= {p.result() for p in conjugate(root, "vidhi", 1, "sg")}
    return out
