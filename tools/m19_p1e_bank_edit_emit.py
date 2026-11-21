#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Edit an owned AMOS AGBO bank and publish its detached cache and Bob stamps."""
from struct import pack

from amos_main_abi import main_index, rjsr
from m19_p0a_amos_bank_transaction_emit import CUR_BANKS_A5
from m19_p0c_checked_bank_stage_emit import F as VALIDATOR, FRAME as VALIDATOR_FRAME
from m19_p0e_v2_object_bridge_emit import OBJ_RELATIVE
from m19_p0f_object_identity_emit import AGA_CORE, OBJ, OBJ_LABELS, STAMP_BYTES, emit_object_identity
from m19_p0j_swap_barrier_emit import G as GUARD
from m19_p1d_limit_bob_emit import emit_limit_bobs
from m19_p1e_bank_repack_emit import ARGUMENTS, emit_bank_repack
from m68k_emit import A, Code, D, I, M, POST

STAMP = OBJ_RELATIVE + len(OBJ) + len(AGA_CORE) + emit_object_identity()[1]['identity_stamp_table']
OBJECT = OBJ_RELATIVE + OBJ_LABELS['object_table']
ROOT = OBJ_RELATIVE + OBJ_LABELS['object_root']
STATE = 0x1c8
FRAME = 256
F = {name: i * 4 for i, name in enumerate(ARGUMENTS + (
    'bank', 'state', 'gfx', 'bank_head', 'bank_link',
    'old_node', 'new_node', 'detached', 'generation', 'old_generation',
    'reg_root', 'reg_link', 'old_cache', 'new_cache', 'objects', 'stamps',
    'object_owner',
))}
assert max(F.values()) + 4 <= FRAME


