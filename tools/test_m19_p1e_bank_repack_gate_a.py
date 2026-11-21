#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Executed MC68020 payload repacker vs the independent Python AGBO model."""
from random import Random
from struct import pack, pack_into

from unicorn import UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, Uc
from unicorn.m68k_const import UC_CPU_M68K_M68020, UC_M68K_REG_PC, UC_M68K_REG_SR

from m19_p0a_capture_transaction import BackBitmap, HostBobBanks
from m19_p0a_multi_bob_abk import (
    delete_images, empty_bank, insert_blank_image, make_abk, parse_abk,
    parse_payload, put_image, set_hotspot,
)
from m19_p1e_bank_repack_emit import emit_bank_repack
from test_m5_generic import DR, AR

SOURCE, TARGET, DESCRIPTOR, STACK, STOP = 0x200000, 0x500000, 0x70000, 0x7f000, 0x80000
CANARY = bytes([0xaa]) * 16


class Runner:
    def __init__(self, pc):
        self.uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0, 0x800000)
        binary, labels = emit_bank_repack()
        self.uc.mem_write(pc, binary)
        self.entry = pc + labels['bank_repack']

    def execute(self, payload, arguments, capacity=0, target=TARGET):
        uc = self.uc
        uc.mem_write(SOURCE, payload)
        uc.mem_write(DESCRIPTOR, pack('>9I', SOURCE, len(payload), target, capacity,
                                      *(a & 0xffffffff for a in arguments)))
        for i, r in enumerate(DR + AR[:7]):
            uc.reg_write(r, 0x55550000 + i)
        uc.reg_write(AR[0], DESCRIPTOR)
        saved = {r: uc.reg_read(r) for r in DR + AR[:7] if r not in (DR[2], DR[3])}
        uc.reg_write(UC_M68K_REG_SR, 0x2000)
        uc.reg_write(AR[7], STACK)
        uc.mem_write(STACK, pack('>I', STOP))
        uc.emu_start(self.entry, STOP, count=20_000_000)
        assert uc.reg_read(UC_M68K_REG_PC) == STOP
        assert uc.reg_read(AR[7]) == STACK + 4 and uc.reg_read(DR[2]) == 0
        assert all(uc.reg_read(r) == val for r, val in saved.items())
        assert uc.mem_read(SOURCE, len(payload)) == payload
        return uc.reg_read(DR[3])

    def compare(self, payload, args):
        a, b, w, h, depth = args
        try:
            expected = delete_images(payload, a, b) if b else insert_blank_image(payload, a, w, h, depth)
        except ValueError:
            self.uc.mem_write(TARGET, CANARY)
            assert self.execute(payload, args, target=0) == 0
            assert self.execute(payload, args, 16) == 0
            assert self.uc.mem_read(TARGET, 16) == CANARY
            return
        size = len(expected)
        self.uc.mem_write(TARGET - 16, CANARY + b'\xaa' * size + CANARY)
        assert self.execute(payload, args, target=0) == size
        assert self.execute(payload, args, size - 1) == 0
        assert self.uc.mem_read(TARGET, size) == b'\xaa' * size
        assert self.execute(payload, args, size, target=SOURCE+2) == 0
        assert self.execute(payload, args, size) == size
        assert self.uc.mem_read(TARGET, size) == expected
        assert self.uc.mem_read(TARGET - 16, 16) == CANARY
        assert self.uc.mem_read(TARGET + size, 16) == CANARY


def host_transaction(payload):
    permitted = True

    def allocation(_size):
        return permitted

    banks = HostBobBanks(allocation)
    banks.load(make_abk(10, payload))
    banks.select(11)
    previous = banks.save(10)
    permitted = False
    for edit, args in ((banks.delete_images, (10, 2, 8)),
                       (banks.insert_blank_image, (10, 3, 17, 4, 8))):
        try:
            edit(*args)
        except MemoryError:
            pass
        else:
            raise AssertionError('edit must refuse the private allocation failure')
        assert banks.save(10) == previous and banks.current_number() == 11
    permitted = True
    banks.delete_images(10, 2, 8)
    original = parse_payload(payload)
    edited = parse_payload(banks.payload(10))
    assert edited.images == tuple(img for img in original.images if not 2 <= img.image_id <= 8)
    assert edited.generation == original.generation + 1
    assert banks.current_number() == 11
    banks.select(10)
    banks.delete_images(10, 1, 4096)
    assert len(banks.payload(10)) == 32
    banks.insert_blank_image(10, 4096, 17, 4, 8)
    img = parse_payload(banks.payload(10)).image(4096)
    assert img.mask == bytes(img.plane_bytes) and img.planes == bytes(8 * img.plane_bytes)
    assert (img.hotspot_x, img.hotspot_y) == (0, 0)
    assert parse_abk(banks.save(10))[2].image(4096) == img
    bitmap = BackBitmap(1, 1, 1, 2, (b'\x80\x00',), safe=True)
    banks.capture(4096, bitmap, 0, 0, 0, 0)
    replacement = parse_payload(banks.payload(10)).image(4096)
    assert replacement.colour(0, 0) == 1 and replacement.mask is None


def main():
    image = empty_bank()
    for ident in (1, 2, 8, 16, 4096):
        pixels = bytes((i * ident + 7) & 7 for i in range(17 * 4))
        mask = None if ident % 2 else bytes(i % 2 for i in range(len(pixels)))
        image = put_image(image, ident, 17, 4, 3, pixels, visibility=mask)
    image = set_hotspot(image, 16, -8, 9)
    exhausted = bytearray(image)
    pack_into('>I', exhausted, 24, 0xffffffff)
    rng = Random(19)
    cases = [
        (image, (a, b, 0, 0, 0)) for a, b in
        ((1, 1), (8, 16), (2, 8), (4096, 4096), (1, 4096), (20, 30), (9, 8), (0, 1), (1, 4097))
    ]
    cases += [(image, (i, 0, 19, 5, 8)) for i in (3, 2, 9, 18, 4095, 4096, 4097, -1)]
    cases += [(empty_bank(), (1, 1, 0, 0, 0)), (empty_bank(), (1, 0, 1, 1, 1)),
              (bytes(exhausted), (1, 1, 0, 0, 0)), (bytes(exhausted), (3, 0, 1, 1, 1)),
              (image, (3, 0, 0, 1, 1)), (image, (3, 0, 1, 1, 9)),
              (image, (3, 0, 4096, 4096, 8)), (image, (3, 0, 0xffffffff, 2, 1)),
              (image, (3, 0, 1024, 1024, 1))]
    for _ in range(40):
        if rng.randrange(2):
            first, last = sorted(rng.sample(range(1, 40), 2))
            cases.append((image, (first, last, 0, 0, 0)))
        else:
            cases.append((image, (rng.randrange(1, 40), 0, rng.randrange(1, 34),
                                  rng.randrange(1, 12), rng.randrange(1, 9))))
    for pc in (0x100000, 0x380000):
        runner = Runner(pc)
        for payload, args in cases:
            try:
                runner.compare(payload, args)
            except AssertionError as exc:
                raise AssertionError((hex(pc), args)) from exc
    host_transaction(image)
    print('P1e private AGBO repacker MC68020 PASS:', len(cases) * 2, 'scenarios on two placements')
    print('P1e host explicit edit rollback and ABK Save/Load PASS')


if __name__ == '__main__':
    main()
