#!/usr/bin/env python3
"""Static, version-independent checks for the curated distribution examples.

This does not claim AMOS / WinUAE runtime success. The existing tests in
tests/ remain untouched and continue to provide the historical evidence.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_ap20 import inspect, parse
from validate_ilbm import inspect as inspect_ilbm, decode as decode_ilbm

EXAMPLES = ("screen", "picture", "blitter", "copper", "mouse", "collide")
EXAMPLE_DIR = ROOT / "examples"
AP20_NAME = re.compile(r"\bAga\s+[A-Za-z]+(?:\s+[A-Za-z]+)?")
FUNCTION_BARE = re.compile(
    r"^\s*Aga\s+(?:"
    r"Copper\s+(?:Clear|Wait|Move|End|On|Off)"
    r"|Mouse\s+(?:X|Y|Buttons|Pressed|Released)"
    r"|Rect\s+Overlap"
    r"|Double\s+Buffer|Swap|Pic\s+Info|Iff\s+Load"
    r"|Wait\s+Key|Key|Detect|Demo"
    r")\b", re.IGNORECASE,
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def main() -> None:
    extension = inspect(parse((ROOT / "dist/AMOSPro_AGA.Lib").read_bytes()))
    require(not extension["issues"], "Invalid current AP20 library")
    valid_commands = {
        item["name"].casefold() for item in extension["tokens"]
        if item["name"].casefold().startswith("aga ")
    }
    actual = {p.name for p in EXAMPLE_DIR.glob("*.asc")}
    expected = {f"{name}.asc" for name in EXAMPLES}
    require(actual == expected, f"Unexpected example set: {actual ^ expected}")
    for name in EXAMPLES:
        source = EXAMPLE_DIR / f"{name}.asc"
        text = source.read_bytes().decode("ascii")
        require("\r" not in text, f"Nonstandard line endings: {source.name}")
        require(text.endswith("\nEnd\n"), f"No final End: {source.name}")
        require("Aga Screen Close" in text and "Amos To Front" in text,
                f"Missing screen cleanup: {source.name}")
        lines = [line for line in text.splitlines()
                 if line.strip() and not line.lstrip().startswith("'")]
        require(sum(bool(re.match(r"^\s*If\b", line)) for line in lines)
                == sum(bool(re.match(r"^\s*End If\b", line)) for line in lines),
                f"Unbalanced If/End If in {source.name}")
        require(sum(bool(re.match(r"^\s*For\b", line)) for line in lines)
                == sum(bool(re.match(r"^\s*Next\b", line)) for line in lines),
                f"Unbalanced For/Next in {source.name}")
        require(not any(re.search(r"\bThen\b", line) for line in lines),
                f"AMOS If must not use Then: {source.name}")
        require(not any(FUNCTION_BARE.match(line) for line in lines),
                f"Integer-returning AP20 function used as instruction: {source.name}")
        used = {match.group(0).casefold()
                for line in lines for match in AP20_NAME.finditer(line)}
        require(used <= valid_commands,
                f"Unknown AP20 calls in {source.name}: {used - valid_commands}")
        require(bool(used), f"No AGA calls in {source.name}")

    for name in ("picture", "blitter", "collide"):
        text = (EXAMPLE_DIR / f"{name}.asc").read_text("ascii")
        require('Fsel$("**")' in text and "Aga Pic Info" in text,
                f"{name}.asc must offer file selection and verify dimensions")
    collide = (EXAMPLE_DIR / "collide.asc").read_text("ascii")
    require(all(call in collide for call in (
        "Aga Rect Overlap", "Aga Mouse X", "Aga Mouse Y",
        "Aga Mouse Pressed", "Aga Blit Clear(0,0,320,256)",
        "Aga Blit Fill", "Aga Swap", "Aga Wait Vbl")),
        "collide.asc must demonstrate R25 AABB, mouse and per-frame redraw/VBL")
    original = (ROOT / "iff-TEST/AGA_TESTCARD_320x256_256C.iff").read_bytes()
    demo = (EXAMPLE_DIR / "demo.iff").read_bytes()
    require(hashlib.sha256(original).digest() == hashlib.sha256(demo).digest()
            and original == demo, "Packaged demo.iff differs from original test card")
    meta, body = inspect_ilbm(demo)
    planes, consumed = decode_ilbm(meta, body)
    require((meta["width"], meta["height"], meta["depth"], meta["cmap_entries"],
             meta["camg"]) == (320, 256, 8, 256, 0x00021000),
            "Bundled IFF is not the documented 320x256x256 PAL test card")
    require(len(planes) == 8 and consumed == len(body), "Incomplete IFF decoding")

    for p in ("README.md", "README.fr.md", "INSTALL.md", "INSTALL.fr.md"):
        require((EXAMPLE_DIR / p).is_file() if p.startswith("README")
                else (ROOT / p).is_file(), f"Missing documentation: {p}")
    for p in ("README.md", "README.fr.md"):
        text = (ROOT / p).read_text("utf-8")
        require("examples/README" in text and "INSTALL" in text,
                f"Missing distribution links in root {p}")
    print(f"Distribution examples PASS: {len(EXAMPLES)} distinct ASCII demos, "
          "all AP20 calls recognized, cleanup checks and matching 320x256x256 ILBM. "
          "AMOS/WinUAE execution still required.")


if __name__ == "__main__":
    main()
