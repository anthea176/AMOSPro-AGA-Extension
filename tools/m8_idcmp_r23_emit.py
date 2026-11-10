"""M8/R23: real IDCMP mouse events + lossless RAWKEY FIFO for Aga Key.

68000-only emitter. A single pump drains up to 64 messages per call, always
ReplyMsg exactly once after copying fields; it never waits. RAWKEY downs
are buffered in a 16-entry FIFO, with backpressure rather than key loss.
Original Aga Key/Wait Key parsing (including Ctrl+C cleanup) is preserved,
receiving a synthetic IntuiMessage that must NOT be replied a second time.
"""
from m68k_emit import Code, A, D, I, M

STATE_PTR = 456
STATE_SCREEN = 0
STATE_WINDOW = 36
WINDOW_SCREEN = 46
WINDOW_FLAGS = 24
WINDOW_USERPORT = 86
WFLG_ACTIVE = 0x2000
IDCMP_MOUSEBUTTONS = 0x8
IDCMP_RAWKEY = 0x400
IDCMP_ACTIVEWINDOW = 0x40000
IDCMP_INACTIVEWINDOW = 0x80000

LAST_WINDOW = 0
DOWN = 4
UP = 8
HELD = 12
KEY_HEAD = 16
KEY_TAIL = 20
KEY_COUNT = 24
ACTIVE = 28
FAKE = 32
FAKE_CLASS = FAKE + 20
FAKE_CODEQUAL = FAKE + 24
KEY_FIFO = 80
KEY_CAP = 16
STATE_BYTES = KEY_FIFO + KEY_CAP * 4
MAX_MESSAGES_PER_CALL = 64

EXECBASE = 4
GET_MSG = -372
REPLY_MSG = -378

def q(c, reg, val):
    assert -128 <= val <= 127
    c.word(0x7000 | reg << 9 | (val & 255))

def clear(c, disp):
    c.word(0x42aa)  # CLR.L d16(A2)
    c.word(disp)

def state_base(c, delta):
    assert 0 < delta < 32767
    c.word(0x45ea)  # LEA d16(A2),A2
    c.word(delta)

def lea_a0(c, disp):
    c.word(0x41ea)  # LEA d16(A2),A0
    c.word(disp)

def dec_branch(c, reg, name):
    c.word(0x51c8 | reg)  # DBRA Dn,d16(PC)
    c.fix.append((len(c.b), name))
    c.word(0)

def reset_mouse(c):
    for off in (DOWN, UP, HELD, ACTIVE):
        clear(c, off)

def add_index(c, disp):
    # D1 = slot_index * 4 ; A0 = (&state[disp]) + D1.
    c.alu('add', D(1), 1)
    c.alu('add', D(1), 1)
    lea_a0(c, disp)
    c.move(A(0), D(0))
    c.alu('add', D(1), 0)
    c.move(D(0), A(0))

