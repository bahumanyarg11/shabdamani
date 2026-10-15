"""Word analyser: surface form → derivations under the Śabdamaṇidarpaṇa.

Strategy: *generate and verify*. Candidate lemmas are proposed (from an index of
Kēśirāja's Dhātupāṭha and closed classes, and from ending templates learned automatically
from the generators), and a reading is accepted only if the engine regenerates the exact
surface form. Every analysis therefore carries a full sūtra-by-sūtra prakriyā.

    >>> from shabdamani.analyze import analyze
    >>> for a in analyze("ಮಾಡಿದಂ"): print(a.describe())

Readings are labelled with their evidence:
  lexicon   — lemma attested in the SMD Dhātupāṭha / examples / Prayōgasāra / closed classes
  inferred  — lemma not attested; form is grammatical for a hypothesised stem
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

from . import lexicon
from . import varna as V
from .prakriya import Prakriya
from .sutras import dhatupatha, load, prayogasara

CASE_LABEL = {"nom": "nominative", "acc": "accusative", "ins": "instrumental", "dat": "dative",
              "abl": "ablative", "gen": "genitive", "loc": "locative", "voc": "vocative"}


@dataclass
class Analysis:
    word: str
    lemma: str
    pos: str                       # noun | verb | pronoun | avyaya | compound | ...
    features: dict = field(default_factory=dict)
    evidence: str = "inferred"     # lexicon | inferred
    prakriya: Prakriya | None = None
    parts: list = field(default_factory=list)     # for clitics / compounds: sub-analyses
    notes: list = field(default_factory=list)
    score: float = 0.0

    def feature_str(self) -> str:
        f = self.features
        order = ("form", "case", "number", "gender", "person", "tense", "clitic", "type", "meaning")
        return ", ".join(f"{f[k]}" for k in order if f.get(k))

    def describe(self, trace: bool = False) -> str:
        head = f"{self.word}  ←  {self.lemma}  [{self.pos}; {self.feature_str()}]  ({self.evidence})"
        lines = [head]
        for n in self.notes:
            lines.append(f"    note: {n}")
        for sub in self.parts:
            lines.append("    + " + sub.describe().replace("\n", "\n      "))
        if trace and self.prakriya is not None:
            lines.append(self.prakriya.trace(load()))
        return "\n".join(lines)

    def rules(self) -> list[str]:
        if not self.prakriya:
            return []
        return [s.rule for s in self.prakriya.history if s.rule not in ("start",)]


def _canon(s: str) -> str:
    return V.canonical(s)


# ---------------------------------------------------------------- closed classes
@lru_cache(maxsize=1)
def avyayas() -> dict[str, str]:
    out = {}
    for r in load().records:
        if r.get("chapter") != "avyaya":
            continue
        for e in r.get("examples") or []:
            w = e.get("output")
            if w and " " not in w and not e.get("input"):
                out.setdefault(_canon(w), (e.get("note") or "").replace("meaning:", "").strip())
    for e in prayogasara():
        if e.get("pos") in ("adverb", "particle"):
            out.setdefault(_canon(e["word"]), e.get("meaning_en", ""))
    # frequent particles / adverbs of Old Kannada (also listed in sūtras 88, 90, 300–322)
    for w, m in {"ಮತ್ತೆ": "again", "ಮೇಣ್": "or", "ದಲ್": "indeed", "ವಲಂ": "indeed", "ಗಡ": "it seems",
                 "ಅಂತೆ": "thus", "ಇಂತು": "thus", "ಅಂತು": "so", "ಎಂತು": "how", "ಮಿಗೆ": "exceedingly",
                 "ಬಳಿಕ": "afterwards", "ಆಗಳ್": "then", "ಈಗಳ್": "now", "ಎಂದುಂ": "ever", "ಎಲೆ": "O",
                 "ಅಯ್ಯೋ": "alas", "ಅಕ್ಕಟ": "alas", "ಒಡನೆ": "at once", "ಮುನ್ನಂ": "before", "ಇನ್ನುಂ": "still",
                 "ಆದೊಡಂ": "even so", "ಅಲ್ಲದೆ": "besides", "ಇಲ್ಲ": "is not", "ಅಲ್ಲ": "is not",
                 "ಬೇಗಂ": "quickly", "ಕೂಡೆ": "together", "ಮುಂದೆ": "in front", "ಪಿಂದೆ": "behind",
                 "ಒಳಗೆ": "inside", "ಪೊಱಗೆ": "outside", "ಮೇಲೆ": "above", "ಕೆಳಗೆ": "below",
                 "ಉಂಟು": "there is", "ಎನೆ": "when said", "ಎಂದು": "saying (quotative)"}.items():
        out.setdefault(_canon(w), m)
    return out


PRONOUN_BASES = ["ನೀನ್", "ಆನ್", "ತಾನ್", "ಅದು", "ಇದು", "ಉದು", "ಆವುದು", "ಏನ್", "ಎಲ್ಲದು", "ಪೆಱತು"]


@lru_cache(maxsize=1)
def _pronoun_index() -> dict[str, list[tuple]]:
    from .nama import CASES, decline, personal_stem
    idx: dict[str, list[tuple]] = {}
    def put(form, lemma, feats, p):
        idx.setdefault(_canon(form), []).append((lemma, feats, p))
    for base in PRONOUN_BASES:
        for num in ("sg", "pl"):
            for case in CASES:
                if case == "voc":
                    continue
                for p in decline(base, case, num, "n"):
                    put(p.result(), base, {"case": CASE_LABEL[case], "number": num}, p)
        if base in ("ಅದು", "ಇದು", "ಉದು", "ಆವುದು", "ಎಲ್ಲದು", "ಪೆಱತು"):
            for g in ("m", "f"):
                for st in personal_stem(base, g):
                    for case in CASES:
                        if case == "voc":
                            continue
                        for p in decline(st, case, "sg", g):
                            put(p.result(), base, {"case": CASE_LABEL[case], "number": "sg",
                                                   "gender": {"m": "masc.", "f": "fem."}[g]}, p)
            for st in personal_stem(base, "m", "pl"):
                for case in CASES:
                    if case in ("voc",):
                        continue
                    for p in decline(st[:-1] if st.endswith("ರ್") else st, case, "pl", "m") if False else []:
                        pass
                put(st, base, {"case": "nominative", "number": "pl", "gender": "human"}, None)
    return idx


# ---------------------------------------------------------------- verbs
VERB_LABELS = [
    ("past", 3, "sg", "m"), ("past", 3, "sg", "f"), ("past", 3, "sg", "n"), ("past", 3, "pl", "m"),
    ("past", 3, "pl", "n"), ("past", 2, "sg", None), ("past", 2, "pl", None), ("past", 1, "sg", None),
    ("past", 1, "pl", None),
    ("present", 3, "sg", "m"), ("present", 3, "sg", "f"), ("present", 3, "sg", "n"), ("present", 3, "pl", "m"),
    ("present", 3, "pl", "n"), ("present", 2, "sg", None), ("present", 2, "pl", None), ("present", 1, "sg", None),
    ("present", 1, "pl", None),
    ("future", 3, "sg", "m"), ("future", 3, "sg", "f"), ("future", 3, "sg", "n"), ("future", 3, "pl", "m"),
    ("future", 3, "pl", "n"), ("future", 2, "sg", None), ("future", 2, "pl", None), ("future", 1, "sg", None),
    ("future", 1, "pl", None),
    ("negative", 3, "sg", "m"), ("negative", 3, "sg", "f"), ("negative", 3, "sg", "n"), ("negative", 3, "pl", "m"),
    ("negative", 3, "pl", "n"), ("negative", 2, "sg", None), ("negative", 2, "pl", None),
    ("negative", 1, "sg", None), ("negative", 1, "pl", None),
    ("aorist", 3, "sg", "m"), ("vidhi", 2, "sg", None), ("vidhi", 2, "pl", None), ("vidhi", 3, "sg", None),
    ("vidhi", 1, "pl", None), ("infinitive", 3, "sg", None), ("prohibitive", 2, "sg", None),
    ("gerund_past", 3, "sg", None), ("gerund_present", 3, "sg", None), ("conditional", 3, "sg", None),
    ("sati", 3, "sg", None), ("participle_past", 3, "sg", None), ("participle_future", 3, "sg", None),
    ("action_noun", 3, "sg", None), ("neg_participle", 3, "sg", None),
]
FORM_NAMES = {"past": "past", "present": "present", "future": "future/present", "negative": "negative",
              "aorist": "aorist -guṃ/-kuṃ", "vidhi": "imperative/optative", "infinitive": "infinitive",
              "prohibitive": "prohibitive", "gerund_past": "past gerund", "gerund_present": "present gerund",
              "conditional": "conditional -oḍe", "sati": "sati-saptamī (when …)",
              "participle_past": "past relative participle", "participle_future": "future relative participle",
              "action_noun": "verbal noun -udu", "neg_participle": "negative participle -ade"}


def _verb_feats(label) -> dict:
    form, person, number, gender = label
    f = {"form": FORM_NAMES[form]}
    if form in ("past", "present", "future", "negative", "vidhi"):
        f["person"] = f"{person}{'' if form != 'vidhi' or True else ''}"
        f["number"] = number
        if gender:
            f["gender"] = {"m": "masc./human", "f": "fem.", "n": "neut."}[gender]
    return f


def _conjugate_label(root, label):
    from .akhyata import conjugate
    form, person, number, gender = label
    try:
        return conjugate(root, form, person, number, gender)
    except Exception:
        return []


@lru_cache(maxsize=1)
def _root_meanings() -> dict[str, str]:
    out = {}
    for r in dhatupatha():
        if r.get("root"):
            out.setdefault(V.normalize(r["root"]), r.get("meaning_en") or r.get("meaning_kn") or "")
    for extra, m in (("ಬರ್", "to come"), ("ತರ್", "to bring"), ("ಪೋಗು", "to go"), ("ಆಗು", "to become"),
                     ("ಕೊಳ್", "to take"), ("ಉಳ್", "to be, exist"), ("ಎನ್", "to say"), ("ಇರ್", "to be, stay"),
                     ("ಕಾಣ್", "to see"), ("ಕೆಯ್", "to do"), ("ಗೆಯ್", "to do"), ("ನುಡಿ", "to speak"),
                     ("ಪೇೞ್", "to tell"), ("ನೋಡು", "to look"), ("ಮಾಡು", "to make"), ("ಕೇಳ್", "to hear"),
                     ("ಈ", "to give"), ("ಕುಡು", "to give"), ("ಅಱಿ", "to know"), ("ಪಡೆ", "to obtain"),
                     ("ನಿಲ್", "to stand"), ("ಸಾ", "to die"), ("ಕೊಲ್", "to kill"), ("ಉಣ್", "to eat"),
                     ("ಬಿಡು", "to leave"), ("ತಾಗು", "to strike"), ("ಏಱು", "to climb"), ("ಪುಗು", "to enter")):
        out.setdefault(extra, m)
    return out


@lru_cache(maxsize=1)
def _verb_index() -> dict[str, list[tuple]]:
    """canonical form → [(root, label)] for every root of the Dhātupāṭha (built once, ~3 s)."""
    idx: dict[str, list[tuple]] = {}
    for root in _root_meanings():
        try:
            V.to_varnas(root)
        except ValueError:
            continue
        for label in VERB_LABELS:
            for p in _conjugate_label(root, label):
                r = p.result()
                if " " in r or not r:
                    continue
                lst = idx.setdefault(_canon(r), [])
                if (root, label) not in lst:
                    lst.append((root, label))
    return idx


# ---------------------------------------------------------------- learned ending templates
NOUN_SAMPLES = [("ಅರಸ", "m", "kannada"), ("ಮರ", "n", "kannada"), ("ಕುಲ", "n", "sanskrit"),
                ("ದೇವ", "m", "sanskrit"), ("ಬಳ್ಳಿ", "n", "kannada"), ("ದೇವಿ", "f", "sanskrit"),
                ("ಕವಿ", "m", "sanskrit"), ("ಮಾತು", "n", "kannada"), ("ಗುರು", "m", "sanskrit"),
                ("ಮಡು", "n", "kannada"), ("ತೊಱೆ", "n", "kannada"), ("ಕಣ್", "n", "kannada"),
                ("ಬೆರಲ್", "n", "kannada"), ("ಊರ್", "n", "kannada"), ("ಕಾಂತೆ", "f", "sanskrit"),
                ("ಅಕ್ಕ", "f", "kannada"), ("ಒಳ್ಳಿತು", "n", "kannada")]
VERB_SAMPLES = ["ಮಾಡು", "ಕಟ್ಟು", "ನಡೆ", "ಪಿಡಿ", "ಕೇಳ್", "ಗೆಲ್", "ಸೂಚಿಸು", "ತಾಗು", "ಕೂರ್", "ಉಣ್", "ಆಳ್",
                "ಮೆಚ್ಚು", "ಅಱಿ", "ಪೊಗೞ್", "ತೋಱು"]


def _lcp(a, b):
    k = 0
    while k < min(len(a), len(b)) and a[k] == b[k]:
        k += 1
    return k


@lru_cache(maxsize=1)
def _noun_templates() -> dict[tuple, list[tuple]]:
    from .nama import CASES, decline
    tpl: dict[tuple, list[tuple]] = {}
    for stem, g, origin in NOUN_SAMPLES:
        sv = V.to_varnas(stem)
        for num in ("sg", "pl"):
            for case in CASES:
                for p in decline(stem, case, num, g, origin):
                    r = p.result()
                    if " " in r:
                        continue
                    fv = V.to_varnas(_canon(r))
                    k = min(_lcp(sv, fv), len(sv) - 1 if len(sv) > 1 else 0)
                    key = tuple(fv[k:])
                    val = (tuple(sv[k:]), case, num, g, origin)
                    if val not in tpl.setdefault(key, []):
                        tpl[key].append(val)
    return tpl


@lru_cache(maxsize=1)
def _verb_templates() -> dict[tuple, list[tuple]]:
    tpl: dict[tuple, list[tuple]] = {}
    for root in VERB_SAMPLES:
        rv = V.to_varnas(root)
        for label in VERB_LABELS:
            for p in _conjugate_label(root, label):
                r = p.result()
                if " " in r or not r:
                    continue
                fv = V.to_varnas(_canon(r))
                k = min(_lcp(rv, fv), len(rv) - 1)
                key = tuple(fv[k:])
                val = (tuple(rv[k:]), label)
                if val not in tpl.setdefault(key, []):
                    tpl[key].append(val)
    return tpl


# verb forms distinctive enough to posit an unattested root
INFERABLE_VERB_FORMS = {"past", "present", "future", "conditional", "gerund_present", "participle_past",
                        "aorist"}


def _match_templates(w: list[str], templates) -> list[tuple]:
    out = []
    n = len(w)
    for L in range(1, min(n, 14)):
        key = tuple(w[n - L:])
        if key in templates:
            for val in templates[key]:
                out.append((w[: n - L], val))
    return out


# ---------------------------------------------------------------- lexical knowledge
@lru_cache(maxsize=1)
def _attested_stems() -> set[str]:
    """Stems that occur as inputs in Kēśirāja's examples or in the Prayōgasāra."""
    out = set()
    for r in load().records:
        for e in r.get("examples") or []:
            for x in (e.get("input") or [])[:1]:
                if isinstance(x, str) and " " not in x:
                    out.add(_canon(x).rstrip("ಂ"))
    for e in prayogasara():
        out.add(_canon(e["word"]).rstrip("ಂ"))
    return out


