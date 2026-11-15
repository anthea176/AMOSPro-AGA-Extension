#!/usr/bin/env python3
"""SHA-pinned, read-only ASM export for the R83-R88 multi-unit AP20 bridge.

The byte-exact AP20 file contains DC.W/DC.B (including FE31 pseudo-ops).
Each native group additionally gets a *partially mnemonic* MC68020 source:
source-proven entrypoints are traced with the conservative decoder; all other
bytes are preserved verbatim as data. No guessed instruction is needed to
round-trip the HUNK, and a native assembler is required to verify mnemonics.
"""
from __future__ import annotations

from hashlib import sha256
import importlib
import json
from pathlib import Path
import re
from struct import unpack_from
import subprocess

from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP, RBSR, unpack_ap20
from decoder68k import Decoder
from export_aga_asm import decode_exact_asm, export_asm, parse_ap20


# SHA + deterministic builder + exact public/native split. Never accept a
# future release based only on a title string or an AP20 dispatcher pattern.
def known_releases():
    from active_library import (
        R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA,
    )
    return {
        R83_SHA: ("R83", "build_aga_r83_modular", 80, ("C2P", "IFF", "AGA")),
        R84_SHA: ("R84", "build_aga_r84_agapic", 82, ("C2P", "IFF", "AGA")),
        R85_SHA: ("R85", "build_m19_p22_fourth_unit_probe", 83, ("C2P", "IFF", "BOBS", "AGA")),
        R86_SHA: ("R86", "build_m19_p23_bob_batch", 84, ("C2P", "IFF", "BOBS", "AGA")),
        R87_SHA: ("R87", "build_m19_p25_no_probe", 83, ("C2P", "IFF", "BOBS", "AGA")),
        R88_SHA: ("R88", "build_m19_p28_r88_in_memory", 84, ("C2P", "IFF", "BOBS", "AGA")),
    }


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError("Multi-unit AP20: " + message)


def identify(data: bytes):
    """Return pinned release metadata or None (legacy exporter handles others)."""
    return known_releases().get(digest(data))


def validate_wrapped(data: bytes, public: int, unit_names: tuple[str, ...]):
    """Check EVERY FE31 linker stub and all independently copied V2 groups."""
    tokens, segments, title = unpack_ap20(data)
    require(len(segments) == public + len(unit_names), "unexpected AP20 entry count")
    require(len(unit_names) in (3, 4), "unexpected native unit count")
    require(len(DISPATCH_V2) == 34, "unknown V2 dispatcher length")
    refs = {public + i: [] for i in range(len(unit_names))}
    for index, group in enumerate(segments[public:], start=public):
        require(group.startswith(DISPATCH_V2), f"native group {index} has no audited V2 dispatcher")
        require(len(group) <= 65534 and (len(group) & 1) == 0,
                f"native group {index} violates Compiler copy size/alignment")
        require(len(group) > len(DISPATCH_V2), f"empty native group {index}")
    for index, stub in enumerate(segments[:public]):
        if stub in (b"", GETP):
            continue
        require(len(stub) in (8, 12) and stub[:2] == RBSR
                and stub[6:8] == b"\x4e\x75"
                and (len(stub) == 8 or stub[8:] == GETP),
                f"invalid AP20 Rbsr/RTS/GetP stub {index}")
        group, offset = unpack_from(">HH", stub, 2)
        require(group in refs, f"public stub {index} targets unknown unit {group}")
        require((offset & 1) == 0 and offset < len(segments[group]) - len(DISPATCH_V2),
                f"public stub {index} has invalid unit-relative offset {offset}")
        refs[group].append((index, len(DISPATCH_V2) + offset))
    require(any(refs.values()), "no live native public entries")
    # Strict linked AP20 parser additionally checks token names and jump spans.
    parse_ap20(data)
    return segments, title, refs


def _source_lines_for_data(blob: bytes, start: int, stop: int):
    return ["    dc.b " + ",".join("$%02X" % x for x in blob[i:min(stop, i + 12)])
            + "  ; +$%05X: %s" % (i, blob[i:min(stop, i + 12)].hex().upper())
            for i in range(start, stop, 12)]


def trace_unit_code(group: bytes, seeds: set[int]):
    """Linear-cost conservative CFG traversal for large 56-KiB AGA groups.

    The repository's flow_decode() uses an O(N^2) overlap scan; each verified
    multi-unit group may contain tens of thousands of 68020 instructions.
    """
    decoder = Decoder(group, 0, allow_scaled_index=True)
    decoded = {}
    occupied = bytearray(len(group))
    stack = [0, *sorted(seeds)]
    while stack:
        pc = stack.pop()
        while 0 <= pc < len(group) - 1 and not occupied[pc]:
            insn = decoder.decode(pc)
            if insn is None or pc + insn.size > len(group):
                break
            if any(occupied[pc:pc + insn.size]):
                break
            decoded[pc] = insn
            occupied[pc:pc + insn.size] = bytes([1]) * insn.size
            if (insn.target is not None and 0 <= insn.target < len(group)
                    and not (insn.target & 1)):
                stack.append(insn.target)
            if insn.stop:
                break
            pc += insn.size
    return decoded, occupied


