"""Conversion between Egyptian Franco-Arabic (3arabizi) and Arabic script.

No FastAPI here: the API layer wraps these functions.

franco_to_arabic() works word by word:
1. Words in DICTIONARY are returned as-is (checked before any rule).
2. The article "el" (and fused forms like "fel", "bel") is attached to the
   next word as "ال".
3. Everything else goes through letter rules, which give a default
   spelling plus alternatives for what Franco leaves ambiguous: vowels
   written or dropped, ت/ط, س/ص, ز/ظ, and doubled letters. Each candidate
   is ranked by how often it occurs in Egyptian/dialectal text, minus a
   cost for each rule it overrides; UniMorph arz breaks ties.

The functions here are str -> str; the word data is read once from
backend/data/ (see app/lexicon.py).
"""

import itertools
import math
import re

from app.lexicon import frequency, is_egyptian_form

# Digits commonly used in Egyptian Franco for sounds Latin letters lack.
# "2" is both ء and ق in Egyptian usage; ق is far more common in everyday
# words ("2al", "wa2t"), so it is the default and hamza words go in
# DICTIONARY. "9" is not used in Egyptian Franco and is deliberately left
# unmapped (kept as a literal digit).
FRANCO_DIGITS = {
    "2": "ق",
    "3": "ع",
    "5": "خ",
    "7": "ح",
    "8": "غ",
}

DIGRAPHS = {
    "sh": "ش",
    "kh": "خ",
    "gh": "غ",
}

CONSONANTS = {
    "b": "ب",
    "c": "ك",
    "d": "د",
    "f": "ف",
    "g": "ج",
    "h": "ه",
    "j": "ج",
    "k": "ك",
    "l": "ل",
    "m": "م",
    "n": "ن",
    "p": "ب",
    "q": "ق",
    "r": "ر",
    "s": "س",
    "t": "ت",
    "v": "ف",
    "w": "و",
    "x": "كس",
    "y": "ي",
    "z": "ز",
    **FRANCO_DIGITS,
}

# Franco writes these letters the same way; frequency alone picks.
EMPHATICS = {
    "t": "ط",
    "s": "ص",
    "z": "ظ",
}

VOWELS = set("aeiou")

LONG_VOWELS = {
    "a": "ا",
    "e": "ي",
    "i": "ي",
    "o": "و",
    "u": "و",
}

PUNCTUATION = {
    "?": "؟",
    ",": "،",
    ";": "؛",
}

# Checked before any rule. Only true exceptions belong here: words that
# candidate ranking gets wrong (ق written without a 2, hamza words, final
# ه that isn't ة, loanwords, fixed expressions).
DICTIONARY = {
    # Pronouns
    "enta": "انت",
    "howa": "هو",
    "heya": "هي",
    # Particles and demonstratives
    "da": "ده",
    "keda": "كده",
    "eh": "ايه",
    "leh": "ليه",
    "elly": "اللي",
    "yalla": "يلا",
    "aywa": "ايوه",
    "la2": "لا",
    "mafeesh": "مفيش",
    "mafish": "مفيش",
    # Fixed expressions
    "wallahi": "والله",
    "el7amdulela": "الحمدلله",
    "enharda": "النهارده",
    "ennaharda": "النهارده",
    # Adverbs ending in tanween (-an written as ا)
    "shokran": "شكرا",
    "gedan": "جدا",
    "tab3an": "طبعا",
    "aslan": "اصلا",
    "abadan": "ابدا",
    "tamaman": "تماما",
    "ahlan": "اهلا",
    "3afwan": "عفوا",
    # 2 as hamza (ء) instead of the default ق
    "so2al": "سؤال",
    "mas2ala": "مسألة",
    "ra2y": "رأي",
    "mas2ool": "مسؤول",
    # Cairene ق pronounced as a glottal stop and written without a 2
    "ahwa": "قهوة",
    "alb": "قلب",
    # English loanwords
    "meeting": "ميتنج",
    "mobile": "موبايل",
    "computer": "كمبيوتر",
    "email": "ايميل",
    "online": "اونلاين",
    "video": "فيديو",
}

