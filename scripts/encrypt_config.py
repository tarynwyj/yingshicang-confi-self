#!/usr/bin/env python3
"""Create a Base64 representation of a JSON configuration.

Base64 is encoding, not encryption. Do not use it to hide passwords or tokens.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Encode a JSON configuration as Base64")
    parser.add_argument("input", type=Path, help="input JSON file")
    parser.add_argument("--output", type=Path, default=Path("config.base64.txt"))
    args = parser.parse_args()

    raw = args.input.read_bytes()
    json.loads(raw.decode("utf-8"))
    args.output.write_text(base64.b64encode(raw).decode("ascii") + "\n", encoding="ascii")
    print(f"Wrote {args.output}. Base64 does not protect secrets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
