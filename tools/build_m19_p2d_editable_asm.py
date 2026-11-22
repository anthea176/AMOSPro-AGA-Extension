#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Link an editable handwritten P2d Bob controls module into the P2d AP20 ASM.

This is an incremental native-source migration, not a production promotion.
Remaining units are the verified P2d audit-assembly baseline until migrated.
Only builds into a user-specified output directory. No writes into dist/.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from functools import lru_cache
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from active_library import P2D_SHA
from build_m19_p2d_in_memory import build_p2d
from build_m19_p1e_bank_edit_in_memory import build_p1e
from compiler_relocation import unpack_ap20
from audit_ap20 import inspect, parse
from m19_p2d_bob_auto_update_emit import emit_bob_auto_update
from m19_p2b_bob_flip_emit import emit_bob_flip
from m19_p2b_planar_orientation020_emit import emit_planar_orientation020
from m19_p2a_collision020_emit import emit_collision020
from m19_p2a_pair_chip_resolve_emit import emit_p2a_pair_chip_resolve
from m19_p2a_pair_hotspot020_emit import emit_p2a_pair_hotspot020
from m19_p2a_pair_geometry020_emit import emit_p2a_pair_geometry020
from m19_p2a_pair_checked_read_emit import emit_p2a_pair_checked_read
from m19_p0i_multibank_draw_emit import emit_multibank_paint
from m19_b8_b7_hook_emit import emit_b8_b7_hooks
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free
from m19_p0j_end_lifecycle_emit import emit_end_lifecycle
from m19_p1b_hotspot_origin_emit import emit_hotspot_origin
from m19_p1c_bob_priority_emit import emit_priority_bobs
from m19_p0e_object_table_emit import emit_object_table

AUDIT_DIR = ROOT / 'src' / 'asm_migration' / 'm19_p2d'
EDITABLE_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2D_CONTROLS_MC68020.s'
PLANES_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2C_PLANES_MC68020.s'
FLIP_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_FLIP_PUBLIC_MC68020.s'
VARIANT_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_VARIANT_ANCHOR_MC68020.s'
PAINT_GEO_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_PAINT_GEOMETRY_MC68020.s'
CLEANUP_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_CLEANUP_MC68020.s'
PUBLIC_COL_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2A_PUBLIC_COL_MC68020.s'
QUERY_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2A_COLLISION_QUERY_MC68020.s'
KERNEL_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2A_COLLISION_KERNEL_MC68020.s'
CHIP_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2A_CHIP_RESOLVE_MC68020.s'
HOTSPOT_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2A_HOTSPOT_MC68020.s'
GEOMETRY_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2A_GEOMETRY_MC68020.s'
PAIR_CHECK_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2A_PAIR_CHECK_MC68020.s'
P0I_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P0I_ROUTED_PAINT_MC68020.s'
B8_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_B8_END_REGISTER_MC68020.s'
B8S1_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_B8S1_BANK_FREE_MC68020.s'
B7_END_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_B7_END_MC68020.s'
P1B_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P1B_HOTSPOT_ORIGIN_MC68020.s'
P1C_PRIORITY_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P1C_PRIORITY_MC68020.s'
P1C_DISPATCH_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P1C_FRAME_DISPATCH_MC68020.s'
P1C_CONTEXT_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P1C_CONTEXT_MC68020.s'
P1C_PRE_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P1C_FRAME_PREFLIGHT_MC68020.s'
P1C_COL_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P1C_ORDER_COLLECT_MC68020.s'
PLANAR_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_PLANAR_MC68020.s'
SLOTS_FILE = ROOT / 'src' / 'native' / 'm19_p2d' / 'M19_P2B_SLOTS_DATA_MC68020.s'
BOBS_FILE = 'M19_P2D_BOBS_MC68020.s'
MASTER_FILE = 'M19_P2D_AP20_SOURCE.s'
SOURCE_NAME = 'M19_P2D_CONTROLS_MC68020.s'
START_LABEL = 'p2d_public_auto_update:'
END_LABEL = 'L_BOBS_0B72A:'
P2C_START_LABEL = 'p2c_public_planes:'
P2C_END_LABEL = 'ENTRY_BOBS_0B58C:'
P2C_SOURCE_NAME = 'M19_P2C_PLANES_MC68020.s'
FLIP_SOURCE_NAME = 'M19_P2B_FLIP_PUBLIC_MC68020.s'
FLIP_START = 0x9E36
FLIP_END = 0x9F26
VARIANT_SOURCE_NAME = 'M19_P2B_VARIANT_ANCHOR_MC68020.s'
VARIANT_START = 0x9F26
VARIANT_END = 0xA0AA
PAINT_GEO_SOURCE_NAME = 'M19_P2B_PAINT_GEOMETRY_MC68020.s'
PAINT_GEO_START = 0xA0AA
PAINT_GEO_END = 0xA1D2
CLEANUP_SOURCE_NAME = 'M19_P2B_CLEANUP_MC68020.s'
CLEANUP_START = 0xA1D2
CLEANUP_END = 0xA28E
PUBLIC_COL_NAME = 'M19_P2A_PUBLIC_COL_MC68020.s'
PUBLIC_COL_START = 0x9D38
PUBLIC_COL_END = 0x9E36
QUERY_SOURCE_NAME = 'M19_P2A_COLLISION_QUERY_MC68020.s'
QUERY_START = 0x9B54
QUERY_END = 0x9D38
KERNEL_SOURCE_NAME = 'M19_P2A_COLLISION_KERNEL_MC68020.s'
KERNEL_START = 0x9858
KERNEL_END = 0x9B54
CHIP_NAME = 'M19_P2A_CHIP_RESOLVE_MC68020.s'
CHIP_START = 0x8BB6
CHIP_END = 0x8E20
HOTSPOT_NAME = 'M19_P2A_HOTSPOT_MC68020.s'
HOTSPOT_START = 0x8E20
HOTSPOT_END = 0x918A
GEOMETRY_NAME = 'M19_P2A_GEOMETRY_MC68020.s'
GEOMETRY_START = 0x918A
GEOMETRY_END = 0x9858
PAIR_CHECK_NAME = 'M19_P2A_PAIR_CHECK_MC68020.s'
PAIR_CHECK_START = 0x8A6E
PAIR_CHECK_END = 0x8BB6
P0I_NAME = 'M19_P0I_ROUTED_PAINT_MC68020.s'
P0I_START = 0x5CF8
P0I_END = 0x5F30
B8_NAME = 'M19_B8_END_REGISTER_MC68020.s'
B8_START = 0x71EE
B8_END = 0x7364
B8S1_NAME = 'M19_B8S1_BANK_FREE_MC68020.s'
B8S1_START = 0x76A8
B8S1_END = 0x7962
B7_END_NAME = 'M19_B7_END_MC68020.s'
B7_END_START = 0x6EAC
B7_END_END = 0x6FA6
P1B_NAME = 'M19_P1B_HOTSPOT_ORIGIN_MC68020.s'
P1B_START = 0x7A14
P1B_END = 0x7AC2
P1C_PRIORITY_NAME = 'M19_P1C_PRIORITY_MC68020.s'
P1C_PRIORITY_START = 0x7B84
P1C_PRIORITY_END = 0x7BBA
P1C_DISPATCH_NAME = 'M19_P1C_FRAME_DISPATCH_MC68020.s'
P1C_DISPATCH_START = 0x7AC2
P1C_DISPATCH_END = 0x7AE8
P1C_CONTEXT_NAME = 'M19_P1C_CONTEXT_MC68020.s'
P1C_CONTEXT_START = 0x7AE8
P1C_CONTEXT_END = 0x7B84
P1C_PRE_NAME = 'M19_P1C_FRAME_PREFLIGHT_MC68020.s'
P1C_PRE_START = 0x7BBA
P1C_PRE_END = 0x7C18
P1C_COL_NAME = 'M19_P1C_ORDER_COLLECT_MC68020.s'
P1C_COL_START = 0x7C18
P1C_COL_END = 0x7C98
PLANAR_SOURCE_NAME = 'M19_P2B_PLANAR_MC68020.s'
SLOTS_SOURCE_NAME = 'M19_P2B_SLOTS_DATA_MC68020.s'
PLANAR_START = 0xA28E
PLANAR_END = 0xA4C0


class SourceError(RuntimeError):
    pass


def require(test: bool, reason: str) -> None:
    if not test:
        raise SourceError(reason)


def checked_vasm(assembler: Path, source: Path, output: Path) -> bytes:
    """Assemble Motorola source with a real MC68020 target, no optimization."""
    require(assembler.is_file(), f'vasm not found: {assembler}')
    cmd = [str(assembler.resolve()), '-Fbin', '-m68020', '-no-opt',
           '-quiet', '-o', str(output.resolve()), source.name]
    result = subprocess.run(cmd, cwd=source.parent, capture_output=True,
                            text=True, check=False)
    require(result.returncode == 0,
            f'vasm return {result.returncode} on {source.name}:\n'
            f'{result.stdout}\n{result.stderr}')
    require(output.is_file(), 'vasm returned success without an output file')
    return output.read_bytes()


@lru_cache(maxsize=1)
def prove_source_provenance() -> tuple[bytes, int, int, int, int, int, int]:
    """Require exact P2d native builder and exact source-region boundaries."""
    lib = (ROOT / 'dist' / 'AMOSPro_AGA.Lib').read_bytes()
    good = (ROOT / 'dist' / 'AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    require(len(lib) == 136020 and sha256(lib).hexdigest() == P2D_SHA,
            'official P2d source is not the selected 136020-byte baseline')
    require(good == lib, 'LAST_GOOD differs from P2d; refused')
    rebuilt, info = build_p2d()
    require(rebuilt == lib and info['sha256'] == P2D_SHA,
            'native Python builder does not reproduce the official P2d')
    _, parts, _ = unpack_ap20(lib)
    group = info['group']
    _, p1e_info = build_p1e()
    native, labels, service_off = emit_bob_auto_update(p1e_info['context_delta'])
    require(parts[group].endswith(native), 'native BOBS suffix diverged')
    prefix = len(parts[group]) - len(native)
    start = prefix + labels['p2d_public_auto_update']
    end = prefix + service_off
    done = prefix + labels['p2d_set_done']
    planes = prefix + labels['p2c_public_planes']
    planes_fail = prefix + labels['p2c_set_fail']
    require((planes, planes_fail, start - planes) == (0xB4C4, 0xB52E, 200),
            'P2c planes native module boundaries changed')
    require((start, end, end-start) == (0xB58C, 0xB72A, 414),
            f'P2d handwritten module boundaries changed: {start:x}:{end:x}')
    require(parts[group][done:done+2] == bytes.fromhex('7601'),
            'expected two-byte moveq #1,d3 at p2d_set_done missing')
    return lib, group, planes, start, end, done, planes_fail


@lru_cache(maxsize=1)
def prove_planar_provenance() -> tuple[int, int, int, bytes]:
    """The exact P2b materializer bytes come from the Python source emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    context = p1e['context_delta']
    # The original P2b unit is the exact prefix of the subsequently extended P2d.
    full, labels = emit_bob_flip(context)
    fragment, frag_labels = emit_planar_orientation020()
    _, parts, _ = unpack_ap20(original)
    native, _, _ = emit_bob_auto_update(context)
    base = len(parts[group]) - len(native)
    start = base + labels['p2b_owner'] - len(fragment)
    end = base + labels['p2b_owner']
    require((start, end) == (PLANAR_START, PLANAR_END),
            f'P2b planar source offsets changed: {start:x}..{end:x}')
    require(parts[group][start:end] == fragment,
            'P2b handwritten source ancestry differs from official P2d')
    require(full[labels['p2b_owner'] - len(fragment):labels['p2b_owner']] == fragment,
            'P2b materializer not adjacent to owned slots')
    require('invalid' in frag_labels, 'P2b invalid label absent')
    return start, end, start + frag_labels['invalid'], fragment


@lru_cache(maxsize=1)
def prove_flip_public_provenance() -> tuple[int, int, int, bytes]:
    """Pin the public Flip / slot-cache block to its original P2b emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels = emit_bob_flip(p1e['context_delta'])
    _, parts, _ = unpack_ap20(original)
    base = PLANAR_END - labels['p2b_owner']
    start = base + labels['p2b_slot']
    public = base + labels['p2b_public_flip']
    end = base + labels['p2b_variant']
    failure = base + labels['p2b_flip_fail']
    require((start, public, failure, end) ==
            (FLIP_START, 0x9E96, 0x9F12, FLIP_END),
            'source P2b Flip public offsets differ from pinned P2d')
    fragment = native[labels['p2b_slot']:labels['p2b_variant']]
    require(len(fragment) == FLIP_END - FLIP_START and
            parts[group][start:end] == fragment,
            'P2b Flip module is not identical to source emitter')
    return start, end, failure, fragment


def replace_raw_flip_public(text: str) -> str:
    """Replace exactly 240 annotated audit bytes, including mixed DC.B/code."""
    anchor = 'L_BOBS_09E36:\np2b_slot:\n'
    first = text.find(anchor)
    last = text.find('p2b_variant:\n', first)
    require(first >= 0 and last > first and
            text.find(anchor, first + len(anchor)) < 0,
            'unique P2b Flip public/variant boundary not found')
    old = text[first:last]
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', old)
    require(matches and
            'ENTRY_BOBS_09E96:\np2b_public_flip:' in old and
            'p2b_flip_fail:' in old,
            'P2b public Flip audit labels missing')
    cursor = FLIP_START
    data = bytearray()
    for offset, value in matches:
        require(int(offset, 16) == cursor,
                'P2b Flip audit offsets are no longer contiguous')
        chunk = bytes.fromhex(value)
        data.extend(chunk)
        cursor += len(chunk)
    require(cursor == FLIP_END and
            bytes(data) == prove_flip_public_provenance()[3],
            'P2b public Flip raw/code bytes differ from authoritative emitter')
    return (text[:first] + 'L_BOBS_09E36:\n    include "' +
            FLIP_SOURCE_NAME + '"\n' + text[last:])


@lru_cache(maxsize=1)
def prove_p2b_variant_provenance() -> tuple[int, int, int, bytes]:
    """Resolve variant/anchor bytes from the original P2b Python emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels = emit_bob_flip(p1e['context_delta'])
    base = PLANAR_END - labels['p2b_owner']
    begin = base + labels['p2b_variant']
    end = base + labels['p2b_paint']
    failure = base + labels['p2b_variant_fail']
    require((begin, end, failure) == (VARIANT_START, VARIANT_END, 0xA06C),
            'P2b variant/anchor emitter positions differ from P2d')
    fragment = native[labels['p2b_variant']:labels['p2b_paint']]
    _, parts, _ = unpack_ap20(original)
    require(len(fragment) == end - begin and
            parts[group][begin:end] == fragment,
            'P2b variant/anchor differs from authoritative emitter')
    return begin, end, failure, fragment


def replace_raw_p2b_variant(text: str) -> str:
    """Remove only the complete, source-verified variant/anchor raw region."""
    begin = text.find('p2b_variant:\n')
    end = text.find('L_BOBS_0A0AA:\np2b_paint:\n', begin)
    require(begin >= 0 and end > begin and
            text.find('p2b_variant:\n', begin+12) < 0,
            'P2b variant raw slice missing or duplicated')
    raw = text[begin:end]
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', raw)
    require(matches and 'p2b_variant_publish:' in raw,
            'P2b variant original audit evidence missing')
    offset, evidence = VARIANT_START, bytearray()
    for pos, hex_bytes in matches:
        require(int(pos, 16) == offset,
                f'P2b variant annotation not contiguous: {pos}')
        value = bytes.fromhex(hex_bytes)
        evidence.extend(value)
        offset += len(value)
    require(offset == VARIANT_END and
            bytes(evidence) == prove_p2b_variant_provenance()[3],
            'P2b variant region does not match original source emitter')
    return (text[:begin] + '    include "' + VARIANT_SOURCE_NAME +
            '"\n' + text[end:])


@lru_cache(maxsize=1)
def prove_p2b_paint_geo_provenance() -> tuple[int, int, int, bytes]:
    """Derive exact painter and pair geometry source bytes from P2b emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels = emit_bob_flip(p1e['context_delta'])
    base = PLANAR_END - labels['p2b_owner']
    begin = base + labels['p2b_paint']
    end = base + labels['p2b_close_return']
    fail = base + labels['p2b_geometry_fail']
    require((begin, end, fail) == (PAINT_GEO_START, PAINT_GEO_END, 0xA1C4),
            'P2b paint/geometry emitter labels differ from pinned P2d')
    fragment = native[labels['p2b_paint']:labels['p2b_close_return']]
    _, parts, _ = unpack_ap20(original)
    require(len(fragment) == end - begin and
            parts[group][begin:end] == fragment,
            'P2b paint/geometry mismatch with source emitter')
    return begin, end, fail, fragment


