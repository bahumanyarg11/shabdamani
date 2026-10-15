# Śabdamaṇidarpaṇa — sūtra encoding guide

This guide documents how the OCR of the *Śabdamaṇidarpaṇa*
(Kēśirāja, c. 1260 CE) into clean, machine-usable sūtra records.

## Sources

Editions consulted (scans and OCR are **not** distributed with this repository):

| Edition | Use |
|---|---|
| Kannada Sāhitya Pariṣattu, ed. T. V. Venkatachala Sastry (2nd rev. ed., 2015 printing) | Base for sūtra numbering and readings |
| F. Kittel (1872), re-edited by Mangesha Rau (1920) | Collation; English headings |
| Kedilaya, University of Madras (1973), with Liṅgaṇārādhya's commentary | Collation; alternative readings |
| F. Kittel, *A Grammar of the Kannada Language* (1903) | English terminology |
| J. S. Kulli, *Kesiraja's Sabdamani Darpana: a linguistic analysis* (1971) | Modern linguistic reading |

Only Kēśirāja's own text (c. 1260 CE: sūtra verses, vṛtti, examples, Prayōgasāra) is reproduced.
Editorial matter of modern editions (the avyaya-chapter vṛttis written by the 2015 editors, group
headings, notes) is omitted; English translations and rule specifications are original to this project.

## Known OCR artefacts (2015 edition scan)

* `ಇ`, `೬`, `ಎ`, `ಥ್ರ`, `ಷ` standing alone between words are usually `=` (gloss separator).
* The letter **ಱ** (śakaṭa-rēpha) is frequently OCR'd as `ಅ`, `ಜ`, `ಟ`, `ಖ`, e.g. `ನೆಅ್‌ಯೆ` → `ನೆಱೆಯೆ`,
  `ಇದಅಕೊಳ್‌` / `ಇದಳಕೊಳ್‌` → `ಇದಱೊಳ್`, `ಅಜಯಲ್ಪಟ್ಟು` → `ಅಱಿಯಲ್ಪಟ್ಟು`.
* The letter **ೞ** (kuḷa / ḻa) is frequently OCR'd as `ಟ`, `ಟ್‌`, `ಳ`, e.g. `ಪೇಟ್ವ` → `ಪೇೞ್ವ`, `ಪೇಟಕಿಂ` → `ಪೇೞ್ಕೆಂ`.
  Use your knowledge of Old Kannada: ೞ occurs in e.g. ಪೇೞ್, ಕೞ್, ಬೞಿ, ಮೞೆ, ತೞ್ತು, ಏೞ್, ಕೀೞ್, ಪೞ, ಬಾೞ್.
* Verse-line ends: `|`, `1`, `!`, `ಟ`, `॥!`, `11`, `1!` are all pāda/half-verse markers.
* `ಖೂ` is often `ೠ`; `ಖು` often `ಋ`; `ಐ`/`ಔ` sometimes split.
* Footnote numerals and page headers (`೪೦ ಶಬ್ದಮಣಿದರ್ಪಣಂ`, `ಸಂಧಿಪ್ರಕರಣಂ | ೪೧`) are noise inside sūtras.
* Stray Latin letters / symbols (`ಕ`, `Pol`, `ಟ`, `ಎ.ಪಿ`) at line starts are noise.

Correct only what you are confident about. Where a reading is uncertain, keep your best
reading and record the doubt in `uncertain`.

## Output record schema (one JSON object per sūtra)

```json
{
  "id": 54,
  "chapter": "sandhi",
  "mula": "ಸದಮಳ ಸಂಸ್ಕೃತ ಕರ್ಣಾ-\nಟದದಂತಪ್ರಕೃತಿಗಳ್ಗಿಸುಪ್ರತ್ಯಯಮಿಂ\nತಿದಿರಾಗೆ ಯತ್ವಮನುಕೃತಿ-\nಪದಕಂ ಮುಂದನುಕೃತಿಸ್ವರಂ ನಿಲೆ ಯತ್ವಂ",
  "vrtti": "ಅಮಳತರ ಸಂಸ್ಕೃತ ಕರ್ಣಾಟದಕಾರಾಂತ ಪ್ರಕೃತಿಗಳ್ಗೆ ಇಸು ಪ್ರತ್ಯಯಂ ಪರಮಾಗೆ, ನಡುವೆ ಯತ್ವಮಕ್ಕುಂ; ...",
  "english": "Literal translation of the sūtra verse.",
  "explanation_en": "What the rule does, in plain English, using the vṛtti and examples. Mention exceptions.",
  "heading_en": "Short title (≤ 8 words), e.g. 'y-insertion before the suffix -isu'",
  "type": "vidhi",
  "optionality": "obligatory",
  "word_class": "both",
  "rule": {
    "domain": "stem+suffix",
    "conditions": ["left: stem ending in a (Sanskrit or Kannada)", "right: suffix isu (causative/denominative)"],
    "operation": "insert y between them (ya-āgama)",
    "also": ["left: onomatopoeic (anukṛti) word ending in a; right: vowel of anukṛti-particle → insert y"]
  },
  "examples": [
    {"input": ["ಶುದ್ಧ", "ಇಸಿದಂ"], "output": "ಶುದ್ಧಯಿಸಿದಂ", "note": "Sanskrit stem"},
    {"input": ["ತೇರ", "ಇಸಿದಂ"], "output": "ತೇರಯಿಸಿದಂ", "note": "Kannada stem"}
  ],
  "counterexamples": [],
  "quotations": [{"text": "ಪಟಪಟಯೆಂದಾಲಿಕಲ್ಗಳುದಿರ್ದುವು ನಭದಿಂ", "poet": null}],
  "cross_refs": [53],
  "uncertain": ["pāda 2: `ಗಳ್ಳಿಸು` read as `ಗಳ್ಗಿಸು`"],
  "source_lines": [4581, 4612]
}
```

