"""Kēśirāja's own examples as the engine's test suite.

Each chapter registers an *adapter*: a function ``(sutra_record, example) -> Case | None``
that turns one prayōga into an engine call. ``run_chapter`` executes all of them and
reports, per sūtra, which examples the engine reproduces.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from .sutras import load


@dataclass
class Case:
    sutra: str
    inputs: list
    expected: str
    note: str
    run: Callable[[], set[str]]          # returns the set of generated outputs
    skip: str | None = None             # reason the case is not testable (yet)


@dataclass
class Outcome:
    case: Case
    ok: bool
    got: set[str] = field(default_factory=set)
    error: str | None = None


ADAPTERS: dict[str, Callable] = {}


def adapter(chapter: str):
    def deco(fn):
        ADAPTERS[chapter] = fn
        return fn
    return deco


def norm(s: str) -> str:
    """Compare forms modulo spacing, ZWNJ/ZWJ and the orthographic equivalences of 161."""
    from .varna import canonical
    s = re.sub(r"\s+", " ", (s or "").replace("\u200c", "").replace("\u200d", "")).strip()
    try:
        return canonical(s)
    except Exception:
        return s


def run_chapter(chapter: str) -> list[Outcome]:
    _load_adapters()
    fn = ADAPTERS.get(chapter)
    if fn is None:
        return []
    outs = []
    for r in load().chapter(chapter):
        counters = {norm(c.get("form", "")) for c in r.get("counterexamples") or []
                    if isinstance(c, dict) and c.get("form")}
        for ex in r.get("examples") or []:
            case = fn(r, ex)
            if case is None:
                continue
            if case.skip:
                outs.append(Outcome(case, False, error="skip: " + case.skip))
                continue
            try:
                got = {norm(g) for g in case.run()}
                bad = sorted(got & counters - {norm(case.expected)})
                if bad:
                    outs.append(Outcome(case, False, got, error=f"overgenerates rejected form(s) {bad}"))
                else:
                    outs.append(Outcome(case, norm(case.expected) in got, got))
            except Exception as e:  # pragma: no cover - reported, not raised
                outs.append(Outcome(case, False, error=f"{type(e).__name__}: {e}"))
    return outs


def _load_adapters():
    from . import adapters  # noqa: F401  (registers adapters)


def coverage_report(verbose: bool = False) -> str:
    _load_adapters()
    lines = []
    total_ok = total = 0
    for ch in ["purva", "sandhi", "nama", "samasa", "taddhita", "akhyata", "apabhramsha", "avyaya"]:
        outs = run_chapter(ch)
        tested = [o for o in outs if not (o.error or "").startswith("skip")]
        ok = sum(o.ok for o in tested)
        total_ok += ok
        total += len(tested)
        if not outs:
            lines.append(f"{ch:12}  (no adapter yet)")
            continue
        lines.append(f"{ch:12}  {ok:5}/{len(tested):<5} examples reproduced"
                     f"  ({len(outs) - len(tested)} skipped)")
        if verbose:
            for o in outs:
                if not o.ok and not (o.error or "").startswith("skip"):
                    c = o.case
                    lines.append(f"    ✗ {c.sutra:>5} {' + '.join(map(str, c.inputs or []))} → {c.expected}"
                                 f"  got {sorted(o.got)[:4]} {o.error or ''}  [{c.note[:50]}]")
    lines.append(f"{'TOTAL':12}  {total_ok:5}/{total}")
    return "\n".join(lines)
