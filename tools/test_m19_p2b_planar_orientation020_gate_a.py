#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Execute P2b plane preparation and feed its output to the P2a mask kernel."""

from dataclasses import replace
from hashlib import sha256
from random import Random
from struct import pack
import unittest

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn import Uc, UC_ARCH_M68K, UC_HOOK_CODE, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import UC_CPU_M68K_M68020, UC_M68K_REG_SR

from m19_p0a_multi_bob_abk import pack_pixels
from m19_p2a_bob_collision_model import Rect
from m19_p2a_collision020_emit import emit_collision020
from m19_p2b_bob_orientation_model import OrientedImage
from m19_p2b_planar_orientation020_emit import emit_planar_orientation020
from test_m19_p2a_collision020_gate_a import (
    NativePair, REG_A, REG_D, STOP, STACK, run_pair, u32,
)

SOURCE, DESTINATION = 0x100010, 0x300010
EXEC_BASE = 0x700000
GUARD = bytes.fromhex("ba37821a") * 4


def planar_bytes(image):
    return image.planes + (image.mask or b"")


def oracle(image, mode):
    view = OrientedImage(image, horizontal=bool(mode & 1), vertical=bool(mode & 2))
    locations = [(x, y) for y in range(image.height) for x in range(image.width)]
    return pack_pixels(image.image_id, image.width, image.height, image.depth,
                       bytes(view.colour(x, y) for x, y in locations),
                       visibility=(bytes(view.visible(x, y) for x, y in locations)
                                   if image.mask is not None else None))


class NativeMaterializer:
    def __init__(self, code, address):
        self.address = address
        self.uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68020)
        self.uc.mem_map(0, 0x800000)
        self.uc.mem_write(address, code)
        self.uc.mem_write(STOP, b"\x4e\x71")

    def run(self, image, mode, *, overrides=None, source=SOURCE,
            destination=DESTINATION, expect=1, chip_entry=None):
        uc = self.uc
        raw = planar_bytes(image)
        output_fill = b"\xa5" * len(raw)
        src_block = GUARD + raw + GUARD
        dst_block = GUARD + output_fill + GUARD
        uc.mem_write(source - len(GUARD), src_block)
        uc.mem_write(destination - len(GUARD), dst_block)
        uc.mem_write(STACK, pack(">I", STOP) + GUARD)
        uc.mem_write(STACK - 192, GUARD)
        uc.reg_write(UC_M68K_REG_SR, 0x2000)
        uc.reg_write(REG_A[7], STACK)
        registers = dict(zip(REG_A[:7], (source, destination, 0x710200, 0x710300,
                                         0x710400, 0x710500, 0x710600)))
        registers.update(zip(REG_D, (image.width, image.height, 0x1234, 0x4321,
                                     image.depth + (image.mask is not None), mode,
                                     len(raw), len(raw))))
        if chip_entry is not None:
            registers[REG_A[6]] = EXEC_BASE
            registers[REG_A[1]] = 0
            registers[REG_D[7]] = 0
        registers.update(overrides or {})
        for register, value in registers.items():
            uc.reg_write(register, u32(value))

        uc.emu_start(self.address + (chip_entry or 0), STOP, count=max(10_000, 50 * len(raw)))
        assert uc.reg_read(REG_A[7]) == STACK + 4
        assert uc.reg_read(REG_D[2]) == 0
        assert uc.reg_read(REG_D[3]) == expect
        outputs = set(REG_D[2:4])
        if chip_entry is not None:
            outputs.update((REG_A[1], REG_D[7]))
            assert uc.reg_read(REG_A[1]) == (destination if expect else 0)
            assert uc.reg_read(REG_D[7]) == (len(raw) if expect else 0)
        for register, value in registers.items():
            if register not in outputs:
                assert uc.reg_read(register) == u32(value), ("register clobbered", register)
        assert bytes(uc.mem_read(STACK + 4, len(GUARD))) == GUARD
        assert bytes(uc.mem_read(STACK - 192, len(GUARD))) == GUARD
        assert bytes(uc.mem_read(source - len(GUARD), len(src_block))) == src_block
        dst = bytes(uc.mem_read(destination - len(GUARD), len(dst_block)))
        assert dst[:len(GUARD)] == dst[-len(GUARD):] == GUARD
        if not expect:
            assert dst == dst_block
        return dst[len(GUARD):-len(GUARD)]


    def mock_exec(self, *, allocation, memory_types):
        """Return the exact Exec calls made by the preparation entry."""
        uc = self.uc
        calls = []
        memory_types = iter(memory_types)
        for lvo in (-198, -210, -534):
            uc.mem_write(EXEC_BASE + lvo, b"\x4e\x75")

        def service(uc, address, instruction_size, user_data):
            lvo = address - EXEC_BASE
            value = uc.reg_read(REG_D[0])
            flags = uc.reg_read(REG_D[1])
            pointer = uc.reg_read(REG_A[1])
            if lvo == -198:
                calls.append(("AllocMem", value, flags))
                result = allocation
            elif lvo == -534:
                calls.append(("TypeOfMem", pointer))
                result = next(memory_types)
            else:
                assert lvo == -210
                calls.append(("FreeMem", value, pointer))
                result = 0
            for register in (REG_D[1], REG_A[0], REG_A[1]):
                uc.reg_write(register, 0x55aa55aa)
            uc.reg_write(REG_D[0], result)

        hook = uc.hook_add(UC_HOOK_CODE, service, begin=EXEC_BASE - 534, end=EXEC_BASE - 198)
        return hook, calls


class PlanarOrientationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code, cls.labels = emit_planar_orientation020()
        cls.machines = [NativeMaterializer(cls.code, address) for address in (0x10000, 0x25000)]

    def test_determinism_decoder_and_entry(self):
        self.assertEqual(emit_planar_orientation020(), (self.code, self.labels))
        self.assertEqual(self.labels["p2b_planar_orientation_entry"], 0)
        decoder = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
        instructions = list(decoder.disasm(self.code, 0x10000))
        self.assertEqual(sum(i.size for i in instructions), len(self.code))
        self.assertFalse(any(i.mnemonic.startswith("dc.") for i in instructions))
        self.assertTrue(any(i.mnemonic == "mulu.l" for i in instructions))
        print("P2B_PLANAR_NATIVE_SHA", sha256(self.code).hexdigest(), "BYTES", len(self.code))

    def test_word_boundaries_colours_and_independent_masks(self):
        random = Random(68020)
        for machine in self.machines:
            for width in (1, 7, 15, 16, 17, 31, 32, 37, 4096):
                for depth, masked in ((1, False), (4, True), (8, True)):
                    height = 3 if width != 1 else 1
                    size = width * height
                    image = pack_pixels(1, width, height, depth,
                                        bytes(random.randrange(1 << depth) for _ in range(size)),
                                        visibility=(bytes(random.randrange(2) for _ in range(size))
                                                    if masked else None))
                    for mode in range(4):
                        with self.subTest(width=width, depth=depth, mode=mode, address=machine.address):
                            self.assertEqual(machine.run(image, mode), planar_bytes(oracle(image, mode)))

    def test_plane_offsets_exceed_a_word(self):
        width, height, depth = 4096, 129, 2
        stride = 512
        plane_size = stride * height
        image = pack_pixels(1, width, 1, depth, b"\x00" * width)
        plane_a = b"\x80" + bytes(plane_size - 1)
        plane_b = bytes(plane_size - 1) + b"\x01"
        source = replace(image, height=height, planes=plane_a + plane_b)
        expected = plane_b + plane_a
        for machine in self.machines:
            self.assertEqual(machine.run(source, 3), expected)

    def test_refusals_happen_before_any_write(self):
        image = pack_pixels(1, 17, 2, 1, bytes(34))
        size = len(planar_bytes(image))
        rejected = (
            {REG_D[0]: 0}, {REG_D[0]: -1}, {REG_D[0]: 4097}, {REG_D[1]: 0},
            {REG_D[1]: 4097}, {REG_D[0]: 4096, REG_D[1]: 1025},
            {REG_D[4]: 0}, {REG_D[4]: 10}, {REG_D[5]: 4}, {REG_D[5]: -1},
            {REG_D[6]: size - 1}, {REG_D[7]: size - 1},
            {REG_A[0]: 0}, {REG_A[1]: 0},
            {REG_A[0]: SOURCE + 1}, {REG_A[1]: DESTINATION + 1},
            {REG_A[0]: 0xfffffffc}, {REG_A[1]: 0xfffffffc},
            {REG_A[1]: SOURCE}, {REG_A[1]: SOURCE + 2},
            {REG_A[0]: DESTINATION + 2},
        )
        for machine in self.machines:
            for registers in rejected:
                with self.subTest(registers=registers, address=machine.address):
                    machine.run(image, 1, overrides=registers, expect=0)

    def test_variant_mask_consumed_by_real_p2a_collision(self):
        image = replace(pack_pixels(1, 17, 2, 1, b"\x00" * 34,
                                    visibility=b"\x01" + b"\x00" * 33), hotspot_x=8)
        target = pack_pixels(2, 1, 1, 1, b"\x00")
        collision_code, _ = emit_collision020()
        for machine, collision_address in zip(self.machines, (0x10000, 0x25000)):
            pair = NativePair(collision_address, collision_code)
            bob = OrientedImage(image, True, True).collision_bob(1, 26, 20, 3)
            point = OrientedImage(target).collision_bob(2, 26, 28, 3)
            actual = machine.run(image, 3)
            variant = replace(image, planes=actual[:image.plane_bytes],
                              mask=actual[image.plane_bytes:])
            run_pair(pair, bob, variant, point, target, 1, screen=Rect(0, 0, 100, 100), expect=1)
            run_pair(pair, bob, variant, point, target, 1, screen=Rect(0, 0, 100, 100),
                     local_limits={1: Rect(0, 0, 28, 10)}, expect=0)


    def test_chip_prepare_checks_size_flags_and_both_endpoints(self):
        source = pack_pixels(1, 17, 2, 4, bytes(range(16)) * 2 + b"\x04\x05",
                             visibility=bytes((0, 1)) * 17)
        size = len(planar_bytes(source))
        entry = self.labels["p2b_planar_chip_prepare_entry"]
        for machine in self.machines:
            hook, calls = machine.mock_exec(allocation=DESTINATION, memory_types=(2, 2))
            try:
                actual = machine.run(source, 3, chip_entry=entry)
                self.assertEqual(actual, planar_bytes(oracle(source, 3)))
                self.assertEqual(calls, [("AllocMem", size, 2),
                                         ("TypeOfMem", DESTINATION),
                                         ("TypeOfMem", DESTINATION + size - 1)])
            finally:
                machine.uc.hook_del(hook)

    def test_chip_failure_frees_exact_block_and_publishes_no_result(self):
        source = pack_pixels(1, 17, 2, 1, bytes(34))
        size = len(planar_bytes(source))
        entry = self.labels["p2b_planar_chip_prepare_entry"]
        cases = (
            ({REG_D[0]: 0}, DESTINATION, (), []),
            ({REG_D[6]: size - 1}, DESTINATION, (), []),
            ({}, 0, (), [("AllocMem", size, 2)]),
            ({}, DESTINATION, (4,), [("AllocMem", size, 2), ("TypeOfMem", DESTINATION),
                                     ("FreeMem", size, DESTINATION)]),
            ({}, DESTINATION, (2, 4), [("AllocMem", size, 2), ("TypeOfMem", DESTINATION),
                                       ("TypeOfMem", DESTINATION + size - 1),
                                       ("FreeMem", size, DESTINATION)]),
            ({REG_A[0]: SOURCE + 1}, DESTINATION, (2, 2),
             [("AllocMem", size, 2), ("TypeOfMem", DESTINATION),
              ("TypeOfMem", DESTINATION + size - 1), ("FreeMem", size, DESTINATION)]),
        )
        for machine in self.machines:
            for overrides, allocation, types, expected in cases:
                hook, calls = machine.mock_exec(allocation=allocation, memory_types=types)
                try:
                    machine.run(source, 1, chip_entry=entry, overrides=overrides, expect=0)
                    self.assertEqual(calls, expected)
                finally:
                    machine.uc.hook_del(hook)


if __name__ == "__main__":
    unittest.main(verbosity=2)
