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
FIXTURE_SHA = "de7691d1bf86974bcd8b2354fc14dd37ece2a7939f7d0f942e3e5c9067bcfb24"

def declarations():
    raw = FIXTURE.read_bytes()
    if sha256(raw).hexdigest() != FIXTURE_SHA:
        raise ValueError("AMOS declaration provenance changed; re-audit include order")
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
