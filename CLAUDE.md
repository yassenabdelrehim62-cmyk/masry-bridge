# Masry Bridge

A web app + API that converts Egyptian Franco-Arabic (3arabizi, e.g. `3amel eh?`)
to Arabic script (`عامل ايه؟`) and back.

## Stack

- **Backend:** Python 3.11+, FastAPI, served with Uvicorn
- **Tests:** pytest
- **Frontend:** React (planned, not started; do not scaffold it until asked)

## Folder structure

```
masry-bridge/
├── CLAUDE.md
├── README.md
└── backend/
    ├── pyproject.toml        # pytest config
    ├── requirements.txt      # runtime dependencies
    ├── requirements-dev.txt  # runtime + test dependencies
    ├── app/
    │   ├── transliterate.py  # core conversion logic (str -> str functions)
    │   └── lexicon.py        # loads word frequencies / Egyptian forms from data/
    ├── data/                 # word data, CC BY-SA 4.0 (see data/README.md)
    ├── scripts/
    │   └── build_data.py     # rebuilds data/ from the original downloads
    └── tests/
        ├── examples.txt      # Franco | Arabic reference pairs, one per line
        ├── test_examples.py  # one parametrized test per line of examples.txt
        └── test_transliterate.py
```

A `frontend/` directory will sit next to `backend/` once the React app is started.

## Conventions

- Keep the transliteration logic in `app/transliterate.py` as `str -> str`
  functions with no FastAPI imports. API routes wrap these functions; they
  don't contain conversion logic themselves. The only I/O is reading the
  files in `data/` once, through `app/lexicon.py`.
- Franco -> Arabic works by generating candidate spellings from letter rules
  and ranking them by frequency. `DICTIONARY` is for true exceptions only:
  add a word there only when ranking gets it wrong, not because it's common.
- The code is MIT; `data/` is CC BY-SA 4.0. Don't add data without checking
  its license allows redistribution, and credit it in `data/README.md`.
- Every change to the conversion rules comes with test cases, ideally real
  Egyptian Franco examples with their expected Arabic output.
- `tests/examples.txt` is the tuning set. Examples the converter doesn't
  handle yet are listed in `KNOWN_FAILURES` in `tests/test_examples.py`
  (strict xfail); remove an entry when it starts passing.
- Egyptian usage is the target, not MSA or other dialects (for example, the
  digit mappings follow Egyptian conventions).

## Setup and running tests

All commands run from `backend/`:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```
