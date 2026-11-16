#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0c: PRIVATE MC68020 Chip DMA staging/ownership lifecycle.

SOURCE CODE, not a disassembly; no public AP20 token, no installed .Lib.

Three independent entry points, with the AMOS integer ABI (D3=1/0, D2=0):
  prepare: A0=VALIDATED AGBO contiguous planar pixel/mask data, D0=byte size,
           A1=PRIVATE ZEROED 20-byte context, D1=AMOS payload identity (even),
           D4=AGBO generation, A4=graphics.library base for replacing a stage.
  release: A1=private context, A4=graphics.library base (required if staged).
  lookup:  A1=private context, D0=current AMOS payload identity, D1=generation.

Context: +0 Chip ptr, +4 allocation size, +8 identity, +12 generation,
         +16 'CHIP' ownership cookie. Caller must initialize all to zero.

A public wrapper MUST strictly validate the WHOLE AGBO directory and bank
ownership before passing A0/D0, and must invalidate Bob users on replacement
and before release. It must also check current AMOS bank identity on EVERY
render. No arbitrary in-place Poke mutations are supported. This primitive
only stages validated contiguous pixels; it cannot itself validate AGBO.

AllocVec(MEMF_PUBLIC|MEMF_CHIP), verify first and last addresses using
TypeOfMem(MEMF_CHIP), CopyMem exactly once, WaitBlit before FreeVec.
A rejected stage leaves the old context untouched. No unbounded wait loop.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, I

MAX_STAGE = 0x01000000
MEMF_CHIP = 2
MEMF_PUBLIC = 1
COOKIE = 0x43484950  # 'CHIP'
FRAME = 64
K = ("src size ctx identity generation gfx newptr oldptr oldlen "
     "oldtag srcend newend oldend result").split()
F = {name: n * 4 for n, name in enumerate(K)}
assert len(F) * 4 <= FRAME

# AmigaOS 3.x NDK: Exec AllocVec -684, FreeVec -690, TypeOfMem -534,
# CopyMem -624; graphics.library WaitBlit -228.
L_ALLOCVEC = -684
L_FREEVEC = -690
L_TYPEOFMEM = -534
L_COPYMEM = -624
L_WAITBLIT = -228


