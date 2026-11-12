"""R54: bank-number convenience wrappers, reusing R53/R46 native routines.

No legacy token or bytecode is changed: entry 57 feeds entry 55 (Image Draw)
and entry 58 feeds entry 49 (Font Bank Select) in the SAME compiler-safe
monolith. PC-relative BSR.W is explicitly resolved from native segment offsets.
No new allocation, bank mutation or second rendering engine.
"""
from __future__ import annotations
from struct import pack_into
from m68k_emit import Code,D,A,M,POST,I
from amos_main_abi import main_index,rjsr

IDX_GETADR=main_index("Bnk.GetAdr")
assert IDX_GETADR==797
MARKER=rjsr(IDX_GETADR)
PRESERVE="48e7efee"
RESTORE="4cdf77f7"
RET_INTEGER="74004e75"

def _patch_delegate(code, labels, native_start, native_target):
    """Patch one BSR.W inside the same relocatable native monolith."""
    off=labels["delegate"]
    out=bytearray(code)
    assert out[off:off+4]==b"\x61\x00\x00\x00"
    relative=native_target-(native_start+off+4)
    assert -32768<=relative<=32767, ("out of BSR.W range",relative)
    pack_into(">h",out,off+2,relative)
    assert out[off:off+2]==b"\x61\x00"
    assert out.count(MARKER)==1
    return bytes(out),dict(labels,delegate_displacement=relative,
         native_start=native_start,native_target=native_target)

def emit_bank_image_draw(native_start,native_target):
    """_OK=Aga Bank Image Draw(Bank,X,Y,Mode).

    D3=Mode, A3 pops Y,X,Bank. Synthesize exactly the original
    (Start,Length,X,Y,Mode) calling convention and invoke native entry 55.
    """
    c=Code()
    L=c.label;B=c.branch
    c.raw(PRESERVE)
    c.raw("4fefffd0")             # LEA -48(SP),SP
    c.move(A(7),A(2))            # local frame
    c.move(D(3),M(2,0))         # Mode
    for offset in (4,8,12):     # Y,X,Bank from (A3)+
        c.move(POST(3),D(7)); c.move(D(7),M(2,offset))
    c.move(A(3),M(2,16))        # final caller A3, consumed 3 parameters
    c.move(M(2,12),D(0))
    c.imm("cmp",5,D(0)); B(5,"fail")
    c.imm("cmp",65535,D(0)); B(2,"fail")
    c.raw(MARKER.hex())         # validated source-derived Bnk.GetAdr
    c.move(A(0),D(0)); c.tst(D(0)); B(7,"fail")
    c.move(A(0),M(2,32))        # synthesized Start(Bank)
    c.move(M(0,-20),D(1))
    c.imm("cmp",16,D(1)); B(5,"fail")
    c.imm("sub",16,D(1))        # synthesized Length(Bank)
    c.move(D(1),M(2,28))
    c.move(M(2,4),D(0)); c.move(D(0),M(2,20))  # Y
    c.move(M(2,8),D(0)); c.move(D(0),M(2,24))  # X
    c.move(M(2,0),D(3))         # restore Mode
    c.raw("47ea0014")           # LEA 20(A2),A3 => [Y,X,Length,Start]
    L("delegate")
    c.raw("61000000")           # BSR.W native R53 Image Draw entry 55
    B(0,"done")
    L("fail")
    c.move(I(0),D(3))
    L("done")
    c.move(M(2,16),A(3))        # restore caller argument pointer
    c.raw("4fef0030")           # LEA +48(SP),SP
    c.raw(RESTORE)
    c.raw(RET_INTEGER)
    return _patch_delegate(c.out(),c.labels,native_start,native_target)

def emit_bank_font_select(native_start,native_target):
    """_OK=Aga Bank Font Select(Bank).

    D3=Bank, A3 has no stacked args. Convert to the original
    Font Bank Select(Start(Bank),Length(Bank)) convention.
    """
    c=Code()
    L=c.label;B=c.branch
    c.raw(PRESERVE)
    c.raw("4fefffe0")           # LEA -32(SP),SP
    c.move(A(7),A(2))
    c.move(D(3),M(2,0))         # bank number
    c.move(A(3),M(2,4))         # caller A3 remains unchanged
    c.move(D(3),D(0))
    c.imm("cmp",5,D(0)); B(5,"fail")
    c.imm("cmp",65535,D(0)); B(2,"fail")
    c.raw(MARKER.hex())
    c.move(A(0),D(0)); c.tst(D(0)); B(7,"fail")
    c.move(A(0),M(2,8))         # synthetic Start
    c.move(M(0,-20),D(3))
    c.imm("cmp",16,D(3)); B(5,"fail")
    c.imm("sub",16,D(3))        # D3=synthetic Length
    c.raw("47ea0008")           # LEA 8(A2),A3 -> [Start]
    L("delegate")
    c.raw("61000000")           # BSR.W native R38 Font Bank Select entry 49
    B(0,"done")
    L("fail")
    c.move(I(0),D(3))
    L("done")
    c.move(M(2,4),A(3))
    c.raw("4fef0020")           # LEA +32(SP),SP
    c.raw(RESTORE)
    c.raw(RET_INTEGER)
    return _patch_delegate(c.out(),c.labels,native_start,native_target)
