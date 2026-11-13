"""AMOS main symbols: include order and Lib_Pos are part of the AP20 ABI.

Reference: +Lib.s:1710 includes +ILib.s, ending with Lib_Pos 500.
+Equ.s:2177-2217 defines the counting macros. The fixture is declaration
metadata, not an implementation of the AMOS runtime. Never count +Lib.s alone.
"""
import json
from hashlib import sha256
from pathlib import Path
from struct import pack

FIXTURE = Path(__file__).resolve().parents[1]/"tests/fixtures/amos_main_declarations.json"
FIXTURE_SHA = "9c5864b7de5bdd9959b0d939a813fb5ea6891ef138c556f5285e900d5094ce90"

def verified_fixture(raw: bytes) -> bytes:
    """Return LF-canonical declaration bytes after checking the immutable SHA256.

    Git on Windows may check out this JSON as CRLF even though the audited
    repository blob is LF. Accept ONLY a uniform LF <-> CRLF conversion,
    not edits, mixed endings, bare CR, BOM, changed include order or symbols.
    The pinned SHA256 is intentionally NEVER recalculated or relaxed.
    """
    if b"\r" in raw:
        crlf = raw.count(b"\r\n")
        if crlf != raw.count(b"\r") or crlf != raw.count(b"\n"):
            raise ValueError(
                "AMOS declaration provenance changed; re-audit include order "
                "(mixed line endings or bare CR in fixture)")
        raw = raw.replace(b"\r\n", b"\n")
    checked_sha = sha256(raw).hexdigest()
    if checked_sha != FIXTURE_SHA:
        raise ValueError(
            "AMOS declaration provenance changed; re-audit include order "
            f"(expected LF SHA256 {FIXTURE_SHA}, got {checked_sha})")
    return raw


def declarations():
    raw = verified_fixture(FIXTURE.read_bytes())
    units = json.loads(raw)["units"]
    if [u["file"] for u in units] != ["+ILib.s", "+Lib.s"]:
        raise ValueError("missing AMOS interpreter prefix")
    count = None
    entries = []
    for unit in units:
        for line, text in unit["directives"]:
            macro, name = text.split()
            if macro == "Lib_Ini":
                count = int(name)
            elif macro == "Lib_Pos":
                count = max(count, int(name))
            elif macro in ("Lib_Def", "Lib_Par", "Lib_Int"):
                if count is None:
                    raise ValueError("Lib_Ini required")
                entries.append((count, name, unit["file"], line, macro))
                count += 1
            else:
                raise ValueError("unhandled declaration " + macro)
    return entries

def main_index(symbol):
    matches = [e[0] for e in declarations() if e[1] == symbol]
    if len(matches) != 1:
        raise ValueError("missing or ambiguous AMOS symbol: " + symbol)
    return matches[0]

def rjsr(index):
    if not 0 <= index <= 8191:
        raise ValueError("AMOS signed negative table displacement overflow")
    return bytes.fromhex("fe11f700") + pack(">H", index)
