"""R82 experimental unified Bank Palette Apply/Fade MC68020 emitters.

AGAPAL v1 is delegated to the unchanged native R32/R33 entry through a
signed 32-bit PC-relative BSR.L.  AGAPIC v2 uses embedded RGB24 directly
and the same AmigaOS RGB32 / blocking DDA contracts.  No source bank writes.

Native code is generated in memory only.  Gate A/WinUAE remain separate.
"""
from __future__ import annotations

from struct import pack, pack_into, unpack_from
from m68k_emit import Code, A, D, M, POST, I

BANK_LOOKUP = bytes.fromhex('fe11f700031d')  # AMOS main Bnk.GetAdr #797
BSR_LONG = bytes.fromhex('61ff00000000')
LVO_TYPEOFMEM = -534
LVO_ALLOCVEC = -684
LVO_FREEVEC = -690
LVO_GETRGB32 = -900
LVO_LOADRGB32 = -882
LVO_WAITTOF = -270
LVO_GETVPMODEID = -792
STATE_PTR = 0x1c8
MAX_PAYLOAD = 0x01000000
UNSUPPORTED_MODE = 0x0c80

# 96-byte local frame, held at SP across BSR.L and Exec/graphics calls.
# The caller A3 pointer is restored regardless of the branch selected.
F = dict(arg=0, bank=4, index=8, caller=12, start=16, rgb=20,
         colors=24, state=28, screen=32, table=36, length=40,
         duration=44, v2_mode=48)


