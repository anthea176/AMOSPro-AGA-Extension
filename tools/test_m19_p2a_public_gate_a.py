#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Gate A candidate: AP20 V2 P2a binary plus public three-argument native entry.

Emulates exact source-built public BOBS entry on two MC68020 mappings.
Amiga OS and AMOS services are mocked; NOT Runtime WinUAE nor Compiler.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from struct import unpack_from,pack
import unittest
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from amos_link_test_support import relocate
from audit_ap20 import inspect,parse,walk_tokens
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from compiler_relocation import RBSR,GETP,unpack_ap20
from build_m19_p1e_bank_edit_in_memory import build_p1e
from build_m19_p1d_limit_bob_in_memory import build_p1d
from build_m19_p2a_public_in_memory import build_p2a
from m19_p1d_limit_bob_emit import emit_limit_bobs
from m19_p2a_public_bob_col_emit import emit_p2a_public_col,ENTRIES
from m19_p2a_bob_collision_model import Bob,Rect,collision
from m19_p2a_agbo_bridge import host_image
from m19_p0a_multi_bob_abk import parse_payload
from test_m19_p1e_bank_edit_gate_a import EditMachine,snapshot
from test_m19_p1d_limit_bob_gate_a import load_native,set_limit
from test_m19_p0j_pending_close_end_gate_a import ready
from test_m19_p1c_bob_priority_gate_a import invoke
from test_m19_p0j_swap_barrier_gate_a import DIRTY
from test_m5_generic import AMOS,AR,DR,EXEC,STACK,STOP

ARGS=0x58000


class PublicMachine(EditMachine):
    def os_call(self,uc,address,size,user):
        if address==EXEC-534 and STACK-32768<=self.a(1)<=STACK:
            return self._os_return(1)
        return super().os_call(uc,address,size,user)

    def col(self,a=1,b=2,mode=0,owner=AMOS):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x65430000+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+0x100*i)
        self.uc.reg_write(AR[3],ARGS)
        self.uc.reg_write(AR[5],owner)
        self.uc.reg_write(DR[3],mode&0xffffffff)
        self.put(ARGS,b);self.put(ARGS+4,a)
        old={r:self.uc.reg_read(r) for r in DR+AR[:7] if r not in (DR[2],DR[3],AR[3])}
        before=snapshot(self)
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(self.entry+self.labels['p2a_public_bob_col'],
                          STOP,count=25000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4 and self.a(3)==ARGS+8
        for reg,val in old.items():
            assert self.uc.reg_read(reg)==val,('AMOS public P2a ABI',reg)
        assert self.d(2)==0
        assert snapshot(self)==before
        res=self.d(3)
        return res-0x100000000 if res&0x80000000 else res


def machine(layout):
    p1d_binary,p1d=build_p1d()
    _,p1d_parts,_=unpack_ap20(p1d_binary)
    m=ready(layout,cls=PublicMachine,inject_failure=False)
    _,_,_,open_wrapper=load_native(m,p1d_parts,p1d)
    original,_=emit_limit_bobs(p1d['context_delta'])
    all_native,labels=emit_p2a_public_col(p1d['context_delta'])
    memory=relocate(all_native,m.entry,{},m.uc)
    # Install source-identified P1e source patches and appended P2a.
    for label,size in (('checked_stage_copy_call',4),
                       ('checked_stage_min_count',6)):
        off=labels[label]
        m.uc.mem_write(m.entry+off,memory[off:off+size])
    m.uc.mem_write(m.entry+len(original),memory[len(original):])
    m.uc.ctl_remove_cache(m.entry,m.entry+len(all_native))
    m.labels.update(labels)
    m.labels['routed_paint_all_entry']=labels['b8_b7_draw_trampoline_entry']
    m.labels['guarded_close_entry']=labels['b8_b7_close_trampoline_entry']
    m.labels['public_aga_bob_entry']=labels['b8_b7_bob_set_bootstrap_entry']
    assert invoke(m,open_wrapper)==1
    # Both P0j staged allocations were created by ready()'s real Update.
    return m


def oracle(m,mode):
    bobs=[]
    for ident,bank,x,y in ((1,10,5,7),(2,11,9,11)):
        src=parse_payload(m.bank_payload(bank)).image(1)
        bobs.append(Bob(ident,bank,1,x,y,host_image(src),
                        src.hotspot_x,src.hotspot_y))
    return int(collision(*bobs,screen=Rect(0,0,320,256),
                         mode='rect' if mode==0 else 'mask'))


class P2aCandidateNative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary,cls.meta=build_p2a()

    def test_01_p1e_ancestor_and_strict_new_ap20_token(self):
        image,meta=build_p2a()
        self.assertEqual((image,meta),(self.binary,self.meta))
        self.assertEqual(meta['public_commands'],97)
        self.assertEqual(meta['entries'],198)
        self.assertLessEqual(meta['group_bytes'],MAX_UNIT_BYTES)
        self.assertLess(meta['pc16_max'],32766)
        tok,parts,_=unpack_ap20(image)
        self.assertEqual(parts[188],GETP)
        self.assertTrue(parts[189].startswith(RBSR))
        self.assertEqual(unpack_from('>HH',parts[189],2),
                         (190,meta['public_offset']))
        self.assertTrue(parts[190].startswith(DISPATCH_V2))
        self.assertEqual(meta['bob_group'],190)
        audit=inspect(parse(image))
        self.assertFalse(audit['issues'])
        self.assertEqual((audit['tokens'][-1]['name'],
                          audit['tokens'][-1]['signature']),
                         ('aga bob col','00,0,0'))
        print('P2A_LIB_BUILD',meta,flush=True)

    def test_02_private_native_source_embeds_exact_ancestry(self):
        _,p1e=build_p1e()
        _,old=emit_p2a_public_col(p1e['context_delta'])
        self.assertTrue(all(key in old for key in ENTRIES))
        native,labels=emit_p2a_public_col(p1e['context_delta'])
        cap=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020)
        fragment=native[labels['p2a_public_bob_col']:]
        decoded=list(cap.disasm(fragment,0x100000))
        self.assertEqual(sum(i.size for i in decoded),len(fragment))
        self.assertTrue(decoded)
        self.assertFalse(any(x.mnemonic.startswith('dc.') for x in decoded))

    def test_03_public_rect_and_mask_on_two_real_layouts(self):
        for layout in ('interpreted','compiled'):
            m=machine(layout)
            for mode in (0,1):
                self.assertEqual(m.col(mode=mode),oracle(m,mode))
            self.assertEqual(m.col(a=1,b=1),-1)
            self.assertEqual(m.col(mode=2),-1)

    def test_04_foreign_owner_and_disabled_bob(self):
        for layout in ('interpreted','compiled'):
            m=machine(layout)
            self.assertEqual(m.col(owner=AMOS+0x1000),-1)
            self.assertEqual(m.col(a=0),-1)
            assert m.public('off',ident=2)==1
            self.assertEqual(m.col(),-1)

    def test_05_p1d_clip_is_live_and_nonmutating(self):
        for layout in ('interpreted','compiled'):
            m=machine(layout)
            self.assertEqual(set_limit(m,0,(0,0,2,2)),1)
            self.assertEqual(m.col(mode=0),0)
            self.assertEqual(set_limit(m,0,None),1)
            self.assertEqual(m.col(mode=0),oracle(m,0))

if __name__=='__main__':
    unittest.main(verbosity=2)