def replace_raw_p2b_paint_geo(text: str) -> str:
    """Replace only source-proven annotated P2b paint and geometry bytes."""
    start_tag = 'L_BOBS_0A0AA:\np2b_paint:\n'
    end_tag = 'L_BOBS_0A1D2:\np2b_close_return:\n'
    begin = text.find(start_tag)
    end = text.find(end_tag, begin)
    require(begin >= 0 and end > begin and
            text.find(start_tag, begin+len(start_tag)) < 0,
            'P2b paint/geometry audit labels missing')
    old = text[begin:end]
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', old)
    require('p2b_paint_hotspot:' in old and matches,
            'P2b original paint/geometry witness incomplete')
    offset, evidence = PAINT_GEO_START, bytearray()
    for pos, encoded in matches:
        require(int(pos,16) == offset,
                f'P2b paint/geometry unexpected offset: {pos}')
        block = bytes.fromhex(encoded)
        evidence.extend(block)
        offset += len(block)
    require(offset == PAINT_GEO_END and
            bytes(evidence) == prove_p2b_paint_geo_provenance()[3],
            'P2b paint/geometry differs from native P2b source')
    return (text[:begin] + 'L_BOBS_0A0AA:\n    include "' +
            PAINT_GEO_SOURCE_NAME + '"\n' + text[end:])


@lru_cache(maxsize=1)
def prove_p2b_cleanup_provenance() -> tuple[int, int, int, bytes]:
    """Verify close/bank-free/purge 188 bytes against original P2b source."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    original_flip, labels = emit_bob_flip(p1e['context_delta'])
    native, _, _ = emit_bob_auto_update(p1e['context_delta'])
    planar, _ = emit_planar_orientation020()
    base = PLANAR_END - labels['p2b_owner']
    begin = base + labels['p2b_close_return']
    end = base + labels['p2b_owner'] - len(planar)
    bank_return = base + labels['p2b_bank_free_return']
    require((begin, end, bank_return) == (CLEANUP_START, CLEANUP_END, 0xA24E),
            'P2b cleanup emitter offsets changed')
    original_bytes = native[labels['p2b_close_return']:
                            labels['p2b_owner']-len(planar)]
    # P2d replaces the old P2b close epilogue with BRA.W p2d_close; NOP.
    old = original_flip[labels['p2b_close_return']:
                        labels['p2b_owner']-len(planar)]
    close_hook = labels['p2b_close_restore']-labels['p2b_close_return']
    clear_hook = labels['p2b_clear_mode']-labels['p2b_close_return']
    require(old[close_hook:close_hook+6] == bytes.fromhex('4cdf7fff4e75') and
            old[clear_hook:clear_hook+6] == bytes.fromhex('26bc00000000'),
            'P2b original close/clear opcodes differ from source emitter')
    # P2c patches all-slot clear to reset slot + planes (BSR/NOP);
    # P2d patches full-register close to guarded close (BRA/NOP).
    require(len(original_bytes) == len(old) and
            original_bytes[close_hook:close_hook+2] == b'\x60\x00' and
            original_bytes[clear_hook:clear_hook+2] == b'\x61\x00' and
            original_bytes[close_hook+4:close_hook+6] == b'\x4e\x71' and
            original_bytes[clear_hook+4:clear_hook+6] == b'\x4e\x71' and
            all(x == y for i,(x,y) in enumerate(zip(old,original_bytes))
                if not (close_hook <= i < close_hook+6 or
                        clear_hook <= i < clear_hook+6)),
            'P2b lifecycle differs beyond the two classified P2c/P2d hooks')
    _, parts, _ = unpack_ap20(original)
    require(len(original_bytes) == end-begin and
            parts[group][begin:end] == original_bytes,
            'P2b cleanup source emitter differs from P2d reference')
    return begin, end, bank_return, original_bytes


def replace_raw_p2b_cleanup(text: str) -> str:
    """Replace source-proven P2b close/bank-free/purge before planar include."""
    anchor = 'L_BOBS_0A1D2:\np2b_close_return:\n'
    terminator = '    include "' + PLANAR_SOURCE_NAME + '"\n'
    begin = text.find(anchor)
    end = text.find(terminator, begin)
    require(begin >= 0 and end > begin and
            'p2b_purge:' in text[begin:end], 'P2b cleanup audit missing')
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                         text[begin:end])
    require(matches, 'P2b cleanup source bytes not annotated')
    offset, collected = CLEANUP_START, bytearray()
    for position, encoded in matches:
        require(int(position,16) == offset,
                f'P2b cleanup non-contiguous: {position}')
        blob = bytes.fromhex(encoded)
        collected.extend(blob)
        offset += len(blob)
    require(offset == CLEANUP_END and
            bytes(collected) == prove_p2b_cleanup_provenance()[3],
            'P2b cleanup raw region diverged from authoritative source')
    return (text[:begin] + 'L_BOBS_0A1D2:\n    include "' +
            CLEANUP_SOURCE_NAME + '"\n' + text[end:])


@lru_cache(maxsize=1)
def prove_p2a_public_provenance() -> tuple[int, int, int, bytes]:
    """Pin Bob Col public entry to P2a emitter WITH P2b geometry callback."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    _, parts, _ = unpack_ap20(original)
    prefix = len(parts[group]) - len(native)
    begin = prefix + labels['p2a_public_bob_col']
    end = prefix + labels['p2b_slot']
    result_moveq = 0x9E32
    require((begin, end) == (PUBLIC_COL_START, PUBLIC_COL_END),
            'P2a public source offsets differ from pinned P2d')
    fragment = native[labels['p2a_public_bob_col']:labels['p2b_slot']]
    require(len(fragment) == end-begin and
            parts[group][begin:end] == fragment and
            parts[group][result_moveq:result_moveq+2] == b'\x74\x00',
            'P2a public Bob Col differs from P2d source emitter')
    return begin, end, result_moveq, fragment


def replace_raw_p2a_public(text: str) -> str:
    """Only replace exact source-authored P2a public Bob Col bytes."""
    anchor = 'ENTRY_BOBS_09D38:\np2a_public_bob_col:\n'
    end_tag = 'L_BOBS_09E36:\np2b_slot:\n'
    first = text.find(anchor)
    end = text.find(end_tag, first)
    require(first >= 0 and end > first,
            'P2a public Bob Col audit source boundaries missing')
    original = text[first:end]
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', original)
    require(matches, 'P2a public Bob Col annotated bytes missing')
    pos, data = PUBLIC_COL_START, bytearray()
    for at, chunk in matches:
        require(int(at,16) == pos,
                f'P2a public annotations not contiguous: {at}')
        data.extend(bytes.fromhex(chunk))
        pos += len(chunk)//2
    require(pos == PUBLIC_COL_END and
            bytes(data) == prove_p2a_public_provenance()[3],
            'P2a public audit bytes differ from verified emitter')
    return (text[:first] + 'ENTRY_BOBS_09D38:\n    include "' +
            PUBLIC_COL_NAME + '"\n' + text[end:])


@lru_cache(maxsize=1)
def prove_p2a_query_provenance() -> tuple[int, int, int, bytes]:
    """Resolve collision orchestration from original P2a source emitters."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(native)
    begin = base + labels['p2a_collision_query_entry']
    end = base + labels['p2a_public_bob_col']
    result_moveq = 0x9D34
    require((begin, end) == (QUERY_START, QUERY_END),
            'P2a collision query emitter positions differ from P2d')
    fragment = native[labels['p2a_collision_query_entry']:
                      labels['p2a_public_bob_col']]
    require(len(fragment) == end-begin and
            parts[group][begin:end] == fragment and
            parts[group][result_moveq:result_moveq+2] == b'\x74\x00',
            'P2a collision query differs from source-emitter contract')
    return begin, end, result_moveq, fragment


def replace_raw_p2a_query(text: str) -> str:
    """Replace exact source-proven query bytes after kernel's six-byte tail."""
    first_line = ('    dc.b $77,$F7,$74,$00,$4E,$75,$2F,$0B,$48,$E7,$EF,$EE'
                  '  ; +$09B4E: 77F774004E752F0B48E7EFEE\n')
    begin = text.find(first_line)
    end = text.find('ENTRY_BOBS_09D38:\np2a_public_bob_col:\n',begin)
    require(begin >= 0 and end > begin,
            'P2a query original raw source boundary missing')
    region = text[begin:end]
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', region)
    pos, data = 0x9B4E, bytearray()
    for offset, words in matches:
        require(int(offset,16) == pos,
                f'P2a collision query original bytes missing at {pos:05X}')
        chunk = bytes.fromhex(words)
        data.extend(chunk)
        pos += len(chunk)
    require(pos == QUERY_END and
            data[:6] == bytes.fromhex('77f774004e75') and
            data[6:] == prove_p2a_query_provenance()[3],
            'P2a query audit bytes do not match the native source emitter')
    return (text[:begin] +
            '    dc.b $77,$F7,$74,$00,$4E,$75  ; +$09B4E: 77F774004E75\n'
            '    include "' + QUERY_SOURCE_NAME + '"\n' +
            text[end:])


@lru_cache(maxsize=1)
def prove_p2a_kernel_provenance() -> tuple[int, int, int, bytes]:
    """Compare native P2a mask kernel to its original dedicated Python emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    full, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    kernel, kernel_labels = emit_collision020()
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(full)
    begin = base + labels['p2a_pair_entry']
    end = base + labels['p2a_collision_query_entry']
    invalid = begin + kernel_labels['p2a_invalid']
    require((begin, end, invalid) == (KERNEL_START, KERNEL_END, 0x9B42),
            'P2a collision kernel source offsets changed')
    require(len(kernel) == end-begin and
            full[labels['p2a_pair_entry']:labels['p2a_collision_query_entry']]
            == kernel and parts[group][begin:end] == kernel,
            'P2a collision kernel differs from dedicated source emitter')
    return begin, end, invalid, kernel


def replace_raw_p2a_kernel(text: str) -> str:
    """Replace P2a kernel, preserving its preceding 10-byte geometry tail."""
    anchor = ('    dc.b $01,$00,$4C,$DF,$77,$F7,$74,$00,$4E,$75,$48,$E7'
              '  ; +$0984E: 01004CDF77F774004E7548E7\n')
    tail = ('    dc.b $77,$F7,$74,$00,$4E,$75'
            '  ; +$09B4E: 77F774004E75\n')
    start = text.find(anchor)
    stop = text.find(tail,start)
    require(start >= 0 and stop > start and
            text[stop+len(tail):].startswith(
                '    include "'+QUERY_SOURCE_NAME+'"'),
            'P2a kernel source/already-converted query boundary missing')
    evidence = text[start:stop+len(tail)]
    annotations = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                              evidence)
    pos, blob = 0x984E, bytearray()
    for off, code in annotations:
        require(int(off,16) == pos,
                'P2a kernel source byte annotations not contiguous')
        data = bytes.fromhex(code)
        blob.extend(data)
        pos += len(data)
    require(pos == KERNEL_END and
            blob[:10] == bytes.fromhex('01004cdf77f774004e75') and
            blob[10:] == prove_p2a_kernel_provenance()[3],
            'P2a kernel audit region not equal to source emitter')
    return (text[:start] +
            '    dc.b $01,$00,$4C,$DF,$77,$F7,$74,$00,$4E,$75'
            '  ; +$0984E: 01004CDF77F774004E75\n' +
            '    include "' + KERNEL_SOURCE_NAME + '"\n' +
            text[stop+len(tail):])


@lru_cache(maxsize=1)
def prove_p2a_chip_provenance() -> tuple[int, int, int, bytes]:
    """Pin original P2a pair/Chip resolver to verified source emitter bytes."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    full, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    chip, chip_labels = emit_p2a_pair_chip_resolve()
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(full)
    begin = base + labels['p2a_pair_chip_resolve_entry']
    end = base + labels['p2a_pair_hotspot_entry']
    epilogue = end - 4
    require((begin, end, epilogue) ==
            (CHIP_START, CHIP_END, 0x8E1C),
            'P2a Chip resolver source offsets differ from P2d')
    fragment = chip[chip_labels['p2a_pair_chip_resolve_entry']:]
    require(len(fragment) == end-begin and
            full[labels['p2a_pair_chip_resolve_entry']:
                 labels['p2a_pair_hotspot_entry']] == fragment and
            parts[group][begin:end] == fragment and
            fragment[-4:] == bytes.fromhex('74004e75'),
            'P2a Chip resolver cannot be reproduced from source')
    return begin, end, epilogue, fragment


def replace_raw_p2a_chip(text: str) -> str:
    """Replace P2a Chip resolver, preserving two mixed audit boundary rows."""
    head = ('    dc.b $74,$00,$4E,$75,$48,$E7,$EF,$EE,$4F,$EF,$FF,$00'
            '  ; +$08BB2: 74004E7548E7EFEE4FEFFF00\n')
    tail = ('    dc.b $01,$00,$4C,$DF,$77,$F7,$74,$00,$4E,$75,$48,$E7'
            '  ; +$08E16: 01004CDF77F774004E7548E7\n')
    first = text.find(head)
    last = text.find(tail, first)
    require(first >= 0 and last > first,
            'P2a Chip resolver source audit boundaries missing')
    original = text[first:last + len(tail)]
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                         original)
    pos, collected = 0x8BB2, bytearray()
    for at, data in matches:
        require(int(at,16) == pos,
                f'P2a Chip source offsets not contiguous at {at}')
        b = bytes.fromhex(data)
        collected.extend(b)
        pos += len(b)
    require(pos == CHIP_END + 2 and
            collected[:4] == bytes.fromhex('74004e75') and
            collected[-2:] == bytes.fromhex('48e7') and
            collected[4:-2] == prove_p2a_chip_provenance()[3],
            'P2a Chip audit bytes do not match source emitter')
    return (text[:first] +
            '    dc.b $74,$00,$4E,$75  ; +$08BB2: 74004E75\n' +
            '    include "' + CHIP_NAME + '"\n' +
            '    dc.b $48,$E7  ; +$08E20: 48E7\n' +
            text[last+len(tail):])


