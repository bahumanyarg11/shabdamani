"""Dump a chapter's rules compactly for implementation work: python3 tools/dump_chapter.py sandhi [maxex]"""
import json, sys
from pathlib import Path
d = json.load(open(Path(__file__).resolve().parents[1] / "shabdamani/data/smd_sutras.json"))
ch = sys.argv[1]; maxex = int(sys.argv[2]) if len(sys.argv) > 2 else 400
for r in d:
    if r.get("chapter") != ch: continue
    print(f"===== {r['id']} {r.get('heading_en')} | {r.get('type')} | {r.get('optionality')} | {r.get('word_class')}")
    print("MULA:", r.get("mula", "").replace("\n", " / "))
    print("EXPL:", r.get("explanation_en"))
    ru = r.get("rule") or {}
    print("DOMAIN:", ru.get("domain"), "| COND:", ru.get("conditions"))
    print("OP:", ru.get("operation"))
    for a in ru.get("also") or []: print("  ALSO:", a)
    ex = r.get("examples") or []
    print(f"EX({len(ex)}):", "; ".join(("+".join(x or "" for x in e["input"]) if e.get("input") else "") + "=" + str(e.get("output")) + (" [" + str(e.get("note"))[:40] + "]" if e.get("note") else "") for e in ex[:maxex]))
    ce = r.get("counterexamples") or []
    if ce: print("COUNTER:", ce)
    print()
