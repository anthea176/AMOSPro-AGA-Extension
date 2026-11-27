#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Integrated AP20 S1 CPU Gate A, two placement models, modeled AmigaOS."""
import argparse,base64,json,os,unittest
from hashlib import sha256
from pathlib import Path
from struct import pack,unpack_from
from unicorn.m68k_const import *
from audit_ap20 import walk_tokens
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import unpack_ap20,RBSR
from build_m19_s1p2i_in_memory import build_s1p2i
from build_m19_p2d_l2_first_bind_in_memory import build_l2
from test_m19_s1p1i_contract_gate_a import ContractMachine
from test_m19_s1p1c_amos_bank_commit import CODE,STOP,AMOS,STACK,EXEC,REGS,HEAD,fixture
from test_m19_s1p1c_pipeline import SCREEN,COLORMAP,GFX,W,H
from test_m19_s1p1e_get_sprite_cpu import PARAMS
from test_m19_s1p1i_l2b_integration_gate_a import chain
from test_m19_p2d_l1_safeport_gate_a import run_cases
from test_m19_p2d_l2b_pattern_gate_a import run_pattern_cases,verify_linked_source
import test_m19_p2d_l2_first_bind_gate_a as l2_gate

ROOT=Path(__file__).resolve().parents[1]
GROUP,INTUI,TASK,TABLE,CI=0x50000,0x260000,0x94000,0x95000,0x468
STATE=GROUP+0x1c2
IDLE=CI+164
NEUTRAL=CI+176
NAME=b'AMOSPro.AGA.AGSP.S1.root.v1\0'

