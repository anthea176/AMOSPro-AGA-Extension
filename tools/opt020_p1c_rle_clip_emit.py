"""OPT020 P1c native RLE row pointer decoder and geometry clipping.

Two independent stand-alone Motorola 68EC020/68020-compatible routines.
They have NO AP20/AMOS entrypoint and write NO bitmap pixels themselves.

decode_row():
 A0 = row start, A1 = row end exclusive, A2 = pointer table capacity groups*4
 D0.l = number of 16-pixel groups (1..256), D1.l=group bytes (2..18 even)
 Returns D3=1 on valid, 0 otherwise. On success A0=end, A2 advanced.
 A3/D5/A5 preserved; D0/D1/D2/D4/D6/D7/A4 scratch.
 It DOES NOT validate AGAPIC global header, pad bits, plane depth or
 row offset table; caller must validate before any painting.

clip_x():
 D0=group_x, D1=source_crop_x, D2=crop_right_exclusive,
 D3=destination_origin_x, D4=destination_bitmap_width,
 D5=source_image_width. All LONG.
 Returns D6/D7 inclusive/exclusive bit indices [0,16] inside the group;
 0/0 means none. D0..D4 preserved; D5 scratch.

clip_y():
 D0=source_y, D1=crop_y, D2=dest_origin_y, D3=bitmap_height
 Returns D6=1 if visible else 0, D7=dest_y, D0..D3 preserved.
"""
from __future__ import annotations

from m68k_emit import A, D, I, POST, Code


def emit_rle_row_020() -> bytes:
    """Bounded native literal/repeat AGAPIC RLE; never paints during decode."""
    c = Code()
    c.imm("cmp", 1, D(0))        # group count 1..256
    c.branch(13, "fail")         # BLT
    c.imm("cmp", 256, D(0))
    c.branch(14, "fail")         # BGT
    c.imm("cmp", 2, D(1))        # 2..18 even bytes/group
    c.branch(13, "fail")
    c.imm("cmp", 18, D(1))
    c.branch(14, "fail")
    c.word(0x0801)              # BTST #0,D1 (immediate bit)
    c.word(0)
    c.branch(6, "fail")
    c.move(D(0), D(2))           # remaining group count
    c.move(D(1), D(6))           # source group byte stride

    c.label("packet")
    c.move(A(0), D(0))
    c.move(A(1), D(1))
    c.alu("cmp", D(1), 0)        # A0 >= row end => no control byte
    c.branch(4, "fail")         # BCC unsigned
    c.word(0x7800)              # MOVEQ #0,D4
    c.move(POST(0), D(4), "b")  # control byte
    c.move(D(4), D(7), "w")
    c.imm("and", 127, D(7), "w")
    c.quick(1, D(7), size="w")  # packet count (1..128)
    c.alu("cmp", D(2), 7, "w")   # count > remaining?
    c.branch(2, "fail")         # BHI (unsigned)
    c.alu("sub", D(7), 2, "w")   # remaining -= count
    c.imm("and", 128, D(4), "w")
    c.branch(6, "repeat")

    c.move(D(7), D(4), "w")
    c.word(0xc8c6)              # MULU.W D6,D4; bounded <=2304
    c.move(A(0), D(0))
    c.alu("add", D(4), 0)
    c.branch(5, "fail")         # BCS (32-bit wrap)
    c.move(A(1), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(2, "fail")         # required literal bytes > row end
    c.label("literal_loop")
    c.move(A(0), POST(2))       # emit address of next literal group
    c.word(0xd1c6)              # ADDA.L D6,A0
    c.quick(1, D(7), sub=True, size="w")
    c.branch(6, "literal_loop")
    c.branch(0, "next_packet")

    c.label("repeat")
    c.move(A(0), D(0))
    c.alu("add", D(6), 0)
    c.branch(5, "fail")
    c.move(A(1), D(1))
    c.alu("cmp", D(1), 0)
    c.branch(2, "fail")         # missing repeated group bytes
    c.move(A(0), A(4))          # A4 points to one repeated group
    c.word(0xd1c6)              # ADDA.L D6,A0 (only once)
    c.label("repeat_loop")
    c.move(A(4), POST(2))
    c.quick(1, D(7), sub=True, size="w")
    c.branch(6, "repeat_loop")

    c.label("next_packet")
    c.tst(D(2), "w")
    c.branch(6, "packet")
    c.move(A(0), D(0))
    c.move(A(1), D(1))
    c.alu("cmp", D(1), 0)        # must consume EXACTLY row end
    c.branch(6, "fail")
    c.word(0x7601)              # MOVEQ #1,D3
    c.word(0x4e75)
    c.label("fail")
    c.word(0x7600)              # MOVEQ #0,D3
    c.word(0x4e75)
    return c.out()


def emit_clip_x_020() -> bytes:
    """Native signed-long horizontal crop/viewport intersection."""
    c = Code()
    c.move(D(0), D(6))           # left = group_x
    c.alu("cmp", D(1), 6)        # left>=crop_x?
    c.branch(12, "left_crop_done")
    c.move(D(1), D(6))
    c.label("left_crop_done")
    c.move(D(1), D(7))
    c.alu("sub", D(3), 7)        # source_x >= crop_x - dst_x
    c.alu("cmp", D(7), 6)
    c.branch(12, "left_screen_done")
    c.move(D(7), D(6))
    c.label("left_screen_done")

    c.move(D(0), D(7))
    c.imm("add", 16, D(7))      # right = group_x +16
    c.alu("cmp", D(2), 7)
    c.branch(15, "right_crop_done")
    c.move(D(2), D(7))
    c.label("right_crop_done")
    c.alu("cmp", D(5), 7)
    c.branch(15, "right_image_done")
    c.move(D(5), D(7))
    c.label("right_image_done")
    c.move(D(1), D(5))
    c.alu("add", D(4), 5)
    c.alu("sub", D(3), 5)        # screen right mapped back to source
    c.alu("cmp", D(5), 7)
    c.branch(15, "right_screen_done")
    c.move(D(5), D(7))
    c.label("right_screen_done")
    c.alu("cmp", D(6), 7)
    c.branch(15, "empty")       # right <= left
    c.alu("sub", D(0), 6)
    c.alu("sub", D(0), 7)
    c.word(0x4e75)
    c.label("empty")
    c.word(0x7c00)              # MOVEQ #0,D6
    c.word(0x7e00)              # MOVEQ #0,D7
    c.word(0x4e75)
    return c.out()


def emit_clip_y_020() -> bytes:
    """Native signed-long vertical crop/viewport intersection."""
    c = Code()
    c.move(D(0), D(7))
    c.alu("sub", D(1), 7)
    c.alu("add", D(2), 7)       # dest_y = source_y-crop_y+origin_y
    c.tst(D(7))
    c.branch(11, "invisible")   # BMI
    c.alu("cmp", D(3), 7)
    c.branch(12, "invisible")   # dest_y >= bitmap height
    c.word(0x7c01)              # MOVEQ #1,D6
    c.word(0x4e75)
    c.label("invisible")
    c.word(0x7c00)              # MOVEQ #0,D6
    c.word(0x4e75)
    return c.out()


if __name__ == "__main__":
    import hashlib
    for name, fn in (("RLE_ROW", emit_rle_row_020),
                     ("CLIP_X", emit_clip_x_020),
                     ("CLIP_Y", emit_clip_y_020)):
        code = fn()
        print(name, len(code), hashlib.sha256(code).hexdigest())