# ---------------------------------------------------------------- analysis
def _verify_noun(stem: str, case, num, g, origin, target: str) -> Prakriya | None:
    from .nama import decline
    for o in (origin, None):
        try:
            ps = decline(stem, case, num, g, o)
        except Exception:
            continue
        for p in ps:
            if _canon(p.result()) == target:
                return p
    return None


def _analyze_core(word: str) -> list[Analysis]:
    w = _canon(word)
    try:
        wv = V.to_varnas(w)
    except ValueError:
        return []
    res: list[Analysis] = []
    seen = set()

    def add(a: Analysis):
        key = (a.lemma, a.pos, tuple(sorted(a.features.items())))
        if key in seen:
            return
        seen.add(key)
        res.append(a)

    # avyaya
    if w in avyayas():
        add(Analysis(word, w, "avyaya", {"meaning": avyayas()[w]}, "lexicon", score=3))
    # pronouns
    for lemma, feats, p in _pronoun_index().get(w, []):
        add(Analysis(word, lemma, "pronoun", dict(feats), "lexicon", p, score=3))
    # known verbs
    meanings = _root_meanings()
    for root, label in _verb_index().get(w, []):
        ps = [p for p in _conjugate_label(root, label) if _canon(p.result()) == w]
        f = _verb_feats(label)
        f["meaning"] = meanings.get(root, "")
        add(Analysis(word, root, "verb", f, "lexicon", ps[0] if ps else None, score=3))
    # nouns via templates
    attested = _attested_stems()
    for prefix, (removed, case, num, g, origin) in _match_templates(wv, _noun_templates()):
        stem_v = list(prefix) + list(removed)
        if len([x for x in stem_v if V.is_vowel(x)]) < 1:
            continue
        stem = V.from_varnas(stem_v)
        p = _verify_noun(stem, case, num, g, origin, w)
        if p is None:
            continue
        ev = "lexicon" if _canon(stem) in attested or stem in meanings else "inferred"
        o = lexicon.guess_origin(stem)
        feats = {"case": CASE_LABEL[case], "number": num,
                 "gender": {"m": "masc.", "f": "fem.", "n": "neut."}[g], "type": o}
        sc = 2 if ev == "lexicon" else (0.6 if _canon(stem).rstrip("ಂ") == w.rstrip("ಂ") else 1)
        add(Analysis(word, stem, "noun", feats, ev, p, score=sc))
    # unknown verbs via templates
    for prefix, (removed, label) in _match_templates(wv, _verb_templates()):
        root_v = list(prefix) + list(removed)
        if not any(V.is_vowel(x) for x in root_v):
            continue
        root = V.from_varnas(root_v)
        if root in meanings or label[0] not in INFERABLE_VERB_FORMS:
            continue
        ps = [p for p in _conjugate_label(root, label) if _canon(p.result()) == w]
        if ps:
            f = _verb_feats(label)
            add(Analysis(word, root, "verb", f, "inferred", ps[0],
                         notes=["root not in Kēśirāja's Dhātupāṭha"], score=0.5))
    return res


