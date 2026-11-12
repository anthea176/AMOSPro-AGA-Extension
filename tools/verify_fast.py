#!/usr/bin/env python3
"""Fast, read-only integrity gate: immutable archives + active Compiler-safe AP20.

Historical native CPU suites and deterministic re-builds remain in the manual
full regression workflow. Do not weaken HASHES or the current builder checks.
"""
from __future__ import annotations

import hashlib

from audit_ap20 import inspect, parse
from compiler_relocation import is_compiler_wrapped, unpack_ap20, unwrap_native_parts
from verify_artifacts import HASHES, ROOT, verify_hunk
from active_library import verify_active


def main() -> None:
    # Hash all archives cheaply: no repeated execution of historical builders.
    for relative, expected in HASHES.items():
        blob = verify_hunk(ROOT / relative)
        actual = hashlib.sha256(blob).hexdigest()
        assert actual == expected, f"Immutable HUNK changed: {relative}"
    print(f"SHA256/HUNK PASS: {len(HASHES)} official and frozen binary artifacts")

    current, last_good, active_label = verify_active(ROOT)
    report = inspect(parse(current))
    assert any(t["name"].startswith("aga ") for t in report["tokens"]), "AGA API missing"

    # The currently promoted C1 must remain independently reversible to its
    # frozen native source. Version-specific extension checks stay in build_aga_current.
    raw = (ROOT / "dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib").read_bytes()
    raw_tokens, raw_parts, _ = unpack_ap20(raw)
    active_tokens, active_parts, _ = unpack_ap20(last_good)
    assert active_tokens == raw_tokens, "Promoted tokens diverge from C1 source"
    assert len(active_parts) == len(raw_parts) + 1, "Compiler bridge entry lost"
    assert unwrap_native_parts(last_good) == (raw_tokens, raw_parts), "LAST_GOOD Compiler bridge corrupt"
    print("ACTIVE AP20 PASS:", active_label, "; R46 LAST_GOOD compiler bridge immutable, reversible")


if __name__ == "__main__":
    main()
