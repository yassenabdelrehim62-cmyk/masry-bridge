"""Conversion between Egyptian Franco-Arabic (3arabizi) and Arabic script.

Pure functions only: no I/O, no FastAPI. The API layer wraps these.
"""

# Digits commonly used in Egyptian Franco for sounds Latin letters lack.
# "2" is ambiguous: ء in some words, ق in others ("2al" -> قال), so the
# converter will need context beyond this table. "9" is not used in Egyptian
# Franco and is deliberately left unmapped (kept as a literal digit).
FRANCO_DIGITS = {
    "2": "ء",
    "3": "ع",
    "5": "خ",
    "7": "ح",
    "8": "غ",
}


def franco_to_arabic(text: str) -> str:
    """Convert Franco-Arabic text (e.g. "3amel eh") to Arabic script."""
    raise NotImplementedError


def arabic_to_franco(text: str) -> str:
    """Convert Arabic script to Franco-Arabic."""
    raise NotImplementedError
