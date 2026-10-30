"""Word frequencies and known Egyptian word forms, loaded from backend/data/.

The files are built by scripts/build_data.py; see data/README.md for sources
and licenses. They are read once, on first use.
"""

import re
from functools import cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FREQUENCY_FILE = DATA_DIR / "camel_da_top100k.tsv"
FORMS_FILE = DATA_DIR / "unimorph_arz_forms.txt"

DIACRITICS = re.compile("[ً-ْٰـ]")

# Spelling variants that are used interchangeably in informal writing:
# final ة written as ه, ى as ي, and hamza seats on alif dropped.
VARIANTS = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي"})


def normalize(word: str) -> str:
    """Map a word to the form used as a key in the data files."""
    word = DIACRITICS.sub("", word).translate(VARIANTS)
    if word.endswith("ة"):
        word = word[:-1] + "ه"
    return word


@cache
def _frequencies() -> dict[str, int]:
    frequencies = {}
    with FREQUENCY_FILE.open(encoding="utf-8") as file:
        for line in file:
            word, count = line.rstrip("\n").split("\t")
            frequencies[word] = int(count)
    return frequencies


@cache
def _forms() -> frozenset[str]:
    return frozenset(FORMS_FILE.read_text(encoding="utf-8").split())


def frequency(word: str) -> int:
    """How often the word occurs in the CAMeL dialectal corpus (0 if unseen)."""
    return _frequencies().get(normalize(word), 0)


def is_egyptian_form(word: str) -> bool:
    """Whether the word is an inflected form in UniMorph arz."""
    return normalize(word) in _forms()
