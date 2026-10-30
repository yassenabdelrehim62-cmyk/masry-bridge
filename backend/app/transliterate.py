"""Conversion between Egyptian Franco-Arabic (3arabizi) and Arabic script.

Pure functions only: no I/O, no FastAPI. The API layer wraps these.

franco_to_arabic() works word by word:
1. Words in DICTIONARY are returned as-is (checked before any rule).
2. The article "el" (and fused forms like "fel", "bel") is attached to the
   next word as "ال".
3. Everything else goes through letter rules: consonants map one-to-one,
   and vowels are written or dropped depending on their position, since
   Arabic script only writes long vowels.
"""

import re

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

# Checked before any rule. Only words the rules can't get right belong here.
DICTIONARY = {
    # Pronouns
    "ana": "انا",
    "enta": "انت",
    "enty": "انتي",
    "enti": "انتي",
    "howa": "هو",
    "heya": "هي",
    "e7na": "احنا",
    "ento": "انتو",
    "homma": "هما",
    # Particles and demonstratives
    "da": "ده",
    "di": "دي",
    "dol": "دول",
    "keda": "كده",
    "ya": "يا",
    "fe": "في",
    "fi": "في",
    "mesh": "مش",
    "msh": "مش",
    "eh": "ايه",
    "leh": "ليه",
    "law": "لو",
    "elly": "اللي",
    "yalla": "يلا",
    "aywa": "ايوه",
    "la2": "لا",
    "mafeesh": "مفيش",
    "mafish": "مفيش",
    "ma3lesh": "معلش",
    # Fixed expressions
    "wallahi": "والله",
    "wallah": "والله",
    "el7amdulela": "الحمدلله",
    "el7amdulillah": "الحمدلله",
    "enharda": "النهارده",
    "ennaharda": "النهارده",
    "embare7": "امبارح",
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
    "laptop": "لابتوب",
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


def _split_units(word: str) -> list[tuple[str, str]]:
    """Split a word into ("c", consonant) and ("v", vowel run) units.

    Doubled consonants collapse to one, since Arabic script doesn't write
    gemination without a shadda.
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
        if not units or units[-1] != ("c", consonant):
            units.append(("c", consonant))
        i += len(consonant)
    return units


def _final_a(units: list[tuple[str, str]]) -> str:
    # Pronoun suffixes "-ha" (her) and "-na" (us/our) keep their alif;
    # otherwise a final "a" is most often the feminine ending ة.
    if len(units) >= 2 and units[-2][1] in ("h", "n"):
        return "ا"
    return "ة"


def _vowel(units: list[tuple[str, str]], i: int, word: str) -> str:
    vowel = units[i][1]
    vowel_indexes = [k for k, (kind, _) in enumerate(units) if kind == "v"]
    is_first = i == vowel_indexes[0]
    monosyllable = len(vowel_indexes) == 1

    if len(vowel) > 1:
        # Doubled or combined vowels ("aa", "ee", "ei", "oo", "ou") are long.
        return LONG_VOWELS[vowel[-1]]
    if i == 0:
        return "ا"
    if i == len(units) - 1:
        return _final_a(units) if vowel == "a" else LONG_VOWELS[vowel]

    following = units[i + 1 : i + 3]
    if vowel == "i":
        return "ي"
    if vowel == "a":
        # Negation "ma...sh": matza3alsh -> ماتزعلش.
        if is_first and re.fullmatch(r"ma.+sh", word) and len(word) > 5:
            return "ا"
        # Active participle pattern CaCeC (فاعل): 3amel, fahem, 3ayez.
        if is_first and len(following) == 2 and following[1] == ("v", "e"):
            return "ا"
        # Monosyllable CaC: kan, gab, gay. "aw" is a diphthong: gaw -> جو.
        if monosyllable and i + 1 == len(units) - 1 and following[0][1] != "w":
            return "ا"
        return ""
    if vowel in ("o", "u") and monosyllable and i + 1 == len(units) - 1:
        # Monosyllable CoC: yom -> يوم.
        return "و"
    # Short medial e/o/u aren't written.
    return ""


def _convert_word(word: str) -> str:
    word = word.lower()
    if word in DICTIONARY:
        return DICTIONARY[word]
    if word.startswith("el") and len(word) > 4 and word[2] not in VOWELS:
        return "ال" + _convert_word(word[2:])

    units = _split_units(word)
    out = []
    for i, (kind, text) in enumerate(units):
        if kind == "v":
            out.append(_vowel(units, i, word))
        elif text in DIGRAPHS:
            out.append(DIGRAPHS[text])
        else:
            out.append(CONSONANTS.get(text, text))
    return "".join(out)


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

        converted = _convert_word(word) if word else ""
        words.append(
            _convert_punctuation(lead) + prefix + converted + _convert_punctuation(trail)
        )
        prefix = ""
    return " ".join(words)


def arabic_to_franco(text: str) -> str:
    """Convert Arabic script to Franco-Arabic."""
    raise NotImplementedError
