#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""CPU020 Gate A of the PRIVATE M19 Chip lifecycle, mocked Exec/graphics.

Exec AllocVec/TypeOfMem/CopyMem/FreeVec and graphics WaitBlit are mocked.
No real Chip RAM, DMA, AP20 or AMOS Compiler is claimed by these CPU tests.
"""
from __future__ import annotations
from struct import pack, unpack
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
from unicorn.m68k_const import (
    UC_CPU_M68K_M68020, UC_M68K_REG_SR, UC_M68K_REG_PC,
    UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
    UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7,
    UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
    UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7,
)
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from m19_p0c_chip_stage_emit import (
    emit_chip_stage, L_ALLOCVEC, L_FREEVEC, L_TYPEOFMEM, L_COPYMEM,
    L_WAITBLIT, COOKIE, MAX_STAGE,
)
from m19_p0a_multi_bob_abk import empty_bank, put_image, make_mask, parse_payload

DR = (UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
      UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7)
AR = (UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
      UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7)
EXEC = 0x20000
GFX = 0x24000
CONTEXT = 0x58000
SOURCE = 0x400000
STACK = 0xeffff0
STOP = 0x10000


def sample():
    raw = empty_bank()
    raw = put_image(raw, 1, 17, 15, 8, bytes((x * 7) & 255 for x in range(255)))
    raw = put_image(raw, 3, 37, 8, 4, bytes((x * 3) & 15 for x in range(296)))
    raw = make_mask(raw, 1, 0)
    bank = parse_payload(raw)
    data_start = 32 + len(bank.images) * 40
    return raw, raw[data_start:]


class CPU:
    def __init__(self, *, entry=0x100000, source=None, allocation_fail=False,
                 fail_chip=None, model=UC_CPU_M68K_M68020):
        if source is None:
            _, source = sample()
        self.entry = entry
        self.code, self.labels = emit_chip_stage()
        self.uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(model)
        self.uc.mem_map(0, 0x1000000)
        self.uc.mem_write(entry, self.code)
        self.uc.mem_write(STOP, b'\x4e\x71')
        self.uc.mem_write(SOURCE, source)
        self.uc.mem_write(CONTEXT, bytes(20))
        self.uc.mem_write(4, pack('>I', EXEC))
        self.uc.mem_write(EXEC + 0x128, b'\x00\x02')
        self.source_size = len(source)
        self.allocations = {}
        self.next = 0x500000
        self.alloc_calls = 0
        self.free_calls = 0
        self.copies = 0
        self.waits = 0
        self.pending = False
        self.allocation_fail = allocation_fail
        self.fail_chip = fail_chip
        self.new_alloc = 0
        self.log = []
        for addr in [EXEC + L_ALLOCVEC, EXEC + L_FREEVEC,
                     EXEC + L_TYPEOFMEM, EXEC + L_COPYMEM, GFX + L_WAITBLIT]:
            self.uc.mem_write(addr, b'\x4e\x75')
        self.uc.hook_add(UC_HOOK_CODE, self.exec_call,
                         begin=EXEC - 700, end=EXEC)
        self.uc.hook_add(UC_HOOK_CODE, self.exec_call,
                         begin=GFX - 250, end=GFX)

    def get(self, addr):
        return unpack('>I', self.uc.mem_read(addr, 4))[0]

    def put(self, addr, value):
        self.uc.mem_write(addr, pack('>I', value & 0xffffffff))

    def a(self, num):
        return self.uc.reg_read(AR[num])

    def d(self, num):
        return self.uc.reg_read(DR[num])

    def context(self):
        return unpack('>5I', self.uc.mem_read(CONTEXT, 20))

    def rts(self, result=0):
        self.uc.reg_write(DR[0], result & 0xffffffff)
        self.uc.reg_write(DR[1], 0xdeadbeef)
        self.uc.reg_write(AR[0], 0xbad000)
        self.uc.reg_write(AR[1], 0xbad100)
        sp = self.a(7)
        self.uc.reg_write(AR[7], sp + 4)
        self.uc.reg_write(UC_M68K_REG_PC, self.get(sp))

    def exec_call(self, uc, addr, size, unused):
        if addr not in (EXEC + L_ALLOCVEC, EXEC + L_FREEVEC,
                        EXEC + L_TYPEOFMEM, EXEC + L_COPYMEM, GFX + L_WAITBLIT):
            return
        result = 0
        self.log.append(addr)
        if addr == EXEC + L_ALLOCVEC:
            self.alloc_calls += 1
            count = self.d(0)
            assert 0 < count <= MAX_STAGE and not (count & 1), count
            assert self.d(1) == 3, 'AllocVec must request MEMF_PUBLIC | MEMF_CHIP'
            if not self.allocation_fail:
                result = self.next
                self.next += ((count + 31) & ~15)
                assert self.next < 0xc00000
                self.allocations[result] = count
                self.new_alloc = result
                self.uc.mem_write(result, b'\xcc' * count)
                self.uc.mem_write(result + count, b'\xa5\x5a\xab\xcd')
        elif addr == EXEC + L_TYPEOFMEM:
            ptr = self.a(1)
            if SOURCE <= ptr < SOURCE + self.source_size:
                result = 1  # AMOS AGBO source in Fast RAM: legal CPU copy source
            for base, count in self.allocations.items():
                if base <= ptr < base + count:
                    result = 3
                    if self.fail_chip == 'first' and ptr == self.new_alloc:
                        result = 1
                    if self.fail_chip == 'end' and ptr == self.new_alloc + count - 1:
                        result = 1
        elif addr == EXEC + L_COPYMEM:
            src, dst, count = self.a(0), self.a(1), self.d(0)
            assert src == SOURCE and count == self.source_size
            assert dst in self.allocations and self.allocations[dst] == count
            self.uc.mem_write(dst, bytes(self.uc.mem_read(src, count)))
            self.copies += 1
        elif addr == GFX + L_WAITBLIT:
            self.waits += 1
            self.pending = False
        elif addr == EXEC + L_FREEVEC:
            ptr = self.a(1)
            assert ptr in self.allocations, ('foreign/double FreeVec', hex(ptr))
            assert not self.pending, 'FreeVec while DMA is active'
            del self.allocations[ptr]
            self.free_calls += 1
        self.rts(result)

    def call(self, label, *, src=SOURCE, size=None, ctx=CONTEXT,
             identity=0x600000, generation=10, gfx=GFX):
        if size is None:
            size = self.source_size
        for n, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1230 + n)
        for n, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000 + n * 0x100)
        self.uc.reg_write(DR[0], size if label == 'stage_entry' else identity)
        self.uc.reg_write(DR[1], identity if label == 'stage_entry' else generation)
        self.uc.reg_write(DR[4], generation)
        self.uc.reg_write(AR[0], src)
        self.uc.reg_write(AR[1], ctx)
        self.uc.reg_write(AR[4], gfx)
        before = {reg: self.uc.reg_read(reg) for reg in DR + AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        try:
            self.uc.emu_start(self.entry + self.labels[label], STOP, count=5000000)
        except Exception as ex:
            raise AssertionError(('Chip CPU020 fault', label, str(ex),
                                  hex(self.uc.reg_read(UC_M68K_REG_PC)),
                                  self.context(), self.log[-12:])) from ex
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK + 4, 'stack leak'
        for reg, value in before.items():
            if reg in (DR[2], DR[3]):
                continue
            assert self.uc.reg_read(reg) == value, ('ABI clobber', label, reg)
        assert self.d(2) == 0
        assert self.d(3) in (0, 1)
        return self.d(3)


def main():
    code, labels = emit_chip_stage()
    assert code == emit_chip_stage()[0], 'native source not deterministic'
    for lo, hi in ((labels['stage_entry'], labels['release_entry']),
                   (labels['release_entry'], labels['lookup_entry']),
                   (labels['lookup_entry'], len(code))):
        dis = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
                   .disasm(code[lo:hi], 0x100000 + lo))
        assert sum(i.size for i in dis) == hi - lo, ('invalid MC68020 decode', lo)
        assert not any(i.mnemonic.startswith('dc.') for i in dis)
    tests = 0
    for address in (0x100000, 0x180000):  # independent load addresses
        m = CPU(entry=address)
        assert m.call('stage_entry') == 1
        ptr, count, identity, gen, cookie = m.context()
        assert (count, identity, gen, cookie) == (
            m.source_size, 0x600000, 10, COOKIE)
        assert ptr in m.allocations and m.allocations[ptr] == count
        assert m.copies == 1 and m.alloc_calls == 1 and m.free_calls == 0
        assert bytes(m.uc.mem_read(ptr, count)) == bytes(
            m.uc.mem_read(SOURCE, count))
        assert bytes(m.uc.mem_read(ptr + count, 4)) == b'\xa5\x5a\xab\xcd'
        tests += 1
        assert m.call('lookup_entry') == 1
        assert m.call('lookup_entry', identity=0x600002) == 0
        assert m.call('lookup_entry', generation=11) == 0
        tests += 3
        m.pending = True
        assert m.call('stage_entry', identity=0x600002, generation=11) == 1
        assert m.waits == 1 and m.free_calls == 1 and not m.pending
        assert m.context()[0] != ptr and ptr not in m.allocations
        assert m.call('lookup_entry', identity=0x600002, generation=11) == 1
        tests += 2
        m.pending = True
        assert m.call('release_entry') == 1
        assert m.context() == (0, 0, 0, 0, 0)
        assert not m.allocations and m.waits == 2 and m.free_calls == 2
        assert m.call('lookup_entry', identity=0x600002, generation=11) == 0
        assert m.call('release_entry') == 1  # idempotent
        tests += 3
        m = CPU(entry=address, allocation_fail=True)
        assert m.call('stage_entry') == 0 and not m.allocations
        assert m.context() == (0, 0, 0, 0, 0)
        tests += 1
        for fail in ('first', 'end'):
            m = CPU(entry=address, fail_chip=fail)
            assert m.call('stage_entry') == 0
            assert m.context() == (0, 0, 0, 0, 0)
            assert m.alloc_calls == 1 and m.free_calls == 1
            assert not m.allocations and m.copies == 0
            tests += 1
        for kw in ({'src': SOURCE + 1}, {'size': 0}, {'size': 1},
                   {'size': 0x01000002}, {'identity': 0},
                   {'identity': 3}, {'generation': 0},
                   {'ctx': 0}, {'ctx': CONTEXT + 1},
                   {'src': SOURCE + 0x20000}):
            m = CPU(entry=address)
            assert m.call('stage_entry', **kw) == 0, kw
            assert m.context() == (0, 0, 0, 0, 0)
            assert m.alloc_calls == 0 and m.copies == 0, kw
            tests += 1
        m = CPU(entry=address)
        assert m.call('stage_entry') == 1
        old = m.context()
        m.allocation_fail = True
        assert m.call('stage_entry', identity=0x600002) == 0
        assert m.context() == old and len(m.allocations) == 1
        assert m.call('stage_entry', identity=0x600002, gfx=0) == 0
        assert m.context() == old and len(m.allocations) == 1
        assert m.call('release_entry', gfx=0) == 0
        assert m.context() == old and len(m.allocations) == 1
        assert m.call('release_entry') == 1
        tests += 5
        m = CPU(entry=address)
        m.put(CONTEXT + 16, 0x12345678)
        assert m.call('stage_entry') == 0
        assert m.call('release_entry') == 0
        assert m.context() == (0, 0, 0, 0, 0x12345678)
        tests += 2
        m = CPU(entry=address)
        m.uc.mem_write(EXEC + 0x128, b'\x00\x00')
        assert m.call('stage_entry') == 0
        assert m.call('release_entry') == 0
        assert m.call('lookup_entry') == 0
        assert m.alloc_calls == 0
        tests += 3
    print('M19 P0c PRIVATE Chip stage MC68020 CPU GATE A PASS', tests,
          'scenarios,', len(code), 'native bytes, Exec/graphics MOCKED;',
          'NO installed Lib, WinUAE or real Compiler test')


if __name__ == '__main__':
    main()
