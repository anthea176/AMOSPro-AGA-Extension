#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0j-b7: preserve P0j-b6 Draw/Swap and guard AMOS End lifecycle.

The actual P0c End bridge frees BOBS Chip before calling the unchanged
AGA End callback; native AGA Close/End drain Safe/Disp cooperatively and
refuse destruction after the bounded wait when a reply stays pending.

B6 has a lifecycle gap: successful native End does not reset B5 DIRTY.
B7 adds two PRIVATE BOBS-only entrypoints, no change to original AGA:
 - b7_guarded_draw_entry: existing B5 Draw; install the checked owner-
   local End callback after return, or fail closed with DIRTY on conflict
 - b7_end_entry: chain the ORIGINAL P0c End bridge, clear guard only if
   real Screen becomes zero; on pending timeout, retain End callback for
   one later attempt and never clear the guard.

SOURCE ONLY, not installed. CPU MC68020+; original callbacks are checked
against the source-pinned relocated AGA End signature. No fake AGA Lib.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I
from m19_p0j_swap_barrier_emit import emit_swap_barrier, G, DIRTY, GUARD_BYTES
from m19_p0c_program_end_bridge_emit import END_SIGNATURE

STATE_A5 = 0x1c8
END1_A5 = 0x1cc
END2_A5 = 0x1d0
OLD_END_DELTA = 0x168
LOCAL_FRAME = 32
F = dict(result=0,state=4,old_end=8,callbacks=12)


