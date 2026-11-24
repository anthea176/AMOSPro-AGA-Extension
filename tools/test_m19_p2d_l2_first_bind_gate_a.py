#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Regression for first B8 Bind, source-assembled L1+L2 on MC68020.

Reuse the established P2d bank/BOB fixture without changing its source.
Patch only the verified BNE.W bytes and append the actual candidate helper.
Exec/graphics/Intuition and AP20 relocation are modeled, not real WinUAE.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from struct import unpack_from
import unittest

from unicorn import UC_HOOK_CODE
from amos_link_test_support import relocate
from audit_ap20 import walk_tokens
from build_m19_p2d_in_memory import build_p2d
from build_m19_p2d_l2_first_bind_in_memory import build_l2, GROUP, GROUP_SIZE
from compiler_relocation import unpack_ap20
from m19_p2d_bob_auto_update_emit import emit_bob_auto_update
from m19_p0j_swap_barrier_emit import READY
from test_m19_p0j_pending_close_end_gate_a import DB,SAFE,DISP
from test_m19_p2d_bob_auto_update_gate_a import AutoUpdateGateA
from test_m19_p0d_safe_bank_blit_native import SIZE, oracle
from test_m19_p1a_getters_gate_a import dispatch_models
from test_m19_p2d_l1_safeport_gate_a import run_cases
from m19_p0a_multi_bob_abk import parse_payload
from test_m5_generic import EXEC,AMOS

IMAGE = None
META = None