class SpriteMachine(ContractMachine):
    def __init__(self,image,info,layout):
        tok,parts,_=unpack_ap20(image)
        sg=unpack_from('>H',parts[204],2)[0]
        super().__init__(parts[sg][len(DISPATCH_V2):],parts,layout)
        self.uc.mem_write(GROUP,parts[142])
        self.cell=GROUP+info['root']
        self.put32(AMOS+456,STATE)
        self.put32(STATE,SCREEN)
        self.put32(STATE+4,INTUI)
        self.put32(STATE+8,GFX)
        self.put32(STATE+12,W)
        self.put32(STATE+16,H)
        self.put32(STATE+20,256)
        self.put32(STATE+28,8)
        self.put32(STATE+32,0)
        self.put32(STATE+36,0)
        self.put32(SCREEN+48,COLORMAP)
        self.put16(SCREEN+76,0x5000)
        self.put32(SCREEN+64,0)
        self.uc.mem_write(COLORMAP+1,b'\x02')
        self.put16(COLORMAP+2,256)
        self.uc.mem_write(COLORMAP+18,b'\x01')
        self.put16(EXEC+16,702)
        self.put16(EXEC+20,40)
        self.put16(GFX+18,512)
        self.put16(GFX+20,40)
        self.put32(GFX+34,0x96000)
        self.put32(GFX+38,CI)
        self.put32(GFX+50,0x97000)
        self.put32(GFX+54,IDLE)
        self.put32(GFX+208,TABLE)
        self.uc.mem_write(GFX+166,b'\x01')
        self.put32(CI+164,0xfffffffe)
        for i in range(8):
            self.put16(CI+88+i*8,0x120+i*4)
            self.put16(CI+92+i*8,0x122+i*4)
            self.copper(i,NEUTRAL)
            self.put32(TABLE+i*4,0)
        for base,offs in ((EXEC,(132,138,294,534,552,570,576,594,600,606,684,690,414)),
                          (GFX,(270,408,414,420,426,708,900)),(INTUI,(66,))):
            for off in offs:self.uc.mem_write(base-off,b'\x4e\x75')
        self.named=0
        self.depth=0
        self.task=TASK
        self.chip=set()
        self.sprite_calls=[]
        self.moves=[]
        self.reject_channel=0
        self.close_ok=True
        self.pending_view=False
        self.palette_mode=True
        self.entries_sprite={}
        api={x['name']:x for x in walk_tokens(tok)}
        for n,name in enumerate(('aga sprite','aga sprite off','aga sprite bank free')):
            index=api[name]['function']
            stub=parts[index]
            group,offset=unpack_from('>HH',stub,2)
            assert group==sg and stub[:2]==RBSR
            if layout=='runtime':
                pc=CODE+(sum(map(len,parts[group:index])) if index>group else -sum(map(len,parts[index:group])))
                raw=pack('>Hh',0x6100,CODE-(pc+2))+stub[4:]
            else:
                pc=CODE-0x400+n*0x20
                raw=pack('>HIH',0x4eb9,CODE,offset)+b'\x4e\x75'
            self.uc.mem_write(pc,raw)
            self.entries_sprite[name]=pc
        payload=fixture()
        self.node=self.make_bank(29,b'AGASPRT ',payload)
        pal=unpack_from('>I',payload,32+20)[0]
        self.rgb=payload[pal+3:pal+12]
        self.cmap=bytes(63)+self.rgb+bytes(768-72)

    def copper(self,ch,ptr):
        self.put16(CI+90+ch*8,ptr>>16)
        self.put16(CI+94+ch*8,ptr&65535)

    def on_code(self,uc,address,size,user):
        a0=uc.reg_read(UC_M68K_REG_A0);a1=uc.reg_read(UC_M68K_REG_A1)
        d0=uc.reg_read(UC_M68K_REG_D0);d1=uc.reg_read(UC_M68K_REG_D1)
        result=0
        if address==EXEC-132:
            self.depth+=1;assert self.depth==1
        elif address==EXEC-138:
            assert self.depth==1;self.depth=0
        elif address==EXEC-294:
            assert a1==0
            result=self.task
        elif address==EXEC-594:
            assert self.depth==1 and self.read(a1,len(NAME))==NAME
            result=self.named
        elif address==EXEC-600:
            assert self.depth==1 and self.named==0
            assert self.read(self.get(a1+10),len(NAME))==NAME
            self.named=a1
            self.uc.mem_write(a1+8,b'\x0f')
            self.put16(a1+14,0);self.put32(a1+40,0);self.put16(a1+44,65535)
        elif address==EXEC-576:
            assert self.depth==1 and a0==self.named
            assert not self.get(a0+40)
            self.put32(a0+40,self.task)
            self.put16(a0+14,1);self.put16(a0+44,0)
            result=1
        elif address==EXEC-606:
            assert self.depth==1 and a1==self.named
            assert self.read(a1+56,16)==bytes(16)
            assert self.get(a1+40)==self.task
            self.named=0
        elif address==EXEC-570:
            assert self.depth==1 and self.get(a0+40)==self.task
            assert self.get(a0+72)==0
            self.put16(a0+14,0);self.put16(a0+44,65535);self.put32(a0+40,0)
        elif address==EXEC-534:
            result=1 if 0<a1<0x3fffff else 0
            if any(p<=a1<p+self.allocations[p] for p in self.chip):result=3
        elif address==EXEC-684:
            assert self.depth==0 and d1 in (0x10001,0x10003)
            self.temp_tries+=1
            if self.temp_tries!=self.fail_temp_at:
                result=self.allocate(d0)
                self.temp_live.add(result);self.temp_allocs.append((result,d0))
                if d1==0x10003:self.chip.add(result)
        elif address==EXEC-690:
            assert self.depth==0 and a1 in self.temp_live and a1!=self.named
            self.temp_live.remove(a1);self.chip.discard(a1)
            self.temp_frees.append(a1)
            length=self.allocations.pop(a1)
            self.uc.mem_write(a1,b'\xa5'*length)
        elif address==EXEC-552:
            assert d0==39 and self.read(a1,17)==b'graphics.library\0'
            result=GFX
        elif address==EXEC-414:
            assert a1 in (INTUI,GFX)
        elif address==GFX-708:
            assert a0==COLORMAP and self.depth==0
            assert [self.get(a1+i*8) for i in range(4)]==[0x80000028,0x80000029,0x80000032,0x80000034]
            for i,v in enumerate((16,16,255,4)):self.put32(a1+i*8+4,v)
            result=0 if self.palette_mode else 1
        elif address==GFX-900 and d0==21:
            assert d1==3 and a0==COLORMAP
            uc.mem_write(a1,b''.join(pack('>I',v*0x01010101) for v in self.cmap[63:72]))
        elif address==GFX-408:
            assert d0 in (2,3) and self.depth==0
            bit=1<<d0;mask=self.read(GFX+166,1)[0]
            if d0==self.reject_channel or mask&bit:result=0xffff
            else:
                self.uc.mem_write(GFX+166,bytes([mask|bit]))
                self.put16(a0+10,d0)
                self.sprite_calls.append('get'+str(d0));result=d0
        elif address==GFX-420:
            assert a0==SCREEN+44 and a1 in self.chip
            ptr=uc.reg_read(UC_M68K_REG_A2)
            assert ptr in (a1+48,a1+self.get(a1+44))
            self.put32(a1,ptr);self.put32(TABLE+8,a1);self.copper(2,ptr)
            self.sprite_calls.append('image' if ptr==a1+48 else 'blank')
        elif address==GFX-426:
            assert a0==SCREEN+44 and a1 in self.chip
            assert self.get(a1)==a1+48 and self.get(TABLE+8)==a1
            self.moves.append((d0,d1))
            self.put16(a1+6,d0);self.put16(a1+8,d1)
        elif address==GFX-414:
            assert d0 in (2,3)
            mask=self.read(GFX+166,1)[0]
            assert mask&(1<<d0)
            self.uc.mem_write(GFX+166,bytes([mask&~(1<<d0)]))
            self.put32(TABLE+d0*4,0);self.copper(d0,NEUTRAL)
            self.sprite_calls.append('free'+str(d0))
        elif address==GFX-270:
            assert self.depth==0
        elif address==INTUI-66:
            assert a0==SCREEN
            self.sprite_calls.append('close')
            result=int(self.close_ok)
            if result and not self.pending_view:
                self.put32(GFX+34,0);self.put32(GFX+50,IDLE);self.put32(GFX+54,IDLE)
        else:
            return super().on_code(uc,address,size,user)
        self.volatile(uc,result)

    def invoke_any(self,pc,last=0,rest=(),legacy=False):
        uc=self.uc
        for i,r in enumerate(REGS):uc.reg_write(r,0x55004000+i)
        uc.reg_write(UC_M68K_REG_A5,AMOS)
        saved={r:uc.reg_read(r) for r in REGS}
        uc.reg_write(UC_M68K_REG_D3,last&0xffffffff)
        uc.reg_write(UC_M68K_REG_A3,PARAMS)
        if rest:uc.mem_write(PARAMS,pack('>'+str(len(rest))+'I',*(x&0xffffffff for x in rest)))
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A7,STACK)
        uc.mem_write(STACK,pack('>I',STOP))
        try:uc.emu_start(pc,STOP,count=20000000)
        except Exception as exc:
            raise AssertionError(('PC',hex(uc.reg_read(UC_M68K_REG_PC)),'entry',hex(pc))) from exc
        assert uc.reg_read(UC_M68K_REG_PC)==STOP
        assert uc.reg_read(UC_M68K_REG_A7)==STACK+4
        assert all(uc.reg_read(r)==v for r,v in saved.items())
        assert uc.reg_read(UC_M68K_REG_A3)==PARAMS+4*len(rest)
        assert self.depth==0
        if not legacy:assert uc.reg_read(UC_M68K_REG_D2)==0
        return uc.reg_read(UC_M68K_REG_D3)
    def sprite(self,n=1,x=30,y=112,image=1):
        return self.invoke_any(self.entries_sprite['aga sprite'],image,(y,x,n))
    def off(self,n=1):return self.invoke_any(self.entries_sprite['aga sprite off'],n)
    def bankfree(self,n=29):return self.invoke_any(self.entries_sprite['aga sprite bank free'],n)
    def close(self,end=False):return self.invoke_any(GROUP+(0x5a if end else 0x7fa),legacy=True)
    def erase(self):
        self.put32(HEAD,0)
        self.uc.mem_write(self.node,b'\xa5'*self.allocations.pop(self.node))
    def empty(self):
        assert not self.temp_live and not self.chip and not self.named and not self.get(self.cell)
    def root(self):
        assert self.get(self.cell)==self.named+56
        return self.get(self.cell)