@lru_cache(maxsize=1)
def prove_p2a_hotspot_provenance() -> tuple[int, int, int, bytes]:
    """Pin the original signed P1b hotspot reader source in the final P2d."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    hotspot, internal_labels = emit_p2a_pair_hotspot020()
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(native)
    begin = base + labels['p2a_pair_hotspot_entry']
    end = base + labels['p2a_pair_geometry_entry']
    moveq = end - 4
    require((begin, end, moveq) ==
            (HOTSPOT_START, HOTSPOT_END, 0x9186),
            'P2a hotspot emitter offsets differ from P2d')
    require(internal_labels['p2a_pair_hotspot_entry'] == 0 and
            len(hotspot) == end-begin and
            native[labels['p2a_pair_hotspot_entry']:
                   labels['p2a_pair_geometry_entry']] == hotspot and
            parts[group][begin:end] == hotspot and
            hotspot[-4:] == b'\x74\x00\x4e\x75',
            'P2a hotspot source does not match official P2d')
    return begin, end, moveq, hotspot


def replace_raw_p2a_hotspot(text: str) -> str:
    """Replace 874 source-proven hotspot bytes between two mixed audit rows."""
    start = '    dc.b $48,$E7  ; +$08E20: 48E7\n'
    end = ('    dc.b $4C,$DF,$77,$F7,$74,$00,$4E,$75,$48,$E7,$EF,$EE'
           '  ; +$09182: 4CDF77F774004E7548E7EFEE\n')
    i = text.find(start)
    j = text.find(end, i)
    require(i >= 0 and j > i,
            'P2a hotspot mixed audit boundaries missing')
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                         text[i:j+len(end)])
    address, collected = HOTSPOT_START, bytearray()
    for where, chunk in matches:
        require(int(where,16) == address,
                'P2a hotspot byte annotations not contiguous')
        data = bytes.fromhex(chunk)
        collected.extend(data)
        address += len(data)
    require(address == HOTSPOT_END+4 and
            collected[:-4] == prove_p2a_hotspot_provenance()[3] and
            collected[-4:] == bytes.fromhex('48e7efee'),
            'P2a hotspot audit bytes differ from source emitter')
    return (text[:i] + '    include "' + HOTSPOT_NAME + '"\n' +
            '    dc.b $48,$E7,$EF,$EE  ; +$0918A: 48E7EFEE\n' +
            text[j+len(end):])


@lru_cache(maxsize=1)
def prove_p2a_geometry_provenance() -> tuple[int, int, int, bytes]:
    """Pin the 1742-byte P2a source-emitter geometry builder to P2d."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    full, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    geometry, geom_labels = emit_p2a_pair_geometry020()
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(full)
    begin = base + labels['p2a_pair_geometry_entry']
    end = base + labels['p2a_pair_entry']
    moveq = end-4
    require((begin, end, moveq) ==
            (GEOMETRY_START, GEOMETRY_END, 0x9854),
            'P2a geometry label offsets differ from known P2d')
    require(geom_labels['p2a_pair_geometry_entry'] == 0 and
            len(geometry) == end-begin and
            full[labels['p2a_pair_geometry_entry']:
                 labels['p2a_pair_entry']] == geometry and
            parts[group][begin:end] == geometry and
            geometry[-4:] == b'\x74\x00\x4e\x75',
            'P2a geometry source does not reproduce P2d')
    return begin, end, moveq, geometry


def replace_raw_p2a_geometry(text: str) -> str:
    """Replace source-verified geometry, including both mixed audit rows."""
    first = '    dc.b $48,$E7,$EF,$EE  ; +$0918A: 48E7EFEE\n'
    last = ('    dc.b $01,$00,$4C,$DF,$77,$F7,$74,$00,$4E,$75'
            '  ; +$0984E: 01004CDF77F774004E75\n')
    i = text.find(first)
    j = text.find(last,i)
    require(i >= 0 and j > i, 'P2a geometry audit source boundaries missing')
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                         text[i:j+len(last)])
    address, data = GEOMETRY_START, bytearray()
    for at, hexbytes in matches:
        require(int(at,16) == address,
                'P2a geometry audit offsets not contiguous')
        blob = bytes.fromhex(hexbytes)
        data.extend(blob)
        address += len(blob)
    require(address == GEOMETRY_END and
            bytes(data) == prove_p2a_geometry_provenance()[3],
            'P2a geometry original bytes differ from native emitter')
    return (text[:i] + '    include "' + GEOMETRY_NAME + '"\n' +
            text[j+len(last):])


@lru_cache(maxsize=1)
def prove_p2a_pair_check_provenance() -> tuple[int, int, int, bytes]:
    """Verify original P2a checked pair-read source before Chip staging."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    pair, pair_labels = emit_p2a_pair_checked_read()
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(native)
    begin = base + labels['p2a_pair_checked_read_entry']
    end = base + labels['p2a_pair_chip_resolve_entry']
    moveq = end - 4
    require((begin, end, moveq) ==
            (PAIR_CHECK_START, PAIR_CHECK_END, 0x8BB2),
            'P2a checked pair-read source positions differ from P2d')
    require(pair_labels['p2a_pair_checked_read_entry'] == 0 and
            len(pair) == end-begin and
            native[labels['p2a_pair_checked_read_entry']:
                   labels['p2a_pair_chip_resolve_entry']] == pair and
            parts[group][begin:end] == pair and
            pair[-4:] == b'\x74\x00\x4e\x75',
            'P2a checked pair source emitter differs from official P2d')
    return begin, end, moveq, pair


def replace_raw_p2a_pair_check(text: str) -> str:
    """Replace annotated checked-read, ending at Chip resolver include."""
    begin_tag = 'p2a_pair_checked_read_entry:\n'
    end_tag = '    include "' + CHIP_NAME + '"\n'
    first = text.find(begin_tag)
    end = text.find(end_tag, first)
    require(first >= 0 and end > first and
            'p2a_pair_fail:' in text[first:end],
            'P2a pair-check audit source missing')
    match = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                       text[first:end])
    position, old = PAIR_CHECK_START, bytearray()
    for at, byteword in match:
        require(int(at,16) == position,
                'P2a checked-read annotations not contiguous')
        blob = bytes.fromhex(byteword)
        old.extend(blob)
        position += len(blob)
    require(position == PAIR_CHECK_END and
            bytes(old) == prove_p2a_pair_check_provenance()[3],
            'P2a pair checked-read audit bytes differ from source')
    return (text[:first] + '    include "' + PAIR_CHECK_NAME +
            '"\n' + text[end:])


@lru_cache(maxsize=1)
def prove_p0i_paint_provenance() -> tuple[int, int, int, bytes]:
    """Verify old P0i bank route directly against original MC68020 emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    routed, route_labels = emit_multibank_paint()
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(native)
    begin = base + labels['routed_paint_one_entry']
    end = base + labels['image_frame_preflight_entry']
    moveq = end - 4
    require((begin, end, moveq) ==
            (P0I_START, P0I_END, 0x5F2C),
            'P0i routed painter source positions differ from final P2d')
    fragment = routed[route_labels['routed_paint_one_entry']:]
    require(len(fragment) == end-begin and
            native[labels['routed_paint_one_entry']:
                   labels['image_frame_preflight_entry']] == fragment and
            parts[group][begin:end] == fragment and
            fragment[-4:] == b'\x74\x00\x4e\x75',
            'P0i router is not source-identical to final P2d')
    return begin, end, moveq, fragment


def replace_raw_p0i_paint(text: str) -> str:
    """Source-backed conversion of 568 bytes of private painter/route code."""
    first_label = 'routed_paint_one_entry:\n'
    end_label = 'L_BOBS_05F30:\nimage_frame_preflight_entry:\n'
    first = text.find(first_label)
    last = text.find(end_label, first)
    require(first >= 0 and last > first and
            'routed_paint_all_entry:' in text[first:last],
            'P0i router source evidence missing')
    annotations = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                              text[first:last])
    pos, assembled = P0I_START, bytearray()
    for where, code in annotations:
        require(int(where,16) == pos,
                f'P0i source audit offsets not contiguous: {where}')
        raw = bytes.fromhex(code)
        assembled.extend(raw)
        pos += len(raw)
    require(pos == P0I_END and
            bytes(assembled) == prove_p0i_paint_provenance()[3],
            'P0i painter audit bytes differ from authoritative emitter')
    return (text[:first] + '    include "' + P0I_NAME +
            '"\n' + text[last:])


@lru_cache(maxsize=1)
def prove_b8_end_register_provenance() -> tuple[int, int, int, bytes]:
    """Source-prove B8 End/registrar with P2b patched guarded cleanup."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    original_b8, b8_labels = emit_b8_b7_hooks()
    _, parts, _ = unpack_ap20(original)
    prefix = len(parts[group]) - len(native)
    begin = prefix + labels['b8_b7_end_trampoline_entry']
    end = prefix + labels['b8_b7_hook_root'] + 8
    return_site = prefix + labels['b8_b7_end_return']
    mutable_byte = prefix + labels['b8_b7_register_arm'] + 17
    require((begin, end, return_site, mutable_byte) ==
            (B8_START, B8_END, 0x7272, 0x7339),
            'B8 lifecycle source offsets differ from final P2d')
    original_fragment = original_b8[
        b8_labels['b8_b7_end_trampoline_entry']:
        b8_labels['b8_b7_hook_root'] + 8]
    patched = bytearray(original_fragment)
    delta = return_site - begin
    require(patched[delta:delta+6] == bytes.fromhex('4cdf7fff4e75'),
            'B8 original full-register End epilogue changed')
    patched[delta:delta+6] = bytes.fromhex('60002f5e4e75')
    fragment = native[labels['b8_b7_end_trampoline_entry']:
                      labels['b8_b7_hook_root']+8]
    require(len(fragment) == end-begin and
            bytes(patched) == fragment and
            parts[group][begin:end] == fragment and
            fragment[0x7278-begin:0x727C-begin] == b'B8RG' and
            fragment[-8:] == b'\x00'*8,
            'B8 End/registrar does not match emitter plus P2b source hook')
    return begin, end, mutable_byte, fragment


def replace_raw_b8_end_register(text: str) -> str:
    """Only replace the source-verified B8 End/Registrar and 12 data bytes."""
    before = 'L_BOBS_071EE:\nb8_b7_end_trampoline_entry:\n'
    after = 'L_BOBS_07364:\nb8_b7_arm_end_nodraw_entry:\n'
    i = text.find(before)
    j = text.find(after, i)
    require(i >= 0 and j > i and
            'b8_b7_hook_root:\n' in text[i:j] and
            'b8_b7_clear_root:\n' in text[i:j],
            'B8 lifecycle audit source labels missing')
    matches = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                         text[i:j])
    pos, collected = B8_START, bytearray()
    for where, data in matches:
        require(int(where,16) == pos,
                'B8 lifecycle native source audit is not contiguous')
        blob = bytes.fromhex(data)
        collected.extend(blob)
        pos += len(blob)
    require(pos == B8_END and
            bytes(collected) == prove_b8_end_register_provenance()[3],
            'B8 lifecycle audit bytes differ from source emitter')
    return (text[:i] + 'L_BOBS_071EE:\n    include "' +
            B8_NAME + '"\n' + text[j:])


@lru_cache(maxsize=1)
def prove_b8s1_bank_free_provenance() -> tuple[int, int, int, bytes]:
    """Pin Bank Free source and the P2b cache purge redirection."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    final, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    bank_source, bank_labels = emit_b8_s1_bank_free()
    _, object_labels = emit_object_table()
    require((object_labels['object_root'], object_labels['object_table'])
            == (0x314, 0x31C),
            'source P0e object root/table relative offsets drifted')
    _, parts, _ = unpack_ap20(original)
    prefix = len(parts[group]) - len(final)
    begin = prefix + labels['b8s1_bank_free_entry']
    end = prefix + labels['p1b_image_hotspot_join']
    result = prefix + labels['b8s1_bank_free_return']
    release = prefix + labels['b8s1_bank_free_release']
    require((begin, end, result, release) ==
            (B8S1_START, B8S1_END, 0x7952, 0x793A),
            'B8 S1 Free source positions differ from pinned P2d')
    first = bank_labels['b8s1_bank_free_entry']
    old = bank_source[first:]
    final_bytes = final[labels['b8s1_bank_free_entry']:
                        labels['p1b_image_hotspot_join']]
    patch_at = release - begin + 6  # MOVE.L bank,D3 + MOVEA.L gfx,A4.
    require(len(old) == end-begin and
            old[patch_at:patch_at+2] == b'\x61\x00' and
            final_bytes[patch_at:patch_at+4] ==
            bytes.fromhex('610028e6') and
            all(x == y for i,(x,y) in enumerate(zip(old,final_bytes))
                if not (patch_at <= i < patch_at+4)),
            'B8 S1 source differs outside the P2b Free-cache hook')
    require(parts[group][begin:end] == final_bytes,
            'B8 S1 Free version in official P2d differs from emitter')
    return begin, end, result-3, final_bytes


def replace_raw_b8s1_bank_free(text: str) -> str:
    """Replace 698 annotated bytes with the source-verified Bank Free module."""
    first_tag = 'b8s1_bank_free_entry:\n'
    last_tag = 'L_BOBS_07962:\np1b_image_hotspot_join:\n'
    begin = text.find(first_tag)
    end = text.find(last_tag, begin)
    require(begin >= 0 and end > begin,
            'B8 S1 Bank Free annotated source boundaries missing')
    lines = text[begin:end]
    rows = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', lines)
    require(len(rows) > 50,
            'B8 S1 Bank Free no longer contains the pinned raw source')
    addr, found = B8S1_START, bytearray()
    for at, chunk in rows:
        require(int(at,16) == addr,
                f'B8 S1 Bank Free original bytes discontinuous at {at}')
        raw = bytes.fromhex(chunk)
        found.extend(raw)
        addr += len(raw)
    require(addr == B8S1_END and
            bytes(found) == prove_b8s1_bank_free_provenance()[3],
            'B8 S1 Bank Free raw bytes differ from source-emitter contract')
    return (text[:begin] + '    include "' + B8S1_NAME +
            '"\n' + text[end:])


@lru_cache(maxsize=1)
def prove_b7_end_provenance() -> tuple[int, int, int, bytes]:
    """Pin original P0j End procedure including P2b close redirect."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    b7_source, b7_labels = emit_end_lifecycle()
    _, parts, _ = unpack_ap20(original)
    prefix = len(parts[group]) - len(native)
    begin = prefix + labels['b7_end_entry']
    end = prefix + labels['b7_multiframe_draw_entry']
    ret = prefix + labels['b7_end_return']
    mutation_byte = 0x6F6D
    require((begin, end, ret) == (B7_END_START, B7_END_END, 0x6FA0),
            'P0j B7 End source positions differ from final P2d')
    old = b7_source[b7_labels['b7_end_entry']:]
    fragment = native[labels['b7_end_entry']:
                      labels['b7_multiframe_draw_entry']]
    patch_at = ret - begin
    require(len(old) == end-begin and
            old[patch_at:patch_at+6] == bytes.fromhex('4cdf7fff4e75') and
            fragment[patch_at:patch_at+6] ==
            bytes.fromhex('600032304e75') and
            all(x==y for i,(x,y) in enumerate(zip(old,fragment))
                if not patch_at <= i < patch_at+6),
            'P0j B7 End differs outside the P2b owner-cleanup source patch')
    require(parts[group][begin:end] == fragment and
            fragment[mutation_byte-begin-5:mutation_byte-begin+3] ==
            bytes.fromhex('217c000000000004'),
            'P0j B7 End source/edited immediate location differs from P2d')
    return begin, end, mutation_byte, fragment


def replace_raw_b7_end(text: str) -> str:
    """Convert only the original 250-byte P0j End region to source module."""
    first = 'L_BOBS_06EAC:\nb7_end_entry:\n'
    last = 'L_BOBS_06FA6:\nb7_multiframe_draw_entry:\n'
    i = text.find(first)
    j = text.find(last,i)
    require(i >= 0 and j > i, 'P0j B7 End boundaries missing from audit')
    raw = text[i:j]
    annotated = re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)',
                           raw)
    pos, expected = B7_END_START, bytearray()
    for where, encoded in annotated:
        require(int(where,16) == pos,
                f'P0j B7 End non-contiguous audit offset {where}')
        block = bytes.fromhex(encoded)
        expected.extend(block)
        pos += len(block)
    require(pos == B7_END_END and
            bytes(expected) == prove_b7_end_provenance()[3],
            'P0j B7 End raw code differs from source emitters')
    return (text[:i] + 'L_BOBS_06EAC:\n    include "' + B7_END_NAME +
            '"\n' + text[j:])


@lru_cache(maxsize=1)
def prove_p1b_origin_provenance() -> tuple[int, int, int, bytes]:
    """Source-prove the P1b 174-byte signed HotSpot origin helper."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    source, src_labels = emit_hotspot_origin()
    _, parts, _ = unpack_ap20(original)
    begin = len(parts[group]) - len(native) + labels['p1b_hotspot_origin_entry']
    end = begin + len(source)
    mutation = 0x7AAD
    require((begin, end) == (P1B_START, P1B_END) and
            src_labels['p1b_hotspot_origin_entry'] == 0,
            'P1b hotspot source range differs from P2d')
    fragment = native[labels['p1b_hotspot_origin_entry']:
                      labels['p1b_hotspot_origin_entry'] + len(source)]
    require(len(source) == 174 and fragment == source and
            parts[group][begin:end] == source and
            source[mutation-begin-5:mutation-begin+1] ==
            bytes.fromhex('263c00000001'),
            'P1b hotspot source differs from original emitter or P2d')
    return begin, end, mutation, source