def emit_bank_edit(context_delta):
    old, labels = emit_limit_bobs(context_delta)
    c = Code()
    c.b.extend(old)
    c.labels.update(labels)
    B, L = c.branch, c.label

    def get(name, reg):
        c.move(M(2, F[name]), reg)

    def save(reg, name):
        c.move(reg, M(2, F[name]))

    def lea(dst, base, displacement):
        c.word(0x41e8 | dst << 9 | base); c.word(displacement)

    def adda(reg, amount):
        c.word(0xd1fc | reg << 9); c.b.extend(pack('>i', amount))

    def amos(name):
        c.b.extend(rjsr(main_index(name)))

    def library(offset):
        c.raw('2c780004'); c.call_os(offset)

    def map_pointer(name, last=0):
        get(name, D(0)); c.tst(D(0)); B(7, 'edit_cleanup')
        c.move(D(0), D(1)); c.imm('and', 1, D(1)); B(6, 'edit_cleanup')
        for offset in dict.fromkeys((0, last)):
            get(name, D(0))
            if offset:
                c.imm('add', offset, D(0)); B(5, 'edit_cleanup')
            c.move(D(0), A(1))
            library(-534); c.tst(D(0)); B(7, 'edit_cleanup')

    def check_source():
        get('bank', D(0)); amos('Bnk.GetAdr')
        c.move(A(0), D(0)); c.alu('cmp', M(2, F['source']), 0); B(6, 'edit_cleanup')
        c.move(M(5, CUR_BANKS_A5), D(0))
        c.alu('cmp', M(2, F['bank_head']), 0); B(6, 'edit_cleanup')
        for field, offset in (('size', 20), ('old_generation', 24)):
            get(field, D(0))
            c.alu('cmp', M(0, offset), 0); B(6, 'edit_cleanup')

    def begin(name):
        L(name)
        c.raw('48e7efee')
        c.word(0x4fef); c.word(-FRAME)
        c.move(A(7), A(2))

    begin('p1e_del_bob')
    save(D(3), 'last')
    c.tst(D(3)); B(7, 'edit_bad_del')
    save(POST(3), 'first'); save(POST(3), 'bank')
    B(0, 'edit_begin')
    L('edit_bad_del')
    c.move(POST(3), D(0)); c.move(POST(3), D(0))
    c.move(I(0), D(3)); B(0, 'edit_return')

    begin('p1e_ins_bob')
    save(D(3), 'depth')
    for field in ('height', 'width', 'first', 'bank'):
        save(POST(3), field)
    save(I(0), 'last')

    L('edit_begin')
    for field in ('dest', 'capacity', 'new_node', 'detached', 'new_cache'):
        save(I(0), field)
    B(1, 'p1c_context')
    c.move(A(0), D(0)); B(7, 'edit_cleanup')
    c.lea(0, 'frame_guard_state')
    c.tst(M(0, GUARD['status'])); B(6, 'edit_cleanup')
    c.move(M(5, STATE), A(0)); save(A(0), 'state')
    save(M(0, 8), 'gfx'); map_pointer('gfx')
    get('bank', D(0))
    c.imm('cmp', 5, D(0)); B(5, 'edit_cleanup')
    c.imm('cmp', 65535, D(0)); B(2, 'edit_cleanup')
    c.move(M(5, CUR_BANKS_A5), D(0)); save(D(0), 'bank_head')
    map_pointer('bank_head')
    get('bank', D(0)); amos('Bnk.GetAdr')
    save(A(0), 'source')
    c.move(A(0), D(0)); c.imm('cmp', 24, D(0)); B(5, 'edit_cleanup')
    c.imm('sub', 24, D(0)); save(D(0), 'old_node')
    map_pointer('old_node', 23)
    get('bank', D(3)); get('source', A(0))
    B(1, 'edit_validate_bank'); c.tst(D(3)); B(7, 'edit_cleanup')
    get('source', A(0))
    save(M(0, 20), 'size'); save(M(0, 24), 'old_generation')
    c.move(A(2), A(0))
    B(1, 'edit_repack')
    c.tst(D(3)); B(7, 'edit_cleanup')
    save(D(3), 'capacity')

    # Build a detached AMOS node via the real AMOS list allocator.
    lea(0, 2, F['detached'])
    get('capacity', D(0)); c.imm('add', 16, D(0))
    c.move(I(0x10001), D(1))
    get('old_node', A(4))
    c.move(M(4, 12), D(4), 'w')
    c.imm('and', 2, D(4), 'w')
    B(7, 'edit_allocate')
    c.quick(2, D(1))
    L('edit_allocate')
    amos('Lst.Cree')
    c.tst(D(0)); B(7, 'edit_cleanup')
    c.move(A(1), D(0)); B(7, 'edit_cleanup')
    save(A(1), 'new_node')
    check_source()
    get('new_node', A(1)); get('bank', D(0)); c.move(D(0), M(1, 8))
    get('old_node', A(0))
    for offset in (12, 16, 20):
        c.move(M(0, offset), M(1, offset))
    lea(0, 1, 24); save(A(0), 'dest')
    c.move(A(2), A(0))
    B(1, 'edit_repack'); c.tst(D(3)); B(7, 'edit_cleanup')
    get('dest', A(0)); save(M(0, 24), 'generation')
    c.tst(M(0, 8), 'w'); B(7, 'edit_find_links')
    c.move(I(32), D(0)); c.move(I(0x10001), D(1))
    library(-684); c.tst(D(0)); B(7, 'edit_cleanup')
    save(D(0), 'new_cache')
    c.move(D(0), A(0)); get('bank', D(0)); c.move(D(0), M(0, 4))
    lea(1, 0, 8)
    get('dest', A(0)); c.move(M(0, 16), D(0))
    get('capacity', D(4)); c.alu('sub', D(0), 4)
    c.raw('d1c0')  # ADDA.L D0,A0, validated data region.
    c.move(D(4), D(0)); get('dest', D(1))
    get('generation', D(4)); get('gfx', A(4))
    B(1, 'checked_chip_stage'); c.tst(D(3)); B(7, 'edit_cleanup')

    L('edit_find_links')
    check_source()
    c.move(M(5, STATE), D(0)); c.alu('cmp', M(2, F['state']), 0); B(6, 'edit_cleanup')
    c.lea(0, 'frame_guard_state')
    c.tst(M(0, GUARD['status'])); B(6, 'edit_cleanup')
    get('bank_head', D(0)); save(D(0), 'bank_link')
    c.move(I(65536), D(7))
    L('edit_bank_link')
    map_pointer('bank_link')
    get('bank_link', A(0)); c.move(M(0), D(0))
    c.alu('cmp', M(2, F['old_node']), 0); B(7, 'edit_registry')
    save(D(0), 'bank_link')
    c.quick(1, D(7), sub=True); B(6, 'edit_bank_link')
    B(0, 'edit_cleanup')

    L('edit_registry')
    c.lea(0, 'registry_state'); save(A(0), 'reg_root')
    c.move(M(0), D(0)); c.tst(D(0)); B(7, 'edit_registry_unbound')
    c.move(A(5), D(1)); c.alu('cmp', D(1), 0); B(6, 'edit_cleanup')
    c.tst(M(0, 4)); B(7, 'edit_cleanup')
    B(0, 'edit_registry_start')
    L('edit_registry_unbound')
    c.tst(M(0, 4)); B(6, 'edit_cleanup')
    L('edit_registry_start')
    lea(0, 0, 4); save(A(0), 'reg_link')
    c.move(I(256), D(7))
    L('edit_registry_link')
    get('reg_link', A(0)); c.move(M(0), D(0)); save(D(0), 'old_cache')
    B(7, 'edit_objects')
    map_pointer('old_cache', 31)
    get('old_cache', A(0)); get('bank', D(0))
    c.alu('cmp', M(0, 4), 0); B(7, 'edit_objects')
    save(A(0), 'reg_link')
    c.quick(1, D(7), sub=True); B(6, 'edit_registry_link')
    B(0, 'edit_cleanup')

    L('edit_objects')
    get('state', A(0)); adda(0, ROOT); save(A(0), 'object_owner')
    map_pointer('object_owner')
    get('object_owner', A(0)); c.move(M(0), D(0))
    B(7, 'edit_object_addresses')
    c.move(A(5), D(1)); c.alu('cmp', D(1), 0); B(6, 'edit_cleanup')
    L('edit_object_addresses')
    for field, displacement, size in (('objects', OBJECT, 64*24), ('stamps', STAMP, 64*STAMP_BYTES)):
        get('state', A(0)); adda(0, displacement); save(A(0), field)
        map_pointer(field, size-1)

    # Validate every reference to this bank before touching the visible state.
    get('objects', A(4)); get('stamps', A(6)); c.move(I(64), D(7))
    L('edit_preflight_slot')
    c.move(M(4, 16), D(0)); c.imm('cmp', 1, D(0)); B(2, 'edit_cleanup')
    c.tst(D(0)); B(7, 'edit_preflight_next')
    get('object_owner', A(0)); c.tst(M(0)); B(7, 'edit_cleanup')
    get('bank', D(0)); c.alu('cmp', M(4), 0); B(6, 'edit_preflight_next')
    for field, offset in (('source', 0), ('old_generation', 4), ('bank_head', 8), ('size', 12)):
        get(field, D(0)); c.alu('cmp', M(6, offset), 0); B(6, 'edit_cleanup')
    # A Bob may have been SET to an absent image before its first Update.
    # An edit cannot silently make that invalid binding point at new data.
    get('source', A(0))
    c.move(I(0), D(1)); c.move(M(0, 8), D(1), 'w')
    adda(0, 32)
    c.move(M(4, 4), D(4))
    L('edit_preflight_image')
    c.tst(D(1)); B(7, 'edit_cleanup')
    c.move(I(0), D(0)); c.move(M(0), D(0), 'w')
    c.alu('cmp', D(4), 0); B(7, 'edit_preflight_next')
    B(2, 'edit_cleanup')
    adda(0, 40)
    c.quick(1, D(1), sub=True); B(0, 'edit_preflight_image')
    L('edit_preflight_next')
    adda(4, 24); adda(6, STAMP_BYTES)
    c.quick(1, D(7), sub=True); B(6, 'edit_preflight_slot')

    # All allocations and checks complete. Old Chip release either refuses
    # before freeing or succeeds. No more fallible calls before publication.
    get('old_cache', D(0)); B(7, 'edit_publish')
    c.move(D(0), A(0)); lea(1, 0, 8); get('gfx', A(4))
    B(1, 'checked_release_entry'); c.tst(D(3)); B(7, 'edit_cleanup')
    L('edit_publish')
    get('old_node', A(0)); get('new_node', A(1))
    c.move(M(0), M(1))
    get('bank_link', A(4)); c.move(A(1), M(4))
    c.move(I(0), M(0)); save(A(0), 'detached')
    get('old_cache', A(0)); c.move(A(0), D(0))
    B(7, 'edit_registry_insert')
    get('reg_link', A(1)); c.move(M(0), M(1))
    L('edit_registry_insert')
    get('new_cache', D(0)); B(7, 'edit_registry_owner')
    c.move(D(0), A(0)); get('reg_link', A(1))
    c.move(M(1), M(0)); c.move(A(0), M(1))
    L('edit_registry_owner')
    get('reg_root', A(0))
    c.move(I(0), M(0)); c.tst(M(0, 4)); B(7, 'edit_selection')
    c.move(A(5), M(0))
    L('edit_selection')
    c.lea(0, 'bank_active_state')
    get('bank', D(0)); c.alu('cmp', M(0), 0); B(6, 'edit_update_refs')
    get('source', D(0)); c.alu('cmp', M(0,4), 0); B(6, 'edit_update_refs')
    get('bank_head', D(0)); c.alu('cmp', M(0,8), 0); B(6, 'edit_update_refs')
    get('dest', D(0)); c.move(D(0), M(0,4))
    L('edit_update_refs')
    get('objects', A(4)); get('stamps', A(6)); c.move(I(64), D(7))
    L('edit_commit_slot')
    c.tst(M(4, 16)); B(7, 'edit_commit_next')
    get('bank', D(0)); c.alu('cmp', M(4), 0); B(6, 'edit_commit_next')
    c.move(M(4,4), D(0))
    get('last', D(1)); B(7, 'edit_refresh_stamp')
    c.alu('cmp', M(2,F['first']), 0); B(5, 'edit_refresh_stamp')
    c.alu('cmp', D(1), 0); B(2, 'edit_refresh_stamp')
    c.move(I(0), M(4,16))
    B(0, 'edit_commit_next')
    L('edit_refresh_stamp')
    for field, offset in (('dest', 0), ('generation', 4), ('bank_head', 8), ('capacity', 12)):
        get(field, D(0)); c.move(D(0), M(6,offset))
    L('edit_commit_next')
    adda(4, 24); adda(6, STAMP_BYTES)
    c.quick(1, D(7), sub=True); B(6, 'edit_commit_slot')

    amos('Bnk.Change')
    get('old_cache', D(0)); B(7, 'edit_drop_old_bank')
    c.move(D(0), A(1)); library(-690)
    L('edit_drop_old_bank')
    lea(0, 2, F['detached']); get('old_node', A(1)); amos('Lst.Del')
    c.move(I(1), D(3)); B(0, 'edit_return')

    L('edit_cleanup')
    get('new_cache', D(0)); B(7, 'edit_cleanup_bank')
    c.move(D(0), A(0)); lea(1, 0, 8); get('gfx', A(4))
    B(1, 'checked_release_entry')
    get('new_cache', A(1)); library(-690)
    L('edit_cleanup_bank')
    get('new_node', D(0)); B(7, 'edit_fail')
    lea(0, 2, F['detached']); get('new_node', A(1)); amos('Lst.Del')
    L('edit_fail')
    c.move(I(0), D(3))
    L('edit_return')
    c.word(0x4fef); c.word(FRAME)
    c.raw('4cdf77f774004e75')

    L('edit_validate_bank')
    c.raw('48e7efee')
    c.word(0x4fef); c.word(-VALIDATOR_FRAME)
    c.move(A(7), A(2))
    c.move(D(3), M(2, VALIDATOR['bank']))
    c.move(A(0), M(2, VALIDATOR['bankptr']))
    for name in ('ctx', 'gfx', 'result'):
        c.move(I(0), M(2, VALIDATOR[name]))
    B(0, 'checked_stage_live_bank_valid')
    L('edit_validate_or_stage')
    c.move(A(1), D(3))
    B(6, 'checked_chip_stage')
    c.move(I(1), D(3)); c.raw('4e75')

    L('edit_repack')
    c.b.extend(emit_bank_repack()[0])
    site = labels['checked_stage_copy_call']
    assert old[site:site + 4] == pack('>Hh', 0x6100, labels['checked_chip_stage'] - site - 2)
    c.b[site:site + 4] = pack('>Hh', 0x6100, c.labels['edit_validate_or_stage'] - site - 2)
    limit = labels['checked_stage_min_count']
    assert old[limit:limit+6] == bytes.fromhex('0c8000000001')
    c.b[limit+5] = 0
    return c.out(), c.labels
