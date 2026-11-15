"""M19/P0a: native 68000/020 emitter for non-destructive AMOS DATA-bank commit.

SOURCE AUTHORITY (READ ONLY): marc365/AMOS-Professional-365 +B.s (Lst.Cree,
Lst.Del, Bnk.Change), +Lib.s (Bnk.GetAdr/Bnk.Reserve), +Equ.s (Cur_Banks
at A5+$05ea). API table indices from R88 amos_main_abi.py pinned declarations.

PRIVATE, not an AP20 entry: input D3=bank (5..65535), A0=PREVALIDATED AGBO
payload in live memory, D1=exact byte count. Result D3=1 success / 0 fail,
D2=0 integer. Repackaging/capture/masks still need their own native callers.

No Bnk.Reserve: it destroys an existing bank BEFORE allocating its replacement.
Stage an AMOS list node in a frame-local detached head via Lst.Cree, fill it,
revalidate source identity, splice via ONE longword write, notify Bnk.Change,
then free the detached old node via Lst.Del. Never allocate a second AMOS
number. On allocation/preflight failure, Lst.Del frees ONLY the stage node.

Requires caller to STRICTLY parse the complete candidate AGBO directory/masks
before invoking; this primitive checks only the container/header boundaries.
Not a Gate A CPU pass until executed by a 68k runner and AP20 integration.
"""
from __future__ import annotations

from m68k_emit import Code, D, A, M, POST, I
from amos_main_abi import main_index, rjsr

CUR_BANKS_A5 = 0x05EA  # marc365 +Equ.s line 1327 (verified RsReset count)
MAX_BANK_BYTES = 0x01000000
HEADER = 32
ENTRY = 40
BANK_NAME = b"AGABOBS "
MEMF_PUBLIC_CLEAR = 0x00010001
IDX = {key: main_index(key) for key in (
    "Bnk.GetAdr", "Bnk.Change", "Lst.Cree", "Lst.Del")}
assert IDX == {"Bnk.GetAdr": 797, "Bnk.Change": 819,
               "Lst.Cree": 91, "Lst.Del": 93}, "R88 ABI mismatch"
MARKERS = {name: rjsr(index) for name, index in IDX.items()}

F = dict(bank=0, source=4, size=8, old_data=12, old_node=16,
         new_node=20, temp_head=24, list_head=28, link_ref=32,
         scan_guard=36, rest=40)
FRAME = 80


