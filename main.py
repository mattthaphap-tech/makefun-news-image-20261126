"""Deliver the finished front page to the harness output directory.

Entry: make.fun news-image-20261126 — "Thursday 26 November 2026 —
35 stories, 7 regions: Kim's nuclear push, Asia shares bounce,
Thanksgiving nor'easter". The newspaper image itself (entry.png) is
drawn by build_26nov.py; this script only delivers it. It copies
entry.png to /output/entry.png, then proves the copy is byte-identical
by comparing the file size and the SHA-256 digest of source and
destination, both computed fresh at run time.
"""

import hashlib
import os
import shutil
import sys

SOURCE = "entry.png"
OUTPUT_DIR = "/output"
TARGET = os.path.join(OUTPUT_DIR, "entry.png")
CHUNK_SIZE = 1024 * 1024


def digest_file(path):
    """Return the hex SHA-256 digest of the file at path."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def abort(message):
    """Print an error and exit non-zero."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    if not os.path.isfile(SOURCE):
        abort(f"source image not found: {SOURCE}")

    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except OSError as exc:
        abort(f"cannot create output directory {OUTPUT_DIR}: {exc}")

    try:
        shutil.copyfile(SOURCE, TARGET)
    except OSError as exc:
        abort(f"copy failed ({SOURCE} -> {TARGET}): {exc}")

    source_size = os.path.getsize(SOURCE)
    target_size = os.path.getsize(TARGET)
    if source_size != target_size:
        abort(
            f"size mismatch: source {source_size} bytes, "
            f"copy {target_size} bytes"
        )

    source_hash = digest_file(SOURCE)
    target_hash = digest_file(TARGET)
    if source_hash != target_hash:
        abort(
            f"SHA-256 mismatch: source {source_hash}, copy {target_hash}"
        )

    print(
        f"ok: {TARGET} written and verified "
        f"({target_size} bytes, sha256 {target_hash})"
    )


if __name__ == "__main__":
    main()
