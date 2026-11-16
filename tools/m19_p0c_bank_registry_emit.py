#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0c PRIVATE MC68020 per-bank Chip-context registry, source-only.

Extends the source-verified checked AGBO->Chip emitter without changing any of
its bytes or public AP20 entries. One private registry per native BOBS unit,
scoped to the current AMOS A5 program identity. Nodes (28 bytes) are Exec
AllocVec(MEMF_PUBLIC|MEMF_CLEAR), never AMOS banks: next(+0), bank(+4),
Chip context(+8..+27). The Chip allocations belong to the existing P0c helper.

PRIVATE ENTRYPOINTS (D2=0, D3=1 success or 0 refusal, all other AMOS regs saved):
  registry_prepare: D3=selected bank, A5=AMOS, A4=valid GfxBase
  registry_lookup:  D3=selected bank, A5=AMOS (returns status only)
  registry_free:    D3=bank, A5=AMOS, A4=valid GfxBase if active
  registry_close:   A5=AMOS, A4=valid GfxBase if active

Prepare publishes a new node only AFTER a validated Chip allocation succeeds.
Replacements keep the old stage if validation or allocation fails. Removal
waits for Blitter completion through checked_release, and only then unlinks
and frees the metadata node. Close is idempotent and handles multiple banks.
All walks are bounded to 256 nodes; no leak on a failed new prepare.

NO Screen Close hook exists yet. registry_close is a callable PRIVATE teardown
entry for the later validated close integration, NOT an installed AMOS command.
The real screen/graphics lifetime and program shutdown are not inferred here.
A5 prevents cross-program reuse. ABA address reuse and in-place Poke remain
unsupported until a stronger owner generation/selection lifecycle exists.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I
from m19_p0c_checked_bank_stage_emit import emit_checked_bank_stage

FRAME=96
NODE_SIZE=28
MAX_NODES=256
META_FLAGS=0x00010001  # MEMF_PUBLIC | MEMF_CLEAR
K=('bank owner gfx root prevlink node newnode result count bad').split()
F={name:4*i for i,name in enumerate(K)}
assert 4*len(K)<=FRAME


