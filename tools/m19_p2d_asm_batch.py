#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-backed batched MC68020 extraction; never emits an installable Lib.

The historical Python emitter and the official P2d AP20 bytes are authoritative.
Audit mnemonics are used only after per-instruction byte verification.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'src/native/m19_p2d'
AUDIT = ROOT / 'src/asm_migration/m19_p2d/M19_P2D_BOBS_MC68020.s'

@dataclass(frozen=True)
class Region:
    name: str
    file: str
    start: int
    stop: int
    begin_label: str
    end_label: str
    needle: str
    replacement: str
    constant: str
    initial: int
    edited: int
    mutation: int
    pseudo_count: int
    owner: str = 'tools/m19_p1e_bank_edit_emit.py::emit_bank_edit'
    end_marker: str | None = None
    staged_end_marker: str | None = None
    start_marker: str | None = None
    raw_code: bool = False
    raw_overhang: int = 0
    raw_labels: tuple[str, ...] = ()
    raw_inclusive_start: bool = False

REGIONS = (
    Region('P1E_BOOT', 'M19_P1E_EDIT_BOOTSTRAP_MC68020.s',
           0x7F54, 0x8306, 'edit_begin', 'edit_objects',
           '    move.l #$00000000,8(a2)',
           '    move.l #P1E_BATCH_BOOT_ZERO,8(a2)',
           'P1E_BATCH_BOOT_ZERO', 0, 1, 0x7F59, 4),
    Region('P1E_COMMIT', 'M19_P1E_EDIT_COMMIT_MC68020.s',
           0x85A6, 0x85E8, 'edit_commit_next', 'edit_cleanup',
           '    move.l #$00000001,d3',
           '    move.l #P1E_BATCH_COMMIT_DONE,d3',
           'P1E_BATCH_COMMIT_DONE', 1, 2, 0x85E3, 2),
    Region('P0J_IMAGE_GATE', 'M19_P0J_IMAGE_GATE_MC68020.s',
           0x05F30, 0x06254, 'image_frame_preflight_entry', 'img_gate_return',
           '    move.l #$00000000,4(a2)',
           '    move.l #P0J_IMAGE_GATE_INITIAL_RESULT,4(a2)',
           'P0J_IMAGE_GATE_INITIAL_RESULT', 0, 1, 0x05F3F, 1,
           'tools/m19_p0j_frame_image_preflight_emit.py::emit_image_preflight'),
    Region('P0J_EXPLICIT_BANK', 'M19_P0J_EXPLICIT_BANK_MC68020.s',
           0x0627E, 0x0685C, 'explicit_bank_lookup_entry', 'explicit_safe_front_zero',
           '    move.l #$00000000,36(a2)',
           '    move.l #P0J_BANK_STAGE_CLEAR_RESULT,36(a2)',
           'P0J_BANK_STAGE_CLEAR_RESULT', 0, 1, 0x06293, 2,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),
    Region('B7_B8_DRAW_BRIDGE', 'M19_B7_B8_DRAW_BRIDGE_MC68020.s',
           0x06FA6, 0x071E8, 'b7_multiframe_draw_entry', 'b8_b7_close_return',
           '    move.l #$00000001,(a0)',
           '    move.l #B7_B8_DRAW_FAIL_FLAG,(a0)',
           'B7_B8_DRAW_FAIL_FLAG', 1, 2, 0x070C7, 0,
           'tools/m19_b8_b7_hook_emit.py::emit_b8_b7_hooks'),
    Region('B8_NODRAW_PRESTAGE', 'M19_B8_NODRAW_PRESTAGE_MC68020.s',
           0x07364, 0x07698, 'b8_b7_arm_end_nodraw_entry', 'b8s1_bank_return',
           '    move.l #$00000000,(a2)',
           '    move.l #B8_PRESTAGE_INITIAL_RESULT,(a2)',
           'B8_PRESTAGE_INITIAL_RESULT', 0, 1, 0x07373, 0,
           'tools/m19_b8_s1_bank_prestage_emit.py::emit_b8_s1_bank_prestage'),
    Region('P0J_SAFE_TAIL', 'M19_P0J_SAFE_TAIL_MC68020.s',
           0x0685C, 0x068FA, 'explicit_safe_front_zero', 'p1b_frame_draw_entry',
           '    move.l 68(a4),d0',
           '    move.l P0J_SAFE_ARG_OFFSET(a4),d0',
           'P0J_SAFE_ARG_OFFSET', 68, 72, 0x068E9, 0,
           'tools/m19_p0j_explicit_safe_draw_emit.py::emit_explicit_safe_draw'),
    Region('P1B_FRAME_GUARD', 'M19_P1B_FRAME_GUARD_MC68020.s',
           0x06902, 0x06D36, 'p1b_frame_body', 'frame_guard_state',
           '    move.l #$00000000,4(a2)',
           '    move.l #P1B_FRAME_GATE_INITIAL_RESULT,4(a2)',
           'P1B_FRAME_GATE_INITIAL_RESULT', 0, 1, 0x06909, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),
    Region('B7_GUARDED_DRAW', 'M19_B7_GUARDED_DRAW_MC68020.s',
           0x06D4E, 0x06EAC, 'b7_guarded_draw_entry', 'b7_end_entry',
           '    move.l #$00000001,(a0)',
           '    move.l #B7_GUARD_DIRTY_ON_CONFLICT,(a0)',
           'B7_GUARD_DIRTY_ON_CONFLICT', 1, 2, 0x06E97, 0,
           'tools/m19_p0j_end_lifecycle_emit.py::emit_end_lifecycle'),

    Region('P0_PRE_CLOSE', 'M19_P0_SCREEN_PRECLOSE_MC68020.s',
           0x046D4, 0x048FA, 'screen_preclose_entry', 'program_end_bridge_entry',
           '    move.l #$00000000,8(a2)',
           '    move.l #P0_PRE_CLOSE_STATE_ZERO,8(a2)',
           'P0_PRE_CLOSE_STATE_ZERO', 0, 1, 0x046F1, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),
    Region('P0_BANK_IMAGE_RESOLVE', 'M19_P0_BANK_IMAGE_RESOLVE_MC68020.s',
           0x049A8, 0x05A5C, 'bank_image_resolve_entry', 'relay_put_entry',
           '    move.l #$00000000,108(a2)',
           '    move.l #P0_IMAGE_RESOLVE_STAGE_ZERO,108(a2)',
           'P0_IMAGE_RESOLVE_STAGE_ZERO', 0, 1, 0x049C1, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='relay_put_entry:'),

    Region('P0_RELAY_COMMANDS', 'M19_P0_RELAY_COMMANDS_MC68020.s',
           0x05A6A, 0x05B6E, 'relay_off_entry', 'public_aga_bob_entry',
           '    move.l #$0000000E,d7',
           '    move.l #P0_RELAY_OFF_SELECTOR,d7',
           'P0_RELAY_OFF_SELECTOR', 14, 15, 0x05A73, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),
    Region('P0_PUBLIC_FRAME', 'M19_P0_PUBLIC_FRAME_MC68020.s',
           0x05B6E, 0x05CF8, 'public_aga_bob_entry', 'routed_paint_one_entry',
           '    move.l #$00000001,4(a2)',
           '    move.l #P0_FRAME_ALL_OK_FLAG,4(a2)',
           'P0_FRAME_ALL_OK_FLAG', 1, 2, 0x05CE5, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='routed_paint_one_entry:',
           staged_end_marker='    include "M19_P0I_ROUTED_PAINT_MC68020.s"'),

    Region('P2D_SUPPORT_TAIL', 'M19_P2D_SUPPORT_TAIL_MC68020.s',
           0x0B72A, 0x0C4FE, '', '',
           '    move.l #$00000000,28(a2)',
           '    move.l #P2D_TAIL_SCRATCH_ZERO,28(a2)',
           'P2D_TAIL_SCRATCH_ZERO', 0, 1, 0x0B74B, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),
    Region('P2D_SYSTEM_SERVICE', 'M19_P2D_SYSTEM_SERVICE_MC68020.s',
           0x0DA30, 0x0DCB4, '', '',
           '    move.l #$00000001,20(a4)',
           '    move.l #P2D_SYSTEM_SUCCESS_FLAG,20(a4)',
           'P2D_SYSTEM_SUCCESS_FLAG', 1, 2, 0x0DC11, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),

    Region('P2D_SERVICE_BODY', 'M19_P2D_SERVICE_BODY_MC68020.s',
           0x0C51E, 0x0DA10, '', '',
           '    move.l #$00000001,36(a4)',
           '    move.l #P2D_SERVICE_MODE_ONE,36(a4)',
           'P2D_SERVICE_MODE_ONE', 1, 2, 0x0D837, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),

    Region('P2D_SERVICE_GUARDS', 'M19_P2D_SERVICE_GUARDS_MC68020.s',
           0x0DD96, 0x0E538, '', '',
           '    move.l #$00000000,(a2)',
           '    move.l #P2D_GUARD_INIT_ZERO,(a2)',
           'P2D_GUARD_INIT_ZERO', 0, 1, 0x0DDA5, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='    dc.b $48,$E7,$CF,$EE,$4F,$EF,$FF,$A0,$28,$4F,$28,$BC  ; +$0E538: 48E7CFEE4FEFFFA0284F28BC'),

    Region('P2D_PUBLIC_UPDATE', 'M19_P2D_PUBLIC_UPDATE_MC68020.s',
           0x0E5C8, 0x0EDD0, '', '',
           '    move.l #$00000003,4(a4)',
           '    move.l #P2D_PUBLIC_MODE_THREE,4(a4)',
           'P2D_PUBLIC_MODE_THREE', 3, 4, 0x0E701, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='ENTRY_BOBS_0EDD0:'),

    Region('P0_CHECKED_REGISTRY', 'M19_P0_CHECKED_REGISTRY_MC68020.s',
           0x03792, 0x046CC, '', '',
           '    move.l #$00000000,d3',
           '    move.l #P0_REGISTRY_INITIAL_STATUS,d3',
           'P0_REGISTRY_INITIAL_STATUS', 0, 1, 0x037B3, 2,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),

    Region('P1B_HOTSPOT_JOIN', 'M19_P1B_HOTSPOT_JOIN_MC68020.s',
           0x07962, 0x079F2, '', '',
           '    move.l #$00000000,d5',
           '    move.l #P1B_JOIN_START_ZERO,d5',
           'P1B_JOIN_START_ZERO', 0, 1, 0x0798B, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='p2b_paint_continue:'),

    Region('P0_CORE_DISPATCH', 'M19_P0_CORE_DISPATCH_MC68020.s',
           0x00022, 0x020A2, '', '',
           '    move.l #$00000002,144(a2)',
           '    move.l #P0_CORE_BUFFER_MODE,144(a2)',
           'P0_CORE_BUFFER_MODE', 2, 3, 0x00447, 12,
           'tools/build_m19_p2d_in_memory.py::build_p2d',
           start_marker='ENTRY_BOBS_00022:'),

    Region('P0_GET_PIPELINE', 'M19_P0_GET_PIPELINE_MC68020.s',
           0x020CE, 0x03772, '', '',
           '    move.l #$00000001,48(a2)',
           '    move.l #P0_GET_FRAME_VALID,48(a2)',
           'P0_GET_FRAME_VALID', 1, 2, 0x023E7, 4,
           'tools/build_m19_p2d_in_memory.py::build_p2d',
           start_marker='get_entry:'),
    Region('P0J_IMAGE_RETURN', 'M19_P0J_IMAGE_RETURN_MC68020.s',
           0x06254, 0x06264, '', '',
           '    move.l 4(a2),d3',
           '    move.l P0J_IMAGE_RESULT_OFFSET(a2),d3',
           'P0J_IMAGE_RESULT_OFFSET', 4, 8, 0x06257, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='routed_paint_prechecked_entry:'),
    Region('B8S1_BANK_RETURN', 'M19_B8S1_BANK_RETURN_MC68020.s',
           0x07698, 0x076A8, '', '',
           '    move.l 36(a2),d3',
           '    move.l B8S1_BANK_RESULT_OFFSET(a2),d3',
           'B8S1_BANK_RESULT_OFFSET', 36, 40, 0x0769B, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='b8s1_bank_free_entry:',
           staged_end_marker='    include "M19_B8S1_BANK_FREE_MC68020.s"'),
    Region('P2D_SERVICE_RETURN', 'M19_P2D_SERVICE_RETURN_MC68020.s',
           0x0E59E, 0x0E5B0, '', '',
           '    move.l #$00000000,d2',
           '    move.l #P2D_SERVICE_RETURN_D2,d2',
           'P2D_SERVICE_RETURN_D2', 0, 1, 0x0E5A5, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update'),
    Region('P2D_PUBLIC_QUERY_HEAD', 'M19_P2D_PUBLIC_QUERY_HEAD_MC68020.s',
           0x0EDD0, 0x0EDF4, '', '',
           '    move.l 4(a7),d3',
           '    move.l P2D_PUBLIC_VALUE_OFFSET(a7),d3',
           'P2D_PUBLIC_VALUE_OFFSET', 4, 8, 0x0EDE9, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           start_marker='ENTRY_BOBS_0EDD0:'),
    Region('P1B_FRAME_BRANCH', 'M19_P1B_FRAME_BRANCH_MC68020.s',
           0x068FA, 0x068FE, '', '',
           '    bra.w L_BOBS_07AC2',
           '    bra.w L_BOBS_07AC2+P1B_BRANCH_LOW_BYTE-198',
           'P1B_BRANCH_LOW_BYTE', 198, 200, 0x068FD, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='    dc.b $4E,$71,$4E,$71  ; +$068FE: 4E714E71'),
    Region('B8_CLOSE_BRANCH', 'M19_B8_CLOSE_BRANCH_MC68020.s',
           0x071E8, 0x071EC, '', '',
           '    bra.w L_BOBS_0A1D2',
           '    bra.w L_BOBS_0A1D2+B8_CLOSE_BRANCH_LOW_BYTE-232',
           'B8_CLOSE_BRANCH_LOW_BYTE', 232, 234, 0x071EB, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='    dc.b $4E,$75  ; +$071EC: 4E75'),
    Region('P2D_PUBLIC_QUERY_TAIL', 'M19_P2D_PUBLIC_QUERY_TAIL_MC68020.s',
           0x0EDF4, 0x0EE00, '', '',
           '    moveq #0,d2',
           '    moveq #P2D_QUERY_RETURN_ZERO,d2',
           'P2D_QUERY_RETURN_ZERO', 0, 1, 0x0EDFD, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='__BOBS_EOF__'),
    Region('P0_RELAY_PUT', 'M19_P0_RELAY_PUT_MC68020.s',
           0x05A5C, 0x05A6A, '', '',
           '    move.l #$00000000,d7',
           '    move.l #P0_RELAY_PUT_OFFSET,d7',
           'P0_RELAY_PUT_OFFSET', 0, 1, 0x05A65, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           start_marker='relay_put_entry:', raw_code=True),
    Region('P0J_PRECHECKED_PAINT', 'M19_P0J_PRECHECKED_PAINT_MC68020.s',
           0x06264, 0x0627E, '', '',
           '    moveq #0,d2',
           '    moveq #P0J_PRECHECK_RETURN_D2,d2',
           'P0J_PRECHECK_RETURN_D2', 0, 1, 0x0627B, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           start_marker='routed_paint_prechecked_entry:', raw_code=True),
    Region('P1B_PAINT_CONTINUE', 'M19_P1B_PAINT_CONTINUE_MC68020.s',
           0x079F2, 0x07A14, '', '',
           '    move.l #$00000001,116(a4)',
           '    move.l #P1B_PAINT_CLIPPED_FLAG,116(a4)',
           'P1B_PAINT_CLIPPED_FLAG', 1, 2, 0x07A0D, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           end_marker='    dc.b $24,$01,$30,$28,$00,$1C,$48,$C0,$94,$80,$26,$04  ; +$07A16: 24013028001C48C094802604',
           staged_end_marker='    include "M19_P1B_HOTSPOT_ORIGIN_MC68020.s"',
           start_marker='p2b_paint_continue:', raw_code=True, raw_overhang=2),
    Region('P0C_PROGRAM_END_CALLBACK', 'M19_P0C_PROGRAM_END_CALLBACK_MC68020.s',
           0x048FA, 0x049A8, '', '',
           '    andi.l #$00000001,d0',
           '    andi.l #P0C_CALLBACK_OWNER_ALIGNMENT,d0',
           'P0C_CALLBACK_OWNER_ALIGNMENT', 1, 2, 0x04915, 0,
           'tools/m19_p0c_program_end_bridge_emit.py::emit_program_end_bridge',
           start_marker='program_end_bridge_entry:', raw_code=True,
           raw_labels=('end_bridge_return:',)),
    Region('P2D_SERVICE_UPDATE_BRIDGE', 'M19_P2D_SERVICE_UPDATE_BRIDGE_MC68020.s',
           0x0DCB4, 0x0DD96, '', '',
           '    move.l #$00000000,20(a4)',
           '    move.l #P2D_SERVICE_BRIDGE_INITIAL_RESULT,20(a4)',
           'P2D_SERVICE_BRIDGE_INITIAL_RESULT', 0, 1, 0x0DCC3, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           raw_code=True),
    Region('P2D_SERVICE_ROOT_RESET', 'M19_P2D_SERVICE_ROOT_RESET_MC68020.s',
           0x0E538, 0x0E59E, '', '',
           '    move.l #$00000000,(a4)',
           '    move.l #P2D_SERVICE_RESET_INITIAL_RESULT,(a4)',
           'P2D_SERVICE_RESET_INITIAL_RESULT', 0, 1, 0x0E547, 0,
           'tools/m19_p2d_bob_auto_update_emit.py::emit_bob_auto_update',
           start_marker='    dc.b $48,$E7,$CF,$EE,$4F,$EF,$FF,$A0,$28,$4F,$28,$BC  ; +$0E538: 48E7CFEE4FEFFFA0284F28BC', raw_code=True,
           raw_inclusive_start=True),
)
ANNOTATION = re.compile(r'\s+; \+\$([0-9A-F]{5}): ([0-9A-F]+)\s*$')
LABEL = re.compile(r'[A-Za-z_][A-Za-z_0-9]*:\s*$')
PSEUDO = re.compile(r'\s*dc\.w \$FE11,\$F700,AMOS_MAIN_[A-Z_]+\s*$')
DATA = re.compile(r'^\s*dcb?\.[bwl]\s+', re.I)

class BatchError(ValueError):
    pass

def require(ok, why):
    if not ok:
        raise BatchError(why)

@lru_cache(maxsize=1)
def _source_p2c_prefix(prefix):
    """Original P2c source-built BOBS prefix; independent SHA-pinned proof."""
    from active_library import P2C_SHA
    from build_m19_p2c_in_memory import build_p2c
    from compiler_relocation import unpack_ap20
    prior, info = build_p2c()
    require(info['sha256'] == P2C_SHA and
            sha256(prior).hexdigest() == P2C_SHA,
            'P2c prior source provenance SHA mismatch')
    _, parts, _ = unpack_ap20(prior)
    group = info['bob_group']
    require(0 <= group < len(parts) and 0 <= prefix <= len(parts[group]),
            'P2c BOBS source prefix boundaries changed')
    return parts[group][:prefix]


def prove_regions(native, labels, group, proven_p2c_prefix=None):
    """Two independently source-built owners: P2c prefix and P2d native suffix."""
    prefix = len(group)-len(native)
    require(prefix >= 0 and group[prefix:] == native, 'P2d emitter suffix drift')
    if proven_p2c_prefix is None:
        proven_p2c_prefix = _source_p2c_prefix(prefix)
    require(len(proven_p2c_prefix) == prefix and
            group[:prefix] == proven_p2c_prefix,
            'P2c source-built prefix differs from official P2d')
    evidence = {}
    previous = 0
    for spec in sorted(REGIONS, key=lambda r: r.start):
        require(spec.start >= previous, 'overlapping batch ownership')
        previous = spec.stop
        if spec.owner == 'tools/build_m19_p2d_in_memory.py::build_p2d':
            # Composite source ownership: the P2c SHA-pinned prefix and
            # the independently verified P2d emitter suffix. This region
            # can cross their exact boundary, but every byte must be proven.
            require(not spec.begin_label and not spec.end_label and
                    0 <= spec.start < spec.stop <= len(group),
                    'invalid composite source region: '+spec.name)
            p2c_end = min(spec.stop, prefix)
            prior = (proven_p2c_prefix[spec.start:p2c_end]
                     if spec.start < p2c_end else b'')
            p2d_begin = max(spec.start,prefix)-prefix
            p2d_end = spec.stop-prefix
            appended = (native[p2d_begin:p2d_end]
                        if p2d_begin < p2d_end else b'')
            chunk = prior + appended
            require(len(chunk) == spec.stop-spec.start,
                    'incomplete composite source ownership: '+spec.name)
        elif spec.stop <= prefix:
            # Dedicated prefix-only regions must name the source P2c builder.
            require(not spec.begin_label and not spec.end_label,
                    'P2c prefix requires absolute source-verified region: '+spec.name)
            require(spec.owner == 'tools/build_m19_p2c_in_memory.py::build_p2c',
                    'wrong source owner for P2c prefix: '+spec.name)
            a,b = spec.start,spec.stop
            chunk = proven_p2c_prefix[a:b]
        else:
            require(spec.start >= prefix,
                    'region crosses P2c/P2d source ownership boundary: '+spec.name)
            if spec.begin_label and spec.end_label:
                require(spec.begin_label in labels and spec.end_label in labels,
                        'missing P2d emitter labels: '+spec.name)
                a,b = labels[spec.begin_label],labels[spec.end_label]
                require(a < b and prefix+a == spec.start and
                        prefix+b == spec.stop,
                        'P2d emitter offset drift: '+spec.name)
            else:
                require(not spec.begin_label and not spec.end_label,
                        'partial P2d emitter-label ownership: '+spec.name)
                a,b = spec.start-prefix,spec.stop-prefix
                require(0 <= a < b <= len(native),
                        'offset span outside P2d source emitter: '+spec.name)
            chunk = native[a:b]
        require(group[spec.start:spec.stop] == chunk and
                len(chunk) == spec.stop-spec.start and
                chunk[spec.mutation-spec.start] == spec.initial,
                'P2d source/size/mutation mismatch: '+spec.name)
        evidence[spec.name] = chunk
    return evidence


def bounds(spec, *, staged=False):
    last = (spec.staged_end_marker if staged and
            spec.staged_end_marker is not None else spec.end_marker)
    first = ((spec.start_marker + '\n') if spec.start_marker is not None
             else ('L_BOBS_%05X:\n' % spec.start))
    if last == '__BOBS_EOF__':
        return first, ''
    return (first,
            (last + '\n') if last is not None
            else ('L_BOBS_%05X:\n' % spec.stop))

def extract(text, spec, bytes_expected, *, staged=False):
    first,last = bounds(spec, staged=staged)
    i = text.find(first)
    j = len(text) if not last else text.find(last,i+len(first))
    require(i >= 0 and j > i and text.find(first,i+len(first)) < 0,
            'audit boundaries missing/ambiguous: '+spec.name)
    result,actual,offset,pseudo = [],bytearray(),spec.start,0
    raw_lines = 0
    clipped = 0
    code_begin = i if spec.raw_inclusive_start else i+len(first)
    for line in text[code_begin:j].splitlines():
        if LABEL.fullmatch(line):
            result.append(line)
            continue
        if not line.strip():
            continue
        match = ANNOTATION.search(line)
        require(match is not None, 'unclassified audit source line: '+line)
        inst = line[:match.start()].rstrip()
        code = bytes.fromhex(match.group(2))
        require(int(match.group(1),16) == offset, 'audit gap at %05X' % offset)
        if spec.raw_code and offset < spec.stop < offset+len(code):
            overflow = offset + len(code) - spec.stop
            require(not staged and overflow == spec.raw_overhang and
                    not clipped, 'unverified raw audit byte overhang: '+spec.name)
            code = code[:-overflow]
            clipped = overflow
        if DATA.match(inst):
            if spec.raw_code:
                require(inst.lstrip().lower().startswith('dc.b '),
                        'raw island contains non-byte data: '+spec.name)
                raw_lines += 1
            else:
                require(PSEUDO.fullmatch(inst) is not None and len(code)==6 and
                        code[:4] == bytes.fromhex('fe11f700'),
                        'data/unverified pseudo-opcode: '+inst)
                pseudo += 1
        else:
            require(not spec.raw_code,
                    'mixed raw bytes and mnemonic instructions: '+spec.name)
        actual.extend(code)
        offset += len(code)
        result.append(inst)
    require(offset == spec.stop and bytes(actual)==bytes_expected and
            pseudo==spec.pseudo_count,
            'P1e audit/emitter bytes or AMOS ABI count changed: '+spec.name)
    if spec.raw_code:
        labels = tuple(line for line in result if LABEL.fullmatch(line))
        require(raw_lines > 0 and labels == spec.raw_labels and
                len(result) == raw_lines + len(labels) and
                clipped == (0 if staged else spec.raw_overhang),
                'raw code island contains unexpected labels, gap or bad end: '+spec.name)
        # The native module is handwritten; source-built bytes plus direct
        # MC68020 vasm AP20 byte identity, not disassembly, prove correctness.
        return ''
    body = '\n'.join(result).rstrip()+'\n'
    require(body.count(spec.needle)==1, 'editable instruction not unique')
    return body.replace(spec.needle,spec.replacement)

def render(spec, body):
    return ('; AGA_NATIVE_MIN_CPU: MC68020\n'
            f'; Historical owner: {spec.owner}\n'
            '; Audited bytes checked against the official M19 P2d library.\n'
            '; BOBS+$%05X..$%05X (%d bytes).\n' %
            (spec.start,spec.stop,spec.stop-spec.start) +
            '; AMOS Main symbolic pseudo-ops preserve six-byte ABI.\n'
            '%s equ %d\n\n' % (spec.constant,spec.initial) + body)

def replace_raw_sections(text, evidence):
    """All-or-nothing source validation before any textual replacement."""
    replacements = []
    for spec in REGIONS:
        extract(text,spec,evidence[spec.name],staged=True)
        first,last = bounds(spec, staged=True)
        i = text.index(first)
        j = len(text) if not last else text.index(last,i+len(first))
        prefix = '' if spec.raw_inclusive_start else first
        replacements.append((i,j,prefix+'    include "'+spec.file+'"\n'))
    for i,j,segment in sorted(replacements,reverse=True):
        text = text[:i]+segment+text[j:]
    return text

def stage_modules(folder,overrides=None):
    overrides = overrides or {}
    require(set(overrides).issubset({s.file for s in REGIONS}),
            'unexpected P1e batch module')
    for spec in REGIONS:
        source_file = NATIVE/spec.file
        require(source_file.is_file(), 'missing source: '+str(source_file))
        text = overrides.get(spec.file,source_file.read_text('ascii'))
        require(text.count('; AGA_NATIVE_MIN_CPU: MC68020')==1 and
                (not spec.begin_label or
                 text.count(spec.begin_label+':')==1) and
                text.count(spec.constant+' equ ')==1 and
                not any(DATA.match(l) and not PSEUDO.fullmatch(l)
                        for l in text.splitlines()),
                'invalid authored batch source: '+spec.name)
        (folder/spec.file).write_text(text,encoding='ascii',newline='\n')

def quick_edits():
    """Mutate one instruction per module; one reassembly checks both deltas."""
    changed,offsets = {},[]
    for spec in REGIONS:
        text = (NATIVE/spec.file).read_text('ascii')
        before = '%s equ %d' % (spec.constant,spec.initial)
        require(text.count(before)==1, 'nonunique batch edit')
        changed[spec.file] = text.replace(
            before,'%s equ %d' % (spec.constant,spec.edited))
        offsets.append(spec.mutation)
    return changed,sorted(offsets)

def check_sources(audit,evidence,compare_files=True):
    for spec in REGIONS:
        body = extract(audit,spec,evidence[spec.name])
        if spec.raw_code:
            source = (NATIVE/spec.file).read_text('ascii')
            header = render(spec,'')
            require(source.startswith(header) and
                    source.count(spec.replacement)==1 and
                    source.endswith('\n'),
                    'invalid authored raw island header: '+spec.name)
            actual_body = source[len(header):]
            require(bool(actual_body.strip()) and
                    not any(DATA.match(line) for line in actual_body.splitlines()),
                    'authored raw island must be mnemonic ASM: '+spec.name)
            # The direct MC68020 assembly and final P2d SHA prove bytes.
        else:
            source = render(spec,body)
            if compare_files:
                require((NATIVE/spec.file).read_text('ascii') == source,
                        'authored module differs from emitter proof: '+spec.file)
        print('BOBS_SOURCE_PROVEN %s %d bytes' %
              (spec.name,spec.stop-spec.start))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan',action='store_true')
    mode.add_argument('--check',action='store_true')
    mode.add_argument('--emit',type=Path)
    args = parser.parse_args()
    try:
        from build_m19_p2d_editable_asm import (
            prove_source_provenance,build_p1e,emit_bob_auto_update,
            unpack_ap20,replace_source_backed_amos_pseudo,
            replace_raw_p1e_cleanup)
        official, group, *_ = prove_source_provenance()
        _,meta = build_p1e()
        native,labels,_ = emit_bob_auto_update(meta['context_delta'])
        _,parts,_ = unpack_ap20(official)
        # The BOBS prefix is inherited unchanged from the P2c source-built
        # library, protected by its own SHA. P2d emitter owns only the suffix.
        from active_library import P2C_SHA
        from build_m19_p2c_in_memory import build_p2c
        prior, prior_info = build_p2c()
        require(prior_info['sha256'] == P2C_SHA and
                sha256(prior).hexdigest() == P2C_SHA,
                'P2c source builder SHA mismatch')
        _, prior_parts, _ = unpack_ap20(prior)
        prior_group = prior_info['bob_group']
        require(0 <= prior_group < len(prior_parts),
                'missing P2c BOBS source group')
        prefix = len(parts[group])-len(native)
        require(prefix >= 0 and len(prior_parts[prior_group]) >= prefix,
                'P2c/P2d BOBS prefix size changed')
        p2c_prefix = prior_parts[prior_group][:prefix]
        print('BOBS_P2C_P2D_EMITTER_BOUNDARY $%05X' % prefix)
        evidence = prove_regions(native,labels,parts[group],p2c_prefix)
        # The cleanup Lst.Del pseudo-op has an authored module already.
        # Replicate builder staging so the 27 remaining raw calls are counted.
        audit = replace_raw_p1e_cleanup(AUDIT.read_text('ascii'))
        audit = replace_source_backed_amos_pseudo(audit)
        check_sources(audit,evidence,compare_files=args.check)
        if args.emit:
            out = args.emit.resolve()
            require(out!=ROOT/'dist' and ROOT/'dist' not in out.parents,
                    'no candidate can be written to dist/')
            out.mkdir(parents=True,exist_ok=True)
            for spec in REGIONS:
                target = out/spec.file
                require(not target.exists(), 'refuse overwrite '+str(target))
                source = ((NATIVE/spec.file).read_text('ascii') if spec.raw_code
                          else render(spec,extract(audit,spec,evidence[spec.name])))
                target.write_text(source,encoding='ascii',newline='\n')
        print('BOBS_BATCH_STATIC_PASS')
        return 0
    except (BatchError,ValueError,OSError) as error:
        print('[ERROR] P1e batch: '+str(error))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
