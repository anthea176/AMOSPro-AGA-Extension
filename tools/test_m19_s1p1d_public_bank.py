#!/usr/bin/env python3
"""S1-P1d public AMOS instruction ABI "Aga Sprite Bank N" MC68020 CPU tests.

The real raw Motorola code is assembled by VASM. AMOS Main/Exec calls are
simulated, so this is Gate A only, NOT a loadable public token or WinUAE.
"""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack
import unittest

from unicorn.m68k_const import (
    UC_M68K_REG_A0,UC_M68K_REG_A5,UC_M68K_REG_A7,
    UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_PC,UC_M68K_REG_SR,
)
from m19_s1_agsp_bank import empty_bank
from test_m19_s1p1c_amos_bank_commit import (
    Machine,REGS,CODE,STACK,STOP,AMOS,fixture
)


class PublicSelectMachine(Machine):
    def __init__(self,old=None,other=False,alloc_fail=False,foreign=False):
        super().__init__(old=old,other=other,alloc_fail=alloc_fail,foreign=foreign)
        self.code=Path(os.environ['AGSP_SELECT_BIN']).read_bytes()
        assert 1000<len(self.code)<65000
        self.uc.mem_write(CODE,self.code)

    def select(self,bank=10):
        uc=self.uc
        for n,reg in enumerate(REGS):
            uc.reg_write(reg,0x50005000+n)
        uc.reg_write(UC_M68K_REG_A5,AMOS)
        uc.reg_write(UC_M68K_REG_A0,0x180000)
        saved={r:uc.reg_read(r) for r in REGS}
        uc.reg_write(UC_M68K_REG_D3,bank & 0xffffffff)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.mem_write(STACK,pack('>I',STOP))
        try:
            uc.emu_start(CODE,STOP,count=30_000_000)
        except Exception as exc:
            raise AssertionError(
                f'public bank CPU fault PC=0x{uc.reg_read(UC_M68K_REG_PC):08x} '
                f'SP=0x{uc.reg_read(UC_M68K_REG_A7):08x} '
                f'D3=0x{uc.reg_read(UC_M68K_REG_D3):08x} '
                f'native_bytes={len(self.code)}') from exc
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in saved.items()),'ABI clobber'
        assert uc.reg_read(UC_M68K_REG_D2)==0
        return uc.reg_read(UC_M68K_REG_D3)

    def selection(self):
        # Last eight bytes of the raw source are the PC-relative selection
        # state. The full bank contents stay owned by AMOS, not this table.
        from struct import unpack
        return unpack('>II',self.read(CODE+len(self.code)-8,8))


@unittest.skipUnless(os.environ.get('AGSP_SELECT_BIN') and os.environ.get('AGSP_PUBLISH_BIN'),
                     'requires real VASM selection and publisher binaries')
class AGSPSpriteBankSelectGateA(unittest.TestCase):
    def test_create_canonical_empty_bank_and_select_owner(self):
        m=PublicSelectMachine()
        self.assertEqual(m.select(10),1)
        self.assertEqual(m.bank(10),empty_bank())
        self.assertEqual(m.selection(),(AMOS,10))
        self.assertEqual(m.word(m.bynum(10)+12),1)
        self.assertEqual(m.read(m.bynum(10)+16,8),b'AGASPRT ')
        self.assertEqual(len(m.notes),1)

    def test_reselect_is_idempotent_and_does_not_allocate(self):
        m=PublicSelectMachine()
        self.assertEqual(m.select(),1)
        num_created=len(m.created)
        self.assertEqual(m.select(),1)
        self.assertEqual(len(m.created),num_created)
        self.assertEqual(len(m.notes),1)
        self.assertEqual(m.selection(),(AMOS,10))

    def test_select_preexisting_loaded_agsp_bank(self):
        original=fixture()
        m=PublicSelectMachine(old=original,other=True)
        self.assertEqual(m.select(),1)
        self.assertEqual(m.bank(10),original)
        self.assertEqual(m.bank(11),bytes(range(32)))
        self.assertEqual(m.freed,[])
        self.assertEqual(m.notes,[])
        self.assertEqual(m.selection(),(AMOS,10))

    def test_allow_amos_normalized_data_flag_zero(self):
        m=PublicSelectMachine(old=fixture())
        m.put16(m.old_node+12,0)
        self.assertEqual(m.select(),1)
        self.assertEqual(m.bank(10),fixture())

    def test_reject_foreign_bank_without_change(self):
        m=PublicSelectMachine(old=fixture(),foreign=True)
        original=m.bank(10)
        self.assertEqual(m.select(),0)
        self.assertEqual(m.bank(10),original)
        self.assertEqual(m.selection(),(0,0))
        self.assertEqual(m.notes,[])
        self.assertEqual(m.freed,[])

    def test_reject_invalid_number_without_callbacks(self):
        for number in (0,4,65536,0xffffffff):
            with self.subTest(number=number):
                m=PublicSelectMachine()
                self.assertEqual(m.select(number),0)
                self.assertEqual(m.calls,[])
                self.assertEqual(m.notes,[])
                self.assertEqual(m.selection(),(0,0))

    def test_allocation_failure_has_no_partial_bank(self):
        m=PublicSelectMachine(alloc_fail=True)
        self.assertEqual(m.select(),0)
        self.assertIsNone(m.bank(10))
        self.assertEqual(m.selection(),(0,0))
        self.assertEqual(m.notes,[])

    def test_corrupted_image_or_palette_refused(self):
        broken=bytearray(fixture())
        # first opaque palette RGB triple may not match another local slot
        pal=80+64
        broken[pal+6:pal+9]=broken[pal+3:pal+6]
        m=PublicSelectMachine(old=bytes(broken))
        self.assertEqual(m.select(),0)
        self.assertEqual(m.bank(10),bytes(broken))
        self.assertEqual(m.notes,[])

    def test_corrupt_amos_flags_refused(self):
        m=PublicSelectMachine(old=fixture())
        m.put16(m.old_node+12,6)
        self.assertEqual(m.select(),0)
        self.assertEqual(m.bank(10),fixture())
        self.assertEqual(m.selection(),(0,0))


if __name__=='__main__':
    unittest.main(verbosity=2)
