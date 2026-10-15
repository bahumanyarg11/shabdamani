"""Derivation (prakriyā) model.

A derivation is a list of :class:`Term` objects (stem, suffixes, augments, following
word ...). Rules are plain Python functions that inspect the prakriyā and modify it;
every change is logged as a :class:`Step` naming the sūtra, so the result carries a
full, human-readable trace.

Optional rules (vā, vikalpa, bahuḷa) are explored exhaustively in the style of
vidyut-prakriya: each run follows a *decision path*; the first time an optional rule
is met it is accepted, and afterwards the driver re-runs the derivation with that rule
declined, until every combination has been tried.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from . import varna as V


@dataclass
class Term:
    """One unit in a derivation: a stem, suffix, augment or following word."""

    text: list[str]
    upadesha: str = ""
    tags: set[str] = field(default_factory=set)

    @classmethod
    def make(cls, script: str, *tags: str) -> "Term":
        return cls(V.to_varnas(script), script, set(tags))

    # convenience -----------------------------------------------------------------
    def __str__(self) -> str:
        return V.from_varnas(self.text)

    def has(self, *tags: str) -> bool:
        return any(t in self.tags for t in tags)

    @property
    def first(self):
        return self.text[0] if self.text else None

    @property
    def last(self):
        return self.text[-1] if self.text else None

    def ends_with(self, *suffixes: str) -> bool:
        s = str(self)
        return any(s.endswith(x) for x in suffixes)

    def copy(self) -> "Term":
        return Term(list(self.text), self.upadesha, set(self.tags))


@dataclass
class Step:
    rule: str
    result: str
    note: str = ""


@dataclass
class Choice:
    rule: str
    accepted: bool


class Prakriya:
    def __init__(self, terms: Iterable[Term] = (), path: list[Choice] | None = None,
                 strict: bool = False):
        self.terms: list[Term] = list(terms)
        self.history: list[Step] = []
        self.choices: list[Choice] = []
        self._path = list(path or [])
        self.strict = strict  # True: optional rules never fire unless the path says so
        self.warnings: list[str] = []
        self.tags: set[str] = set()  # derivation-level tags (gender, case, tense ...)
        if self.terms:
            self.log("start")

    # ---------------------------------------------------------------- inspection
    def text(self, sep: str = "") -> str:
        """Surface string.

        With ``sep=""`` the varṇas of all terms are joined and written out together (so a
        consonant ending one term fuses with a vowel starting the next); terms tagged
        ``sep`` (a word boundary left unjoined) are preceded by a space. A non-empty
        ``sep`` (e.g. ``" + "``) shows the terms separately, for traces.
        """
        if sep:
            parts = []
            for k, t in enumerate(self.terms):
                if k:
                    parts.append(" | " if t.has("sep") else sep)
                parts.append(str(t) if t.text else "∅")
            return "".join(parts)
        words, cur = [], []
        for k, t in enumerate(self.terms):
            if k and t.has("sep") and cur:
                words.append(V.from_varnas(cur))
                cur = []
            cur.extend(t.text)
        if cur:
            words.append(V.from_varnas(cur))
        return " ".join(words)

    def varnas(self) -> list[str]:
        out: list[str] = []
        for t in self.terms:
            out.extend(t.text)
        return out

    def find(self, *tags: str) -> int | None:
        for i, t in enumerate(self.terms):
            if t.has(*tags):
                return i
        return None

    def has_tag(self, *tags: str) -> bool:
        return any(t in self.tags for t in tags)

    # ---------------------------------------------------------------- mutation
    def log(self, rule: str, note: str = "") -> None:
        self.history.append(Step(rule, self.text(" + "), note))

    def run(self, rule: str, fn: Callable[["Prakriya"], object], note: str = "") -> bool:
        fn(self)
        self.log(rule, note)
        return True

    def run_at(self, rule: str, i: int, fn: Callable[[Term], object], note: str = "") -> bool:
        fn(self.terms[i])
        self.log(rule, note)
        return True

    def insert(self, rule: str, i: int, term: Term, note: str = "") -> bool:
        self.terms.insert(i, term)
        self.log(rule, note)
        return True

    # ---------------------------------------------------------------- options
    def decide(self, rule: str) -> bool:
        """Return whether optional rule ``rule`` applies on this decision path."""
        k = len(self.choices)
        if k < len(self._path):
            choice = self._path[k]
            if choice.rule != rule:
                # derivation diverged from the recorded path: treat as fresh decision
                self._path = self._path[:k]
            else:
                self.choices.append(choice)
                return choice.accepted
        accepted = not self.strict
        self.choices.append(Choice(rule, accepted))
        return accepted

    def optional(self, rule: str, fn: Callable[["Prakriya"], object], note: str = "") -> bool:
        if self.decide(rule):
            return self.run(rule, fn, note + (" (optional)" if note else "optional"))
        self.log(rule, "optional rule declined")
        return False

    def optional_at(self, rule: str, i: int, fn: Callable[[Term], object], note: str = "") -> bool:
        if self.decide(rule):
            return self.run_at(rule, i, fn, note + (" (optional)" if note else "optional"))
        self.log(rule, "optional rule declined")
        return False

    def warn(self, rule: str, message: str) -> None:
        self.warnings.append(f"[{rule}] {message}")

    # ---------------------------------------------------------------- output
    def result(self) -> str:
        return self.text()

    def trace(self, sutras=None, iso: bool = False) -> str:
        """Readable derivation trace. ``sutras`` is an optional registry for headings."""
        lines = []
        for s in self.history:
            res = V.iso_text(s.result) if iso else s.result
            head = ""
            if sutras is not None and s.rule not in ("start",):
                head = sutras.heading(s.rule)
            note = f"  ({s.note})" if s.note else ""
            lines.append(f"{s.rule:>8}  {res}{note}{'  — ' + head if head else ''}")
        return "\n".join(lines)


def derive_all(fn: Callable[..., None], *args, limit: int = 256, **kwargs) -> list[Prakriya]:
    """Run ``fn(prakriya, *args)`` over every combination of optional-rule decisions.

    ``fn`` receives a fresh :class:`Prakriya` (with a decision path) and must build the
    derivation from scratch. Returns one Prakriya per distinct decision path.
    """
    results: list[Prakriya] = []
    queue: list[list[Choice]] = [[]]
    seen: set[tuple] = set()
    while queue and len(results) < limit:
        path = queue.pop(0)
        p = Prakriya(path=path)
        fn(p, *args, **kwargs)
        key = tuple((c.rule, c.accepted) for c in p.choices)
        if key in seen:
            continue
        seen.add(key)
        results.append(p)
        for k in range(len(path), len(p.choices)):
            c = p.choices[k]
            if c.accepted:
                queue.append(p.choices[:k] + [Choice(c.rule, False)])
    return results


def unique_results(prakriyas: list[Prakriya]) -> dict[str, list[Prakriya]]:
    out: dict[str, list[Prakriya]] = {}
    for p in prakriyas:
        out.setdefault(p.result(), []).append(p)
    return out
