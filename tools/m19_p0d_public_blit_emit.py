#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0d EXPERIMENT: first PUBLIC Bob Blit(I,X,Y) CPU020 entry SOURCE ONLY.

The public function is intentionally a one-shot draw, NOT the future
persistent object command Aga Bob N,X,Y,I from the accepted design.

AMOS 365 numeric ABI: D3=Y; (A3)+=X, then I; function result D3=1/0,
D2=0; A3 advances by exactly eight bytes even on failure.
Requires an already selected AGBO bank (public Aga Bob Bank N) and a live
AGA Screen + Double Buffer state. The bank may initially be empty when
selected; after Get AGA Bob / Make AGA Bob Mask / Load, the first Blit
stages the FULL verified bank into owned Chip. Reuse staging while its
AMOS payload and generation remain current; recapture will restage once.
Do not force a Chip allocation at Aga Bob Bank N if no image exists.

Private P0c program_end_arm_entry MUST succeed before drawing or newly
staged Chip must be released. No back-buffer DMA when the End callback
is not secured. Actual drawing uses safe_bank_blit_entry and WaitBlit.
No Aga Swap, no target-bank destruction, no revalidation by Poke allowed.
No installed .Lib / WinUAE / real AMOS Compiler claim.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, POST, I
from m19_p0d_safe_bank_blit_emit import emit_safe_bank_blit

FRAME = 96
STATE_A5 = 0x1c8
F = {name:4*i for i,name in enumerate(
    ('image x y bank state gfx result').split())}
assert max(F.values())+4 <= FRAME


def emit_public_blit() -> tuple[bytes, dict[str,int]]:
    prefix, labels = emit_safe_bank_blit()
    c = Code()
    c.raw(prefix.hex())
    c.labels.update(labels)
    B,L = c.branch,c.label

    def S(src,name):
        c.move(src,M(2,F[name]))

    def G(name,dst):
        c.move(M(2,F[name]),dst)

    L('public_bob_blit_entry')
    c.raw('48e7efee')              # saved AMOS D0/D1/D4-D7/A0-A2/A4-A6
    c.raw('4fefffa0')              # LEA -96(SP),SP
    c.move(A(7),A(2))
    S(D(3),'y')
    c.move(POST(3),D(0)); S(D(0),'x')
    c.move(POST(3),D(0)); S(D(0),'image')
    S(I(0),'result')

    # Refuse <68020 before any AMOS/AGA bank access.
    B(1,'registry_cpu_guard')
    c.tst(D(0)); B(7,'public_blit_return')
    c.move(A(5),D(0))
    c.tst(D(0)); B(7,'public_blit_return')
    c.imm('and',1,D(0)); B(6,'public_blit_return')

    G('image',D(0))
    c.imm('cmp',1,D(0)); B(5,'public_blit_return')
    c.imm('cmp',4096,D(0)); B(2,'public_blit_return')
    for name in ('x','y'):
        G(name,D(0))
        c.imm('cmp',-32768,D(0)); B(13,'public_blit_return')
        c.imm('cmp',32767,D(0)); B(14,'public_blit_return')

    # Use exactly the selection published by the verified P0a bank-select
    # source, not a guessed current AMOS bank number.
    c.lea(0,'bank_active_state')
    c.move(M(0,0),D(0))
    c.imm('cmp',5,D(0)); B(5,'public_blit_return')
    c.imm('cmp',65535,D(0)); B(2,'public_blit_return')
    S(D(0),'bank')

    # P0c's real AGA Init owns the state pointer; obtain valid GfxBase before
    # invoking any Chip replacement (which must WaitBlit before FreeVec).
    c.move(M(5,STATE_A5),D(0)); S(D(0),'state')
    c.tst(D(0)); B(7,'public_blit_return')
    c.imm('and',1,D(0)); B(6,'public_blit_return')
    G('state',A(1))
    c.raw('2c780004'); c.call_os(-534)  # Exec TypeOfMem(state)
    c.tst(D(0)); B(7,'public_blit_return')
    # State+32 holds DBState. Probe both endpoints of the structure before
    # reading GfxBase or DBState, and reject pointer arithmetic overflow.
    G('state',D(0))
    c.imm('add',32,D(0)); B(5,'public_blit_return')
    c.move(D(0),A(1))
    c.raw('2c780004'); c.call_os(-534) # Exec TypeOfMem(state+32)
    c.tst(D(0)); B(7,'public_blit_return')
    G('state',A(0))
    c.move(M(0,32),D(0))
    c.tst(D(0)); B(7,'public_blit_return') # no AGA Double Buffer
    c.imm('and',1,D(0)); B(6,'public_blit_return')
    G('state',A(0))
    c.move(M(0,8),D(0)); S(D(0),'gfx')
    c.tst(D(0)); B(7,'public_blit_return')
    c.imm('and',1,D(0)); B(6,'public_blit_return')

    # A stale payload/generation requires an atomic, fully checked restage.
    # No Chip copy is made for an unchanged selected bank.
    G('bank',D(3))
    B(1,'registry_lookup_entry')
    c.tst(D(3)); B(6,'public_blit_arm')
    G('bank',D(3)); G('gfx',A(4))
    B(1,'registry_prepare_entry')
    c.tst(D(3)); B(7,'public_blit_return')
    L('public_blit_arm')
    B(1,'program_end_arm_entry')
    c.tst(D(3)); B(7,'public_blit_unwind')

    # The synchronously drawing private bridge verifies the same bank
    # again, selects Safe back BitMap and does Blit+WaitBlit; no Swap.
    G('bank',D(3))
    G('image',D(0)); G('x',D(1)); G('y',D(4))
    B(1,'safe_bank_blit_entry')
    c.tst(D(3)); B(7,'public_blit_return')
    S(I(1),'result')
    B(0,'public_blit_return')

    # Unarmed Chip allocations must not survive End. This is also safe for
    # an idempotent earlier stage. Keep the official AMOS AGBO bank intact.
    L('public_blit_unwind')
    G('bank',D(3)); G('gfx',A(4))
    B(1,'registry_free_entry')

    L('public_blit_return')
    G('result',D(3))
    c.raw('4fef0060')               # restore local 96-byte frame
    c.raw('4cdf77f7')               # restore AMOS-preserved set
    c.raw('74004e75')               # D2=0, RTS

    raw=c.out()
    assert raw[:len(prefix)]==prefix, 'P0c/P0d private prefix altered'
    assert c.labels['public_bob_blit_entry']==len(prefix)
    assert len(raw)<32766 and len(raw)%2==0, 'V2 group exceeds 16-bit bound'
    return raw,c.labels


if __name__=='__main__':
    from hashlib import sha256
    raw, labels=emit_public_blit()
    print('M19 P0d public Bob Blit SOURCE ONLY',
          len(raw),sha256(raw).hexdigest(),
          'entry',labels['public_bob_blit_entry'],
          'no installed AP20/WinUAE/Compiler claim')
