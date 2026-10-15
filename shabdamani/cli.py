"""Command-line interface.

    shabdamani sutra 54                 show a sūtra (text, translation, examples)
    shabdamani sandhi ಮಱ ಅಡಿ            join two words, with derivation trace
    shabdamani decline ಮರ               full nominal paradigm
    shabdamani conjugate ಮಾಡು           verb paradigm
    shabdamani tadbhava ಶಿಲಾ             tatsama -> tadbhava
    shabdamani analyze ಮಾಡಿದಂ            word -> possible derivations
    shabdamani coverage                 which sūtras are implemented and how many examples pass
"""
from __future__ import annotations

import argparse
import sys

from . import varna as V
from .sutras import load


def _print_prakriyas(ps, iso=False, show_trace=True):
    reg = load()
    seen = set()
    for p in ps:
        r = p.result()
        key = (r, tuple(s.rule for s in p.history))
        if key in seen:
            continue
        seen.add(key)
        out = V.iso_text(r) if iso else r
        print(f"=> {out}" + (f"   [{V.iso_text(r)}]" if not iso else ""))
        if show_trace:
            print(p.trace(reg, iso=iso))
        for w in p.warnings:
            print("   ! " + w)
        print()


def cmd_sutra(a):
    reg = load()
    r = reg.get(a.id)
    if not r:
        print(f"sūtra {a.id} not found ({len(reg)} loaded)")
        return 1
    print(f"Śabdamaṇidarpaṇa {r['id']}  [{r.get('chapter')}]  {r.get('heading_en', '')}")
    print()
    print(r.get("mula", ""))
    print()
    if a.iso:
        print(V.iso_text(r.get("mula", "")))
        print()
    print("Translation:", r.get("english", ""))
    print()
    print(r.get("explanation_en", ""))
    if r.get("vrtti"):
        print("\nVṛtti:", r["vrtti"])
    ex = r.get("examples") or []
    if ex:
        print(f"\nExamples ({len(ex)}):")
        for e in ex[: a.limit]:
            inp = " + ".join(e["input"]) if e.get("input") else ""
            print(f"  {inp + ' = ' if inp else ''}{e.get('output')}   {e.get('note', '')}")
    return 0


def cmd_sandhi(a):
    from .sandhi import join
    _print_prakriyas(join(a.left, a.right, left_origin=a.left_origin, right_origin=a.right_origin,
                          context=a.context), iso=a.iso)


def cmd_decline(a):
    from .nama import paradigm
    for (case, number), ps in paradigm(a.stem, gender=a.gender, origin=a.origin).items():
        forms = sorted({p.result() for p in ps})
        print(f"{case:>12} {number:>3}: {', '.join(forms)}")
        if a.trace:
            _print_prakriyas(ps, iso=a.iso)


def cmd_conjugate(a):
    from .akhyata import paradigm
    for key, ps in paradigm(a.root).items():
        forms = sorted({p.result() for p in ps})
        print(f"{' '.join(key):>28}: {', '.join(forms)}")
        if a.trace:
            _print_prakriyas(ps, iso=a.iso)


def cmd_tadbhava(a):
    from .apabhramsha import tadbhava
    _print_prakriyas(tadbhava(a.word), iso=a.iso)


def cmd_analyze(a):
    from .analyze import analyze
    res = analyze(a.word)
    if not res:
        print("no analysis found (word not derivable from the lexicon + rules implemented so far)")
    for an in res:
        print(an.describe())
        if a.trace:
            print(an.prakriya.trace(load(), iso=a.iso))
        print()


def cmd_coverage(a):
    from .testing import coverage_report
    print(coverage_report(verbose=a.verbose))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="shabdamani", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--iso", action="store_true", help="show ISO 15919 transliteration")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sutra"); s.add_argument("id"); s.add_argument("--limit", type=int, default=40)
    s.set_defaults(fn=cmd_sutra)
    s = sub.add_parser("sandhi"); s.add_argument("left"); s.add_argument("right")
    s.add_argument("--left-origin"); s.add_argument("--right-origin")
    s.add_argument("--context", default="word+word",
                   help="word+word | stem+suffix | compound")
    s.set_defaults(fn=cmd_sandhi)
    s = sub.add_parser("decline"); s.add_argument("stem"); s.add_argument("--gender")
    s.add_argument("--origin"); s.add_argument("--trace", action="store_true")
    s.set_defaults(fn=cmd_decline)
    s = sub.add_parser("conjugate"); s.add_argument("root"); s.add_argument("--trace", action="store_true")
    s.set_defaults(fn=cmd_conjugate)
    s = sub.add_parser("tadbhava"); s.add_argument("word"); s.set_defaults(fn=cmd_tadbhava)
    s = sub.add_parser("analyze"); s.add_argument("word"); s.add_argument("--trace", action="store_true")
    s.set_defaults(fn=cmd_analyze)
    s = sub.add_parser("coverage"); s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(fn=cmd_coverage)

    a = ap.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
