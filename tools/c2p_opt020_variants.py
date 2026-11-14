"""Experimental MC68020 C2P hot-loop variants; NEVER a released binary.

These wrappers call immutable historical R78/R79/R80 emitters, replace one
entry into a hot loop with BRA.W and append new position-independent code.
No original emitter, pinned Rxx builder, dist binary, or current ASC is changed.
The historical callable entry, argument validation, bank checks and cleanup
remain byte-for-byte untouched except for the four-byte loop-entry branch.

Activation requires a separately approved future builder and native CPU tests.
"""
from __future__ import annotations

from struct import pack, unpack_from
from m68k_emit import Code, D, A, M, I, POST
from c2p_r78_blit_emit import emit_blit, F as BLIT_FRAME
from c2p_r79_zoom_emit import emit_zoom, F as ZOOM_FRAME
from c2p_r80_iff_chunky_emit import emit_iff_to_chunky
from build_m5_generic import BODY


def _signed_word(delta: int) -> bytes:
    if not -32768 <= delta <= 32767:
        raise ValueError("BRA.W displacement outside signed 16-bit range")
    return pack(">h", delta)


def _dbra(c: Code, register: int, target: str) -> None:
    c.word(0x51C8 | register)
    c.fix.append((len(c.b), target))
    c.word(0)


def _external_jump(c: Code) -> int:
    """Reserve a BRA.W to an original entry offset; return extension location."""
    c.word(0x6000)
    extension = len(c.b)
    c.word(0)
    return extension


def _hook(original: bytes, labels: dict, at: str, expected: bytes,
          tail: Code, external_extension: int, return_offset: int) -> tuple[bytes, dict]:
    """Append a native subroutine, linking both branches PC-relatively.

    Both jumps use the address of the displacement word as PC reference.
    Only a four-byte entry instruction is replaced; the rest is immutable.
    """
    pos = labels[at]
    if len(expected) != 4 or original[pos:pos + 4] != expected:
        raise ValueError(f"unexpected historical opcode at {at}; refusing patch")
    appended = bytearray(tail.out())
    if appended[external_extension - 2:external_extension] != b"\x60\x00":
        raise ValueError("invalid external return BRA.W")
    appended[external_extension:external_extension + 2] = _signed_word(
        return_offset - (len(original) + external_extension))
    patched = bytearray(original)
    patched[pos:pos + 4] = b"\x60\x00" + _signed_word(len(original) - (pos + 2))
    patched.extend(appended)
    out_labels = dict(labels)
    out_labels[f"{at}_opt020"] = len(original)
    return bytes(patched), out_labels


def emit_blit_opt020() -> tuple[bytes, dict]:
    """R78: MOVE.L for groups of four indices, then 0..3 byte tail.

    68020 accepts unaligned longword source/destination in Amiga memory.
    Original clipping, bank bounds, and non-overlap checks are unchanged.
    """
    old, labels = emit_blit()
    c = Code()
    B, L = c.branch, c.label
    L("row")
    c.move(M(2, BLIT_FRAME["w"]), D(6))
    c.move(D(6), D(5))
    c.imm("and", 3, D(5))
    c.shift(6, 2)  # LSR.L #2,D6: width // 4
    c.tst(D(6))
    B(7, "bytes")
    c.quick(1, D(6), sub=True)
    L("longs")
    c.move(POST(0), POST(1), "l")  # MOVE.L (A0)+,(A1)+
    _dbra(c, 6, "longs")
    L("bytes")
    c.tst(D(5))
    B(7, "next_row")
    c.quick(1, D(5), sub=True)
    L("byte_tail")
    c.move(POST(0), POST(1), "b")
    _dbra(c, 5, "byte_tail")
    L("next_row")
    c.move(M(2, BLIT_FRAME["srcskip"]), D(0))
    c.move(A(0), D(1))
    c.alu("add", D(0), 1)
    c.move(D(1), A(0))
    c.move(M(2, BLIT_FRAME["dstskip"]), D(0))
    c.move(A(1), D(1))
    c.alu("add", D(0), 1)
    c.move(D(1), A(1))
    _dbra(c, 7, "row")
    c.move(I(1), D(3))
    external = _external_jump(c)
    return _hook(old, labels, "copy_row", bytes.fromhex("2c2a000c"),
                 c, external, labels["finish"])


