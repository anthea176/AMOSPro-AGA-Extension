"""68000 native mouse-edge samplers: private shared state, no IDCMP consumption.

The current R22 contract reads input.device qualifiers at each function
call, preserving the existing Aga Key RAWKEY queue. Short clicks occurring
entirely between samples remain unobservable. The two edge masks are queued
independently until their respective functions consume them.
"""
from m68k_emit import Code, A, D, I, M

STATE_PTR = 0x1C8
WINDOW = 36
SCREEN = 0
WINDOW_SCREEN = 46
WINDOW_FLAGS = 24
ACTIVE_BIT = 0x2000
IO_DEVICE = 20
OPEN_DEVICE = -444
CLOSE_DEVICE = -450
PEEK_QUALIFIER = -42
STATE_BYTES = 16


def clr(c, off):
    c.word(0x42AA)  # CLR.L d16(A2)
    c.word(off)


def lea_shared(c, delta):
    assert 0 < delta < 32767, delta
    c.word(0x45EA)  # LEA d16(A2),A2
    c.word(delta)


def emit_edge(which, delta, with_state=False):
    assert which in ('pressed', 'released')
    c = Code()
    c.raw('48e7efee')
    c.move(M(5, STATE_PTR), A(2))
    c.move(A(2), D(0)); c.tst(D(0)); c.branch(7, 'no_state')
    c.move(M(2, SCREEN), A(1))
    c.move(A(1), D(0)); c.tst(D(0)); c.branch(7, 'invalid')
    c.move(M(2, WINDOW), A(4))
    c.move(A(4), D(0)); c.tst(D(0)); c.branch(7, 'invalid')
    c.move(M(4, WINDOW_SCREEN), D(0))
    c.move(A(1), D(1)); c.alu('cmp', D(1), 0); c.branch(6, 'invalid')
    c.move(M(4, WINDOW_FLAGS), D(0))
    c.imm('and', ACTIVE_BIT, D(0)); c.branch(7, 'invalid')
    c.move(A(4), D(6))  # window identity, protects reopen/focus reset
    lea_shared(c, delta)
    c.raw('4fefffd0')  # LEA -48(SP),SP; local IOStdReq
    c.move(A(7), A(4)); c.move(A(4), A(0))
    for _ in range(12):
        c.raw('4298')  # CLR.L (A0)+
    c.raw('2c780004')  # ExecBase
    c.lea(0, 'device_name')
    c.move(I(0), D(0)); c.move(A(4), A(1)); c.move(I(0), D(1))
    c.call_os(OPEN_DEVICE)
    c.tst(D(0)); c.branch(6, 'device_fail')
    c.move(M(4, IO_DEVICE), A(6))
    c.move(A(6), D(0)); c.tst(D(0)); c.branch(7, 'device_close_fail')
    c.call_os(PEEK_QUALIFIER)
    c.imm('and', 0x7000, D(0), size='w')
    c.move(I(0), D(4))
    for mask, flag, suffix in ((0x4000, 1, 'left'),
                               (0x2000, 2, 'right'),
                               (0x1000, 4, 'middle')):
        c.move(D(0), D(1))
        c.imm('and', mask, D(1), size='w')
        c.branch(7, suffix)
        c.quick(flag, D(4))
        c.label(suffix)
    c.raw('2c780004')
    c.move(A(4), A(1))
    c.call_os(CLOSE_DEVICE)
    c.raw('4fef0030')
    c.branch(0, 'have_sample')
    c.label('device_close_fail')
    c.raw('2c780004')
    c.move(A(4), A(1))
    c.call_os(CLOSE_DEVICE)
    c.label('device_fail')
    c.raw('4fef0030')
    c.branch(0, 'clear_data')
    c.label('have_sample')
    c.move(M(2, 0), D(0))
    c.alu('cmp', D(6), 0)
    c.branch(6, 'baseline')
    c.move(M(2, 4), D(0))
    c.move(I(7), D(1))
    c.alu('sub', D(0), 1)
    c.alu('and', D(4), 1)  # pressed = (~previous & current) & 7
    c.move(I(7), D(5))
    c.alu('sub', D(4), 5)
    c.alu('and', D(0), 5)  # released = (previous & ~current) & 7
    c.move(M(2, 8), D(7))
    c.alu('or', D(1), 7)
    c.move(D(7), M(2, 8))
    c.move(M(2, 12), D(7))
    c.alu('or', D(5), 7)
    c.move(D(7), M(2, 12))
    c.move(D(4), M(2, 4))
    off = 8 if which == 'pressed' else 12
    c.move(M(2, off), D(3))
    clr(c, off)
    c.branch(0, 'done')
    c.label('baseline')
    c.move(D(6), M(2, 0))
    c.move(D(4), M(2, 4))
    clr(c, 8)
    clr(c, 12)
    c.move(I(0), D(3))
    c.branch(0, 'done')
    c.label('invalid')
    lea_shared(c, delta)
    c.label('clear_data')
    for off in (0, 4, 8, 12):
        clr(c, off)
    c.label('no_state')
    c.move(I(-1), D(3))
    c.label('done')
    c.raw('4cdf77f7')
    c.raw('74004e75')
    c.label('device_name')
    c.raw('696e7075742e6465766963650000')
    if with_state:
        c.label('shared_state')
        c.raw('00' * STATE_BYTES)
    output = c.out()
    assert len(output) % 2 == 0
    return output, c.labels
