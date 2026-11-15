"""M19 P2.3: compact fourth AP20 BOBS engine, using tested source emitters.

The two image painters are emitted from their existing AGAPIC v2 and
FICON8 implementations. They are copied inside the same Compiler V2
BOBS unit because cross-unit PC-relative calls are not relocation-safe.
No private AGA core or historical R84 unit is patched.
"""
from __future__ import annotations

from struct import pack_into, unpack_from
from m68k_emit import Code, D, A, M, POST, I
from amos_main_abi import main_index, rjsr
from m16_agapic_v2_draw_emit import emit_image_draw_v2
from m16_bank_api_r54_emit import emit_bank_image_draw
from m18_ficon_ap20_emit import emit_ficon_ap20

GETADR = rjsr(main_index("Bnk.GetAdr"))
assert main_index("Bnk.GetAdr") == 797
STATE_PTR = 0x1C8
LVO_TYPEOFMEM = -534
FRAME = 96
MAX_BOBS = 256
STRIDE = 20
HEADER = 16
MAGIC = 0x424F4231   # BOB1, big-endian
F = dict(count=0, descriptor_bank=4, caller_a3=8, base=12,
         size=16, first=20, y=24, x=28, arg3=32, arg4=36)


def emit_bob_batch():
    """Return (native bytes, labels), including copied native image backends.

    D3=Count; A3 points to one bank number. All descriptors are in ascending
    drawing order (Z is resolved by BASIC). Returns D3=1/0 and D2=0.
    On a source-image error, rendering stops and returns 0. Any earlier
    writes remain in the *inactive* back buffer: BASIC MUST NOT swap it.
    """
    c = Code()
    B, L = c.branch, c.label
    def load(field, reg):
        c.move(M(2, F[field]), reg)
    def store(reg, field):
        c.move(reg, M(2, F[field]))
    def word0(off, reg=0):
        c.move(I(0), D(reg))
        c.move(M(0, off), D(reg), "w")
    def need_mem_from(reg):
        c.move(reg, A(1))
        c.raw("2c780004")             # ExecBase
        c.call_os(LVO_TYPEOFMEM)
        c.tst(D(0))
        B(7, "reject")

    c.raw("48e7efee")                 # Standard AGA AP20 save, except D2/D3/A3
    c.raw("4fefffa0")                 # LEA -96(SP),SP
    c.move(A(7), A(2))
    store(D(3), "count")
    c.move(POST(3), D(7))
    store(D(7), "descriptor_bank")
    store(A(3), "caller_a3")
    c.move(I(0), D(3))                # failure by default

    # Refuse MC68000 before any 020 operations, AMOS bank calls or pixels.
    c.raw("20780004")
    c.move(A(0), D(0))
    c.tst(D(0))
    B(7, "reject")
    c.move(M(0, 0x128), D(0), "w")
    c.word(0x0800)
    c.word(1)                       # BTST #AFF_68020,D0
    B(7, "reject")

    load("count", D(0))
    c.tst(D(0))
    B(15, "reject")
    c.imm("cmp", MAX_BOBS, D(0))
    B(14, "reject")
    load("descriptor_bank", D(0))
    c.imm("cmp", 5, D(0))
    B(5, "reject")
    c.imm("cmp", 65535, D(0))
    B(2, "reject")
    c.raw(GETADR.hex())
    c.move(A(0), D(5))
    c.imm("cmp", 24, D(5))
    B(3, "reject")
    c.move(D(5), D(0))
    c.imm("and", 1, D(0))
    B(6, "reject")
    store(D(5), "base")
    need_mem_from(D(5))
    load("base", D(0))
    c.imm("sub", 24, D(0))
    need_mem_from(D(0))

    # Verify an exact AMOS DATA payload size before reading the first record.
    load("count", D(0))
    c.move(I(STRIDE), D(1))
    c.word(0xC0C1)                  # MULU.W D1,D0
    c.imm("add", HEADER, D(0))
    store(D(0), "size")
    load("base", A(0))
    c.move(M(0, -20), D(0))
    load("size", D(1))
    c.imm("add", 16, D(1))           # AMOS bank header length convention
    c.alu("cmp", D(1), 0)
    B(6, "reject")
    c.move(M(0, -16), D(0))
    load("descriptor_bank", D(1))
    c.alu("cmp", D(1), 0)
    B(6, "reject")
    word0(-12)
    c.tst(D(0))
    B(7, "bank_flags_ok")          # reloaded AMOS DATA may report flags=0
    c.imm("and", 0xFFFD, D(0), "w")
    c.imm("cmp", 1, D(0))
    B(6, "reject")
    L("bank_flags_ok")
    load("base", D(0))
    load("size", D(1))
    c.alu("add", D(1), 0)
    B(5, "reject")
    c.quick(1, D(0), sub=True)
    need_mem_from(D(0))

    load("base", A(0))
    c.move(M(0, 0), D(0))
    c.imm("cmp", MAGIC, D(0))
    B(6, "reject")
    word0(4)
    c.imm("cmp", 1, D(0))
    B(6, "reject")
    word0(6)
    c.imm("cmp", STRIDE, D(0))
    B(6, "reject")
    c.move(M(0, 8), D(0))
    load("count", D(1))
    c.alu("cmp", D(1), 0)
    B(6, "reject")
    c.tst(M(0, 12))
    B(6, "reject")
    c.move(A(0), A(4))
    c.raw("49ec0010")                 # LEA 16(A4),A4
    store(A(4), "first")
    load("count", D(6))

    # Complete descriptor preflight before the first pixel write.
    L("preflight")
    c.move(I(0), D(0))
    c.move(M(4, 16), D(0), "w")   # kind: 1=AGAPIC, 2=FICON8
    c.imm("cmp", 1, D(0))
    B(7, "agapic_valid")
    c.imm("cmp", 2, D(0))
    B(6, "reject")
    c.move(M(4, 12), D(0))       # FICON8 ID
    c.tst(D(0))
    B(15, "reject")
    c.imm("cmp", 4096, D(0))
    B(14, "reject")
    B(0, "kind_ok")
    L("agapic_valid")
    c.tst(M(4, 12))              # AGAPIC ID must be zero
    B(6, "reject")
    L("kind_ok")
    c.move(I(0), D(0))
    c.move(M(4, 18), D(0), "w")   # mode: opaque/masked
    c.imm("cmp", 1, D(0))
    B(2, "reject")
    c.move(M(4, 8), D(0))        # source bank number
    c.imm("cmp", 5, D(0))
    B(5, "reject")
    c.imm("cmp", 65535, D(0))
    B(2, "reject")
    for off in (0, 4):           # signed Y and X
        c.move(M(4, off), D(0))
        c.imm("cmp", -32768, D(0))
        B(13, "reject")
        c.imm("cmp", 32767, D(0))
        B(14, "reject")
    c.raw("49ec0014")            # LEA 20(A4),A4
    c.quick(1, D(6), sub=True)
    B(6, "preflight")

    # The native painters consume A3 = [Y, X, Bank] or [Y, X, ID, Bank].
    # They independently validate each source and the inactive Safe bitmap.
    load("first", A(4))
    load("count", D(6))
    L("draw_next")
    c.move(M(4, 0), D(0))
    store(D(0), "y")
    c.move(M(4, 4), D(0))
    store(D(0), "x")
    c.move(I(0), D(3))
    c.move(M(4, 18), D(3), "w")
    c.move(I(0), D(0))
    c.move(M(4, 16), D(0), "w")
    c.imm("cmp", 1, D(0))
    B(6, "draw_ficon")
    c.move(M(4, 8), D(0))       # AGAPIC: third argument is Bank
    store(D(0), "arg3")
    c.raw("47ea0018")           # LEA 24(A2),A3
    B(1, "backend_agapic")      # BSR.W to private cloned R84 wrapper
    B(0, "after_draw")
    L("draw_ficon")
    c.move(M(4, 12), D(0))      # FICON8: third argument is IconID
    store(D(0), "arg3")
    c.move(M(4, 8), D(0))
    store(D(0), "arg4")
    c.raw("47ea0018")
    B(1, "backend_ficon")
    L("after_draw")
    c.imm("cmp", 1, D(3))
    B(6, "reject")
    c.raw("49ec0014")           # next descriptor
    c.quick(1, D(6), sub=True)
    B(6, "draw_next")
    c.move(I(1), D(3))
    B(0, "finish")
    L("reject")
    c.move(I(0), D(3))
    L("finish")
    load("caller_a3", A(3))
    c.raw("4fef0060")           # frame cleanup
    c.raw("4cdf77f7")           # restored registers, except D2/D3/A3
    c.raw("74004e75")           # D2=0, RTS

    # Source-backed painters: emit exact existing code; only the wrapper's
    # audited intra-unit BSR.W is relinked to this unit's Image Draw entry.
    image, _ = emit_image_draw_v2()
    ficon, _ = emit_ficon_ap20(opt020=True)
    L("backend_image")
    c.raw(image.hex())
    L("backend_agapic")
    wrapper, _ = emit_bank_image_draw(
        c.labels["backend_agapic"], c.labels["backend_image"])
    wrapper = bytearray(wrapper)
    site = 122                        # native_relative_links.py audited site
    assert unpack_from(">H", wrapper, site)[0] == 0x6100
    delta = c.labels["backend_image"] - (
        c.labels["backend_agapic"] + site + 2)
    assert -32768 <= delta <= 32767
    pack_into(">h", wrapper, site + 2, delta)
    assert (c.labels["backend_agapic"] + site + 2 +
            unpack_from(">h", wrapper, site + 2)[0]
            == c.labels["backend_image"])
    c.raw(bytes(wrapper).hex())
    L("backend_ficon")
    c.raw(ficon.hex())
    native = c.out()
    assert len(native) % 2 == 0
    assert native.count(GETADR) == 3   # descriptor + wrapper + FICON
    assert native[c.labels["backend_image"]:].startswith(image)
    return native, dict(c.labels, image_bytes=len(image),
                        wrapper_bytes=len(wrapper), ficon_bytes=len(ficon))
