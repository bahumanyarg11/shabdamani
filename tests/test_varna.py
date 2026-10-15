import pytest
from shabdamani import varna as V

CASES = ["ಮರಂ", "ಪೇೞ್", "ಕನ್ನಡಂ", "ಱೆಕ್ಕೆ", "ಬಂದಿರ್ದಂ", "ಕೆಂದಾವರೆ", "ಶಬ್ದಮಣಿದರ್ಪಣಂ", "ಕೃಷ್ಣಂ", "ಅಱಿವು", "ಔದಾರ್ಯಂ", "ದುಃಖಂ"]

@pytest.mark.parametrize("w", CASES)
def test_roundtrip(w):
    assert V.from_varnas(V.to_varnas(w)) == w

def test_split():
    assert V.to_varnas("ಮರಂ") == ["ಮ್", "ಅ", "ರ್", "ಅ", "ಂ"]
    assert V.to_varnas("ಪೇೞ್") == ["ಪ್", "ಏ", "ೞ್"]

def test_iso():
    assert V.to_iso("ಪೇೞ್") == "pēḻ"
    assert V.to_iso("ಅಱಿವು") == "aṟivu"
    assert V.to_iso("ಮರಂ") == "maraṁ"

def test_zwnj_dropped():
    assert V.to_varnas("ವಿಬುಧರ್‌") == V.to_varnas("ವಿಬುಧರ್")