CLITICS = [("ುಂ", "-uṃ 'and/also' (122)"), ("ಉಂ", "-uṃ 'and/also' (122)"), ("ೆ", "-e emphatic (56)"),
           ("ೇ", "-ē emphatic/interrogative"), ("ೋ", "-ō doubt/admiration (56–57)"),
           ("ಂ", "-aṃ 'and' after -oḷ (122)")]


def _strip_clitic(w: str) -> list[tuple[str, str]]:
    """Possible (base, clitic) splits, undoing the sandhi of the clitic."""
    out = []
    for cl, name in CLITICS:
        if not w.endswith(cl) or len(w) <= len(cl) + 1:
            continue
        base = w[: -len(cl)]
        cands = {base}
        if cl in ("ುಂ", "ೆ", "ೇ", "ೋ"):
            # base + vowel sign: the consonant before belongs to the base
            vs = V.to_varnas(w)[:-1] if cl != "ುಂ" else V.to_varnas(w)[:-2]
            if vs:
                last = vs[-1]
                bv = list(vs)
                cands = {V.from_varnas(bv)}
                if last in ("ನ್", "ಮ್"):           # ಅವನುಂ < ಅವಂ ; ಮರಮುಂ < ಮರಂ
                    cands.add(V.from_varnas(bv[:-1] + [V.ANUSVARA]))
                if last in ("ಯ್", "ವ್"):           # ಕವಿಯುಂ < ಕವಿ ; ಗುರುವುಂ < ಗುರು
                    cands.add(V.from_varnas(bv[:-1]))
                if len(bv) > 1 and bv[-1] == bv[-2]:   # ಕಣ್ಣುಂ < ಕಣ್
                    cands.add(V.from_varnas(bv[:-1]))
                if V.is_consonant(last):            # ಮಾಡಿದೆ < ಮಾಡಿದ (+e)? keep vowel-final options
                    cands.add(V.from_varnas(bv + ["ಉ"]))
        if cl == "ಂ" and w.endswith("ೊಳಂ"):
            cands = {w[:-1] + "್"}
        for c in cands:
            if c and c != w:
                out.append((c, name))
    return out


