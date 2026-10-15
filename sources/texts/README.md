# Pampa, *Vikramārjunavijaya* (Pampa Bhārata, 941 CE): source texts

Prepared 2026-10-15 for computational grammatical analysis (Old Kannada / Haḷagannaḍa).

## Files

| file | content |
|---|---|
| `pampa_bharata_asvasa1.txt` | **Clean, collated verse text of āśvāsa 1, all 149 verses** (1.1–1.149). One verse per block, `## 1.N` header, blank line between verses. |
| `pampa_bharata_asvasa1_meta.tsv` | Per verse: metre label as printed (ಉ, ಚಂ, ಕಂ …), metre name, number and kind of corrections, whether it contains `[?]`. |
| `pampa_bharata_asvasa1_corrections.tsv` | All 119 changes made to the Wikisource text (verse, kind, Wikisource reading, adopted reading). Line breaks inside a reading are shown as ` / `. |
| `pampa_bharata_asvasa2_uncollated.txt` | Verse text of āśvāsa 2 (2.1–2.98), extracted automatically from Wikisource. **Not collated or corrected.** Same format. |

## Sources

1. **Kannada Wikisource**, a typed transcription. This is the base text.
   - https://kn.wikisource.org/wiki/ಪಂಪಭಾರತ_ಪ್ರಥಮಾಶ್ವಾಸಂ (revision 278603, 2025-03-28)
   - https://kn.wikisource.org/wiki/ಪಂಪಭಾರತ_ದ್ವಿತೀಯಾಶ್ವಾಸಂ (revision 178472, 2019-03-15)
   - Index of all 14 āśvāsas: https://kn.wikisource.org/wiki/ಪಂಪಭಾರತ
   - The page names its source as "೧೯೩೧ ರ ಮುದ್ರಣ – ಪಂಪ ಭಾರತ – ವಿಕ್ರಮಾರ್ಜುನ ವಿಜಯ" (the 1931 printing). It does not name an editor. Its verse numbering and readings match the Venkatanaranappa edition below.
2. **Witness G**: *ಪಂಪ ಭಾರತಂ ಎಂಬ ವಿಕ್ರಮಾರ್ಜುನ ವಿಜಯಂ*, Kannada and Culture Department, Govt. of Karnataka, 1977 (catalogued under K. V. Puttappa). https://archive.org/details/unset0000unse_r2i1. Its OCR is good apart from ಱ and ೞ. It has a critical apparatus with variants from manuscripts ಕ ಖ ಗ ಘ ಪ, and its text, numbering and footnotes are those of the Mysore University edition. One page, verses 1.17–1.28, is missing from the OCR.
3. **Witness M**: *Pampa bhāratam emba Vikramārjuna vijayam*, part 1 (āśvāsas 1–8), Mysore University Kannada Granthamale 30, 3rd printing 1969, general editor K. V. Puttappa. The textual editor was **Bellave Venkatanaranappa** of the Karnataka Sahitya Parishat; his preface says āśvāsas 1–8 were first printed in December 1926 and revised from Rice 1898 with a newly found palm-leaf manuscript. Two scans exist: https://archive.org/details/bmshri.pampabharatamemb0000kvpu (used) and https://archive.org/details/tgs.pampabharatamvik0000drkv, which was used to check verses 1.17–1.28.
4. **Rice 1898**: *The Pampa Bharata or Vikramarjuna Vijaya*, ed. B. Lewis Rice, Bibliotheca Carnatica, Mysore Govt. Press. https://archive.org/details/india.history.resource.111026. The OCR is **unusable**: unspaced 19th-century type and heavy glyph errors (for example, verse 1 begins "ಕ್ರೀಯನರಾತಿಸಾಧನನಯೋನಿಧಿ…"). It is kept only for reference.

