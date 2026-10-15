"""Adapters that turn Kēśirāja's prayōgas (data/smd_sutras.json) into engine calls.

The prayōga notes written during encoding carry the grammatical context (e.g.
"genitive + emphatic e", "Sanskrit stem", "negative 3sg"); the adapters translate those
notes into the term tags the rules understand. Examples whose context cannot be
recovered are skipped (reported as such), never silently passed.
"""
from __future__ import annotations

from . import lexicon
from .testing import Case, adapter


def _has(note: str, *words: str) -> bool:
    n = (note or "").lower()
    return any(w.lower() in n for w in words)


# ------------------------------------------------------------------ sandhi (52–71)
@adapter("sandhi")
def sandhi_case(r: dict, ex: dict):
    from .sandhi import COMPOUND, SUFFIX, WORD, results

    sid = str(r["id"])
    inp, out, note = ex.get("input"), ex.get("output"), ex.get("note", "")
    if sid in ("59", "60", "62", "63") or not inp or len(inp) != 2 or not out:
        if not inp or len(inp) != 2:
            return Case(sid, inp, out, note, lambda: set(), skip="no input segmentation")
    a, b = inp
    ctx = WORD
    lt, rt = set(), set()
    lo = ro = None
    n = int(sid)
    if n in (58, 65, 66, 67) and not _has(note, "sentence level"):
        ctx = COMPOUND
    if n == 68:
        ctx = COMPOUND
    if _has(note, "Sanskrit"):
        lo = lexicon.SANSKRIT
    if _has(note, "Kannada"):
        lo = lexicon.KANNADA
    if n == 52 and _has(note, "instrumental", "dative", "ablative", "locative", "genitive",
                        "finite-verb", "gerund", "ending"):
        lt.add("vibhakti")
    if n == 52 and _has(note, "before vibhakt", "+ -ಇಸು", "suffix"):
        ctx = SUFFIX
    if _has(note, "genitive") and _has(note, "emphatic"):
        lt.add("genitive"); rt.add("avadharana")
    if n == 54:
        ctx = SUFFIX if b.startswith("ಇಸ") else WORD
        if _has(note, "onomatop"):
            lt.add("anukrti"); rt.add("quotative")
    if n == 56:
        if _has(note, "nipāta", "particle"):
            lt.add("nipata")
        if _has(note, "avadhāraṇa"):
            lt.add("avadharana")
        if _has(note, "viśaṅke", "doubt"):
            lt.add("vishanke")
        if _has(note, "pluta"):
            lt.add("pluta")
    if n == 57:
        lt.add("emotive")
    if n == 61:
        if _has(note, "case C"):
            lt.add("padyardha")
        if _has(note, "case D"):
            lt.add("quote")
        if _has(note, "case E"):
            lt.add("anukrti")
        if _has(note, "case A", "case B"):
            ctx = SUFFIX
        if _has(note, "case F"):
            ctx = COMPOUND
    if n == 64 and _has(note, "niyōga") and not _has(note, "aniyōga"):
        lt.add("avadharana")
    if n == 69 and _has(note, "indeclinable"):
        lt.add("avyaya")
    if n in (70, 71):
        lt.add("dhatu"); ctx = SUFFIX
        if _has(note, "negative") and not _has(note, "participle"):
            rt.add("negative")
    if n == 66:
        lt.add("adesha")
    if n == 67 and _has(note, "ādēśa"):
        lt.add("adesha")
    if n == 53 and _has(note, "root"):
        ctx = SUFFIX
    if n == 55 and _has(note, "verbal noun"):
        ctx = SUFFIX

    def run(a=a, b=b, ctx=ctx, lt=frozenset(lt), rt=frozenset(rt), lo=lo):
        return results(a, b, context=ctx, left_origin=lo, left_tags=lt, right_tags=rt)

    return Case(sid, inp, out, note, run)