def replace_raw_p1b_origin(text: str) -> str:
    """Preserve 10 prefix bytes, replace exactly 174 emitter-owned bytes."""
    first = '    dc.b $00,$00,$00,$01,$00,$74,$60,$00,$D5,$FA,$2F,$00  ; +$07A0A: 0000000100746000D5FA2F00\n'
    last = 'L_BOBS_07AC2:\np1c_frame_dispatch:\n'
    i, j = text.find(first), text.find(last, text.find(first))
    require(i >= 0 and j > i, 'P1b raw audit boundaries absent')
    offset, verified = 0x7A0A, bytearray()
    for at, encoded in re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', text[i:j]):
        require(int(at, 16) == offset, 'P1b raw offset discontinuity')
        chunk = bytes.fromhex(encoded)
        verified.extend(chunk)
        offset += len(chunk)
    require(offset == P1B_END and
            bytes(verified[:10]) == bytes.fromhex('0000000100746000d5fa') and
            bytes(verified[10:]) == prove_p1b_origin_provenance()[3],
            'P1b audit bytes mismatch authoritative source emitter')
    return (text[:i] +
            '    dc.b $00,$00,$00,$01,$00,$74,$60,$00,$D5,$FA  ; +$07A0A: 0000000100746000D5FA\n'
            '    include "' + P1B_NAME + '"\n' + text[j:])


@lru_cache(maxsize=1)
def prove_p1c_priority_provenance() -> tuple[int, int, int, bytes]:
    """Verify all 54 priority bytes against original MC68020 source."""
    official, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    p1c, p1c_labels = emit_priority_bobs(p1e['context_delta'])
    _, parts, _ = unpack_ap20(official)
    prefix = len(parts[group]) - len(native)
    begin = prefix + labels['p1c_priority_entry']
    end = prefix + labels['explicit_frame_draw_entry']
    fragment = p1c[p1c_labels['p1c_priority_entry']:
                   p1c_labels['explicit_frame_draw_entry']]
    mutation = 0x7BA7
    require((begin, end) == (P1C_PRIORITY_START, P1C_PRIORITY_END) and
            len(fragment) == 54 and
            native[labels['p1c_priority_entry']:
                   labels['explicit_frame_draw_entry']] == fragment and
            parts[group][begin:end] == fragment and
            fragment[mutation-begin-5:mutation-begin+1] == bytes.fromhex('263c00000001'),
            'P1c priority source/emitter/P2d byte contract differs')
    return begin, end, mutation, fragment


def replace_raw_p1c_priority(text: str) -> str:
    """Convert only verified P1c priority code and retain AP20 ENTRY label."""
    first = 'ENTRY_BOBS_07B84:\np1c_priority_entry:\n'
    last = 'L_BOBS_07BBA:\nexplicit_frame_draw_entry:\n'
    i, j = text.find(first), text.find(last, text.find(first))
    require(i >= 0 and j > i, 'P1c priority audit boundaries missing')
    pos, code = P1C_PRIORITY_START, bytearray()
    for at, encoded in re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', text[i:j]):
        require(int(at, 16) == pos, 'P1c priority annotated bytes discontinuous')
        chunk = bytes.fromhex(encoded)
        code.extend(chunk)
        pos += len(chunk)
    require(pos == P1C_PRIORITY_END and
            bytes(code) == prove_p1c_priority_provenance()[3],
            'P1c priority annotated bytes differ from source emitter')
    return (text[:i] + 'ENTRY_BOBS_07B84:\n    include "' +
            P1C_PRIORITY_NAME + '"\n' + text[j:])


@lru_cache(maxsize=1)
def prove_p1c_dispatch_provenance() -> tuple[int, int, int, bytes]:
    """Verify the original 38-byte priority-aware frame dispatcher."""
    official, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    p1c, p1c_labels = emit_priority_bobs(p1e['context_delta'])
    _, parts, _ = unpack_ap20(official)
    prefix = len(parts[group]) - len(native)
    begin = prefix + labels['p1c_frame_dispatch']
    end = prefix + labels['p1c_context']
    fragment = p1c[p1c_labels['p1c_frame_dispatch']:
                   p1c_labels['p1c_context']]
    mutation = 0x7AE3
    require((begin, end) == (P1C_DISPATCH_START, P1C_DISPATCH_END) and
            len(fragment) == 38 and
            native[labels['p1c_frame_dispatch']:
                   labels['p1c_context']] == fragment and
            parts[group][begin:end] == fragment and
            fragment[mutation-begin-3:mutation-begin+1] == bytes.fromhex('4fefff60'),
            'P1c dispatch source/emitter/P2d byte contract differs')
    return begin, end, mutation, fragment


def replace_raw_p1c_dispatch(text: str) -> str:
    """Convert only the verified 38-byte P1c dispatch."""
    first = 'L_BOBS_07AC2:\np1c_frame_dispatch:\n'
    last = 'L_BOBS_07AE8:\np1c_context:\n'
    i, j = text.find(first), text.find(last, text.find(first))
    require(i >= 0 and j > i, 'P1c dispatch audit boundaries missing')
    pos, code = P1C_DISPATCH_START, bytearray()
    for at, encoded in re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', text[i:j]):
        require(int(at, 16) == pos, 'P1c dispatch annotated bytes discontinuous')
        chunk = bytes.fromhex(encoded)
        code.extend(chunk)
        pos += len(chunk)
    require(pos == P1C_DISPATCH_END and
            bytes(code) == prove_p1c_dispatch_provenance()[3],
            'P1c dispatch annotated bytes differ from source emitter')
    return (text[:i] + 'L_BOBS_07AC2:\n    include "' +
            P1C_DISPATCH_NAME + '"\n' + text[j:])


@lru_cache(maxsize=1)
def prove_p1c_context_provenance() -> tuple[int, int, int, bytes]:
    """Pin P1c 156-byte State owner/type check and priority-mode reader."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    emitted, emitted_labels = emit_priority_bobs(p1e['context_delta'])
    _, parts, _ = unpack_ap20(original)
    prefix = len(parts[group]) - len(native)
    begin = prefix + labels['p1c_context']
    end = prefix + labels['p1c_priority_entry']
    fragment = emitted[emitted_labels['p1c_context']:
                       emitted_labels['p1c_priority_entry']]
    mutation = 0x7B71
    require((begin, end) == (P1C_CONTEXT_START, P1C_CONTEXT_END) and
            len(fragment) == 156 and p1e['context_delta'] == 0xEF08 and
            native[labels['p1c_context']:labels['p1c_priority_entry']] == fragment and
            parts[group][begin:end] == fragment and
            fragment[mutation-begin-5:mutation-begin+1] ==
            bytes.fromhex('207c00000000'),
            'P1c owner context origin source differs from the P2d binary')
    return begin, end, mutation, fragment


def replace_raw_p1c_context(text: str) -> str:
    """Replace only 156 source-matched P1c context bytes."""
    first = 'L_BOBS_07AE8:\np1c_context:\n'
    last = 'ENTRY_BOBS_07B84:\n'
    i, j = text.find(first), text.find(last, text.find(first))
    require(i >= 0 and j > i, 'P1c context audit boundaries missing')
    pos, code = P1C_CONTEXT_START, bytearray()
    for at, encoded in re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', text[i:j]):
        require(int(at, 16) == pos, 'P1c context source annotation offset drift')
        part = bytes.fromhex(encoded)
        code.extend(part)
        pos += len(part)
    require(pos == P1C_CONTEXT_END and
            bytes(code) == prove_p1c_context_provenance()[3],
            'P1c context audit bytes are not source-authored')
    return (text[:i] + 'L_BOBS_07AE8:\n    include "' +
            P1C_CONTEXT_NAME + '"\n' + text[j:])


@lru_cache(maxsize=1)
def prove_p1c_frame_preflight_provenance() -> tuple[int, int, int, bytes]:
    """Prove P1c 94-byte frame preparation against original code emitter."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    p1c, src_labels = emit_priority_bobs(p1e['context_delta'])
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(native)
    begin = base + labels['explicit_frame_draw_entry']
    end = base + labels['p1c_collect']
    expected = p1c[src_labels['explicit_frame_draw_entry']:
                   src_labels['p1c_collect']]
    mutation = 0x7C05
    require((begin, end) == (P1C_PRE_START, P1C_PRE_END) and
            len(expected) == 94 and
            native[labels['explicit_frame_draw_entry']:labels['p1c_collect']] == expected and
            parts[group][begin:end] == expected and
            expected[mutation-begin-5:mutation-begin+3] ==
            bytes.fromhex('257c00000001002c'),
            'P1c frame preflight source does not match P2d original')
    return begin, end, mutation, expected


def replace_raw_p1c_frame_preflight(text: str) -> str:
    """Replace only the 94 source-verified bytes of P1c frame setup."""
    first = 'L_BOBS_07BBA:\nexplicit_frame_draw_entry:\n'
    last = 'L_BOBS_07C18:\np1c_collect:\n'
    i, j = text.find(first), text.find(last, text.find(first))
    require(i >= 0 and j > i, 'P1c frame preflight audit boundaries missing')
    pos, found = P1C_PRE_START, bytearray()
    for at, encoded in re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', text[i:j]):
        require(int(at, 16) == pos, 'P1c preflight annotation gap')
        chunk = bytes.fromhex(encoded)
        found.extend(chunk)
        pos += len(chunk)
    require(pos == P1C_PRE_END and bytes(found) == prove_p1c_frame_preflight_provenance()[3],
            'P1c preflight annotated ASM differs from source emitter')
    return (text[:i] + 'L_BOBS_07BBA:\n    include "' +
            P1C_PRE_NAME + '"\n' + text[j:])


@lru_cache(maxsize=1)
def prove_p1c_order_collect_provenance() -> tuple[int, int, int, bytes]:
    """Prove 128 priority key/insert-sort bytes from PriorityTraversal."""
    original, group, *_ = prove_source_provenance()
    _, p1e = build_p1e()
    native, labels, _ = emit_bob_auto_update(p1e['context_delta'])
    p1c, src_labels = emit_priority_bobs(p1e['context_delta'])
    _, parts, _ = unpack_ap20(original)
    base = len(parts[group]) - len(native)
    begin = base + labels['p1c_collect']
    end = base + labels['explicit_frame_next']
    expected = p1c[src_labels['p1c_collect']:src_labels['explicit_frame_next']]
    mutation = 0x7C95
    require((begin, end) == (P1C_COL_START, P1C_COL_END) and
            len(expected) == 128 and
            native[labels['p1c_collect']:labels['explicit_frame_next']] == expected and
            parts[group][begin:end] == expected and
            expected[mutation-begin-5:mutation-begin+3] ==
            bytes.fromhex('257c000000000020'),
            'P1c collection/insertion original source differs from official P2d')
    return begin, end, mutation, expected


def replace_raw_p1c_order_collect(text: str) -> str:
    """Replace the P1c key ordering loop, preserving external BOBS symbols."""
    first = 'L_BOBS_07C18:\np1c_collect:\n'
    last = 'L_BOBS_07C98:\nexplicit_frame_next:\n'
    i, j = text.find(first), text.find(last, text.find(first))
    require(i >= 0 and j > i, 'P1c collect audit boundaries missing')
    pos, found = P1C_COL_START, bytearray()
    for at, encoded in re.findall(r'; \+\$([0-9A-F]{5}): ([0-9A-F]+)', text[i:j]):
        require(int(at, 16) == pos, 'P1c collect annotation gap')
        chunk = bytes.fromhex(encoded)
        found.extend(chunk)
        pos += len(chunk)
    require(pos == P1C_COL_END and
            bytes(found) == prove_p1c_order_collect_provenance()[3],
            'P1c sorted key loop differs from source emission')
    return (text[:i] + 'L_BOBS_07C18:\n    include "' +
            P1C_COL_NAME + '"\n' + text[j:])


def replace_raw_planar_block(text: str) -> str:
    """Replace only the source-pinned 562-byte DC.B block, not other data."""
    first_line = ('    dc.b $53,$85,$66,$00,$FF,$DA,$4E,$75,$48,$E7,$CF,$FE'
                  '  ; +$0A286: 53856600FFDA4E75' + '48E7CFFE\n')
    # The source audit records a 12-byte line at $A286. The first eight
    # bytes close p2b_purge; the next four begin the materializer.
    # Keep the prefix as bytes, then insert the actual handwritten source.
    start = text.find(first_line)
    require(start >= 0, 'P2b source bytes at $A286 are not the pinned baseline')
    stop = text.find('L_BOBS_0A4C0:', start)
    require(stop > start, 'P2b owner data label missing after materializer')
    original_block = text[start:stop]
    lines = original_block.splitlines()
    require(len(lines) > 40 and all('dc.b ' in line for line in lines),
            'P2b materializer is not a contiguous unclassified data block')
    hexdump = ''.join(line.split('  ; +$')[1].split(': ')[1]
                      for line in lines)
    expected = bytes.fromhex(hexdump)
    require(len(expected) == PLANAR_END - 0xA286,
            'unclassified materializer byte coverage changed')
    require(expected[:8] == bytes.fromhex('53856600ffda4e75'),
            'P2b purge epilogue changed')
    require(expected[8:] == prove_planar_provenance()[3],
            'unclassified bytes differ from original P2b code emitter')
    replacement = ('    dc.b $53,$85,$66,$00,$FF,$DA,$4E,$75'
                   '  ; +$0A286: 53856600FFDA4E75\n'
                   '    include "' + PLANAR_SOURCE_NAME + '"\n')
    return text[:start] + replacement + text[stop:]


def replace_raw_p2b_slot_data(text: str) -> str:
    """Convert source-proven 4-byte owner + 4096-byte object table from raw."""
    anchor = 'L_BOBS_0A4C0:\np2b_owner:\n'
    first = text.find(anchor)
    last = text.find('ENTRY_BOBS_0B4C4:', first)
    require(first >= 0 and last > first,
            'BOBS 64-slot zeroed data has changed from the source baseline')
    lines = text[first + len(anchor):last].splitlines()
    require(len(lines) > 300 and all(line.startswith('    dc.b ') for line in lines),
            'raw P2b slots are not a contiguous zeroed data region')
    hexdump = ''.join(line.split('  ; +$')[1].split(': ')[1]
                      for line in lines)
    values = bytes.fromhex(hexdump)
    require(len(values) == 4 + 64 * 64 and not any(values),
            'BOBS p2b_owner/p2b_slots bytes differ from emitter zeros')
    return (text[:first] + 'L_BOBS_0A4C0:\n    include "' +
            SLOTS_SOURCE_NAME + '"\n' + text[last:])


