"""M15bis/R44 68000 mouse-pointer visibility, window-local only.

Public AP20 function: _OK=Aga Mouse Cursor(Visible), 0=hide, 1=show.
A 16x16 all-zero two-bitplane sprite (72 bytes) is owned for the lifetime
of the active private Intuition window, allocated lazily from Chip memory.
All four *owned-window* CloseWindow calls are redirected to one cleanup
wrapper, called before the window is actually closed. An unrelated
Aga Palette Save private-window close is intentionally UNMODIFIED.
"""
from m68k_emit import Code, D, A, M, I

ENTRY_INDEX = 54
AMOS_STATE_PTR = 0x01C8
STATE_SCREEN = 0
STATE_INTUITION = 4
STATE_WINDOW = 36
WD_SCREEN = 46

SPRITE_SIZE = 72
SPRITE_HEIGHT = 16
SPRITE_WIDTH = 16
MEMF_CHIP_CLEAR = 0x00010002
LVO_SET_POINTER = -270
LVO_CLEAR_POINTER = -60
LVO_CLOSE_WINDOW = -72
LVO_ALLOC_MEM = -198
LVO_FREE_MEM = -210


def emit_cursor():
    c = Code()
    # ABI: AMOS D3=Visible, numeric function returns D3=0/1, D2=0.
    # A3 (AMOS parameter stack) stays unchanged; all other ordinary
    # callee-preserved registers as in R43. The wrapper saves ALL D/A0-A6.
    c.raw("48e7efee")
    c.move(D(3), D(7))
    c.move(I(0), D(3))
    c.tst(D(7))
    c.branch(13, "done")              # BLT: negative rejected
    c.imm("cmp", 1, D(7))
    c.branch(14, "done")              # BGT: >1 rejected
    c.move(M(5, AMOS_STATE_PTR), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, "done")
    c.move(M(4, STATE_SCREEN), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, "done")
    c.move(M(4, STATE_INTUITION), A(6))
    c.move(A(6), D(0))
    c.tst(D(0))
    c.branch(7, "done")
    c.move(M(4, STATE_WINDOW), A(3))
    c.move(A(3), D(0))
    c.tst(D(0))
    c.branch(7, "done")
    c.move(M(3, WD_SCREEN), D(0))
    c.move(A(1), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(6, "done")              # No pointer from Workbench/other Window.
    c.lea(2, "cursor_state")           # A2 -> pointer, owning Window

    # A cached cursor may only belong to this exact active private Window.
    c.move(M(2, 0), D(0))
    c.tst(D(0))
    c.branch(7, "state_ready")
    c.move(M(2, 4), D(0))
    c.move(A(3), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(6, "done")
    c.label("state_ready")

    # Visible=1 -> ClearPointer even when no image has been allocated.
    # ClearPointer has no documented error code; result 1 means applied.
    c.tst(D(7))
    c.branch(7, "hide")
    c.move(A(3), A(0))
    c.call_os(LVO_CLEAR_POINTER)
    c.move(I(1), D(3))
    c.branch(0, "done")

    c.label("hide")
    c.move(M(2, 0), D(0))
    c.tst(D(0))
    c.branch(6, "set_pointer")
    # First hide only; no allocation on repeated hide/show calls.
    c.move(I(SPRITE_SIZE), D(0))
    c.move(I(MEMF_CHIP_CLEAR), D(1))
    c.raw("2c780004")                # A6=ExecBase via absolute address 4
    c.call_os(LVO_ALLOC_MEM)
    c.tst(D(0))
    c.branch(7, "done")              # OOM; no state or pointer modification.
    c.move(D(0), M(2, 0))
    c.move(A(3), M(2, 4))

    c.label("set_pointer")
    c.move(A(3), A(0))
    c.move(M(2, 0), A(1))
    c.move(I(SPRITE_HEIGHT), D(0))
    c.move(I(SPRITE_WIDTH), D(1))
    c.move(I(0), D(2))
    c.move(I(0), D(3))
    c.move(M(4, STATE_INTUITION), A(6))
    c.call_os(LVO_SET_POINTER)
    c.move(I(1), D(3))

    c.label("done")
    c.raw("4cdf77f7")                # R43 normal ABI restore (except D3/A3)
    c.raw("74004e75")                # D2=integer result, RTS

    # Shared CloseWindow hook for segment 0,8,17,18:
    # A0 = Window*, A6 = IntuitionBase. All original register values
    # are restored, so caller's post-CloseWindow logic is untouched.
    c.label("close_window_hook")
    c.raw("48e7fffe")                # D0-D7 / A0-A6, not A7
    c.move(A(0), A(3))
    c.lea(4, "cursor_state")
    c.move(M(4, 0), D(0))
    c.tst(D(0))
    c.branch(7, "close_actual")
    c.move(M(4, 4), D(0))
    c.move(A(3), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(6, "close_actual")
    c.move(A(3), A(0))
    c.call_os(LVO_CLEAR_POINTER)      # BEFORE CloseWindow, before FreeMem

    c.label("close_actual")
    c.move(A(3), A(0))
    c.call_os(LVO_CLOSE_WINDOW)

    # The old Window cannot refer to this image after CloseWindow.
    # Free exactly 72 bytes, not its rounded 8-byte footprint.
    c.move(M(4, 0), D(0))
    c.tst(D(0))
    c.branch(7, "close_done")
    c.move(M(4, 4), D(0))
    c.move(A(3), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(6, "close_done")
    c.move(M(4, 0), A(1))
    c.move(I(SPRITE_SIZE), D(0))
    c.raw("2c780004")                # ExecBase, not IntuitionBase
    c.call_os(LVO_FREE_MEM)
    c.move(I(0), M(4, 0))
    c.move(I(0), M(4, 4))

    c.label("close_done")
    c.raw("4cdf7fff")                # Restore all D0-D7/A0-A6, not A7
    c.raw("4e75")                    # RTS to original cleanup caller

    # Two longs placed after RTS in private extension code storage, not
    # in 40-byte shared AGA runtime state. Never touch the R43 state size.
    c.label("cursor_state")
    c.raw("0000000000000000")
    raw = c.out()
    assert len(raw) & 1 == 0 and raw[-8:] == bytes(8)
    return raw, c.labels