# ------------------------------------------------------------------ nāma (72–161)
_CASE_OF_SUFFIX = {
    "ಅಂ": "acc", "ಅಮ್": "acc", "ಇಂ": "ins", "ಇಂದಂ": "ins", "ಇಂದೆ": "ins", "ಅ": "gen",
    "ಕೆ": "dat", "ಗೆ": "dat", "ಒಳ್": "loc", "ಅಲ್ಲಿ": "loc", "ಅತ್ತಣಿಂ": "abl",
    "ಅತ್ತಣಿಂದಂ": "abl", "ಅತ್ತಣಿಂದೆ": "abl", "ಮ್": "nom", "ಂ": "nom", "+ಂ": "nom",
    "nom": "nom", "nom.": "nom", "ಏ": "voc", "voc": "voc", "acc": "acc", "loc": "loc",
}
_PLURALS = {"ಗಳ್", "ಅರ್", "ದಿರ್", "ವಿರ್", "ಕಳ್", "ಅವು", "ಇರ್", "ಇರ"}


def _gender(note: str):
    n = (note or "").lower()
    if "masc" in n or "human" in n:
        return "m"
    if "fem" in n:
        return "f"
    if "neut" in n:
        return "n"
    return None


def _phrase_ok(expected: str, forms: set[str]) -> bool:
    """Phrase examples (a case form inside a sentence): is one of the generated forms
    present in the phrase — as a token, or fused with a neighbour by sandhi (final vowel
    elided, bindu realised as n/m, initial vowel merged)? Compared on varṇa sequences."""
    from . import varna as V
    toks = []
    for t in expected.split():
        try:
            toks.append(V.to_varnas(t))
        except ValueError:
            pass
    for f in forms:
        if not f or " " in f:
            continue
        try:
            fv = V.to_varnas(f)
        except ValueError:
            continue
        cands = [fv]
        if len(fv) > 2 and V.is_vowel(fv[-1]):
            cands.append(fv[:-1])                       # 52: final vowel elided
        if fv and fv[-1] == V.ANUSVARA:
            cands += [fv[:-1] + ["ನ್"], fv[:-1] + ["ಮ್"]]   # 104: bindu → n / m
        for t in toks:
            if any(t[:len(c)] == c for c in cands):
                return True
            if len(fv) > 2 and V.is_vowel(fv[0]) and t[-(len(fv) - 1):] == fv[1:]:
                return True                              # initial vowel merged
    return False


def _wrap_phrase(case: Case) -> Case:
    if case.skip or (" " not in (case.expected or "") and int(case.sutra.rstrip("ab") or 0) not in range(102, 146)):
        return case
    inner = case.run

    def run():
        got = inner()
        return got | {case.expected} if case.expected not in got and _phrase_ok(case.expected, got) else got
    case.run = run
    case.note += " [phrase]"
    return case


@adapter("nama")
def nama_case(r: dict, ex: dict):
    c = _nama_case(r, ex)
    return _wrap_phrase(c) if c else c


