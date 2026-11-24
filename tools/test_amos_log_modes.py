#!/usr/bin/env python3
"""Guard against reusing a single RAM log across AMOS Runtime and Compiler.

This is a static source-contract check only; it neither executes nor
compiles AMOS and cannot validate WinUAE display or file I/O behavior.
"""
from pathlib import Path
from hashlib import sha256
import re

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "tests/current"
FLIP = ROOT / "examples/aga_bob_flip/FLIP_VISUAL.asc"
PROMOTED = ROOT / "examples/bob_p2_all_in_one/BOB_ALL_IN_ONE.asc"
FROZEN = ROOT / "tests/passed/M19_P2_ALL_IN_ONE.asc"
MODES = ((0, "INTERPRETED"), (1, "RUNTIME"), (-1, "COMPILED"))
L2_FROZEN = "720348897fd0f939dc413687ccc69ed524fd7edff863dcc89f320a1f68e0f974"


def verify(path: Path) -> list[str]:
    raw = path.read_bytes()
    assert raw.isascii(), f"{path}: ASCII source expected"
    source = raw.decode("ascii")
    assert "_PRG=Prg State" in source, f"{path}: missing Prg State"
    assert '_MODE$="UNKNOWN"' in source, f"{path}: missing fallback mode"
    assert "Trap Open Out 1,_LOG$" in source, f"{path}: missing log open"
    assert 'Print #1,"PRG_STATE ";_PRG' in source, f"{path}: missing state in log"
    assert 'Print #1,"RUN_MODE ";_MODE$' in source, f"{path}: missing mode in log"
    assert 'Print "RAM LOG ";_LOG$' in source, f"{path}: missing filename on exit"

    fallback = re.search(r'_LOG\$="RAM:([A-Za-z0-9_]+)_UNKNOWN\.TXT"', source)
    assert fallback, f"{path}: no safe log prefix / UNKNOWN file"
    prefix = fallback.group(1)
    names = [prefix + "_UNKNOWN.TXT"]
    for state, mode in MODES:
        expected = (
            f'If _PRG={state}\n'
            f'   _MODE$="{mode}"\n'
            f'   _LOG$="RAM:{prefix}_{mode}.TXT"\n'
            'End If'
        )
        assert expected in source, f"{path}: missing independent {mode} filename"
        names.append(prefix + "_" + mode + ".TXT")
    assert len(names) == len(set(names)), f"{path}: filename collision"
    assert all(len(name) <= 30 for name in names), (
        f"{path}: AmigaDOS filename longer than 30 characters: {names}"
    )
    return names


def verify_l2_frozen(path: Path) -> list[str]:
    """Exact already-tested L2 probe predates UNKNOWN and RUN_MODE fields.

    Do not change its evidence-bearing bytes just to satisfy a newer format.
    Any edited/new ASC must pass the full verify() contract instead.
    """
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == L2_FROZEN, "L2 probe changed"
    source = raw.decode("ascii")
    for marker in ("_PRG=Prg State", 'Print #1,"PRG_STATE ";_PRG',
                   "Trap Open Out 1,_LOG$", 'Print "RAM LOG ";_LOG    active = sorted(CURRENT.glob("*.asc"))
    assert len(active) == 1, f"Expected exactly one active ASC, found {active}"
    assert PROMOTED.is_file() and FROZEN.read_bytes() == PROMOTED.read_bytes(), (
        "The B/C-validated example and its frozen regression must match"
    )
    paths = [PROMOTED, FLIP, *active]
    for path in paths:
        if path == active[0] and sha256(path.read_bytes()).hexdigest() == L2_FROZEN:
            filenames = verify_l2_frozen(path)
        else:
            filenames = verify(path)
        print(f"MODE_LOG_NAMING PASS: {path.relative_to(ROOT)} : {', '.join(filenames)}")
    print("MODE_LOG_NAMING PASS (static source only; AMOS Runtime/Compiler not tested)")


if __name__ == "__main__":
    main()
):
        assert marker in source, f"{path}: missing {marker}"
    names = [f"P2D_L2_{mode}.TXT" for _, mode in MODES]
    assert f'_LOG$="RAM:{names[0]}"' in source
    for (state, _), name in zip(MODES[1:], names[1:]):
        assert f'If _PRG={state}\n   _LOG$="RAM:{name}"\nEnd If' in source
    assert len(names) == len(set(names)) and all(len(n) <= 30 for n in names)
    print("MODE_LOG_NAMING: exact historical L2 exception (no UNKNOWN/RUN_MODE)")
    return names


def main() -> None:
    active = sorted(CURRENT.glob("*.asc"))
    assert len(active) == 1, f"Expected exactly one active ASC, found {active}"
    assert PROMOTED.is_file() and FROZEN.read_bytes() == PROMOTED.read_bytes(), (
        "The B/C-validated example and its frozen regression must match"
    )
    assert active[0].read_bytes() == PROMOTED.read_bytes(), "Active and public ASC differ"
    paths = [PROMOTED, FLIP, *active]
    for path in paths:
        filenames = verify(path)
        print(f"MODE_LOG_NAMING PASS: {path.relative_to(ROOT)} : {', '.join(filenames)}")
    print("MODE_LOG_NAMING PASS (static source only; AMOS Runtime/Compiler not tested)")


if __name__ == "__main__":
    main()
