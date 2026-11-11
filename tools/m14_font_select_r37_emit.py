"""R37 0.10.9: select an AmigaOS disk font for the extension's AGA text.

Exactly one new public AP20 function:
    _OK = Aga Font Select(name$, ysize)
Reset via ("",0). Name must have 1..127 non-NUL bytes, ysize 1..255.
OpenDiskFont may choose the closest installed size (standard AmigaOS rule).
Uses a private 8-byte HUNK runtime slot (screen*, TextFont*) as R23 does
for input state, not AMOS graphics or Screen.UserData. R37 text and close
hooks query this slot, and CloseFont releases the prior owned TextFont.
No persistent diskfont.library handle. No heap allocation by this code.
"""
from m68k_emit import Code, D, A, M, POST, PRE, I

ENTRY_FONT_SELECT = 48
BASE_ENTRIES = 48
ENTRY_TEXT = 36
ENTRY_SCREEN_CLOSE = 8
CLOSE_SCREEN_CALL_OFFSET = 0x8c
GETP = b"GetP"
STATE_PTR = 456
LVO_OPEN_LIBRARY = -552
LVO_CLOSE_LIBRARY = -414
LVO_OPEN_DISK_FONT = -30
LVO_CLOSE_FONT = -78
LVO_CLOSE_SCREEN = -66
FONT_STACK = 176
FONT_NAME_MAX = 127
FONT_SIZE_MAX = 255


