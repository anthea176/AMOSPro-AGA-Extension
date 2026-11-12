#!/usr/bin/env python3
"""M17 R55 Gate A: grouped Fill/Clear, Safe, pixels and Compiler bridge.

Executes the real generated 68000 native code in Unicorn with AmigaOS
graphics calls mocked. No WinUAE/physical Amiga result is claimed.
"""
from __future__ import annotations

from hashlib import sha256
from struct import unpack_from

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC
from unicorn.m68k_const import UC_M68K_REG_SR

from audit_ap20 import inspect, parse
from compiler_relocation import (
    native_from_promoted, unpack_ap20, unwrap_native_parts, is_compiler_wrapped,
)
from build_m17_blit_group_r55 import (
    build, BASE, BASE_SHA, TITLE, FILL_ENTRY, CLEAR_ENTRY, LAST_ENTRY,
)
from m17_blit_group_r55_emit import emit_fill_grouped
from m12_blit_safe_r27_emit import emit_fill_safe
from test_m12_blit_safe_r27 import SafeMixin, SafeCopyMachine
from test_m6_blit_fill_r14 import FillMachine, expected_fill
from test_m6_blit_clear_r15 import ClearMachine
from test_m5_generic import Machine, DR, AR, GFX, DB, BITMAP


class GroupMachine(SafeMixin, FillMachine):
    """Strict mock: multi-bit plane masks, exact counts and asynchronous wait."""
    run_clear = ClearMachine.run_clear

    def __init__(self, *args, fail_call=None, pending=0, safe_ready=False,
                 port_valid=True, **kwargs):
        super().__init__(*args, pending=pending, safe_ready=safe_ready,
                         port_valid=port_valid, **kwargs)
        self.fail_call = fail_call
        self.group_calls = []
        self.pending_groups = []

    def perform_pending(self):
        jobs = list(self.pending_groups)
        self.pending_groups.clear()
        self.pending = None
        for plane,x,y,w,h,value in jobs:
            after = bytearray(self.uc.mem_read(self.planes[plane], self.plane_size))
            for py in range(y,y+h):
                for px in range(x,x+w):
                    idx = py*self.stride+(px>>3)
                    bit = 1 << (7-(px & 7))
                    if value:
                        after[idx] |= bit
                    else:
                        after[idx] &= 255 ^ bit
            self.uc.mem_write(self.planes[plane], bytes(after))

    def os_call(self, uc, address, size, user):
        if address == GFX - 30:
            assert self.a(0) == self.a(1) == self.expected_bitmap
            assert self.a(2) == 0, "TempA must be NULL"
            x,y,dx,dy,w,h = (self.d(i) for i in range(6))
            assert (x,y) == (dx,dy)
            assert 0 <= x and 0 <= y and w > 0 and h > 0
            assert x+w <= self.meta["width"] and y+h <= self.meta["height"]
            minterm = self.d(6) & 255
            mask = self.d(7) & 255
            assert minterm in (0, 0xF0), minterm
            assert 0 < mask < (1 << self.meta["depth"])
            assert not self.pending_groups, "WaitBlit skipped between groups"
            selected = [p for p in range(self.meta["depth"]) if mask & (1 << p)]
            expected = len(selected)
            partial = self.fail_call == len(self.group_calls)
            if partial:
                selected = selected[:max(0,expected-1)]
            self.pending_groups = [(p,x,y,w,h,minterm == 0xF0) for p in selected]
            self.pending = True
            self.group_calls.append((mask,minterm,expected,len(selected)))
            uc.reg_write(DR[0], len(selected))
            uc.reg_write(DR[1], 0xDEADBEEF)
            uc.reg_write(AR[0], 0xBAD000)
            uc.reg_write(AR[1], 0xBAD100)
            pc = self.get(self.a(7))
            uc.reg_write(AR[7], self.a(7)+4)
            uc.reg_write(UC_M68K_REG_PC, pc)
            return
        if address == GFX - 228:
            assert self.pending is not None, "WaitBlit without DMA"
            self.waits += 1
            self.perform_pending()
            return Machine.os_call(self,uc,address,size,user)
        return SafeMixin.os_call(self,uc,address,size,user)