def emit_chip_stage() -> tuple[bytes, dict[str, int]]:
    c = Code()
    B, L = c.branch, c.label

    def S(src, name):
        c.move(src, M(2, F[name]))

    def G(name, dst):
        c.move(M(2, F[name]), dst)

    def osbase():
        c.raw('2c780004')   # MOVEA.L (4).W,A6 = ExecBase

    def prologue():
        c.raw('48e7efee')   # Project-validated AMOS saved register subset
        c.raw('4fefffc0')   # LEA -64(SP),SP
        c.move(A(7), A(2))
        S(I(0), 'result')

    def epilogue():
        G('result', D(3))
        c.raw('4fef0040')   # LEA 64(SP),SP
        c.raw('4cdf77f7')   # Restore registers, keep D3 result
        c.raw('74004e75')   # MOVEQ #0,D2; RTS

    def cpu_guard(fail):
        # All instructions before this test are legal on 68000.
        c.raw('20780004')   # MOVEA.L (4).W,A0
        c.move(A(0), D(0))
        c.tst(D(0)); B(7, fail)
        c.move(M(0, 0x128), D(0), 'w')  # ExecBase.AttnFlags
        c.word(0x0800); c.word(1)      # BTST #AFF_68020,D0
        B(7, fail)

    def nonzero_even(name, fail):
        G(name, D(0))
        c.tst(D(0)); B(7, fail)
        c.imm('and', 1, D(0))
        B(6, fail)

    def size_check(name, fail):
        G(name, D(0))
        c.tst(D(0)); B(7, fail)
        c.imm('cmp', MAX_STAGE, D(0))
        B(2, fail)     # unsigned higher than 16 MiB
        c.imm('and', 1, D(0))
        B(6, fail)

    def range_end(ptr, size, dest, fail):
        # End is inclusive; detect wrap before the subtraction.
        G(ptr, D(0))
        G(size, D(1))
        c.alu('add', D(1), 0)
        B(5, fail)     # BCS overflow
        c.quick(1, D(0), sub=True)
        S(D(0), dest)

    def typeof_nonzero(name, fail):
        G(name, A(1))
        osbase(); c.call_os(L_TYPEOFMEM)
        c.tst(D(0)); B(7, fail)

    def typeof_chip(name, fail):
        G(name, A(1))
        osbase(); c.call_os(L_TYPEOFMEM)
        c.imm('and', MEMF_CHIP, D(0))
        c.imm('cmp', MEMF_CHIP, D(0))
        B(6, fail)

    # PREPARE: do not publish new ptr until ALL checks and copy succeeded.
    L('stage_entry')
    prologue()
    S(A(0), 'src')
    S(D(0), 'size')
    S(A(1), 'ctx')
    S(D(1), 'identity')
    S(D(4), 'generation')
    S(A(4), 'gfx')
    S(I(0), 'newptr')
    cpu_guard('stage_fail')
    nonzero_even('src', 'stage_fail')
    nonzero_even('ctx', 'stage_fail')
    nonzero_even('identity', 'stage_fail')
    size_check('size', 'stage_fail')
    G('generation', D(0))
    c.tst(D(0)); B(7, 'stage_fail')
    # A prevalidated AMOS DATA bank owns this contiguous source region.
    range_end('src', 'size', 'srcend', 'stage_fail')
    typeof_nonzero('src', 'stage_fail')
    typeof_nonzero('srcend', 'stage_fail')
    G('ctx', A(0))
    c.move(M(0), D(0)); S(D(0), 'oldptr')
    c.move(M(0, 4), D(0)); S(D(0), 'oldlen')
    c.move(M(0, 16), D(0)); S(D(0), 'oldtag')
    G('oldptr', D(0))
    c.tst(D(0))
    B(6, 'stage_has_old')
    # All-zero context is the sole uninitialized state.
    for off in (4, 8, 12, 16):
        G('ctx', A(0))
        c.tst(M(0, off))
        B(6, 'stage_fail')
    B(0, 'stage_allocate')
    L('stage_has_old')
    nonzero_even('oldptr', 'stage_fail')
    size_check('oldlen', 'stage_fail')
    G('oldtag', D(0))
    c.imm('cmp', COOKIE, D(0))
    B(6, 'stage_fail')
    G('gfx', D(0)); c.tst(D(0))
    B(7, 'stage_fail')  # replacement needs a real graphics base
    range_end('oldptr', 'oldlen', 'oldend', 'stage_fail')
    typeof_chip('oldptr', 'stage_fail')
    typeof_chip('oldend', 'stage_fail')
    L('stage_allocate')
    G('size', D(0))
    c.move(I(MEMF_CHIP | MEMF_PUBLIC), D(1))
    osbase(); c.call_os(L_ALLOCVEC)
    c.tst(D(0)); B(7, 'stage_fail')
    S(D(0), 'newptr')
    nonzero_even('newptr', 'stage_cleanup')
    range_end('newptr', 'size', 'newend', 'stage_cleanup')
    # AllocVec's MEMF_CHIP is a whole-block guarantee. Check both edges too.
    typeof_chip('newptr', 'stage_cleanup')
    typeof_chip('newend', 'stage_cleanup')
    G('src', A(0))
    G('newptr', A(1))
    G('size', D(0))
    osbase(); c.call_os(L_COPYMEM)  # synchronous, exact byte count
    G('oldptr', D(0))
    c.tst(D(0)); B(7, 'stage_commit')
    # The old source remains allocated until the Blitter is done reading it.
    G('gfx', A(6))
    c.call_os(L_WAITBLIT)
    L('stage_commit')
    G('ctx', A(0))
    G('newptr', D(0)); c.move(D(0), M(0, 0))
    G('size', D(0)); c.move(D(0), M(0, 4))
    G('identity', D(0)); c.move(D(0), M(0, 8))
    G('generation', D(0)); c.move(D(0), M(0, 12))
    c.move(I(COOKIE), M(0, 16))
    G('oldptr', D(0))
    c.tst(D(0)); B(7, 'stage_ok')
    G('oldptr', A(1))
    osbase(); c.call_os(L_FREEVEC)
    L('stage_ok')
    S(I(1), 'result')
    B(0, 'stage_return')
    L('stage_cleanup')
    G('newptr', A(1))
    osbase(); c.call_os(L_FREEVEC)
    L('stage_fail')
    L('stage_return')
    epilogue()

    # RELEASE: refuse any ambiguous owner; never free an unchecked pointer.
    L('release_entry')
    prologue()
    S(A(1), 'ctx')
    S(A(4), 'gfx')
    cpu_guard('release_return')
    nonzero_even('ctx', 'release_return')
    G('ctx', A(0))
    c.move(M(0), D(0)); S(D(0), 'oldptr')
    c.move(M(0, 4), D(0)); S(D(0), 'oldlen')
    G('oldptr', D(0))
    c.tst(D(0)); B(6, 'release_has_old')
    for off in (4, 8, 12, 16):
        G('ctx', A(0)); c.tst(M(0, off))
        B(6, 'release_return')
    S(I(1), 'result')
    B(0, 'release_return')
    L('release_has_old')
    nonzero_even('oldptr', 'release_return')
    size_check('oldlen', 'release_return')
    G('ctx', A(0))
    c.move(M(0, 16), D(0))
    c.imm('cmp', COOKIE, D(0))
    B(6, 'release_return')
    G('gfx', D(0)); c.tst(D(0))
    B(7, 'release_return')
    range_end('oldptr', 'oldlen', 'oldend', 'release_return')
    typeof_chip('oldptr', 'release_return')
    typeof_chip('oldend', 'release_return')
    G('gfx', A(6))
    c.call_os(L_WAITBLIT)
    G('oldptr', A(1))
    osbase(); c.call_os(L_FREEVEC)
    G('ctx', A(0))
    for off in (0, 4, 8, 12, 16):
        c.move(I(0), M(0, off))
    S(I(1), 'result')
    L('release_return')
    epilogue()

    # LOOKUP: only the owner may use the pointer, after checking current bank
    # payload identity+generation. This intentionally DOES NOT dereference it.
    L('lookup_entry')
    prologue()
    S(A(1), 'ctx')
    S(D(0), 'identity')
    S(D(1), 'generation')
    cpu_guard('lookup_return')
    nonzero_even('ctx', 'lookup_return')
    nonzero_even('identity', 'lookup_return')
    G('generation', D(0))
    c.tst(D(0)); B(7, 'lookup_return')
    G('ctx', A(0))
    c.move(M(0, 16), D(0))
    c.imm('cmp', COOKIE, D(0)); B(6, 'lookup_return')
    c.move(M(0, 0), D(0))
    c.tst(D(0)); B(7, 'lookup_return')
    c.move(M(0, 8), D(0))
    G('identity', D(1)); c.alu('cmp', D(1), 0)
    B(6, 'lookup_return')
    c.move(M(0, 12), D(0))
    G('generation', D(1)); c.alu('cmp', D(1), 0)
    B(6, 'lookup_return')
    S(I(1), 'result')
    L('lookup_return')
    epilogue()

    raw = c.out()
    assert len(raw) % 2 == 0
    assert len(raw) < 32766
    assert c.labels['stage_entry'] == 0
    assert c.labels['stage_entry'] < c.labels['release_entry'] < c.labels['lookup_entry']
    return raw, c.labels


if __name__ == '__main__':
    from hashlib import sha256
    code, entries = emit_chip_stage()
    print('M19 P0c PRIVATE MC68020 CHIP staging SOURCE ONLY',
          len(code), sha256(code).hexdigest(),
          {k: entries[k] for k in ('stage_entry', 'release_entry', 'lookup_entry')},
          'no AP20/WinUAE/Compiler claim')