def replace_source_backed_amos_pseudo(text: str) -> str:
    """Convert source-pinned AMOS Main pseudo ops, not MC68020 instructions."""
    from amos_main_abi import main_index, rjsr
    definitions = ('; Original AMOS Main rjsr indices '
                   '(source tools/amos_main_abi.py).\n'
                   'AMOS_MAIN_GETADR     equ 797\n'
                   'AMOS_MAIN_CHANGE     equ 819\n'
                   'AMOS_MAIN_LIST_CREATE equ 91\n'
                   'AMOS_MAIN_LIST_DELETE equ 93\n')
    marker = '; AGA_NATIVE_MIN_CPU: MC68020\n'
    require(marker in text, 'BOBS MC68020 marker missing')
    table = (('Bnk.GetAdr','GETADR',797,20),
             ('Bnk.Change','CHANGE',819,2),
             ('Lst.Cree','LIST_CREATE',91,2),
             ('Lst.Del','LIST_DELETE',93,4))
    pattern = re.compile(r'(?m)^    dc\.b [^\n]*  ; \+\$([0-9A-F]{5}): '
                         r'(FE11F700[0-9A-F]{4})$')
    records = list(pattern.finditer(text))
    require(len(records)==28, 'AMOS Main pseudo call count changed')
    for command, alias, index, count in table:
        signature = rjsr(index).hex().upper()
        require(main_index(command)==index and
                signature=='FE11F700'+f'{index:04X}',
                'AMOS Main source index drift: '+command)
        occurrences = [x for x in records if x.group(2)==signature]
        require(len(occurrences)==count,
                'AMOS Main source call count drift: '+command)
        for record in occurrences:
            line=('    dc.w $FE11,$F700,AMOS_MAIN_'+alias+
                  '  ; +$'+record.group(1)+': '+record.group(2))
            text=text.replace(record.group(0),line,1)
    return text.replace(marker,marker+definitions,1)


def staged_sources(folder: Path, *, module_text: str | None = None,
                   planes_text: str | None = None,
                   planar_text: str | None = None,
                   flip_text: str | None = None,
                   variant_text: str | None = None,
                   paint_geo_text: str | None = None,
                   cleanup_text: str | None = None,
                   public_col_text: str | None = None,
                   query_text: str | None = None,
                   kernel_text: str | None = None,
                   chip_text: str | None = None,
                   hotspot_text: str | None = None,
                   geometry_text: str | None = None,
                   pair_check_text: str | None = None,
                   p0i_text: str | None = None,
                   b8_text: str | None = None,
                   b8s1_text: str | None = None,
                   b7_end_text: str | None = None,
                   p1b_text: str | None = None,
                   p1c_priority_text: str | None = None,
                   p1c_dispatch_text: str | None = None,
                   p1c_context_text: str | None = None,
                   p1c_pre_text: str | None = None,
                   p1c_col_text: str | None = None) -> None:
    """Create one complete AP20 assembly project; replace only verified P2d region."""
    require(AUDIT_DIR.is_dir(), f'missing audited P2d assembly: {AUDIT_DIR}')
    require(EDITABLE_FILE.is_file(), f'missing authored module: {EDITABLE_FILE}')
    require(PLANES_FILE.is_file(), f'missing authored module: {PLANES_FILE}')
    require(PLANAR_FILE.is_file(), f'missing authored module: {PLANAR_FILE}')
    require(FLIP_FILE.is_file(), f'missing authored module: {FLIP_FILE}')
    require(VARIANT_FILE.is_file(), f'missing authored module: {VARIANT_FILE}')
    require(PAINT_GEO_FILE.is_file(), f'missing authored module: {PAINT_GEO_FILE}')
    require(CLEANUP_FILE.is_file(), f'missing authored module: {CLEANUP_FILE}')
    require(PUBLIC_COL_FILE.is_file(), f'missing authored module: {PUBLIC_COL_FILE}')
    require(QUERY_FILE.is_file(), f'missing authored module: {QUERY_FILE}')
    require(KERNEL_FILE.is_file(), f'missing authored module: {KERNEL_FILE}')
    require(CHIP_FILE.is_file(), f'missing authored module: {CHIP_FILE}')
    require(HOTSPOT_FILE.is_file(), f'missing authored module: {HOTSPOT_FILE}')
    require(GEOMETRY_FILE.is_file(), f'missing authored module: {GEOMETRY_FILE}')
    require(PAIR_CHECK_FILE.is_file(), f'missing authored module: {PAIR_CHECK_FILE}')
    require(P0I_FILE.is_file(), f'missing authored module: {P0I_FILE}')
    require(B8_FILE.is_file(), f'missing authored module: {B8_FILE}')
    require(B8S1_FILE.is_file(), f'missing authored module: {B8S1_FILE}')
    require(B7_END_FILE.is_file(), f'missing authored module: {B7_END_FILE}')
    require(P1B_FILE.is_file(), f'missing authored module: {P1B_FILE}')
    require(P1C_PRIORITY_FILE.is_file(), f'missing authored module: {P1C_PRIORITY_FILE}')
    require(P1C_DISPATCH_FILE.is_file(), f'missing authored module: {P1C_DISPATCH_FILE}')
    require(P1C_CONTEXT_FILE.is_file(), f'missing authored module: {P1C_CONTEXT_FILE}')
    require(P1C_PRE_FILE.is_file(), f'missing authored module: {P1C_PRE_FILE}')
    require(P1C_COL_FILE.is_file(), f'missing authored module: {P1C_COL_FILE}')
    require(SLOTS_FILE.is_file(), f'missing source-owned data: {SLOTS_FILE}')
    for name in (MASTER_FILE, BOBS_FILE, 'M19_P2D_UNIT142_MC68020.s',
                 'M19_P2D_UNIT153_MC68020.s',
                 'M19_P2D_UNIT156_MC68020.s'):
        p = AUDIT_DIR / name
        require(p.is_file(), f'missing audit source dependency: {p}')
        shutil.copyfile(p, folder / name)
    text = (folder / BOBS_FILE).read_text(encoding='ascii')
    text = replace_raw_p2a_chip(text)
    text = replace_raw_p2a_pair_check(text)
    text = replace_raw_p0i_paint(text)
    text = replace_raw_b8_end_register(text)
    text = replace_raw_b8s1_bank_free(text)
    text = replace_raw_b7_end(text)
    text = replace_raw_p1b_origin(text)
    text = replace_raw_p1c_priority(text)
    text = replace_raw_p1c_dispatch(text)
    text = replace_raw_p1c_context(text)
    text = replace_raw_p1c_frame_preflight(text)
    text = replace_raw_p1c_order_collect(text)
    text = replace_raw_p2a_hotspot(text)
    text = replace_raw_p2a_query(text)
    text = replace_raw_p2a_kernel(text)
    text = replace_raw_p2a_geometry(text)
    text = replace_raw_p2a_public(text)
    text = replace_raw_flip_public(text)
    text = replace_raw_p2b_variant(text)
    text = replace_raw_p2b_paint_geo(text)
    text = replace_raw_planar_block(text)
    text = replace_raw_p2b_cleanup(text)
    text = replace_raw_p2b_slot_data(text)
    require(text.count(P2C_START_LABEL) == 1 and text.count(P2C_END_LABEL) == 1,
            'audited P2c assembly has ambiguous module boundaries')
    p2c_first = text.index(P2C_START_LABEL)
    p2c_last = text.index(P2C_END_LABEL, p2c_first)
    require(text[p2c_first:p2c_last].count('p2c_reset_slot:') == 1 and
            'dc.b ' in text[p2c_first:p2c_last],
            'P2c reset slot missing from raw audit baseline')
    text = (text[:p2c_first] + '    include "' + P2C_SOURCE_NAME + '"\n' +
            text[p2c_last:])
    require(text.count(START_LABEL) == 1 and text.count(END_LABEL) == 1,
            'audited P2d assembly has ambiguous module boundaries')
    first = text.index(START_LABEL)
    last = text.index(END_LABEL, first)
    old_region = text[first:last]
    require(old_region.count('p2d_close:') == 1 and
            old_region.count('p2d_mode:') == 1 and
            'dc.b ' in old_region, 'mismatched historical P2d assembly region')
    text = (text[:first] + '    include "' + SOURCE_NAME + '"\n' +
            text[last:])
    text = replace_source_backed_amos_pseudo(text)
    (folder / BOBS_FILE).write_text(text, encoding='ascii', newline='\n')
    source = module_text if module_text is not None else EDITABLE_FILE.read_text('ascii')
    require(source.count('p2d_public_auto_update:') == 1 and
            source.count('p2d_close:') == 1 and
            source.count('p2d_mode:') == 1 and
            source.count('dcb.b 12,0') == 1,
            'handwritten source missing mandatory routines or state')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', source),
            'unclassified data directive inside handwritten routine')
    (folder / SOURCE_NAME).write_text(source, encoding='ascii', newline='\n')
    planes_source = (planes_text if planes_text is not None
                     else PLANES_FILE.read_text('ascii'))
    require(planes_source.count('p2c_public_planes:') == 1 and
            planes_source.count('p2c_apply_planes:') == 1 and
            planes_source.count('p2c_reset_slot:') == 1,
            'handwritten P2c module incomplete')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', planes_source),
            'unclassified opcode/data directive inside P2c module')
    (folder / P2C_SOURCE_NAME).write_text(planes_source, encoding='ascii', newline='\n')
    flip_source = (flip_text if flip_text is not None
                   else FLIP_FILE.read_text('ascii'))
    for label in ('p2b_slot:', 'p2b_mode:', 'p2b_free_slot:',
                  'p2b_public_flip:', 'p2b_flip_fail:'):
        require(flip_source.count(label) == 1,
                f'P2b public Flip module missing {label}')
    # Vasm chooses 6/10-byte LEA variants, whereas the source emitter
    # uses exactly 8 bytes: 41FB 0170 + PC-relative full displacement.
    # These are the four explicitly classified instruction exceptions.
    cleaned = flip_source
    for symbol, count in (('p2b_slots', 1), ('p2b_owner', 3)):
        pair = ('    dc.w $41FB,$0170\n    dc.l ' + symbol + '-(*-2)')
        require(flip_source.count(pair) == count,
                f'P2b exact PC32 LEA mismatch: {symbol}')
        cleaned = cleaned.replace(pair, '')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', cleaned),
            'unclassified opcode/data directive inside P2b public Flip')
    (folder / FLIP_SOURCE_NAME).write_text(flip_source, encoding='ascii',
                                           newline='\n')
    variant_source = (variant_text if variant_text is not None
                      else VARIANT_FILE.read_text('ascii'))
    for label in ('p2b_variant:', 'p2b_variant_miss:',
                  'p2b_variant_prepare:', 'p2b_variant_publish:',
                  'p2b_variant_fail:', 'p2b_adjust_anchor:'):
        require(variant_source.count(label) == 1,
                'P2b variant/anchor source missing ' + label)
    exceptions = ('    dc.w $4C04,$6000', '    dc.w $4C01,$2000')
    for exc in exceptions:
        require(variant_source.count(exc) == 1,
                'P2b variant missing source-backed MULU.L encoding: ' + exc)
    variant_clean = variant_source
    for exc in exceptions:
        variant_clean = variant_clean.replace(exc, '')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', variant_clean),
            'unexpected raw opcode in P2b variant/anchor source')
    (folder / VARIANT_SOURCE_NAME).write_text(variant_source,
                                             encoding='ascii', newline='\n')
    paint_source = (paint_geo_text if paint_geo_text is not None
                    else PAINT_GEO_FILE.read_text('ascii'))
    for label in ('p2b_paint:', 'p2b_paint_hotspot:', 'p2b_geometry:',
                  'p2b_geo_done_0:', 'p2b_geo_done_1:',
                  'p2b_geometry_fail:'):
        require(paint_source.count(label) == 1,
                'P2b painter source missing ' + label)
    exception = ('    dc.w $41FB,$0170\n'
                 '    dc.l p1d_drawing_id-(*-2)')
    require(paint_source.count(exception) == 1,
            'P2b painter source-owned PC32 instruction missing')
    clean_paint = paint_source.replace(exception, '')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', clean_paint),
            'unexpected raw opcode in P2b painter/geometry')
    (folder / PAINT_GEO_SOURCE_NAME).write_text(paint_source,
                                               encoding='ascii', newline='\n')
    cleanup_source = (cleanup_text if cleanup_text is not None
                      else CLEANUP_FILE.read_text('ascii'))
    for label in ('p2b_close_return:', 'p2b_closed:', 'p2b_bank_free:',
                  'p2b_bank_free_return:', 'p2b_purge:', 'p2b_purge_loop:'):
        require(cleanup_source.count(label) == 1,
                'P2b cleanup source missing ' + label)
    checked = cleanup_source
    for symbol, opcode, count in (('p2b_owner', '41FB', 3),
                                  ('p2b_slots', '47FB', 1)):
        exact = ('    dc.w $' + opcode + ',$0170\n    dc.l ' +
                 symbol + '-(*-2)')
        require(cleanup_source.count(exact) == count,
                'P2b cleanup missing source-owned PC32 LEA')
        checked = checked.replace(exact, '')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', checked),
            'unexpected raw opcode in P2b cleanup')
    (folder / CLEANUP_SOURCE_NAME).write_text(cleanup_source,
                                             encoding='ascii', newline='\n')
    public_source = (public_col_text if public_col_text is not None
                     else PUBLIC_COL_FILE.read_text('ascii'))
    require(public_source.count('p2a_public_bob_col:') == 1 and
            public_source.count('p2a_public_col_done:') == 1,
            'public P2a Bob Col ASM source incomplete')
    full_pc = [('4DFB','p1c_context'),
               ('41FB','p2a_pair_chip_resolve_entry'),
               ('41FB','explicit_image_resolve_entry'),
               ('41FB','p2a_pair_hotspot_entry'),
               ('41FB','explicit_bank_lookup_entry'),
               ('41FB','p2b_geometry'),
               ('41FB','p2a_pair_entry')]
    checked = public_source
    for code, target in full_pc:
        exc = ('    dc.w $' + code + ',$0170\n    dc.l ' +
               target + '-(*-2)')
        require(public_source.count(exc) == 1,
                'P2a full-format PC32 emitter instruction missing: '+target)
        checked = checked.replace(exc, '')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', checked),
            'unclassified opcode/data inside P2a public Bob Col')
    (folder / PUBLIC_COL_NAME).write_text(public_source,
                                          encoding='ascii', newline='\n')
    query_source = (query_text if query_text is not None
                    else QUERY_FILE.read_text('ascii'))
    require(query_source.count('p2a_collision_query_entry:') == 1 and
            query_source.count('p2a_query_return:') == 1 and
            not re.search(r'(?im)^\s*dc\.[bwll]\b', query_source),
            'P2a collision query native source contains incomplete/raw code')
    (folder / QUERY_SOURCE_NAME).write_text(query_source,
                                             encoding='ascii', newline='\n')
    kernel_source = (kernel_text if kernel_text is not None
                     else KERNEL_FILE.read_text('ascii'))
    for name in ('p2a_pair_entry:', 'p2a_v0_validated:',
                 'p2a_v1_validated:', 'p2a_pixel:', 'p2a_invalid:',
                 'p2a_return:'):
        require(kernel_source.count(name) == 1,
                'P2a collision kernel label missing: '+name)
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', kernel_source),
            'P2a collision kernel contains unclassified machine code')
    (folder / KERNEL_SOURCE_NAME).write_text(kernel_source,
                                            encoding='ascii', newline='\n')
    chip_source = (chip_text if chip_text is not None
                   else CHIP_FILE.read_text('ascii'))
    require(chip_source.count('p2a_pair_chip_resolve_entry:') == 1 and
            chip_source.count('p2a_pair_chip_return:') == 1 and
            not re.search(r'(?im)^\s*dc\.[bwll]\b', chip_source),
            'P2a Chip pair source missing entry/return or has raw bytes')
    (folder / CHIP_NAME).write_text(chip_source,
                                    encoding='ascii', newline='\n')
    hotspot_source = (hotspot_text if hotspot_text is not None
                      else HOTSPOT_FILE.read_text('ascii'))
    for marker in ('p2a_pair_hotspot_entry:', 'p2a_h0_scan:',
                   'p2a_h0_found:', 'p2a_h1_scan:', 'p2a_h1_found:',
                   'p2a_hot_refuse:'):
        require(hotspot_source.count(marker) == 1,
                'P2a hotspot source missing ' + marker)
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', hotspot_source),
            'P2a hotspot source contains raw machine-code bytes')
    (folder / HOTSPOT_NAME).write_text(hotspot_source,
                                       encoding='ascii', newline='\n')
    geometry_source = (geometry_text if geometry_text is not None
                       else GEOMETRY_FILE.read_text('ascii'))
    for label in ('p2a_pair_geometry_entry:', 'p2a_g0_complete:',
                  'p2a_g1_complete:', 'p2a_g0_empty:', 'p2a_g1_empty:',
                  'p2a_geo_reject:'):
        require(geometry_source.count(label) == 1,
                'P2a geometry source missing label ' + label)
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', geometry_source),
            'P2a geometry source contains unclassified opcodes')
    (folder / GEOMETRY_NAME).write_text(geometry_source,
                                       encoding='ascii', newline='\n')
    pair_check_source = (pair_check_text if pair_check_text is not None
                         else PAIR_CHECK_FILE.read_text('ascii'))
    require(pair_check_source.count('p2a_pair_checked_read_entry:') == 1 and
            pair_check_source.count('p2a_pair_fail:') == 1 and
            not re.search(r'(?im)^\s*dc\.[bwll]\b', pair_check_source),
            'P2a checked-read source incomplete or raw opcodes remain')
    (folder / PAIR_CHECK_NAME).write_text(pair_check_source,
                                          encoding='ascii', newline='\n')
    routed_source = (p0i_text if p0i_text is not None
                     else P0I_FILE.read_text('ascii'))
    for marker in ('routed_paint_one_entry:', 'routed_paint_all_entry:',
                   'route_return:', 'route_restore:', 'route_unwind:'):
        require(routed_source.count(marker) == 1,
                'P0i source module missing '+marker)
    exception = ('    dc.w $FE11,$F700,$031D'
                 '   ; AMOS Main: Bnk.GetAdr (index 797)')
    require(routed_source.count(exception) == 1,
            'P0i AMOS Main Bnk.GetAdr source-backed pseudo opcode missing')
    checked = routed_source.replace(exception,'')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', checked),
            'P0i routed painter contains unclassified raw opcode')
    (folder / P0I_NAME).write_text(routed_source,
                                  encoding='ascii', newline='\n')
    b8_source = b8_text if b8_text is not None else B8_FILE.read_text('ascii')
    for marker in ('b8_b7_end_trampoline_entry:', 'b8_b7_end_return:',
                   'b8_b7_clear_root:', 'b8_b7_hook_root:'):
        require(b8_source.count(marker) == 1,
                'B8 end/registrar native source missing '+marker)
    data_magic = '    dc.b $42,$38,$52,$47'
    state_data = '    dcb.b 8,0'
    require(b8_source.count(data_magic) == 1 and
            b8_source.count(state_data) == 1 and
            '    bra.w p2b_close_return\n    rts' in b8_source,
            'B8 registrar data/End bridge source contract changed')
    b8_code = b8_source.replace(data_magic, '').replace(state_data,'')
    require(not re.search(r'(?im)^\s*dcb?\.[bwll]\b', b8_code),
            'unclassified source bytes in B8 lifecycle module')
    (folder / B8_NAME).write_text(b8_source,
                                  encoding='ascii', newline='\n')
    bank_free_source = (b8s1_text if b8s1_text is not None
                        else B8S1_FILE.read_text('ascii'))
    for marker in ('b8s1_bank_free_entry:',
                   'b8s1_bank_free_scan_start:'):
        require(bank_free_source.count(marker) == 1,
                'B8 S1 Bank Free source missing '+marker)
    require('    bsr.w p2b_bank_free' in bank_free_source and
            not re.search(r'(?im)^\s*dcb?\.[bwll]\b', bank_free_source),
            'B8 S1 Bank Free not sourced as explicit MC68020 instructions')
    (folder / B8S1_NAME).write_text(bank_free_source,
                                    encoding='ascii', newline='\n')
    b7_end_source = (b7_end_text if b7_end_text is not None
                     else B7_END_FILE.read_text('ascii'))
    # Only the baseline clear or its one-instruction mutation is admissible.
    # verify_link() still enforces the exact modified byte and AP20 identity.
    b7_clear_original = b7_end_source.count('    move.l #0,4(a0)')
    b7_clear_edited = b7_end_source.count('    move.l #1,4(a0)')
    require(b7_end_source.count('b7_end_entry:') == 1 and
            '    bra.w p2b_close_return\n    rts' in b7_end_source and
            (b7_clear_original, b7_clear_edited) in ((1, 0), (0, 1)) and
            not re.search(r'(?im)^\s*dcb?\.[bwll]\b', b7_end_source),
            'B7 End source missing lifecycle or has raw instructions')
    (folder / B7_END_NAME).write_text(b7_end_source,
                                      encoding='ascii', newline='\n')
    p1b_source = p1b_text if p1b_text is not None else P1B_FILE.read_text('ascii')
    p1b_original = p1b_source.count('    move.l #1,d3')
    p1b_edited = p1b_source.count('    move.l #2,d3')
    require(p1b_source.count('p1b_hotspot_origin_entry:') == 1 and
            p1b_source.count('p1b_no_overlap:') == 1 and
            p1b_source.count('p1b_hotspot_return:') == 1 and
            (p1b_original, p1b_edited) in ((1, 0), (0, 1)) and
            not re.search(r'(?im)^\s*dcb?\.[bwll]\b', p1b_source),
            'P1b authored source incomplete or unclassified')
    (folder / P1B_NAME).write_text(p1b_source, encoding='ascii', newline='\n')
    priority_source = (p1c_priority_text if p1c_priority_text is not None
                       else P1C_PRIORITY_FILE.read_text('ascii'))
    priority_base = priority_source.count('    move.l #1,d3')
    priority_changed = priority_source.count('    move.l #2,d3')
    require(priority_source.count('p1c_priority_entry:') == 1 and
            priority_source.count('p1c_priority_fail:') == 1 and
            priority_source.count('p1c_priority_return:') == 1 and
            (priority_base, priority_changed) in ((1, 0), (0, 1)) and
            not re.search(r'(?im)^\s*dcb?\.[bwll]\b', priority_source),
            'P1c Priority source missing procedure or contains raw bytes')
    (folder / P1C_PRIORITY_NAME).write_text(priority_source, encoding='ascii', newline='\n')
    dispatch_source = (p1c_dispatch_text if p1c_dispatch_text is not None
                       else P1C_DISPATCH_FILE.read_text('ascii'))
    dispatch_base = dispatch_source.count('    lea -160(a7),a7')
    dispatch_changed = dispatch_source.count('    lea -156(a7),a7')
    require(dispatch_source.count('p1c_frame_dispatch:') == 1 and
            dispatch_source.count('p1c_frame_default:') == 1 and
            (dispatch_base, dispatch_changed) in ((1, 0), (0, 1)) and
            not re.search(r'(?im)^\s*dcb?\.[bwll]\b', dispatch_source),
            'P1c Dispatch source missing labels or contains raw bytes')
    (folder / P1C_DISPATCH_NAME).write_text(dispatch_source, encoding='ascii', newline='\n')
    context_source = (p1c_context_text if p1c_context_text is not None
                      else P1C_CONTEXT_FILE.read_text('ascii'))
    context_base = context_source.count('    movea.l #0,a0')
    context_changed = context_source.count('    movea.l #1,a0')
    for marker in ('p1c_context:', 'p1c_no_context:',
                   'p1c_read_mode:', 'p1c_read_return:',
                   'L_BOBS_07B6C:', 'L_BOBS_07B74:', 'L_BOBS_07B82:'):
        require(context_source.count(marker) == 1, 'P1c context source missing '+marker)
    require((context_base, context_changed) in ((1, 0), (0, 1)) and
            context_source.count('P1C_CONTEXT_DELTA equ $EF08') == 1 and
            not re.search(r'(?im)^\s*dcb?\.[bwll]\b', context_source),
            'P1c context contains unclassified bytes or missing pointer guard')
    (folder / P1C_CONTEXT_NAME).write_text(context_source,
                                           encoding='ascii', newline='\n')
    pre_source = p1c_pre_text if p1c_pre_text is not None else P1C_PRE_FILE.read_text('ascii')
    pre_baseline = pre_source.count('    move.l #1,44(a2)')
    pre_edited = pre_source.count('    move.l #2,44(a2)')
    require(pre_source.count('explicit_frame_draw_entry:') == 1 and
            pre_source.count('    lea -P1C_FRAME_BYTES(a7),a7') == 1 and
            (pre_baseline, pre_edited) in ((1, 0), (0, 1)) and
            not re.search(r'(?im)^\s*dcb?\.[bwll]\b', pre_source),
            'P1c frame setup contains raw instructions or missing source hooks')
    (folder / P1C_PRE_NAME).write_text(pre_source, encoding='ascii', newline='\n')
    col_source = p1c_col_text if p1c_col_text is not None else P1C_COL_FILE.read_text('ascii')
    col_baseline = col_source.count('    move.l #0,P1C_CURSOR(a2)')
    col_edited = col_source.count('    move.l #1,P1C_CURSOR(a2)')
    for marker in ('p1c_collect:', 'p1c_insert:', 'p1c_insert_scan:',
                   'p1c_store_key:', 'p1c_collect_next:', 'p1c_collect_done:',
                   'L_BOBS_07C58:', 'L_BOBS_07C6A:', 'L_BOBS_07C82:',
                   'L_BOBS_07C88:', 'L_BOBS_07C90:'):
        require(col_source.count(marker) == 1, 'P1c priority scan missing '+marker)
    require((col_baseline, col_edited) in ((1, 0), (0, 1)) and
            col_source.count('P1C_LIST equ 160') == 1 and
            not re.search(r'(?im)^\s*dcb?\.[bwll]\b', col_source),
            'P1c priority collection has unclassified bytes or invalid list bounds')
    (folder / P1C_COL_NAME).write_text(col_source, encoding='ascii', newline='\n')
    planar_source = (planar_text if planar_text is not None
                     else PLANAR_FILE.read_text('ascii'))
    for label in ('p2b_planar_orientation_entry:',
                  'p2b_planar_measure:', 'p2b_planar_chip_prepare_entry:'):
        require(planar_source.count(label) == 1,
                f'P2b materializer source label missing: {label}')
    # 68020 MULU.L D4,D3: the emitter uses a noncanonical but legal
    # extension word $3000; vasm's canonical choice is $3003.
    # Preserve ONE source-verified legacy encoding, fail on all other DC opcodes.
    exception = '    dc.w $4C04,$3000   ; exact MULU.L D4,D3; documented encoder exception'
    require(planar_source.count(exception) == 1,
            'P2b original MULU.L extension exception altered')
    inspected = planar_source.replace(exception, '')
    require(not re.search(r'(?im)^\s*dc\.[bwll]\b', inspected),
            'unclassified opcode/data directive inside P2b materializer')
    (folder / PLANAR_SOURCE_NAME).write_text(planar_source,
                                            encoding='ascii', newline='\n')
    slots = SLOTS_FILE.read_text('ascii')
    require(slots.count('p2b_owner:') == 1 and
            slots.count('p2b_slots:') == 1 and
            slots.count('dcb.b P2B_SLOT_STATE_BYTES,0') == 1 and
            slots.count('P2B_SLOT_COUNT         equ 64') == 1 and
            slots.count('P2B_SLOT_BYTES         equ 64') == 1,
            'P2b table source contract changed')
    (folder / SLOTS_SOURCE_NAME).write_text(slots,
                                           encoding='ascii', newline='\n')