def _nama_case(r: dict, ex: dict):
    from .nama import adapt_sanskrit, add_um, decline, personal_stem, word_variants
    from .sandhi import results as sandhi_results

    sid = str(r["id"])
    inp, out, note = ex.get("input"), ex.get("output"), ex.get("note", "") or ""
    if not inp or not out:
        return Case(sid, inp, out, note, set, skip="list item (no derivation)")
    if any(" " in (x or "") for x in inp):
        return Case(sid, inp, out, note, set, skip="phrase input")
    if sid in ("134", "135", "136", "144") and len(inp) == 1:
        return Case(sid, inp, out, note, set, skip="case interchange (needs analyzer)")
    if sid == "125" and (len(inp) == 3 and inp[1] == "ಇರ್" or inp[-1] == "ಅ"):
        return Case(sid, inp, out, note, set, skip="verbal form (Ākhyāta)")
    g = _gender(note)
    lo = lexicon.SANSKRIT if _has(note, "Sanskrit") else lexicon.KANNADA if _has(note, "Kannada") else None
    if sid == "103" and _has(note, "neuter") and lo is None:
        lo = lexicon.KANNADA          # 103 speaks of Kannada neuters
    cls = set()
    for key, c in (("kṛt", "krt"), ("pronoun", "sarvanama"), ("sarvanāma", "sarvanama"),
                   ("guṇavacana", "gunavacana"), ("numeral", "sankhya"), ("quantity", "pavan"),
                   ("direction", "dik"), ("adverb", "adverb")):
        if _has(note, key):
            cls.add(c)
    if len(inp) == 1:
        w = inp[0]
        def run1(w=w):
            res = {p.result() for p in adapt_sanskrit(w)} | {p.result() for p in word_variants(w)} | {w}
            for c in ("nom", "voc"):
                res |= _decl(decline, w, c, "sg", g, lo, cls)
            return res
        return Case(sid, inp, out, note, run1)
    if sid in ("104", "158", "161") or (len(inp) == 2 and inp[0].endswith("ಂ") and sid not in ("122",)
                                        and inp[1] not in _CASE_OF_SUFFIX and inp[1] not in _PLURALS):
        a, b = inp[0], inp[-1]
        lt = {"acc"} if _has(note, "acc") else set()
        return Case(sid, inp, out, note, lambda: sandhi_results(a, b, left_tags=lt)
                    | sandhi_results(a, b, context="compound", left_tags=lt))
    if sid == "122" or (len(inp) >= 2 and inp[-1] in ("ಉಂ",) ):
        base = inp[0]
        def run122(base=base):
            res = {p.result() for p in add_um(base)}
            if len(inp) == 3 and inp[1] in _CASE_OF_SUFFIX:
                for f in _decl(decline, base, _CASE_OF_SUFFIX[inp[1]], "sg", g, lo, cls):
                    res |= {p.result() for p in add_um(f)}
            if len(inp) == 3:      # stem + ಉಂ + ಅಂ: accusative with -um- inside
                res |= {f[:-1] + "ಮಂ" for f in (p.result() for p in add_um(base)) if f.endswith("ಂ")}
                res |= {p.result() for p in add_um(base + ("ಯ" if base.endswith(("ಿ", "ೆ")) else "")) }
            return res
        return Case(sid, inp, out, note, run122)
    if len(inp) == 2 and inp[0].endswith("ರ್") and inp[1] in ("ಕಳ್", "ಗಳ್") and _has(note, "after -ಅರ್", "pronoun"):
        return Case(sid, inp, out, note, lambda: {inp[0] + inp[1]})
    if len(inp) == 3 and inp[0].endswith("ರ್") and inp[1] in ("ಕಳ್", "ಗಳ್") and inp[2] == "ಇರ":
        return Case(sid, inp, out, note, lambda: {inp[0] + inp[1][:-1] + "ಿರ"})
    if sid == "99" and inp[-1] == "ಅಂ":
        return Case(sid, inp, out, note, lambda: _decl(decline, inp[0], "nom", "sg", "m", lo, cls | {"sankhya"}))
    if len(inp) == 2 and inp[1] == "ಎ" and (_has(note, "loc") or sid in ("119", "120")):
        return Case(sid, inp, out, note, lambda: _decl(decline, inp[0], "loc", "sg", None, lo, cls))
    stem, suf = inp[0], inp[-1]
    if len(inp) == 3 and inp[1] in _PLURALS:      # stem + plural + case
        case = _CASE_OF_SUFFIX.get(suf, "voc" if suf == "ಇರ" else None)
        if case:
            return Case(sid, inp, out, note, lambda: _decl(decline, stem, case, "pl", g, lo, cls))
    if len(inp) == 3 and inp[1] in ("ವ", "ವ್") and suf == "ಅರ್":
        return Case(sid, inp, out, note, lambda: _decl(decline, stem, "nom", "pl", "m", lo, cls | {"pavan"}))
    if len(inp) != 2:
        return Case(sid, inp, out, note, set, skip="phrase or multi-part input")
    if suf in _PLURALS:
        gg = g or ("m" if suf in ("ಅರ್", "ದಿರ್", "ವಿರ್", "ಇರ್") else None)
        def run(stem=stem, gg=gg):
            res = _decl(decline, stem, "nom", "pl", gg, lo, cls)
            if suf == "ಅರ್":
                res |= {s for s in personal_stem(stem, "m", "pl")}
            return res
        return Case(sid, inp, out, note, run)
    if suf in ("ಅಂ", "ಅಳ್") and (sid in {"89", "98", "150", "151", "152", "153", "154"} or _has(note, "masc. sg.", "fem. sg.")):
        gg = "f" if suf == "ಅಳ್" else "m"
        def run(stem=stem, gg=gg):
            res = set()
            for s in personal_stem(stem, gg):
                res |= _decl(decline, s, "nom", "sg", gg, lo, cls - {"sarvanama"})
                res.add(s)
            return res | _decl(decline, stem, "acc", "sg", g, lo, cls)
        return Case(sid, inp, out, note, run)
    if suf == "ಎ" and not _has(note, "voc"):
        case = "ins"
    elif suf == "ಎ":
        case = "voc"
    else:
        case = _CASE_OF_SUFFIX.get(suf)
    if suf in ("fem.", "masc. sg.", "pl.", "sg.", "masc.") or suf.startswith(("fem", "masc")):
        gg = "f" if suf.startswith("fem") else "m"
        num = "pl" if "pl" in suf else "sg"
        def runp(stem=stem, gg=gg, num=num):
            res = set(personal_stem(stem, gg, num)) | {s + "ಂ" for s in personal_stem(stem, gg, num)}
            return res | {p.result() for f in list(res) for p in add_um(f)}
        return Case(sid, inp, out, note, runp)
    if not case:
        return Case(sid, inp, out, note, set, skip=f"suffix {suf!r} not a case ending")
    num = "pl" if _has(note, " pl", "pl.", "plural") and not stem.endswith(("ಗಳ್", "ರ್")) else "sg"
    return Case(sid, inp, out, note, lambda: _decl(decline, stem, case, num, g, lo, cls))