# Standalone tokens that attach "ال" (with any fused preposition) to the
# next word: "el sa3a" -> الساعة, "fel tare2" -> في الطريق.
ARTICLES = {
    "el": "ال",
    "il": "ال",
    "al": "ال",
    "fel": "في ال",
    "fil": "في ال",
    "bel": "بال",
    "lel": "لل",
    "wel": "وال",
}

# Sun-letter spellings of the article: "es sa3a", "en nas".
SUN_ARTICLE = re.compile(r"e(sh|[stdrzn])")

TOKEN = re.compile(r"^(\W*)(.*?)(\W*)$")

# Overriding a rule costs log-frequency: a candidate that breaks a rule must
# be this many times more frequent than one that follows it. Targeted rules
# (the فاعل pattern, monosyllables, negation, -ha/-na) are more reliable than
# the catch-all defaults (drop short vowels, final a -> ة), so they cost more.
TARGETED_RULE_COST = math.log(10)
DEFAULT_RULE_COST = math.log(2)

# Words with more candidates than this keep the default spelling.
MAX_CANDIDATES = 4096

Options = list[tuple[str, float]]


def _split_units(word: str) -> list[tuple[str, str]]:
    """Split a word into ("c", consonant), ("cc", doubled consonant) and
    ("v", vowel run) units.
    """
    units: list[tuple[str, str]] = []
    i = 0
    while i < len(word):
        if word[i] in VOWELS:
            j = i
            while j < len(word) and word[j] in VOWELS:
                j += 1
            units.append(("v", word[i:j]))
            i = j
            continue
        consonant = word[i : i + 2] if word[i : i + 2] in DIGRAPHS else word[i]
        if units and units[-1] == ("c", consonant):
            units[-1] = ("cc", consonant)
        elif not units or units[-1] != ("cc", consonant):
            units.append(("c", consonant))
        i += len(consonant)
    return units


def _final_a(units: list[tuple[str, str]]) -> Options:
    # Pronoun suffixes "-ha" (her) and "-na" (us/our) keep their alif;
    # otherwise a final "a" is most often the feminine ending ة.
    if len(units) >= 2 and units[-2][1] in ("h", "n"):
        return [("ا", 0), ("ة", TARGETED_RULE_COST)]
    return [("ة", 0), ("ا", DEFAULT_RULE_COST)]


def _targeted(spelling: str) -> Options:
    return [(spelling, 0), ("", TARGETED_RULE_COST)]


def _default_dropped(spelling: str) -> Options:
    return [("", 0), (spelling, DEFAULT_RULE_COST)]


def _vowel_options(units: list[tuple[str, str]], i: int, word: str) -> Options:
    """Spellings for the vowel at units[i], the rule's default first."""
    vowel = units[i][1]
    vowel_indexes = [k for k, (kind, _) in enumerate(units) if kind == "v"]
    is_first = i == vowel_indexes[0]
    monosyllable = len(vowel_indexes) == 1

    if len(vowel) > 1:
        # Doubled or combined vowels ("aa", "ee", "ei", "oo", "ou") are long.
        return [(LONG_VOWELS[vowel[-1]], 0)]
    if i == 0:
        return [("ا", 0)]
    if i == len(units) - 1:
        return _final_a(units) if vowel == "a" else [(LONG_VOWELS[vowel], 0)]

    following = units[i + 1 : i + 3]
    ends_after_next = i + 1 == len(units) - 1
    if vowel == "i":
        return [("ي", 0), ("", DEFAULT_RULE_COST)]
    if vowel == "a":
        # Negation "ma...sh": matza3alsh -> ماتزعلش.
        if is_first and re.fullmatch(r"ma.+sh", word) and len(word) > 5:
            return _targeted("ا")
        # Active participle pattern CaCeC (فاعل): 3amel, fahem, 3ayez.
        if is_first and len(following) == 2 and following[1] == ("v", "e"):
            return _targeted("ا")
        # Monosyllable CaC: kan, gab, gay. "aw" is a diphthong: gaw -> جو.
        if monosyllable and ends_after_next and following[0][1] != "w":
            return _targeted("ا")
        return _default_dropped("ا")
    if vowel in ("o", "u") and monosyllable and ends_after_next:
        # Monosyllable CoC: yom -> يوم.
        return _targeted("و")
    # Short medial e/o/u aren't written by default.
    return _default_dropped(LONG_VOWELS[vowel])


