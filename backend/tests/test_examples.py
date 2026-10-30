from pathlib import Path

import pytest

from app.transliterate import franco_to_arabic

EXAMPLES_FILE = Path(__file__).parent / "examples.txt"

# Examples the converter doesn't handle yet. Strict xfail: when one of these
# starts passing, the test fails so it gets removed from this set.
KNOWN_FAILURES = {
    "mesh fahem 7aga",
    "yalla bena nenzel",
    "3ayez a3raf el sa3a kam",
    "el gaw 7ar awy enharda",
    "5alas 5aleha bokra",
    "shokran ya basha",
    "e7na msafreen yom el 5ames",
    "el 3arabeya 3otlet tany",
    "el net bayez 3andy",
    "ana gay fel tare2",
    "2oly law 3ayez 7aga",
    "el emte7an kan sa3b awy",
    "sa7by gab laptop gedeed",
    "tab3an ya 3am",
    "eshta keda",
}


def load_examples():
    examples = []
    for line in EXAMPLES_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        franco, arabic = (part.strip() for part in line.split("|"))
        marks = (
            [pytest.mark.xfail(strict=True, reason="not handled yet")]
            if franco in KNOWN_FAILURES
            else []
        )
        examples.append(pytest.param(franco, arabic, id=franco, marks=marks))
    return examples


@pytest.mark.parametrize(("franco", "arabic"), load_examples())
def test_example(franco, arabic):
    assert franco_to_arabic(franco) == arabic


def test_known_failures_exist_in_examples():
    francos = {param.values[0] for param in load_examples()}
    assert KNOWN_FAILURES <= francos
