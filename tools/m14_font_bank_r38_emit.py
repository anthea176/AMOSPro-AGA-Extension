"""R38 v0.11.0: AMCAF V1.31+ fixed/proportional monochrome BankFont -> private AGA TextFont.

One AP20 integer-result command: Aga Font Bank Select(Start(bank),Length(bank)).
Consumes the previous argument at (A3)+, length arrives in D3. The caller
must provide a real, live AMOS BankFont Start/Length pair; TypeOfMem is not
proof that an arbitrary address belongs to AMOS. No bank memory is changed.

The R37 font state continues to own the *selected pointer*, but ReleaseFont
is dispatched through R38 for bank-owned pointers. StripFont() + FreeVec()
cleans up the copied font (no CloseFont on manually constructed TextFont).
"""
from m68k_emit import Code, D, A, M, POST, PRE, I

ENTRY_INDEX = 49
R37_ENTRY_INDEX = 48
R37_SCREEN_CLOSE = 8
R37_TEXT = 36
MAX_BANK_BYTES = 65535
STATE_PTR = 456
FONT_AT = 24
NAME_AT = 76
LVO_TYPE_OF_MEM = -534
LVO_ALLOC_VEC = -684
LVO_FREE_VEC = -690
LVO_COPY_MEM = -624
LVO_CLOSE_FONT = -78
LVO_STRIP_FONT = -822
MEMF_PUBLIC_CHIP_CLEAR = 0x10003