def sprite_suite(image,info):
    count=0
    for layout in ('runtime','compiled'):
        def new():
            m=SpriteMachine(image,info,layout)
            assert m.select(29)==1
            return m
        for end in (False,True):
            m=new()
            assert m.sprite()==1
            assert m.sprite_calls==['get2','get3','image']
            p=m.get(m.get(m.root()))
            assert p in m.chip and len(m.temp_live)==3
            before=len(m.temp_allocs)
            m.erase()
            for x in range(32,232,2):assert m.sprite(x=x)==1
            assert m.moves[-1]==(230,112) and len(m.temp_allocs)==before
            assert m.sprite(image=2)==0 and m.off(2)==0
            assert m.off()==1 and m.off()==1
            assert m.sprite_calls[-3:]==['blank','free3','free2']
            assert m.sprite()==1 and len(m.temp_allocs)==before
            m.close(end);m.empty();assert m.get(STATE)==0
            m.close(end);m.empty();count+=1
        for fail in (1,2,3):
            m=new();m.fail_temp_at=fail
            assert m.sprite()==0;m.empty();assert not m.sprite_calls;count+=1
        m=new();m.cmap=bytes(768)
        assert m.sprite()==0;m.empty();assert not m.sprite_calls;count+=1
        m=new();m.palette_mode=False
        assert m.sprite()==0;m.empty();count+=1
        m=new();m.reject_channel=2
        assert m.sprite()==0;m.empty();count+=1
        m=new();m.reject_channel=3
        assert m.sprite()==0 and m.sprite_calls==['get2','free2']
        assert len(m.temp_live)==3
        m.close();m.empty();count+=1
        m=new()
        for kw in ({'x':-1},{'x':305},{'y':241},{'n':0},{'image':2}):
            assert m.sprite(**kw)==0;m.empty();count+=1
        m=new();assert m.sprite()==1
        m.close_ok=False;m.close()
        assert m.get(STATE)==SCREEN and m.get(m.root()+12)==SCREEN
        assert len(m.temp_live)==3
        m.close_ok=True;m.close();m.empty();count+=1
        m=new();assert m.sprite()==1
        m.pending_view=True;m.close()
        assert m.get(STATE)==0 and m.named and not m.get(m.cell)
        assert len(m.temp_live)==3 and m.get(m.named+56+12)==0
        assert m.bankfree()==0 and len(m.temp_live)==3
        m.put32(GFX+34,0);m.put32(GFX+50,IDLE);m.put32(GFX+54,IDLE)
        m.task=TASK+4
        assert m.bankfree()==1;m.empty();count+=1
        m=new();assert m.sprite()==1
        assert m.bankfree(29)==1 and m.bank(29)==fixture()
        m.close();m.empty();count+=1
        print('S1P2I_PUBLIC_ROUTE_PASS',layout,count,flush=True)
    return count

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm',type=Path,required=True)
    cli.add_argument('--historical',type=Path,required=True)
    cli.add_argument('--full',action='store_true')
    args=cli.parse_args()
    for key in ('AGSP_GET_BIN','AGSP_PUBLISH_BIN','AGSP_PIPELINE_BIN'):
        os.environ[key]=str(args.historical)
    image,info=build_s1p2i(args.vasm)
    print('S1P2I_BUILT '+json.dumps(info,sort_keys=True),flush=True)
    n=sprite_suite(image,info)
    print('S1P2I_PUBLIC_CPU_PASS',n,flush=True)
    if args.full:
        chain(image)
        prior,meta=build_l2(args.vasm)
        good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
        verify_linked_source(args.vasm,good)
        assert run_pattern_cases(prior,image)==184
        assert run_cases(image,info)==172
        l2_gate.IMAGE,l2_gate.META=image,meta
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(l2_gate.L2GateA))
        assert result.wasSuccessful() and result.testsRun==10
        print('S1P2I_FULL_GATE_A_PASS '+json.dumps(info,sort_keys=True),flush=True)
        # No second installable file; exact candidate bytes in CI log only.
        encoded=base64.b64encode(image).decode('ascii')
        for i in range(0,len(encoded),2048):
            print(f'S1P2I_BYTES {i//2048:04d} {encoded[i:i+2048]}',flush=True)
if __name__=='__main__':main()