def expected_groups(depth,pen):
    full=(1 << depth)-1
    groups=[]
    clear_mask=full ^ pen
    if clear_mask:
        groups.append((clear_mask,0))
    if pen:
        groups.append((pen,0xF0))
    return groups


def build_checks():
    binary,info=build()
    assert binary == build()[0], "non deterministic builder"
    stable=BASE.read_bytes()
    assert sha256(stable).hexdigest()==BASE_SHA
    assert is_compiler_wrapped(binary)
    old_tokens,old=unwrap_native_parts(stable)
    new_tokens,parts=unwrap_native_parts(binary)
    assert old_tokens==new_tokens
    assert len(old)==len(parts)==59
    assert all(parts[i]==old[i] for i in range(59) if i not in (20,58))
    assert parts[20][4:]==old[20][4:]
    assert parts[58].startswith(old[58])
    assert parts[19]==old[19]
    assert parts[21]==old[21]
    assert parts[20][:2]==bytes.fromhex("6000")
    assert info["fill_bra_displacement"]==unpack_from(">h",parts[20],2)[0]
    assert info["native_fill_start"]+2+info["fill_bra_displacement"]==info["native_helper_start"]
    assert info["native_helper_start"]==sum(map(len,old))
    assert unwrap_native_parts(binary)==(old_tokens,parts)
    assert inspect(parse(binary))["issues"]==[]
    assert len(unpack_ap20(binary)[1])==60

    original_fill,_=emit_fill_safe()
    assert old[20]==original_fill+b"GetP"
    new_fill,labels=emit_fill_grouped()
    assert parts[58]==old[58]+new_fill
    assert labels==info["helper_labels"]
    dis=Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    decoded=list(dis.disasm(new_fill,0))
    assert sum(x.size for x in decoded)==len(new_fill)
    boundaries={x.address for x in decoded}
    assert all(x in boundaries for x in labels.values())
    assert all(x.mnemonic not in ("dc.w","illegal","trap") for x in decoded)
    assert new_fill.count(bytes.fromhex("4eaeffe2"))==1
    assert new_fill.count(bytes.fromhex("4eaeff1c"))==1

    # Verify old Clear's exact BSR.W hits the stable Fill entry and not GetP.
    starts=[];off=0
    for part in parts:
        starts.append(off);off+=len(part)
    assert parts[21][22:24]==bytes.fromhex("6100")
    assert starts[21]+24+unpack_from(">h",parts[21],24)[0]==starts[20]

    # Test the native form; it preserves original offsets and runs the
    # grouped helper through the real BRA.W in Fill, including Clear BSR.W.
    native=native_from_promoted(binary,TITLE)
    assert inspect(parse(native))["issues"]==[]
    # On real compiler-safe build the old stubs are unchanged and one
    # final monolithic unit holds the new helper and its internal calls.
    old_wrapped=unpack_ap20(stable)[1]
    new_wrapped=unpack_ap20(binary)[1]
    assert old_wrapped[:-1]==new_wrapped[:-1]
    assert len(new_wrapped[-1])<32768
    return native,info