def emit_dispatcher(delta):
    """Return real 68000 code, PC-label offsets. Entry is private AP20 #33."""
    c = Code()
    c.label('pump')
    c.raw('48e77ffe')  # save D1-D7/A0-A6 (D0 is result)
    c.move(M(5, STATE_PTR), A(2))
    c.move(A(2), D(0))
    c.tst(D(0))
    c.branch(7, 'pump_invalid')
    c.move(M(2, STATE_SCREEN), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, 'pump_invalid')
    c.move(M(2, STATE_WINDOW), A(3))
    c.move(A(3), D(0))
    c.tst(D(0))
    c.branch(7, 'pump_invalid')
    c.move(M(3, WINDOW_SCREEN), D(0))
    c.move(A(1), D(1))
    c.alu('cmp', D(1), 0)
    c.branch(6, 'pump_invalid')
    c.move(M(3, WINDOW_USERPORT), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, 'pump_invalid')
    state_base(c, delta)
    c.move(M(2, LAST_WINDOW), D(0))
    c.move(A(3), D(1))
    c.alu('cmp', D(1), 0)
    c.branch(7, 'same_window')
    c.move(A(3), M(2, LAST_WINDOW))
    reset_mouse(c)
    c.move(M(3, WINDOW_FLAGS), D(0))
    c.imm('and', WFLG_ACTIVE, D(0))
    c.branch(7, 'same_window')
    c.move(I(1), M(2, ACTIVE))
    c.label('same_window')
    c.move(M(3, WINDOW_FLAGS), D(0))
    c.imm('and', WFLG_ACTIVE, D(0))
    c.branch(6, 'pump_loop_setup')
    reset_mouse(c)
    c.label('pump_loop_setup')
    q(c, 7, MAX_MESSAGES_PER_CALL - 1)
    c.label('pump_loop')
    c.move(M(2, KEY_COUNT), D(0))
    c.imm('cmp', KEY_CAP, D(0))
    c.branch(4, 'pump_done')  # BCC: do not dequeue any new message if full
    c.move(A(4), A(0))
    c.raw('2c780004')  # MOVEA.L (4).W,A6 = ExecBase
    c.call_os(GET_MSG)
    c.tst(D(0))
    c.branch(7, 'pump_done')
    c.move(D(0), A(3))
    c.move(M(3, 20), D(4))  # IntuiMessage.Class
    q(c, 5, 0)
    c.move(M(3, 24), D(5), size='w')  # Code (unsigned 16)
    q(c, 6, 0)
    c.move(M(3, 26), D(6), size='w')  # Qualifier
    c.imm('cmp', IDCMP_RAWKEY, D(4))
    c.branch(7, 'rawkey')
    c.imm('cmp', IDCMP_MOUSEBUTTONS, D(4))
    c.branch(7, 'mouse_event')
    c.imm('cmp', IDCMP_INACTIVEWINDOW, D(4))
    c.branch(7, 'inactive_event')
    c.imm('cmp', IDCMP_ACTIVEWINDOW, D(4))
    c.branch(7, 'active_event')
    c.branch(0, 'reply')
    c.label('rawkey')
    c.move(D(5), D(0))
    c.imm('and', 0x80, D(0))  # ignore raw key UP, as the R22 Key did
    c.branch(6, 'reply')
    c.move(D(5), D(0))
    c.word(0x4840)  # SWAP D0: rawcode to high word
    c.move(D(6), D(0), size='w')  # qualifier into low word
    c.move(D(0), D(4))  # packed code/qual
    c.move(M(2, KEY_TAIL), D(1))
    add_index(c, KEY_FIFO)
    c.move(D(4), M(0))
    c.move(M(2, KEY_TAIL), D(0))
    c.quick(1, D(0))
    c.imm('and', KEY_CAP - 1, D(0))
    c.move(D(0), M(2, KEY_TAIL))
    c.quick(1, M(2, KEY_COUNT))
    c.branch(0, 'reply')
    c.label('mouse_event')
    c.move(M(2, ACTIVE), D(0))
    c.tst(D(0))
    c.branch(7, 'reply')
    c.move(D(5), D(0))
    c.imm('and', 0x7f, D(0))
    c.imm('cmp', 0x68, D(0))
    c.branch(7, 'mouse_left')
    c.imm('cmp', 0x69, D(0))
    c.branch(7, 'mouse_right')
    c.imm('cmp', 0x6a, D(0))
    c.branch(7, 'mouse_middle')
    c.branch(0, 'reply')
    c.label('mouse_left')
    q(c, 1, 1)
    c.branch(0, 'mouse_have_mask')
    c.label('mouse_right')
    q(c, 1, 2)
    c.branch(0, 'mouse_have_mask')
    c.label('mouse_middle')
    q(c, 1, 4)
    c.label('mouse_have_mask')
    c.move(D(5), D(0))
    c.imm('and', 0x80, D(0))
    c.branch(6, 'mouse_up')
    c.move(M(2, HELD), D(0))
    c.move(D(0), D(4))
    c.alu('and', D(1), 4)
    c.tst(D(4))
    c.branch(6, 'reply')  # ignore repeated DOWN without UP
    c.alu('or', D(1), 0)
    c.move(D(0), M(2, HELD))
    c.move(M(2, DOWN), D(0))
    c.alu('or', D(1), 0)
    c.move(D(0), M(2, DOWN))
    c.branch(0, 'reply')
    c.label('mouse_up')
    c.move(M(2, HELD), D(0))
    c.move(D(0), D(4))
    c.alu('and', D(1), 4)
    c.tst(D(4))
    c.branch(7, 'reply')  # orphan UP is not a click
    c.alu('sub', D(1), 0)
    c.move(D(0), M(2, HELD))
    c.move(M(2, UP), D(0))
    c.alu('or', D(1), 0)
    c.move(D(0), M(2, UP))
    c.branch(0, 'reply')
    c.label('inactive_event')
    reset_mouse(c)
    c.branch(0, 'reply')
    c.label('active_event')
    reset_mouse(c)
    c.move(M(2, LAST_WINDOW), A(0))
    c.move(M(0, WINDOW_FLAGS), D(0))
    c.imm('and', WFLG_ACTIVE, D(0))
    c.branch(7, 'reply')
    c.move(I(1), M(2, ACTIVE))
    c.label('reply')
    c.move(A(3), A(1))  # original message, fields were read before ReplyMsg
    c.raw('2c780004')
    c.call_os(REPLY_MSG)
    dec_branch(c, 7, 'pump_loop')
    c.label('pump_done')
    q(c, 0, 0)
    c.branch(0, 'pump_exit')
    c.label('pump_invalid')
    q(c, 0, -1)
    c.label('pump_exit')
    c.raw('4cdf7ffe')  # restore D1-D7/A0-A6, keep D0 result
    c.word(0x4e75)

    c.label('key_next')
    c.branch(1, 'pump')  # BSR.W shared dispatcher
    c.tst(D(0))
    c.branch(6, 'no_key')
    c.raw('48e77ffe')
    c.move(M(5, STATE_PTR), A(2))
    state_base(c, delta)
    c.move(M(2, KEY_COUNT), D(0))
    c.tst(D(0))
    c.branch(7, 'no_queued_key')
    c.move(M(2, KEY_HEAD), D(1))
    add_index(c, KEY_FIFO)
    c.move(M(0), D(4))  # packed (code << 16 | qualifier)
    lea_a0(c, FAKE)
    c.move(I(IDCMP_RAWKEY), M(0, 20))
    c.move(D(4), M(0, 24))
    c.move(M(2, KEY_HEAD), D(1))
    c.quick(1, D(1))
    c.imm('and', KEY_CAP - 1, D(1))
    c.move(D(1), M(2, KEY_HEAD))
    c.quick(1, M(2, KEY_COUNT), sub=True)
    c.move(A(0), D(0))
    c.branch(0, 'key_finish')
    c.label('no_queued_key')
    q(c, 0, 0)
    c.label('key_finish')
    c.raw('4cdf7ffe')
    c.word(0x4e75)
    c.label('no_key')
    q(c, 0, 0)
    c.word(0x4e75)

    c.label('runtime_state')
    c.raw('00' * STATE_BYTES)
    raw = c.out()
    assert len(raw) % 2 == 0
    assert c.labels['runtime_state'] + STATE_BYTES == len(raw)
    return raw, c.labels


