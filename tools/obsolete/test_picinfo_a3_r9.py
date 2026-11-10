#!/usr/bin/env python3
"""Execute actual R9 PicInfo 68000 in Unicorn and validate A3 consumption.

R8 baseline wrongly preserves A3. R9 must advance it by 4 on success
and all error exits, while preserving all other public registers.
These CPU tests do not replace AMOS/WinUAE runtime validation.
"""
from pathlib import Path
from ap20_utils import split, digest
from audit_ap20 import parse, inspect as audit
from build_picinfo_a3_r9 import build, BASE, ARCHIVE, DEST, R9_SHA256
from test_m5_generic import Machine, fixture
from validate_ilbm import inspect

def main():
    r9, report = build()
    r8 = BASE.read_bytes()
    assert ARCHIVE.read_bytes() == r9
    assert digest(r9) == R9_SHA256
    assert not audit(parse(r9))["issues"]
    oldtokens, oldparts, oldtitle = split(r8)
    newtokens, parts, title = split(r9)
    assert oldtokens == newtokens
    assert [i for i in range(19) if oldparts[i] != parts[i]] == [14]
    assert parts[14][:4].hex() == "48e7efee"
    assert parts[14][492:496].hex() == "4cdf77f7"
    assert parts[13] == oldparts[13]  # IFF Load untouched
    assert all(parts[i] == oldparts[i] for i in range(19) if i != 14)

    data = fixture(width=17, height=2, depth=2, compression=1, camg=0)
    meta, body = inspect(data)
    values = (17, 2, 2, 4, 1, 0, 0, 4)

    # Demonstrate the baseline failure without changing its regression tests.
    baseline = Machine(r8, data)
    assert baseline.execute(14, field=0) == 17
    assert baseline.a(3) == 0x58000, "Unexpected baseline A3 behavior"

    for field, value in enumerate(values):
        m = Machine(r9, data)
        assert m.execute(14, field=field, a3_delta=4) == value, (field, value)
        assert m.a(3) == 0x58004
        assert not m.owned and m.open_files == 0 and m.open_libraries == 0

    cases = [
        ("missing", None, 0),
        ("empty", b"", 0),
        ("truncated", data[:12], 0),
        ("bad_field", data, 8),
    ]
    for name, source, field in cases:
        m = Machine(r9, source)
        assert m.execute(14, field=field, a3_delta=4) == 0xFFFFFFFF, name
        assert m.a(3) == 0x58004 and not m.owned, name

    for failing_allocation in (1, 2):
        m = Machine(r9, data, allocation_failure=failing_allocation)
        assert m.execute(14, field=0, a3_delta=4) == 0xFFFFFFFF
        assert not m.owned

    print("R9 PASS: baseline reproduced, 8 fields, 4 error paths, 2 allocations, A3 +4, loader unchanged")


if __name__ == "__main__":
    main()