def verify_link(original: bytes, image: bytes, group: int,
                planes_start: int, control_start: int, control_end: int,
                *, allow_edited: bool) -> list[int]:
    """Reject AP20 topology/geometry changes and changes outside the owned code."""
    if len(image) != len(original):
        try:
            _, op, _ = unpack_ap20(original)
            _, np, _ = unpack_ap20(image)
            first = next((i for i, (a, b) in enumerate(zip(op[group], np[group]))
                          if a != b), min(len(op[group]), len(np[group])))
            import difflib
            old_frag = op[group][PLANAR_START:PLANAR_END]
            delta = len(np[group]) - len(op[group])
            new_frag = np[group][PLANAR_START:PLANAR_END+delta]
            matcher = difflib.SequenceMatcher(None, old_frag, new_frag,
                                              autojunk=False)
            changes = []
            for tag, a, b, c, d in matcher.get_opcodes():
                if tag != 'equal':
                    changes.append((tag, f'{PLANAR_START+a:05X}',
                                    old_frag[a:b].hex(), new_frag[c:d].hex()))
            context = (f'BOBS original={len(op[group])} compiled={len(np[group])}; '
                       f'first_diff=${first:05X}; '
                       f'orig={op[group][first:first+24].hex()}; '
                       f'new={np[group][first:first+24].hex()}; '
                       f'PLANAR changes={changes[:16]}')
        except Exception as exc:
            context = f'AP20 parse failed: {exc}'
        raise SourceError(f'changed binary length {len(image)}, expected '
                          f'{len(original)}; {context}')
    old_tokens, old_parts, old_title = unpack_ap20(original)
    tokens, parts, title = unpack_ap20(image)
    require((tokens, title, len(parts)) == (old_tokens, old_title, len(old_parts)),
            'AP20 tokens, title, or entry count changed')
    require(all(x == y for i, (x, y) in enumerate(zip(old_parts, parts)) if i != group),
            'modified an AP20 unit outside the controlled P2d BOBS module')
    require(len(parts[group]) == len(old_parts[group]),
            'BOBS size/entry offsets changed; variable-length relocation NOT supported')
    differences = [i for i, (a, b) in enumerate(zip(old_parts[group], parts[group])) if a != b]
    planar_start, planar_end, _, _ = prove_planar_provenance()
    flip_start, flip_end, _, _ = prove_flip_public_provenance()
    variant_start, variant_end, _, _ = prove_p2b_variant_provenance()
    paint_start, paint_end, _, _ = prove_p2b_paint_geo_provenance()
    cleanup_start, cleanup_end, _, _ = prove_p2b_cleanup_provenance()
    public_start, public_end, _, _ = prove_p2a_public_provenance()
    query_start, query_end, _, _ = prove_p2a_query_provenance()
    kernel_start, kernel_end, _, _ = prove_p2a_kernel_provenance()
    chip_start, chip_end, _, _ = prove_p2a_chip_provenance()
    hotspot_start, hotspot_end, _, _ = prove_p2a_hotspot_provenance()
    geometry_start, geometry_end, _, _ = prove_p2a_geometry_provenance()
    pair_check_start, pair_check_end, _, _ = prove_p2a_pair_check_provenance()
    p0i_start, p0i_end, _, _ = prove_p0i_paint_provenance()
    b8_start, b8_end, _, _ = prove_b8_end_register_provenance()
    b8s1_start, b8s1_end, _, _ = prove_b8s1_bank_free_provenance()
    b7_start, b7_end, _, _ = prove_b7_end_provenance()
    p1b_start, p1b_end, _, _ = prove_p1b_origin_provenance()
    p1c_priority_start, p1c_priority_end, _, _ = prove_p1c_priority_provenance()
    p1c_dispatch_start, p1c_dispatch_end, _, _ = prove_p1c_dispatch_provenance()
    p1c_context_start, p1c_context_end, _, _ = prove_p1c_context_provenance()
    p1c_pre_start, p1c_pre_end, _, _ = prove_p1c_frame_preflight_provenance()
    p1c_col_start, p1c_col_end, _, _ = prove_p1c_order_collect_provenance()
    require(all((planes_start <= i < control_end) or
                (planar_start <= i < planar_end) or
                (flip_start <= i < flip_end) or
                (variant_start <= i < variant_end) or
                (paint_start <= i < paint_end) or
                (cleanup_start <= i < cleanup_end) or
                (public_start <= i < public_end) or
                (query_start <= i < query_end) or
                (kernel_start <= i < kernel_end) or
                (chip_start <= i < chip_end) or
                (hotspot_start <= i < hotspot_end) or
                (geometry_start <= i < geometry_end) or
                (pair_check_start <= i < pair_check_end) or
                (p0i_start <= i < p0i_end) or
                (b8_start <= i < b8_end) or
                (b8s1_start <= i < b8s1_end) or
                (b7_start <= i < b7_end) or
                (p1b_start <= i < p1b_end) or
                 (p1c_priority_start <= i < p1c_priority_end) or
                 (p1c_dispatch_start <= i < p1c_dispatch_end) or
                 (p1c_context_start <= i < p1c_context_end) or
                 (p1c_pre_start <= i < p1c_pre_end) or
                 (p1c_col_start <= i < p1c_col_end) for i in differences),
            'a byte outside the authored P2b/P2c/P2d modules differs from the reference')
    if not allow_edited:
        require(not differences and image == original,
                f'baseline assembly differs in BOBS at {differences[:8]}')
    report = inspect(parse(image))
    require(not report['issues'], f'AP20 parsing issues: {report["issues"]}')
    return differences


