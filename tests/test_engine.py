"""Spot checks of derivations with their sūtras."""
from shabdamani.akhyata import derive_parts
from shabdamani.analyze import analyze
from shabdamani.nama import forms
from shabdamani.sandhi import results


def test_sandhi():
    assert results("ಮಾತು", "ಎಲ್ಲಂ") == {"ಮಾತುವೆಲ್ಲಂ", "ಮಾತೆಲ್ಲಂ"}          # 52/55 bahula
    assert results("ನದಿ", "ಎಲ್ಲಂ") == {"ನದಿಯೆಲ್ಲಂ"}                     # 55 Sanskrit nitya
    assert "ಕಣ್ಬೊಲನ್" in results("ಕಣ್", "ಪೊಲನ್", context="compound")     # 65


def test_declension():
    assert forms("ಅರಸ", "dat", gender="m") == {"ಅರಸಂಗೆ"}
    assert "ಮರದೊಳ್" in forms("ಮರ", "loc", gender="n")
    assert forms("ಅದು", "dat", gender="n") == {"ಅದರ್ಕೆ"}


def test_verbs():
    assert "ಕೊಟ್ಟಂ" in derive_parts(["ಕುಡು", "ದ", "ಅಂ"])
    assert "ಮಾೞ್ಪಂ" in derive_parts(["ಮಾಡು", "ವ", "ಅಂ"])


def test_analyzer():
    a = analyze("ಅರಸಂಗೆ")[0]
    assert a.lemma == "ಅರಸ" and a.features["case"] == "dative"
    assert any(x.lemma == "ಬರ್" and x.pos == "verb" for x in analyze("ಬಂದಂ"))


# ---------------------------------------------------------------- sūtra 5: prāsa, la vs ḷa
def test_prasa_sutra5():
    from shabdamani.prasa import check_prasa, prasa_letter
    from shabdamani.varna import from_iso
    assert prasa_letter("ಕಿಳಿಱೆ ಹಯಂಗಳ್") == "ಳ್"
    assert prasa_letter(from_iso("caṇḍavirōdhi")) == prasa_letter(from_iso("ṣaṁḍamaraldu"))
    kula = "ಕಿಳಿಱೆ ಹಯಂಗಳ್ ಗರ್ಜಿಸೆ"
    assert check_prasa([kula, "ಜಳದನಿಭಂಗಳ್ ಗಜಂಗಳ್"]) == ("ಳ್", [])          # Darpaṇavivaraṇe p. 190
    _, f = check_prasa([kula, "ಜಲದನಿಭಂಗಳ್ ಗಜಂಗಳ್"])
    assert [x.kind for x in f] == ["sutra5"]
    la = "ಓಲಗದೊಳೊರ್ಮೆ ನತನರ"
    assert check_prasa([la, "ಪಾಲಕಚೂಡಾಮಣಿ"]) == ("ಲ್", [])
    _, f = check_prasa([la, "ಪಾಳಕಚೂಡಾಮಣಿ", "ಮಾಲೆ"])
    assert [x.kind for x in f] == ["sutra5"] and f[0].pada == 1
    _, f = check_prasa([la, "ಪಾಲಕ", "ಮಾರಿ"])                          # not an l/ḷ swap
    assert [x.kind for x in f] == ["other"]


def test_from_iso_roundtrip():
    from shabdamani.varna import from_iso, iso_text
    for w in ["ಶ್ರೀಯನರಾತಿಸಾಧನ", "ನೆಗೞ್ತೆಯಂ", "ಕಿಳಿಱ್", "ಹೃದಯಾಂಬುಜಮಂ", "ಪಯೋನಿಧಿಯೊಳ್"]:
        assert from_iso(iso_text(w)) == w
