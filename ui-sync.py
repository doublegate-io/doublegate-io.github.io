#!/usr/bin/env python3
"""Pin public DoubleGate UI assets into this independently deployed static site."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI_ASSETS = ROOT.parent / "doublegate-ui" / "src" / "doublegate_ui" / "assets"
LOCAL_ASSETS = ROOT / "assets"
NAMES = ("institutional.css", "logo.svg", "logo-dark.svg", "favicon-32.png", "apple-touch-icon.png")
PIN = LOCAL_ASSETS / "doublegate-ui.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    check = "--check" in sys.argv[1:]
    missing = [name for name in NAMES if not (LOCAL_ASSETS / name).is_file()]
    if missing and check:
        print("ui-sync: missing local assets: " + ", ".join(missing))
        return 1
    if not UI_ASSETS.is_dir():
        print("ui-sync: doublegate-ui checkout absent; committed pin remains deployable")
        return 0

    different = [name for name in NAMES if not (LOCAL_ASSETS / name).is_file()
                 or (UI_ASSETS / name).read_bytes() != (LOCAL_ASSETS / name).read_bytes()]
    expected = {name: digest((UI_ASSETS / name).read_bytes()) for name in NAMES}
    pin = {"source": "doublegate-ui", "assets": expected}
    pin_text = json.dumps(pin, indent=2, sort_keys=True) + "\n"
    if check:
        if different or not PIN.exists() or PIN.read_text() != pin_text:
            print("ui-sync: stale shared assets: " + ", ".join(different or [PIN.name]))
            return 1
        print("ui-sync: shared assets match doublegate-ui")
        return 0

    for name in different:
        (LOCAL_ASSETS / name).write_bytes((UI_ASSETS / name).read_bytes())
    PIN.write_text(pin_text)
    print("ui-sync: pinned " + ", ".join(NAMES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
