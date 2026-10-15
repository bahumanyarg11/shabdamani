# shabdamani — a rule engine for Kēśirāja's Śabdamaṇidarpaṇa (Old Kannada grammar)

Python library + CLI. Each sūtra is data (`shabdamani/data/smd_sutras.json`: verse, vṛtti,
English translation, rule spec, examples) and each implemented rule cites its sūtra in a
step-by-step derivation trace (Vidyut-style prakriyā, optional rules explored exhaustively).

```bash
python3 -m shabdamani.cli sutra 54
python3 -m shabdamani.cli sandhi ಮಾತು ಎಲ್ಲಂ
python3 -m shabdamani.cli decline ಮರ
python3 -m shabdamani.cli coverage -v      # Kēśirāja's own examples as the test suite
```

## Status (Kēśirāja's examples reproduced)
| chapter | module | reproduced |
|---|---|---|
| Sandhi 52–71 | sandhi.py | 360/360 |
| Nāma 72–161 | nama.py | 1004/1004 (phrase examples check the inflected word) |
| Samāsa 162–196 | samasa.py | 484/492 |
| Taddhita 197–215 | taddhita.py | 372/372 |
| Ākhyāta 216–251a | akhyata.py | 599/600 |
| Apabhraṃśa 252–299 | apabhramsha.py | 1016/1107 (search mode; ~1.5% false positives on unrelated pairs) |
| Pūrva 1–51 | purva.py | 276/280 |
| Avyaya 300–322 | adapters | 40/40 |

Total: 4,151 / 4,255 testable examples. `pytest` runs the suite (`SHABDAMANI_SLOW=1` adds Apabhraṃśa).

## Analysing texts
```bash
PYTHONPATH=. python3 tools/analyze_text.py sources/texts/pampa_bharata_asvasa1.txt reports/pampa_asvasa1_analysis.md
python3 -m shabdamani.cli analyze ಬೇಡಿಕೊಳ್ಳದೆ --trace
```
Pampa Bhārata āśvāsa 1 (149 verses, 1,876 tokens): 894 analysed with lexicon-backed lemmas,
957 with a verified grammatical derivation but an unattested stem (or a heuristic saṃhitā split), 25 unanalysed.

Data: 322 sūtras + closing verses, 5,776 examples, 984 dhātus, 236 Prayōgasāra glossary entries,
proofread from the 2015 KSP edition collated with Kittel 1920 and Kedilaya 1973.
Doubtful readings are listed per sūtra in the `uncertain` field — scholarly review needed.

## Known limits
- No general noun lexicon yet (Kittel's dictionary would raise "lexicon" coverage a lot); proper names are unknown.
- Saṃhitā splitting is heuristic (DP over sandhi-undone segments) and sometimes mis-splits.
- Doubtful readings of the edition are listed per sūtra in `uncertain` — scholarly review needed.

## Licence and sources
- **Code** (`shabdamani/`, `tests/`, `tools/`): MIT, see [LICENSE](LICENSE).
- **Kēśirāja's text** (sūtra verses, vṛtti, examples, dhātupāṭha, Prayōgasāra; c. 1260 CE) is in the public domain. Readings were collated by the author across the 2015 Kannada Sāhitya Pariṣattu edition, Kittel/Mangesha Rau (1920) and Kedilaya (1973).
- **Not included:** editorial matter of modern editions. In particular, the avyaya-chapter vṛttis that the 2015 edition's editors wrote themselves (sūtras 301–320; marked `vrtti_editorial`) and the editors' group headings are omitted. No scans or OCR of any edition are distributed.
- **English translations, explanations and rule specifications** are original to this project, released under CC BY 4.0.
- **Pampa Bhārata text** (`sources/texts/`): Pampa (941 CE) is public domain. The transcription is based on Kannada Wikisource and is released under CC BY-SA 4.0 with attribution to the Kannada Wikisource contributors. See [sources/texts/README.md](sources/texts/README.md).

## Citation
If you use this, please cite it with the metadata in [CITATION.cff](CITATION.cff).