def _consonant_options(kind: str, consonant: str) -> Options:
    letter = DIGRAPHS.get(consonant) or CONSONANTS.get(consonant, consonant)
    letters = [letter]
    if consonant in EMPHATICS:
        letters.append(EMPHATICS[consonant])
    options = [(letter, 0) for letter in letters]
    if kind == "cc":
        # Arabic script usually doesn't write a doubled letter (shadda),
        # except across word parts: "elly" -> اللي.
        options += [(letter * 2, DEFAULT_RULE_COST) for letter in letters]
    return options


def _candidates(word: str) -> list[tuple[str, float]]:
    """Every spelling of the word with the total cost of the rules it breaks.

    The first candidate is the default spelling.
    """
    units = _split_units(word)
    options = [
        _vowel_options(units, i, word) if kind == "v" else _consonant_options(kind, text)
        for i, (kind, text) in enumerate(units)
    ]
    if math.prod(len(unit_options) for unit_options in options) > MAX_CANDIDATES:
        options = [unit_options[:1] for unit_options in options]
    return [
        ("".join(spelling for spelling, _ in choice), sum(cost for _, cost in choice))
        for choice in itertools.product(*options)
    ]


def _rank(candidates: list[tuple[str, float]], context: str) -> str:
    """Pick the best candidate.

    The score is log-frequency minus the cost of broken rules. Frequency is
    looked up with the article attached when there is one ("ال" + word),
    falling back to the bare word if no candidate occurs that way. Unseen
    candidates fall back to UniMorph arz, then to the lowest cost.
    """
    with_context = [frequency(context + spelling) for spelling, _ in candidates]
    counts = (
        with_context
        if context and any(with_context)
        else [frequency(spelling) for spelling, _ in candidates]
    )

    def score(index: int) -> tuple[float, bool, float]:
        spelling, cost = candidates[index]
        log_frequency = math.log(counts[index]) - cost if counts[index] else -math.inf
        return (log_frequency, is_egyptian_form(context + spelling), -cost)

    # max() keeps the first of equal scores, and the default comes first.
    return candidates[max(range(len(candidates)), key=score)][0]


def _convert_word(word: str, article: str = "") -> str:
    """Convert one word. `article` is the "ال" attached in front, if any."""
    word = word.lower()
    if word in DICTIONARY:
        return DICTIONARY[word]
    if word.startswith("el") and len(word) > 4 and word[2] not in VOWELS:
        return "ال" + _convert_word(word[2:], article="ال")
    return _rank(_candidates(word), article)


def _convert_punctuation(text: str) -> str:
    return "".join(PUNCTUATION.get(char, char) for char in text)


def franco_to_arabic(text: str) -> str:
    """Convert Franco-Arabic text (e.g. "3amel eh") to Arabic script."""
    words = []
    prefix = ""
    chunks = text.split()
    for index, chunk in enumerate(chunks):
        lead, word, trail = TOKEN.match(chunk).groups()
        lowered = word.lower()
        next_word = chunks[index + 1].lower() if index + 1 < len(chunks) else ""

        if not trail and next_word:
            sun = SUN_ARTICLE.fullmatch(lowered)
            if lowered in ARTICLES:
                prefix = ARTICLES[lowered]
                continue
            if sun and next_word.startswith(sun.group(1)):
                prefix = "ال"
                continue

        article = "ال" if prefix.endswith("ال") else ""
        converted = _convert_word(word, article) if word else ""
        words.append(
            _convert_punctuation(lead) + prefix + converted + _convert_punctuation(trail)
        )
        prefix = ""
    return " ".join(words)


def arabic_to_franco(text: str) -> str:
    """Convert Arabic script to Franco-Arabic."""
    raise NotImplementedError
