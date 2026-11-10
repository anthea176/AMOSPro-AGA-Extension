"""M10/R25: stateless, overflow-safe signed 32-bit AABB overlap for AMOS 68000.

Aga Rect Overlap(ax,ay,aw,ah,bx,by,bw,bh) -> 1 iff rectangles overlap
with a POSITIVE area, otherwise 0. Touching edges/corners are NOT overlap.
Negative origins are valid. Width/height <= 0 are always rejected.

AP20 ABI for eight parameters: D3=bh, then 7 longs on (A3)+ in
reverse call order: bw,by,bx,ah,aw,ay,ax. A3 must advance by 28 bytes.
D3 returns 0/1 and D2=0. No OS, window, hardware, memory allocation, or
persistent state. Other registers and hardware SP are preserved.

On each axis, after ordering rectangle starts, compare the
nonnegative start difference to the earlier rectangle's extent. An
overflowed signed subtraction cannot overlap because 32-bit positive
lengths are <= INT32_MAX; reject BVS explicitly. Avoid x+width overflow.
"""
from m68k_emit import Code, D, POST, I

ENTRY_ARG_COUNT = 8
A3_CONSUMED_BYTES = (ENTRY_ARG_COUNT - 1) * 4


def emit_rect_overlap():
    c = Code()
    c.raw("48e7efee")            # ABI: save D0,D1,D4..D7,A0..A2,A4..A6
    c.move(D(3), D(7))         # B height is final AMOS arg
    # A3 stack order: bw,by,bx,ah,aw,ay,ax
    for r in (6, 5, 4, 3, 2, 1, 0):
        c.move(POST(3), D(r))

    for r in (2, 3, 6, 7):
        c.tst(D(r))
        c.branch(15, "miss")  # BLE: zero or negative dimension

    # X axis: A starts D0 with width D2; B starts D4 with width D6
    c.alu("cmp", D(4), 0)     # CMP.L D4,D0 = ax - bx
    c.branch(13, "ax_before_bx")  # BLT (signed, V-aware)
    # ax >= bx: distance to bx is < B width for area overlap
    c.alu("sub", D(4), 0)
    c.branch(9, "miss")      # BVS: reject overflowed distance
    c.alu("cmp", D(6), 0)
    c.branch(12, "miss")     # BGE: exclude exact boundary
    c.branch(0, "x_ok")
    c.label("ax_before_bx")
    # bx > ax: distance to ax is < A width
    c.alu("sub", D(0), 4)
    c.branch(9, "miss")
    c.alu("cmp", D(2), 4)
    c.branch(12, "miss")
    c.label("x_ok")

    # Y axis: A starts D1 with height D3; B starts D5 with height D7
    c.alu("cmp", D(5), 1)
    c.branch(13, "ay_before_by")
    c.alu("sub", D(5), 1)
    c.branch(9, "miss")
    c.alu("cmp", D(7), 1)
    c.branch(12, "miss")
    c.branch(0, "hit")
    c.label("ay_before_by")
    c.alu("sub", D(1), 5)
    c.branch(9, "miss")
    c.alu("cmp", D(3), 5)
    c.branch(12, "miss")

    c.label("hit")
    c.move(I(1), D(3))
    c.branch(0, "return")
    c.label("miss")
    c.move(I(0), D(3))
    c.label("return")
    c.raw("4cdf77f7")        # restore all except D2,D3,A3
    c.raw("74004e75")        # MOVEQ #0,D2; RTS
    raw = c.out()
    assert raw and not (len(raw) & 1)
    return raw, c.labels
