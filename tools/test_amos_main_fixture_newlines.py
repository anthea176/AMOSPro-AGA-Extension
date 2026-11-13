#!/usr/bin/env python3
"""Regression for strict AMOS main-index provenance across Windows checkouts.

Accept only byte-identical SHA256-pinned LF content and its uniform CRLF
checkout equivalent. Real data/source/include edits must still fail closed.
"""
from __future__ import annotations

from hashlib import sha256

from amos_main_abi import FIXTURE, FIXTURE_SHA, declarations, main_index, verified_fixture


def rejected(blob: bytes, label: str) -> None:
    try:
        verified_fixture(blob)
    except ValueError as exc:
        assert "AMOS declaration provenance changed" in str(exc), (label, exc)
    else:
        raise AssertionError("Untrusted declaration fixture accepted: " + label)


def main() -> None:
    raw = FIXTURE.read_bytes()
    lf = verified_fixture(raw)
    assert b"\r" not in lf and sha256(lf).hexdigest() == FIXTURE_SHA

    crlf = lf.replace(b"\n", b"\r\n")
    assert crlf != lf and verified_fixture(crlf) == lf
    assert sha256(crlf).hexdigest() != FIXTURE_SHA
    assert crlf.count(b"\r\n") == lf.count(b"\n")
    assert lf.count(b"\n") == 3132

    assert b"Lib_Pos 500" in lf
    rejected(lf.replace(b"Lib_Pos 500", b"Lib_Pos 501"), "changed include offset")
    rejected(crlf.replace(b"Lib_Pos 500", b"Lib_Pos 501"), "CRLF plus ABI edit")
    rejected(lf.replace(b"\n", b"\r\n", 1), "mixed LF and CRLF")
    rejected(lf.replace(b"\n", b"\r", 1), "bare CR")
    rejected(b"\xef\xbb\xbf" + lf, "UTF-8 BOM")
    rejected(lf + b" ", "trailing data")

    entries = declarations()
    assert len(entries) == 770
    expected = {"MainLibrary": 500, "Bnk.GetAdr": 797,
                "Bnk.Eff": 800, "Bnk.Reserve": 816,
                "Bnk.Change": 819, "FnOne": 822}
    assert {name: main_index(name) for name in expected} == expected
    assert FIXTURE.read_bytes() == raw, "Fixture must remain read-only"
    print("AMOS declaration provenance PASS: exact LF + Windows CRLF SHA pin")
    print("770 declarations, MainLibrary=500, Bnk.GetAdr=797, FnOne=822")
    print("Reject malformed source, changed index, mixed EOL, bare CR and BOM")


if __name__ == "__main__":
    main()
