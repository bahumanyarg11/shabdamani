"""Saṃjñā: Kēśirāja's sound classes (Pūrva-prakaraṇa) as sets of varṇas.

Each class names the sūtra that defines it (2015-edition numbering) in ``SOURCE``.
Varṇas are in the internal representation of :mod:`shabdamani.varna`.
"""
from __future__ import annotations

from .varna import ANUSVARA, VISARGA, JIHVAMULIYA, UPADHMANIYA, VIRAMA

def _c(letters: str) -> frozenset[str]:
    return frozenset(ch + VIRAMA for ch in letters)

# ---------------------------------------------------------------- vowels (svara)
SVARA = frozenset("ಅ ಆ ಇ ಈ ಉ ಊ ಋ ೠ ಌ ೡ ಎ ಏ ಐ ಒ ಓ ಔ".split())
HRASVA = frozenset("ಅ ಇ ಉ ಋ ಌ ಎ ಒ".split())
DIRGHA = frozenset("ಆ ಈ ಊ ೠ ೡ ಏ ಐ ಓ ಔ".split())
# samāna: the simple vowels a ā i ī u ū ṛ ṝ ḷ ḹ (Kātantra-style "samāna")
SAMANA = frozenset("ಅ ಆ ಇ ಈ ಉ ಊ ಋ ೠ ಌ ೡ".split())
# sandhyakṣara: diphthong/compound vowels e ē ai o ō au
SANDHYAKSHARA = frozenset("ಎ ಏ ಐ ಒ ಓ ಔ".split())
# nāmi: all vowels except a/ā
NAMI = SVARA - {"ಅ", "ಆ"}
SAVARNA = {  # savarṇa pairs (same place of articulation)
    "ಅ": "ಅಆ", "ಆ": "ಅಆ", "ಇ": "ಇಈ", "ಈ": "ಇಈ", "ಉ": "ಉಊ", "ಊ": "ಉಊ",
    "ಋ": "ಋೠ", "ೠ": "ಋೠ", "ಌ": "ಌೡ", "ೡ": "ಌೡ",
}
LENGTHEN = {"ಅ": "ಆ", "ಇ": "ಈ", "ಉ": "ಊ", "ಋ": "ೠ", "ಌ": "ೡ", "ಎ": "ಏ", "ಒ": "ಓ"}
SHORTEN = {v: k for k, v in LENGTHEN.items()}

# vowel groups by quality (used by the ya/va-āgama sandhi rules)
A_VARNA = frozenset("ಅ ಆ".split())
I_VARNA = frozenset("ಇ ಈ".split())
U_VARNA = frozenset("ಉ ಊ".split())
RI_VARNA = frozenset("ಋ ೠ".split())
E_VARNA = frozenset("ಎ ಏ".split())
O_VARNA = frozenset("ಒ ಓ".split())

# ---------------------------------------------------------------- consonants (vyañjana)
KA_VARGA, CA_VARGA, TA_VARGA_RETRO, TA_VARGA, PA_VARGA = (
    _c("ಕಖಗಘಙ"), _c("ಚಛಜಝಞ"), _c("ಟಠಡಢಣ"), _c("ತಥದಧನ"), _c("ಪಫಬಭಮ"))
VARGA = (KA_VARGA, CA_VARGA, TA_VARGA_RETRO, TA_VARGA, PA_VARGA)
VARGIYA = frozenset().union(*VARGA)
AVARGIYA = _c("ಯರಲವಶಷಸಹಳ")
VYANJANA = VARGIYA | AVARGIYA | _c("ಱೞ")

VARGA_PRATHAMA = _c("ಕಚಟತಪ")   # 1st of each class
VARGA_DVITIYA = _c("ಖಛಠಥಫ")    # 2nd
VARGA_TRITIYA = _c("ಗಜಡದಬ")    # 3rd
VARGA_CHATURTHA = _c("ಘಝಢಧಭ")  # 4th
ANUNASIKA = _c("ಙಞಣನಮ")         # 5th, nasal
MAHAPRANA = VARGA_DVITIYA | VARGA_CHATURTHA | _c("ಶಷಸಹ")
ALPAPRANA = VYANJANA - MAHAPRANA
ANTAHSTHA = _c("ಯರಲವ")
USHMA = _c("ಶಷಸಹ")

# the three Old Kannada "special" laterals/rhotic
RA_ARKA = _c("ರ")        # ordinary ra
SHAKATA_REPHA = _c("ಱ")  # ṟa
KULA = _c("ೞ")           # ḻa ("kuḷa")
KSHALA = _c("ಳ")         # ḷa

YOGAVAHA = frozenset({ANUSVARA, VISARGA, JIHVAMULIYA, UPADHMANIYA})

# consonant voicing / ādēśa maps (used by sandhi & samāsa rules)
VOICED_OF = {"ಕ್": "ಗ್", "ಚ್": "ಜ್", "ಟ್": "ಡ್", "ತ್": "ದ್", "ಪ್": "ಬ್",
             "ಖ್": "ಘ್", "ಛ್": "ಝ್", "ಠ್": "ಢ್", "ಥ್": "ಧ್", "ಫ್": "ಭ್"}
NASAL_OF_VARGA = {}
for _vg in VARGA:
    _nasal = next(iter(_vg & ANUNASIKA))
    for _x in _vg:
        NASAL_OF_VARGA[_x] = _nasal

SOURCE = {
    "SVARA": "purva", "HRASVA": "purva", "DIRGHA": "purva", "SAMANA": "purva",
    "SANDHYAKSHARA": "purva", "NAMI": "purva", "VYANJANA": "purva", "VARGA": "purva",
    "ANUNASIKA": "purva", "MAHAPRANA": "purva", "YOGAVAHA": "purva",
    "SHAKATA_REPHA": "purva", "KULA": "purva", "KSHALA": "purva",
}


def is_svara(v) -> bool:
    return v in SVARA


def is_vyanjana(v) -> bool:
    return v in VYANJANA


def varga_of(v) -> frozenset | None:
    for g in VARGA:
        if v in g:
            return g
    return None
