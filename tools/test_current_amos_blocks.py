#!/usr/bin/env python3
"""Guard new AMOS tests against block syntax and obvious string type errors.

R24 initially failed under AMOS because single-line THEN was used in a
block. Check only tests/current/*.asc, not legacy archived examples.
This is a STATIC guard; it is not an AMOS Professional parser/runtime test.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "tests" / "current"


def strip_comment(line):
    quote = False
    for i, char in enumerate(line):
        if char == '"':
            quote = not quote
        elif char == "'" and not quote:
            return line[:i]
    return line


def scan(path):
    if_blocks, for_blocks = [], []
    errors = []
    for index, raw in enumerate(path.read_bytes().decode("latin-1").splitlines(), 1):
        line = strip_comment(raw).strip()
        if not line:
            continue
        # AMOS Peek$ returns a string and requires a $-typed destination.
        peek_assignment = re.match(r"(?i)^([A-Za-z_][A-Za-z0-9_]*\$?)\s*=\s*Peek\$\s*\(", line)
        if peek_assignment and not peek_assignment.group(1).endswith("$"):
            errors.append(f"{index}: Peek$ returns a string; target needs a $ suffix")
        # Direct numeric-variable vs quoted-string comparisons are invalid.
        if re.search(r'(?i)(?<![A-Za-z0-9_$])[A-Za-z_][A-Za-z0-9_]*\s*(?:<>|=)\s*"', line):
            errors.append(f"{index}: string literal compared with non-$ numeric variable")
        if re.match(r"(?i)^If\s+", line):
            if re.search(r"(?i)\bThen\b", line):
                errors.append(f"{index}: single-line THEN is not allowed in current block tests")
            if_blocks.append(index)
        elif re.fullmatch(r"(?i)Else", line):
            if not if_blocks:
                errors.append(f"{index}: ELSE without IF")
        elif re.fullmatch(r"(?i)End\s+If", line):
            if if_blocks:
                if_blocks.pop()
            else:
                errors.append(f"{index}: END IF without IF")
        elif re.match(r"(?i)^For\s+", line):
            for_blocks.append(index)
        elif re.match(r"(?i)^Next\b", line):
            if for_blocks:
                for_blocks.pop()
            else:
                errors.append(f"{index}: NEXT without FOR")
    errors.extend(f"{i}: IF without END IF" for i in if_blocks)
    errors.extend(f"{i}: FOR without NEXT" for i in for_blocks)
    return errors


def main():
    files = sorted(CURRENT.glob("*.asc"))
    assert len(files) <= 1, "Only one active AMOS test is permitted"
    for path in files:
        errors = scan(path)
        assert not errors, f"{path}:\n" + "\n".join(errors)
        print(f"PASS: {path.name} has matched IF/END IF and FOR/NEXT; no single-line THEN")
    if not files:
        print("PASS: no active AMOS test (zero is valid after archiving)")
    if files and files[0].name == "C2P_P2_R73_BITMAP_01.asc":
        source = files[0].read_text("ascii")
        required = (
            "Aga Detect=0", "_CF0=Chip Free",
            "_OPEN=Aga Screen Open(320,256,256,$00021000)",
            "_DB=Aga Double Buffer", "_SW=Aga Swap",
            "_K=Aga Key", "Until _K=69", "Aga Screen Close",
            "Amos To Front", "_CF1=Chip Free",
            'Print "RESULT ";_RESULT', 'Print "CLOSE RETURNED"',
        )
        assert all(x in source for x in required), "C2P/P2 ASC misses the layout probe lifecycle"
        assert source.index("Aga Double Buffer") < source.index("_K=Aga Key") < source.index("Aga Screen Close", source.index("Until _K=69"))
        assert "_K=Aga Wait Key" not in source, "Alt+Tab must not terminate P2 diagnostics"
        assert "Aga C2P" not in source, "P2 diagnostics must not call C2P"
        print("PASS: C2P P2 active ASC opens 320x256x8 and holds both buffers, then cleans up (STATIC ONLY)")
    if files and files[0].name == "C2P_R74_OPEN_01.asc":
        source = files[0].read_text("ascii")
        required = (
            "Reserve As Data 12,81920", "_LEN=Length(12)",
            "_NOS=Aga C2P Open(12)", "_BADBANK=Aga C2P Open(4)",
            "For _DEPTH=4 To 8", "_COL=16",
            "_OPEN=Aga Screen Open(320,256,_COL,$00021000)",
            "_DB=Aga Double Buffer", "_C2P=Aga C2P Open(12)",
            "_DUP=Aga C2P Open(12)", "Aga Screen Close",
            "_POST=Aga C2P Open(12)", "_COL=_COL*2",
            "Erase 12", 'Print "RESULT ";_RESULT', 'Print "CLOSE RETURNED"',
        )
        assert all(x in source for x in required), "R74 C2P Open ASC contract incomplete"
        assert "Aga C2P Convert" not in source and "Aga C2P Close" not in source
        assert source.index("Reserve As Data 12") < source.index("For _DEPTH=4 To 8") < source.index("Erase 12")
        print("PASS: C2P R74 active ASC covers 4..8 planes, duplicate Open, cleanup; STATIC ONLY")
    if files and files[0].name in ("C2P_R75_CONVERT_01.asc", "C2P_R76_CONVERT_01.asc"):
        source=files[0].read_text("ascii")
        required=(
            "Reserve As Data 12,81920",
            "For _I=0 To 81919",
            "Poke _PTR+_I,_I Mod 256",
            "For _DEPTH=4 To 8",
            "_OPEN=Aga Screen Open(320,256,_COL,$00021000)",
            "_DB=Aga Double Buffer",
            "_PAL=Aga Palette Set(_I,_R,_G,_B)",
            "_C2P=Aga C2P Open(12)",
            "_CV0=Aga C2P Convert",
            "_SW0=Aga Swap",
            "_CV1=Aga C2P Convert",
            "_SW1=Aga Swap",
            "If _COL=256", "_K=Aga Key", "Until _K=69",
            "Aga Screen Close",
            "_POST=Aga C2P Convert",
            "Erase 12", 'Print "RESULT ";_RESULT',
            'Print "CLOSE RETURNED"',
        )
        assert all(k in source for k in required),"R75 Convert test incomplete"
        assert source.count("Aga C2P Convert")>=4
        assert source.index("_CV0=Aga C2P Convert")<source.index("_SW0=Aga Swap")<source.index("_CV1=Aga C2P Convert")<source.index("_SW1=Aga Swap")
        assert "Aga C2P Close" not in source
        assert "GDB" not in source or "No GDB" in source
        print("PASS: C2P R75/R76 ASC tests 4..8 planes, 2 converted frames + 2 explicit swaps; STATIC ONLY")
    # OPT020/P1e has ONE interpreted-only active ASC, and keeps R68 archived.
    if files and files[0].name == "OPT020_P1E_R69_INTERPRETED_01.asc":
        source = files[0].read_bytes().decode("latin-1")
        needed = (
            "Aga Image Region(10,0,0,32,20,20,65,0)",
            "Aga Image Region(10,32,0,32,20,88,65,1)",
            "Aga Image Region(10,0,0,16,16,304,208,0)",
            "Aga Image Region(10,1,1,17,12,313,240,1)",
            "Aga Image Region(4,0,0,16,16,10,10,0)",
            "Aga Screen Close", 'Print "RESULT ";_RESULT',
            'Print "CLOSE RETURNED"',
        )
        assert all(x in source for x in needed), "P1e interpreted Gate B scenario incomplete"
        print("PASS: P1e active ASC covers opaque/masked, aligned/clip, reject, close (STATIC only)")
    # R71/R72 integrated Gate B: Clear -> Fill before first P2 Draw.
    if files and files[0].name in ("OPT020_P2_R71_INTERPRETED_01.asc", "OPT020_P2_R72_INTERPRETED_01.asc", "OPT020_P3_R73_INTERPRETED_01.asc"):
        source = files[0].read_bytes().decode("latin-1")
        required = (
            "Aga Blit Clear(0,0,320,256)",
            "Aga Blit Fill(0,0,320,256,2)",
            "Aga Image Draw(_BASE,_LEN,18,20,0)",
            "Aga Image Draw(_BASE,_LEN,108,20,1)",
            "Aga Image Draw(_BASE,_LEN,197,22,1)",
            "Aga Image Draw(_BASE,_LEN,-15,196,1)",
            "Aga Image Draw(_BASE,_LEN,291,182,0)",
            "Aga Image Draw(_BASE,_LEN,256,-17,1)",
            "Aga Image Draw(_BASE,_LEN,105,241,1)",
            "Aga Image Draw(_BASE,_LEN,320,256,0)",
            "Aga Image Draw(0,_LEN,20,20,1)",
            "Aga Image Draw(_BASE,20,20,20,0)",
            "Aga Image Draw(_BASE,_LEN,20,20,2)",
            "Aga Image Draw(_BASE,_LEN,32768,20,0)",
            "_P2NOS=Aga Image Draw(_BASE,_LEN,25,25,0)",
            "Aga Image Region(10,0,0,32,20,20,65,0)",
            "Aga Image Region(10,32,0,32,20,88,65,1)",
            "_OLD=Aga Bank Image Draw(10,116,169,0)",
            "Aga Screen Close", "Erase 10",
            'Print "RESULT ";_RESULT',
            'Print "CLOSE RETURNED"',
        )
        assert all(x in source for x in required), "P2 active test misses R69 or P2 cases"
        assert source.count('Print "CLOSE RETURNED"') == 1
        assert source.index("Aga Blit Clear(") < source.index("Aga Blit Fill(") < source.index("Aga Image Draw(")
        print("PASS: P2 active ASC exercises Clear -> Fill -> Draw, Region and legacy Bank Draw (STATIC only)")
    # R73: preserve all R72 P1e/P2 cases, plus P3 capture+draw.
    if files and files[0].name == "OPT020_P3_R73_INTERPRETED_01.asc":
        source = files[0].read_bytes().decode("latin-1")
        needed = (
            'Load "M18_FICON8_SAMPLE_BANK10.abk",11',
            '_OPEN=Aga Screen Open(320,256,16,$00021000)',
            '_OPEN8=Aga Screen Open(320,256,256,$00021000)',
            '_FOPA=Aga F Icon(11,1,31,104,0)',
            '_FCAP=Aga F Icon Capture(11,4,31,104)',
            "For _I=0 To 287",
            "Peek(Start(11)+12+864+_I)",
            "_FMASK=Aga F Icon(11,4,61,105,1)",
            "_FSHIFT=Aga F Icon(11,2,133,110,0)",
            "_FCL=Aga F Icon(11,3,-7,154,1)",
            "_FCR=Aga F Icon(11,3,314,154,1)",
            "_FCT=Aga F Icon(11,1,220,-5,0)",
            "_FCB=Aga F Icon(11,2,251,252,0)",
            "_FBADBANK=Aga F Icon(4,2,120,120,0)",
            "_FCBADID=Aga F Icon Capture(11,5,31,44)",
            "_FNOS=Aga F Icon(11,2,25,25,0)",
            "_FCAPNOS=Aga F Icon Capture(11,4,25,25)",
            "Erase 11", "Erase 10",
            "_CF0<>_CFMID or _CFMID<>_CF1",
            "_CLOSED8<>-1",
            'Print "FICON CAP/EQ288 ";_FCAP;" ";_FEQ',
        )
        assert all(x in source for x in needed), (
            "R73 ASC misses a Fast Icon Capture or Draw safety case"
        )
        assert "or _FCAP<>1 or _FEQ<>1" in source
        # Regression guard for the 2026-11-13 failed integrated Gate B:
        # AGAPIC bank 10 has 4 planes, whereas Fast Icons use 8 planes.
        # The 68020 P1e/P2 code correctly rejects a depth mismatch.
        open4 = source.index("_OPEN=Aga Screen Open(320,256,16,$00021000)")
        draw4 = source.index("_P2OPA=Aga Image Draw(")
        region4 = source.index("_D0=Aga Image Region(")
        close4 = source.index("_CLOSED=Aga Mouse X")
        open8 = source.index("_OPEN8=Aga Screen Open(320,256,256,$00021000)")
        draw8 = source.index("_FOPA=Aga F Icon(")
        capture8 = source.index("_FCAP=Aga F Icon Capture(")
        close8 = source.index("_CLOSED8=Aga Mouse X")
        assert open4 < draw4 < region4 < close4 < open8 < draw8 < capture8 < close8, (
            "R73 P1e/P2 AGAPIC4 and P3 FICON8 must run on separate 4/8-plane screens"
        )
        assert source.index("Aga Blit Clear(") < source.index("Aga Blit Fill(") < draw4
        assert source.count("_OPEN8=Aga Screen Open(")==1
        assert source.count('Print "CLOSE RETURNED"')==1
        print("PASS: R73 single ASC exercises AGAPIC4 on 16 colors, then FICON8 on 256 colors, with capture/288-byte compare/bounds (STATIC only)")
    # Final M18 Compiler Gate C coverage: static only, never executes Compiler.
    if files and files[0].name == "M18_R68_COMPILER_FINAL_01.asc":
        source = files[0].read_text("ascii")
        required = (
            "Aga F Icon Bank Create(", "Aga F Icon Bank Put(",
            "Aga F Chip Bank Create(", "Aga F Chip Stage(",
            "Aga F Icon Capture(", "Aga F Blit(",
            "Aga C Block Capture(", "Aga C Block Draw(",
            "Aga C Block Restore(",
            "Aga C Block Draw(14,8,200,0)",
            "Aga C Block Draw(14,96,200,2)",
            "Aga C Block Draw(14,176,200,1)",
            "Aga C Block Restore(14,1)",
            "Erase 14", 'Print "RESULT ";_RESULT',
            'Print "CLOSE RETURNED"',
        )
        assert all(x in source for x in required), "Final M18 test misses R64-R68 calls"
        assert "_CBLEN<>1064" in source, "Final CBlock 32x32x8 bank length mismatch"
        print("PASS: single R68 Compiler Gate C ASC covers R64-R68 (static only)")



if __name__ == "__main__":
    main()
