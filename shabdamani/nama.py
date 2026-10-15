"""Nāma-prakaraṇa (sūtras 72–161): nominal stems, gender, number and case.

Main entry points
-----------------
``decline(stem, case, number="sg", gender=None, origin=None, cls=())``
    → list of Prakriyā (every optional variant), e.g. ``decline("ಮರ", "ins")``.
``paradigm(stem, ...)``  → {(case, number): [Prakriyā, ...]}
``adapt_sanskrit(word)`` → Sanskrit word → Kannada nominal stem(s) (80–87)
``personal_stem(base, gender, number)`` → masculine/feminine/human-plural stems of
    pronouns and quality words (98, 150–154).

Cases: nom acc ins dat abl gen loc voc. Genders: m f n. Origins: kannada / sanskrit.
Stem classes (``cls``): sarvanama, gunavacana, krt, sankhya (numeral), pavan (quantity),
dik (direction word), avyaya, kinship.
"""
from __future__ import annotations

from . import lexicon
from . import samjna as S
from . import varna as V
from .prakriya import Prakriya, Term, derive_all
from .sandhi import SUFFIX, junction

CASES = ("nom", "acc", "ins", "dat", "abl", "gen", "loc", "voc")
NUMBERS = ("sg", "pl")
GENDERS = ("m", "f", "n")
CASE_NAMES = {"nom": "prathamā", "acc": "dvitīyā", "ins": "tṛtīyā", "dat": "caturthī",
              "abl": "pañcamī", "gen": "ṣaṣṭhī", "loc": "saptamī", "voc": "sambōdhane"}

# ---------------------------------------------------------------- lexical classes
SARVANAMA = {"ಅದು", "ಇದು", "ಉದು", "ಆವುದು", "ಎಲ್ಲದು", "ಪೆಱತು", "ಪೆಱದು", "ಏನ್"}       # 78
SARVANAMA_PL = {"ಅವು", "ಇವು", "ಉವು", "ಪೆಱವು", "ಎಲ್ಲವು"}
PAVAN = {"ಅನಿತು", "ಇನಿತು", "ಉನಿತು", "ಎನಿತು", "ಎಲ್ಲವು", "ಕೆಲವು", "ಪಲವು", "ಪಲ", "ಕೆಲ", "ಎಲ್ಲ"}               # 99–100
SANKHYA = {"ಒಂದು", "ಎರಡು", "ಮೂಱು", "ನಾಲ್ಕು", "ಅಯ್ದು", "ಆಱು", "ಏೞು", "ಎಂಟು", "ಒಂಬತ್ತು",
           "ಪತ್ತು", "ನೂಱು", "ಸಾಸಿರ", "ಒರ್", "ಇರ್", "ಮೂ", "ನಾಲ್", "ಐ", "ಅಱು", "ಏೞ್", "ಎಣ್", "ನೂರ್"}
DIK_AN = {"ಮೂಡು", "ತೆಂಕು", "ಪಡುವು", "ಪಡು", "ಬಡಗು", "ಮೇಗು", "ಕೆಳಗು", "ಕಡೆ", "ಎಡೆ", "ಅತ್ತ", "ಇತ್ತ",
          "ಉತ್ತ", "ಎತ್ತ", "ಮುಂದು", "ಪಿಂದು", "ಮುಂತು", "ಪಿಂತು", "ಒಳಗು", "ಪೊಱಗು", "ನಡು", "ನಡುವು"}  # 110
DIK_A = {"ಮೂಡ", "ಪಡುವ", "ತೆಂಕ", "ಬಡಗ", "ಅತ್ತ", "ಇತ್ತ", "ಉತ್ತ", "ಎತ್ತ"}             # 119, 121
DIK_U_E = {"ಒಳಗು", "ಪೊಱಗು", "ಪೆಱಗು", "ಮೇಗು", "ಕೆಳಗು", "ಮುಂದು", "ಪಿಂದು", "ಮುಂತು", "ಪಿಂತು", "ನಡು"}
TIME_WORDS = {"ಅಂದು", "ಇಂದು", "ಉಂದು", "ಎಂದು"}                                          # 121
PERSONAL = {"ನೀನ್": ("ನಿನ್", "ನಿನ"), "ಆನ್": ("ಎನ್", "ಎನ"), "ತಾನ್": ("ತನ್", "ತನ"),       # 146
            "ನೀಮ್": ("ನಿಮ್", "ನಿಮ"), "ಆಮ್": ("ಎಮ್", "ಎಮ"), "ತಾಮ್": ("ತಮ್", "ತಮ")}
PERSONAL_ALIAS = {"ನೀಂ": "ನೀನ್", "ಆಂ": "ಆನ್", "ತಾಂ": "ತಾನ್", "ನಿನ್": "ನೀನ್", "ಎನ್": "ಆನ್",
                  "ತನ್": "ತಾನ್", "ನಿಮ್": "ನೀಮ್", "ಎಮ್": "ಆಮ್", "ತಮ್": "ತಾಮ್"}
