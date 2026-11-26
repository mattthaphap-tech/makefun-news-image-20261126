"""Hand the finished front page to the harness.

This entry is the make.fun news-image-20261126 front page:
"Thursday 26 November 2026 — 35 stories, 7 regions: Kim's nuclear push,
Asia shares bounce, Thanksgiving nor'easter". The picture itself is drawn
by build_26nov.py; this module only moves the finished file into place.
It copies entry.png from the repository root into /output/entry.png and
then proves the copy is exact: the byte count and the SHA-256 digest of
the source and the destination are computed fresh and must match, or the
run stops with an error instead of handing over a bad file.
"""

import hashlib
import os
import shutil
import sys

SOURCE = "entry.png"
OUTPUT_DIR = "/output"
TARGET = os.path.join(OUTPUT_DIR, "entry.png")
CHUNK_SIZE = 1024 * 1024


def sha256_of(path):
    """Hex SHA-256 digest of the file at path, read in chunks."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def fail(message):
    """Report a fatal problem on stderr and stop with a non-zero exit."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    if not os.path.isfile(SOURCE):
        fail(f"source image not found: {SOURCE}")

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except OSError as exc:
        fail(f"cannot create output directory {OUTPUT_DIR}: {exc}")

    try:
        shutil.copyfile(SOURCE, TARGET)
    except OSError as exc:
        fail(f"copy failed ({SOURCE} -> {TARGET}): {exc}")

    source_size = os.path.getsize(SOURCE)
    target_size = os.path.getsize(TARGET)
    if source_size != target_size:
        fail(
            f"size mismatch: source {source_size} bytes, "
            f"copy {target_size} bytes"
        )

    source_hash = sha256_of(SOURCE)
    target_hash = sha256_of(TARGET)
    if source_hash != target_hash:
        fail(
            f"SHA-256 mismatch: source {source_hash}, copy {target_hash}"
        )

    print(
        f"ok: {TARGET} written and verified "
        f"({target_size} bytes, sha256 {target_hash})"
    )


if __name__ == "__main__":
    main()
