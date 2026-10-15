"""Apabhraṃśa-prakaraṇa (sūtras 252–299): tadbhava formation (Sanskrit/Prakrit → Kannada).

Kēśirāja states the sound changes generally but insists (252) that each applies only
where usage attests it. So the module offers two modes:

``explain(tatsama, tadbhava)``  → the shortest sequence of SMD sound changes (each with its
    sūtra) that turns the Sanskrit word into the Kannada one, or None. This is the
    checking/analysis mode: "is X a regular tadbhava of Y, and by which rules?"
``tadbhava(word)``  → forms obtained by applying only the regular, near-obligatory changes
    (253 ś/ṣ→s, 255 de-aspiration, 261 rC→CC, final -ā→-e, -ī→-i, initial v→b, y→j ...).

Every rule is a *single-site* rewrite ``(varṇas) -> [(new_varṇas, sūtra, note)]``.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from . import samjna as S
from . import varna as V
from .prakriya import Prakriya, Term

C = lambda s: s + V.VIRAMA  # consonant varṇa from letter
VOWELS = set(V.VOWELS)


def _isv(x):
    return x in VOWELS


def _isc(x):
    return V.is_consonant(x)


def _syllable_index(vs: list[str]) -> list[int]:
    """syllable number (0-based) of each varṇa position (consonants belong to the next vowel)."""
    idx, n = [], 0
    seen_vowel = False
    for v in vs:
        if _isv(v):
            idx.append(n)
            n += 1
            seen_vowel = True
        else:
            idx.append(n)
    return idx


def _vowel_positions(vs):
    return [k for k, v in enumerate(vs) if _isv(v)]


# ---------------------------------------------------------------- single-site rules
def _sub_each(vs, src, dsts, rule, note, where=None):
    out = []
    for k, v in enumerate(vs):
        if v == src and (where is None or where(vs, k)):
            for d in dsts:
                out.append((vs[:k] + list(d) + vs[k + 1:], rule, note))
    return out


def _initial(vs, k):
    return k == 0 or (k == 1 and _isc(vs[0]) and _isv(vs[1]) and False)


def _word_initial_consonant(vs, k):
    return k == 0


def _medial(vs, k):
    return 0 < k < len(vs) - 1


def _between_vowels(vs, k):
    return 0 < k < len(vs) - 1 and _isv(vs[k - 1]) and _isv(vs[k + 1])


def _first_syllable_vowel(vs, k):
    vp = _vowel_positions(vs)
    return bool(vp) and k == vp[0]


def _non_initial_vowel(vs, k):
    vp = _vowel_positions(vs)
    return bool(vp) and k != vp[0] and k != vp[-1]


def _final_vowel(vs, k):
    return k == len(vs) - 1 and _isv(vs[k])


def _final_syllable_consonant(vs, k):
    vp = _vowel_positions(vs)
    return len(vp) >= 2 and vp[-2] < k < vp[-1]


def rules(vs: list[str]) -> list[tuple[list[str], str, str]]:
    out = []
    add = out.extend
    # 253 ś, ṣ → s ; 263 → c
    add(_sub_each(vs, C("ಶ"), [[C("ಸ")]], "253", "ś → s"))
    add(_sub_each(vs, C("ಷ"), [[C("ಸ")]], "253", "ṣ → s"))
    add(_sub_each(vs, C("ಶ"), [[C("ಚ")]], "263", "ś → c"))
    add(_sub_each(vs, C("ಷ"), [[C("ಚ")]], "263", "ṣ → c"))
    add(_sub_each(vs, C("ಸ"), [[C("ಚ")]], "263", "s → c (bahula)"))
    # 255 voicing (medial) and de-aspiration
    for a, b in (("ಕ", "ಗ"), ("ಚ", "ಜ"), ("ಟ", "ಡ"), ("ತ", "ದ")):
        add(_sub_each(vs, C(a), [[C(b)]], "255", f"{a} → {b}", where=lambda v, k: k > 0 or True))
    for a, b in (("ಖ", "ಕ"), ("ಛ", "ಚ"), ("ಠ", "ಟ"), ("ಥ", "ತ"), ("ಫ", "ಪ"),
                 ("ಘ", "ಗ"), ("ಝ", "ಜ"), ("ಢ", "ಡ"), ("ಧ", "ದ"), ("ಭ", "ಬ")):
        add(_sub_each(vs, C(a), [[C(b)]], "255", f"de-aspiration {a} → {b}"))
    # 256
    add(_sub_each(vs, C("ಖ"), [[C("ಗ")]], "256", "kh → g"))
    add(_sub_each(vs, C("ಛ"), [[C("ಸ")]], "256", "ch → s"))
    # 257
    add(_sub_each(vs, C("ಠ"), [[C("ಡ")], [C("ೞ")]], "257", "ṭh → ḍ / ḻ"))
    add(_sub_each(vs, C("ಥ"), [[C("ದ")], [C("ಟ")], [C("ಹ")]], "257", "th → d / ṭ / h"))
    # 258 labials
    add(_sub_each(vs, C("ಪ"), [[C("ವ")]], "258", "p → v", where=lambda v, k: k > 0))
    add(_sub_each(vs, C("ಪ"), [[C("ಹ")]], "258", "p → h"))
    add(_sub_each(vs, C("ಬ"), [[C("ವ")]], "258", "b → v"))
    add(_sub_each(vs, C("ವ"), [[C("ಬ")]], "258", "v → b"))
    # 259 y
    add(_sub_each(vs, C("ಯ"), [[C("ಜ")]], "259", "y → j"))
    add(_sub_each(vs, C("ಯ"), [[C("ಗ")], [C("ನ")]], "259", "y → g / n (rare)"))
    # 263 m → v ; c → s / d ; h → y / g / ṇ
    add(_sub_each(vs, C("ಮ"), [[C("ವ")]], "263", "m → v", where=lambda v, k: k > 0))
    add(_sub_each(vs, C("ಚ"), [[C("ಸ")], [C("ದ")]], "263", "c → s / d"))
    add(_sub_each(vs, C("ಹ"), [[C("ಯ")], [C("ಗ")], [C("ಣ")]], "263", "h → y / g / ṇ"))
    # 267 d → v r j y t ḍ
    add(_sub_each(vs, C("ದ"), [[C("ವ")], [C("ರ")], [C("ಜ")], [C("ಯ")], [C("ತ")], [C("ಡ")]], "267", "d → v/r/j/y/t/ḍ"))
    # 276 medial m/ḷ → g ; k → v
    add(_sub_each(vs, C("ಮ"), [[C("ಗ")]], "276", "medial m → g", where=_medial))
    add(_sub_each(vs, C("ಳ"), [[C("ಗ")]], "276", "medial ḷ → g", where=_medial))
    add(_sub_each(vs, C("ಕ"), [[C("ವ")]], "276", "medial k → v", where=_medial))
    # 277 t → r/ṭ/g (medial), ḍ/h (final syllable)
    add(_sub_each(vs, C("ತ"), [[C("ರ")], [C("ಟ")], [C("ಗ")]], "277", "medial t → r/ṭ/g", where=_medial))
    add(_sub_each(vs, C("ತ"), [[C("ಡ")], [C("ಹ")]], "277", "t → ḍ/h", where=_final_syllable_consonant))
    # 278 n / k → ṇ
    add(_sub_each(vs, C("ನ"), [[C("ಣ")]], "278", "n → ṇ"))
    add(_sub_each(vs, C("ಕ"), [[C("ಣ")]], "278", "k → ṇ (final syllable)", where=_final_syllable_consonant))
    # 282 j → y/s/d/c ; bh → h/p/v ; r → l/ḷ
    add(_sub_each(vs, C("ಜ"), [[C("ಯ")], [C("ಸ")], [C("ದ")], [C("ಚ")]], "282", "j → y/s/d/c"))
    add(_sub_each(vs, C("ಭ"), [[C("ಹ")], [C("ಪ")], [C("ವ")]], "282", "bh → h/p/v"))
    add(_sub_each(vs, C("ರ"), [[C("ಲ")], [C("ಳ")]], "282", "r → l/ḷ"))
    add(_sub_each(vs, C("ಧ"), [[C("ಜ")]], "283", "dh → j"))
    add(_sub_each(vs, C("ಮ"), [[C("ಬ")]], "284", "m → b"))
    add(_sub_each(vs, C("ಡ"), [[C("ಳ")]], "284", "ḍ → ḷ"))
    add(_sub_each(vs, C("ಲ"), [[C("ಳ")]], "16", "l → ḷ (kṣaḷa)"))
    add(_sub_each(vs, C("ಣ"), [[C("ಲ")]], "280a", "ṇ → l"))
    # 20–22: ṭ, t, ṭh, r, ḷ → ḻ ; ḍ, ṭ → ḷ in tadbhavas
    for src in ("ಟ", "ತ", "ರ", "ಳ"):
        add(_sub_each(vs, C(src), [[C("ೞ")]], "21", f"{src} → ḻ (tadbhava)"))
    add(_sub_each(vs, C("ಟ"), [[C("ಳ")]], "22", "ṭ → ḷ (tadbhava)"))

    # ---- clusters
    for k in range(len(vs) - 1):
        a, b = vs[k], vs[k + 1]
        if not (_isc(a) and _isc(b)):
            continue
        pre, post = vs[:k], vs[k + 2:]
        rest = vs[k + 2:]
        def put(new, rule, note):
            out.append((pre + new + post, rule, note))
        # 262 kṣ
        if a == C("ಕ") and b == C("ಷ"):
            for new in ([C("ಕ"), C("ಕ")], [C("ಚ"), C("ಚ")], [C("ಖ"), C("ಖ")], [C("ಸ")], [C("ಕ")]):
                put(new, "262", "kṣ → kk/cc/khkh/s/k")
        # 269/278 jñ
        if a == C("ಜ") and b == C("ಞ"):
            put([C("ನ"), C("ನ")], "269", "jñ → nn")
            put([C("ಣ")], "278", "jñ → ṇ")
        # 261 rC → CC ; Cr → C / CC
        if a == C("ರ") and b != C("ರ"):
            put([b, b], "261", "pre-consonantal r lost, consonant doubled")
            put([b], "261", "pre-consonantal r lost")
        if b == C("ರ") and a != C("ರ"):
            put([a], "261", "post-consonantal r lost")
            put([a, a], "261", "post-consonantal r lost, consonant doubled")
        # 259/260/266/281 Cy
        if b == C("ಯ"):
            if a in (C("ದ"), C("ಧ")):
                put([C("ಜ"), C("ಜ")], "259", "dy → jj")
                put([C("ಜ")], "260", "dy/dhy → j")
                put([C("ದ"), C("ದ")], "276", "dhy → dd")
            if a == C("ವ"):
                put([C("ಬ"), C("ಬ")], "266", "vy → bb")
            if a == C("ತ"):
                put([C("ಚ"), C("ಚ")], "263", "ty → cc")
            if a == C("ಛ"):
                put([C("ಚ"), C("ಚ")], "256", "chy → cc")
            put([a, a], "266", "Cy → CC")
            put([a], "281", "y lost after a consonant")
        # Cv
        if b == C("ವ"):
            put([a, a], "266", "Cv → CC")
            put([a], "281", "v lost after a consonant")
        # 266 gn ; 265 ṣm ṣk tp tn nm rṇ ; 264 kt st pt hm hn ; 283 ṣṭ(h) ddh ; 257 sth ; 263 śc ts
        pairs = {
            (C("ಗ"), C("ನ")): ([C("ಗ"), C("ಗ")], "266"), (C("ಷ"), C("ಮ")): ([C("ಮ"), C("ಮ")], "265"),
            (C("ಷ"), C("ಕ")): ([C("ಕ"), C("ಕ")], "265"), (C("ತ"), C("ಪ")): ([C("ಪ"), C("ಪ")], "265"),
            (C("ತ"), C("ಫ")): ([C("ಪ"), C("ಪ")], "265"), (C("ತ"), C("ನ")): ([C("ನ"), C("ನ")], "265"),
            (C("ನ"), C("ಮ")): ([C("ಮ"), C("ಮ")], "265"), (C("ಕ"), C("ತ")): ([C("ತ"), C("ತ")], "264"),
            (C("ಸ"), C("ತ")): ([C("ತ"), C("ತ")], "264"), (C("ಪ"), C("ತ")): ([C("ತ"), C("ತ")], "264"),
            (C("ಹ"), C("ಮ")): ([C("ಮ"), C("ಮ")], "264"), (C("ಹ"), C("ನ")): ([C("ನ"), C("ನ")], "264"),
            (C("ಶ"), C("ಚ")): ([C("ಚ"), C("ಚ")], "263"), (C("ತ"), C("ಸ")): ([C("ಚ"), C("ಚ")], "263"),
            (C("ತ"), C("ಕ")): ([C("ಕ"), C("ಕ")], "264"), (C("ದ"), C("ಗ")): ([C("ಗ"), C("ಗ")], "264"),
            (C("ಪ"), C("ಸ")): ([C("ಚ"), C("ಚ")], "263"), (C("ಣ"), C("ಯ")): ([C("ಣ"), C("ಣ")], "266"),
        }
        if (a, b) in pairs:
            new, rule = pairs[(a, b)]
            put(new, rule, "cluster assimilation")
        if a == C("ಷ") and b in (C("ಟ"), C("ಠ")):
            for new in ([C("ಟ"), C("ಟ")], [C("ಡ"), C("ಡ")], [C("ಟ")]):
                put(new, "283", "ṣṭ(h) → ṭṭ/ḍḍ/ṭ")
        if a == C("ದ") and b == C("ಧ"):
            for new in ([C("ಡ"), C("ಡ")], [C("ಜ"), C("ಜ")], [C("ಡ")]):
                put(new, "283", "ddh → ḍḍ/jj")
        if a == C("ಸ") and b == C("ಥ"):
            put([C("ತ")], "257", "sth → t")
        if k == 0 and a in (C("ಸ"), C("ಶ")):
            put([b], "272", "initial s/ś lost")
        if a == C("ಸ") and b == C("ನ"):
            put([C("ಸ")], "281", "n of snu lost")
        # 254 epenthesis
        if a != b:
            for vow in ("ಅ", "ಇ", "ಉ"):
                put([a, vow, b], "254", f"vowel {vow} inserted into the cluster")
    # ---- anusvāra (285)
    for k, v in enumerate(vs):
        if v == V.ANUSVARA:
            out.append((vs[:k] + vs[k + 1:], "285", "anusvāra lost"))
    vp = _vowel_positions(vs)
    for k in vp[:2]:
        if k + 1 < len(vs) and vs[k + 1] != V.ANUSVARA:
            out.append((vs[:k + 1] + [V.ANUSVARA] + vs[k + 1:], "285", "anusvāra inserted"))
    # ---- vowels
    if vs and vs[0] == "ಋ":
        out.append(([C("ರ"), "ಇ"] + vs[1:], "268", "initial ṛ → ri"))
    for k, v in enumerate(vs):
        if v == "ಋ" and k > 0:
            for d in ("ಇ", "ಎ", "ಅ", "ಉ"):
                out.append((vs[:k] + [d] + vs[k + 1:], "268", f"ṛ → {d}"))
            out.append((vs[:k] + ["ಅ", C("ರ")] + vs[k + 1:], "268", "ṛ → ar"))
    if vp:
        f = vp[0]
        fv = vs[f]
        if f == 0 and fv == "ಅ":
            for d in ("ಉ", "ಇ"):
                out.append(([d] + vs[1:], "269", f"initial a → {d}"))
            out.append(([C("ಹ")] + vs, "269", "prothetic h"))
        if fv in ("ಉ", "ಊ", "ಔ", "ಅ"):
            for d in ("ಒ", "ಓ"):
                out.append((vs[:f] + [d] + vs[f + 1:], "270", f"first-syllable {fv} → {d}"))
        if fv in S.DIRGHA and fv in S.SHORTEN:
            out.append((vs[:f] + [S.SHORTEN[fv]] + vs[f + 1:], "270", "first-syllable long vowel shortened"))
        if fv in ("ಇ", "ಅ", "ಐ", "ಆ"):
            for d in ("ಎ", "ಏ"):
                out.append((vs[:f] + [d] + vs[f + 1:], "271", f"first-syllable {fv} → {d}"))
        if fv in ("ಐ",):
            out.append((vs[:f] + ["ಏ"] + vs[f + 1:], "271", "ai → ē"))
        if fv in ("ಅ", "ಆ") and f + 2 < len(vs) and vs[f + 1] == C("ಹ"):
            out.append((vs[:f] + ["ಐ"] + vs[f + 3:], "275", "a + hi → ai"))
    if vs and vs[0] == C("ಹ"):
        out.append((vs[1:], "271", "initial h dropped"))
    for k in vp[1:]:
        v = vs[k]
        last = k == vp[-1]
        if v in S.SHORTEN and v in S.DIRGHA:
            out.append((vs[:k] + [S.SHORTEN[v]] + vs[k + 1:], "273", "non-initial long vowel shortened"))
        if not last:
            for src, dsts, rule in (("ಓ", ("ಉ",), "273"), ("ಉ", ("ಇ", "ಅ"), "273"), ("ಅ", ("ಇ", "ಉ", "ಎ", "ಒ"), "274"),
                                    ("ಏ", ("ಅ",), "274"), ("ಈ", ("ಅ",), "274"), ("ಆ", ("ಎ",), "274"),
                                    ("ಊ", ("ಅ",), "286")):
                if v == src:
                    for d in dsts:
                        out.append((vs[:k] + [d] + vs[k + 1:], rule, f"medial {src} → {d}"))
    if vs and _isv(vs[-1]):
        v = vs[-1]
        finals = {"ಆ": ("ಎ", "ಅ", "ಇ"), "ಈ": ("ಇ", "ಎ"), "ಊ": ("ಉ",), "ಅ": ("ಎ", "ಇ", "ಉ"),
                  "ಉ": ("ಇ", "ಅ"), "ಇ": ("ಉ", "ಎ")}
        for d in finals.get(v, ()):
            out.append((vs[:-1] + [d], "278" if v == "ಅ" else "279" if v in ("ಉ", "ಇ") else "82",
                        f"final {v} → {d}"))
        if len(vp) > 1 and _isc(vs[-2]):
            out.append((vs[:-1], "279", "final vowel dropped"))
        if len(vp) > 2:
            out.append((vs[:vp[-2] + 1], "280", "final syllable lost"))
    if vs and vs[-1] == V.VISARGA:
        out.append((vs[:-1], "87", "visarga dropped"))
    # 275/288 medial syllable loss
    for j in range(1, len(vp) - 1):
        start = vp[j - 1] + 1
        end = vp[j] + 1
        out.append((vs[:start] + vs[end:], "288", "a medial syllable lost"))
    # geminate simplification (bahula, cf. 262 note / 285)
    for k in range(len(vs) - 1):
        if _isc(vs[k]) and vs[k] == vs[k + 1]:
            out.append((vs[:k] + vs[k + 1:], "283", "geminate simplified"))
    return out


# ---------------------------------------------------------------- search
def _dist(a: list[str], b: list[str]) -> int:
    n, m = len(a), len(b)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m
        for j in range(1, m + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        prev = cur
    return prev[m]


@dataclass
class Explanation:
    tatsama: str
    tadbhava: str
    steps: list[tuple[str, str, str]] = field(default_factory=list)   # (sūtra, note, result)

    def describe(self) -> str:
        lines = [f"{self.tatsama} → {self.tadbhava}"]
        for rule, note, res in self.steps:
            lines.append(f"  {rule:>5}  {res}   ({note})")
        return "\n".join(lines)

    def prakriya(self) -> Prakriya:
        p = Prakriya([Term.make(self.tatsama)])
        for rule, note, res in self.steps:
            p.terms = [Term.make(res)]
            p.log(rule, note)
        return p


# lexically rare substitutions (Kēśirāja: "in some words"); a derivation may use at most
# MAX_RARE of them — calibrated so that unrelated word pairs are not "explained"
RARE_RULES = {"267", "282", "277", "288", "280", "276", "269", "272", "285", "21", "22"}
MAX_RARE = 2
MAX_PER_SOUND = 2      # an original sound may be rewritten at most twice (e.g. ph → p → h)


def explain(tatsama: str, tadbhava: str, max_steps: int = 7, beam: int = 400) -> Explanation | None:
    """Search for a derivation tatsama → tadbhava using the chapter's sound changes
    (at most ``max_steps`` changes, at most MAX_RARE lexically rare ones)."""
    src, tgt = V.to_varnas(V.normalize(tatsama)), V.to_varnas(V.normalize(tadbhava).rstrip("ಂ"))
    tgt_full = V.to_varnas(V.normalize(tadbhava))
    targets = {tuple(tgt), tuple(tgt_full)}
    start = tuple(src)
    if start in targets:
        return Explanation(tatsama, tadbhava, [])
    # state = (varṇas, touched-flags): every original sound may be rewritten at most MAX_PER_SOUND times
    start_state = (start, tuple(0 for _ in start))
    frontier = [(_dist(src, tgt), 0, start_state)]
    parent: dict[tuple, tuple] = {start: None}
    rare = {start: 0}
    for _ in range(max_steps):
        nxt = {}
        for _, _, (state, touched) in frontier:
            for new, rule, note in rules(list(state)):
                t = tuple(new)
                if t in parent:
                    continue
                # changed span: old[i:len(old)-j] → new[i:len(new)-j]
                i = 0
                while i < min(len(state), len(t)) and state[i] == t[i]:
                    i += 1
                j = 0
                while j < min(len(state), len(t)) - i and state[-1 - j] == t[-1 - j]:
                    j += 1
                span = touched[i:len(state) - j]
                if any(c >= MAX_PER_SOUND for c in span):
                    continue
                r = rare[state] + (rule in RARE_RULES)
                if r > MAX_RARE:
                    continue
                level = (max(span) if span else 0) + 1
                new_touched = touched[:i] + tuple(level for _ in range(len(t) - j - i)) + touched[len(state) - j:]
                parent[t] = (state, rule, note)
                rare[t] = r
                if t in targets:
                    return _build_expl(tatsama, tadbhava, parent, t)
                d = min(_dist(new, tgt), _dist(new, tgt_full))
                if t not in nxt or nxt[t][0] > d:
                    nxt[t] = (d, new_touched)
        if not nxt:
            break
        frontier = heapq.nsmallest(beam, ((d, len(s), (s, tch)) for s, (d, tch) in nxt.items()))
    return None


def _build_expl(tatsama, tadbhava, parent, t):
    steps = []
    while parent[t] is not None:
        prev, rule, note = parent[t]
        steps.append((rule, note, V.from_varnas(list(t))))
        t = prev
    return Explanation(tatsama, tadbhava, list(reversed(steps)))


# ---------------------------------------------------------------- generation (regular changes only)
REGULAR = ("253", "255", "261", "82", "259", "258")


def tadbhava(word: str) -> list[Prakriya]:
    """Apply the regular changes greedily: ś/ṣ→s, de-aspiration, rC→CC, final ā→e / ī→i,
    initial y→j, initial v→b, pre-consonantal r loss. Returns the prakriyā(s)."""
    vs = V.to_varnas(V.normalize(word))
    p = Prakriya([Term.make(word, "sanskrit")])

    def apply(rule_ok, note_ok=lambda n: True):
        nonlocal vs
        changed = True
        while changed:
            changed = False
            for new, rule, note in rules(vs):
                if rule_ok(rule, note) and note_ok(note):
                    vs = new
                    p.terms = [Term.make(V.from_varnas(vs))]
                    p.log(rule, note)
                    changed = True
                    break
    apply(lambda r, n: r == "253" and n in ("ś → s", "ṣ → s"))
    apply(lambda r, n: r == "255" and n.startswith("de-aspiration"))
    apply(lambda r, n: r == "261" and n == "pre-consonantal r lost, consonant doubled")
    apply(lambda r, n: r == "262" and n.startswith("kṣ") and False)
    if vs and vs[0] == C("ಯ"):
        vs = [C("ಜ")] + vs[1:]
        p.terms = [Term.make(V.from_varnas(vs))]
        p.log("259", "initial y → j")
    if vs and vs[0] == C("ವ"):
        vs = [C("ಬ")] + vs[1:]
        p.terms = [Term.make(V.from_varnas(vs))]
        p.log("258", "initial v → b")
    if vs and vs[-1] == "ಆ":
        vs = vs[:-1] + ["ಎ"]
        p.terms = [Term.make(V.from_varnas(vs))]
        p.log("82", "final ā → e")
    elif vs and vs[-1] in ("ಈ", "ಊ"):
        vs = vs[:-1] + [S.SHORTEN[vs[-1]]]
        p.terms = [Term.make(V.from_varnas(vs))]
        p.log("83", "final long vowel shortened")
    return [p]
