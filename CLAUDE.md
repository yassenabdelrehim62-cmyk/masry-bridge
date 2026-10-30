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
    │   └── transliterate.py  # core conversion logic (pure functions)
    └── tests/
        └── test_transliterate.py
```

A `frontend/` directory will sit next to `backend/` once the React app is started.

## Conventions

- Keep the transliteration logic in `app/transliterate.py` as pure functions
  (`str -> str`) with no FastAPI imports. API routes wrap these functions; they
  don't contain conversion logic themselves.
- Every change to the conversion rules comes with test cases, ideally real
  Egyptian Franco examples with their expected Arabic output.
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