# 121a: a-final feminine/animal nouns declined like masculines
MASC_LIKE = {"ಅಕ್ಕ", "ಅವ್ವ", "ಅಮ್ಮ", "ಹರಿಣ", "ಕೋಣ", "ಹಂಗ", "ಹಸುಬ", "ಸರ್ಪ", "ಗರುಡ", "ಕೂರ್ಮ",
             "ಕಮಠ", "ವೃಷಭ", "ಬಸವ"}
MASC_LIKE_OPTIONAL = {"ವರಾಹ"}
# 109: consonant stems with the in-augment
IN_OPTIONAL = {"ಪಗಲ್", "ಇರುಳ್"}
IN_OBLIGATORY = {"ಆಗಳ್", "ಈಗಳ್", "ಸೂೞ್"}
# 114: datives that keep k (compound-like)
DAT_KE = {"ಕಾಲ್", "ಕೋಲ್", "ನಾಳ್"}
# 97/101: lexical plural suffixes
PLURAL_IR = {"ತೊೞ್ತು": "ತೊೞ್ತಿರ್", "ಪೆಣ್": "ಪೆಂಡಿರ್"}
PLURAL_DIR = {"ಅಣ್ಣ", "ಭಾವ", "ಮಾವ", "ಅಯ್ಯ", "ಅಕ್ಕ", "ಇವಳ್", "ಅವಳ್", "ಉವಳ್", "ಇವನ್", "ಅವನ್", "ಉವನ್"}
PLURAL_VIR = {"ತಂದೆ", "ತಾಯ್", "ಸೊಸೆ", "ಅತ್ತೆ"}
PLURAL_KAL = {"ಮಗ": "ಮಕ್ಕಳ್", "ನಾಳ್": "ನಾಳ್ಕಳ್", "ಕೋಳ್": "ಕೋಳ್ಕಳ್"}
PLURAL_AR_KAL = {"ಬುಧ", "ಗೋವ", "ಘೋಟಾಯ್ಲ", "ದೇವಿಯ"}


def _t(script: str, *tags) -> Term:
    return Term.make(script, *tags)


def _classify(stem: str, cls) -> set[str]:
    c = set(cls or ())
    if stem in SARVANAMA or stem in SARVANAMA_PL:
        c.add("sarvanama")
    if stem in PAVAN:
        c.add("pavan")
    if stem in SANKHYA:
        c.add("sankhya")
    if stem in DIK_AN or stem in DIK_A:
        c.add("dik")
    if stem.endswith(("ಿದು", "ಿತು", "ಿತ್ತು")) and stem not in SARVANAMA:
        c.add("gunavacana")
    if stem.endswith(("ಉದು", "ಪುದು", "ವುದು")) and len(stem) > 3:
        c.add("krt")
    return c


def _origin(stem: str, origin: str | None) -> str:
    if origin:
        return origin
    o = lexicon.guess_origin(stem)
    return lexicon.SANSKRIT if o == lexicon.SANSKRIT else lexicon.KANNADA


# ---------------------------------------------------------------- 161 orthography
def finalize(p: Prakriya) -> None:
    """161: ಮ್/ನ್ before a consonant or word-finally are written as anusvāra;
    42/209: ṟ before a consonant is written r."""
    vs_terms = p.terms
    for k, t in enumerate(vs_terms):
        nxt = next((u for u in vs_terms[k + 1:] if u.text), None)
        if t.text and t.last == "ಱ್" and nxt is not None and not nxt.has("sep") and V.is_consonant(nxt.first):
            t.text[-1] = "ರ್"
            p.log("42", "ṟ written r before a consonant")
    changed = False
    for k, t in enumerate(vs_terms):
        if not t.text:
            continue
        nxt = next((u for u in vs_terms[k + 1:] if u.text), None)
        if t.last in ("ಮ್", "ನ್") and (nxt is None or nxt.has("sep") or V.is_consonant(nxt.first)):
            if t.has("no161"):
                continue
            t.text[-1] = V.ANUSVARA
            changed = True
    if changed:
        p.log("161", "final m/n written as anusvāra")


# ---------------------------------------------------------------- Sanskrit stems (80–87)
SKT_A_TO_A = {"ಕಂಧರಾ", "ಉಪತ್ಯಕಾ", "ಕರುಣಾ", "ಅಧಿತ್ಯಕಾ", "ದಂಷ್ಟ್ರಿಕಾ", "ವಾಲುಕಾ"}
SKT_A_BOTH = {"ಗ್ರೀವಾ", "ಭಿಕ್ಷಾ"}
SKT_A_TO_E = {"ವಧ", "ಅಭಿಲಾಷ", "ಉದಾಹರಣ", "ದರ್ಭ", "ಪ್ರಶ್ನ", "ಊಹ", "ಅಳಕ"}       # 83 (lexical)
SKT_CONS_DOUBLE_U = {"ಅಪ್", "ಕ್ಷುತ್", "ಪ್ರತಿಪತ್", "ಋಕ್", "ಯಜುಸ್", "ವಿದ್ಯುತ್", "ದ್ವಿಟ್",
                     "ಪ್ರಾವೃಟ್", "ವಾಕ್"}


