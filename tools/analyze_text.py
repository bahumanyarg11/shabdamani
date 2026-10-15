"""Analyse a Halegannada text file: python3 tools/analyze_text.py FILE [OUT.md]"""
import sys, collections
from shabdamani.analyze import analyze_text
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else src.rsplit(".", 1)[0] + "_analysis.md"
import re
raw = open(src, encoding="utf-8").read()
# verse blocks: drop "## N" headers, join a verse's lines (words run across line ends)
blocks = [b for b in re.split(r"\n\s*\n", raw) if b.strip()]
text = "\n".join("".join(l.strip() for l in b.splitlines() if not l.startswith("#")) for b in blocks)
reps = analyze_text(text)
stat = collections.Counter(r.status for r in reps)
rules = collections.Counter()
lines = [f"# Analysis of {src}", "", f"Tokens: {len(reps)} — " + ", ".join(f"{k}: {v}" for k, v in stat.items()), ""]
body = []
for r in reps:
    if not r.analyses:
        body.append(f"- **{r.token}** — ❓ not derivable with the rules + lexicon"); continue
    a = r.analyses[0]
    rules.update(a.rules())
    alt = "; ".join(f"{b.lemma} [{b.feature_str()}]" for b in r.analyses[1:3])
    body.append(f"- **{r.token}** ← {a.lemma} [{a.pos}; {a.feature_str()}] ({a.evidence})"
                + (f" · rules {', '.join(a.rules())}" if a.rules() else "") + (f" · alt: {alt}" if alt else ""))
lines += ["Most used sūtras: " + ", ".join(f"{k}×{v}" for k, v in rules.most_common(15)), ""] + body
open(out, "w", encoding="utf-8").write("\n".join(lines))
print(out, dict(stat))
