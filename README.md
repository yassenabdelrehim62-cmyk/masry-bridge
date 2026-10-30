# Masry Bridge

Masry Bridge converts Egyptian Franco-Arabic (3arabizi), the Latin-letter
Arabic people type in chats, into Arabic script:

```
ezayak 3amel eh          →  ازيك عامل ايه
el emte7an kan sa3b awy  →  الامتحان كان صعب اوي
```

It will become a web app and API. So far the Franco → Arabic converter is
built as a Python library. The FastAPI routes, Arabic → Franco conversion and
the React frontend are still to come.

## How it works

Franco is ambiguous: it doesn't say whether a vowel is long or short, or
whether `t` is ت or ط. Each word is converted in three steps (see
`backend/app/transliterate.py`):

1. **Dictionary.** A small list of true exceptions is checked first, such
   as `ahwa` → قهوة (the ق is not written in Franco), hamza words like
   `so2al` → سؤال, and English loanwords like `meeting` → ميتنج.
2. **Letter rules.** Consonants and Egyptian Franco digits map to letters
   (`3` → ع, `7` → ح, `2` → ق, `8` → غ; `9` is left as a digit). The article
   `el` (also `fel`, `bel`, `lel`, `wel`) attaches to the next word as ال.
   Vowel rules give a default spelling: for example the فاعل pattern
   (`3amel` → عامل), one-syllable words (`kan` → كان) and dropped short
   vowels.
3. **Candidate ranking.** For each ambiguous spot the rules also give
   alternatives: vowel written or dropped, ت/ط, س/ص, ز/ظ, a doubled letter
   written once or twice, and final `-an` as tanween (`shokran` → شكرا).
   Every candidate is scored by how often it occurs in dialectal Arabic
   text, minus a cost for each rule it overrides. A candidate breaking a
   targeted rule must be 10× more frequent to win; breaking a catch-all
   default costs 2×; ت/ط, س/ص and ز/ظ cost nothing, since Franco never
   distinguishes them. UniMorph Egyptian Arabic breaks ties between
   candidates the frequency list has never seen.

## Accuracy

**21 of 28** sentences in the development set (`backend/tests/examples.txt`)
come out exactly right. The rules and costs were designed while looking at
this set, so expect lower accuracy on new text; a separate held-out set is
planned for a fair number.

Known limitations, from the 7 sentences that still fail:

- **A more frequent wrong word wins.** بنا beats بينا (`bena`), and كم beats
  كام (`kam`).
- **Doubled consonants aren't written in Franco.** `7ar` (7arr) gives حار
  instead of حر, and `3am` gives عام ("year") instead of عم.
- **Near ties.** خلها narrowly beats خليها (`5aleha`).
- **Vowels Franco writes differently.** `5ames` → خميس needs `a` to become
  ي, which isn't a candidate.
- **ة vs ه.** The frequency data merges the two, so ranking can't choose
  between them. A final `a` is written ة, and words with a real ه (ده,
  كده) are in the dictionary. `eshta` comes out as اشطة, not اشطا.

## Running the tests

From `backend/` (Python 3.11+):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Each line of `tests/examples.txt` is one test. Sentences the converter
doesn't handle yet are listed in `KNOWN_FAILURES` in
`tests/test_examples.py` and marked as strict expected failures, so the
suite stays green and reports any that start passing.

## Project layout

```
backend/
├── app/
│   ├── transliterate.py  # conversion: dictionary, letter rules, ranking
│   └── lexicon.py        # loads the word data
├── data/                 # word frequencies and Egyptian word forms
├── scripts/
│   └── build_data.py     # rebuilds data/ from the original downloads
└── tests/
```

## Data credits

The word data in `backend/data/` is adapted from:

- **CAMeL Arabic Frequency Lists** (dialectal Arabic list), CAMeL Lab,
  NYU Abu Dhabi, CC BY-SA 4.0. Go Inoue, Bashar Alhafni, Nurpeiis Baimukan,
  Houda Bouamor, and Nizar Habash. 2021. *The Interplay of Variant, Size, and
  Task Type in Arabic Pre-trained Language Models.* WANLP 2021.
- **UniMorph Egyptian Arabic (arz)**, Salam Khalifa and Nizar Habash,
  CC BY-SA 3.0.

Details, the changes made, and rebuild steps are in
[`backend/data/README.md`](backend/data/README.md).

## License

The code is under the [MIT License](LICENSE). The data in `backend/data/` is
under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