def adapt_sanskrit(word: str) -> list[Prakriya]:
    """Sanskrit word → Kannada nominal stem(s), sūtras 82–87."""
    def build(p: Prakriya):
        t = _t(word, lexicon.SANSKRIT)
        p.terms = [t]
        p.log("start")
        vs = t.text
        s = word
        nsyl = sum(V.is_vowel(v) for v in vs)
        if vs[-1] == V.VISARGA:                       # 87: nom. pl. minus visarga
            vs.pop()
            p.log("87", "Sanskrit nominative plural minus visarga → a-stem")
            return
        if s == "ಪಿತೃ":
            t.text = V.to_varnas("ಪಿತರ")
            return p.log("85", "ಪಿತೃ → ಪಿತರ")
        if s == "ಸಖಿ":
            t.text = V.to_varnas("ಸಖ")
            return p.log("85", "ಸಖಿ → ಸಖ")
        if s in ("ಧಾತೃ", "ಮಾಂಧಾತೃ"):
            vs[-1] = "ಅ"
            return p.log("84", "ಧಾತೃ → ಧಾತ")
        if s == "ವಿಧಾತೃ":
            t.text = V.to_varnas("ವಿಧಾತ್ರ")
            return p.log("84", "ವಿಧಾತೃ → ವಿಧಾತ್ರ")
        last = vs[-1]
        if last == "ಆ" and nsyl > 1:                  # 82
            if s in SKT_A_TO_A:
                vs[-1] = "ಅ"
                return p.log("82", "ā → a (lexical)")
            if s in SKT_A_BOTH and not p.decide("82"):
                vs[-1] = "ಅ"
                return p.log("82", "ā → a (variant)")
            vs[-1] = "ಎ"
            return p.log("82", "ā → e")
        if last in ("ಈ", "ಊ") and nsyl > 1:            # 83
            vs[-1] = S.SHORTEN[last]
            return p.log("83", "polysyllabic ī/ū shortened")
        if last == "ಋ" and p.decide("84") is False:   # 84 optional ṛ → āra
            vs[-1:] = ["ಆ", "ರ್", "ಅ"]
            return p.log("84", "ṛ → ār (optional)")
        if last == "ಅ" and s in SKT_A_TO_E and p.decide("83"):
            vs[-1] = "ಎ"
            return p.log("83", "a → e (lexical, optional)")
        if V.is_consonant(last):                     # 86
            if s.endswith(("ನ್",)):
                vs.pop()
                p.log("86", "final n dropped")
                if s in ("ಸೀಮನ್", "ಊಷ್ಮನ್") and p.decide("86"):
                    vs[-1] = "ಎ"
                    p.log("86", "a → e")
                return
            if s == "ಗೀರ್" and not p.decide("86"):
                t.text = V.to_varnas("ಗಿರೆ")
                return p.log("86", "ಗೀರ್ → ಗಿರೆ")
            if s.endswith("ಸ್") and s not in SKT_CONS_DOUBLE_U:
                if p.decide("86"):
                    vs.pop()
                    return p.log("86", "final s dropped")
                if p.decide("86"):
                    vs.extend([last, "ಉ"])
                    return p.log("86", "final consonant doubled + u")
                vs.append("ಅ")
                return p.log("86", "a added")
            if s in SKT_CONS_DOUBLE_U:
                vs.extend([last, "ಉ"])
                return p.log("86", "final consonant doubled + u")
            vs.append("ಅ")
            return p.log("86", "a added")
        p.log("84", "vowel-final Sanskrit stem used unchanged")
    return derive_all(build)


# ---------------------------------------------------------------- gender forms (98, 150–154)
def personal_stem(base: str, gender: str, number: str = "sg") -> list[str]:
    """Masculine/feminine/human-plural stems (before -ಅಂ / -ಅಳ್ / -ಅರ್) of pronouns and
    quality words. Returns stems *without* the nominative ending."""
    out = []
    if base in ("ಅದು", "ಇದು", "ಉದು"):
        v = base[0]
        if number == "pl":
            return [v + "ವರ್"]                                     # 150 ಅವರ್
        if gender == "m":
            return [v + "ವ", {"ಅ": "ಆ", "ಇ": "ಈ", "ಉ": "ಊ"}[v] + "ತ"]  # 150 ಅವ(ಂ), ಆತ(ಂ)
        if gender == "f":
            return [v + "ವಳ್", {"ಅ": "ಆ", "ಇ": "ಈ", "ಉ": "ಊ"}[v] + "ಕೆ"]  # 154
    if base == "ಆವುದು":
        return ["ಆರ್"] if number == "pl" else ["ಆವ"]                # 151
    if base == "ಎಲ್ಲದು":
        return ["ಎಲ್ಲರ್"] if number == "pl" else ["ಎಲ್ಲ"]            # 151
    if base in ("ಪೆಱತು", "ಪೆಱದು"):                                  # 152
        return ["ಪೆಱರ್"] if number == "pl" else (["ಪೆಱ"] if gender == "m" else ["ಪೆಱಳ್"])
    special = {"ಎಳದು": "ಎಳೆಯ", "ಪೞದು": "ಪೞೆಯ", "ಬಱದು": "ಬಱುವ", "ಪೊಸತು": "ಪೊಸಂಬ"}  # 153
    if base in special:
        st = special[base]
    elif base.endswith("ದು"):
        st = base[:-2] + "ಯ"                                      # 152 -ದು → -ಅ + y
    elif base.endswith("ತು"):
        st = base[:-2] + "ದ"                                      # 152 -ತು → -ದ
    else:
        st = base + ("ಯ" if base.endswith(("ಿ", "ೆ")) else "")
    if number == "pl":
        return [st + "ರ್" if st.endswith(("ಯ", "ದ", "ವ", "ಬ")) else st + "ರ್"]
    if gender == "f":
        return [st + "ಳ್"]
    return [st]