def build(assembler: Path, target: Path, *, allow_edited: bool = False,
          module_text: str | None = None,
          planes_text: str | None = None,
          planar_text: str | None = None,
          flip_text: str | None = None,
          variant_text: str | None = None,
          paint_geo_text: str | None = None,
          cleanup_text: str | None = None,
          public_col_text: str | None = None,
          query_text: str | None = None,
          kernel_text: str | None = None,
          chip_text: str | None = None,
          hotspot_text: str | None = None,
          geometry_text: str | None = None,
          pair_check_text: str | None = None,
          p0i_text: str | None = None,
          b8_text: str | None = None,
          b8s1_text: str | None = None,
          b7_end_text: str | None = None,
          p1b_text: str | None = None,
          p1c_priority_text: str | None = None,
          p1c_dispatch_text: str | None = None,
          p1c_context_text: str | None = None,
          p1c_pre_text: str | None = None,
          p1c_col_text: str | None = None) -> tuple[bytes, list[int]]:
    original, group, planes_start, control_start, control_end, _, _ = prove_source_provenance()
    target.mkdir(parents=True, exist_ok=True)
    staged_sources(target, module_text=module_text, planes_text=planes_text,
                   planar_text=planar_text, flip_text=flip_text,
                   variant_text=variant_text, paint_geo_text=paint_geo_text,
                   cleanup_text=cleanup_text, public_col_text=public_col_text,
                   query_text=query_text, kernel_text=kernel_text,
                   chip_text=chip_text, hotspot_text=hotspot_text,
                   geometry_text=geometry_text,
                   pair_check_text=pair_check_text,
                   p0i_text=p0i_text, b8_text=b8_text,
                   b8s1_text=b8s1_text, b7_end_text=b7_end_text,
                    p1b_text=p1b_text,
                    p1c_priority_text=p1c_priority_text,
                    p1c_dispatch_text=p1c_dispatch_text,
                    p1c_context_text=p1c_context_text,
                    p1c_pre_text=p1c_pre_text,
                    p1c_col_text=p1c_col_text)
    output = target / ('M19_P2D_EDITED_UNTESTED.Lib' if allow_edited
                       else 'M19_P2D_ASM_REBUILT_CHECK.Lib')
    result = checked_vasm(assembler, target / MASTER_FILE, output)
    differences = verify_link(original, result, group, planes_start,
                              control_start, control_end, allow_edited=allow_edited)
    print('P2D ASM', 'EDITED UNTESTED' if allow_edited else 'BASELINE EXACT',
          'BYTES', len(result), 'DIFF', len(differences),
          'SHA256', sha256(result).hexdigest())
    return result, differences


