"""Taddhita-prakaraṇa (sūtras 197–215): secondary derivation from nouns.

``derive(base, suffix)`` → list[Prakriyā]; the result is given both as the bare derived
stem and in its nominative citation form (a-final stems take -ṃ, 105).

General junction (209): before a vowel-initial taddhita suffix the base loses its final
vowel (in a few words its final syllable); compound sandhi (Samāsa) and verbal sandhi
(Ākhyāta: ḍ → ṭ) also apply inside taddhita formations.
"""
from __future__ import annotations

from . import lexicon
from . import samjna as S
from . import varna as V
from .prakriya import Prakriya, Term
from .sandhi import COMPOUND, junction

SUFFIXES = {
    # suffix: (sūtra, meaning)
    "ಇಗ": ("197", "maker / seller / holder of X"),
    "ವಳ": ("198", "manager of X"), "ವಳ್ಳ": ("198", "manager of X"), "ಆಯ್ತ": ("198", "dealer in X"),
    "ವಡಿಗ": ("198", "one who sets out X"),
    "ಕಾಱ": ("199", "one engaged with X"), "ಗಾಱ": ("199", "maker of X"),
    "ಇಚ": ("200", "born in X"),
    "ಕುಟಿಗ": ("201", "one intent on X"), "ಗ": ("201", "one given to X"), "ಉಳಿಗ": ("201", "one living by X"),
    "ಗುಳಿ": ("202", "one addicted to X"), "ಉಣಿ": ("202", "eater of X"),
    "ಉಕ": ("203", "habitual agent"), "ಕುಳಿ": ("203", "habitual agent"), "ಆಳಿ": ("203", "habitual agent"),
    "ಇಕ": ("203", "habitual agent"), "ಅಡಿಗ": ("203", "living by X"),
    "ಉಗ": ("204", "dealer in X"), "ಅಟಿಗ": ("204", "performer / bearer of X"),
    "ಕ": ("205", "one having quality X"), "ಇಲ": ("205", "one living in X"),
    "ಉಳ್ಳ": ("206", "having X"), "ಒಡೆಯ": ("206", "lord of X"), "ವಂತ": ("206", "possessing X"),
    "ವಣಿಗ": ("206", "one living to eat X"),
    "ಅನೆಯ": ("207", "ordinal"), "ಮೆ": ("207", "X times"),
    "ಇತಿ": ("208", "feminine"), "ತಿ": ("208", "feminine"), "ಅಳ್": ("208", "feminine"),
    "ವಿ": ("210", "abstract"), "ವು": ("210", "abstract"), "ವೆ": ("210", "abstract"),
    "ತ": ("210", "abstract"), "ತೆ": ("210", "abstract"),
    "ಇಕೆ": ("211", "abstract (animate quality)"), "ತನ": ("211", "abstract (-ness)"),
    "ಉಮೆ": ("211", "abstract"), "ಅಮೆ": ("211", "abstract"), "ಗೆ": ("211", "abstract"),
    "ಕೆ": ("211", "abstract"), "ಪು": ("211", "abstract"), "ಪಿ": ("211", "abstract"),
    "ಉ": ("211", "abstract"),
    "ವೋಲ್": ("214", "like X"), "ವೊಲ್": ("214", "like X"), "ಅಂತೆ": ("214", "like X"),
    "ಅಂತೆವೋಲ್": ("214", "like X"), "ಅಂತೆವೊಲ್": ("214", "like X"),
    "ಆಯಿಲ": ("215", "having X"), "ವಳಿ": ("215", "manner of X"),
}
NUM_ME = {"ಒಂದು": "ಒರ್", "ಎರಡು": "ಇರ್", "ಮೂಱು": "ಮೂರ್", "ಸಾಸಿರ": "ಸಾಸಿರ್"}
FINAL_SYLLABLE_LOSS_209 = {"ಏಱು", "ಓದು", "ದೀವಿಗೆ"}


def _vs(s):
    return V.to_varnas(s)