def emit_transaction() -> tuple[bytes, dict[str, int]]:
    """Produce one private routine, relocatable as a whole with R88 AP20 V2."""
    c = Code()
    B, L = c.branch, c.label

    def st(register, key):
        c.move(register, M(2, F[key]))

    def ld(key, register):
        c.move(M(2, F[key]), register)

    def addr_frame(dst, key):
        """LEA displacement(A2),Adst; no synthesized ADDI to address regs."""
        c.word(0x41C0 | (dst << 9) | 0x28 | 2)
        c.word(F[key])

    def jsr(name):
        c.raw(MARKERS[name].hex())

    def reject_if_odd(register):
        c.move(register, D(0))
        c.imm("and", 1, D(0))
        B(6, "abort")

    # Preserve R88 native AP20 registers; D3 result and D2 type are outputs.
    c.raw("48e7efee")
    c.raw("4fefffb0")        # LEA -80(SP),SP
    c.move(A(7), A(2))
    st(D(3), "bank")
    st(A(0), "source")
    st(D(1), "size")
    for f in ("old_data", "old_node", "new_node", "temp_head", "list_head", "link_ref"):
        c.move(I(0), M(2, F[f]))
    c.move(I(0), D(3))

    # Input/bounds must be checked before touching AMOS bank lists.
    ld("bank", D(0))
    c.imm("cmp", 5, D(0)); B(5, "abort")
    c.imm("cmp", 65535, D(0)); B(2, "abort")
    ld("size", D(0))
    c.imm("cmp", HEADER, D(0)); B(5, "abort")
    c.imm("cmp", MAX_BANK_BYTES, D(0)); B(2, "abort")
    c.move(D(0), D(1)); c.imm("and", 1, D(1)); B(6, "abort")
    ld("source", D(0))
    c.imm("cmp", 24, D(0)); B(3, "abort")
    reject_if_odd(D(0))
    # The complete directory/padding validation belongs to the caller, but
    # reject inconsistent top-level AGBO payloads before allocating.
    ld("source", A(0))
    c.move(M(0,0), D(0)); c.imm("cmp", 0x4147424F, D(0)); B(6, "abort")
    c.move(I(0), D(0)); c.move(M(0,4), D(0), "w")
    c.imm("cmp", 1, D(0)); B(6, "abort")
    c.tst(M(0,6), "w"); B(6, "abort")
    c.move(I(0), D(0)); c.move(M(0,10), D(0), "w")
    c.imm("cmp", ENTRY, D(0)); B(6, "abort")
    c.move(M(0,12), D(0)); c.imm("cmp", HEADER, D(0)); B(6, "abort")
    c.move(M(0,20), D(0))
    c.alu("cmp", M(2, F["size"]), 0); B(6, "abort")
    c.move(M(0,24), D(0)); c.tst(D(0)); B(7, "abort")
    c.tst(M(0,28)); B(6, "abort")
    c.move(I(0), D(0)); c.move(M(0,8), D(0), "w")
    c.imm("cmp", 4096, D(0)); B(2, "abort")
    c.raw("c0fc0028")  # MULU.W #40,D0, full 32-bit result (68000)
    c.imm("add", HEADER, D(0))
    ld("source", A(0))
    c.alu("cmp", M(0,16), 0); B(6, "abort")
    ld("size", D(0)); c.imm("add", 15, D(0))
    ld("source", D(1)); c.alu("add", D(0), 1); B(5, "abort")

    # Read runtime list-head through the A5 offset derived from TRUE 365 +Equ.
    c.move(M(5,CUR_BANKS_A5), A(0))
    c.move(A(0), D(0)); c.tst(D(0)); B(7, "abort")
    st(A(0), "list_head")
    reject_if_odd(D(0))

    # Lookup old number; if present, reject any foreign bank before allocation.
    ld("bank", D(0)); jsr("Bnk.GetAdr")
    c.move(A(0), D(4)); c.tst(D(4)); B(7, "old_missing")
    c.imm("cmp", 24, D(4)); B(3, "abort")
    reject_if_odd(D(4))
    st(D(4), "old_data")
    c.imm("sub", 24, D(4)); st(D(4), "old_node")
    c.move(D(4), A(4))
    c.move(M(4,8), D(0)); ld("bank", D(1)); c.alu("cmp", D(1), 0); B(6, "abort")
    c.move(I(0), D(0)); c.move(M(4,12), D(0), "w")
    c.tst(D(0)); B(7, "old_flags_ok")
    c.imm("and", 0xfffd, D(0), "w")
    c.imm("cmp", 1, D(0), "w"); B(6, "abort")
    L("old_flags_ok")
    c.move(M(4,16), D(0)); c.imm("cmp", 0x41474142, D(0)); B(6, "abort")
    c.move(M(4,20), D(0)); c.imm("cmp", 0x4f425320, D(0)); B(6, "abort")
    c.move(M(4,4), D(0)); c.imm("cmp", 16+HEADER, D(0)); B(5, "abort")
    c.imm("cmp", 16+MAX_BANK_BYTES, D(0)); B(2, "abort")
    c.imm("sub", 16, D(0))
    ld("old_data", A(0))
    c.move(M(0,0), D(1)); c.imm("cmp", 0x4147424F, D(1)); B(6, "abort")
    c.alu("cmp", M(0,20), 0); B(6, "abort")
    B(0, "stage")
    L("old_missing")
    # The old bank identity is zero; any reallocation/creation during staging
    # will be detected by the second Bnk.GetAdr immediately before commit.
    L("stage")

    # Lst.Cree(A0=&private_head,D0=payload+16,D1=MEMF_PUBLIC|CLEAR):
    # allocates [next.l,size.l,bank_no.l,flags.w,spare.w,name[8],payload...].
    addr_frame(0, "temp_head")
    ld("size", D(0)); c.imm("add", 16, D(0))
    c.move(I(MEMF_PUBLIC_CLEAR), D(1)); jsr("Lst.Cree")
    c.move(A(1), D(4)); c.tst(D(0)); B(7, "abort")
    c.tst(D(4)); B(7, "abort")
    st(D(4), "new_node")
    c.move(D(4), A(4))
    ld("bank", D(0)); c.move(D(0), M(4,8))
    c.move(I(1,"w"), M(4,12),"w")
    c.move(I(0,"w"), M(4,14),"w")
    c.move(I(0x41474142), M(4,16))
    c.move(I(0x4f425320), M(4,20))
    ld("source", A(0))
    c.word(0x43ec); c.word(24)  # LEA 24(A4),A1
    ld("size", D(6)); c.move(D(6), D(7))
    c.shift(6,2,left=False)
    L("copy_longs")
    c.move(POST(0), POST(1))
    c.quick(1, D(6), sub=True); B(6, "copy_longs")
    c.imm("and", 2, D(7))
    c.tst(D(7)); B(7, "copy_done")
    c.move(POST(0), POST(1), "w")
    L("copy_done")

    # Revalidate old bank identity AFTER any allocation/memory flush.
    ld("bank", D(0)); jsr("Bnk.GetAdr")
    c.move(A(0), D(0)); c.alu("cmp", M(2,F["old_data"]),0); B(6,"abort")
    c.move(M(5,CUR_BANKS_A5),D(0))
    c.alu("cmp",M(2,F["list_head"]),0); B(6,"abort")

    # Revalidate old link in real list; scan bounded even on corrupt cycles.
    ld("list_head", A(0)); st(A(0), "link_ref")
    ld("old_node", D(5)); c.tst(D(5)); B(7, "insert_new")
    c.move(I(65535), D(6))
    L("seek_previous_link")
    ld("link_ref", A(0)); c.move(M(0), D(0))
    c.alu("cmp", D(5), 0); B(7, "replace_old")
    c.tst(D(0)); B(7, "abort")
    st(D(0), "link_ref")
    c.quick(1, D(6), sub=True); B(6, "seek_previous_link")
    B(0, "abort")

    L("replace_old")
    ld("old_node", A(0)); c.move(M(0), D(0))
    ld("new_node", A(1)); c.move(D(0), M(1))
    ld("link_ref", A(0)); c.move(A(1), M(0))  # SINGLE PUBLISH WRITE
    ld("old_node", A(0)); c.move(I(0), M(0))
    st(A(0), "temp_head")  # detached old node waits for Bnk.Change
    B(0, "notify")

    L("insert_new")
    ld("list_head", A(0)); c.move(M(0), D(0))
    ld("new_node", A(1)); c.move(D(0), M(1))
    c.move(A(1), M(0))  # SINGLE PUBLISH WRITE, no old node
    c.move(I(0), M(2, F["temp_head"]))

    L("notify")
    jsr("Bnk.Change")  # extension callbacks while old payload is STILL ALIVE
    ld("old_node", D(0)); c.tst(D(0)); B(7, "success")
    addr_frame(0, "temp_head")
    ld("old_node", A(1)); jsr("Lst.Del")  # free ONLY unlinked old node
    L("success")
    c.move(I(1), D(3)); B(0, "return")

    # Failed after staging: private allocation can be freed independently.
    L("abort")
    ld("new_node", D(0)); c.tst(D(0)); B(7, "return")
    addr_frame(0, "temp_head")
    ld("new_node", A(1)); jsr("Lst.Del")
    L("return")
    c.raw("4fef0050")  # LEA +80(SP),SP
    c.raw("4cdf77f7")  # restore ABI preserved set
    c.raw("74004e75")  # D2=0 integer, RTS; D3=1/0

    binary = c.out()
    assert len(binary) % 2 == 0 and len(binary) < 65534
    assert binary.count(MARKERS["Bnk.GetAdr"]) == 2
    assert binary.count(MARKERS["Bnk.Change"]) == 1
    assert binary.count(MARKERS["Lst.Cree"]) == 1
    assert binary.count(MARKERS["Lst.Del"]) == 2
    return binary, c.labels


if __name__ == "__main__":
    from hashlib import sha256
    raw, labels = emit_transaction()
    print("M19 P0a private native AMOS bank transaction", len(raw),
          sha256(raw).hexdigest(), len(labels), "NOT A GATE A PASS")
