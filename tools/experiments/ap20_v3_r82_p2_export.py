#!/usr/bin/env python3
"""Export a DISPOSABLE P2 test artifact outside dist/. Never promotes R82.

This is an experimental AMOS library to be installed only in a separate
WinUAE test environment after backing up its existing APSystem extension.
Not an approved release; real AMOS Interpreter/Compiler Gates B/C pending.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path

from ap20_v3_r82_p2 import (build_in_memory, r82_bytes, ROOT,
                               NEW_PROBE_GROUP, NEW_R82_GROUP,
                               validate_interpreter_rbsr)
from audit_ap20 import inspect, parse
from compiler_relocation import unpack_ap20


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dest = args.output.resolve()
    protected = [(ROOT / "dist").resolve(), (ROOT / "tests/current").resolve()]
    if any(dest == root or root in dest.parents for root in protected):
        raise SystemExit("Refusing to write a protected project path")
    if dest.name != "AMOSPro_AGA_V3_FIXED.Lib":
        raise SystemExit("Output must clearly identify the experimental .Lib")
    source = r82_bytes()
    image, meta = build_in_memory(source)
    _, parts, _ = unpack_ap20(image)
    validate_interpreter_rbsr(parts)
    report = inspect(parse(image))
    if (report["issues"] or len(parts) != 83
            or meta["sum_native_units_bytes"] != 73006
            or len(parts[NEW_PROBE_GROUP]) != 12034 or len(parts[NEW_R82_GROUP]) != 60972):
        raise SystemExit("Experimental AP20 integrity failure")
    if len(image) <= 65536:
        raise SystemExit("Unexpectedly not testing the >64 KiB boundary")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(image)
    if sha256(dest.read_bytes()).digest() != sha256(image).digest():
        raise SystemExit("Written test output differs from deterministic builder")
    if r82_bytes() != source:
        raise SystemExit("R82 source file was unexpectedly changed")
    print("AP20 V3 R82 DISPOSABLE TEST LIB GENERATED", meta, flush=True)
    print("EXPERIMENTAL_FILE", dest, flush=True)
    print("EXPERIMENTAL_SHA256", sha256(image).hexdigest(), flush=True)
    print("THIS IS NOT A R82 RELEASE AND HAS NOT PASSED WINUAE OR COMPILER", flush=True)


if __name__ == "__main__":
    main()