def _prune(res: list[Analysis]) -> list[Analysis]:
    """Drop vacuous readings (word = inferred bare root / its own vocative) when anything
    better exists, and merge readings that differ only in gender."""
    def vacuous(a):
        if a.evidence != "inferred":
            return False
        if a.pos == "verb" and a.features.get("form") == "imperative/optative" and _canon(a.lemma) == _canon(a.word):
            return True
        if a.pos == "noun" and a.features.get("case") == "vocative":
            return True
        if a.pos == "noun" and a.features.get("case") == "vocative":
            a.score = 0.4
        return False
    good = [a for a in res if not vacuous(a)]
    res = good or res
    merged: dict[tuple, Analysis] = {}
    for a in res:
        key = (a.lemma, a.pos, a.features.get("case"), a.features.get("number"), a.features.get("form"),
               a.features.get("person"), a.features.get("clitic"))
        if key in merged and a.pos == "noun":
            g0, g1 = merged[key].features.get("gender", ""), a.features.get("gender", "")
            if g1 and g1 not in g0:
                merged[key].features["gender"] = f"{g0}/{g1}" if g0 else g1
            continue
        merged.setdefault(key, a)
    return list(merged.values())


@lru_cache(maxsize=20000)
def _analyze_cached(word: str) -> tuple:
    res = _prune(_analyze_core(word))
    if not res:
        for base, clitic in _strip_clitic(_canon(word)):
            for a in _analyze_core(base):
                b = Analysis(word, a.lemma, a.pos, dict(a.features, clitic=clitic), a.evidence, a.prakriya,
                             notes=a.notes + [f"clitic: {clitic}; base form {base}"], score=a.score - 0.2)
                res.append(b)
        res = _prune(res)
    res.sort(key=lambda a: -a.score)
    return tuple(res)