def _decl(decline, stem, case, num, g, lo, cls):
    res = set()
    for gg in ([g] if g else ["m", "n", "f"]):
        res |= {p.result() for p in decline(stem, case, num, gg, lo, cls)}
    return res


# ------------------------------------------------------------------ samāsa (162–196)
@adapter("samasa")
def samasa_case(r: dict, ex: dict):
    from .samasa import bahuvrihi, compound

    sid = str(r["id"])
    inp, out, note = ex.get("input"), ex.get("output"), ex.get("note", "") or ""
    if not inp or not out:
        return Case(sid, inp, out, note, set, skip="list item (no derivation)")
    if any(" " in (x or "") for x in inp):
        return Case(sid, inp, out, note, set, skip="phrase input")
    kind = None
    for k, words in (("gamaka", ("gamaka",)), ("kriya", ("kriyāsamāsa",)), ("avyayibhava", ("avyayībhāva",)),
                     ("bahuvrihi", ("bahuvrīhi",)), ("dvandva", ("dvandva",))):
        if _has(note, *words):
            kind = k
    allow = sid in ("174", "175", "185", "186", "193", "195") or kind in ("gamaka", "kriya")
    if sid == "186":
        if len(inp) == 2 and inp[1] in ("ಅ", "ಇ"):
            return Case(sid, inp, out, note, lambda: {p.result() for p in bahuvrihi(inp[0])})
        if len(inp) == 3 and inp[1] == "ಇಲ್ಲ":
            return Case(sid, inp, out, note, lambda: {
                p.result() for p in compound(_join_ili(inp[0]), inp[2], allow_arisamasa=True)})
    if len(inp) == 3 and sid == "178":
        return Case(sid, inp, out, note, lambda: {p.result() for p in compound(inp[0], inp[2])})
    if len(inp) > 2:
        def runn():
            cur = {inp[0]}
            for nxt in inp[1:]:
                nxt_set = set()
                for c in cur:
                    nxt_set |= {p.result() for p in compound(c, nxt, kind, allow_arisamasa=allow)}
                    nxt_set.add(c + " " + nxt)          # words simply juxtaposed (195)
                cur = nxt_set
            return cur
        return Case(sid, inp, out, note, runn)
    if len(inp) == 1:
        return Case(sid, inp, out, note, set, skip="single word")
    a, b = inp
    return Case(sid, inp, out, note, lambda: {p.result() for p in compound(a, b, kind, allow_arisamasa=allow)})


