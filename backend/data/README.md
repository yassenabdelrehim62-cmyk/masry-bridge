# Word data

The files in this folder are licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
The rest of the repository is MIT-licensed (see `LICENSE` at the root).

Both files are adaptations of the sources below and are rebuilt from the
originals by `scripts/build_data.py`.

| File | Contents |
|---|---|
| `camel_da_top100k.tsv` | The 100,000 most frequent words in the CAMeL dialectal Arabic (DA) frequency list, one `word<TAB>count` per line |
| `unimorph_arz_forms.txt` | Every inflected form in UniMorph Egyptian Arabic, one per line |

## Changes from the originals

- Diacritics and tatweel removed.
- Spelling variants merged: أ/إ/آ → ا, ى → ي, final ة → ه. Counts of merged
  CAMeL words are summed before the top 100,000 are taken.
- UniMorph lemmas and morphological tags dropped; only the forms are kept.

## Sources

### CAMeL Arabic Frequency Lists (DA list)

- Source: https://github.com/CAMeL-Lab/Camel_Arabic_Frequency_Lists
  (release v1.0, `DA_freq_lists.tsv.zip`)
- License: CC BY-SA 4.0
- Built from the pretraining data of the CAMeLBERT models. Cite:

  Go Inoue, Bashar Alhafni, Nurpeiis Baimukan, Houda Bouamor, and Nizar Habash.
  2021. The Interplay of Variant, Size, and Task Type in Arabic Pre-trained
  Language Models. In *Proceedings of the Sixth Arabic Natural Language
  Processing Workshop*, pages 92–104, Kyiv, Ukraine (Online). Association for
  Computational Linguistics.

- Dataset citation: Salam Khalifa, Go Inoue, Bashar Alhafni, Nurpeiis
  Baimukan, Houda Bouamor, and Nizar Habash. 2021. *Camel Arabic Frequency
  Lists*.

### UniMorph Egyptian Arabic (arz)

- Source: https://github.com/unimorph/arz (file `arz`, commit `e3fd562`)
- License: CC BY-SA 3.0 Unported. CC BY-SA 3.0 allows adaptations to be
  released under a later version of the license, so the adapted file here is
  under CC BY-SA 4.0.
- Annotators: Salam Khalifa and Nizar Habash (CAMeL Lab, NYU Abu Dhabi).
  Lemmas from the Egyptian Arabic Treebank (Maamouri et al., 2014) and
  CALIMA-ARZ (Habash et al., 2012); forms generated with CAMeL Tools
  (Obeid et al., 2020).

## Rebuilding

Download the originals:

```bash
curl -LO https://github.com/CAMeL-Lab/Camel_Arabic_Frequency_Lists/releases/download/v1.0/DA_freq_lists.tsv.zip
```

```bash
curl -LO https://raw.githubusercontent.com/unimorph/arz/e3fd562845647176b8be9b8e21710732bc76d558/arz
```

Then, from `backend/`:

```bash
python -m scripts.build_data --camel DA_freq_lists.tsv.zip --unimorph arz
```

The script checks both downloads against the SHA-256 checksums of the files
the committed data was built from.