def _emit(is_fade: bool, native_start: int, legacy_target: int):
    c = Code()
    def b(cond, label): c.branch(cond, label)
    def l(name): c.label(name)
    def fail_if_zero(r):
        c.move(r,D(0)); c.tst(D(0)); b(7,'fail')
    def u16(off, dst=0):
        c.move(I(0),D(dst))
        c.move(M(0,off),D(dst),'w')
    def fl(key, reg): c.move(M(2,F[key]),reg)
    def fs(reg, key): c.move(reg,M(2,F[key]))
    c.raw('48e7efee')          # standard R81 register-save set
    c.raw('4fefffa0')          # LEA -96(SP),SP
    c.move(A(7),A(2))
    fs(D(3),'arg')             # Apply=index; Fade=duration
    if is_fade:
        c.move(POST(3),D(7)); fs(D(7),'index')
        c.move(POST(3),D(7)); fs(D(7),'bank')
    else:
        fs(D(3),'index')
        c.move(POST(3),D(7)); fs(D(7),'bank')
    fs(A(3),'caller')
    c.move(I(0),D(3))        # fail closed
    if is_fade:
        fl('arg',D(0))
        c.tst(D(0)); b(7,'fail')
        c.imm('cmp',255,D(0)); b(2,'fail')
    fl('bank',D(0))
    c.imm('cmp',5,D(0)); b(5,'fail')
    c.imm('cmp',65535,D(0)); b(2,'fail')
    # Never execute BSR.L (020 only) on CPU 68000/68010.
    c.raw('20780004')         # MOVEA.L 4.W,A0 (ExecBase)
    fail_if_zero(A(0))
    c.move(M(0,0x128),D(0),'w')
    c.word(0x0800); c.word(1)  # BTST #AFF_68020,D0
    b(7,'fail')
    fl('bank',D(0))
    c.raw(BANK_LOOKUP.hex())
    fail_if_zero(A(0))
    fs(A(0),'start')
    c.move(A(0),D(4))        # preserve Start(B) across dispatch
    c.move(M(0,-8),D(0))
    c.imm('cmp',0x41474150,D(0)); b(6,'fail')
    c.move(M(0,-4),D(0))
    c.imm('cmp',0x414c2020,D(0)); b(6,'try_image')
    # AGAPAL v1: exactly the old API implementation (full native preflight).
    # R32 Apply consumes one LONG Start at frame+64; R33 Fade takes
    # slot at +64 then Start at +68. Do not shift Apply by four bytes.
    fl('start',D(0)); c.move(D(0),M(2,68 if is_fade else 64))
    if is_fade:
        fl('index',D(0)); c.move(D(0),M(2,64))
    fl('arg',D(3))
    c.raw('47ea0040')        # LEA 64(A2),A3 synthetic arguments
    l('delegate')
    c.raw(BSR_LONG.hex())
    b(0,'done')

    l('try_image')
    c.imm('cmp',0x49432020,D(0)); b(6,'fail')  # bank label "AGAPIC  "
    fl('index',D(0)); c.tst(D(0)); b(6,'fail')  # AGAPIC v2 only index 0
    # Verify mapped native bank header before any bank allocation fields.
    c.move(D(4),D(0)); c.imm('sub',24,D(0))
    c.move(D(0),A(1)); c.raw('2c780004')
    c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0)); b(7,'fail')
    fl('start',A(0))
    c.move(M(0,-16),D(0))
    fl('bank',D(1)); c.alu('cmp',D(1),0); b(6,'fail')
    u16(-12)
    # Loaded AGAPIC DATA may report 0, 1 or 3 native flags.
    c.tst(D(0)); b(7,'v2_bank_flags_ok')
    c.imm('and',0xfffd,D(0),'w')
    c.imm('cmp',1,D(0)); b(6,'fail')
    l('v2_bank_flags_ok')
    c.move(M(0,-20),D(0))
    c.imm('cmp',16+64,D(0)); b(5,'fail')
    c.imm('sub',16,D(0))
    c.imm('cmp',MAX_PAYLOAD,D(0)); b(2,'fail')
    fs(D(0),'length')
    fl('start',D(1)); c.alu('add',D(1),0); b(5,'fail')
    c.quick(1,D(0),sub=True); c.move(D(0),A(1))
    c.raw('2c780004'); c.call_os(LVO_TYPEOFMEM)
    c.tst(D(0)); b(7,'fail')
    fl('start',A(0))
    c.move(M(0),D(0)); c.imm('cmp',0x41474150,D(0)); b(6,'fail')
    u16(4); c.imm('cmp',0x4943,D(0)); b(6,'fail')
    u16(6); c.imm('cmp',2,D(0)); b(6,'fail')
    u16(8)
    c.imm('cmp',2,D(0)); b(5,'fail')
    c.imm('cmp',3,D(0)); b(2,'fail')
    c.move(D(0),D(1)); c.imm('and',1,D(1))
    fs(D(1),'v2_mode')      # temporary mask present flag
    u16(10); c.imm('cmp',1,D(0)); b(6,'fail')
    for off in (12,14):
        u16(off)
        c.tst(D(0)); b(7,'fail')
        c.imm('cmp',4096,D(0)); b(2,'fail')
    u16(12,1); u16(14)
    c.word(0xc0c1)  # MULU.W width,height -> image pixel count
    c.imm('cmp',0x00400000,D(0)); b(2,'fail')
    u16(16)
    c.tst(D(0)); b(7,'fail')
    c.imm('cmp',8,D(0)); b(2,'fail')
    c.move(D(0),D(7))       # image depth
    fl('v2_mode',D(1)); c.alu('add',D(1),0)
    c.shift(0,1,left=True)
    u16(18,1); c.alu('cmp',D(1),0); b(6,'fail')
    c.move(M(0,28),D(0))
    fl('length',D(1)); c.alu('cmp',D(1),0); b(6,'fail')
    # Mandatory mode / full RGB24 metadata.
    c.move(M(0,32),D(0))
    c.tst(D(0)); b(7,'fail')
    c.imm('cmp',-1,D(0)); b(7,'fail')
    fs(D(0),'v2_mode')
    c.move(I(1),D(7))
    u16(16,5)
    l('palette_count_loop')
    c.shift(7,1,left=True)
    c.quick(1,D(5),sub=True)
    b(6,'palette_count_loop')
    u16(36); c.alu('cmp',D(7),0); b(6,'fail')
    u16(38); c.imm('cmp',1,D(0)); b(6,'fail')
    for off in (40,48):
        c.move(M(0,off),D(0)); c.imm('cmp',64,D(0)); b(6,'fail')
    c.move(D(7),D(5))
    c.raw('cafc0003')       # MULU.W #3,D5
    c.move(M(0,44),D(0)); c.alu('cmp',D(5),0); b(6,'fail')
    for off in (52,56,60):
        c.tst(M(0,off)); b(6,'fail')
    c.move(D(5),D(0)); c.imm('add',67,D(0))
    c.imm('and',0xfffffffc,D(0))
    c.alu('cmp',M(0,20),0); b(6,'fail')
    fs(D(0),'table')
    # RGB24 padding (0..3 bytes) must be zero before the row table.
    c.move(D(0),D(6))
    c.move(D(5),D(1)); c.imm('add',64,D(1))
    c.alu('sub',D(1),6)
    c.tst(D(6)); b(7,'padding_done')
    fl('start',D(0)); c.alu('add',D(1),0); c.move(D(0),A(1))
    l('padding_loop')
    c.tst(POST(1),'b'); b(6,'fail')
    c.quick(1,D(6),sub=True); b(6,'padding_loop')
    l('padding_done')
    fl('start',A(0))
    fl('table',D(0))  # relative table offset, not last padding pointer
    u16(14,1)
    c.quick(1,D(1)); c.shift(1,2,left=True)
    c.alu('add',D(1),0)
    c.alu('cmp',M(0,24),0); b(6,'fail')
    fl('length',D(1)); c.alu('cmp',D(1),0); b(2,'fail')
    c.move(D(0),D(4))       # stream offset, not screen!
    fl('table',D(1))
    fl('start',D(0)); c.alu('add',D(1),0)
    c.move(D(0),A(1))
    c.move(M(1),D(5)); c.alu('cmp',D(4),5); b(6,'fail')
    u16(14,6)
    l('row_offsets_loop')
    c.move(M(1,4),D(0))
    c.alu('cmp',D(5),0); b(3,'fail')  # offset <= previous: reject
    fl('length',D(1)); c.alu('cmp',D(1),0); b(2,'fail')
    c.move(D(0),D(5)); c.quick(4,A(1))
    c.quick(1,D(6),sub=True); b(6,'row_offsets_loop')
    fl('length',D(1)); c.alu('cmp',D(1),5); b(6,'fail')
    # Palette bytes are inside payload: 64 + 3*N <= TableOffset.
    fl('start',D(0)); c.imm('add',64,D(0))
    fs(D(0),'rgb')   # keep A2 as frame pointer until all screen checks
    # Screen validation: source depth and real ModeID are mandatory.
    c.move(M(5,STATE_PTR),A(4)); fail_if_zero(A(4))
    c.move(M(4,0),A(1)); fail_if_zero(A(1))
    fs(A(1),'screen')
    c.tst(M(4,8)); b(7,'fail')
    c.move(M(4,28),D(0))
    u16(16,1)  # A0 still bank Start; reloaded below if needed
    c.alu('cmp',D(1),0); b(6,'fail')
    c.move(M(4,24),D(0)); c.imm('and',UNSUPPORTED_MODE,D(0)); b(6,'fail')
    c.move(M(4,20),D(0)); c.imm('cmp',256,D(0)); b(2,'fail')
    c.alu('cmp',D(7),0); b(5,'fail')
    fl('screen',A(1))
    c.move(M(1,48),A(1)); fail_if_zero(A(1))
    c.move(A(1),A(0))
    u16(2)  # ColorMap.Count
    c.imm('cmp',256,D(0)); b(2,'fail')
    c.alu('cmp',D(7),0); b(5,'fail')
    fl('screen',A(0))
    c.move(A(0),D(0)); c.imm('add',44,D(0)); c.move(D(0),A(0))
    c.move(M(4,8),A(6))
    c.call_os(LVO_GETVPMODEID)
    c.imm('cmp',-1,D(0)); b(7,'fail')
    fl('v2_mode',D(1)); c.alu('cmp',D(1),0); b(6,'fail')
    fl('rgb',A(2))  # switch A2 to read-only RGB24 after validation
    # A2 holds embedded RGB24 throughout painting; never write to it.
    if is_fade:
        _fade_rgb32(c)
    else:
        _apply_rgb32(c)
    b(0,'done')
    l('fail')
    c.move(I(0),D(3))
    l('done')
    c.move(M(7,F['caller']),A(3))
    c.raw('4fef0060')       # release 96-byte frame
    c.raw('4cdf77f7')       # restore except result D2,D3, consumed A3
    c.raw('74004e75')       # D2 integer; RTS
    result=bytearray(c.out())
    at=c.labels['delegate']
    assert result[at:at+6]==BSR_LONG
    relative=legacy_target-(native_start+at+2)
    assert -(1<<31)<=relative<1<<31
    pack_into('>i',result,at+2,relative)
    assert native_start+at+2+unpack_from('>i',result,at+2)[0]==legacy_target
    assert result.count(BANK_LOOKUP)==1
    return bytes(result),dict(c.labels, native_start=native_start,
                              native_target=legacy_target,
                              legacy_branch_long_displacement=relative)


