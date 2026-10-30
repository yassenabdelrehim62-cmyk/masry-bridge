import pytest

from app.transliterate import arabic_to_franco, franco_to_arabic


@pytest.mark.parametrize("func", [franco_to_arabic, arabic_to_franco])
def test_converters_not_implemented_yet(func):
    with pytest.raises(NotImplementedError):
        func("placeholder")