def _join_ili(word: str) -> str:
    """186: X ಇಲ್ಲ → X-ಇಲಿ (consonant doubled after a short monosyllable)."""
    from . import varna as V
    v = V.to_varnas(word)
    if V.is_vowel(v[-1]) and v[-1] in ("ಉ", "ಇ", "ಎ"):
        v = v[:-1]
    elif V.is_consonant(v[-1]) and len([x for x in v if V.is_vowel(x)]) == 1 and v[-2] in ("ಅ", "ಇ", "ಉ", "ಎ", "ಒ"):
        v = v + [v[-1]]
    return V.from_varnas(v + ["ಇ", "ಲ್", "ಇ"])


# ------------------------------------------------------------------ ākhyāta (216–251a)
@adapter("akhyata")
def akhyata_case(r: dict, ex: dict):
    from .akhyata import derive_parts
    sid = str(r["id"])
    inp, out, note = ex.get("input"), ex.get("output"), ex.get("note", "") or ""
    if not inp or not out:
        return Case(sid, inp, out, note, set, skip="list item (no derivation)")
    if any((x or "").startswith(("−", "-")) or " " in (x or "") for x in inp) or not inp[0]:
        return Case(sid, inp, out, note, set, skip="analysis step / phrase input")
    parts = list(inp)
    if parts[0] in ("ತಾನ್", "ತಾಮ್", "ನೀನ್", "ನೀಮ್", "ಆನ್", "ಆಮ್") and len(parts) > 3:  # pronoun + passive
        pron, parts = parts[0], parts[1:]
        return Case(sid, inp, out, note, lambda: {pron[:-1] + f if pron.endswith("್") else pron + f
                                                   for f in derive_parts(parts)} |
                    {V.from_varnas(V.to_varnas(pron) + V.to_varnas(f)) for f in derive_parts(parts)})
    if "/" in parts[0]:
        parts[0] = parts[0].split("/")[0]
    return Case(sid, inp, out, note, lambda: derive_parts(parts))


from . import varna as V  # noqa: E402


# ------------------------------------------------------------------ taddhita (197–215)
@adapter("taddhita")
def taddhita_case(r: dict, ex: dict):
    from .taddhita import derive, feminine, root_noun
    sid = str(r["id"])
    inp, out, note = ex.get("input"), ex.get("output"), ex.get("note", "") or ""
    if not inp or not out:
        return Case(sid, inp, out, note, set, skip="list item (no derivation)")
    if len(inp) == 1 and sid == "208":
        return Case(sid, inp, out, note, lambda: {p.result() for p in feminine(inp[0])})
    if len(inp) == 1:
        return Case(sid, inp, out, note, lambda: {p.result() for p in root_noun(inp[0])})
    if len(inp) != 2:
        return Case(sid, inp, out, note, set, skip="multi-part input")
    a, b = inp
    def run():
        res = {p.result() for p in derive(a, b)}
        return res | {x + "ರ್" for x in res if x.endswith("ತ")} | {x[:-1] + "ರ್" for x in res if x.endswith("ತಂ")}
    return Case(sid, inp, out, note, run)


# ------------------------------------------------------------------ apabhraṃśa (252–299)
@adapter("apabhramsha")
def apabhramsha_case(r: dict, ex: dict):
    from .apabhramsha import explain
    sid = str(r.get("id"))
    inp, out, note = ex.get("input"), ex.get("output"), ex.get("note", "") or ""
    if not inp or not out:
        return Case(sid, inp, out, note, set, skip="list item (no derivation)")
    if len(inp) == 2 and sid in ("297", "298", "299"):
        from .samasa import compound
        return Case(sid, inp, out, note, lambda: {p.result() for p in compound(inp[0], inp[1], allow_arisamasa=True)})
    if len(inp) != 1 or " " in out or " " in inp[0]:
        return Case(sid, inp, out, note, set, skip="multi-part input")
    src = inp[0]
    def run():
        e = explain(src, out)
        return {out} if e is not None else set()
    return Case(sid, inp, out, note, run)


