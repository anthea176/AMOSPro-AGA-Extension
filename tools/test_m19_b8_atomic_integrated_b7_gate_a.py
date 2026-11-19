#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Full B7 native + B8 atomic registered Update integration, MC68020 Gate A.

Unlike the standalone B8 atomic harness, B7's real 64-image AGBO
preflight, Bob Draw, B7 End callbacks and Close all execute under
Unicorn MC68020. B8's true CPU planar snapshot/restore loops execute
against both real B7 fixture BitMaps. B7 graphics/OS/Chip painting is
still mocked by the established B7 Gate A fixture: this is not real
WinUAE Runtime or a true AMOS Compiler-produced executable.

Registration is bootstrapped by the existing tested B7 Draw path
(B7 has already armed End); first-call Update bootstrap remains TODO.
"""
from __future__ import annotations

from m19_b8_atomic_registered_update_emit import emit_b8_atomic_registered_update
from m19_b8_page_manager_emit import R as SROOT
from m19_b8_snapshot_pool_emit import R as POOL
from m19_p0j_swap_barrier_emit import DIRTY,READY
from test_m19_b8_b7_trampoline_gate_a import Combined,SNAP0,SNAP1
from test_m19_p0j_pending_close_end_gate_a import ready,DB
from test_m19_p0d_safe_bank_blit_native import SIZE,BM0,BM1
from test_m19_b7m2_close_reset_gate_a import active_ids
from test_m5_generic import AMOS

DEPTH=8
PAGE=SIZE*DEPTH


class AtomicIntegrated(Combined):
    def __init__(self,source,layout):
        super().__init__(source,layout)
        self.fifth_source,self.fifth_labels=emit_b8_atomic_registered_update()
        self.uc.mem_write(self.fifth,self.fifth_source)
        self.snapshot_allocs={SNAP0:PAGE,SNAP1:PAGE}
        self.uc.mem_write(SNAP0,bytes(PAGE))
        self.uc.mem_write(SNAP1,bytes(PAGE))

    def setup_b8_pool(self):
        super().setup_b8_pool()
        root=self.fifth+self.fifth_labels['b8_service_root']
        for field,value in (('bitmap0',BM0),('bitmap1',BM1),('bytes',PAGE),
                            ('valid',0)):
            self.put(root+SROOT[field],value)
        pool=self.fifth+self.fifth_labels['b8_pool_root']
        self.put(pool+POOL['bytes0'],PAGE)
        self.put(pool+POOL['bytes1'],PAGE)

    def atomic(self):
        return self.direct(self.fifth+self.fifth_labels[
            'b8_service_update_atomic_registered_entry'],maxcount=18000000)

    def clear(self):
        return self.direct(self.fifth+self.fifth_labels[
            'b8_service_clear_guard_entry'],maxcount=18000000)

    def physical_back_bytes(self):
        return b''.join(bytes(x) for x in self.read_back())


def main():
    raw,labels=emit_b8_atomic_registered_update()
    assert len(raw)%2==0 and len(raw)<32766
    checks=0
    for layout in ('interpreted','compiled'):
        m=ready(layout,cls=AtomicIntegrated,inject_failure=False)
        assert m.callbacks()==(m.end_callback(),)*2
        m.setup_b8_pool()
        assert m.arm()==1;checks+=1
        assert m.b7_root()[0]==AMOS
        # The existing B7 Draw was real, not a synthetic shim hook.
        assert m.invoke_guard('swap')==1
        m.put(DB+20,0)  # the B7 fixture models delivered Safe/Disp
        before=m.physical_back_bytes()
        paints_before=len(m.paint_blits)
        assert m.atomic()==1;checks+=1
        assert m.status()==READY and m.b8post_calls==0;checks+=1
        assert len(m.paint_blits)>paints_before;checks+=1
        back_bit=1 if m.get(DB+8)==1 else 2
        ptr=SNAP0 if back_bit==1 else SNAP1
        assert m.get(m.fifth+m.fifth_labels['b8_service_root']+SROOT['valid'])&back_bit
        assert bytes(m.uc.mem_read(ptr,PAGE))==before;checks+=1
        assert m.physical_back_bytes()!=before;checks+=1
        # Clear must restore exact previous background, not solid fill.
        assert m.clear()==1;checks+=1
        assert m.physical_back_bytes()==before and m.status()==0;checks+=1
        assert m.atomic()==1 and m.status()==READY;checks+=1
        assert m.b8post_calls==0
        # Real B7 Close resets Bob registry, THEN private B8 postclose.
        m.invoke_guard('close')
        assert m.get(m.real_state)==0;checks+=1
        assert m.b7_root()==(0,0) and m.b8post_calls==1;checks+=1
        assert len(m.b8_frees)==2 and not m.snapshot_allocs;checks+=1
        assert active_ids(m.table())==[];checks+=1
        m.invoke_guard('close')
        assert len(m.b8_frees)==2;checks+=1

        # Late/invalid original AGBO image: full native B7 64-ID gate
        # refuses BEFORE first snapshot copy and no Draw/Blit occurs.
        n=ready(layout,cls=AtomicIntegrated,inject_failure=False)
        n.setup_b8_pool()
        assert n.arm()==1
        assert n.invoke_guard('swap')==1
        n.put(DB+20,0)
        assert n.public('bob',ident=3,image=4096,x=8,y=9)==1
        original=n.physical_back_bytes()
        paints=len(n.paint_blits)
        assert n.atomic()==0;checks+=1
        assert n.status()==DIRTY;checks+=1
        assert n.physical_back_bytes()==original
        assert len(n.paint_blits)==paints;checks+=1
        assert n.get(n.fifth+n.fifth_labels['b8_service_root']+SROOT['valid'])==0
        n.invoke_guard('close')
        assert len(n.b8_frees)==2 and n.b8post_calls==1;checks+=1

    print('M19 B8 FULL B7-NATIVE/B8 ATOMIC MC68020 Gate A PASS',
          checks,'checks, two relocated layouts; real B7 preflight/Draw/Close',
          'and B8 planar copy, graphics/OS MOCKED; no first-call bootstrap')


if __name__=='__main__':
    main()