def native_unit_source(name: str, group: bytes, entries: list[tuple[int, int]]):
    """Emit real 020 mnemonics at verified public entrypoints, raw data elsewhere.

    The decoded mnemonics have NOT been assembler-verified: the exact HUNK
    sibling is the immutable reference, never the generated mnemonic file.
    """
    seeds = {at for _, at in entries}
    # The 34-byte V2 dispatcher is executable 68000 code, but the linker
    # FE31 words in public stubs are NOT CPU code and are never decoded here.
    instructions, occupied = trace_unit_code(group, seeds)
    undecoded_entrypoints = sorted(seeds.difference(instructions))
    # Some authentic entrypoints start with AMOS pseudo-ops or unsupported
    # 020 encodings; preserve their bytes rather than rejecting a valid Lib.

    # Labels are emitted only at instruction boundaries or inside untouched
    # data ranges; they must never split a decoded instruction.
    labels = {0: "UNIT_" + name}
    for _, at in entries:
        labels[at] = "ENTRY_%s_%05X" % (name, at)
    candidate_refs = set()
    for insn in instructions.values():
        if insn.target is not None:
            candidate_refs.add(insn.target)
        candidate_refs.update(insn.data_refs)
    for at in sorted(candidate_refs):
        if not 0 <= at < len(group):
            continue
        if occupied[at] and at not in instructions:
            continue
        labels.setdefault(at, "L_%s_%05X" % (name, at))

    out = [
        "; PARTIAL MC68020 MNEMONIC RESTORATION (not an installable .Lib)",
        "; Unit: " + name + " | SHA256: " + digest(group),
        "; Proven SHA-pinned AP20 unit, including its 34-byte V2 dispatcher.",
        "; DC.B preserves unclassified code/data, GetP and AMOS linker markers.",
        "; Mnemonic equivalence is NOT proven without --verify-vasm.",
        "    cpu 68020", "",
    ]
    pos = 0
    decoded_bytes = 0
    data_bytes = 0
    raw_instructions = 0
    while pos < len(group):
        if pos in labels:
            out.append(labels[pos] + ":")
        insn = instructions.get(pos)
        if insn is not None:
            raw = group[pos:pos + insn.size]
            line = insn.text
            # Branch target is relative to THIS independently copied module.
            # A target that is not a well-formed local label stays raw.
            if insn.target is not None:
                if insn.target in labels:
                    line = line.replace("@$%06X" % insn.target, labels[insn.target])
                else:
                    line = None
            if line is not None and insn.data_refs:
                for ref in insn.data_refs:
                    if ref in labels and "(pc)" in line:
                        line = re.sub(r"-?\d+\(pc\)", labels[ref] + "(pc)", line, count=1)
            if line is None:
                out.extend(_source_lines_for_data(group, pos, pos + insn.size))
                raw_instructions += 1
                data_bytes += insn.size
            else:
                out.append("    %-50s ; +$%05X: %s" % (line, pos, raw.hex().upper()))
                decoded_bytes += insn.size
            pos += insn.size
            continue
        # Never let raw bytes consume the following label or instruction.
        end = min(len(group), pos + 12)
        for at in range(pos + 1, end):
            if at in labels or at in instructions:
                end = at
                break
        out.extend(_source_lines_for_data(group, pos, end))
        data_bytes += end - pos
        pos = end
    require(decoded_bytes + data_bytes == len(group), "byte coverage differs from native unit")
    return "\n".join(out) + "\n", {
        "unit": name,
        "sha256": digest(group),
        "bytes": len(group),
        "public_entrypoints": [{"ap20_index": i, "unit_offset": at} for i, at in entries],
        "mnemonic_instructions": len(instructions) - raw_instructions,
        "mnemonic_bytes": decoded_bytes,
        "raw_dc_bytes": data_bytes,
        "unresolved_instruction_encodings": raw_instructions,
        "undecoded_public_entry_offsets": undecoded_entrypoints,
        "native_assembler_verified": False,
    }


def _assemble(assembler, source: Path, result: Path):
    cmd = [assembler, "-Fbin", "-m68020", "-quiet", "-o", str(result), str(source)]
    run = subprocess.run(cmd, text=True, capture_output=True, timeout=120)
    require(run.returncode == 0,
            "vasm failed on %s: %s %s" % (source.name, run.stdout, run.stderr))
    return result.read_bytes()