def emit_bank_select():
    c = Code()
    c.label('font_bank_select')
    c.raw('48e7efee')               # preserve all AMOS registers except D2/D3/A3
    c.move(D(3), D(7))            # length
    c.move(POST(3), D(6))         # Start(bank) pointer
    c.move(I(0), D(3))            # default numeric failure
    c.move(M(5,STATE_PTR), A(2))
    c.move(A(2), D(0)); c.tst(D(0)); c.branch(7,'fail')
    c.move(M(2), D(0)); c.tst(D(0)); c.branch(7,'fail') # Screen*
    c.move(M(2,8), D(0)); c.tst(D(0)); c.branch(7,'fail') # GfxBase
    c.imm('cmp',112,D(7)); c.branch(5,'fail') # BCS <112
    c.imm('cmp',MAX_BANK_BYTES,D(7)); c.branch(2,'fail') # BHI
    c.move(D(6),D(0)); c.imm('cmp',24,D(0)); c.branch(3,'fail')
    c.imm('and',1,D(0)); c.branch(6,'fail') # reject odd pointers
    c.move(D(6), A(4))

    # Make sure the native header and the last byte exist in managed RAM.
    c.move(D(6),D(0)); c.imm('sub',24,D(0)); c.move(D(0),A(1))
    c.raw('2c780004')             # A6=ExecBase at 4.W
    c.call_os(LVO_TYPE_OF_MEM)
    c.tst(D(0)); c.branch(7,'fail')
    c.move(D(6), D(0)); c.alu('add',D(7),0); c.branch(5,'fail')
    c.quick(1,D(0),sub=True); c.move(D(0),A(1))
    c.call_os(LVO_TYPE_OF_MEM)
    c.tst(D(0)); c.branch(7,'fail')

    # Native AMOS bank header: Length at Start-20 = payload+16,
    # number Start-16, class at Start-12, 8-byte name at Start-8.
    c.move(M(4,-20),D(0)); c.move(D(7),D(1)); c.imm('add',16,D(1))
    c.alu('cmp',D(1),0); c.branch(6,'fail')
    c.move(M(4,-16),D(0))
    c.imm('cmp',5,D(0)); c.branch(5,'fail')
    c.imm('cmp',65535,D(0)); c.branch(2,'fail')
    c.move(I(0),D(0)); c.move(M(4,-12),D(0),'w')
    c.imm('and',0xfffc,D(0),'w'); c.tst(D(0)); c.branch(6,'fail') # flags 0..3: WORK/DATA, FAST/CHIP
    c.move(M(4,-8),D(0)); c.imm('cmp',0x42616e6b,D(0)); c.branch(6,'fail') # Bank
    c.move(M(4,-4),D(0)); c.imm('cmp',0x466f6e74,D(0)); c.branch(6,'fail') # Font
    c.move(M(4),D(0)); c.imm('cmp',0x464f4e54,D(0)); c.branch(6,'fail') # FONT
    c.move(I(0),D(0)); c.move(M(4,32),D(0),'b')
    c.imm('cmp',12,D(0)); c.branch(6,'fail') # NT_FONT

    # Header offsets are relative to Start(bank), not saved raw pointers.
    c.move(I(0),D(4)); c.move(M(4,10),D(4),'w')   # bitmap offset
    c.move(I(0),D(5)); c.move(M(4,14),D(5),'w')   # charloc offset
    c.imm('cmp',NAME_AT+2,D(4)); c.branch(5,'fail')
    c.alu('cmp',D(4),5); c.branch(3,'fail') # loc <= bitmap
    c.alu('cmp',D(7),5); c.branch(4,'fail') # loc >= length

    c.move(I(0),D(0)); c.move(M(4,44),D(0),'w') # ysize
    c.tst(D(0)); c.branch(7,'fail')
    c.imm('cmp',255,D(0)); c.branch(2,'fail')
    c.move(I(0),D(3)); c.move(M(4,48),D(3),'w') # xsize
    c.tst(D(3)); c.branch(7,'fail')
    c.imm('cmp',255,D(3)); c.branch(2,'fail')
    c.move(I(0),D(1)); c.move(M(4,50),D(1),'w') # baseline
    c.alu('cmp',D(0),1); c.branch(4,'fail')   # baseline>=ysize
    c.move(I(0),D(1)); c.move(M(4,46),D(1),'b')
    c.imm('and',0x40,D(1),'b'); c.tst(D(1)); c.branch(6,'fail')
    c.move(M(4,68),D(0)); c.tst(D(0)); c.branch(6,'fail')
    c.move(M(4,72),D(0)); c.tst(D(0)); c.branch(6,'fail')

    c.move(I(0),D(6)); c.move(M(4,57),D(6),'b') # hi
    c.move(I(0),D(0)); c.move(M(4,56),D(0),'b') # lo
    c.alu('sub',D(0),6); c.branch(5,'fail')
    c.quick(2,D(6))                 # glyphs including fallback
    # Fixed font: CharLoc[n] (4*n). Proportional font (FPF_PROPORTIONAL):
    # CharLoc[n] (4*n), CharSpace[n] (2*n), CharKern[n] (2*n).
    c.move(D(6),D(0)); c.shift(0,2,left=True)
    c.alu('add',D(5),0); c.branch(5,'fail')
    c.move(I(0),D(1)); c.move(M(4,47),D(1),'b')
    c.imm('and',0x20,D(1),'b'); c.tst(D(1),'b'); c.branch(7,'table_end')
    c.move(D(6),D(1)); c.shift(1,2,left=True)
    c.alu('add',D(1),0); c.branch(5,'fail')
    c.label('table_end')
    c.alu('cmp',D(7),0); c.branch(6,'fail') # all tables end at Length(bank)

    c.move(I(0),D(1)); c.move(M(4,62),D(1),'w') # modulo bytes
    c.tst(D(1)); c.branch(7,'fail')
    c.move(D(1),D(2)); c.imm('and',1,D(2)); c.branch(6,'fail')
    c.move(D(1),D(2)); c.shift(2,3,left=True) # bits per glyph row
    c.move(I(0),D(0)); c.move(M(4,44),D(0),'w') # height
    c.word(0xc0c1)                   # MULU.W D1,D0
    c.move(D(5),D(1)); c.alu('sub',D(4),1)
    c.alu('cmp',D(1),0); c.branch(6,'fail')

    # Scan font name until NUL without leaving the font's header.
    c.move(D(6), PRE(7))           # save glyph count while scanning name
    c.move(D(4),D(1)); c.imm('sub',NAME_AT,D(1))
    c.move(A(4),D(0)); c.imm('add',NAME_AT,D(0)); c.move(D(0),A(1))
    c.move(M(1),D(0),'b'); c.tst(D(0),'b'); c.branch(7,'abort_name')
    c.label('name_loop')
    c.move(I(0),D(0)); c.move(POST(1),D(0),'b')
    c.tst(D(0),'b'); c.branch(7,'name_done')
    c.quick(1,D(1),sub=True)       # D1 counts remaining bytes
    c.branch(6,'name_loop')
    c.label('abort_name')
    c.move(POST(7),D(6))
    c.branch(0,'fail')
    c.label('name_done')
    c.move(POST(7),D(6))

    # Validate bounded CharLoc table (offset & width for all glyphs).
    c.move(A(4),D(0)); c.alu('add',D(5),0); c.move(D(0),A(1))
    # For proportional fonts tf_XSize is the nominal advance, NOT the
    # (often wider) monochrome bitmap glyph width from CharLoc.
    c.move(I(0),D(0)); c.move(M(4,47),D(0),'b')
    c.imm('and',0x20,D(0),'b'); c.tst(D(0),'b'); c.branch(7,'charloc_loop')
    c.move(I(256),D(3))            # safe upper bound for proportional glyphs
    c.label('charloc_loop')
    c.label('check_loc')
    c.move(I(0),D(0)); c.move(POST(1),D(0),'w')
    c.move(I(0),D(1)); c.move(POST(1),D(1),'w')
    c.alu('cmp',D(3),1); c.branch(2,'fail')  # glyph width > xsize
    c.alu('add',D(1),0); c.alu('cmp',D(2),0); c.branch(2,'fail')
    c.quick(1,D(6),sub=True); c.branch(6,'check_loc')

    # All source-bank validation is now complete; allocate private CHIP RAM.
    c.move(A(4), PRE(7))          # save original bank pointer across AllocVec
    c.move(D(7),D(0)); c.move(I(MEMF_PUBLIC_CHIP_CLEAR),D(1))
    c.raw('2c780004')              # ExecBase
    c.call_os(LVO_ALLOC_VEC)
    c.tst(D(0)); c.branch(6,'have_mem')
    c.move(POST(7),A(0))          # allocation failed, balance stack
    c.branch(0,'fail')
    c.label('have_mem')
    c.move(D(0),A(4))             # private allocation base
    c.move(POST(7),A(0))         # original Start(bank) as CopyMem source
    c.move(A(4),A(1)); c.move(D(7),D(0))
    c.call_os(LVO_COPY_MEM)

    # Fix all TextFont pointers. In-bank pointers were absolute AMCAF values.
    c.move(A(4),D(0)); c.imm('add',NAME_AT,D(0)); c.move(D(0),M(4,34))
    c.move(A(4),D(0)); c.alu('add',D(4),0); c.move(D(0),M(4,58))
    c.move(A(4),D(0)); c.alu('add',D(5),0); c.move(D(0),M(4,64))
    c.move(I(0),M(4,38))           # no stale TextFontExtension: FONT payload offset24 + TextFont offset14
    c.move(I(0,'w'),M(4,54),'w')   # tf_Accessors 0
    c.move(I(0),D(0)); c.move(M(4,47),D(0),'b')
    c.imm('and',0x20,D(0),'b'); c.tst(D(0),'b')
    c.branch(6,'prop_pointers')
    c.move(I(0),M(4,68)); c.move(I(0),M(4,72))
    c.branch(0,'pointers_done')
    c.label('prop_pointers')
    # CharSpace = CharLoc + 4*n; CharKern = CharSpace + 2*n.
    # Their saved disk pointers are stale; both are now within private CHIP RAM.
    c.move(I(0),D(0)); c.move(M(4,57),D(0),'b')
    c.move(I(0),D(1)); c.move(M(4,56),D(1),'b')
    c.alu('sub',D(1),0); c.quick(2,D(0)); c.shift(0,2,left=True)
    c.move(A(4),D(1)); c.alu('add',D(5),1); c.alu('add',D(0),1)
    c.move(D(1),M(4,68))
    c.shift(0,1,left=False); c.alu('add',D(0),1)
    c.move(D(1),M(4,72))
    c.label('pointers_done')
    c.move(I(0),D(0)); c.move(M(4,47),D(0),'b')
    c.imm('and',0xfc,D(0),'b')     # unset ROM/disk flags for heap-owned font
    c.move(D(0),M(4,47),'b')

    # Release previous selection before changing the ownership record.
    c.word(0x43fa); c.label('r37_state_lookup'); c.word(0) # LEA d16(PC),A1
    c.move(M(1,4),D(6))            # old font pointer
    c.tst(D(6)); c.branch(7,'commit')
    c.move(D(6),A(1))
    c.move(M(2,8),A(6))            # GfxBase
    c.branch(1,'font_release')     # BSR.W helper, bank or OS font
    c.label('commit')
    c.move(A(4),D(0)); c.imm('add',FONT_AT,D(0))
    c.lea(1,'bank_state')
    c.move(D(0),M(1)); c.move(A(4),M(1,4))
    c.word(0x43fa); c.label('r37_state_commit'); c.word(0)
    c.move(M(2),M(1))              # write private Screen* to R37 slot
    c.move(D(0),M(1,4))            # write new TextFont*
    c.move(I(1),D(3))
    c.branch(0,'exit')

    c.label('fail')
    c.move(I(0),D(3))
    c.label('exit')
    c.raw('4cdf77f7')
    c.raw('74004e75')

    # Hook for all three R37 release calls; input A1=previous font,
    # A6=GfxBase; uses StripFont and FreeVec only for our owned bank copy.
    c.label('font_release')
    for reg in (D(0),D(1),A(0),A(2),A(6)):
        c.move(reg,PRE(7))
    c.move(A(1),D(0)); c.tst(D(0)); c.branch(7,'release_done')
    c.lea(2,'bank_state')
    c.alu('cmp',M(2),0)
    c.branch(6,'release_os_font')
    c.move(A(1),A(0))
    c.call_os(LVO_STRIP_FONT)
    c.lea(2,'bank_state')
    c.move(M(2,4),A(1))
    c.move(I(0),M(2)); c.move(I(0),M(2,4))
    c.raw('2c780004')
    c.call_os(LVO_FREE_VEC)
    c.branch(0,'release_done')
    c.label('release_os_font')
    c.call_os(LVO_CLOSE_FONT)
    c.label('release_done')
    for reg in (A(6),A(2),A(0),D(1),D(0)):
        c.move(POST(7),reg)
    c.word(0x4e75)

    c.label('bank_state')
    c.raw('0000000000000000')      # selected bank TextFont*, AllocVec base
    data = c.out()
    assert len(data)%2 == 0 and data[-8:] == bytes(8)
    return data,c.labels
