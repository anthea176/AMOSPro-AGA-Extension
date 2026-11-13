#!/usr/bin/env python3
"""Read-only Gate A probe for the experimental 34-byte unsigned-offset bridge.

Default: execute the actual 68000 dispatcher with Unicorn, including the
compiler-simulated BSR.W and JSR absolute linkage. --static-only runs just
format, boundary and provenance checks (NOT a CPU Gate A result).
No candidate library, AP20 test artifact, or .asc file is written.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from

from compiler_bridge_v2_probe import (
    DISPATCH_V2, MAX_UNIT_BYTES, is_v2_wrapped,
    unwrap_native_parts_v2, wrap_native_ap20_v2,
)
from compiler_relocation import (
    DISPATCH, GETP, is_compiler_wrapped, repack_ap20,
    unpack_ap20, unwrap_native_parts,
)

ROOT = Path(__file__).resolve().parents[1]
R57_SHA256 = 'aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0'  # Historical deterministic native reference
R58_SHA256 = 'c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b'
R59_SHA256 = '00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d'
R60_SHA256 = '00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8'
LAST_GOOD_SHA256 = 'fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba'  # Promoted R63 LAST_GOOD; historical R60 is rebuilt independently
R61_SHA256 = 'ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f'
R62_SHA256 = '9fede9f8899ff8ec3c4d978a354e30d16b7e40006c854ac96f547098d786d6f6'
R63_SHA256 = 'fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba'
R64_SHA256 = '4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c'
R65_SHA256 = '6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2'
TITLE = b'AP20 bridge V2 probe\0'
TITLE += bytes(len(TITLE) & 1)
TOKENS = b'\0' * 6  # Valid minimal terminated AP20 token table.
TARGET = bytes.fromhex('76634e75')  # MOVEQ #99,D3 ; RTS (valid 68000).


def template() -> bytes:
    return (pack('>5I', 0x3f3, 0, 1, 0, 0) + pack('>I', 0)
            + pack('>I', 0x3e9) + pack('>I', 0) + pack('>I', 0x3f2))


def native_at(offset: int) -> bytes:
    assert offset % 2 == 0 and 0 <= offset <= 65498
    # Synthetic first routine is NOP padding, target is the second routine.
    return repack_ap20(template(), TOKENS,
                       [bytes.fromhex('4e71') * (offset // 2), TARGET], TITLE)


def reject(call, what: str) -> None:
    try:
        call()
    except ValueError:
        return
    raise AssertionError('Expected ValueError: ' + what)


def static_checks() -> tuple[list[tuple[int, bytes]], bytes | None]:
    # 65534 is the maximum WORD-count-derived byte size supported by the
    # unchanged AMOS 365 +APComp.s LSL.W loader. 65536 would wrap to zero.
    assert len(DISPATCH) == 32 and len(DISPATCH_V2) == 34
    assert MAX_UNIT_BYTES == 65534
    tests = []
    offsets = [0, 30000, 32766, 32768, 40000, 65496]
    for off in offsets:
        source = native_at(off)
        v2 = wrap_native_ap20_v2(source, TITLE)
        assert v2 == wrap_native_ap20_v2(source, TITLE)
        assert is_v2_wrapped(v2) and not is_compiler_wrapped(v2)
        tok, native_parts, old_title = unpack_ap20(source)
        vt, entries, title = unpack_ap20(v2)
        assert vt == tok and title == old_title
        assert len(entries) == len(native_parts) + 1 == 3
        assert len(entries[-1]) == len(DISPATCH_V2) + off + len(TARGET)
        assert len(entries[-1]) <= MAX_UNIT_BYTES
        assert entries[1][:4] == b'\xfe\x31' + pack('>H', 2)
        assert unpack_from('>H', entries[1], 4)[0] == off
        assert entries[1][6:8] == b'\x4e\x75'
        assert unwrap_native_parts_v2(v2) == (tok, native_parts)
        reject(lambda: wrap_native_ap20_v2(v2, TITLE), 'V2 double wrap')
        tests.append((off, entries[-1]))
    reject(lambda: wrap_native_ap20_v2(native_at(65498), TITLE), '65536-byte V2 blob')
    # Never silently accept the old C1 bridge into V2 as if it were native.
    from compiler_relocation import wrap_native_ap20
    v1 = wrap_native_ap20(native_at(30000), TITLE)
    reject(lambda: wrap_native_ap20_v2(v1, TITLE), 'V1 double wrap')
    reject(lambda: unwrap_native_parts_v2(v1), 'V1 masquerades as V2')
    # Marker-only entries remain unmodified through the V2 roundtrip.
    marker = repack_ap20(template(), TOKENS, [b'', GETP, TARGET], TITLE)
    check = wrap_native_ap20_v2(marker, TITLE)
    assert unpack_ap20(check)[1][:2] == [b'', GETP]
    assert unwrap_native_parts_v2(check) == (TOKENS, [b'', GETP, TARGET])
    # Force wrong word offset into a V2 stub; strict reverse mapping must fail.
    token, entries, name = unpack_ap20(wrap_native_ap20_v2(native_at(40000), TITLE))
    damaged = list(entries)
    damaged[1] = damaged[1][:4] + pack('>H', 40001) + damaged[1][6:]
    bad = repack_ap20(template(), token, damaged, name)
    reject(lambda: unwrap_native_parts_v2(bad), 'corrupted offset')

    # Rebuild exact historical R57 without treating the newly promoted
    # R59 LAST_GOOD as the old V1 source. All 59 native routines and
    # already validated R57 public stubs must be byte-identical.
    active = ROOT / 'dist/AMOSPro_AGA.Lib'
    last_good = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
    realistic = None
    if active.is_file() or last_good.is_file():
        assert active.is_file() and last_good.is_file(), 'incomplete current/LAST_GOOD fixture'
        current_bytes, protected_bytes = active.read_bytes(), last_good.read_bytes()
        active_hash=sha256(current_bytes).hexdigest()
        assert active_hash in (R60_SHA256,R61_SHA256,R62_SHA256,R63_SHA256,R64_SHA256,R65_SHA256), "Current must be pinned R60/R61/R62/R63"
        from build_m17_r59_compact_v2 import build as build_r59
        assert sha256(build_r59()[0]).hexdigest() == R59_SHA256, "Historical R59 builder changed"
        from build_m18_r60_image_region import build as build_r60
        assert sha256(build_r60()[0]).hexdigest() == R60_SHA256, "Historical R60 deterministic builder mismatch"
        assert sha256(protected_bytes).hexdigest() == LAST_GOOD_SHA256
        if active_hash == R65_SHA256:
            from build_m18_r65_ficon_bank_put import build as build_r65
            assert current_bytes == build_r65()[0] and current_bytes != protected_bytes, (
                "R65 candidate must match pinned builder and preserve R63 LAST_GOOD")
        elif active_hash == R64_SHA256:
            from build_m18_r64_ficon_bank_create import build as build_r64
            assert current_bytes == build_r64()[0] and current_bytes != protected_bytes, (
                "R64 candidate must differ from R63 LAST_GOOD")
        elif active_hash == R63_SHA256:
            from build_m18_r63_chip_blit import build as build_r63
            assert current_bytes == build_r63()[0] and current_bytes == protected_bytes, "Promoted R63 candidate/LAST_GOOD mismatch"
        elif active_hash == R62_SHA256:
            from build_m18_r62_chip_blit import build as build_r62
            assert current_bytes == build_r62()[0] and current_bytes != protected_bytes, "R62 pinned candidate mismatch"
        elif active_hash == R61_SHA256:
            from build_m18_r61_ficon import build as build_r61
            assert current_bytes == build_r61()[0] and current_bytes != protected_bytes, "R61 pinned candidate mismatch"
        else:
            assert current_bytes == protected_bytes, "R60 current mismatch"
        from build_m17_r57_rastport import build as build_r57
        source_bytes, _ = build_r57()
        assert sha256(source_bytes).hexdigest() == R57_SHA256, "R57 historical source changed"
        tokens, original = unwrap_native_parts(source_bytes)
        assert len(original) == 59 and len(tokens) > 6
        old_parts = unpack_ap20(source_bytes)[1]
        original_title = unpack_ap20(source_bytes)[2]
        native = repack_ap20(source_bytes, tokens, original, original_title)
        v2 = wrap_native_ap20_v2(native, original_title)
        vt, entries, title = unpack_ap20(v2)
        assert vt == tokens and title == original_title
        assert entries[:-1] == old_parts[:-1], 'All original public stubs must remain exact'
        assert entries[-1][34:] == old_parts[-1][32:], 'Original native code must remain exact'
        assert len(entries[-1]) == 30782, 'R57 V2 candidate must be only 2 bytes larger'
        assert unwrap_native_parts_v2(v2) == (tokens, original)
        # Real R57 layout plus a synthetic far-away helper, entirely in RAM.
        size = sum(map(len, original))
        assert size == 30748
        pad = 40000 - size
        assert pad > 0 and not pad & 1
        extended = original + [bytes.fromhex('4e71') * (pad // 2), TARGET]
        extended_native = repack_ap20(source_bytes, tokens, extended, original_title)
        extended_v2 = wrap_native_ap20_v2(extended_native, original_title)
        far_segments = unpack_ap20(extended_v2)[1]
        assert unpack_from('>H', far_segments[-2], 4)[0] == 40000
        assert len(far_segments[-1]) == 40038
        assert unwrap_native_parts_v2(extended_v2) == (tokens, extended)
        realistic = far_segments[-1]
        # No generated AP20 is written to disk.
        assert active.read_bytes() == current_bytes and sha256(current_bytes).hexdigest()==active_hash
        assert last_good.read_bytes() == protected_bytes
        assert sha256(protected_bytes).hexdigest() == LAST_GOOD_SHA256
    print('STATIC PASS: V2 AP20 offsets', offsets, 'MAX', MAX_UNIT_BYTES,
          'R57', 'REPACK PASS' if realistic is not None else 'not mounted', flush=True)
    return tests, realistic


def emulate(link: bytes, bridge: bytes, target_offset: int, *, absolute: bool, expected_d3: int = 99) -> None:
    """Run original M68000 instructions, not a Python approximation."""
    from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
    from unicorn.m68k_const import (
        UC_CPU_M68K_M68000, UC_M68K_REG_PC, UC_M68K_REG_SR,
        UC_M68K_REG_A7, UC_M68K_REG_A0, UC_M68K_REG_D0,
        UC_M68K_REG_D2, UC_M68K_REG_D3,
    )
    STUB = 0x80000
    BRIDGE = (0x100000 if absolute else STUB + 8)
    STOP = 0x10000
    STACK = 0x3F0000
    uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    uc.mem_map(0, 0x400000)
    uc.mem_write(STUB, link)
    uc.mem_write(BRIDGE, bridge)
    uc.mem_write(STOP, b'\x4e\x71')
    uc.mem_write(STACK, pack('>I', STOP))
    uc.reg_write(UC_M68K_REG_SR, 0x2000)
    uc.reg_write(UC_M68K_REG_A7, STACK)
    uc.reg_write(UC_M68K_REG_A0, 0x1F00C0)
    uc.reg_write(UC_M68K_REG_D0, 0xA5A51234)
    uc.reg_write(UC_M68K_REG_D2, 0x20313233)
    uc.reg_write(UC_M68K_REG_D3, 0)
    visits = []
    far_pc = BRIDGE + len(DISPATCH_V2) + target_offset
    def trace(_uc, address, size, _user):
        if address == far_pc:
            visits.append(address)
    uc.hook_add(UC_HOOK_CODE, trace)
    uc.emu_start(STUB, STOP, count=200)
    assert visits == [far_pc], '68000 did not reach the requested far native entry'
    assert uc.reg_read(UC_M68K_REG_PC) == STOP, '68000 failed to return normally'
    assert uc.reg_read(UC_M68K_REG_A7) == STACK + 4, 'stack imbalance'
    assert uc.reg_read(UC_M68K_REG_A0) == 0x1F00C0, 'A0 destroyed'
    assert uc.reg_read(UC_M68K_REG_D0) == 0xA5A51234, 'D0 destroyed'
    assert uc.reg_read(UC_M68K_REG_D2) == 0x20313233, 'D2 destroyed'
    assert uc.reg_read(UC_M68K_REG_D3) == expected_d3, 'target result/ABI mismatch'


def cpu_checks(tests: list[tuple[int, bytes]], realistic: bytes | None) -> None:
    try:
        from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
        from unicorn import Uc  # noqa: F401
    except ImportError as exc:
        raise SystemExit('Install capstone==5.0.9 and unicorn==2.1.4 for actual 68000 Gate A') from exc
    dis = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    code = list(dis.disasm(DISPATCH_V2, 0))
    assert sum(x.size for x in code) == 34, 'cannot decode whole M68000 bridge'
    assert any(x.mnemonic.lower().startswith('adda') for x in code)
    assert any(x.mnemonic.lower().startswith('moveq') for x in code)
    assert not any(x.mnemonic.lower() in ('illegal', 'dc.w') for x in code)
    for off, bridge in tests:
        # Compiler's Rbsr marker $FE31 becomes a BSR.W when close.
        rel = bytes.fromhex('61000006') + pack('>H', off) + b'\x4e\x75\x4e\x71'
        emulate(rel, bridge, off, absolute=False)
        # The compiler can also emit a long absolute JSR after relocation.
        abs_link = b'\x4e\xb9' + pack('>I', 0x100000) + pack('>H', off) + b'\x4e\x75'
        emulate(abs_link, bridge, off, absolute=True)
    if realistic is not None:
        off = 40000
        rel = bytes.fromhex('61000006') + pack('>H', off) + b'\x4e\x75\x4e\x71'
        emulate(rel, realistic, off, absolute=False)
        abs_link = b'\x4e\xb9' + pack('>I', 0x100000) + pack('>H', off) + b'\x4e\x75'
        emulate(abs_link, realistic, off, absolute=True)
    print('M68000 CPU PASS:', 2 * len(tests) + (2 if realistic is not None else 0),
          '68k ABI/stack/call tests, real R57 preserved, no generated files', flush=True)
    print('NO new AMOS Compiler/WinUAE Gate C claimed; CPU test only', flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-only', action='store_true', help='NO CPU Gate A; skip Unicorn')
    args = parser.parse_args()
    cases, realistic = static_checks()
    if not args.static_only:
        cpu_checks(cases, realistic)
    else:
        print('STATIC ONLY: not a real CPU nor a WinUAE result', flush=True)


if __name__ == '__main__':
    main()