### Field rules

* `id` — the sūtra number printed in the 2015 edition (Kannada numerals → integer). If a sūtra
  has no visible number, infer it from its neighbours and mention that in `uncertain`.
  Sūtras marked *anukta* (not in the original; added by later hands) get `"anukta": true`.
* `chapter` — one of `purva, sandhi, nama, samasa, taddhita, akhyata, dhatu, apabhramsha, avyaya`.
* `mula` — the kanda verse, corrected, **pādas separated by `\n`**, no daṇḍas, no verse number.
  Keep the Old Kannada orthography (ಱ, ೞ, final consonants written with virāma, e.g. `ವಿಬುಧರ್`;
  drop the ZWNJ that the OCR emits after virāma).
* `vrtti` — Kēśirāja's own prose vṛtti, corrected. **Do not copy the modern ṭīke**
  (the word-by-word gloss) into any field; use it only to understand the verse.
* `english` — faithful translation of the verse. `explanation_en` — clear explanation.
* `type` — one of:
  `mangala` (invocation/colophon), `meta` (about the book, its sources, method),
  `samjna` (defines a technical term or sound class), `paribhasha` (interpretive meta-rule),
  `vidhi` (operation: insert/delete/substitute/add suffix), `niyama` (restricts another rule),
  `nishedha` (prohibition), `atidesha` (extension: X behaves like Y), `adhikara` (heading),
  `nipatana` (lists irregular/ready-made forms), `list` (word lists, e.g. words with ೞ),
  `semantic` (meaning/usage of a case, tense, particle), `dosha` (a fault poets must avoid).
* `optionality` — `obligatory`, `optional` (vā, vikalpa), `bahula` (variably/as per usage),
  `prohibited`, or `n/a`.
* `word_class` — `kannada` (dēśya), `sanskrit` (tatsama), `tadbhava`, `both`, or `n/a`.
* `rule` — semi-formal spec that a programmer can implement directly. Be explicit about
  *what is on the left, what is on the right, what changes*. Use these terms:
  - positions: `left` (pūrva: preceding word/stem), `right` (para: following word/suffix);
  - domains: `word+word` (pada sandhi), `stem+suffix` (vibhakti/pratyaya), `compound`,
    `within-word`, `semantic`, `orthography`, `prosody`, `lexicon`;
  - operations: `insert X` (āgama), `delete X` (lōpa), `replace X→Y` (ādēśa),
    `double X` (dvitva), `lengthen`, `shorten`, `add suffix X`, `assign class/label`.
  If one verse contains several rules, list them under `also`.
* `examples` — **every** prayōga the vṛtti/prayōga section gives, as structured derivations
  where possible (`input` parts → `output`). For examples that are only a list of
  attested words, use `{"input": null, "output": "word"}`. These are the engine's test suite,
  so correctness of these forms matters most.
* `counterexamples` — forms the sūtra explicitly rejects (`{"form": "...", "why": "..."}`).
* `quotations` — longer illustrative quotations from poets (verse text, poet if named).
* `cross_refs` — ids of sūtras this one refers to.
* `uncertain` (doubtful readings) and `source_lines` ([first, last] line in the OCR of the 2015 edition, not distributed).

## Dhātu-prakaraṇa (root list) records

The Dhātu chapter mostly lists roots with meanings in verse. Encode it as one JSON object per root:

```json
{"root": "ಅಱಿ", "meaning_kn": "ಜ್ಞಾನ", "meaning_en": "to know", "group": "ಇಕಾರಾಂತ",
 "verse": 12, "notes": "", "uncertain": [], "source_lines": [15020, 15024]}
```

Plus one ordinary sūtra record for any verse that states a rule rather than listing roots.

## Prayōgasāra (glossary appendix)

One object per entry: `{"word": "ಕನ್ನಡವಕ್ಕಿ", "meaning_kn": "ಗಿಳಿ", "meaning_en": "parrot", "uncertain": [], "source_line": 20390}`.
