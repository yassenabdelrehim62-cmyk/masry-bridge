import pytest

from app.lexicon import normalize
from app.transliterate import FRANCO_DIGITS, arabic_to_franco, franco_to_arabic


def test_arabic_to_franco_not_implemented_yet():
    with pytest.raises(NotImplementedError):
        arabic_to_franco("placeholder")


def test_franco_digits_follow_egyptian_usage():
    assert FRANCO_DIGITS["2"] == "ق"
    assert FRANCO_DIGITS["8"] == "غ"
    assert "9" not in FRANCO_DIGITS


@pytest.mark.parametrize(
    ("franco", "arabic"),
    [
        ("so2al", "سؤال"),
        ("mas2ala", "مسألة"),
        ("ra2y", "رأي"),
    ],
)
def test_hamza_words_come_from_dictionary(franco, arabic):
    assert franco_to_arabic(franco) == arabic


@pytest.mark.parametrize(
    ("franco", "arabic"),
    [
        ("8ayeb", "غايب"),
        ("ana 9", "انا 9"),
        ("en nas", "الناس"),
        ("bel 3arabeya", "بالعربية"),
        ("lel bet", "للبيت"),
    ],
)
def test_letter_and_article_rules(franco, arabic):
    assert franco_to_arabic(franco) == arabic


def test_lexicon_normalizes_spelling_variants():
    assert normalize("حاجة") == "حاجه"
    assert normalize("أنا") == "انا"
    assert normalize("على") == "علي"
    assert normalize("كُوَيِّس") == "كويس"