# ---------------------------------------------------------------- plural stems (95–103)
def _plural(p: Prakriya, gender: str, origin: str, cls: set[str]) -> None:
    """Turn p.terms (a singular stem) into a plural stem."""
    st = p.terms[-1]
    s = str(st)
    if gender == "n" and ("sarvanama" in cls or "gunavacana" in cls):
        if s in SARVANAMA_PL:
            return
        if s in ("ಅದು", "ಇದು", "ಉದು", "ಪೆಱದು", "ಪೆಱತು", "ಎಲ್ಲದು"):     # 95–96
            st.text = st.text[:-2] + ["ವ್", "ಉ"]
            return p.log("96", "pronoun: final syllable and the a of -avu deleted")
        if s.endswith("ದು"):                                           # 96
            st.text = st.text[:-2] + ["ಯ್", "ಅ", "ವ್", "ಉ"]
            return p.log("96", "quality word in -du: du deleted, -avu with y-glide")
        if s.endswith("ತು"):                                           # 97
            st.text = st.text[:-2] + ["ದ್", "ಉ", "ವ್", "ಉ"]
            return p.log("97", "quality word in -tu: t → d, a of -avu deleted")
    human = gender in ("m", "f") or "human" in cls
    if human:
        if s in PLURAL_IR:
            st.text = V.to_varnas(PLURAL_IR[s])
            return p.log("97", "plural -ir")
        if s in PLURAL_KAL:
            st.text = V.to_varnas(PLURAL_KAL[s])
            return p.log("101", "plural -kaḷ")
        if s in PLURAL_DIR and not p.decide("101"):
            p.terms.append(_t("ಗಳ್", "plural"))
            _bindu_103(p, gender, origin, obligatory=True)
            return p.log("101", "-gaḷ for -dir (optional)")
        if s in PLURAL_DIR:
            p.terms.append(_t("ದಿರ್", "plural"))
            _bindu_103(p, gender, origin, obligatory=True)
            return p.log("97", "plural -dir")
        if s in PLURAL_VIR:
            if p.decide("101"):
                p.terms.append(_t("ವಿರ್", "plural"))
                return p.log("97", "plural -vir")
            p.terms.append(_t("ಗಳ್", "plural"))
            return p.log("101", "-gaḷ for -vir (optional)")
        if "pavan" in cls or "sankhya" in cls:                       # 99–100
            if s in ("ಅನಿತು", "ಇನಿತು", "ಎನಿತು", "ಉನಿತು", "ಎಲ್ಲವು", "ಕೆಲವು", "ಪಲವು"):
                st.text = st.text[:-2]
                p.log("100", "final syllable lost before v")
            if st.last == "ಅ" and p.decide("99"):
                st.text.append(V.ANUSVARA)
                p.log("99", "optional bindu before b")
            if p.decide("99"):
                p.terms.append(_t("ವ್", "augment"))
                p.log("99", "v inserted")
                if p.decide("99"):
                    p.terms[-1].text = ["ಬ್"]
                    p.log("99", "v → b")
            p.terms.append(_t("ಅರ್", "plural", "vibhakti"))
            junction(p, len(p.terms) - 2, SUFFIX)
            return p.log("98", "plural -ar")
        if not p.decide("98"):
            p.terms.append(_t("ಗಳ್", "plural"))
            p.log("102", "-gaḷ with a human noun (honorific/optional)")
            return _bindu_103(p, gender, origin, obligatory=True)
        p.terms.append(_t("ಅರ್", "plural"))
        p.log("98", "masculine/feminine plural -ar")
        _nominal_junction(p, len(p.terms) - 2)
        if s in PLURAL_AR_KAL and p.decide("101"):
            p.terms.append(_t("ಕಳ್", "plural"))
            p.log("101", "-kaḷ added after -ar")
        return
    p.terms.append(_t("ಗಳ್", "plural"))
    p.log("95", "plural augment -gaḷ")
    _bindu_103(p, gender, origin, obligatory=origin == lexicon.SANSKRIT)


def _bindu_103(p: Prakriya, gender, origin, obligatory: bool):
    st = p.terms[-2]
    if st.last != "ಅ":
        return
    if obligatory or gender in ("m", "f") or p.decide("103"):
        st.text.append(V.ANUSVARA)
        p.log("103", "bindu before -gaḷ/-dir")


