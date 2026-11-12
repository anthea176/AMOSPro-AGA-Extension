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

EXAMPLES = ("screen", "picture", "blitter", "copper", "mouse", "collide", "show", "fade_to_bank_r33", "font_bank_r38", "m15_2d_cursor")
EXAMPLE_DIR = ROOT / "examples"
AP20_NAME = re.compile(r"\bAga\s+[A-Za-z]+(?:\s+[A-Za-z]+){0,3}")
FUNCTION_BARE = re.compile(
    r"^\s*Aga\s+(?:"
    r"Copper\s+(?:Clear|Wait|Move|End|On|Off)"
    r"|Mouse\s+(?:X|Y|Buttons|Pressed|Released|Cursor)"
    r"|Rect\s+Overlap|Text|Blit\s+(?:Copy|Fill|Clear)"
    r"|Double\s+Buffer|Swap|Pic\s+Info|Iff\s+Load"
    r"|Wait\s+Key|Key|Detect|Demo|Plot|Draw|Box|Circle"
    r")\b", re.IGNORECASE,
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def main() -> None:
    extension = inspect(parse((ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()))
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

    for name in ("picture", "blitter", "collide", "show"):
        text = (EXAMPLE_DIR / f"{name}.asc").read_text("ascii")
        require('Fsel$("**")' in text and "Aga Pic Info" in text,
                f"{name}.asc must offer file selection and verify dimensions")
    collide = (EXAMPLE_DIR / "collide.asc").read_text("ascii")
    require(all(call in collide for call in (
        "Aga Rect Overlap", "Aga Mouse X", "Aga Mouse Y",
        "Aga Mouse Pressed", "Aga Blit Clear(0,0,320,256)",
        "Aga Blit Fill", "Aga Swap", "Aga Wait Vbl")),
        "collide.asc must demonstrate R25 AABB, mouse and per-frame redraw/VBL")
    showcase = (EXAMPLE_DIR / "show.asc").read_text("ascii")
    require(all(phrase in showcase for phrase in (
        "Aga Blit Clear(0,0,320,256)", "Aga Blit Fill",
        "Aga Blit Copy", "Aga Text", "Aga Rect Overlap",
        "Aga Mouse X", "Aga Mouse Pressed", "Aga Key",
        "Aga Swap", "Aga Wait Vbl", "For _TRY=1 To 12",
        "For _ST=1 To 12", "If _READY=0", "If _SWREADY=0",
    )), "show.asc must cover R27 Safe, animation, text, copy, collision and input")
    require("If _READY=0" in showcase and
            showcase.index("_CLEAR=Aga Blit Clear(0,0,320,256)") <
            showcase.index("_HEAD=Aga Blit Fill"),
            "show.asc must guard all subsequent drawing with first Safe-aware Clear")
    require("_ERR=1" in showcase and "_ERR=2" in showcase and
            "_ERR=3" in showcase, "show.asc needs bounded failure exits")

    fade = (EXAMPLE_DIR / "fade_to_bank_r33.asc").read_text("ascii")
    instructions = [line.strip() for line in fade.splitlines()
                    if line.strip() and not line.lstrip().startswith("'")]
    require(instructions.index("_SWAP=Aga Swap") <
            instructions.index("Amos To Back") <
            instructions.index("_GREEN=Aga Fade To Bank(_PTR,1,150)"),
            "R33 visual fade must present scene BEFORE animating ColorMap")
    require(all(fragment in fade for fragment in (
        "_GREEN=Aga Fade To Bank(_PTR,1,150)",
        "_BLUE=Aga Fade To Bank(_PTR,2,150)",
        "_RED=Aga Fade To Bank(_PTR,0,150)",
        "Aga Palette Bank Init(_PTR,8)",
        "Aga Palette Bank Capture(_PTR,0)",
        "Aga Palette Bank Capture(_PTR,1)",
        "Aga Palette Bank Capture(_PTR,2)",
        "Reserve As Data _B,6224",
        "Print \"CLOSE RETURNED\"",
    )), "R33 demo must cover three slow colour transitions and cleanup")
    require(fade.count("Aga Fade To Bank(")==3,
            "R33 demo should have exactly three blocking fades")
    require("Save " not in fade and "Load " not in fade,
            "R33 visual demo must not touch files")

    font_demo = (EXAMPLE_DIR / "font_bank_r38.asc").read_text("ascii")
    require(all(fragment in font_demo for fragment in (
        'Load "Amcaf Fonts/Hwarf1252S.abk",25',
        'Load "Amcaf Fonts/Pix3M-1252L.abk",25',
        'Aga Font Bank Select(Start(25),Length(25))',
        'Aga Text(', 'Erase 25',
        'Aga Font Select("",0)', 'Aga Swap', 'Aga Wait Key',
        'Aga Screen Close', 'Amos To Front',
    )), "R38 font example must load both BankFont files and clean up")
    require(font_demo.count('Aga Font Bank Select(Start(25),Length(25))') == 2,
            "R38 example must select exactly two BankFonts")
    require(font_demo.index('Hwarf1252S.abk') < font_demo.index('Pix3M-1252L.abk'),
            "R38 example must render Hwarf before Pix3M")
    for name in ("Hwarf1252S.abk", "Pix3M-1252L.abk"):
        require((EXAMPLE_DIR / "Amcaf Fonts" / name).is_file(),
                f"Missing bundled R38 font bank {name}")

    combined = (EXAMPLE_DIR / "m15_2d_cursor.asc").read_text("ascii")
    require(all(fragment in combined for fragment in (
        "_OPEN=Aga Screen Open(320,256,256,$00021000)",
        "_DB=Aga Double Buffer",
        "Aga Palette Set(", "Aga Blit Clear(0,0,320,256)",
        "Aga Plot(", "Aga Draw(", "Aga Box(", "Aga Circle(",
        "_CUR=Aga Mouse Cursor(0)",
        "_CUR=Aga Mouse Cursor(_VISIBLE)",
        "Aga Mouse X", "Aga Mouse Y", "Aga Mouse Pressed",
        "Aga Key", "Aga Swap", "Aga Wait Vbl",
        "For _TRY=1 To 12", "For _ST=1 To 12",
        "_READY=0", "_SWREADY=0",
        "If _READY=0", "If _SWREADY=0",
        "Aga Screen Close", "Amos To Front",
        'Print "RESULT ";_RESULT', 'Print "CLOSE RETURNED"',
    )), "M15/M15bis combined example must exercise all five APIs and safe cleanup")
    require(combined.index("_CLEAR=Aga Blit Clear(0,0,320,256)") <
            combined.index("_TOP=Aga Blit Fill(") <
            combined.index("_B0=Aga Box("),
            "M15/M15bis must clear a Safe buffer before drawing primitives")
    require('Fsel$(' not in combined and "Aga Iff Load" not in combined and
            'Load "' not in combined,
            "M15/M15bis combined example must not require any external asset")
    require(all(x in combined for x in ("_ERR=1","_ERR=2","_ERR=3","_ERR=4")),
            "M15/M15bis example must have bounded failure outcomes")

    # Archived exact R46 C1 integrated Compiler PASS example.
    kit = EXAMPLE_DIR / "compiler_r46_all_in_one"
    all_in_one = (kit/"COMPILER_R46_ALL_IN_ONE.asc").read_bytes()
    assert all_in_one == (ROOT/"tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc").read_bytes()
    assert len(all_in_one)==5404 and all_in_one.endswith(b"End\n")
    lines = all_in_one.decode("ascii").splitlines()
    assert sum(x.strip().startswith("If ") for x in lines) == sum(x.strip()=="End If" for x in lines)
    assert sum(x.strip().startswith("For ") for x in lines) == sum(x.strip().startswith("Next ") for x in lines)
    for command in ("Aga Image Draw(", "Aga Mouse Cursor(", "Aga Font Bank Select(",
                    "Aga Font Select(", "Aga Swap", "Aga Screen Close",
                    "Aga Plot(", "Aga Draw(", "Aga Box(", "Aga Circle("):
        assert command in all_in_one.decode("ascii"), "C1 example missing "+command
    assert (kit/"M16_AGAPIC_SAMPLE_BANK10.abk").read_bytes() == (
        ROOT/"tests/current/M16_AGAPIC_SAMPLE_BANK10.abk").read_bytes()
    assert (kit/"Hwarf1252S.abk").read_bytes() == (
        EXAMPLE_DIR/"Amcaf Fonts/Hwarf1252S.abk").read_bytes()
    assert (kit/"README.md").is_file() and (kit/"Hwarf-12xxS.licence").is_file()
    import zipfile
    with zipfile.ZipFile(EXAMPLE_DIR/"COMPILER_R46_ALL_IN_ONE.zip") as archive:
        names=archive.namelist()
        root="R46_C1_COMPILER_ALL_IN_ONE/"
        assert set(names)=={root+n for n in (
            "COMPILER_R46_ALL_IN_ONE.asc","M16_AGAPIC_SAMPLE_BANK10.abk",
            "Hwarf1252S.abk","Hwarf-12xxS.licence","README.md")}
        for name in names:
            assert archive.read(name)==(kit/name.removeprefix(root)).read_bytes()
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
    print(f"Distribution examples PASS: {len(EXAMPLES)+1} distinct ASCII demos, "
          "all AP20 calls recognized, cleanup checks and matching 320x256x256 ILBM. "
          "AMOS/WinUAE execution still required.")


if __name__ == "__main__":
    main()
