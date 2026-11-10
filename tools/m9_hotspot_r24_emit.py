"""M9/R24: CPU-only, stateless rectangle hotspot hit test for AMOS 68000.

Aga Hotspot Hit(px,py,x,y,w,h) -> 1 or 0.
AMOS AP20 input: D3=h, (A3)+ = w,y,x,py,px (reverse parameter order).
AMOS output: D3=0/1, D2=0; A3 advances by exactly 20 bytes.

Points are screen-logical, so negative px/py are invalid (-1 indicates no
mouse position). Rectangle x/y may be negative and are not clamped.
Both bounds are start-inclusive / end-exclusive. 32-bit signed subtraction
with BVS guard prevents wrap-around false positives. No state, OS calls,
allocations, input events or screen changes.
"""
from m68k_emit import Code, D, POST, I


def emit_hotspot_hit():
    c = Code()
    c.raw("48e7efee")            # save D0/D1/D4-D7/A0-A2/A4-A6; NOT D2,D3,A3
    c.move(D(3), D(5))        # h, last arg delivered by AMOS
    for reg in (4, 3, 2, 1, 0):
        c.move(POST(3), D(reg))  # w,y,x,py,px

    c.tst(D(0)); c.branch(11, "miss")   # negative px = invalid
    c.tst(D(1)); c.branch(11, "miss")   # negative py = invalid
    c.tst(D(4)); c.branch(15, "miss")   # w <= 0
    c.tst(D(5)); c.branch(15, "miss")   # h <= 0

    c.alu("cmp", D(2), 0)            # px < x
    c.branch(13, "miss")              # signed BLT
    c.alu("sub", D(2), 0)            # relative x = px-x
    c.branch(9, "miss")               # signed BVS catches overflow
    c.alu("cmp", D(4), 0)            # relx >= width is outside
    c.branch(12, "miss")              # signed BGE

    c.alu("cmp", D(3), 1)            # py < y
    c.branch(13, "miss")
    c.alu("sub", D(3), 1)            # relative y = py-y
    c.branch(9, "miss")
    c.alu("cmp", D(5), 1)            # rely >= height
    c.branch(12, "miss")

    c.move(I(1), D(3))
    c.branch(0, "return")
    c.label("miss")
    c.move(I(0), D(3))
    c.label("return")
    c.raw("4cdf77f7")                # restore all except D2,D3,A3
    c.raw("74004e75")                # MOVEQ #0,D2; RTS
    result = c.out()
    assert result and len(result) % 2 == 0
    return result, c.labels