# ---------------------------------------------------------------- case endings (93, 104–124)
def _case_suffix(p: Prakriya, case: str) -> Term | None:
    """Choose the case-suffix allomorph (before augments). Returns None for zero endings."""
    if case == "acc":
        return _t("ಅಮ್", "case", "acc")
    if case == "ins":
        if p.has_tag("neuter_a") and not p.decide("107"):
            return _t("ಎ", "case", "ins", "ins_e")
        forms = ["ಇಮ್", "ಇಂದಮ್", "ಇಂದೆ"]
        k = 0
        while k < 2 and not p.decide("107"):
            k += 1
        return _t(forms[k], "case", "ins")
    if case == "abl":
        forms = ["ಅತ್ತಣಿಮ್", "ಅತ್ತಣಿಂದಮ್", "ಅತ್ತಣಿಂದೆ"]
        k = 0
        while k < 2 and not p.decide("116"):
            k += 1
        return _t(forms[k], "case", "abl")
    if case == "gen":
        return _t("ಅ", "case", "gen")
    if case == "loc":
        return _t("ಒಳ್" if p.decide("119") else "ಅಲ್ಲಿ", "case", "loc")
    if case == "dat":
        return _t("ಕೆ", "case", "dat")
    return None


def _decline_build(p: Prakriya, stem: str, case: str, number: str, gender: str, origin: str,
                   cls: set[str]) -> None:
    st = _t(stem, gender, origin, "nama", *cls)
    p.terms = [st]
    p.log("start")

    # ---- special paradigms
    base = PERSONAL_ALIAS.get(stem, stem)
    if number == "pl":
        base = {"ನೀನ್": "ನೀಮ್", "ಆನ್": "ಆಮ್", "ತಾನ್": "ತಾಮ್"}.get(base, base)
    if base in PERSONAL:
        return _personal(p, base, case)
    if stem in ("ಏನ್", "ಏತಱ್"):
        return _en(p, case)
    if stem in TIME_WORDS and case in ("nom", "acc", "loc") and number == "sg":
        return p.log("121", "time word: nom = acc = loc")
    if "avyaya" in cls:
        return p.log("90", "indeclinable: no case ending")

    # ---- number
    if number == "pl":
        _plural(p, gender, origin, cls)
        stem_t = p.terms[-1]
    else:
        stem_t = st
    a_final = stem_t.last == "ಅ" and not stem_t.has("plural")
    masc_pattern = gender == "m" or str(st) in MASC_LIKE or (
        str(st) in MASC_LIKE_OPTIONAL and p.decide("121a")) or (gender == "f" and a_final)
    if a_final and number == "sg" and not masc_pattern:
        p.tags.add("neuter_a")

    # ---- 119/121: a-final direction words: nom = acc = loc in -al; u-final take loc -e
    if number == "sg" and str(st) in DIK_A and case in ("nom", "acc", "loc"):
        st.text.append("ಲ್")
        st.tags.add("no161")
        return p.log("121", "direction word: -al serves as nom., acc. and loc.")
    if number == "sg" and str(st) in DIK_U_E and case == "loc" and p.decide("119"):
        if str(st) == "ನಡು":
            st.text.extend(["ವ್", "ಎ"])
            return p.log("119", "ನಡು + e: v-glide")
        st.text[-1] = "ಎ"
        return p.log("119", "direction word: u → e in the locative")
    if number == "sg" and str(st) == "ಮೇಲ್" and case == "loc" and p.decide("120"):
        st.text.append("ಎ")
        return p.log("120", "ಮೇಲ್ + locative -e")
    # ---- 99: human singular of numerals (ಒರ್ಬಂ)
    if number == "sg" and gender == "m" and "sankhya" in cls and case == "nom" and st.last == "ರ್":
        p.terms.append(_t("ಬ್" if p.decide("99") else "ವ್", "augment"))
        p.terms.append(_t("ಅಮ್", "case"))
        p.log("99", "numeral, masculine: v/b augment + -aṃ")
        return finalize(p)

    # ---- nominative
    if case == "nom":
        if a_final and number == "sg":
            p.terms.append(_t("ಮ್", "case", "nom"))
            p.log("105", "nominative singular: bindu after an a-stem")
        else:
            p.log("105", "nominative: zero ending")
        finalize(p)
        return

    # ---- vocative (123–125)
    if case == "voc":
        return _vocative(p, a_final, masc_pattern, number)

    suf = _case_suffix(p, case)
    vowel_initial = V.is_vowel(suf.first)

    # ---- augments
    cur = p.terms[-1]
    cs = str(cur)
    if number == "sg" and "dik" in cls and case != "acc" and cur.last in ("ಉ", "ಅ", "ಎ"):
        if cur.last == "ಉ":
            cur.text.pop()
        elif cur.last == "ಎ":
            cur.text.append("ಯ್")
        else:
            cur.text.pop()
        p.terms.append(_t("ಅಣ್", "augment"))
        p.log("110", "direction word: augment -aṇ")
    elif cur.last == "ಉ" and case != "acc" and (
            cls & {"sarvanama", "gunavacana", "krt", "sankhya", "pavan"} or cs in SARVANAMA_PL):
        cur.text.pop()
        p.terms.append(_t("ಅಱ್", "augment", "ar_aug"))
        p.log("110", "augment -aṟ (u replaced)")
    elif a_final and number == "sg":
        if masc_pattern:
            if vowel_initial:
                p.terms.append(_t("ನ್", "augment"))
                p.log("105" if str(st) not in MASC_LIKE else "121a", "masculine a-stem: n-augment")
            elif case == "dat":
                p.terms.append(_t("ನ್", "augment"))
                suf = _t("ಗೆ", "case", "dat")
                p.log("113", "masculine a-stem dative -ṃge")
        else:
            if case == "acc":
                if origin == lexicon.SANSKRIT and not stem_t.has("upacara"):
                    aug = "ಮ್"
                else:
                    aug = "ಮ್" if p.decide("106") else "ನ್"
                p.terms.append(_t(aug, "augment"))
                p.log("106", f"neuter a-stem accusative: {V.from_varnas([aug])}-augment")
            elif case == "dat":
                if p.decide("113"):
                    suf = _t("ಕ್ಕೆ", "case", "dat")
                    p.log("113", "neuter a-stem dative -kke")
                else:
                    p.log("113", "neuter a-stem dative -ke")
            else:
                p.terms.append(_t("ದ್", "augment"))
                p.log("106", "neuter a-stem: d-augment")
    elif number == "sg" and case not in ("acc",) and _takes_in(p, cur, case, origin):
        pass  # _takes_in appended the augment
    if case == "dat" and str(suf) == "ಕೆ" and not (a_final and number == "sg" and not masc_pattern):
        last = p.terms[-1]
        if last.has("ar_aug") or (last.last == "ಱ್"):
            last.text[-1] = "ರ್"
            p.log("114", "-aṟ + ke: ṟ → r, no voicing")
        elif str(last) in DAT_KE:
            p.log("114", "compound-like dative: no voicing (-ke)")
        else:
            suf = _t("ಗೆ", "case", "dat")
            p.log("113", "dative -ge")
            if str(last).endswith("ರ್") and len(last.text) > 1 and last.text[-2] == "ಅ" \
                    and (last.has("plural") or len(last.text) > 3) and p.decide("115") is False:
                suf = _t("ಗ್ಗೆ", "case", "dat")
                p.log("115", "dative plural: g doubled (optional)")

    if suf.has("ins_e") and p.terms[-1].has("augment") and str(p.terms[-1]) == "ಅತ್ತಣ್":
        return  # 116 forbids
    p.terms.append(suf)
    # ---- junctions
    for k in range(len(p.terms) - 1):
        a, b = p.terms[k], p.terms[k + 1]
        if a.text and b.text and V.is_vowel(b.first):
            b.tags.add("vibhakti")
            _nominal_junction(p, k)
    if case == "gen" and p.decide("117") is False:
        p.terms[-1].text[-1] = "ಆ"
        p.log("117", "genitive -a lengthened (optional)")
    finalize(p)