I also searched archive.org for "pampa bharata", "vikramarjuna vijaya", "ಪಂಪಭಾರತ" and "ವಿಕ್ರಮಾರ್ಜುನ". The other hits were Gamaka Kala Parishat audio recordings, a 1960 Mysore University print (`bmshri.vikramarjunavija0000drkv`, which has a smaller text layer), selections (*Pampa Bharata Sangraha*, *Pampa Bharata Dipike*), and modern studies. No other complete Unicode edition text turned up.

## Licence and copyright

This is not legal advice.

- Pampa's text (941 CE) is in the public domain.
- Rice 1898 is in the public domain.
- The Venkatanaranappa / Mysore University edition text was first printed in 1926, and its editor Bellave Venkatanaranappa died in 1943. Under Indian law that is life + 60 years, or 60 years from publication for institutional works, so the edited text is public domain in India. The 1969 and 1977 reprints carry "rights reserved" notices. These may cover their new matter (introductions, indexes, typesetting), but the verse text reproduced here is the 1926/1931 edition text.
- The Wikisource pages are under CC BY-SA 4.0. That licence matters mainly for the contributors' commentary, which is not included here. The files here contain only the transcribed public-domain verse text. Still, credit "Kannada Wikisource contributors" when redistributing.
- The raw Wikisource wikitext and the archive.org OCR used for collation are not distributed here.
- The files in this folder are released under CC BY-SA 4.0, with attribution to the Kannada Wikisource contributors.

## Method (āśvāsa 1)

1. **Base**: I parsed the verse lines (the `;`-prefixed lines) from the Wikisource wikitext and dropped everything else: commentary, word division, meanings, section headings and the prose *vacana* passages. Wikisource repeats verses 9–12, 32 and 146–149; the first copy was kept.
2. **Collation**: I fuzzy-aligned each verse with its counterpart in the G and M OCR, using 4-gram voting and then a difflib refinement. The similarity is usually 0.90–0.99. I then read all 149 verses side by side (W, G and M, plus the second M scan for 1.17–1.28).
3. **Correction policy**:
   - Where W differs from the printed edition in a way OCR cannot explain, and G and M agree, I adopted the edition reading. This is kind `edition` (71 cases). Examples: 1.1 ಸುಪುಷ್ಪಪಟ್ಟಮನ್ → ಸುಪುಷ್ಪವೃಷ್ಟಿಯನ್; 1.4 ರತೋತ್ಸವಂಗಳು → ರತೋತ್ಸವಂಗಳಂ; 1.15 ನೆಗೞ್ದ → ನೆಗೞ್ದಂ; 1.26 ವನಪರೀತ → ವನಧಿಪರೀತ; 1.99 ಜೇರೊಡೆಯೆ ವಿಱುವ → ಜೇವೊಡೆಯೆ ಮೀಱುವ.
   - Plain typing slips in W are kind `ws_typo` (30 cases). Examples: ನರಾಪರೋಳಿ → ನರಾಧಿಪರೋಳಿ; ಸೌಲಪ್ರಾಂಶು → ಸಾಲಪ್ರಾಂಶು; ಪೊzೞ್ದಾಜ್ಞೆ → ಪೊದೞ್ದಾಜ್ಞೆ.
   - Glosses or variant notes inside verse lines were removed (`ws_gloss`, 2 cases): 1.6 "ಬಾಳ (ಲ )ಮೃಣಾಳ" and 1.49 "ಸಮಗತ (ಸಮಧಿಗತ)". There were also 6 spacing fixes (`spacing`).
   - Where the reading stays doubtful, `[?]` follows the word (kind `doubtful`, 10 places in 9 verses: 1.4, 1.6, 1.18, 1.29, 1.35 ×2, 1.83, 1.108, 1.112, 1.115). Some of these keep W's reading even though both OCR witnesses differ, for example 1.18 ಪುಟ್ಟೆ (OCR ಪುಟ್ಟಿ). Others are choices between unclear witnesses, for example 1.112 ಕೂಡಿಯುಮಾಗಡೆ, 1.115 ಪ್ರವಿಭಾಸಿತ (W ಪ್ರವಿಭಾಷಿತ). For 1.108 ನಕ್ಕರವದ್ದಿ, the edition itself prints "(?)".
