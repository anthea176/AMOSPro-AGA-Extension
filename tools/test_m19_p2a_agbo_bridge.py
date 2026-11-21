#!/usr/bin/env python3
"""Source-backed P1e/AGBO-to-P2a host adapter tests; NO native Gate A."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from struct import pack_into
import unittest

from m19_p0a_multi_bob_abk import (empty_bank, put_image, parse_payload,
                                  set_hotspot, delete_images, insert_blank_image)
from m19_p2a_bob_collision_model import Rect
from m19_p2a_agbo_bridge import (BankSnapshot, OBJECT, STAMP, LIMIT,
                                decode_objects, decode_limits, host_image,
                                collisions_from_snapshots)

SCREEN = Rect(0, 0, 320, 256)
HEAD = 0x00300000


def payload(width=8, height=1, image_id=1, visibility=None, depth=1):
    pixels = bytes(width * height)  # all palette index zero
    return put_image(empty_bank(), image_id, width, height, depth, pixels,
                     visibility=bytes(visibility) if visibility is not None else None)


def state(definitions, payloads):
    """Construct OFFLINE copies of 64 native object/stamp slots."""
    table = bytearray(OBJECT.size * 64)
    stamps = bytearray(STAMP.size * 64)
    snapshots = {bank: BankSnapshot(raw, 0x100000 + bank * 0x1000, HEAD)
                 for bank, raw in payloads.items()}
    for bob_id, bank_id, image_id, x, y, active in definitions:
        OBJECT.pack_into(table, (bob_id - 1) * OBJECT.size,
                         bank_id, image_id, x, y, active, 0)
        if bank_id in snapshots:
            snap = snapshots[bank_id]
            STAMP.pack_into(stamps, (bob_id - 1) * STAMP.size,
                            snap.payload_ptr, parse_payload(snap.payload).generation,
                            snap.bank_list_head, len(snap.payload))
    return bytes(table), bytes(stamps), snapshots


def query(defs, raw, **kwargs):
    table, stamps, banks = state(defs, {24: raw})
    return collisions_from_snapshots(table, stamps, banks, screen=SCREEN, **kwargs)


class AGBOBridgeP2aHost(unittest.TestCase):
    def test_01_native_layout_constants(self):
        from m19_p0e_object_table_emit import SLOT_BYTES, MAX_OBJECTS
        from m19_p0f_object_identity_emit import STAMP_BYTES
        from m19_p1d_limit_bob_emit import SLOT_BYTES as LIMIT_BYTES, SLOTS
        from m19_p0a_multi_bob_abk import HEADER, ENTRY
        self.assertEqual((SLOT_BYTES, MAX_OBJECTS, STAMP_BYTES), (24, 64, 16))
        self.assertEqual((LIMIT_BYTES, SLOTS, HEADER.size, ENTRY.size), (16, 65, 32, 40))

    def test_02_unmasked_palette_zero_is_opaque(self):
        raw = payload()
        self.assertEqual(query([(1,24,1,10,10,1),(2,24,1,10,10,1)], raw, mode='mask'), [(1,2)])

    def test_03_rectangle_vs_mask_false_positive(self):
        raw=payload(8,1,visibility=[1,0,0,0,0,0,0,0])
        defs=[(1,24,1,0,0,1),(2,24,1,1,0,1)]
        self.assertEqual(query(defs,raw,mode='rect'), [(1,2)])
        self.assertEqual(query(defs,raw,mode='mask'), [])

    def test_04_exact_shared_opaque_bit(self):
        raw=payload(8,1,visibility=[0,1,0,0,0,0,0,0])
        defs=[(1,24,1,0,0,1),(2,24,1,0,0,1)]
        self.assertEqual(query(defs,raw,mode='mask'), [(1,2)])

    def test_05_agbo_16bit_to_host_8bit_stride(self):
        for width in (1,7,8,9,15,16,17,31,32,33):
            visibility = [int((x+y*3)%5==1) for y in range(3) for x in range(width)]
            raw=payload(width,3,visibility=visibility)
            native=parse_payload(raw).image(1)
            model=host_image(native)
            with self.subTest(width=width):
                self.assertEqual(model.stride,(width+7)//8)
                for y in range(3):
                    for x in range(width):
                        self.assertEqual(model.opaque(x,y),native.visible(x,y))
                self.assertFalse(model.opaque(width,0))

    def test_06_hotspot_from_real_agbo_directory(self):
        raw=set_hotspot(payload(), 1, 4, -3)
        table,stamps,banks=state([(1,24,1,20,20,1),(2,24,1,16,20,1)],{24:raw})
        bobs=decode_objects(table,stamps,banks)
        self.assertEqual((bobs[0].origin_x,bobs[0].origin_y),(16,23))
        self.assertEqual(collisions_from_snapshots(table,stamps,banks,screen=SCREEN),[(1,2)])

    def test_07_off_bob_keeps_bindings_but_no_hit(self):
        raw=payload()
        defs=[(1,24,1,0,0,0),(2,24,1,0,0,1)]
        self.assertEqual(query(defs,raw),[])
        table,stamps,banks=state([(1,99,4096,-32000,32000,0)],{})
        self.assertEqual(decode_objects(table,stamps,banks),())

    def test_08_multi_bank_identity(self):
        raw=payload()
        defs=[(3,25,1,0,0,1),(1,24,1,0,0,1),(2,24,1,0,0,1)]
        table,stamps,banks=state(defs,{24:raw,25:raw})
        self.assertEqual(collisions_from_snapshots(table,stamps,banks,screen=SCREEN),
                         [(1,2),(1,3),(2,3)])

    def test_09_shared_image_identity_no_mutation(self):
        raw=payload(9,2,visibility=[1]*18)
        table,stamps,banks=state([(1,24,1,0,0,1),(2,24,1,0,0,1)],{24:raw})
        bobs=decode_objects(table,stamps,banks)
        self.assertIs(bobs[0].image,bobs[1].image)
        self.assertEqual(banks[24].payload,raw)
        with self.assertRaises(FrozenInstanceError):
            bobs[0].image.mask=b'changed'

    def test_10_global_local_limits(self):
        raw=payload(8,1)
        defs=[(1,24,1,0,0,1),(2,24,1,4,0,1)]
        limits=bytearray(LIMIT.size*65)
        LIMIT.pack_into(limits,0,4,0,8,1)
        self.assertEqual(query(defs,raw,limits=bytes(limits)),[(1,2)])
        LIMIT.pack_into(limits,1*LIMIT.size,0,0,4,1)
        self.assertEqual(query(defs,raw,limits=bytes(limits)),[])
        self.assertEqual(decode_limits(bytes(LIMIT.size*65))[0],None)

    def test_11_negative_onscreen_clipping(self):
        raw=payload(8,1)
        defs=[(1,24,1,-7,0,1),(2,24,1,0,0,1)]
        self.assertEqual(query(defs,raw),[(1,2)])
        defs[0]=(1,24,1,-8,0,1)
        self.assertEqual(query(defs,raw),[])

    def test_12_changed_generation_requires_new_stamp(self):
        raw=payload()
        table,stamps,banks=state([(1,24,1,0,0,1)],{24:raw})
        fresh=set_hotspot(raw,1,1,0)
        newer=dict(banks)
        newer[24]=BankSnapshot(fresh,banks[24].payload_ptr,banks[24].bank_list_head)
        with self.assertRaisesRegex(ValueError,'stale P0f stamp'):
            decode_objects(table,stamps,newer)
        stamp=bytearray(stamps)
        STAMP.pack_into(stamp,0,newer[24].payload_ptr,parse_payload(fresh).generation,
                        newer[24].bank_list_head,len(fresh))
        self.assertEqual(len(decode_objects(table,bytes(stamp),newer)),1)

    def test_13_stale_pointer_or_bank_head_rejected(self):
        raw=payload()
        table,stamps,banks=state([(1,24,1,0,0,1)],{24:raw})
        with self.assertRaisesRegex(ValueError,'stale P0f stamp'):
            decode_objects(table,stamps,{24:BankSnapshot(raw,0x120000,HEAD)})
        with self.assertRaisesRegex(ValueError,'stale P0f stamp'):
            decode_objects(table,stamps,{24:BankSnapshot(raw,banks[24].payload_ptr,HEAD+2)})

    def test_14_corrupted_native_bank_fails_before_collision(self):
        raw=payload(9,1,visibility=[1]*9)
        table,stamps,banks=state([(1,24,1,0,0,1)],{24:raw})
        bad=bytearray(raw)
        bad[-1] |= 1  # Must be zero padding after width 9.
        with self.assertRaises(ValueError):
            decode_objects(table,stamps,{24:BankSnapshot(bytes(bad),banks[24].payload_ptr,HEAD)})

    def test_15_deleted_image_reference_fails_closed(self):
        raw=payload()
        raw=insert_blank_image(raw,2,8,1,1)
        table,stamps,banks=state([(1,24,2,0,0,1)],{24:raw})
        removed=delete_images(raw,2,2)
        fresh=BankSnapshot(removed,banks[24].payload_ptr,HEAD)
        updated_stamp=bytearray(stamps)
        STAMP.pack_into(updated_stamp,0,fresh.payload_ptr,parse_payload(removed).generation,
                        HEAD,len(removed))
        with self.assertRaisesRegex(ValueError,'missing AGBO image'):
            decode_objects(table,bytes(updated_stamp),{24:fresh})
        off=bytearray(table)
        OBJECT.pack_into(off,0,24,2,0,0,0,0)
        self.assertEqual(decode_objects(bytes(off),bytes(updated_stamp),{24:fresh}),())

    def test_16_bad_object_flag_or_reserved_rejected(self):
        raw=payload()
        table,stamps,banks=state([(1,24,1,0,0,1)],{24:raw})
        for flag,reserved in ((2,0),(1,7)):
            broken=bytearray(table)
            OBJECT.pack_into(broken,0,24,1,0,0,flag,reserved)
            with self.assertRaisesRegex(ValueError,'corrupt P0e'):
                decode_objects(bytes(broken),stamps,banks)

    def test_17_out_of_range_signed_coordinate_refused(self):
        raw=payload()
        table,stamps,banks=state([(1,24,1,40000,0,1)],{24:raw})
        with self.assertRaisesRegex(ValueError,'invalid active'):
            decode_objects(table,stamps,banks)

    def test_18_missing_bank_fails(self):
        raw=payload()
        table,stamps,banks=state([(1,24,1,0,0,1)],{24:raw})
        with self.assertRaisesRegex(ValueError,'missing validated AGBO'):
            decode_objects(table,stamps,{})

    def test_19_exact_snapshot_lengths(self):
        raw=payload()
        table,stamps,banks=state([(1,24,1,0,0,1)],{24:raw})
        for objects,stamp in ((table[:-1],stamps),(table,stamps[:-1])):
            with self.assertRaisesRegex(ValueError,'exact 64'):
                decode_objects(objects,stamp,banks)

    def test_20_invalid_screen_or_depth(self):
        raw=payload(depth=2)
        table,stamps,banks=state([(1,24,1,0,0,1)],{24:raw})
        with self.assertRaisesRegex(ValueError,'screen depth'):
            decode_objects(table,stamps,banks,screen_depth=1)
        with self.assertRaisesRegex(ValueError,'logical AGA screen'):
            collisions_from_snapshots(table,stamps,banks,screen=Rect(1,0,320,256))

    def test_21_zero_or_negative_limit_extent_rejected(self):
        limits=bytearray(LIMIT.size*65)
        LIMIT.pack_into(limits,0,4,0,4,5)
        with self.assertRaisesRegex(ValueError,'noncanonical P1d'):
            decode_limits(bytes(limits))
        LIMIT.pack_into(limits,0,4,5,2,8)
        with self.assertRaises(ValueError):
            decode_limits(bytes(limits))
        with self.assertRaises(ValueError):
            decode_limits(bytes(limits[:-1]))

    def test_22_bank_snapshot_rejects_unaligned_pointer(self):
        with self.assertRaises(ValueError):
            BankSnapshot(payload(),3,HEAD)
        with self.assertRaises(ValueError):
            BankSnapshot(payload(),0x100000,0)


    def test_23_real_p1b_bank26_agbo_fixture(self):
        from hashlib import sha256
        from pathlib import Path
        from build_m19_p1b_hotspot_fixture import fixture, VISIBLE
        from m19_p0a_multi_bob_abk import parse_abk
        path=Path(__file__).resolve().parents[1]/'tests/current/M19_P1B_HOTSPOT_BANK26.abk'
        actual=path.read_bytes()
        self.assertEqual(len(actual),200)
        self.assertEqual(sha256(actual).hexdigest(),
                         '8dda90831afb616854c03094a34b728c6cb95bc4952c77af152d8cfe4a16f325')
        self.assertEqual(actual,fixture())
        bank_id,flags,bank=parse_abk(actual)
        self.assertEqual((bank_id,flags),(26,1))
        native=bank.image(1)
        self.assertEqual((native.width,native.height,native.hotspot_x,native.hotspot_y),(8,6,4,3))
        mask=host_image(native)
        for y in range(native.height):
            for x in range(native.width):
                self.assertEqual(mask.opaque(x,y),bool(VISIBLE[y*native.width+x]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