def _nominal_junction(p: Prakriya, k: int) -> None:
    """Stem/augment + vowel-initial case ending. i/e/ī/ai-stems keep their vowel with a
    y-glide (no lōpa before a case ending); everything else follows the Sandhi chapter."""
    L, R = p.terms[k], p.terms[k + 1]
    if V.is_vowel(L.last) and L.last in ("ಇ", "ಈ", "ಎ", "ಏ", "ಐ") and not L.has("vibhakti"):
        R.text.insert(0, "ಯ್")
        return p.log("53", "ya-āgama before a case ending")
    if R.has("voc") and L.last in ("ಊ", "ಋ", "ಓ", "ಔ"):
        R.text.insert(0, "ವ್")
        return p.log("124", "va-āgama before the vocative -e")
    junction(p, k, SUFFIX)


def _takes_in(p: Prakriya, cur: Term, case: str, origin: str) -> bool:
    """108–109: the -in- augment."""
    s = str(cur)
    last = cur.last
    if V.is_consonant(last):
        if s in IN_OBLIGATORY or (s in IN_OPTIONAL and p.decide("109")):
            p.terms.append(_t("ಇನ್", "augment"))
            p.log("109", "consonant stem: -in- augment")
            return True
        return False
    if last in ("ಉ", "ಊ", "ಋ", "ೠ", "ಓ", "ಔ") or (last == "ಎ" and "adverb" in cur.tags):
        v_glide = last in ("ಊ", "ಋ", "ೠ", "ಓ", "ಔ") or origin == lexicon.SANSKRIT or _short_stem(cur)
        optional = case == "ins" or (v_glide and last == "ಉ")
        if optional and not p.decide("108"):
            return False
        if last == "ಉ" and not v_glide:
            cur.text.pop()
        elif last == "ಎ":
            cur.text.pop()
        else:
            cur.text.append("ವ್")
        p.terms.append(_t("ಇನ್", "augment"))
        p.log("108", "-in- augment" + (" (optional)" if optional else ""))
        return True
    return False


def _short_stem(t: Term) -> bool:
    from .sandhi import namarudhi_blocks_lopa
    return namarudhi_blocks_lopa(t)


