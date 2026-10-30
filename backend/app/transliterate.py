"""Conversion between Egyptian Franco-Arabic (3arabizi) and Arabic script.

Pure functions only: no I/O, no FastAPI. The API layer wraps these.
"""

# Digits commonly used in Egyptian Franco for sounds Latin letters lack.
# Starting point only; the full mapping is still to be designed.
FRANCO_DIGITS = {
    "2": "ء",
    "3": "ع",
    "5": "خ",
    "7": "ح",
}


def franco_to_arabic(text: str) -> str:
    """Convert Franco-Arabic text (e.g. "3amel eh") to Arabic script."""
    raise NotImplementedError


def arabic_to_franco(text: str) -> str:
    """Convert Arabic script to Franco-Arabic."""
    raise NotImplementedError