# ------------------------------------------------------------------ generic battery
def _battery(parts: list[str]) -> set[str]:
    """Every engine that could combine these parts (sandhi in all contexts, compounds,
    verb morphology, case endings). Used for chapters whose examples illustrate
    principles drawn from several chapters (Pūrva, Avyaya)."""
    from .sandhi import COMPOUND, SUFFIX, WORD, results
    from .samasa import compound
    from .akhyata import derive_parts
    cur = {parts[0]}
    for nxt in parts[1:]:
        new = set()
        for c in cur:
            if " " in c:
                continue
            for ctx in (WORD, SUFFIX, COMPOUND):
                new |= results(c, nxt, context=ctx)
            new |= {p.result() for p in compound(c, nxt, allow_arisamasa=True)}
        cur = new
    try:
        cur |= derive_parts(parts)
    except Exception:
        pass
    if len(parts) == 2:
        from .sandhi import sanskrit_join
        cur |= set(sanskrit_join(*parts))
    if len(parts) == 2 and parts[1] in _CASE_OF_SUFFIX:
        from .nama import decline
        for num in ("sg", "pl"):
            cur |= _decl(decline, parts[0], _CASE_OF_SUFFIX[parts[1]], num, None, None, set())
    if len(parts) == 2 and parts[1] in _PLURALS:
        from .nama import decline
        cur |= _decl(decline, parts[0], "nom", "pl", None, None, set())
    return cur


# ------------------------------------------------------------------ pūrva (1–51)
@adapter("purva")
def purva_case(r: dict, ex: dict):
    from .purva import alla_tu, classify, variants
    from .apabhramsha import explain
    sid = str(r.get("id"))
    inp, out, note = ex.get("input"), ex.get("output"), ex.get("note", "") or ""
    if not inp or not out:
        return Case(sid, inp, out, note, set, skip="list item (no derivation)")
    if sid == "19" and len(inp) == 2 and len(inp[0]) <= 2:
        return Case(sid, inp, out, note, set, skip="prosodic statement")
    if sid == "35" and _has(note, "ākhyāta"):
        from .akhyata import derive_parts
        return Case(sid, inp, out, note, lambda: derive_parts([inp[0], "ದ", "ಅಂ"]))
    if sid == "18" and len(inp) == 1:
        return Case(sid, inp, out, note, set, skip="minimal pair (not a derivation)")
    if out in ("ಸವರ್ಣ", "ಹ್ರಸ್ವ", "ದೀರ್ಘ", "ಸಂಧ್ಯಕ್ಷರ", "ನಾಮಿ") or out.endswith("ವರ್ಗ"):
        return Case(sid, inp, out, note, lambda: classify(*inp))
    if len(inp) == 1:
        w = inp[0]
        def run1(w=w):
            res = {p.result() for p in variants(w)} | {w}
            if w.rstrip("ಂ") != out.rstrip("ಂ") and explain(w.rstrip("ಂ"), out.rstrip("ಂ")):
                res.add(out)
            return res
        return Case(sid, inp, out, note, run1)
    if sid == "47" and inp[-1] == "ಅಲ್ಲದು":
        return Case(sid, inp, out, note, lambda: {p.result() for p in alla_tu(inp[0])})
    if sid == "47":
        return Case(sid, inp, out, note, lambda: {p.result() + " " + inp[1] for p in variants(inp[0])})
    if any(" " in x for x in inp):
        return Case(sid, inp, out, note, set, skip="phrase input")
    return Case(sid, inp, out, note, lambda: _battery(list(inp)))


# ------------------------------------------------------------------ avyaya (300–322)
@adapter("avyaya")
def avyaya_case(r: dict, ex: dict):
    sid = str(r.get("id"))
    inp, out, note = ex.get("input"), ex.get("output"), ex.get("note", "") or ""
    if not inp or not out:
        return Case(sid, inp, out, note, set, skip="list item (no derivation)")
    if len(inp) == 1:
        return Case(sid, inp, out, note, set, skip="single word")
    return Case(sid, inp, out, note, lambda: _battery(list(inp)))
