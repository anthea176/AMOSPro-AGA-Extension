#!/usr/bin/env python3
"""Static, non-executing AMOS preflight for the M18 R60 16x16 benchmark.

Does not validate benchmark measurements, 68000 native code, or AMOS runtime.
"""
from pathlib import Path

from test_current_amos_blocks import scan

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / "benchmarks/m18_r60_cpu_vs_blit_16x16.asc"
RESOURCE = ROOT / "tests/current/M16_AGAPIC_SAMPLE_BANK10.abk"


def main() -> None:
    raw = PROGRAM.read_bytes()
    assert b"\x00" not in raw and all(c < 128 for c in raw), "ASC must be plain ASCII"
    assert RESOURCE.is_file(), "Missing frozen AGAPIC sample bank"
    bad = scan(PROGRAM)
    assert not bad, "\n".join(bad)
    source = raw.decode("ascii")
    assert "Aga Image Region(10,0,0,16,16" in source
    assert "Aga Blit Copy(_SX,_SY,_DX,_DY,16,16)" in source
    assert 'Load "M16_AGAPIC_SAMPLE_BANK10.abk",10' in source
    assert source.count("Aga Screen Close") >= 2
    assert "BENCH FINISHED - CLOSE RETURNED" in source
    assert "Wait Key" not in source and "Blitter Wait" not in source
    # In every timed series, only a loop of the intended draw call is run.
    loops = (
        ("_LASTCPU=Aga Image Region(", "_TM(0,_CASE,_TR)=Timer-_T0"),
        ("_LASTBLIT=Aga Blit Copy(", "_TM(1,_CASE,_TR)=Timer-_T0"),
    )
    for name, until in loops:
        i = source.index(name)
        j = source.index(until, i)
        measured = source[i:j]
        assert measured.count("Next _I") == 1
        assert not any(x in measured for x in (
            "Wait Vbl", "Aga Swap", "Aga Screen Close", "Print ",
            "Aga Blit Clear", "Amos To Back"))
    print("M18 CPU/BLIT 16x16 BENCH STATIC PASS:",
          len(source.splitlines()), "ASCII lines, IF/FOR matched,",
          "one staged source, three runs, no wait or print in timing loops")
    print("STATIC ONLY: no actual WinUAE or AMOS Compiler result")


if __name__ == "__main__":
    main()