def derive(base: str, suffix: str) -> list[Prakriya]:
    base, suffix = V.normalize(base), V.normalize(suffix)
    sid = SUFFIXES.get(suffix, ("209", ""))[0]
    out: list[Prakriya] = []

    def mk(text, rule, note):
        p = Prakriya([Term.make(base), Term.make(suffix)])
        p.terms = [Term.make(t) for t in text.split(" ")]
        for t in p.terms[1:]:
            t.tags.add("sep")
        p.log(rule, note)
        out.append(p)
        if " " not in text and V.to_varnas(text)[-1] == "ಅ":
            q = Prakriya([Term.make(base), Term.make(suffix)])
            q.terms = [Term.make(text), Term.make("ಂ")]
            q.history = list(p.history)
            q.log("105", "nominative singular -ṃ")
            out.append(q)

    bv, sv = _vs(base), _vs(suffix)
    vowel_initial = V.is_vowel(sv[0])

    # ---- specific rules
    if suffix == "ಗಾಱ" and base in ("ಕಮ್ಮ", "ಕುಂಬ"):
        mk(V.from_varnas(_vs(base)[:-1] + ["ಆ", "ಱ್", "ಅ"]), "199", "ಗ of -gāṟa deleted after kamma/kumba")
    if suffix == "ಗಾಱ" and bv[-1] == "ಉ":
        mk(base + "ಂಗಾಱ", "200", "u-stem: anusvāra before -gāṟa")
        mk(V.from_varnas(bv[:-1] + ["ಅ"]) + "ಗಾಱ", "200", "u-stem: u → a before -gāṟa")
    if suffix == "ಗುಳಿ":
        mk((base if bv[-1] != "ಅ" else base) + "ಂಗುಳಿ", "202", "anusvāra before -guḷi")
    if suffix == "ಮೆ" and base in NUM_ME:
        mk(NUM_ME[base] + "ಮೆ", "207", "numeral in combining form + -me")
    if suffix in ("ವೋಲ್", "ವೊಲ್") and bv[-1] == "ಅ":
        mk(base + "ಂಬೋಲ್" if suffix == "ವೋಲ್" else base + "ಂಬೊಲ್", "214", "a-final: anusvāra, v → b")
    if suffix == "ವೋಲ್":
        mk(base + "ವೊಲ್", "214", "vōl shortened")
    if suffix in ("ವೋಲ್", "ವೊಲ್", "ಅಂತೆ"):
        mk(base + " " + suffix, "214", "particle written as a separate word")
    if suffix in ("ವಳಿ", "ವಳ") and bv[-1] in ("ಎ", "ಇ", "ಉ"):
        mk(V.from_varnas(bv[:-1] + ["ಅ"]) + suffix, "215", "stem-final vowel → a")
    if suffix == "ಅ" and bv[-1] == "ಉ" and len(bv) > 2 and bv[-2] == "ಡ್":
        mk(V.from_varnas(bv[:-2] + ["ಟ್", "ಅ"]), "209", "ḍ → ṭ (Ākhyāta rule) + a")
    if suffix == "ಪು" and base == "ಪಿರಿದು":
        mk("ಪೆಂಪು", "212", "ಪಿರಿದು + -pu → ಪೆಂಪು")
    if suffix in ("ಇತಿ", "ತಿ"):
        if bv[-1] == "ಅ" and len(bv) > 2 and bv[-2] in ("ಱ್", "ರ್"):          # -gāṟa/-kāṟa → -gārti
            mk(V.from_varnas(bv[:-2] + ["ರ್", "ತ್", "ಇ"]), "208", "-ti after -gāṟa/-kāṟa (ṟ → r)")
            mk(V.from_varnas(bv[:-1] + ["ತ್", "ಇ"]), "208", "-ti after -ṟa")
        if bv[-1] == "ಅ" and len(bv) > 2 and bv[-2] == "ಳ್":                  # -vaḷa → -vaḷti
            mk(V.from_varnas(bv[:-1] + ["ತ್", "ಇ"]), "208", "-ti after -vaḷa")
        if bv[-1] == "ಎ":                                                      # ಪೊಲೆ → ಪೊಲತಿ
            mk(V.from_varnas(bv[:-1] + ["ಅ", "ತ್", "ಇ"]), "208", "e → a + -ti")
        if bv[-1] == "ಇ":                                                      # ಕುಟುಂಬಿ → ಕುಟುಂಬಿತ್ತಿ
            mk(base + "ತ್ತಿ", "208", "i-stem + -tti")
    if suffix in ("ವಿ", "ವು", "ವೆ"):                                            # 210 linking a
        if V.is_vowel(bv[-1]):
            mk(V.from_varnas(bv[:-1] + ["ಅ"] + sv), "210", "stem-final vowel → linking a")
        else:
            mk(V.from_varnas(bv + ["ಅ"] + sv), "210", "linking a after a consonant stem")
        mk(base + suffix, "210", "without linking a (piriduṃ)")
    if suffix == "ತ" and base in FINAL_SYLLABLE_LOSS_209:
        mk(V.from_varnas(bv[:-2] + ["ತ್", "ಅ"]), "209", "final syllable lost before -ta")
    if suffix == "ಉಣಿ" and V.is_consonant(bv[-1]) and sum(V.is_vowel(v) for v in bv) == 1:
        mk(V.from_varnas(bv + [bv[-1]]) + "ುಣಿ", "202", "final consonant doubled before -uṇi")
    if suffix == "ಅಟಿಗ" and base == "ದೀವಿಗೆ":
        mk("ದೀವಟಿಗ", "204", "final syllable lost")
    if suffix == "ಅಟಿಗ" and V.is_consonant(bv[-1]):
        lv = list(bv)
        for k, v in enumerate(lv):
            if v in S.DIRGHA:
                lv[k] = S.SHORTEN.get(v, v)
                break
        mk(V.from_varnas(lv + [lv[-1], "ಅ", "ಟ್", "ಇ", "ಗ್", "ಅ"]), "204", "shortened, doubled + -aṭiga")
    if suffix == "ಇಲ" and bv[-1] in ("ಎ", "ಅ"):
        mk(base + "ಯಿಲ", "205", "y-glide before -ila")
    if suffix == "ಇಚ":
        lv = list(bv)
        for k in range(len(lv) - 1, -1, -1):
            if lv[k] in S.DIRGHA:
                lv[k] = S.SHORTEN[lv[k]]
                mk(V.from_varnas(lv + ["ಇ", "ಚ್", "ಅ"]), "200", "upadhā vowel shortened")
                break
    if suffix in ("ಉಳ್ಳ", "ಒಡೆಯ"):
        if bv[-1] == "ಅ":
            aug = "ನ್" if base in ("ನೆಲ",) else "ಮ್"
            mk(V.from_varnas(bv + [aug] + sv), "206", f"{V.from_varnas([aug])}-augment before {suffix}")
        if bv[-1] in ("ಎ", "ಇ"):
            mk(V.from_varnas(bv + ["ಯ್"] + sv), "206", "y-glide")
        if V.is_consonant(bv[-1]) and bv[-1] == "ತ್":
            mk(V.from_varnas(bv[:-1] + ["ದ್"] + sv), "206", "t → d before a vowel (Sanskrit)")
    if suffix in ("ಅಂತೆ", "ಅಂತೆವೋಲ್", "ಅಂತೆವೊಲ್") and bv[-1] in ("ಇ", "ಎ", "ಈ"):
        mk(V.from_varnas(bv + ["ಯ್"] + sv), "214", "y-glide before ante")
    if suffix == "ಇಕೆ" and V.is_consonant(bv[-1]):
        return out  # 211: -ike not after consonant-final stems (fault)
    if suffix == "ತನ" and lexicon.guess_origin(base) == lexicon.SANSKRIT:
        return out  # 211: -tana not with Sanskrit stems
    if suffix == "ಇಕೆ":
        mk(V.from_varnas(bv[:-1] + sv[:-2] + ["ಕ್", "ಕ್", "ಎ"]) if V.is_vowel(bv[-1]) else base + "ಇಕ್ಕೆ",
           "211", "-ike geminated (optional)")

    # ---- general 209: vowel-initial suffix replaces the base-final vowel
    if vowel_initial:
        if V.is_vowel(bv[-1]):
            mk(V.from_varnas(bv[:-1] + sv), "209", "base-final vowel lost before a vowel-initial suffix")
        else:
            p = Prakriya([Term.make(base, "kannada"), Term.make(suffix)])
            junction(p, 0, COMPOUND)
            mk(p.result(), "209", "consonant stem + vowel-initial suffix")
    else:
        p = Prakriya([Term.make(base, "kannada"), Term.make(suffix)])
        junction(p, 0, COMPOUND)
        mk(p.result(), sid, f"-{suffix}")
        if p.result() != base + suffix:
            mk(base + suffix, sid, f"-{suffix} (no junction change)")
    return out