def _vocative(p: Prakriya, a_final: bool, masc_pattern: bool, number: str) -> None:
    cur = p.terms[-1]
    if number == "pl":
        if str(cur).endswith(("ಗಳ್", "ಕಳ್")) or (str(cur).endswith("ರ್") and p.decide("125")):
            p.terms.append(_t("ಇರ", "case", "voc"))
            junction(p, len(p.terms) - 2, SUFFIX)
            return p.log("125", "vocative plural -ira")
        p.terms.append(_t("ಏ" if p.decide("124") else "ಎ", "case", "voc"))
        return p.log("124", "vocative plural + e/ē")
    p.log("123", "vocative: nominative ending dropped")
    if p.decide("124"):
        if a_final:
            p.terms.append(_t("ನ್" if masc_pattern else "ಮ್", "augment"))
            p.log("124", "bindu before vocative -ē")
        p.terms.append(_t("ಏ" if p.decide("124") else "ಎ", "case", "voc"))
        _nominal_junction(p, len(p.terms) - 2)
        return p.log("124", "vocative particle -e/-ē")
    if V.is_vowel(cur.last) and cur.last in S.LENGTHEN and p.decide("123") is False:
        cur.text[-1] = S.LENGTHEN[cur.last]
        p.log("123", "long kāku")


def _personal(p: Prakriya, base: str, case: str) -> None:
    """146: ನೀನ್, ಆನ್, ತಾನ್ (and plurals ನೀಮ್, ಆಮ್, ತಾಮ್)."""
    oblique, dat_stem = PERSONAL[base]
    t = p.terms[0]
    if case == "nom":
        t.text = V.to_varnas(base)
        p.log("146", "nominative")
        return finalize(p)
    if case == "dat":
        t.text = V.to_varnas(dat_stem)
        p.terms.append(_t("ಗೆ", "case"))
        return p.log("146", "dative ninage/enage/tanage")
    t.text = V.to_varnas(oblique)
    t.tags.add(lexicon.KANNADA)
    p.log("146", "oblique stem")
    suf = _case_suffix(p, case) if case != "voc" else None
    if suf is None:
        return
    p.terms.append(suf)
    t.text.append(t.text[-1])
    p.log("146", "n/m doubled before a vowel ending")
    finalize(p)


def _en(p: Prakriya, case: str) -> None:
    """112: ಏನ್."""
    t = p.terms[0]
    if case == "nom":
        if not p.decide("112"):
            t.text = V.to_varnas("ಏತಱ್")
        return p.log("112", "nominative ēn ~ ētaṟ")
    if case == "dat":
        t.text = V.to_varnas("ಏತರ್ಕೆ" if p.decide("112") else "ಏಕೆ")
        return p.log("112", "dative ētarke ~ ēke")
    t.text = V.to_varnas("ಏತಱ್")
    p.log("112", "oblique stem ētaṟ")
    suf = _case_suffix(p, case)
    if suf:
        p.terms.append(suf)
    finalize(p)


# ---------------------------------------------------------------- public API
def decline(stem: str, case: str, number: str = "sg", gender: str | None = None,
            origin: str | None = None, cls=()) -> list[Prakriya]:
    stem = V.normalize(stem)
    if stem.endswith("ಂ") and len(stem) > 1:
        stem = stem[:-1]        # accept nominative citation forms like ಮರಂ
    cls = _classify(stem, cls)
    origin = _origin(stem, origin)
    genders = [gender] if gender else (["n", "m"] if not cls & {"sarvanama"} else ["n"])
    out = []
    for g in genders:
        out.extend(derive_all(_decline_build, stem, case, number, g, origin, cls))
    return out


def paradigm(stem: str, gender: str | None = None, origin: str | None = None, cls=()):
    g = gender or "n"
    return {(c, n): decline(stem, c, n, g, origin, cls) for n in NUMBERS for c in CASES}


def forms(stem: str, case: str, number: str = "sg", **kw) -> set[str]:
    return {p.result() for p in decline(stem, case, number, **kw)}


# ---------------------------------------------------------------- within-word variants
def add_um(form: str) -> list[Prakriya]:
    """122: the conjunctive particle -ಉಂ / -ಅಂ after an inflected form."""
    from .sandhi import results  # noqa: F401  (documented dependency)
    out = []
    f = V.normalize(form)
    def mk(new, note):
        p = Prakriya([_t(f)])
        p.terms = [_t(new)]
        p.log("122", note)
        out.append(p)
    vs = V.to_varnas(f)
    if f.endswith(("ಗೆ", "ಕೆ")):
        mk(V.from_varnas(vs[:-1] + ["ಅ", V.ANUSVARA]), "dative + -aṃ (e elided)")
        mk(f + "ಯುಂ", "dative + -uṃ (y-glide)")
    elif f.endswith("ಒಳ್") or f.endswith("ೊಳ್"):
        mk(V.from_varnas(vs + ["ಅ", V.ANUSVARA]), "locative -oḷ + -aṃ")
    elif f.endswith("ಂ"):
        mk(V.from_varnas(vs[:-1] + ["ನ್", "ಉ", V.ANUSVARA]), "nominative -aṃ + -uṃ")
    elif V.is_vowel(vs[-1]):
        glide = "ಯ್" if vs[-1] in ("ಇ", "ಈ", "ಎ", "ಏ", "ಐ") else "ವ್"
        mk(V.from_varnas(vs + [glide, "ಉ", V.ANUSVARA]), "+ -uṃ")
    else:
        mk(V.from_varnas(vs + ["ಉ", V.ANUSVARA]), "+ -uṃ")
    return out