def test_editability(assembler: Path) -> None:
    """Prove a REAL one-instruction edit changes only its own machine-code byte."""
    _, group, planes_start, start, end, done, planes_fail = prove_source_provenance()
    with TemporaryDirectory(prefix='p2d_native_edit_') as d:
        root = Path(d)
        original, baseline_diff = build(assembler, root/'baseline')
        require(not baseline_diff, 'no-edit compile changed the binary')
        source = EDITABLE_FILE.read_text('ascii')
        before = 'p2d_set_done:\n    moveq #1,d3'
        require(source.count(before) == 1, 'no unique source instruction to edit')
        altered = source.replace(before, 'p2d_set_done:\n    moveq #2,d3')
        modified, diffs = build(assembler, root/'modified',
                                allow_edited=True, module_text=altered)
        require(diffs == [done+1], f'wrong edited byte(s): {diffs[:12]}, expected {done+1}')
        require(modified != original and len(modified) == len(original),
                'edit was ignored or changed AP20 size')
        require(unpack_ap20(modified)[1][group][done:done+2] == b'\x76\x02',
                'modified instruction did not encode MOVEQ #2,D3')
        require(start <= done < end, 'edit escaped the authored module')

        planes_source = PLANES_FILE.read_text('ascii')
        needle = 'p2c_set_fail:\n    moveq #0,d3'
        require(planes_source.count(needle) == 1,
                'missing uniquely modifiable P2c failure instruction')
        planes_edited = planes_source.replace(needle,
                        'p2c_set_fail:\n    moveq #1,d3')
        modified_planes, plane_diffs = build(
            assembler, root/'modified_planes', allow_edited=True,
            planes_text=planes_edited)
        require(plane_diffs == [planes_fail+1],
                f'P2c wrong edited byte: {plane_diffs}, expected {planes_fail+1}')
        require(unpack_ap20(modified_planes)[1][group][planes_fail:planes_fail+2]
                == b'\x76\x01', 'P2c modified opcode did not assemble')
        require(planes_start <= planes_fail < start,
                'P2c modified opcode escaped the authored module')

        planar_start, planar_end, invalid, _ = prove_planar_provenance()
        planar_source = PLANAR_FILE.read_text('ascii')
        needle = 'p2b_planar_invalid:\n    moveq #0,d3'
        require(planar_source.count(needle) == 1,
                'P2b planar failure opcode not uniquely editable')
        planar_edited = planar_source.replace(
            needle, 'p2b_planar_invalid:\n    moveq #1,d3')
        changed_planar, planar_diffs = build(
            assembler, root/'modified_planar', allow_edited=True,
            planar_text=planar_edited)
        require(planar_diffs == [invalid+1],
                f'P2b planar edit affected {planar_diffs}, expected {[invalid+1]}')
        require(unpack_ap20(changed_planar)[1][group][invalid:invalid+2] == b'\x76\x01',
                'P2b planar MOVEQ #1,D3 was not encoded')
        require(planar_start <= invalid < planar_end,
                'P2b modified opcode escaped authored materializer')

        flip_start, flip_end, flip_fail, _ = prove_flip_public_provenance()
        flip_source = FLIP_FILE.read_text('ascii')
        flip_needle = 'p2b_flip_fail:\n    moveq #0,d3'
        require(flip_source.count(flip_needle) == 1,
                'P2b public Flip failure opcode not uniquely editable')
        flip_edit = flip_source.replace(
            flip_needle, 'p2b_flip_fail:\n    moveq #1,d3')
        changed_flip, flip_diffs = build(
            assembler, root/'modified_flip', allow_edited=True,
            flip_text=flip_edit)
        require(flip_diffs == [flip_fail+1],
                f'P2b Flip edit changed {flip_diffs}, expected {[flip_fail+1]}')
        require(unpack_ap20(changed_flip)[1][group][flip_fail:flip_fail+2]
                == b'\x76\x01', 'P2b Flip failure instruction was not encoded')
        require(flip_start <= flip_fail < flip_end,
                'P2b public Flip edit escaped authored region')
        variant_start, variant_end, variant_fail, _ = prove_p2b_variant_provenance()
        variant_source = VARIANT_FILE.read_text('ascii')
        variant_needle = 'p2b_variant_fail:\n    moveq #0,d3'
        require(variant_source.count(variant_needle) == 1,
                'P2b variant fail instruction not uniquely editable')
        variant_edited = variant_source.replace(
            variant_needle, 'p2b_variant_fail:\n    moveq #1,d3')
        changed_variant, variant_diffs = build(
            assembler, root/'modified_variant', allow_edited=True,
            variant_text=variant_edited)
        require(variant_diffs == [variant_fail+1],
                f'P2b variant edit affected {variant_diffs}, expected {[variant_fail+1]}')
        require(unpack_ap20(changed_variant)[1][group][variant_fail:variant_fail+2]
                == b'\x76\x01', 'P2b variant failure MOVEQ did not assemble')
        require(variant_start <= variant_fail < variant_end,
                'P2b variant source edit escaped authored module')
        paint_start, paint_end, paint_fail, _ = prove_p2b_paint_geo_provenance()
        paint_source = PAINT_GEO_FILE.read_text('ascii')
        paint_needle = 'p2b_geometry_fail:\n    moveq #0,d3'
        require(paint_source.count(paint_needle) == 1,
                'P2b geometry failure instruction not uniquely editable')
        paint_edited = paint_source.replace(
            paint_needle, 'p2b_geometry_fail:\n    moveq #1,d3')
        changed_paint, paint_diffs = build(
            assembler, root/'modified_paint_geometry', allow_edited=True,
            paint_geo_text=paint_edited)
        require(paint_diffs == [paint_fail+1],
                f'P2b geometry edit affected {paint_diffs}, expected {[paint_fail+1]}')
        require(unpack_ap20(changed_paint)[1][group][paint_fail:paint_fail+2]
                == b'\x76\x01', 'P2b geometry failure MOVEQ did not assemble')
        require(paint_start <= paint_fail < paint_end,
                'P2b paint/geometry edit escaped authored module')
        cleanup_start, cleanup_end, bank_ret, _ = prove_p2b_cleanup_provenance()
        cleanup_source = CLEANUP_FILE.read_text('ascii')
        needle = ('p2b_bank_free_return:\n'
                  '    movem.l (a7)+,d0-d1/d4-d7/a0-a6\n'
                  '    moveq #0,d2')
        require(cleanup_source.count(needle) == 1,
                'P2b bank-free return opcode not uniquely editable')
        altered = cleanup_source.replace(
            needle, needle.replace('moveq #0,d2', 'moveq #1,d2'))
        changed_cleanup, cleanup_diffs = build(
            assembler, root/'modified_cleanup', allow_edited=True,
            cleanup_text=altered)
        require(cleanup_diffs == [bank_ret+5],
                f'P2b cleanup edit affected {cleanup_diffs}, expected {[bank_ret+5]}')
        require(unpack_ap20(changed_cleanup)[1][group][bank_ret+4:bank_ret+6]
                == b'\x74\x01', 'P2b cleanup MOVEQ edit not assembled')
        require(cleanup_start <= bank_ret+4 < cleanup_end,
                'P2b cleanup edit escaped authored region')
        public_start, public_end, public_moveq, _ = prove_p2a_public_provenance()
        public_source = PUBLIC_COL_FILE.read_text('ascii')
        needle = '    moveq #0,d2\n    rts'
        require(public_source.count(needle) == 1,
                'P2a public result MOVEQ not uniquely editable')
        altered = public_source.replace(needle, '    moveq #1,d2\n    rts')
        modified_public, public_diffs = build(
            assembler, root/'modified_public_col', allow_edited=True,
            public_col_text=altered)
        require(public_diffs == [public_moveq+1],
                f'P2a public edit affected {public_diffs}, '
                f'expected {[public_moveq+1]}')
        require(unpack_ap20(modified_public)[1][group]
                [public_moveq:public_moveq+2] == b'\x74\x01',
                'P2a public MOVEQ did not assemble')
        require(public_start <= public_moveq < public_end,
                'P2a public source edit outside owned region')
        query_start, query_end, query_moveq, _ = prove_p2a_query_provenance()
        query_source = QUERY_FILE.read_text('ascii')
        needle = '    moveq #0,d2\n    rts'
        require(query_source.count(needle) == 1,
                'P2a query epilogue MOVEQ not uniquely editable')
        modified_source = query_source.replace(needle, '    moveq #1,d2\n    rts')
        edited_query, query_diffs = build(
            assembler, root/'modified_query', allow_edited=True,
            query_text=modified_source)
        require(query_diffs == [query_moveq+1],
                f'P2a query edit changed {query_diffs}, expected {[query_moveq+1]}')
        require(unpack_ap20(edited_query)[1][group][query_moveq:query_moveq+2]
                == b'\x74\x01', 'P2a query modified MOVEQ did not encode')
        require(query_start <= query_moveq < query_end,
                'P2a query edit escaped owned region')
        kernel_start, kernel_end, invalid, _ = prove_p2a_kernel_provenance()
        kernel_source = KERNEL_FILE.read_text('ascii')
        needle = 'p2a_invalid:\n    move.l #-1,d3'
        require(kernel_source.count(needle) == 1,
                'P2a invalid result opcode not uniquely editable')
        edited = kernel_source.replace(needle, 'p2a_invalid:\n    move.l #-2,d3')
        changed_kernel, kernel_diffs = build(
            assembler, root/'modified_kernel', allow_edited=True,
            kernel_text=edited)
        require(kernel_diffs == [invalid+5],
                f'P2a kernel edit changed {kernel_diffs}, expected {[invalid+5]}')
        require(unpack_ap20(changed_kernel)[1][group][invalid:invalid+6]
                == bytes.fromhex('263cfffffffe'),
                'P2a invalid result edit not assembled')
        require(kernel_start <= invalid < kernel_end,
                'P2a kernel edit escaped source-owned region')
        chip_start, chip_end, chip_ret, _ = prove_p2a_chip_provenance()
        chip_source = CHIP_FILE.read_text('ascii')
        needle = 'p2a_pair_chip_return:\n    move.l 20(a2),d3'
        require(chip_source.count(needle) == 1,
                'P2a Chip result path not uniquely identified')
        # Editing a one-byte immediate while preserving AP20 topology.
        end_needle = '    moveq #0,d2\n    rts'
        require(chip_source.count(end_needle) == 1,
                'P2a Chip result MOVEQ not uniquely editable')
        revised = chip_source.replace(end_needle,'    moveq #1,d2\n    rts')
        edited_chip, chip_diffs = build(
            assembler, root/'modified_chip_resolve',
            allow_edited=True, chip_text=revised)
        require(chip_diffs == [chip_ret+1],
                f'P2a Chip edit affected {chip_diffs}, '
                f'expected {[chip_ret+1]}')
        require(unpack_ap20(edited_chip)[1][group][chip_ret:chip_ret+2]
                == b'\x74\x01', 'P2a Chip modified MOVEQ was not encoded')
        require(chip_start <= chip_ret < chip_end,
                'P2a Chip edit escaped source-owned region')
        hotspot_start, hotspot_end, hot_moveq, _ = prove_p2a_hotspot_provenance()
        hotspot_source = HOTSPOT_FILE.read_text('ascii')
        needle = 'p2a_hot_refuse:\n    move.l 12(a2),d3'
        require(hotspot_source.count(needle) == 1,
                'P2a hotspot return path not uniquely identifiable')
        moveq_needle = '    moveq #0,d2\n    rts'
        require(hotspot_source.count(moveq_needle) == 1,
                'P2a hotspot epilogue MOVEQ not unique')
        edited_source = hotspot_source.replace(
            moveq_needle, '    moveq #1,d2\n    rts')
        changed_hotspot, hot_diffs = build(
            assembler, root/'modified_hotspot', allow_edited=True,
            hotspot_text=edited_source)
        require(hot_diffs == [hot_moveq+1],
                f'P2a hotspot source edit {hot_diffs}, expected {[hot_moveq+1]}')
        require(unpack_ap20(changed_hotspot)[1][group]
                [hot_moveq:hot_moveq+2] == b'\x74\x01',
                'P2a hotspot modified MOVEQ not present in AP20')
        require(hotspot_start <= hot_moveq < hotspot_end,
                'P2a hotspot edit outside owned source')
        geometry_start, geometry_end, geom_moveq, _ = prove_p2a_geometry_provenance()
        geometry_source = GEOMETRY_FILE.read_text('ascii')
        needle = '    moveq #0,d2\n    rts'
        require(geometry_source.count(needle) == 1,
                'P2a geometry epilogue instruction not uniquely editable')
        altered = geometry_source.replace(needle,'    moveq #1,d2\n    rts')
        changed_geometry, geo_diffs = build(
            assembler, root/'modified_geometry', allow_edited=True,
            geometry_text=altered)
        require(geo_diffs == [geom_moveq+1],
                f'P2a geometry edit changed {geo_diffs}, '
                f'expected {[geom_moveq+1]}')
        require(unpack_ap20(changed_geometry)[1][group]
                [geom_moveq:geom_moveq+2] == b'\x74\x01',
                'P2a geometry modified MOVEQ not present')
        require(geometry_start <= geom_moveq < geometry_end,
                'P2a geometry edit escaped source range')
        pair_start, pair_end, pair_moveq, _ = prove_p2a_pair_check_provenance()
        pair_source = PAIR_CHECK_FILE.read_text('ascii')
        needle = '    moveq #0,d2\n    rts'
        require(pair_source.count(needle) == 1,
                'P2a checked pair epilogue not uniquely editable')
        edited = pair_source.replace(needle,'    moveq #1,d2\n    rts')
        edited_pair, pair_diffs = build(
            assembler, root/'modified_pair_checked', allow_edited=True,
            pair_check_text=edited)
        require(pair_diffs == [pair_moveq+1],
                f'P2a pair edit changed {pair_diffs}, expected {[pair_moveq+1]}')
        require(unpack_ap20(edited_pair)[1][group]
                [pair_moveq:pair_moveq+2] == b'\x74\x01',
                'P2a checked pair MOVEQ edit not assembled')
        require(pair_start <= pair_moveq < pair_end,
                'P2a pair edit escaped owned source')
        p0i_start, p0i_end, route_moveq, _ = prove_p0i_paint_provenance()
        routed_source = P0I_FILE.read_text('ascii')
        needle = '    moveq #0,d2\n    rts'
        require(routed_source.count(needle) == 2,
                'P0i two-return module does not have expected MOVEQs')
        # Edit only the final all-objects return, not the one-object route.
        first, last = routed_source.rsplit(needle, 1)
        edited_source = first + '    moveq #1,d2\n    rts' + last
        edited_route, route_diffs = build(
            assembler, root/'modified_p0i_route', allow_edited=True,
            p0i_text=edited_source)
        require(route_diffs == [route_moveq+1],
                f'P0i edit modified {route_diffs}, expected {[route_moveq+1]}')
        require(unpack_ap20(edited_route)[1][group]
                [route_moveq:route_moveq+2] == b'\x74\x01',
                'P0i route edited MOVEQ not assembled')
        require(p0i_start <= route_moveq < p0i_end,
                'P0i source modification escaped local module')
        b8_start, b8_end, b8_opcode, _ = prove_b8_end_register_provenance()
        b8_source = B8_FILE.read_text('ascii')
        needle = '    move.l #1,(a2)\n'
        require(b8_source.count(needle) == 1,
                'B8 register arm immediate not uniquely editable')
        altered = b8_source.replace(needle, '    move.l #2,(a2)\n')
        edited_b8, b8_diffs = build(
            assembler, root/'modified_b8_end_register',
            allow_edited=True, b8_text=altered)
        require(b8_diffs == [b8_opcode],
                f'B8 register arm edit affected {b8_diffs}, '
                f'expected {[b8_opcode]}')
        require(unpack_ap20(edited_b8)[1][group]
                [b8_opcode-5:b8_opcode+1] == bytes.fromhex('24bc00000002'),
                'B8 register arm MOVE.L #2 was not encoded')
        require(b8_start <= b8_opcode < b8_end,
                'B8 callback source edit escaped the owned module')
        b8s1_start, b8s1_end, imm, _ = prove_b8s1_bank_free_provenance()
        b8s1_source = B8S1_FILE.read_text('ascii')
        needle = '    move.l #1,4(a2)'
        require(b8s1_source.count(needle) == 1,
                'B8 S1 Free result setter not uniquely editable')
        revised = b8s1_source.replace(needle, '    move.l #2,4(a2)')
        edited_b8s1, b8s1_diffs = build(
            assembler, root/'modified_b8s1_bank_free',
            allow_edited=True, b8s1_text=revised)
        require(b8s1_diffs == [imm],
                f'B8 S1 Free edit affected {b8s1_diffs}, expected {[imm]}')
        require(unpack_ap20(edited_b8s1)[1][group]
                [imm-5:imm+3] == bytes.fromhex('257c000000020004'),
                'B8 S1 Free modified result immediate not assembled')
        require(b8s1_start <= imm < b8s1_end,
                'B8 S1 Free edit escaped authored region')
        b7_start, b7_end, b7_imm, _ = prove_b7_end_provenance()
        b7_source = B7_END_FILE.read_text('ascii')
        needle = '    move.l #0,4(a0)'
        require(b7_source.count(needle) == 1,
                'P0j B7 End frame-guard clear not uniquely editable')
        edited_src = b7_source.replace(needle, '    move.l #1,4(a0)')
        edited_b7, b7_diffs = build(
            assembler, root/'modified_b7_end', allow_edited=True,
            b7_end_text=edited_src)
        require(b7_diffs == [b7_imm],
                f'P0j B7 End source edit {b7_diffs}, expected {[b7_imm]}')
        require(unpack_ap20(edited_b7)[1][group]
                [b7_imm-5:b7_imm+3] == bytes.fromhex('217c000000010004'),
                'P0j B7 End changed instruction not encoded')
        require(b7_start <= b7_imm < b7_end,
                'P0j B7 End modified byte outside authored region')
        p1b_start, p1b_end, p1b_imm, _ = prove_p1b_origin_provenance()
        p1b_source = P1B_FILE.read_text('ascii')
        needle = '    move.l #1,d3'
        require(p1b_source.count(needle) == 1,
                'P1b HotSpot result setter not uniquely editable')
        changed, diffs = build(
            assembler, root/'modified_p1b_origin', allow_edited=True,
            p1b_text=p1b_source.replace(needle, '    move.l #2,d3'))
        require(diffs == [p1b_imm],
                f'P1b hotspot edited bytes {diffs}, expected {[p1b_imm]}')
        require(unpack_ap20(changed)[1][group]
                [p1b_imm-5:p1b_imm+1] == bytes.fromhex('263c00000002'),
                'P1b hotspot MOVE.L #2 source edit was not assembled')
        require(p1b_start <= p1b_imm < p1b_end,
                'P1b edited byte escaped source range')
        pri_start, pri_end, pri_imm, _ = prove_p1c_priority_provenance()
        priority_source = P1C_PRIORITY_FILE.read_text('ascii')
        needle = '    move.l #1,d3'
        require(priority_source.count(needle) == 1, 'P1c priority result edit not unique')
        edited, changes = build(
            assembler, root/'modified_p1c_priority', allow_edited=True,
            p1c_priority_text=priority_source.replace(needle, '    move.l #2,d3'))
        require(changes == [pri_imm],
                f'P1c priority changed {changes}, expected {[pri_imm]}')
        require(unpack_ap20(edited)[1][group]
                [pri_imm-5:pri_imm+1] == bytes.fromhex('263c00000002'),
                'P1c priority edited machine instruction differs')
        require(pri_start <= pri_imm < pri_end, 'P1c priority edit escaped source')

        dis_start, dis_end, dis_imm, _ = prove_p1c_dispatch_provenance()
        dispatch_source = P1C_DISPATCH_FILE.read_text('ascii')
        needle = '    lea -160(a7),a7'
        require(dispatch_source.count(needle) == 1, 'P1c dispatch edit not unique')
        edited, changes = build(
            assembler, root/'modified_p1c_dispatch', allow_edited=True,
            p1c_dispatch_text=dispatch_source.replace(needle, '    lea -156(a7),a7'))
        require(changes == [dis_imm],
                f'P1c dispatch changed {changes}, expected {[dis_imm]}')
        require(unpack_ap20(edited)[1][group]
                [dis_imm-3:dis_imm+1] == bytes.fromhex('4fefff64'),
                'P1c dispatch edited stack frame LEA differs')
        require(dis_start <= dis_imm < dis_end, 'P1c dispatch edit escaped source')
        ctx_start, ctx_end, ctx_imm, _ = prove_p1c_context_provenance()
        ctx_source = P1C_CONTEXT_FILE.read_text('ascii')
        needle = '    movea.l #0,a0'
        require(ctx_source.count(needle) == 1, 'P1c context edit not unique')
        edited, diffs = build(
            assembler, root/'modified_p1c_context', allow_edited=True,
            p1c_context_text=ctx_source.replace(needle, '    movea.l #1,a0'))
        require(diffs == [ctx_imm],
                f'P1c context edit changed {diffs}, expected {[ctx_imm]}')
        require(unpack_ap20(edited)[1][group]
                [ctx_imm-5:ctx_imm+1] == bytes.fromhex('207c00000001'),
                'P1c context MOVEA.L edited instruction not assembled')
        require(ctx_start <= ctx_imm < ctx_end, 'P1c context edit escaped source')
        pre_start, pre_end, pre_imm, _ = prove_p1c_frame_preflight_provenance()
        pre_source = P1C_PRE_FILE.read_text('ascii')
        needle = '    move.l #1,44(a2)'
        require(pre_source.count(needle) == 1, 'P1c preflight edit not unique')
        changed, diffs = build(
            assembler, root/'modified_p1c_preflight', allow_edited=True,
            p1c_pre_text=pre_source.replace(needle, '    move.l #2,44(a2)'))
        require(diffs == [pre_imm],
                f'P1c frame preflight changed {diffs}, expected {[pre_imm]}')
        require(unpack_ap20(changed)[1][group]
                [pre_imm-5:pre_imm+3] == bytes.fromhex('257c00000002002c'),
                'P1c frame preflight one-byte mutation was not assembled')
        require(pre_start <= pre_imm < pre_end, 'P1c preflight edit escaped source')

        col_start, col_end, col_imm, _ = prove_p1c_order_collect_provenance()
        col_source = P1C_COL_FILE.read_text('ascii')
        needle = '    move.l #0,P1C_CURSOR(a2)'
        require(col_source.count(needle) == 1, 'P1c collector edit not unique')
        changed, diffs = build(
            assembler, root/'modified_p1c_collector', allow_edited=True,
            p1c_col_text=col_source.replace(needle, '    move.l #1,P1C_CURSOR(a2)'))
        require(diffs == [col_imm],
                f'P1c collect changed {diffs}, expected {[col_imm]}')
        require(unpack_ap20(changed)[1][group]
                [col_imm-5:col_imm+3] == bytes.fromhex('257c000000010020'),
                'P1c ordered key collection one-byte mutation not assembled')
        require(col_start <= col_imm < col_end, 'P1c collector edit escaped source')
    print('P2D_EDITABILITY_TEST PASS: MOVEQ #1,D3 -> #2,D3, one byte changed,')
    print('P2C_EDITABILITY_TEST PASS: MOVEQ #0,D3 -> #1,D3, one byte changed')
    print('P2B_PLANAR_EDITABILITY_TEST PASS: MOVEQ #0,D3 -> #1,D3, one byte changed')
    print('P2B_FLIP_EDITABILITY_TEST PASS: MOVEQ #0,D3 -> #1,D3, one byte changed')
    print('P2B_VARIANT_EDITABILITY_TEST PASS: MOVEQ #0,D3 -> #1,D3, one byte changed')
    print('P2B_PAINT_GEOMETRY_EDITABILITY_TEST PASS: MOVEQ #0,D3 -> #1,D3, one byte changed')
    print('P2B_CLEANUP_EDITABILITY_TEST PASS: MOVEQ #0,D2 -> #1,D2, one byte changed')
    print('P2A_PUBLIC_EDITABILITY_TEST PASS: MOVEQ #0,D2 -> #1,D2, one byte changed')
    print('P2A_QUERY_EDITABILITY_TEST PASS: MOVEQ #0,D2 -> #1,D2, one byte changed')
    print('P2A_KERNEL_EDITABILITY_TEST PASS: MOVE.L #-1,D3 -> #-2,D3, one byte changed')
    print('P2A_CHIP_EDITABILITY_TEST PASS: MOVEQ #0,D2 -> #1,D2, one byte changed')
    print('P2A_HOTSPOT_EDITABILITY_TEST PASS: MOVEQ #0,D2 -> #1,D2, one byte changed')
    print('P2A_GEOMETRY_EDITABILITY_TEST PASS: MOVEQ #0,D2 -> #1,D2, one byte changed')
    print('P2A_PAIR_CHECK_EDITABILITY_TEST PASS: MOVEQ #0,D2 -> #1,D2, one byte changed')
    print('P0I_ROUTED_PAINT_EDITABILITY_TEST PASS: MOVEQ #0,D2 -> #1,D2, one byte changed')
    print('B8_REGISTER_EDITABILITY_TEST PASS: MOVE.L #1,(A2) -> #2, one byte changed')
    print('B8S1_BANK_FREE_EDITABILITY_TEST PASS: MOVE.L #1,4(A2) -> #2, one byte changed')
    print('B7_END_EDITABILITY_TEST PASS: MOVE.L #0,4(A0) -> #1, one byte changed')
    print('P1B_HOTSPOT_EDITABILITY_TEST PASS: MOVE.L #1,D3 -> #2, one byte changed')
    print('P1C_PRIORITY_EDITABILITY_TEST PASS: MOVE.L #1,D3 -> #2, one byte changed')
    print('P1C_DISPATCH_EDITABILITY_TEST PASS: LEA -160(A7),A7 -> -156, one byte changed')
    print('P1C_CONTEXT_EDITABILITY_TEST PASS: MOVEA.L #0,A0 -> #1, one byte changed')
    print('P1C_PREFLIGHT_EDITABILITY_TEST PASS: MOVE.L #1,44(A2) -> #2, one byte changed')
    print('P1C_COLLECT_EDITABILITY_TEST PASS: MOVE.L #0,32(A2) -> #1, one byte changed')
    print('AP20 topology and all other groups unchanged; NOT a WinUAE Runtime test')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vasm', required=True, type=Path)
    parser.add_argument('--out', type=Path,
                        default=ROOT/'src'/'generated'/'p2d_editable')
    parser.add_argument('--allow-edited', action='store_true',
                        help='Output a same-size edited candidate ONLY in --out, NOT dist/')
    parser.add_argument('--self-test-edit', action='store_true',
                        help='Prove real modified-source vasm roundtrip without publishing a Lib')
    args = parser.parse_args()
    try:
        if args.self_test_edit:
            test_editability(args.vasm)
        else:
            build(args.vasm, args.out.resolve(), allow_edited=args.allow_edited)
        return 0
    except (SourceError, AssertionError, OSError, ValueError) as exc:
        print('[ERROR] P2d editable ASM: '+str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
