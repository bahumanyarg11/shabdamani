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
