#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Private P0c full-AGBO bank validation + Chip lifecycle CPU Gate A.

Uses the exact R88-derived P0b P0a+Mask source prefix. All AMOS/Exec/graphics
system calls are MOCKS. Does not prove WinUAE, real Chip RAM or Compiler.
"""
from __future__ import annotations

from struct import pack
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020

from test_m5_generic import DR, AR, AMOS, EXEC, GFX, STACK, STOP
from amos_link_test_support import relocate
from test_m19_p0b_masks_gate_a import MaskMachine
from test_m19_p0a_r88_get_gate_a import HEAD
from m19_p0a_multi_bob_abk import parse_payload
from build_m19_p0b_masks_in_memory import build
from m19_p0c_checked_bank_stage_emit import emit_checked_bank_stage
from m19_p0c_chip_stage_emit import COOKIE

CONTEXT = 0x5e000
CHIP_START = 0xd00000
ONE = 0x10000


class BankChipMachine(MaskMachine):
    def __init__(self, binary, layout='interpreted', depth=8,
                 *, chip_fail=False, bad_type=None):
        super().__init__(binary, layout=layout, depth=depth)
        self.native, self.labels = emit_checked_bank_stage()
        self.uc.mem_write(self.entry, relocate(self.native, self.entry, {}, self.uc))
        self.checked_entry = self.entry + self.labels['checked_stage_entry']
        self.get_entry = self.entry + self.labels['get_entry']
        self.make_entry = self.entry + self.labels['mask_make_entry']
        self.no_entry = self.entry + self.labels['mask_no_entry']
        self.uc.mem_write(CONTEXT, bytes(20))
        self.uc.mem_write(EXEC - 624, b'\x4e\x75')
        self.next_chip = CHIP_START
        self.chip_live = {}
        self.chip_allocs = 0
        self.chip_frees = 0
        self.chip_copies = 0
        self.chip_fail = chip_fail
        self.bad_type = bad_type
        self.pending_dma = False

    def context(self):
        return tuple(self.get(CONTEXT+4*n) for n in range(5))

    def os_call(self, uc, address, size, user):
        if address == EXEC-684 and self.d(1) == 3:
            self.chip_allocs += 1
            if self.chip_fail:
                return self._os_return(0)
            n = self.d(0)
            assert 0 < n <= 0x1000000 and n % 2 == 0, n
            address_ = self.next_chip
            self.next_chip += (n+15)&~15
            assert self.next_chip < 0xf00000, 'chip test address range exceeded'
            self.chip_live[address_] = n
            self.uc.mem_write(address_, bytes([0xcc])*n)
            self.uc.mem_write(address_+n, b'\xa5\x5a\xab\xcd')
            return self._os_return(address_)
        if address == EXEC-690 and self.a(1) in self.chip_live:
            ptr = self.a(1)
            assert not self.pending_dma, 'FreeVec while Blitter is still using source'
            del self.chip_live[ptr]
            self.chip_frees += 1
            return self._os_return(0)
        if address == EXEC-624:
            dst, src, n = self.a(1), self.a(0), self.d(0)
            assert dst in self.chip_live and self.chip_live[dst] == n
            self.uc.mem_write(dst, bytes(self.uc.mem_read(src, n)))
            self.chip_copies += 1
            return self._os_return(0)
        if address == EXEC-534:
            p = self.a(1)
            for start, length in self.chip_live.items():
                if start <= p < start+length:
                    result = 3  # TypeOfMem: MEMF_PUBLIC|MEMF_CHIP
                    if self.bad_type == 'first' and p == start:
                        result = 1
                    if self.bad_type == 'last' and p == start+length-1:
                        result = 1
                    return self._os_return(result)
        if address == GFX-228:
            self.pending_dma = False
        return super().os_call(uc, address, size, user)

    def run_checked(self, bank=10, *, ctx=CONTEXT, gfx=GFX, limit=9000000):
        for i, r in enumerate(DR):
            self.uc.reg_write(r, 0x1230+i)
        for i, r in enumerate(AR[:7]):
            self.uc.reg_write(r, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[1], ctx)
        self.uc.reg_write(AR[4], gfx)
        self.uc.reg_write(DR[3], bank)
        before = {r: self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        try:
            self.uc.emu_start(self.checked_entry, STOP, count=limit)
        except Exception as exc:
            raise AssertionError(('P0c checked bank CPU020 fault', str(exc),
                                  hex(self.uc.reg_read(UC_M68K_REG_PC)),
                                  bank, self.calls[-10:],
                                  self.context(), sorted(self.chip_live))) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4, 'P0c leaked stack'
        for r, value in before.items():
            if r in (DR[2], DR[3]):
                continue
            assert self.uc.reg_read(r) == value, ('P0c ABI clobber', r)
        assert self.d(2) == 0
        assert self.d(3) in (0, 1)
        assert self.plane_writes == 0, 'Chip staging wrote to screen planes'
        return self.d(3)


def ready(binary, layout='interpreted', depth=8, *, masked=True, **kwargs):
    m = BankChipMachine(binary, layout=layout, depth=depth, **kwargs)
    assert m.run_select(10) == 1
    assert m.run_get(1, 4, 5, 20, 8) == 1
    assert m.run_get(2, 5, 6, 35, 10) == 1
    assert m.run_get(3, 10, 7, 46, 10) == 1
    if masked:
        assert m.mask(True, 1, 0) == 1
        assert m.mask(True, 2, (1<<depth)-1) == 1
    return m


def expected_data(m):
    bank = parse_payload(m.bank_payload(10))
    return b''.join(img.planes + (img.mask or b'') for img in bank.images)


def main():
    src, labels = emit_checked_bank_stage()
    assert src == emit_checked_bank_stage()[0], 'native output non-deterministic'
    assert labels['checked_stage_entry'] < labels['checked_chip_stage']
    dis = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
               .disasm(src[labels['checked_stage_entry']:], 
                       ONE + labels['checked_stage_entry']))
    assert sum(ins.size for ins in dis) == len(src)-labels['checked_stage_entry']
    assert not any(ins.mnemonic.startswith('dc.') for ins in dis)

    lib, meta = build()
    assert meta['sha256'] == 'f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9'
    cases = 0
    for layout in ('interpreted', 'compiled'):
        for depth in (1, 4, 8):
            m = ready(lib, layout, depth)
            source = expected_data(m)
            bankptr = m.find(10)+24
            assert m.run_checked() == 1
            chip, size, ident, generation, tag = m.context()
            assert (size, ident, generation, tag) == (
                len(source), bankptr, parse_payload(m.bank_payload(10)).generation, COOKIE)
            assert chip in m.chip_live
            assert bytes(m.uc.mem_read(chip, size)) == source
            assert bytes(m.uc.mem_read(chip+size, 4)) == b'\xa5\x5a\xab\xcd'
            assert (m.chip_allocs, m.chip_copies, m.chip_frees) == (1, 1, 0)
            cases += 1

            # Updating a Bob invalidates the old identity: the new generation
            # is not reused; replacement waits for the DMA before FreeVec.
            m.pending_dma = True
            assert m.run_get(1, 4, 5, 20, 9) == 1
            assert m.run_checked() == 1
            assert m.chip_allocs == 2 and m.chip_frees == 1
            assert not m.pending_dma and m.context()[0] != chip
            assert bytes(m.uc.mem_read(m.context()[0], m.context()[1])) == expected_data(m)
            cases += 1

        m = ready(lib, layout, 8)
        assert m.run_checked(11) == 0, 'wrong selection accepted'
        assert m.chip_allocs == 0 and m.context() == (0, 0, 0, 0, 0)
        cases += 1
        m = ready(lib, layout, 8, chip_fail=True)
        assert m.run_checked() == 0 and not m.chip_live
        assert m.context() == (0, 0, 0, 0, 0) and m.chip_allocs == 1
        cases += 1

        for where in ('first', 'last'):
            m = ready(lib, layout, 8, bad_type=where)
            assert m.run_checked() == 0
            assert m.context() == (0, 0, 0, 0, 0)
            assert m.chip_allocs == m.chip_frees == 1 and not m.chip_live
            cases += 1

        for argument in ({'ctx':0}, {'ctx':CONTEXT+1}, {'bank':4},
                         {'bank':65536}):
            m = ready(lib, layout, 8)
            assert m.run_checked(**argument) == 0, argument
            assert m.chip_allocs == 0
            cases += 1

        # Bank absence, stale selection and corrupt headers/entries all
        # reject before the first Chip allocation.
        for offset, invalid in (
                (0, b'BAD!'),       # AGBO magic
                (6, b'\x00\x01'), # header flags
                (8, b'\x00\x00'), # no images, unsupported for staging
                (32, b'\x00\x00'),# image ID 0
                (34, b'\x00\x00'),# width 0
                (40, b'\x00\x01'),# wrong stride
                (42, b'\x00\x02'),# illegal mask flags
                (44, b'\x00\x00\x00\x00'), # wrong pixel offset
                (52, b'\x00\x00\x00\x01'), # wrong mask offset
                (64, b'\x00\x00\x00\x01'), # reserved field
        ):
            m = ready(lib, layout, 8)
            p = m.find(10)+24
            m.uc.mem_write(p+offset, invalid)
            assert m.run_checked() == 0, (layout, offset, invalid)
            assert m.chip_allocs == 0 and m.context() == (0, 0, 0, 0, 0)
            cases += 1
        m = ready(lib, layout, 8)
        p = m.find(10)+24
        data_start = 32 + 3*40
        # Width 17: unused bits in the last word of the first plane
        # must be zero; flip the lowest forbidden padding bit.
        target = p+data_start+2
        current = bytearray(m.uc.mem_read(target, 2))
        current[1] |= 1
        m.uc.mem_write(target, bytes(current))
        assert m.run_checked() == 0
        assert m.chip_allocs == 0
        cases += 1
        m = ready(lib, layout, 8)
        m.put(HEAD, 0)  # AGBO bank list identity lost
        assert m.run_checked() == 0
        assert m.chip_allocs == 0
        cases += 1
        m = ready(lib, layout, 8)
        m.uc.mem_write(EXEC+0x128, b'\x00\x00')
        assert m.run_checked() == 0
        assert m.chip_allocs == 0
        cases += 1

    print('M19 P0c PRIVATE checked AGBO->Chip MC68020 CPU Gate A PASS',
          cases, 'cases,', len(src), 'native unit bytes, private wrapper; '
          'no AP20 export, WinUAE, real Compiler or hardware DMA test')


if __name__ == '__main__':
    main()
