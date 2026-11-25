#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P2j diagnostic candidate on the EXACT Runtime ABK, two AP20 layouts.
Graphics/Exec/Intuition are modeled, NOT emulated AmigaOS or real DMA.
Challenge assumptions which the P2i mock made about publication and close.
"""
import argparse,base64,json,os,unittest
from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from
from unicorn.m68k_const import *
from build_m19_s1p2j_in_memory import build_s1p2j
from test_m19_s1p2i_gate_a import SpriteMachine,GROUP,INTUI,STATE,CI
from test_m19_s1p1c_amos_bank_commit import EXEC
from test_m19_s1p1c_pipeline import DB,SB0,SB1,GFX,SCREEN
from test_m19_s1p1i_contract_gate_a import SAFE,DISP,MSG
from test_m19_s1p1i_l2b_integration_gate_a import chain
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases,verify_linked_source
from test_m19_p2d_l1_safeport_gate_a import run_cases
import test_m19_p2d_l2_first_bind_gate_a as l2_gate

ROOT=Path(__file__).resolve().parents[1]
FAST_TABLE=0x40004690
WIN,WINPORT=0x149800,0x149a00
FIXTURE_SHA='225970dda0271260f598b5e379ee52ca2d605a19a13c6b133b46ac13edf92a93'

def exact_fixture():
    raw=(ROOT/'tests/proto/sprite_s1_public/AGSP_S1P1E_FINAL.ABK').read_bytes()
    assert len(raw)==532 and sha256(raw).hexdigest()==FIXTURE_SHA
    assert raw[:4]==b'AmBk' and raw[12:20]==b'AGASPRT '
    payload=raw[20:]
    assert payload[:4]==b'AGSP' and unpack_from('>H',payload,8)[0]==3
    assert unpack_from('>H',payload,128)[0]==3
    assert payload[467:476]==bytes((255,70,40,36,220,117,26,115,255))
    return payload

class ProbeMachine(SpriteMachine):
    def __init__(self,image,info,layout,db=True):
        super().__init__(image,info,layout)
        self.erase()
        self.payload=exact_fixture()
        self.node=self.make_bank(29,b'AGASPRT ',self.payload)
        self.cmap=bytes(63)+self.payload[467:476]+bytes(768-72)
        # Real P2d r2 observed table in Z3 Fast, not low 24-bit RAM.
        self.uc.mem_map(0x40000000,0x10000)
        self.put32(GFX+208,FAST_TABLE)
        self.put32(FAST_TABLE,0x40002700)
        self.tofs=0
        self.ever=set()
        self.blank_noop=False
        self.image_noop=False
        self.keep_refs=False
        self.did_first_move=False
        self.close_resources=[]
        self.db=db
        self.pending=set()
        if db:
            # Nonzero window and DB with outstanding Safe/Disp replies.
            # The actual UNIT142 cleanup must drain and free both.
            self.put32(STATE+32,DB)
            self.put32(STATE+36,WIN)
            self.put32(WIN+86,WINPORT)
            self.put32(DB,SB0);self.put32(DB+4,SB1)
            self.put32(DB+12,SAFE);self.put32(DB+16,DISP)
            self.put32(DB+20,3)
            self.pending={SAFE,DISP}
        for base,offs in ((EXEC,(372,672)),(INTUI,(72,774))):
            for off in offs:self.uc.mem_write(base-off,b'\x4e\x75')

    def sprite(self,n=1,x=32,y=112,image=3):
        result=super().sprite(n,x,y,image)
        return result-(1<<32) if result&0x80000000 else result

    def on_code(self,uc,address,size,user):
        a0=uc.reg_read(UC_M68K_REG_A0)
        a1=uc.reg_read(UC_M68K_REG_A1)
        d0=uc.reg_read(UC_M68K_REG_D0)
        d1=uc.reg_read(UC_M68K_REG_D1)
        result=0
        if address==EXEC-534 and 0x40000000<=a1<0x40010000:
            result=5
        elif address==EXEC-690 and a1==DB:
            assert self.db and not self.pending
            assert 'db' not in self.close_resources
            assert 'sb0' in self.close_resources and 'sb1' in self.close_resources
            self.close_resources.append('db')
        elif address==EXEC-690:
            assert a1 not in self.ever,'FreeVec of ever-exposed allocation'
            return super().on_code(uc,address,size,user)
        elif address==EXEC-372 and a0 in (SAFE,DISP,WINPORT):
            if a0 in self.pending and self.tofs>=2:
                self.pending.remove(a0)
                result=MSG if a0==SAFE else MSG+4
        elif address==EXEC-672:
            assert a0 in (SAFE,DISP) and a0 not in self.pending
            self.close_resources.append('safe' if a0==SAFE else 'disp')
        elif address==INTUI-72:
            assert a0==WIN and 'window' not in self.close_resources
            self.close_resources.append('window')
        elif address==INTUI-774:
            assert a0==SCREEN and a1 in (SB0,SB1) and not self.pending
            self.close_resources.append('sb0' if a1==SB0 else 'sb1')
        elif address==INTUI-66:
            if self.db:
                assert sorted(self.close_resources)==sorted(
                    ['window','sb0','sb1','safe','disp','db'])
                assert self.get(STATE+32)==0 and self.get(STATE+36)==0
            return super().on_code(uc,address,size,user)
        elif address==GFX-408:
            super().on_code(uc,address,size,user)
            if d0==2 and uc.reg_read(UC_M68K_REG_D0)&65535==2:
                assert a0 in self.chip
                self.ever.add(a0)
            return
        elif address==GFX-708:
            # Unlike P2i, require the exact observed P2b ordering.
            assert self.read(GFX+166,1)[0]&12==12
            return super().on_code(uc,address,size,user)
        elif address==GFX-420:
            assert a0==SCREEN+44 and a1 in self.ever
            ptr=uc.reg_read(UC_M68K_REG_A2)
            assert ptr in (a1+48,a1+self.get(a1+44))
            image=ptr==a1+48
            self.sprite_calls.append('image' if image else 'blank')
            if image:
                assert self.get(FAST_TABLE+8)==0
                if not self.image_noop:self.put32(a1,ptr)
                # Deliberately defer table/Copper publication until Move.
            elif not self.blank_noop:
                self.put32(a1,ptr)
                if not self.keep_refs:
                    self.put32(FAST_TABLE+8,a1);self.copper(2,ptr)
        elif address==GFX-426:
            assert a0==SCREEN+44 and a1 in self.ever
            assert self.get(a1)==a1+48
            if not self.did_first_move:
                assert self.get(FAST_TABLE+8)==0,'test did not defer publication'
                self.did_first_move=True
            self.put32(FAST_TABLE+8,a1);self.copper(2,a1+48)
            self.moves.append((d0,d1))
            self.put16(a1+6,d0);self.put16(a1+8,d1)
        elif address==GFX-414:
            assert d0 in (2,3)
            mask=self.read(GFX+166,1)[0]
            assert mask&(1<<d0)
            self.uc.mem_write(GFX+166,bytes([mask&~(1<<d0)]))
            if not self.keep_refs:
                self.put32(FAST_TABLE+d0*4,0)
                self.copper(d0,CI+176)
            self.sprite_calls.append('free'+str(d0))
        elif address==GFX-270:
            assert self.depth==0
            self.tofs+=1
        else:
            return super().on_code(uc,address,size,user)
        self.volatile(uc,result)

    def held(self):
        assert len(self.ever)==1 and self.chip==self.ever
        assert self.named and len(self.temp_live)==3
        assert sorted(self.allocations[p] for p in self.temp_live)==[40,112,192]
        assert self.read(GFX+166,1)[0]&12==0
        assert self.get(self.get(self.named+56)+12)==4

    def closed(self,end=False):
        self.close(end)
        assert self.get(STATE)==0 and not self.get(self.cell)
        self.held()
        assert self.get(self.named+56+12)==0
        assert self.get(self.named+72)==0 and self.get(self.named+40)==0
        before=len(self.temp_allocs)
        assert self.bankfree()==0
        self.held()
        assert len(self.temp_allocs)==before

def suite(image,info):
    count=0
    for layout in ('runtime','compiled'):
        def new(db=True):
            m=ProbeMachine(image,info,layout,db)
            assert m.select(29)==1
            return m
        for end in (False,True):
            for db in (False,True):
                m=new(db)
                assert m.sprite()==1
                assert m.did_first_move and m.sprite_calls==['get2','get3','image']
                m.erase()
                before=len(m.temp_allocs)
                for x in range(34,234,2):assert m.sprite(x=x)==1
                assert len(m.moves)==101 and len(m.temp_allocs)==before
                # Explicit Off followed by real Close/End continuation.
                assert m.off()==1 and m.off()==1
                assert m.sprite()==-140
                m.closed(end);count+=1
                # A later screen must not allocate another exposed block.
                m.put32(STATE,SCREEN);m.put32(STATE+4,INTUI);m.put32(STATE+8,GFX)
                m.put32(STATE+12,320);m.put32(STATE+16,256);m.put32(STATE+20,256)
                m.node=m.make_bank(29,b'AGASPRT ',m.payload)
                assert m.select(29)==1 and m.sprite()==-123
                assert len(m.temp_allocs)==before
                m.held();count+=1
                # Close while active, even with stale sampled private refs.
                m=new(db);m.keep_refs=True
                assert m.sprite()==1
                m.closed(end);count+=1
        for fail,reason in ((1,-134),(2,-124),(3,-126)):
            m=new();m.fail_temp_at=fail
            assert m.sprite()==reason;m.empty()
            assert not m.sprite_calls;count+=1
        for ch,reason in ((2,-141),(3,-142)):
            m=new();m.reject_channel=ch
            assert m.sprite()==reason
            if ch==2:
                m.empty();m.close();assert m.get(STATE)==0
            else:
                m.closed()
            count+=1
        m=new();m.cmap=bytes(768)
        assert m.sprite()==-153
        assert m.sprite_calls==['get2','get3','free3','free2']
        m.closed();count+=1
        m=new();m.palette_mode=False
        assert m.sprite()==-150;m.closed();count+=1
        m=new();m.image_noop=True
        assert m.sprite()==-160
        assert not m.moves
        m.closed();count+=1
        m=new();assert m.sprite()==1;m.blank_noop=True
        assert m.off()==0 and m.off()==1
        m.closed();count+=1
        m=new();m.erase()
        assert m.sprite()==-121;m.empty();count+=1
        m=new();m.put16(SCREEN+76,0x1000)
        assert m.sprite()==-115;m.empty();count+=1
        m=new();m.put32(m.cell+4,0)
        assert m.sprite()==-111;m.empty();count+=1
        m=new();assert m.sprite(x=-1)==-102;m.empty();count+=1
        m=new();assert m.sprite()==1
        m.close_ok=False;m.close()
        assert m.get(STATE)==SCREEN and m.get(m.root()+12)==SCREEN
        m.held();m.close_ok=True;m.closed();count+=1
        m=new(False);m.close_ok=False;m.close()
        assert m.get(STATE)==SCREEN;m.empty()
        m.close_ok=True;m.close();assert m.get(STATE)==0;m.empty();count+=1
        print('S1P2J_ROUTE_PASS',layout,count,flush=True)
    return count

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--historical',required=True,type=Path)
    a=p.parse_args()
    for k in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[k]=str(a.historical)
    image,info=build_s1p2j(a.vasm)
    print('S1P2J_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    count=suite(image,info)
    print('S1P2J_DISPLAY_CPU_PASS',count,flush=True)
    chain(image)
    prior,meta=build_l2(a.vasm)
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    verify_linked_source(a.vasm,good)
    assert run_pattern_cases(prior,image)==184
    assert run_cases(image,info)==172
    l2_gate.IMAGE,l2_gate.META=image,meta
    result=unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
    assert result.wasSuccessful() and result.testsRun==10
    print('S1P2J_FULL_GATE_A_PASS '+json.dumps(info,sort_keys=True),flush=True)
    encoded=base64.b64encode(image).decode('ascii')
    for i in range(0,len(encoded),2048):
        print(f'S1P2J_BYTES {i//2048:04d} {encoded[i:i+2048]}',flush=True)

if __name__=='__main__':main()