def emit_mouse_reader(which, delta):
    """R23 mouse function calling the pump; BSR target patched by builder."""
    assert which in ('pressed', 'released')
    c = Code()
    c.raw('48e7efee')  # preserve R22 ABI except result D3
    c.move(M(5, STATE_PTR), A(2))
    c.move(A(2), D(0))
    c.tst(D(0))
    c.branch(7, 'invalid')
    c.move(M(2, STATE_WINDOW), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, 'invalid')
    c.move(M(4, WINDOW_FLAGS), D(0))
    c.imm('and', WFLG_ACTIVE, D(0))
    c.branch(7, 'unfocused')
    c.word(0x6100)  # BSR.W into private dispatcher
    call_ext = len(c.b)
    c.word(0)
    c.tst(D(0))
    c.branch(6, 'invalid')
    c.move(M(5, STATE_PTR), A(2))
    state_base(c, delta)
    off = DOWN if which == 'pressed' else UP
    c.move(M(2, off), D(3))
    clear(c, off)
    c.branch(0, 'done')
    c.label('unfocused')
    state_base(c, delta)
    reset_mouse(c)
    c.label('invalid')
    q(c, 3, -1)
    c.label('done')
    c.raw('4cdf77f7')  # restore D0-D2/D4-D7/A0-A6
    c.raw('74004e75')  # MOVEQ #0,D2; RTS
    return c.out(), call_ext
