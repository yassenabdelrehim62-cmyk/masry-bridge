import pytest

from app.transliterate import FRANCO_DIGITS, arabic_to_franco, franco_to_arabic


@pytest.mark.parametrize("func", [franco_to_arabic, arabic_to_franco])
def test_converters_not_implemented_yet(func):
    with pytest.raises(NotImplementedError):
        func("placeholder")


def test_franco_digits_follow_egyptian_usage():
    assert FRANCO_DIGITS["8"] == "غ"
    assert "9" not in FRANCO_DIGITS
