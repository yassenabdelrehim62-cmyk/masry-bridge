from pathlib import Path

import pytest

from app.transliterate import franco_to_arabic

EXAMPLES_FILE = Path(__file__).parent / "examples.txt"


def load_examples():
    examples = []
    for line in EXAMPLES_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        franco, arabic = (part.strip() for part in line.split("|"))
        examples.append(pytest.param(franco, arabic, id=franco))
    return examples


@pytest.mark.parametrize(("franco", "arabic"), load_examples())
def test_example(franco, arabic):
    assert franco_to_arabic(franco) == arabic