def run():
    native,info=build_checks()
    cases=0
    # Pure exhaustive mask equivalence on every palette value (1..8 planes).
    for depth in range(1,9):
        full=(1<<depth)-1
        for pen in range(full+1):
            groups=expected_groups(depth,pen)
            assert len(groups) in (1,2)
            mask_union=0
            for mask,mt in groups:
                assert mask and (mask_union&mask)==0
                mask_union|=mask
                for plane in range(depth):
                    if mask&(1<<plane):
                        assert (mt==0xF0)==bool(pen&(1<<plane))
            assert mask_union==full
            cases+=1

    for depth in range(1,9):
        full=(1<<depth)-1
        pens=sorted(set((0,1,full//2,full,full ^ (1 << (depth-1)))))
        for front in (0,1):
            for pen in pens:
                m=GroupMachine(native,depth=depth,front=front)
                before=m.snapshot()
                assert m.run_fill(11,17,9,5,pen)==1,(depth,front,pen)
                want=expected_groups(depth,pen)
                assert [(mask,mt) for mask,mt,_,_ in m.group_calls]==want
                assert all(exp==actual for _,_,exp,actual in m.group_calls)
                assert m.waits==len(want)
                for plane in range(depth):
                    assert m.snapshot()[plane]==expected_fill(
                        before[plane],11,17,9,5,pen,plane,m.stride)
                cases+=1
            m=GroupMachine(native,depth=depth,front=front)
            before=m.snapshot()
            assert m.run_clear(7,13,6,4)==1
            assert m.group_calls==[(full,0,depth,depth)]
            assert m.waits==1
            for plane in range(depth):
                assert m.snapshot()[plane]==expected_fill(
                    before[plane],7,13,6,4,0,plane,m.stride)
            cases+=1

    # Safe and Disp flags: must be checked once before any DMA.
    for depth in (1,4,8):
        for pending,ready,result in ((0,False,1),(1,False,0),
                                     (1,True,1),(2,False,1),
                                     (3,False,0),(3,True,1)):
            m=GroupMachine(native,depth=depth,front=1,pending=pending,
                           safe_ready=ready)
            before=m.snapshot()
            out=m.run_fill(21,32,7,5,(1<<depth)-1)
            assert out==result
            assert m.safe_calls==int(bool(pending&1))
            assert m.get(DB+20)==(pending&~1 if result else pending)
            assert len(m.group_calls)==(1 if result else 0)
            assert m.waits==(1 if result else 0)
            if not result:
                assert m.snapshot()==before
            cases+=1
        m=GroupMachine(native,depth=4,pending=3,safe_ready=True,port_valid=False)
        before=m.snapshot()
        assert m.run_clear(3,4,7,6)==0
        assert m.snapshot()==before and not m.group_calls and m.waits==0
        cases+=1

    # Reject invalid geometry/pen before Safe consumption or DMA.
    for args in ((-1,0,10,10,1),(0,-1,10,10,1),(0,0,0,10,1),
                 (0,0,10,0,1),(319,0,2,1,1),(0,255,1,2,1),
                 (0,0,10,10,-1),(0,0,10,10,256),
                 (0x7fffffff,0,10,10,1)):
        m=GroupMachine(native,depth=8,pending=3,safe_ready=True)
        before=m.snapshot()
        assert m.run_fill(*args)==0,args
        assert m.snapshot()==before and not m.group_calls
        assert not m.safe_calls and not m.waits and m.get(DB+20)==3
        cases+=1

    # Partial or zero planecnt must return 0 and still WaitBlit to complete.
    for depth,pen in ((1,0),(5,0),(5,31),(5,21),(8,85),(8,255)):
        for fail_call in range(len(expected_groups(depth,pen))):
            m=GroupMachine(native,depth=depth,fail_call=fail_call)
            assert m.run_fill(17,19,6,4,pen)==0
            assert m.waits==fail_call+1
            assert len(m.group_calls)==fail_call+1
            assert not m.pending_groups
            cases+=1

    # Stable R54 Copy remains executable; no change in Copy's mask or Safe.
    m=SafeCopyMachine(native,depth=4,pending=0)
    assert m.run_copy((2,3,40,50,16,10))==1
    assert len(m.blits)==m.waits==1
    cases+=1
    print("M17 R55 grouped Fill/Clear CPU/ABI/bitmap/monolith Gate A PASS:",
          cases,"cases; candidate in-memory",info["size"],"bytes",
          "sha256",info["sha256"])
    print("Gate B WinUAE / Gate C AMOS Compiler / Gate D hardware: NOT TESTED")


if __name__=="__main__":
    run()
