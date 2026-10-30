"""Rebuild the files in backend/data/ from the original downloads.

Run from backend/:

    python -m scripts.build_data --camel PATH/DA_freq_lists.tsv.zip --unimorph PATH/arz

See data/README.md for where to download the originals.
"""

import argparse
import hashlib
import io
import sys
import zipfile
from collections import Counter
from pathlib import Path

from app.lexicon import FORMS_FILE, FREQUENCY_FILE, normalize

# Checksums of the originals the committed data files were built from.
CAMEL_SHA256 = "7684ad364cae59f23a917424b96377a188e5db8ced1d1a71bac1f3049ff7e0e5"
UNIMORPH_SHA256 = "971457a56dc9a67d5bdc04aae14fa0a0aeb18f3360e15023acbc43b682a4210a"

CAMEL_MEMBER = "DA_freq_lists.tsv"
TOP_WORDS = 100_000


def check_sha256(path: Path, expected: str) -> None:
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        sys.exit(f"{path}: sha256 {actual} does not match expected {expected}")


def build_frequencies(camel_zip: Path) -> None:
    # Spelling variants are merged before ranking, so the top list is
    # counted over normalized words.
    counts: Counter[str] = Counter()
    with zipfile.ZipFile(camel_zip) as archive, archive.open(CAMEL_MEMBER) as raw:
        for line in io.TextIOWrapper(raw, encoding="utf-8"):
            word, count = line.rstrip("\n").split("\t")
            counts[normalize(word)] += int(count)
    with FREQUENCY_FILE.open("w", encoding="utf-8") as file:
        for word, count in counts.most_common(TOP_WORDS):
            file.write(f"{word}\t{count}\n")


def build_forms(unimorph: Path) -> None:
    forms = set()
    for line in unimorph.read_text(encoding="utf-8").splitlines():
        if line.strip():
            forms.add(normalize(line.split("\t")[1]))
    FORMS_FILE.write_text("\n".join(sorted(forms)) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--camel", type=Path, required=True, help="DA_freq_lists.tsv.zip")
    parser.add_argument("--unimorph", type=Path, required=True, help="the arz file")
    args = parser.parse_args()

    check_sha256(args.camel, CAMEL_SHA256)
    check_sha256(args.unimorph, UNIMORPH_SHA256)
    build_frequencies(args.camel)
    build_forms(args.unimorph)
    print(f"wrote {FREQUENCY_FILE} and {FORMS_FILE}")


if __name__ == "__main__":
    main()