def emit_end_lifecycle() -> tuple[bytes, dict[str, int]]:
    old, labels = emit_swap_barrier()
    c = Code()
    c.raw(old.hex())
    c.labels.update(labels)
    B,L = c.branch,c.label

    def save(reg,name):
        c.move(reg,M(2,F[name]))

    def load(name,reg):
        c.move(M(2,F[name]),reg)

    def mapped(ptr, reject):
        c.move(ptr,A(1))
        c.raw('2c780004')  # MOVEA.L 4.W,A6 (ExecBase)
        c.call_os(-534)    # Exec TypeOfMem
        c.tst(D(0)); B(7,reject)

    L('b7_guarded_draw_entry')
    c.raw('48e7efee')  # all AMOS D0,D1,D4-D7,A0-A2,A4-A6; D3/D2 are result
    c.raw('4fefffe0')  # LEA -32(SP),SP
    c.move(A(7),A(2))
    B(1,'guarded_frame_draw_entry')
    save(D(3),'result')

    # On any result (including preflight failure), End must clear B5's
    # frame guard when the AGA screen genuinely closes. Check BEFORE arming.
    B(1,'registry_cpu_guard')
    c.tst(D(0)); B(7,'b7_draw_fail')
    c.move(A(5),D(0));c.tst(D(0)); B(7,'b7_draw_fail')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'b7_draw_fail')
    mapped(A(5),'b7_draw_fail')
    c.move(M(5,STATE_A5),D(0))
    c.tst(D(0));B(7,'b7_draw_fail')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'b7_draw_fail')
    save(D(0),'state')
    mapped(D(0),'b7_draw_fail')
    load('state',A(0))
    c.tst(M(0,0)); B(7,'b7_draw_fail') # screen is no longer open

    # Native AGA End is exactly State - $168 in the immutable AGA island.
    load('state',D(0))
    c.imm('cmp',OLD_END_DELTA,D(0)); B(5,'b7_draw_fail')
    c.imm('sub',OLD_END_DELTA,D(0))
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'b7_draw_fail')
    save(D(0),'old_end')
    mapped(D(0),'b7_draw_fail')
    load('old_end',D(0))
    c.imm('add',11,D(0));B(5,'b7_draw_fail')
    mapped(D(0),'b7_draw_fail')
    load('old_end',A(4))
    for offset,word in enumerate(END_SIGNATURE):
        c.move(M(4,4*offset),D(0))
        c.imm('cmp',word,D(0));B(6,'b7_draw_fail')

    # Do not replace a third-party End callback or half-patched pair.
    c.move(M(5,END1_A5),D(0))
    c.move(M(5,END2_A5),D(1))
    c.alu('cmp',D(1),0);B(6,'b7_draw_fail')
    save(D(0),'callbacks')
    load('callbacks',D(0))
    load('old_end',D(1))
    c.alu('cmp',D(1),0);B(7,'b7_draw_arm')
    load('callbacks',D(0))
    c.lea(1,'program_end_bridge_entry')
    c.move(A(1),D(1));c.alu('cmp',D(1),0);B(7,'b7_draw_arm')
    load('callbacks',D(0))
    c.lea(1,'b7_end_entry')
    c.move(A(1),D(1));c.alu('cmp',D(1),0);B(6,'b7_draw_fail')
    L('b7_draw_arm')
    c.lea(0,'b7_end_entry')
    c.move(A(0),M(5,END1_A5))
    c.move(A(0),M(5,END2_A5))
    B(0,'b7_draw_return')

    # If callback installation fails AFTER painting, invalidate the back
    # even when B5 itself succeeded. The Swap guard will refuse exposure.
    L('b7_draw_fail')
    c.lea(0,'frame_guard_state')
    c.move(I(DIRTY),M(0,G['status']))
    save(I(0),'result')
    L('b7_draw_return')
    load('result',D(3))
    c.raw('4fef0020')  # restore local frame
    c.raw('4cdf77f7')  # restore preserved AMOS registers, not D2/D3
    c.raw('74004e75')  # numeric result D2=0; RTS

    L('b7_end_entry')
    c.raw('48e7fffe')  # actual AMOS End is a callback: preserve D0-D7/A0-A6
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'b7_end_return')
    c.move(A(5),D(0));c.tst(D(0));B(7,'b7_end_return')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'b7_end_return')
    mapped(A(5),'b7_end_return')
    c.move(M(5,STATE_A5),D(0));c.tst(D(0));B(7,'b7_end_return')
    c.move(D(0),D(1));c.imm('and',1,D(1));B(6,'b7_end_return')
    mapped(D(0),'b7_end_return')

    # Ensure *both* live AMOS callbacks still point at this exact BOBS
    # End hook. P0c expects its own pointer, so install it just for call.
    c.lea(0,'b7_end_entry')
    c.move(A(0),D(1))
    c.move(M(5,END1_A5),D(0))
    c.alu('cmp',D(1),0);B(6,'b7_end_return')
    c.move(M(5,END2_A5),D(0))
    c.alu('cmp',D(1),0);B(6,'b7_end_return')

    c.lea(0,'program_end_bridge_entry')
    c.move(A(0),M(5,END1_A5))
    c.move(A(0),M(5,END2_A5))
    B(1,'program_end_bridge_entry')  # checked P0c -> original native AGA End

    # AGA static State remains mapped across Close; inspect actual Screen.
    c.move(M(5,STATE_A5),D(0))
    c.tst(D(0));B(7,'b7_end_return')
    mapped(D(0),'b7_end_return')
    c.move(M(5,STATE_A5),A(0))
    c.tst(M(0,0));B(6,'b7_end_pending')

    # True successful End: clear owner-bound frame latch. NEVER reset
    # DIRTY on a timeout or while ScreenBuffer is still live.
    c.lea(0,'frame_guard_state')
    c.move(M(0,G['owner']),D(0))
    c.move(A(5),D(1))
    c.alu('cmp',D(1),0);B(6,'b7_end_return')
    for offset in range(0,GUARD_BYTES,4):
        c.move(I(0),M(0,offset))
    B(0,'b7_end_return')

    # Original native End may abort cooperatively when Safe/Disp is still
    # pending. It restores original callbacks on entry; reinstall our
    # hook for a future attempt, without FreeScreenBuffer/DeletePort.
    L('b7_end_pending')
    c.lea(0,'b7_end_entry')
    c.move(A(0),M(5,END1_A5))
    c.move(A(0),M(5,END2_A5))
    L('b7_end_return')
    c.raw('4cdf7fff4e75')

    native=c.out()
    assert native.startswith(old)
    assert c.labels['b7_guarded_draw_entry']==len(old)
    assert c.labels['b7_end_entry']>len(old)
    assert len(native)%2==0 and len(native)<32766
    return native,c.labels