def emit_zoom_opt020() -> tuple[bytes, dict]:
    """R79: hoist DDA quotient/remainder/denominator out of per-pixel loop.

    Nearest-neighbour mapping, clipping, all preflight and vertical math are
    unchanged. D1, D2, D5 are caller-saved across the full native entry.
    """
    old, labels = emit_zoom()
    c = Code()
    B, L = c.branch, c.label
    c.move(M(2, ZOOM_FRAME["xquot"]), D(5))
    c.move(M(2, ZOOM_FRAME["xrem"]), D(2))
    c.move(M(2, ZOOM_FRAME["dstw"]), D(1))
    L("pixel_fast")
    c.move(M(0), M(1), "b")
    c.quick(1, A(1))
    c.word(0xD1C5)  # ADDA.L D5,A0 (source index quotient)
    c.alu("add", D(2), 4)  # err += xrem
    c.alu("cmp", D(1), 4)
    B(5, "no_carry")
    c.alu("sub", D(1), 4)
    c.quick(1, A(0))
    L("no_carry")
    _dbra(c, 6, "pixel_fast")
    external = _external_jump(c)
    # First instruction is MOVE.B (A0),(A1), followed by ADDQ.L #1,A1.
    # The historical DBRA at x_no_carry is bypassed; continue after it.
    return _hook(old, labels, "pixel", bytes.fromhex("12905289"),
                 c, external, labels["x_no_carry"] + 4)


def _nibble_lut() -> bytes:
    """Nibble bits 3..0 expanded into 4 bytes containing 0 or 1."""
    return b"".join(bytes((n >> shift) & 1 for shift in (3, 2, 1, 0))
                    for n in range(16))


def emit_iff_chunky_opt020() -> tuple[bytes, dict]:
    """R80: 020 scaled-index LUT, 4 pixels per OR.L, no per-bit branches.

    Keep both existing BODY passes, full-file validation, 40-byte row buffer
    and output-zeroing. The new loop only replaces the bit expansion phase.
    """
    old, labels = emit_iff_to_chunky()
    c = Code()
    B, L = c.branch, c.label
    c.lea(6, "nibble_lut")  # LEA (d16,PC),A6; cleanup restores DOS A6
    L("byte_fast")
    c.word(0x7000)  # MOVEQ #0,D0 (guarantee 32-bit unsigned index)
    c.move(POST(3), D(0), "b")
    c.move(D(0), D(1))
    c.shift(0, 4)  # LSR.L #4,D0 -> high nibble
    c.raw("20360c00")  # MOVE.L (A6,D0.L*4),D0 (68020 scaled index)
    c.word(0xEDA8)  # LSL.L D6,D0 (bitplane position)
    c.word(0x819C)  # OR.L D0,(A4)+; 4 destination indices
    c.move(D(1), D(0))
    c.imm("and", 15, D(0))
    c.raw("20360c00")  # MOVE.L (A6,D0.L*4),D0
    c.word(0xEDA8)
    c.word(0x819C)
    _dbra(c, 2, "byte_fast")
    external = _external_jump(c)
    c.label("nibble_lut")
    c.b.extend(_nibble_lut())
    result, result_labels = _hook(
        old, labels, "byte_start", bytes.fromhex("101b0800"),
        c, external, labels["plane_done"])

    # The historical R80 decoder did not need a CPU guard: it was 68000
    # compatible. Add a 68000-safe feature gate before its first BODY pass,
    # so a 68000/010 exits with 0 and untouched destination bank. The
    # original chunky_decode MOVEM prologue remains live and balanced.
    guard = Code()
    B, L = guard.branch, guard.label
    guard.raw("20780004")  # MOVE.L 4.W,A0; ExecBase pointer
    guard.move(A(0), D(0))
    guard.tst(D(0))
    B(7, "unsupported")
    guard.move(I(0), D(0))
    guard.move(M(0, 0x128), D(0), "w")  # ExecBase.AttnFlags
    guard.word(0x0800)  # BTST #AFF_68020,D0
    guard.word(1)
    B(7, "unsupported")
    guard.move(M(5, BODY), A(0))  # replay overwritten MOVE.L BODY(A5),A0
    continue_ext = _external_jump(guard)
    L("unsupported")
    refuse_ext = _external_jump(guard)
    guard_bytes = bytearray(guard.out())
    guard_start = len(result)
    for ext, target in ((continue_ext, labels["chunky_decode"] + 8),
                        (refuse_ext, labels["fail_chunky_decode"])):
        guard_bytes[ext:ext + 2] = _signed_word(
            target - (guard_start + ext))
    guard_site = labels["chunky_decode"] + 4  # immediately after MOVEM
    expected = Code()
    expected.move(M(5, BODY), A(0))
    if len(expected.out()) != 4 or result[guard_site:guard_site + 4] != expected.out():
        raise ValueError("R80 chunky_decode prologue drift; refusing CPU guard")
    result = bytearray(result)
    result[guard_site:guard_site + 4] = (
        b"\x60\x00" + _signed_word(guard_start - (guard_site + 2)))
    result.extend(guard_bytes)
    result_labels["chunky_decode_cpu_guard_opt020"] = guard_start
    return bytes(result), result_labels


__all__ = ["emit_blit_opt020", "emit_zoom_opt020", "emit_iff_chunky_opt020"]
