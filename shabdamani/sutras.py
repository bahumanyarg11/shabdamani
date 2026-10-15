"""Registry of Śabdamaṇidarpaṇa sūtras (text, translation, examples) loaded from JSON.

Rule ids used in traces are strings: ``"54"`` for sūtra 54, ``"54b"`` for the second
rule packed into the same verse (the ``also`` list in the data), ``"v:..."`` for an
engine-internal step that is not a sūtra (e.g. writing conventions).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "data"


class Sutras:
    def __init__(self, records: list[dict]):
        self.by_id: dict[str, dict] = {}
        for r in records:
            if r.get("id") is not None:
                self.by_id.setdefault(str(r["id"]), r)
        self.records = records

    @staticmethod
    def _num(rule: str) -> int | None:
        m = re.match(r"^(\d+)", str(rule))
        return int(m.group(1)) if m else None

    def get(self, rule) -> dict | None:
        """Look up ``"54"``, ``"251a"`` (anukta) or a sub-rule like ``"54b"`` (falls back to 54)."""
        rule = str(rule)
        if rule in self.by_id:
            return self.by_id[rule]
        n = self._num(rule)
        return self.by_id.get(str(n)) if n is not None else None

    def heading(self, rule) -> str:
        r = self.get(rule)
        if not r:
            return ""
        return r.get("heading_en") or (r.get("english") or "")[:70]

    def mula(self, rule) -> str:
        r = self.get(rule)
        return r.get("mula", "") if r else ""

    def chapter(self, name: str) -> list[dict]:
        return [r for r in self.records if r.get("chapter") == name]

    def __len__(self):
        return len(self.by_id)

    def __iter__(self):
        return iter(sorted(self.by_id.values(), key=lambda r: (self._num(r["id"]) or 0, str(r["id"]))))


@lru_cache(maxsize=1)
def load() -> Sutras:
    path = DATA / "smd_sutras.json"
    if not path.exists():
        return Sutras([])
    return Sutras(json.loads(path.read_text(encoding="utf-8")))


@lru_cache(maxsize=1)
def dhatupatha() -> list[dict]:
    path = DATA / "dhatupatha.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


@lru_cache(maxsize=1)
def prayogasara() -> list[dict]:
    path = DATA / "prayogasara.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