def word_variants(word: str) -> list[Prakriya]:
    """Optional within-word changes of the Nāma chapter applied to a whole word:
    77 (-tu → -ttu), 104 (m → v), 117 (lengthening in particles), 120 (mundu → muntu),
    147 (ninnadu → ninatu), 149 (contractions), 157 (avu → au, ayi → ai, -aṃ → -oṃ),
    159 (p → h), 160 (antappaṃ → antahaṃ / annaṃ), 161 (homorganic nasal)."""
    w = V.normalize(word)
    rules = []

    def add(rule, new, note):
        rules.append((rule, new, note))

    if w.endswith(("ದಂ", "ವಂ", "ಪಂ", "ಬಂ")) and len(w) > 3:
        add("73", w[:-1], "kṛt stem: personal ending -aṃ stripped")
    if w in DIK_U_E:
        add("119", w[:-1] + "ೆ", "direction word: u → e (locative)")
    for k in range(2, len(w)):
        if w[k] == "ೊ":
            add("118", w[:k] + "ೋ" + w[k + 1:], "medial o lengthened (optional)")
            break
        if w[k] == "ಂ" and w[k - 1] == "ಯ":
            add("118", w[:k] + "ಾ" + w[k:], "medial a lengthened (optional)")
            break
    if w.endswith("ತು") and not w.endswith("ತ್ತು"):
        add("77", w[:-2] + "ತ್ತು", "adjective -tu doubled")
    if "ಮ" in w[1:]:
        k = w.index("ಮ", 1)
        add("104", w[:k] + "ವ" + w[k + 1:], "m → v")
    if w.endswith("ಟ") or w.endswith("ಡ"):
        add("117", w + "ಾ", "final a lengthened (grief/agitation)")
    for a, b in (("ಮುಂದು", "ಮುಂತು"), ("ಪಿಂದು", "ಪಿಂತು")):
        if w.startswith(a):
            add("120", b + w[len(a):], "du → tu")
    for a, b in (("ನಿನ್ನದು", "ನಿನತು"), ("ಎನ್ನದು", "ಎನತು"), ("ತನ್ನದು", "ತನತು"),
                 ("ನಿಮ್ಮದು", "ನಿಮತು"), ("ಎಮ್ಮದು", "ಎಮತು"), ("ತಮ್ಮದು", "ತಮತು")):
        if w == a:
            add("147", b, "possessive")
            add("147", b[:-1] + "್ತು", "possessive, t doubled")
    if w == "ಎತ್ತಣದು":
        add("149", "ಎತ್ತಣ್ತು", "contraction")
    if w == "ಆರದು":
        add("149", "ಆರ್ತು", "contraction")
    if w.startswith("ಅವು"):
        add("157", "ಔ" + w[3:], "avu → au")
    if "ವು" in w[1:]:
        k = w.index("ವು", 1)
        if w[k - 1] not in "ಾಿೀುೂೆೇೈೊೋೌ್ಂ":
            add("157", w[:k] + "ೌ" + w[k + 2:], "avu → au")
    if "ಯಿ" in w[1:] or "ಯ್" in w[1:]:
        k = w.index("ಯಿ", 1) if "ಯಿ" in w[1:] else w.index("ಯ್", 1)
        if w[k - 1] not in "ಾಿೀುೂೆೇೈೊೋೌ್ಂ":
            add("157", w[:k] + "ೈ" + w[k + 2:], "ayi/ay → ai")
    if w.endswith("ಂ") and len(w) > 2 and w[-2] not in "ಾಿೀುೂೆೇೈೊೋೌ್":
        add("157", w[:-1] + "ೊಂ", "-aṃ → -oṃ")
    if w.startswith("ಪ") and not w.startswith("ಪ್"):
        add("159", "ಹ" + w[1:], "p → h (dēśi)")
    for a in ("ಅಂತಪ್ಪಂ", "ಇಂತಪ್ಪಂ", "ಉಂತಪ್ಪಂ", "ಎಂತಪ್ಪಂ"):
        if w == a:
            add("160", a.replace("ಪ್ಪ", "ಹ"), "pp → h")
            add("160", a[0] + "ನ್ನಂ", "gaḍa sense")
    nasal = {"ಕ": "ಙ", "ಖ": "ಙ", "ಗ": "ಙ", "ಘ": "ಙ", "ಚ": "ಞ", "ಛ": "ಞ", "ಜ": "ಞ", "ಝ": "ಞ",
             "ಟ": "ಣ", "ಠ": "ಣ", "ಡ": "ಣ", "ಢ": "ಣ", "ತ": "ನ", "ಥ": "ನ", "ದ": "ನ", "ಧ": "ನ",
             "ಪ": "ಮ", "ಫ": "ಮ", "ಬ": "ಮ", "ಭ": "ಮ", "ಮ": "ಮ"}
    for k, ch in enumerate(w[:-1]):
        if ch == "ಂ" and w[k + 1] in nasal:
            add("161", w[:k] + nasal[w[k + 1]] + "್" + w[k + 1:], "homorganic nasal")
            break
    out = []
    for rule, new, note in rules:
        p = Prakriya([_t(w)])
        p.terms = [_t(new)]
        p.log(rule, note)
        out.append(p)
    return out