def analyze(word: str, split: bool = True) -> list[Analysis]:
    """All analyses of a single word (no spaces)."""
    word = V.normalize(word).strip("।॥|.,;:!?\"'()[]{}-–—0123456789೦೧೨೩೪೫೬೭೮೯ ")
    if not word:
        return []
    try:
        V.to_varnas(word)
    except ValueError:
        return []
    res = list(_analyze_cached(word))
    if split and (not res or max(a.score for a in res) < 2) and len(V.to_varnas(word)) > 5:
        parts = segment(word)
        if parts:
            avg = sum(p.score for p in parts) / len(parts)
            res.append(Analysis(word, " + ".join(p.lemma for p in parts), "phrase/compound",
                                {"type": f"saṃhitā split into {len(parts)}"},
                                "lexicon" if all(p.evidence == "lexicon" for p in parts) else "inferred",
                                parts=parts, score=avg + 0.3))
        res = sorted(res, key=lambda a: -a.score)
    return res


# ---------------------------------------------------------------- sandhi / compound splitting
def split_analyze(word: str, max_parts: int = 3) -> list[Analysis]:
    """Analyse a token that fuses several words (saṃhitā) or a compound: try every split
    point, undoing the common junction changes, and require every part to be analysable."""
    from .samasa import check_arisamasa
    wv = V.to_varnas(_canon(word))
    best: list[Analysis] = []
    n = len(wv)
    for k in range(2, n - 1):
        left_v, right_v = wv[:k], wv[k:]
        if not any(V.is_vowel(x) for x in left_v) or not any(V.is_vowel(x) for x in right_v):
            continue
        lefts = {V.from_varnas(left_v)}
        rights = {V.from_varnas(right_v)}
        # undo sandhi: right starts with a vowel after a consonant: left lost a vowel (52)
        if V.is_consonant(left_v[-1]) and V.is_vowel(right_v[0]):
            for vow in ("ಉ", "ಅ", "ಇ", "ಎ"):
                lefts.add(V.from_varnas(left_v + [vow]))
            if left_v[-1] == "ಮ್":
                lefts.add(V.from_varnas(left_v[:-1] + [V.ANUSVARA]))
            if left_v[-1] == "ನ್":
                lefts.add(V.from_varnas(left_v[:-1] + [V.ANUSVARA]))
        if right_v[0] in ("ಯ್", "ವ್") and len(right_v) > 1 and V.is_vowel(right_v[1]):
            rights.add(V.from_varnas(right_v[1:]))          # glide insertion (53/55)
        if right_v[0] in ("ಗ್", "ದ್", "ಬ್", "ವ್", "ಜ್"):     # compound voicing (65/67)
            for orig in {"ಗ್": ("ಕ್",), "ದ್": ("ತ್",), "ಬ್": ("ಪ್",), "ವ್": ("ಪ್", "ಬ್", "ಮ್"), "ಜ್": ("ಸ್",)}[right_v[0]]:
                rights.add(V.from_varnas([orig] + right_v[1:]))
        la = [a for l in lefts for a in _analyze_cached(l)]
        if not la:
            continue
        ra = []
        for r in rights:
            ra.extend(_analyze_cached(r))
            if not ra and max_parts > 2 and len(r) > 3:
                ra.extend(split_analyze(r, max_parts - 1))
        if not ra:
            continue
        la.sort(key=lambda a: -a.score)
        ra.sort(key=lambda a: -a.score)
        a0, b0 = la[0], ra[0]
        comp = Analysis(word, f"{a0.lemma} + {b0.lemma}", "phrase/compound",
                        {"type": "sandhi split"}, "inferred" if "inferred" in (a0.evidence, b0.evidence) else "lexicon",
                        parts=[a0, b0], score=min(a0.score, b0.score) - 0.5 - 0.1 * k / n)
        bad = check_arisamasa(a0.lemma, b0.lemma) if a0.pos == "noun" and b0.pos == "noun" else None
        if bad:
            comp.notes.append(f"if a compound: {bad} (sūtra 174)")
        best.append(comp)
    best.sort(key=lambda a: -a.score)
    return best[:3]


