#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A: real MC68020 resolver of an existing P0c staged AGBO bank.

Unicorn executes emitted native P0b+P0c+P0d code. AMOS/Exec/graphics are
mocked, not WinUAE or a native Compiler. The descriptor must match actual
validated AGBO planar bytes in the single owned Chip allocation.
"""
from __future__ import annotations

from struct import pack, unpack
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from test_m5_generic import DR, AR, AMOS, STACK, STOP, EXEC
from test_m19_p0c_program_end_real_gate_a import EndMachine
from build_m19_p0c_screen_close_in_memory import build
from m19_p0c_program_end_bridge_emit import emit_program_end_bridge
from m19_p0d_bank_image_resolve_emit import emit_bank_image_resolve
from m19_p0a_multi_bob_abk import parse_payload, ENTRY, HEADER
from amos_link_test_support import relocate

DESC = 0x59000
CANARY = bytes.fromhex('a5a5f00dd15ea55afee1beef') * 3
assert len(CANARY) == 36

class ResolverMachine(EndMachine):
    def __init__(self, lib, layout='interpreted', depth=8):
        super().__init__(lib, layout=layout, depth=depth, with_db=True)
        self.native, self.labels = emit_bank_image_resolve()
        self.uc.mem_write(self.entry, relocate(self.native, self.entry, {}, self.uc))
        self.registry_entries['bank_image_resolve_entry'] = (
            self.entry + self.labels['bank_image_resolve_entry'])

    def resolve(self, image=1, bank=10, *, owner=AMOS, descriptor=DESC,
                count=9000000):
        self.uc.mem_write(DESC, CANARY)
        for i, r in enumerate(DR):
            self.uc.reg_write(r, 0x1230 + i)
        for i, r in enumerate(AR[:7]):
            self.uc.reg_write(r, 0x40000 + i*256)
        self.uc.reg_write(AR[5], owner)
        self.uc.reg_write(AR[1], descriptor)
        self.uc.reg_write(DR[0], image & 0xffffffff)
        self.uc.reg_write(DR[3], bank & 0xffffffff)
        old = {r: self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        try:
            self.uc.emu_start(
                self.entry + self.labels['bank_image_resolve_entry'],
                STOP, count=count)
        except Exception as exc:
            raise AssertionError((
                'M19 P0d resolve MC68020 fault', str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),
                image, bank, self.root(), self.nodes() if self.metadata else {}
            )) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK+4
        for r, value in old.items():
            if r not in (DR[2], DR[3]):
                assert self.uc.reg_read(r) == value, ('AMOS ABI clobber', r)
        assert self.d(2) == 0
        status = self.d(3)
        assert status in (0, 1)
        data = bytes(self.uc.mem_read(DESC, 36))
        if not status:
            assert data == CANARY, ('partial descriptor published', data)
            return 0, None
        return 1, unpack('>9I', data)


def prepared(lib, layout, depth):
    m = ResolverMachine(lib, layout=layout, depth=depth)
    assert m.run_select(10) == 1
    assert m.run_get(3, 6, 3, 36, 10) == 1   # 31 x 8, opaque
    assert m.run_get(1, 4, 5, 20, 8) == 1    # 17 x 4, mask 0
    assert m.run_get(2, 20, 6, 56, 9) == 1   # 37 x 4, mask max
    assert m.mask(True, 1, 0) == 1
    assert m.mask(True, 2, (1 << depth)-1) == 1
    m.activate_aga_state()                    # original AGA Init from P0c
    assert m.call('registry_prepare_entry') == 1
    assert m.call('program_end_arm_entry') == 1
    return m


def check_image(m, image):
    bank = parse_payload(m.bank_payload(10))
    count = len(bank.images)
    info = bank.image(image)
    index = [v.image_id for v in bank.images].index(image)
    raw = bank.raw
    entry = ENTRY.unpack_from(raw, HEADER.size + index*ENTRY.size)
    pix_off, pix_len, mask_off, mask_len = entry[6:10]
    data_start = HEADER.size + ENTRY.size*count
    node, ctx = m.nodes()[10]
    base, allocation, identity, generation, cookie = ctx
    assert identity != 0 and generation == bank.generation and cookie == 0x43484950
    status, desc = m.resolve(image)
    assert status == 1
    p, mask, w, h, stride, depth, plane_bytes, owner, size = desc
    assert (owner, size) == (base, allocation)
    assert (w, h, stride, depth, plane_bytes) == (
        info.width, info.height, info.stride, info.depth, info.plane_bytes)
    assert p == base + pix_off - data_start
    assert allocation >= pix_off - data_start + pix_len
    assert bytes(m.uc.mem_read(p, pix_len)) == info.planes
    if info.mask is None:
        assert mask == 0 and not mask_off and not mask_len
    else:
        assert mask == base + mask_off - data_start
        assert allocation >= mask_off-data_start + mask_len
        assert bytes(m.uc.mem_read(mask, mask_len)) == info.mask


def main():
    lib, meta = build()
    assert meta['ap20_entries'] == 92
    raw, labels = emit_bank_image_resolve()
    previous, previous_labels = emit_program_end_bridge()
    assert raw[:len(previous)] == previous
    assert all(labels[k] == v for k, v in previous_labels.items())
    assert raw == emit_bank_image_resolve()[0]
    section = raw[labels['bank_image_resolve_entry']:]
    inst = list(Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_020)
                .disasm(section, 0x10000))
    assert sum(v.size for v in inst) == len(section)
    assert not any(v.mnemonic.startswith('dc.') for v in inst)

    passed = 0
    for layout in ('interpreted','compiled'):
        for depth in (1,4,8):
            m = prepared(lib,layout,depth)
            one_alloc = m.chip_allocs
            for image in (1,2,3):
                check_image(m,image)
                passed += 1
            assert m.chip_allocs == one_alloc, 'resolver should never recopy Chip'
            for missing in (0, 4, 4097):
                assert m.resolve(missing)[0] == 0
                passed += 1
            for kw in ({'bank':11}, {'owner':AMOS+0x100},
                       {'descriptor':0}, {'descriptor':DESC+1}):
                assert m.resolve(1, **kw)[0] == 0
                passed += 1

            # Recapture invalidates the staged identity, with no stale DMA.
            assert m.mask(True, 1, (1 << depth)-1) == 1  # update AGBO generation
            assert m.resolve(1)[0] == 0
            assert m.call('registry_prepare_entry') == 1
            check_image(m,1)
            passed += 2

            assert m.run_select(11) == 1
            assert m.resolve(1,bank=10)[0] == 0
            assert m.run_select(10) == 1
            check_image(m,2)
            passed += 2

            # Original P0c real Close -> cleanup must free ALL owned Chip.
            m.invoke('bridge')
            assert not m.chip_live and not m.metadata
            assert m.root() == (0,0)
            assert m.resolve(1)[0] == 0
            passed += 1

    print('M19 P0d PRIVATE MC68020 AGBO->Chip RESOLVER GATE A PASS',
          len(section),'new native bytes;',passed,'scenario assertions;',
          'OS mock only; NOT WinUAE/AMOS Compiler')


if __name__ == '__main__':
    main()
