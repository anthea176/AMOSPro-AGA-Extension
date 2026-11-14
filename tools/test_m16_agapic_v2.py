#!/usr/bin/env python3
"""AGAPIC v2 P0 host test with legacy v1 codec and unified palette selector."""
from __future__ import annotations
import struct
from m16_agapic import pack_image as pack_v1, parse_payload as parse_v1, unpack_image, make_abk as make_v1_abk
from m16_agapic_v2 import (
    pack_image_v2, parse_payload_any, parse_abk_any, make_abk_v2,
    compatible_screen, select_bank_palette,
)

MODE = 0x00021000


def fail(fn):
    try: fn()
    except ValueError: return
    raise AssertionError('expected rejection')


def main() -> None:
    pairs = 0
    for width in (1,15,16,17,19,31,32):
        for height in (1,2,4):
            for depth in (1,2,4,8):
                pixels = bytes((i*7 + (i>>3)*3) % (1 << depth) for i in range(width*height))
                mask = bytes((i*5) % 3 != 0 for i in range(width*height))
                palette = bytes((i*13 + 7) & 0xff for i in range(3 * (1 << depth)))
                for m in (None, mask):
                    v1 = pack_v1(width,height,depth,pixels,m)
                    v2 = pack_image_v2(width,height,depth,pixels,palette,MODE,m)
                    a = parse_payload_any(v1)
                    b = parse_payload_any(v2)
                    assert a.original == v1 and b.original == v2
                    assert b.palette == palette and b.mode_id == MODE
                    assert b.image.raw[b.image.offsets[0]:] == parse_v1(v1).raw[parse_v1(v1).offsets[0]:]
                    assert unpack_image(a.image) == (pixels,m)
                    assert unpack_image(b.image) == (pixels,m)
                    assert compatible_screen(a,screen_depth=depth,screen_mode_id=0)
                    assert compatible_screen(b,screen_depth=depth,screen_mode_id=MODE)
                    assert not compatible_screen(b,screen_depth=depth,screen_mode_id=MODE+1)
                    assert not compatible_screen(b,screen_depth=depth+1,screen_mode_id=MODE)
                    assert select_bank_palette(v2,0,screen_depth=depth,screen_mode_id=MODE) == palette
                    fail(lambda:select_bank_palette(v2,1,screen_depth=depth,screen_mode_id=MODE))
                    fail(lambda:select_bank_palette(v2,0,screen_depth=depth,screen_mode_id=MODE+1))
                    fail(lambda:select_bank_palette(v1,0,screen_depth=depth,screen_mode_id=MODE))
                    wrapped = make_abk_v2(10,v2)
                    assert parse_abk_any(wrapped)[2] == b
                    assert parse_abk_any(make_v1_abk(10,v1))[2] == a
                    pairs += 1
    # V2 strict header/mode/palette and RLE corruption negatives.
    p = pack_image_v2(17,3,4,bytes(i & 15 for i in range(17))*3,bytes(48),MODE)
    def corrupt(off, width, value):
        bb = bytearray(p)
        bb[off:off+width] = value.to_bytes(width,'big')
        fail(lambda:parse_payload_any(bytes(bb)))
    for off,w,v in ((6,2,3),(8,2,0),(32,4,0),(32,4,0xffffffff),
                    (36,2,5),(38,2,2),(40,4,0),(44,4,0),(48,4,0),
                    (52,4,1),(56,4,1),(60,4,1),(20,4,32),(24,4,0),
                    (28,4,0),(10,2,2)):
        corrupt(off,w,v)
    fail(lambda:pack_image_v2(17,3,4,bytes(i & 15 for i in range(17))*3,bytes(15),MODE))
    fail(lambda:pack_image_v2(17,3,4,bytes(i & 15 for i in range(17))*3,bytes(48),0))
    fail(lambda:parse_payload_any(p[:-1]))
    fail(lambda:parse_payload_any(p+b'\0'))
    # Valid AGAPAL v1 with two slots, first count 4, second empty.
    n = 2
    agapal = bytearray(16 + 776*n)
    struct.pack_into('>6sHHHI',agapal,0,b'AGAPAL',1,n,0,0)
    for i in range(n):
        struct.pack_into('>IHH',agapal,16+8*i,16+8*n+768*i,4 if i==0 else 0,0)
    rgb = bytes(range(12))
    agapal[16+8*n:16+8*n+len(rgb)] = rgb
    assert select_bank_palette(bytes(agapal),0,screen_depth=4) == rgb
    fail(lambda:select_bank_palette(bytes(agapal),1,screen_depth=4))
    fail(lambda:select_bank_palette(bytes(agapal),0,screen_depth=1))
    print('AGAPIC V2 HOST TEST PASS:',pairs,'v1/v2 roundtrips + palette dispatch + 23 negative checks')


if __name__ == '__main__':
    main()
