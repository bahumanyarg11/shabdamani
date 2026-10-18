"""Survey sūtra-5 prāsa behaviour in Ollett's kannada_texts (ISO plain text).

Research use only: kannada_texts output stays in reports/private/ and is not published.
Usage: PYTHONPATH=. python tools/prasa_survey.py <txt file> [<txt file> ...]
"""
import re
import sys
from collections import Counter

from shabdamani.prasa import check_prasa
from shabdamani.varna import from_iso

VERSE_END = re.compile(r"//\s*(\S+)\s*(\[([^\]]+)\])?")


def verses(path):
    buf = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("[p."):
            buf = [] if not line else buf
            continue
        m = VERSE_END.search(line)
        if m:
            buf.append(line[:m.start()].strip())
            yield m.group(1), m.group(3) or "", buf
            buf = []
        else:
            buf.append(line)


def main(paths):
    stats, hits = Counter(), []
    for path in paths:
        for ref, meter, padas in verses(path):
            if len(padas) != 4:
                stats["skipped (not 4 lines)"] += 1
                continue
            kn = [from_iso(p) for p in padas]
            letter, found = check_prasa(kn)
            stats["verses"] += 1
            if letter and ("ಳ" in letter or "ಲ" in letter):
                stats["l/ḷ prāsa: " + ("ḷ" if "ಳ" in letter else "l")] += 1
            for f in found:
                stats[f.kind] += 1
                if f.kind == "sutra5":
                    hits.append((ref, meter, f.message, padas[f.pada]))
    for k, v in sorted(stats.items()):
        print(f"{k:28} {v}")
    print("\nsūtra-5 findings:")
    for h in hits:
        print(" | ".join(h))


if __name__ == "__main__":
    main(sys.argv[1:])