def _expand_rgb(c):
    """Low byte D0 replicated to RGB32, stored in (A1)+; modifies D1."""
    c.move(D(0),D(1)); c.shift(0,8,left=True); c.alu('or',D(1),0)
    c.move(D(0),D(1)); c.raw('4840'); c.alu('or',D(1),0)
    c.move(D(0),POST(1))


def _apply_rgb32(c):
    def b(cond,lbl): c.branch(cond,lbl)
    def l(lbl): c.label('apply_'+lbl)
    c.move(D(7),D(0)); c.raw('c0fc000c'); c.imm('add',8,D(0))
    c.move(I(1),D(1)); c.raw('2c780004'); c.call_os(LVO_ALLOCVEC)
    c.tst(D(0)); b(7,'fail')
    c.move(D(0),A(4))
    c.move(A(4),A(1))
    c.move(D(7),D(0)); c.raw('4840'); c.move(D(0),POST(1))
    c.move(D(7),D(6))
    l('color_loop')
    for _ in range(3):
        c.move(I(0),D(0)); c.move(POST(2),D(0),'b'); _expand_rgb(c)
    c.quick(1,D(6),sub=True); b(6,'apply_color_loop')
    c.move(I(0),M(1))
    c.move(M(5,STATE_PTR),A(0)); c.move(M(0,0),A(0))
    c.move(A(0),D(0)); c.imm('add',44,D(0)); c.move(D(0),A(0))
    c.move(A(4),A(1))
    c.move(M(5,STATE_PTR),A(6)); c.move(M(6,8),A(6))
    c.call_os(LVO_LOADRGB32)
    c.move(A(4),A(1)); c.raw('2c780004'); c.call_os(LVO_FREEVEC)
    c.move(I(1),D(3))
    c.branch(0,'done')