class L2GateA(AutoUpdateGateA):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        original,_=build_p2d()
        _,cls.old,_=unpack_ap20(original)
        _,cls.new,_=unpack_ap20(IMAGE)
        cls.raw,_,_=emit_bob_auto_update(cls.p1d['context_delta'])
        cls.prefix=GROUP_SIZE-len(cls.raw)
        assert cls.old[GROUP][cls.prefix:]==cls.raw
        assert META['branch']>=cls.prefix

    def machine(self,layout,*,fixed=True):
        m=super().machine(layout)
        if fixed:
            old=self.old[GROUP]
            new=self.new[GROUP]
            at=META['branch']
            # Only the candidate's actual source-assembled bytes enter the
            # live emulator fixture; preserve its registered Bobs/metadata.
            addr=m.entry+at-self.prefix
            assert bytes(m.uc.mem_read(addr,4))==old[at:at+4]
            m.uc.mem_write(addr,new[at:at+4])
            m.uc.mem_write(m.entry+len(self.raw),new[GROUP_SIZE:])
            m.uc.ctl_remove_cache(addr,m.entry+len(new)-self.prefix)
        return m

    @staticmethod
    def root(m):
        return m.get(m.entry+m.labels['p2d_service_root'])

    @staticmethod
    def pages(m):
        return tuple(tuple(bytes(m.uc.mem_read(p,SIZE)) for p in page)
                     for page in (m.screen_planes,m.back_planes))

    def pending_first_bind(self,layout,*,fixed=True):
        m=self.machine(layout,fixed=fixed)
        # Existing fixture starts READY (two previously prepared Bobs).
        # Finish its setup; only this warmup's replies are modeled as already
        # acquired. The discriminating empty Swap below is the REAL native
        # Swap and must arm Safe+Disp itself; never inject those bits for it.
        self.assertEqual(self.swap(m),1)
        m.put(DB+20,0)
        for ident in (1,2):
            self.assertEqual(m.public('off',ident=ident),1)
        self.assertEqual(self.set_mode(m,1),1)
        self.assertEqual(self.root(m),0)
        self.assertEqual(m.status(),0)
        oldpage=m.get(DB+8)
        oldpages=self.pages(m)
        reads=(m.safe_count,m.disp_count)
        visits=m.native_swap_visits
        self.assertEqual(self.swap(m),1)
        self.assertEqual(m.native_swap_visits,visits+1)
        self.assertEqual(m.get(DB+8),1-oldpage)
        self.assertEqual(m.get(DB+20),3)
        self.assertEqual(self.root(m),0)
        self.assertEqual(self.pages(m),oldpages)
        self.assertEqual((m.safe_count,m.disp_count),reads)
        # No Blit Fill, no synthetic clear of pending Safe, no B8 Bind.
        self.assertEqual(m.run_select(10),1)
        self.assertEqual(m.public('bob',ident=1,x=5,y=7,image=1),1)
        self.assertEqual(self.root(m),0)
        self.assertEqual(m.get(DB+20),3)
        self.assertEqual((m.safe_count,m.disp_count),reads)
        return m

    def assert_refusal(self,m,*,polls):
        old=self.pages(m)
        counts=(m.safe_count,m.disp_count)
        page=m.get(DB+8)
        visits=m.native_swap_visits
        paints=self.paint_count(m)
        resources=(dict(m.chip_live),dict(m.metadata))
        self.assertEqual(self.swap(m),0)
        self.assertEqual(self.root(m),0)
        self.assertEqual(m.status(),0)
        self.assertEqual(m.get(DB+8),page)
        self.assertEqual(m.get(DB+20),3)
        self.assertEqual((m.safe_count,m.disp_count),(counts[0]+polls,counts[1]))
        self.assertEqual(self.pages(m),old)
        self.assertEqual(m.native_swap_visits,visits)
        self.assertEqual(self.paint_count(m),paints)
        self.assertEqual((dict(m.chip_live),dict(m.metadata)),resources)

    def ready_messages(self,m):
        m.safe_after=m.safe_count+1
        m.disp_after=m.disp_count+1

    def finish_first_bind(self,m):
        page=m.get(DB+8)
        front=self.pages(m)[page]
        back=m.active_back_planes()
        image=parse_payload(m.bank_payload(10)).image(1)
        expected=oracle(m.read_back(),image,5,7)
        reads=(m.safe_count,m.disp_count)
        draws=self.paint_count(m)
        visits=m.native_swap_visits
        # Prove Safe alone is consumed at entry into the appended helper's
        # resume path; no premature Disp acknowledgement or page flip.
        seen=[]
        resume=m.entry+META['branch']+4-self.prefix
        def observe(uc,addr,size,unused):
            if not seen:
                seen.append((m.get(DB+20),m.get(DB+8),m.safe_count,m.disp_count))
        hook=m.uc.hook_add(UC_HOOK_CODE,observe,begin=resume,end=resume)
        try:
            self.assertEqual(self.swap(m),1)
        finally:
            m.uc.hook_del(hook)
        self.assertEqual(seen,[(2,page,reads[0]+1,reads[1])])
        self.assertEqual((m.safe_count,m.disp_count),(reads[0]+1,reads[1]+1))
        self.assertEqual(m.get(DB+8),1-page)
        self.assertEqual(m.get(DB+20),3)
        self.assertNotEqual(self.root(m),0)
        self.assertEqual(m.status(),0)
        self.assertEqual(m.native_swap_visits,visits+1)
        self.assertGreater(self.paint_count(m),draws)
        self.assertEqual([bytes(m.uc.mem_read(a,SIZE)) for a in back],expected)
        self.assertEqual(self.pages(m)[page],front)

    def test_aga002_p2d_witness_and_l2_progress(self):
        for layout in ('interpreted','compiled'):
            with self.subTest(layout=layout):
                old=self.pending_first_bind(layout,fixed=False)
                self.ready_messages(old)
                self.assert_refusal(old,polls=0)
                self.assert_refusal(old,polls=0)
                self.assertFalse(old.safe_received)
                m=self.pending_first_bind(layout)
                self.ready_messages(m)
                self.finish_first_bind(m)

    def test_unavailable_safe_then_retry(self):
        for layout in ('interpreted','compiled'):
            m=self.pending_first_bind(layout)
            self.assert_refusal(m,polls=1)
            self.assert_refusal(m,polls=1)
            self.ready_messages(m)
            self.finish_first_bind(m)

    def test_missing_odd_or_unmapped_safe_port(self):
        for layout in ('interpreted','compiled'):
            for port in (0,SAFE+1,SAFE):
                m=self.pending_first_bind(layout)
                m.put(DB+12,port)
                if port==SAFE:
                    m.reject_type=SAFE
                self.ready_messages(m)
                self.assert_refusal(m,polls=0)

    def test_already_acquired_safe_and_explicit_first_update(self):
        for layout in ('interpreted','compiled'):
            m=self.pending_first_bind(layout)
            self.ready_messages(m)
            reads=(m.safe_count,m.disp_count)
            page=m.get(DB+8)
            front=self.pages(m)[page]
            image=parse_payload(m.bank_payload(10)).image(1)
            expected=oracle(m.read_back(),image,5,7)
            update=m.entry+m.labels['p2d_service_update']
            self.assertEqual(m.direct(update,maxcount=20_000_000),1)
            self.assertEqual(m.get(DB+20),2)
            self.assertEqual((m.safe_count,m.disp_count),(reads[0]+1,reads[1]))
            self.assertEqual(m.get(DB+8),page)
            self.assertEqual(m.status(),READY)
            self.assertEqual(m.read_back(),expected)
            self.assertEqual(self.pages(m)[page],front)
            draws=self.paint_count(m)
            self.assertEqual(self.swap(m),1)
            self.assertEqual(self.paint_count(m),draws)
            self.assertEqual(m.safe_count,reads[0]+1)
            # Separate control: model a previously acquired Safe before Bind.
            control=self.pending_first_bind(layout)
            control.put(DB+20,2)
            self.ready_messages(control)
            oldsafe=control.safe_count
            self.assertEqual(self.swap(control),1)
            self.assertEqual(control.safe_count,oldsafe)

    def test_combined_candidate_dispatch(self):
        tokens,parts,_=unpack_ap20(IMAGE)
        for row in walk_tokens(tokens):
            if row['name'] not in ('aga swap','aga bob update','aga bob auto update'):
                continue
            idx=row['function']
            group,offset=unpack_from('>HH',parts[idx],2)
            self.assertEqual(group,GROUP)
            self.assertEqual(dispatch_models(parts,group,offset,idx),2)


def main():
    global IMAGE,META
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',type=Path,required=True)
    IMAGE,META=build_l2(p.parse_args().vasm)
    print('P2D L2 SOURCE IN MEMORY',META,flush=True)
    cases=run_cases(IMAGE,META)
    assert cases==172
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(L2GateA)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print('P2D L2 MC68020 Gate A PASS',result.testsRun,'Bob suites and',cases,'writer cases',META)
    print('WinUAE B / real Compiler C / physical D NOT TESTED')


if __name__=='__main__':
    main()