# ---------------------------------------------------------------- running text
TOKEN_RE = re.compile(r"[ಀ-೿‌‍]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(V.normalize(text))


@dataclass
class TokenReport:
    token: str
    analyses: list[Analysis]

    @property
    def status(self) -> str:
        if not self.analyses:
            return "unanalysed"
        a = self.analyses[0]
        if a.evidence == "lexicon":
            return "ok"
        return "inferred"


def analyze_text(text: str) -> list[TokenReport]:
    out = []
    for tok in tokenize(text):
        out.append(TokenReport(tok, analyze(tok)))
    return out


# ---------------------------------------------------------------- DP segmentation of saṃhitā runs
def _segment_candidates(seg_v: list[str], first: bool, last: bool) -> list[str]:
    """Surface segment → underlying word candidates (undoing vowel elision, glides,
    bindu → m/n, compound voicing)."""
    c = [seg_v]
    if not last and seg_v and V.is_consonant(seg_v[-1]):
        for vow in ("ಉ", "ಅ", "ಇ", "ಎ"):
            c.append(seg_v + [vow])                       # 52: final vowel elided before a vowel
        if seg_v[-1] in ("ಮ್", "ನ್"):
            c.append(seg_v[:-1] + [V.ANUSVARA])            # 104: bindu realised as m/n
    if not first and len(seg_v) > 1 and seg_v[0] in ("ಯ್", "ವ್") and V.is_vowel(seg_v[1]):
        c.append(seg_v[1:])                               # 53/55 glide
    if not first and seg_v and seg_v[0] in ("ಗ್", "ದ್", "ಬ್", "ವ್", "ಜ್"):
        for orig in {"ಗ್": ("ಕ್",), "ದ್": ("ತ್",), "ಬ್": ("ಪ್",), "ವ್": ("ಪ್", "ಬ್", "ಮ್"), "ಜ್": ("ಸ್",)}[seg_v[0]]:
            c.append([orig] + seg_v[1:])                  # 65/67 compound voicing
    return [V.from_varnas(x) for x in c if x]


def _seg_value(a: Analysis, seg: str) -> float:
    v = a.score
    f = a.features
    if f.get("form") == "imperative/optative" or f.get("case") == "vocative":
        v -= 1.5                     # bare roots / bare stems are weak evidence inside a run
    nv = len(V.to_varnas(seg))
    if nv < 4 and a.pos not in ("pronoun", "avyaya"):
        v -= 1.0
    return v


def _segment_score(seg: str, last: bool) -> tuple[float, Analysis | None]:
    best, bv = None, -1e9
    for a in _analyze_cached(seg):
        if a.evidence != "lexicon" and not last:
            continue
        v = _seg_value(a, seg)
        if v > bv:
            best, bv = a, v
    if best is None and not last and lexicon.guess_origin(seg) == lexicon.SANSKRIT and seg.endswith(("ಅ",)) is False:
        pass
    # bare stems inside a run: compound members (Sanskrit or Kannada)
    if best is None and not last:
        if _canon(seg) in _attested_stems() or _canon(seg + "ಂ").rstrip("ಂ") in _attested_stems():
            best = Analysis(seg, seg, "stem", {"type": "compound member"}, "lexicon", score=1.5)
    if best is None:
        return -1e9, None
    return (bv if bv > -1e9 else best.score), best


def segment(word: str, max_len: int = 18) -> list[Analysis] | None:
    """Best segmentation of a fused token into analysable words (Viterbi over split points)."""
    wv = V.to_varnas(_canon(word))
    n = len(wv)
    best: dict[int, tuple[float, list]] = {0: (0.0, [])}
    for j in range(1, n + 1):
        cands = []
        for i in range(max(0, j - max_len), j):
            if i not in best or j - i < 2:
                continue
            seg = wv[i:j]
            if not any(V.is_vowel(x) for x in seg):
                continue
            for s in _segment_candidates(seg, i == 0, j == n):
                sc, a = _segment_score(s, j == n)
                if a is not None:
                    cands.append((best[i][0] + sc - 1.0, best[i][1] + [a]))
        if cands:
            best[j] = max(cands, key=lambda x: x[0])
    if n not in best or len(best[n][1]) < 2:
        return None
    return best[n][1]