def emit_bank_registry() -> tuple[bytes,dict[str,int]]:
    previous, previous_labels = emit_checked_bank_stage()
    c=Code()
    c.raw(previous.hex())
    c.labels.update(previous_labels)
    B,L=c.branch,c.label

    def S(src,key):c.move(src,M(2,F[key]))
    def G(key,dst):c.move(M(2,F[key]),dst)
    def osbase():c.raw('2c780004')  # MOVEA.L (4).W,A6

    def prologue(*,need_bank=True):
        c.raw('48e7efee')             # MOVEM.L preserved AMOS registers
        c.raw('4fefffa0')             # LEA -96(SP),SP
        c.move(A(7),A(2))
        S(D(3),'bank')
        S(A(5),'owner')
        S(A(4),'gfx')
        S(I(0),'result')
        S(I(0),'newnode')
        c.lea(0,'registry_state')
        S(A(0),'root')
        B(1,'registry_cpu_guard')
        c.tst(D(0)); B(7,'registry_return')
        G('owner',D(0))
        c.tst(D(0)); B(7,'registry_return')
        B(1,'registry_owner_guard')
        c.tst(D(0)); B(7,'registry_return')
        if need_bank:
            G('bank',D(0))
            c.imm('cmp',5,D(0));B(5,'registry_return')
            c.imm('cmp',65535,D(0));B(2,'registry_return')

    def epilogue():
        L('registry_return')
        G('result',D(3))
        c.raw('4fef0060')   # frame +96
        c.raw('4cdf77f7')   # restore AMOS caller
        c.raw('74004e75')   # D2=0, RTS

    def find():
        B(1,'registry_find')
        G('bad',D(0))
        c.tst(D(0));B(6,'registry_return')

    def node_context():
        G('node',D(0))
        c.imm('add',8,D(0))
        c.move(D(0),A(1))

    def call_release():
        node_context()
        G('gfx',A(4))
        B(1,'checked_release_entry')
        c.tst(D(3))
        B(7,'registry_return')

    def unlink_and_free():
        B(1,'registry_unlink_and_free')

    # Prepare selected bank, using allocated or existing per-bank context.
    L('registry_prepare_entry')
    prologue()
    find()
    G('node',D(0));c.tst(D(0))
    B(6,'registry_prepare_checked')
    # On a newly seen bank, allocate zero-initialized metadata DETACHED.
    c.move(I(NODE_SIZE),D(0))
    c.move(I(META_FLAGS),D(1))
    osbase();c.call_os(-684)   # AllocVec
    c.tst(D(0));B(7,'registry_return')
    S(D(0),'newnode')
    c.move(D(0),D(1))
    c.imm('and',1,D(1))
    B(6,'registry_prepare_free_new')
    c.move(D(0),A(0))
    G('bank',D(1))
    c.move(D(1),M(0,4))
    S(D(0),'node')
    L('registry_prepare_checked')
    node_context()
    G('bank',D(3))
    G('gfx',A(4))
    B(1,'checked_stage_entry')
    c.tst(D(3));B(7,'registry_prepare_free_new')
    G('newnode',D(0));c.tst(D(0))
    B(7,'registry_prepare_success')
    # Atomic metadata publication after successful Chip staging.
    G('root',A(0))
    c.move(M(0,4),D(1))
    G('newnode',A(0))
    c.move(D(1),M(0))
    G('root',A(0))
    G('newnode',D(0))
    c.move(D(0),M(0,4))
    G('owner',D(0))
    c.move(D(0),M(0,0))
    L('registry_prepare_success')
    S(I(1),'result')
    B(0,'registry_return')
    L('registry_prepare_free_new')
    G('newnode',D(0));c.tst(D(0))
    B(7,'registry_return')
    G('newnode',A(1))
    osbase();c.call_os(-690)
    B(0,'registry_return')

    # Resolve only a stage whose CURRENT selected AGBO bank still matches.
    L('registry_lookup_entry')
    prologue()
    find()
    G('node',D(0));c.tst(D(0));B(7,'registry_return')
    node_context()
    G('bank',D(3))
    B(1,'checked_lookup_entry')
    c.tst(D(3));B(7,'registry_return')
    S(I(1),'result')
    B(0,'registry_return')

    # Explicit bank disable; unlink only after the entire Chip buffer is freed.
    L('registry_free_entry')
    prologue()
    find()
    G('node',D(0))
    c.tst(D(0));B(7,'registry_free_no_node')
    call_release()
    unlink_and_free()
    L('registry_free_no_node')
    S(I(1),'result')
    B(0,'registry_return')

    # PRIVATE lifecycle hook for future Screen Close: iteratively release
    # all bank resources, still owned by current program A5.
    L('registry_close_entry')
    prologue(need_bank=False)
    S(I(MAX_NODES),'count')
    L('registry_close_next')
    G('root',A(0))
    c.move(M(0,4),D(0))
    S(D(0),'node')
    c.tst(D(0));B(7,'registry_close_finished')
    G('count',D(0))
    c.tst(D(0));B(7,'registry_return')
    c.quick(1,D(0),sub=True)
    S(D(0),'count')
    # Head is always the predecessor link for close cleanup.
    G('root',D(0))
    c.imm('add',4,D(0))
    c.move(D(0),A(0))
    S(A(0),'prevlink')
    call_release()
    unlink_and_free()
    B(0,'registry_close_next')
    L('registry_close_finished')
    G('root',A(0))
    c.move(I(0),M(0,0))  # clear owner on idempotent empty close
    S(I(1),'result')
    B(0,'registry_return')

    # Shared bounded linked-list search; stores node and predecessor slot.
    L('registry_find')
    G('root',D(0))
    c.imm('add',4,D(0))
    c.move(D(0),A(0))
    S(A(0),'prevlink')
    S(I(0),'bad')
    S(I(MAX_NODES),'count')
    L('registry_find_next')
    G('prevlink',A(0))
    c.move(M(0),D(0))
    S(D(0),'node')
    c.tst(D(0));B(7,'registry_find_exit')
    G('count',D(1))
    c.tst(D(1));B(7,'registry_find_broken')
    c.quick(1,D(1),sub=True)
    S(D(1),'count')
    c.move(D(0),A(0))
    c.move(M(0,4),D(1))
    G('bank',D(0))
    c.alu('cmp',D(1),0)
    B(7,'registry_find_exit')
    G('node',A(0))
    S(A(0),'prevlink')
    B(0,'registry_find_next')
    L('registry_find_broken')
    S(I(1),'bad')
    L('registry_find_exit')
    c.raw('4e75')

    L('registry_unlink_and_free')
    # Called only once checked_release has returned success.
    G('node',A(0))
    c.move(M(0),D(1))     # next
    G('prevlink',A(0))
    c.move(D(1),M(0))     # unlink in ONE longword write
    G('node',A(1))
    osbase();c.call_os(-690)   # FreeVec metadata, no size parameter
    G('root',A(0))
    c.tst(M(0,4))
    B(6,'registry_keep_owner')
    c.move(I(0),M(0,0))
    L('registry_keep_owner')
    c.raw('4e75')   # RTS


    # Per-code-unit owner protection, preventing reuse of Chip resources
    # across different AMOS program contexts. D0=1/0.
    L('registry_owner_guard')
    G('root',A(0))
    c.move(M(0,0),D(0))
    c.tst(D(0));B(7,'registry_owner_unbound')
    G('owner',D(1))
    c.alu('cmp',D(1),0)
    B(7,'registry_owner_allowed')
    c.move(I(0),D(0))
    c.raw('4e75')
    L('registry_owner_unbound')
    c.tst(M(0,4))
    B(6,'registry_owner_denied')
    L('registry_owner_allowed')
    c.move(I(1),D(0))
    c.raw('4e75')
    L('registry_owner_denied')
    c.move(I(0),D(0))
    c.raw('4e75')

    L('registry_cpu_guard')
    c.raw('20780004')      # MOVEA.L 4.W,A0
    c.move(A(0),D(0))
    c.tst(D(0));B(7,'registry_cpu_absent')
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800);c.word(1)  # BTST #AFF_68020
    B(7,'registry_cpu_absent')
    c.move(I(1),D(0))
    c.raw('4e75')
    L('registry_cpu_absent')
    c.move(I(0),D(0))
    c.raw('4e75')

    epilogue()
    # Must never treat the persistent owner data as executable bytes.
    L('registry_state')
    c.raw('0000000000000000')

    raw=c.out()
    assert raw[:len(previous)]==previous, 'no change allowed in P0b/P0c prefix'
    assert raw[c.labels['registry_state']:]==bytes(8)
    assert len(raw)<32766 and len(raw)%2==0
    assert all(c.labels[k]>len(previous)-1 for k in (
        'registry_prepare_entry','registry_lookup_entry',
        'registry_free_entry','registry_close_entry','registry_state'))
    return raw,c.labels


if __name__=='__main__':
    from hashlib import sha256
    code,labels=emit_bank_registry()
    print('M19 P0c PRIVATE MC68020 bank-registry SOURCE ONLY',
          len(code),sha256(code).hexdigest(),'registry bytes',
          len(code)-labels['registry_prepare_entry'],
          'no AP20/export/installed Lib/WinUAE/Compiler claim')