4. **ಱ and ೞ**: the OCR layers contain **no ಱ or ೞ at all**. ಱ comes out as ಅ, ಜ, ಖ, ಣ or ಆ, and ೞ as ಟ, ಬ, ಲ or ಐ. W uses both letters consistently, so W's ಱ/ೞ were kept. I changed ರ → ಱ, ಳ → ೞ or ೞ → ಳ only where the OCR clearly showed the other letter:
   - ರ → ಱ: 1.8 ಬಿಣ್ಪೊಱೆ, 1.48 ಪೊೞ್ತಱೊಳ್, 1.52 ತೋಱೆ, 1.58 ಅದಱ, 1.108 ಪೊಱೆ/ಬಾಯ್ದೆಱೆ/ನೆಱೆದ, 1.126 ಆಱದೆ, 1.135 ಮಱೆವಿನಂ, 1.143 ನೆಱೆಯದ, 1.147 ಪಱೆಗಳ
   - ೞ → ಳ: 1.5 ಕೇಳ್ದು
   - ಳ → ೞ: 1.77 ಮಾೞ್ಪೆಂ
   No other ಱ/ೞ was changed silently.
5. **Normalisation**, applied mechanically to every verse:
   - Metre labels (ಉ॥, ಚಂ॥, ಕಂ॥ …), daṇḍas (। ॥), verse numbers, ZWJ/ZWNJ and stray punctuation were removed. The metre is recorded in the meta TSV; where the edition labels only the first kanda of a run, unlabelled verses take the kanda or preceding label.
   - The edition's square-bracketed conjectural restorations, e.g. ಸಲೆ ಪೇೞ್ದ [ಕವೀಶ್ವರರಿ]ಲ್ಲ, appear without the brackets, as in W.
   - Unicode was normalised to NFC.

## Conventions and caveats for analysis

- **Each line is a metrical line (pāda) as printed, not a word boundary.** Old Kannada editions break lines mid-word, for example 1.1 ending a line with ನರೇಂದ್ರರನೊತ್ತಿಕೊಂಡುಮಾ and starting the next with ತ್ಮೀಯ. Join lines with no space before tokenising, and still expect some lines to end on a complete word. The file does not mark which is which.
- Spaces follow the edition and W, which separate words loosely. Sandhi-fused strings are left fused.
- Final consonants with virāma (ಪಯೋನಿಧಿಯೊಳ್, ಪೊನ್, ಬೇಡಿದನ್ …), ಱ and ೞ are preserved.
- The **prose (vacana) passages are not included**. The Wikisource text of āśvāsa 1 has about 70 vacana lines (a few duplicated). They exist in the Wikisource wikitext (lines starting `;ವ॥` / `;ವಚನ॥`), but Wikisource has inserted glosses in parentheses inside them, so they would need the same collation before use.
- Verse 1.58 is a *lalita ragaḷe* of 13 printed lines.
- **Āśvāsa 2** (98 verses, numbering matching G's 2.1–2.98) is uncorrected Wikisource text with parenthesised glosses stripped. Expect about one discrepancy per two verses, as in āśvāsa 1, before collation. Verse 2.61's first line was typed as a commentary line in W and was recovered.

## Quality assessment

- Wikisource base: good overall. ಱ/ೞ are consistent and the text is complete, but 77 of 149 verses needed at least one fix. Most were single-word divergences from the printed edition or typing slips, and a few changed the sense (1.1, 1.13, 1.26, 1.99, 1.112).
- After collation: I expect residual errors to be rare. They would be cases where W and both OCRs share a mistake, or ಳ/ೞ and ರ/ಱ distinctions the OCR cannot show. Open points are marked `[?]`.
- The OCR witnesses are useful only for collation. The Rice 1898 OCR is useless as text.