def emit_end_lifecycle_multiframe() -> tuple[bytes, dict[str, int]]:
    """Append a checked P0c/B7 callback handoff, keeping installed B7 byte-exact.

    A B7 End hook is swapped to the original P0c hook only during Draw.
    The historical B7 Draw then validates and reinstalls B7 on return,
    including when its inner Draw has failed. No foreign hook is changed.
    """
    original, labels = emit_end_lifecycle()
    c = Code()
    c.raw(original.hex())
    c.labels.update(labels)
    B, L = c.branch, c.label

    def mapped(ptr, reject):
        c.move(ptr, A(1))
        c.raw('2c780004')  # MOVEA.L 4.W,A6: ExecBase
        c.call_os(-534)    # TypeOfMem(pointer)
        c.tst(D(0)); B(7, reject)

    L('b7_multiframe_draw_entry')
    c.raw('48e7efee')      # AMOS preserved set; D2/D3 are the integer result
    B(1, 'registry_cpu_guard')
    c.tst(D(0)); B(7, 'b7_multiframe_refuse')
    c.move(A(5), D(0))
    c.tst(D(0)); B(7, 'b7_multiframe_refuse')
    c.imm('and', 1, D(0)); B(6, 'b7_multiframe_refuse')
    mapped(A(5), 'b7_multiframe_refuse')
    c.move(M(5, STATE_A5), D(0))
    c.tst(D(0)); B(7, 'b7_multiframe_refuse')
    c.move(D(0), D(1)); c.imm('and', 1, D(1))
    B(6, 'b7_multiframe_refuse')
    mapped(D(0), 'b7_multiframe_refuse')
    c.move(M(5, STATE_A5), A(0))
    c.tst(M(0, 0)); B(7, 'b7_multiframe_refuse')  # closed screen

    # Check the actual relocated native AGA End before authorizing a swap.
    c.move(M(5, STATE_A5), D(0))
    c.imm('cmp', OLD_END_DELTA, D(0)); B(5, 'b7_multiframe_refuse')
    c.imm('sub', OLD_END_DELTA, D(0))
    c.move(D(0), D(1)); c.imm('and', 1, D(1))
    B(6, 'b7_multiframe_refuse')
    c.move(D(0), A(4))
    mapped(A(4), 'b7_multiframe_refuse')
    c.move(A(4), D(0))
    c.imm('add', 11, D(0)); B(5, 'b7_multiframe_refuse')
    mapped(D(0), 'b7_multiframe_refuse')
    for offset, word in enumerate(END_SIGNATURE):
        c.move(M(4, 4 * offset), D(0))
        c.imm('cmp', word, D(0)); B(6, 'b7_multiframe_refuse')

    # Both callback slots must agree and belong to native AGA, P0c or B7.
    c.move(M(5, END1_A5), D(0))
    c.move(M(5, END2_A5), D(1))
    c.alu('cmp', D(1), 0); B(6, 'b7_multiframe_refuse')
    c.move(A(4), D(1))
    c.alu('cmp', D(1), 0); B(7, 'b7_multiframe_forward')
    c.lea(1, 'program_end_bridge_entry')
    c.move(A(1), D(1))
    c.alu('cmp', D(1), 0); B(7, 'b7_multiframe_forward')
    c.lea(1, 'b7_end_entry')
    c.move(A(1), D(1))
    c.alu('cmp', D(1), 0); B(6, 'b7_multiframe_refuse')

    # Second and later frames: allow P0c to rearm its own callback.
    c.lea(0, 'program_end_bridge_entry')
    c.move(A(0), M(5, END1_A5))
    c.move(A(0), M(5, END2_A5))
    L('b7_multiframe_forward')
    c.raw('4cdf77f7')      # restore preserved AMOS regs
    B(0, 'b7_guarded_draw_entry')  # tail call, B7 restores its End hook

    L('b7_multiframe_refuse')
    c.lea(0, 'frame_guard_state')
    c.move(I(DIRTY), M(0, G['status']))
    c.move(I(0), D(3))
    c.raw('4cdf77f7')
    c.raw('74004e75')      # numeric failure D2=0/D3=0; RTS

    native = c.out()
    assert native.startswith(original)
    assert c.labels['b7_multiframe_draw_entry'] == len(original)
    assert len(native) % 2 == 0 and len(native) < 32766
    return native, c.labels

if __name__=='__main__':
    from hashlib import sha256
    native,labels=emit_end_lifecycle()
    print('M19 P0j-b7 End lifecycle source-only',
          len(native),sha256(native).hexdigest(),
          labels['b7_guarded_draw_entry'],
          labels['b7_end_entry'],
          'uninstalled; real WinUAE/Compiler NOT TESTED')
