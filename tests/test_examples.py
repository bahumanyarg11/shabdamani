"""Kēśirāja's own prayōgas as regression tests.

Thresholds are the currently reproduced counts: a change that breaks a derivation fails
the suite. Known misses are doubtful readings in the edition (see each sūtra's
`uncertain` field) or internal contradictions of the text.
"""
import os

import pytest

from shabdamani.testing import run_chapter

MIN_REPRODUCED = {"purva": 276, "sandhi": 360, "nama": 1004, "samasa": 484, "taddhita": 372,
                  "akhyata": 599, "avyaya": 40, "apabhramsha": 1010}
SLOW = {"apabhramsha"}


@pytest.mark.parametrize("chapter", sorted(MIN_REPRODUCED))
def test_chapter(chapter):
    if chapter in SLOW and not os.environ.get("SHABDAMANI_SLOW"):
        pytest.skip("slow (set SHABDAMANI_SLOW=1)")
    outs = run_chapter(chapter)
    tested = [o for o in outs if not (o.error or "").startswith("skip")]
    ok = sum(o.ok for o in tested)
    overgen = [o for o in tested if (o.error or "").startswith("overgenerates")]
    assert not overgen, [(o.case.sutra, o.case.inputs, o.error) for o in overgen[:5]]
    assert ok >= MIN_REPRODUCED[chapter], f"{chapter}: {ok} reproduced (expected ≥ {MIN_REPRODUCED[chapter]})"