def _fade_rgb32(c):
    """Port of the R33 fixed-point color transition after v2 validation."""
    def b(cond,lbl): c.branch(cond,lbl)
    def l(lbl): c.label('fade_'+lbl)
    c.move(M(7,F['arg']),D(6))  # original vbl, stack frame not A2
    c.tst(D(6)); b(7,'fail')
    c.imm('cmp',255,D(6)); b(2,'fail')
    c.move(D(7),D(0)); c.raw('c0fc002a'); c.imm('add',8,D(0))
    c.move(I(1),D(1)); c.raw('2c780004'); c.call_os(LVO_ALLOCVEC)
    c.tst(D(0)); b(7,'fail')
    c.move(D(0),A(4))
    c.imm('cmp',1,D(6)); b(7,'fade_frames_setup')
    # GetRGB32 output is at scratch +8+12*N
    c.move(D(7),D(0)); c.raw('c0fc000c'); c.imm('add',8,D(0))
    c.move(A(4),D(1)); c.alu('add',D(1),0); c.move(D(0),A(1))
    c.move(M(5,STATE_PTR),A(0)); c.move(M(0,0),A(0))
    c.move(M(0,48),A(0)); c.move(I(0),D(0))
    c.move(D(7),D(1)); c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6)); c.call_os(LVO_GETRGB32)
    c.move(D(7),D(0)); c.raw('c0fc000c'); c.imm('add',8,D(0))
    c.move(A(4),D(1)); c.alu('add',D(1),0); c.move(D(0),A(0))
    c.move(D(7),D(0)); c.raw('c0fc0018'); c.imm('add',8,D(0))
    c.move(A(4),D(1)); c.alu('add',D(1),0); c.move(D(0),A(1))
    c.move(D(7),D(5)); c.raw('cafc0003')
    l('component_init')
    c.move(I(0),D(0)); c.move(POST(0),D(0),'b')
    c.quick(3,A(0)); c.shift(0,8,left=True); c.move(D(0),POST(1))
    c.move(I(0),D(1)); c.move(POST(2),D(1),'b')
    c.shift(1,8,left=True); c.alu('sub',D(0),1)
    c.raw('83c6'); c.move(D(1),POST(1),'w')
    c.quick(1,D(5),sub=True); b(6,'fade_component_init')
    c.move(D(7),D(0)); c.raw('c0fc0003')
    c.move(A(2),D(1)); c.alu('sub',D(0),1); c.move(D(1),A(2))
    l('frames_setup')
    c.move(D(6),D(4))
    l('frame_loop')
    c.move(M(5,STATE_PTR),A(6)); c.move(M(6,8),A(6))
    c.call_os(LVO_WAITTOF)
    c.move(A(4),A(1)); c.move(D(7),D(0)); c.raw('4840')
    c.move(D(0),POST(1)); c.imm('cmp',1,D(4)); b(7,'fade_exact_frame')
    c.move(D(7),D(0)); c.raw('c0fc0018'); c.imm('add',8,D(0))
    c.move(A(4),D(1)); c.alu('add',D(1),0); c.move(D(0),A(0))
    c.move(D(7),D(5)); c.raw('cafc0003')
    c.move(A(4),A(1)); c.quick(4,A(1))
    l('component_step')
    c.move(M(0),D(0)); c.move(I(0),D(1))
    c.move(M(0,4),D(1),'w'); c.raw('48c1')
    c.alu('add',D(1),0); c.move(D(0),M(0))
    c.quick(6,A(0)); c.shift(0,8); _expand_rgb(c)
    c.quick(1,D(5),sub=True); b(6,'fade_component_step')
    b(0,'fade_load_frame')
    l('exact_frame')
    c.move(A(2),A(0)); c.move(D(7),D(5)); c.raw('cafc0003')
    l('component_exact')
    c.move(I(0),D(0)); c.move(POST(0),D(0),'b'); _expand_rgb(c)
    c.quick(1,D(5),sub=True); b(6,'fade_component_exact')
    l('load_frame')
    c.move(I(0),M(1))
    c.move(M(5,STATE_PTR),A(0)); c.move(M(0),A(0))
    c.move(A(0),D(0)); c.imm('add',44,D(0)); c.move(D(0),A(0))
    c.move(A(4),A(1)); c.move(M(5,STATE_PTR),A(6))
    c.move(M(6,8),A(6)); c.call_os(LVO_LOADRGB32)
    c.quick(1,D(4),sub=True); b(6,'fade_frame_loop')
    c.move(A(4),A(1)); c.raw('2c780004'); c.call_os(LVO_FREEVEC)
    c.move(I(1),D(3)); b(0,'done')


def emit_bank_palette_apply(native_start: int, legacy_target: int):
    return _emit(False,native_start,legacy_target)


def emit_bank_palette_fade(native_start: int, legacy_target: int):
    return _emit(True,native_start,legacy_target)