def export(data: bytes, *, root: Path, target: Path, strict: bool,
           assembler: str | None = None, baseline: str = "auto") -> list[Path]:
    release = identify(data)
    require(release is not None, "unknown multi-unit SHA; new audited builder required")
    revision, builder_module, public, groups = release
    # verify_active protects both the active .Lib and frozen R84 LAST_GOOD.
    from active_library import verify_active
    active_file = root / "dist/AMOSPro_AGA.Lib"
    frozen_file = root / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
    before_active = digest(active_file.read_bytes())
    before_frozen = digest(frozen_file.read_bytes())
    verify_active(root)
    builder = importlib.import_module(builder_module)
    expected, meta = builder.build()
    require(expected == data, "deterministic builder and selected .Lib differ")
    require(digest(expected) == digest(data), "builder SHA drift")
    require(digest(active_file.read_bytes()) == before_active and
            digest(frozen_file.read_bytes()) == before_frozen,
            "a builder changed the active or LAST_GOOD binary")
    segments, title, refs = validate_wrapped(data, public, groups)

    # Independent, byte-exact representation of the complete linked library:
    # the legacy source_binary_from_input() intentionally cannot perform this
    # operation because it is limited to ONE V2 dispatcher.
    exact, _, original_report = export_asm(parse_ap20(data), None, None)
    require(decode_exact_asm(exact) == data, "lossless AP20 source round-trip failed")
    sources = {}
    reports = []
    for index, name in enumerate(groups, start=public):
        source, report = native_unit_source(name, segments[index], refs[index])
        filename = "AMOSPro_AGA_%s_%s_NATIVE.s" % (revision, name)
        sources[filename] = source
        report["file"] = filename
        report["ap20_index"] = index
        reports.append(report)
    manifest = {
        "revision": revision,
        "compiler_format": "AP20 V2 multiple independently relocated native groups",
        "input_sha256": digest(data), "input_bytes": len(data),
        "builder": builder_module, "deterministic_builder_verified": True,
        "pinned_build_metadata_sha256": str(meta.get("sha256", "")),
        "last_good_verified": True, "input_is_read_only": True,
        "public_entries": public, "ap20_entries": len(segments),
        "groups": reports,
        "exact_ap20_binary_roundtrip_verified": True,
        "native_assembler_verified": False,
        "source_status": "partial verified-entrypoint disassembly plus exact DC data",
        "strict_status": ("pinned builder and exact-byte preservation verified; "
                          "full code/data classification not claimed"),
        "baseline_comparison": "not available for separately relocated multi-unit AP20",
        "warnings": [
            "Rbsr FE31 is an AMOS linker pseudo-op, not Motorola machine code.",
            "The exact AP20 source is byte-perfect DC.W/DC.B, not a symbolic source.",
            "Native unit ASM is a partial mnemonic reconstruction: DC.B may include undecoded code.",
            "AMOS Compiler and WinUAE Gates B/C are NOT validated by export.",
        ],
    }
    target = target.resolve()
    protected = (root / "dist").resolve()
    require(target != protected and protected not in target.parents,
            "refusing to write generated files inside dist/")
    # Pre-check complete generation before creating the output directory.
    sources["AMOSPro_AGA_%s_AP20_EXACT.s" % revision] = exact
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, text in sources.items():
        path = target / filename
        path.write_text(text, encoding="ascii", errors="backslashreplace", newline="\n")
        paths.append(path)

    if assembler:
        for report in reports:
            native_file = target / report["file"]
            output_file = target / (native_file.stem + "_ASSEMBLED.bin")
            assembled = _assemble(assembler, native_file, output_file)
            require(assembled == segments[report["ap20_index"]],
                    "native ASM mismatch at " + native_file.name)
            report["native_assembler_verified"] = True
        source_file = target / ("AMOSPro_AGA_%s_AP20_EXACT.s" % revision)
        output_file = target / ("AMOSPro_AGA_%s_AP20_ASSEMBLED.bin" % revision)
        require(_assemble(assembler, source_file, output_file) == data,
                "exact AP20 vasm output differs from selected .Lib")
        manifest["native_assembler_verified"] = True
    manifest_file = target / ("AMOSPro_AGA_%s_NATIVE.json" % revision)
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8", newline="\n")
    paths.append(manifest_file)
    print("MULTI-UNIT %s: verified SHA/builder and byte-exact AP20 HUNK" % revision)
    for report in reports:
        print("  %-4s group: %5d bytes, %5d mnemonic / %5d raw DC bytes" % (
            report["unit"], report["bytes"], report["mnemonic_bytes"], report["raw_dc_bytes"]))
    print("  ASM source: " + str(target))
    print("  STRICT: pinned binary and exact bytes checked; full mnemonic classification NOT claimed")
    print("  Original .Lib unchanged; assembler/Compiler verification is separate")
    return paths
