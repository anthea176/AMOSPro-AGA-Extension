#!/usr/bin/env python3
"""P0a host-only ABK/planar contract checks; not WinUAE or AMOS Compiler."""
from __future__ import annotations

from dataclasses import replace
from random import Random
from struct import pack_into
import unittest

from m19_p0a_multi_bob_abk import (
    ABK, ENTRY, HEADER, BANK_NAME, BobImage, MAX_BANK_BYTES,
    empty_bank, make_abk, make_mask, no_mask, pack_pixels,
    parse_abk, parse_payload, put_image,
)


class MultiBobP0a(unittest.TestCase):
    def test_empty_bank_and_save_load_envelope(self):
        payload = empty_bank()
        self.assertEqual(len(payload), 32)
        self.assertEqual(parse_payload(payload).generation, 1)
        self.assertEqual(parse_payload(payload).images, ())
        for n in (5, 10, 65535):
            for prefer_chip in (False, True):
                file = make_abk(n, payload, chip_preferred=prefer_chip)
                self.assertEqual(file[:4], b"AmBk")
                self.assertEqual(file[12:20], BANK_NAME)
                number, flags, bank = parse_abk(file)
                self.assertEqual((number, flags, bank.raw),
                                 (n, 3 if prefer_chip else 1, payload))

    def test_native_amos_save_length_bit31_real_m19_geometry(self):
        # Reproduce the observed AMOS Runtime Save: 3 images, generation 5,
        # 1,032 payload bytes, 1,052 file bytes, size word 0x80000410.
        payload = put_image(empty_bank(), 1, 17, 15, 8, bytes([255]) * (17 * 15))
        payload = put_image(payload, 3, 37, 8, 8, bytes([37]) * (37 * 8))
        payload = put_image(payload, 2, 31, 16, 8, bytes([127]) * (31 * 16))
        payload = put_image(payload, 2, 1, 1, 8, bytes([127]))
        self.assertEqual((len(payload), parse_payload(payload).generation), (1032, 5))
        file = make_abk(24, payload)
        self.assertEqual(len(file), 1052)
        native = bytearray(file)
        pack_into(">I", native, 8, 0x80000000 | (len(file) - 12))
        self.assertEqual(native[8:12], bytes.fromhex("80000410"))
        number, flags, bank = parse_abk(bytes(native))
        self.assertEqual((number, flags, bank.raw), (24, 1, payload))
        self.assertEqual([im.image_id for im in bank.images], [1, 2, 3])
        self.assertEqual([bank.image(i).colour(0, 0) for i in (1, 2, 3)],
                         [255, 127, 37])
        # The host-produced unflagged AmBk envelope remains supported.
        self.assertEqual(parse_abk(file)[2].raw, payload)
        # Ignore ONLY the high bit; wrong low bits or other high bits fail.
        for bad_length in (0x80000412, 0x00000412, 0x40000410, 0x80000000):
            damaged = bytearray(native)
            pack_into(">I", damaged, 8, bad_length)
            with self.assertRaises(ValueError):
                parse_abk(bytes(damaged))
        with self.assertRaises(ValueError):
            parse_abk(bytes(native) + bytes([0]))

    def test_plane_major_one_pixel_and_zero_opaque(self):
        img = pack_pixels(1, 1, 1, 8, b"\x89")
        self.assertEqual(img.stride, 2)
        self.assertEqual(img.planes, b"\x80\x00" + b"\x00\x00"*2 +
                         b"\x80\x00" + b"\x00\x00"*3 + b"\x80\x00")
        self.assertEqual(img.colour(0, 0), 0x89)
        self.assertTrue(img.visible(0, 0))
        with self.assertRaises(IndexError):
            img.colour(1, 0)

    def test_many_widths_depths_and_mask_independence(self):
        rng = Random(0x19A88)
        for depth in (1, 4, 8):
            for w in (1, 17, 31, 32, 37):
                h = 3
                pixels = bytes(rng.randrange(1 << depth) for _ in range(w*h))
                pixels = bytes([0, (1 << depth) - 1]) + pixels[2:]
                visibility = bytes(1 if i % 4 else 0 for i in range(w*h))
                visibility = bytes([1, 0]) + visibility[2:]
                img = pack_pixels(21, w, h, depth, pixels, visibility=visibility)
                self.assertTrue(img.visible(0, 0))   # colour zero OPAQUE
                if w > 1:
                    self.assertFalse(img.visible(1, 0))  # nonzero TRANSPARENT
                self.assertEqual(img.stride, ((w+15)//16)*2)
                self.assertEqual(len(img.mask), img.stride*h)
                for y in range(h):
                    for x in range(w):
                        self.assertEqual(img.colour(x,y), pixels[y*w+x])
                        self.assertEqual(img.visible(x,y), bool(visibility[y*w+x]))
                payload = put_image(empty_bank(), 21, w, h, depth,
                                    pixels, visibility=visibility)
                self.assertEqual(parse_payload(payload).image(21), img)
                n, f, parsed = parse_abk(make_abk(10, payload))
                self.assertEqual((n, f), (10, 1))
                self.assertEqual(parsed.image(21), img)

    def test_multiple_images_replace_preserves_others_and_order(self):
        a = put_image(empty_bank(), 23, 17, 2, 4, bytes(i%16 for i in range(17))*2)
        b = put_image(a, 1, 32, 1, 8, bytes(range(32)))
        c = put_image(b, 4096, 37, 1, 8, bytes(range(37)))
        original = parse_payload(c)
        self.assertEqual([im.image_id for im in original.images], [1, 23, 4096])
        out = put_image(c, 23, 1, 1, 8, b"\xab")
        after = parse_payload(out)
        self.assertEqual(after.generation, original.generation + 1)
        self.assertEqual(after.image(23).colour(0,0), 0xab)
        self.assertEqual(after.image(1), original.image(1))
        self.assertEqual(after.image(4096), original.image(4096))
        self.assertEqual(parse_abk(make_abk(12, out))[2], after)
        self.assertEqual(parse_payload(c), original)  # source unchanged

    def test_make_and_no_mask_distinct_from_colour_zero(self):
        pixels = bytes([0, 1, 0, 2, 3, 0, 1, 0, 3])
        start = put_image(empty_bank(), 1, 9, 1, 4, pixels)
        masked = parse_payload(make_mask(start, 1, 1)).image(1)
        self.assertTrue(masked.visible(0, 0))
        self.assertFalse(masked.visible(1, 0))
        self.assertTrue(masked.visible(2, 0))
        removed = no_mask(make_mask(start, 1, 0), 1)
        self.assertIsNone(parse_payload(removed).image(1).mask)
        self.assertTrue(parse_payload(removed).image(1).visible(0,0))
        self.assertEqual(no_mask(removed,1), removed)

    def test_invalid_inputs_leave_original_unchanged(self):
        p = put_image(empty_bank(), 1, 1, 1, 1, b"\x01")
        pristine = bytes(p)
        wrongs = [
            (0,1,1,b"\0"), (4097,1,1,b"\0"),
            (2,0,1,b""), (2,1,9,b"\0"),
        ]
        for identifier, width, depth, pixels in wrongs:
            with self.assertRaises(ValueError):
                put_image(p, identifier, width, 1, depth, pixels)
        with self.assertRaises(ValueError):
            make_mask(p, 1, 2)
        with self.assertRaises(KeyError):
            no_mask(p, 2)
        with self.assertRaises(ValueError):
            make_abk(4, p)
        self.assertEqual(p, pristine)

    def test_corrupt_offsets_flags_header_and_padding(self):
        base = put_image(empty_bank(), 1, 17, 2, 4,
                         bytes([0,1,2,3]*8+[4,5]))
        def altered(offset, fmt, value):
            bad=bytearray(base)
            pack_into(fmt, bad, offset, value)
            return bytes(bad)
        # header invalid total, unknown flags, directory stride
        for sample in (altered(20, ">I",len(base)-2),
                       altered(6, ">H",1),
                       altered(10,">H",41),
                       altered(16,">I",31),
                       altered(24,">I",0),
                       altered(32+12,">I",0),
                       altered(32+16,">I",0),
                       altered(32+10,">H",2),
                       base+b"\0"):
            with self.assertRaises(ValueError):
                parse_payload(sample)
        # last row, last group, unused bit: expected zero
        bad=bytearray(base)
        bad[-1] |= 1
        with self.assertRaises(ValueError):
            parse_payload(bytes(bad))
        # a tampered AMOS file header cannot change bank ID / format
        abk=bytearray(make_abk(10,base))
        abk[3]=ord("X")
        with self.assertRaises(ValueError):
            parse_abk(bytes(abk))

    def test_dir_order_duplicate_overlapping_offsets_and_mask_bits(self):
        base=put_image(empty_bank(), 12, 17, 2, 8, bytes(range(34)))
        base=put_image(base, 24, 31, 1, 8, bytes(range(31)),
                       visibility=bytes(1 if i%2 else 0 for i in range(31)))
        self.assertEqual([im.image_id for im in parse_payload(base).images],[12,24])
        def wrong(offset, fmt, value):
            buf=bytearray(base)
            pack_into(fmt,buf,offset,value)
            return bytes(buf)
        for invalid in (
            wrong(HEADER.size+ENTRY.size,">H",12),
            wrong(HEADER.size+ENTRY.size+12,">I",32),
            wrong(HEADER.size+ENTRY.size+20,">I",50000),
            wrong(HEADER.size+ENTRY.size+24,">I",0),
            wrong(HEADER.size+ENTRY.size+32,">I",1),
        ):
            with self.assertRaises(ValueError):
                parse_payload(invalid)
        self.assertEqual(parse_abk(make_abk(500,base))[2].raw,base)

    def test_bank_mutation_is_transactional_and_generation_bound(self):
        initial=put_image(empty_bank(), 5, 4, 1, 8,bytes([0,4,8,16]))
        info=parse_payload(initial)
        self.assertEqual(info.generation,2)
        image=info.image(5)
        self.assertEqual([image.colour(x,0) for x in range(4)],[0,4,8,16])
        for update in (
            lambda: put_image(initial,7,31,1,4,bytes([255]*31)),
            lambda: make_mask(initial,5,256),
            lambda: no_mask(initial,456),
        ):
            with self.assertRaises((ValueError,KeyError)):
                update()
            self.assertEqual(parse_payload(initial),info)
        exhausted=bytearray(initial)
        pack_into(">I",exhausted,24,0xffffffff)
        with self.assertRaises(ValueError):
            put_image(bytes(exhausted),7,1,1,1,b"\x00")
        with self.assertRaises(ValueError):
            make_mask(bytes(exhausted),5,0)

    def test_invalid_amos_bank_header_and_chip_flag_not_residency(self):
        bank=make_abk(10,empty_bank(),chip_preferred=True)
        self.assertEqual(parse_abk(bank)[1],3)
        for field,fmt,value in ((6,">H",2),(8,">I",0),(12,">I",0)):
            bad=bytearray(bank)
            pack_into(fmt,bad,field,value)
            with self.assertRaises(ValueError):
                parse_abk(bytes(bad))

    def test_reject_malformed_in_memory_image(self):
        image=pack_pixels(1, 17, 2, 8, bytes(range(34)))
        with self.assertRaises(ValueError):
            # corrupt unused bits in last 16-bit word
            p=bytearray(image.planes)
            p[-1] |= 1
            from m19_p0a_multi_bob_abk import _build
            _build((replace(image,planes=bytes(p)),),2)
        with self.assertRaises(ValueError):
            parse_payload(bytes(MAX_BANK_BYTES + 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