def root_noun(root: str) -> list[Prakriya]:
    """213: action nouns from roots by vowel change / ḍ → ṭ."""
    out = []
    vs = _vs(V.normalize(root))

    def mk(text, note):
        p = Prakriya([Term.make(root)])
        p.terms = [Term.make(text)]
        p.log("213", note)
        out.append(p)
    first = next(k for k, v in enumerate(vs) if V.is_vowel(v))
    v0 = vs[first]
    if v0 == "ಇ":
        mk(V.from_varnas(vs[:first] + ["ಏ"] + vs[first + 1:]), "i → ē")
    if v0 == "ಉ":
        mk(V.from_varnas(vs[:first] + ["ಓ"] + vs[first + 1:]), "u → ō")
    if v0 in S.LENGTHEN:
        mk(V.from_varnas(vs[:first] + [S.LENGTHEN[v0]] + vs[first + 1:]), "vowel lengthened")
    if vs[-1] == "ಉ" and len(vs) > 2 and vs[-2] == "ಡ್":
        mk(V.from_varnas(vs[:-2] + ["ಟ್", "ಅ", V.ANUSVARA]), "ḍu → ṭa + nominative")
    mk(root, "root used as a noun")
    return out


def feminine(base: str) -> list[Prakriya]:
    """208: feminine of a-final agent nouns: -iti / -ti / -aḷ / final a → e."""
    out = []
    bv = _vs(V.normalize(base))
    for suf in ("ಇತಿ", "ಅಳ್"):
        out.extend(derive(base, suf))
    if bv[-1] == "ಅ":
        p = Prakriya([Term.make(base)])
        p.terms = [Term.make(V.from_varnas(bv[:-1] + ["ಎ"]))]
        p.log("208", "feminine: final a → e")
        out.append(p)
    return out