def emit_font_select():
    """Build one PIC AP20 entry, two private entrypoints and HUNK data.

    labels['font_query'] is the BSR.W target for patched Aga Text,
    labels['font_close'] the BSR.W target for existing Screen Close.
    Data footer contains two longwords, initialised to zero.
    """
    c = Code()
    c.label("font_select")
    c.raw("48e7efee")                 # preserve D0,D1,D4..D7,A0..A2,A4..A6
    c.move(D(3), D(7))              # last argument: requested ysize
    c.move(POST(3), A(4))           # previous argument: AMOS string descriptor
    c.move(I(0), D(3))              # failure default (D2 is cleared at exit)

    c.move(M(5, STATE_PTR), A(2))
    c.move(A(2), D(0))
    c.tst(D(0)); c.branch(7, "exit")
    c.move(M(2), D(6))              # own private Screen*
    c.tst(D(6)); c.branch(7, "exit")
    c.move(M(2, 8), D(0))           # own GfxBase*
    c.tst(D(0)); c.branch(7, "exit")

    # Empty name with size=0 resets the override. Any other size/name
    # combination is rejected atomically without CloseFont.
    c.tst(D(7)); c.branch(6, "load_font")
    c.move(A(4), D(0))
    c.tst(D(0)); c.branch(7, "reset")
    c.move(I(0), D(0))
    c.move(M(4), D(0), "w")
    c.tst(D(0)); c.branch(6, "exit")
    c.label("reset")
    c.move(D(6), A(0))
    c.branch(1, "font_query")      # BSR.W, D0=previous font or 0
    c.tst(D(0)); c.branch(7, "reset_ok")
    c.lea(1, "font_state")
    c.move(I(0), M(1))
    c.move(I(0), M(1, 4))
    c.move(D(0), A(1))              # A1=old owned TextFont*
    c.move(M(2, 8), A(6))
    c.call_os(LVO_CLOSE_FONT)
    c.label("reset_ok")
    c.move(I(1), D(3))
    c.branch(0, "exit")

    c.label("load_font")
    c.imm("cmp", FONT_SIZE_MAX, D(7))
    c.branch(2, "exit")           # unsigned >255 also catches negatives
    c.move(A(4), D(0))
    c.tst(D(0)); c.branch(7, "exit")
    c.move(I(0), D(5))
    c.move(M(4), D(5), "w")
    c.tst(D(5)); c.branch(7, "exit")
    c.imm("cmp", FONT_NAME_MAX, D(5))
    c.branch(2, "exit")

    # Stack: TextAttr(+0..7), temporary name(+16..143),
    # diskfont.library NUL-string(+144..160); balanced on all exits.
    c.raw("4fefff50")             # LEA -176(SP),SP
    c.raw("41ef0010")             # LEA 16(SP),A0 (name output)
    c.move(A(4), A(1))
    c.quick(2, A(1))               # length-prefixed AMOS string data
    c.move(D(5), D(4))
    c.quick(1, D(4), sub=True)     # DBRA = length-1
    c.label("name_copy")
    c.move(POST(1), D(0), "b")
    c.tst(D(0), "b")
    c.branch(7, "abort_stack")    # reject an embedded NUL
    c.move(D(0), POST(0), "b")
    c.word(0x51cc)                 # DBRA D4,name_copy
    c.fix.append((len(c.b), "name_copy"))
    c.word(0)
    c.raw("4210")                 # CLR.B (A0) terminal NUL

    c.raw("41ef0010")             # LEA 16(SP),A0
    c.move(A(0), M(7))             # TextAttr.ta_Name
    c.move(D(7), M(7, 4), "w")     # ta_YSize
    c.move(I(0, "w"), M(7, 6), "w")  # ta_Style=0; ta_Flags=0

    # Build the library name on stack, no persistent string pointer.
    for off, value in ((144, 0x6469736b), (148, 0x666f6e74),
                       (152, 0x2e6c6962), (156, 0x72617279)):
        c.move(I(value), M(7, off))
    c.word(0x422f); c.word(160)   # CLR.B 160(SP)
    c.raw("43ef0090")            # LEA 144(SP),A1
    c.move(I(0), D(0))            # OpenLibrary version 0
    c.raw("2c780004")            # A6=ExecBase
    c.call_os(LVO_OPEN_LIBRARY)
    c.tst(D(0)); c.branch(7, "abort_stack")

    c.move(D(0), A(6))            # diskfont.library base
    c.move(A(7), A(0))            # TextAttr at SP
    c.call_os(LVO_OPEN_DISK_FONT)
    c.move(D(0), D(4))            # font pointer, or 0
    c.move(A(6), A(1))            # library handle to close
    c.raw("2c780004")            # ExecBase
    c.call_os(LVO_CLOSE_LIBRARY)
    c.tst(D(4)); c.branch(7, "abort_stack")

    # The new TextFont is now owned. Commit it only after successful open.
    c.move(D(6), A(0))
    c.branch(1, "font_query")
    c.move(D(0), D(5))            # previous selected font, if same screen
    c.lea(1, "font_state")
    c.move(D(6), M(1))
    c.move(D(4), M(1, 4))
    c.tst(D(5)); c.branch(7, "loaded_ok")
    c.move(D(5), A(1))
    c.move(M(2, 8), A(6))
    c.call_os(LVO_CLOSE_FONT)
    c.label("loaded_ok")
    c.move(I(1), D(3))
    c.label("abort_stack")
    c.raw("4fef00b0")            # LEA 176(SP),SP
    c.label("exit")
    c.raw("4cdf77f7")            # restore all nonresult registers
    c.raw("74004e75")            # D2=0 ; RTS

    # Private getter. Input A0=screen*, output D0=font* if matched.
    # Clobbers only scratch D0/D1/A1 and CCR.
    c.label("font_query")
    c.lea(1, "font_state")
    c.move(M(1), D(0))
    c.move(A(0), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(6, "query_none")
    c.move(M(1, 4), D(0))
    c.word(0x4e75)
    c.label("query_none")
    c.move(I(0), D(0))
    c.word(0x4e75)

    # Private Screen Close hook, called in place of original JSR -66(A6).
    # A0=Screen*, A2=State*, A6=IntuitionBase*, preserving each across
    # the graphics.library/CloseFont call, then invoking CloseScreen once.
    c.label("font_close")
    c.move(A(6), PRE(7))
    c.move(A(0), PRE(7))
    c.move(A(2), PRE(7))
    c.branch(1, "font_query")
    c.tst(D(0)); c.branch(7, "close_screen")
    c.lea(1, "font_state")
    c.move(I(0), M(1))
    c.move(I(0), M(1, 4))
    c.move(D(0), A(1))
    c.move(M(2, 8), A(6))
    c.call_os(LVO_CLOSE_FONT)
    c.label("close_screen")
    c.move(POST(7), A(2))
    c.move(POST(7), A(0))
    c.move(POST(7), A(6))
    c.call_os(LVO_CLOSE_SCREEN)
    c.word(0x4e75)

    c.label("font_state")
    c.raw("0000000000000000")  # screen*, TextFont* in private HUNK RAM
    raw = c.out()
    assert raw and len(raw) % 2 == 0
    assert raw[-8:] == bytes(8)
    return raw, c.labels


if __name__ == "__main__":
    raw, labels = emit_font_select()
    print("R37 font-select emitter",len(raw),"bytes",labels)
