#!/usr/bin/env python3
"""M18/R68 real 68000 wrapper Gate A with mocked AMOS/Exec/graphics APIs.

Validates interpreted and moved Compiler-V2-style native placements; no
actual WinUAE, hardware Blitter, AMOS Compiler or real Chip allocations.
"""
from struct import pack,unpack
from random import Random
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import Machine,DR,AR,AMOS,EXEC,GFX,STATE,DB,SB,BITMAP,STACK,STOP
from amos_link_test_support import main_table,relocate,MAIN_BASE
from amos_main_abi import declarations
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from build_m18_r68_cblock import build,APIS
from build_m18_r67_ficon_capture import build as build_r67
from m18_cblock_bank_emit import (
    emit_capture,emit_draw,emit_restore,ENTRY_CAPTURE,ENTRY_DRAW,
    ENTRY_RESTORE,GETADR,RESERVE,CHANGE,EFF,HEADER,NAME,MAGIC,
)
from m18_cblock_copy_model import Surface,copy_pixel_oracle,copy_blitter_word_model

ENTRY=0x180000
MOVED=0x1a0000
ARGS=0x58000
NEW=0xc00000
OLD=0xd40000
GUARD=b"R68-CBLOCK-CANARY"
NAMES=("Bnk.GetAdr","Bnk.Reserve","Bnk.Change","Bnk.Eff")
WIDTH,HEIGHT,DEPTH=65,45,8
RBYTES=10

def norm_surface(uc,ptr):
    stride,rows,flags,depth,pad=unpack(">HHBBH",bytes(uc.mem_read(ptr,8)))
    if not 1<=depth<=8:raise ValueError("bad BitMap depth")
    pointers=[unpack(">I",bytes(uc.mem_read(ptr+8+4*i,4)))[0] for i in range(depth)]
    plane_bytes=stride*rows
    return Surface(stride*8,rows,depth,stride,
                   [bytearray(uc.mem_read(p,plane_bytes)) for p in pointers]),pointers

def valid_payload(w,h,depth,x,y,screen,source_bm):
    bpr=((w+15)//16)*2
    plane=bpr*h
    out=bytearray(HEADER+depth*plane)
    out[:8]=MAGIC
    out[8:40]=pack(">HHHHiiIIII",40,1,depth,0,x,y,w,h,bpr,plane)
    for layer in range(depth):
        src=source_bm.planes[layer]; dst=out
        for yy in range(h):
            off=(yy+y)*screen.stride+x//8
            start=40+layer*plane+yy*bpr
            dst[start:start+w//8]=src[off:off+w//8]
    return bytes(out)

class CBlockMachine(Machine):
    def __init__(self,raw,layout="interpreted",*,nonchip=False,fail_at=None,
                 occupied=False,safe=True,corrupt=None):
        super().__init__(raw,None,meta=dict(width=WIDTH,height=HEIGHT,
                                           depth=DEPTH,row_bytes=RBYTES,camg=0x21000))
        self.lib=raw;self.entry=ENTRY if layout=="interpreted" else MOVED
        self.banks={10:OLD}
        self.uc.mem_write(OLD,b"DO-NOT-OVERWRITE-OLD-BANK")
        self.nonchip=nonchip;self.fail_at=fail_at;self.corrupt=corrupt
        self.safeready=safe
        self.calls=[];self.draws=0;self.waits=0;self.getmsg=0;self.reserved=0
        self.type_calls=[];self.type_results=[];self.freed=0
        self.new_total=0
        self.uc.mem_write(NEW+0x200,b"\xf9"*16)
        self.put(DB+12,0x5c000)  # Safe-message port for inactive screen buffer
        self.put(DB+20,1)  # pending Safe acquisition
        self.uc.mem_write(EXEC-534,b"\x4e\x75")
        self.uc.mem_write(EXEC-372,b"\x4e\x75")
        self.uc.mem_write(GFX-198,b"\x4e\x75")
        self.uc.mem_write(GFX-606,b"\x4e\x75")
        table,_=main_table(self.uc)
        self.addr={table[idx]:name for idx,name,*_ in declarations() if name in NAMES}
        for a in self.addr:self.uc.mem_write(a,b"\x4e\x75")
        self.uc.hook_add(UC_HOOK_CODE,self.main_call,begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        _,self.parts=unwrap_native_parts_v2(raw)
        self.occupied=occupied
        if occupied:self.banks[11]=OLD
        self.slot=11
        if corrupt:self.prepare_bank(corrupt=corrupt)

    def load_entry(self,index):
        assert index in (ENTRY_CAPTURE,ENTRY_DRAW,ENTRY_RESTORE)
        self.uc.mem_write(self.entry,relocate(self.parts[index],self.entry,
                          {index+1:self.entry+0x3000},self.uc))
        self.current_index=index

    def prepare_bank(self,w=24,h=16,x=8,y=4,corrupt=None):
        if corrupt is None:corrupt=self.corrupt
        self.new_total=40+8*(((w+15)//16)*2)*h
        # Existing bank is fully Chip and correctly labeled except mutations.
        source,ptrs=norm_surface(self.uc,BITMAP)
        blob=bytearray(valid_payload(w,h,8,x,y,source,source))
        self.uc.mem_write(NEW,bytes(blob))
        self.uc.mem_write(NEW-24,pack(">IIIHH8s",0,len(blob)+16,11,3,0,NAME))
        self.uc.mem_write(NEW+len(blob),GUARD)
        self.banks[11]=NEW
        if corrupt=="magic":self.uc.mem_write(NEW,b"BADMAGIC")
        elif corrupt=="name":self.uc.mem_write(NEW-8,b"BADNAME ")
        elif corrupt=="flags":self.uc.mem_write(NEW-12,bytes.fromhex("0002"))
        elif corrupt=="len":self.put(NEW-20,len(blob)+17)
        elif corrupt=="width":self.put(NEW+24,9999)
        elif corrupt=="stride":self.put(NEW+32,1)
        elif corrupt=="plane":self.put(NEW+36,3)
        elif corrupt=="depth":self.uc.mem_write(NEW+12,b"\x00\x04")
        elif corrupt is not None:raise ValueError(corrupt)

    def _return(self,value=0,ptr=None):
        self.uc.reg_write(DR[0],value&0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000 if ptr is None else ptr)
        self.uc.reg_write(AR[1],0xbad100)
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def main_call(self,uc,address,size,user):
        assert address in self.addr,(hex(address),self.current_index)
        name=self.addr[address]
        self.calls.append(name)
        assert self.a(5)==AMOS
        if name=="Bnk.GetAdr":
            ptr=self.banks.get(self.d(0),0);self._return(ptr,ptr=ptr)
        elif name=="Bnk.Reserve":
            bank,flags,need=self.d(0),self.d(1),self.d(2)
            assert (bank,flags)==(11,3)
            assert bank not in self.banks,"destructive Reserve"
            assert bytes(self.uc.mem_read(self.a(0),8))==NAME
            assert need>40 and need<=1048576
            self.new_total=need
            self.reserved+=1
            self.banks[bank]=NEW
            # Force uninitialized Chip RAM; first creation must explicitly clear padding.
            self.uc.mem_write(NEW,bytes([0xa7])*need)
            self.uc.mem_write(NEW-24,pack(">IIIHH8s",0,need+16,bank,flags,0,NAME))
            self.uc.mem_write(NEW+need,GUARD)
            self._return(NEW,ptr=NEW)
        elif name=="Bnk.Change":
            assert self.banks.get(11)==NEW
            self._return()
        elif name=="Bnk.Eff":
            assert self.d(0)==11 and self.banks.get(11)==NEW
            self.banks.pop(11)
            self.freed+=1
            self._return()

    def os_call(self,uc,address,size,user):
        if address==EXEC-534:
            p=self.a(1)
            self.type_calls.append(p)
            chip=(NEW-24<=p<NEW+self.new_total and not self.nonchip)
            chip|=any(base<=p<base+self.plane_size for base in self.planes)
            # Plane defaults from Machine are real Chip; other memory is not.
            if p==self.fail_at:chip=False
            self.type_results.append((hex(p),bool(chip)))
            self._return(3 if chip else 0)
        elif address==EXEC-372:
            assert self.a(0)==0x5c000,("Safe port missing",hex(self.a(0)))
            self.getmsg+=1
            self._return(0x99999 if self.safeready else 0)
        elif address==GFX-228:
            self.waits+=1
            self._return(0)
        elif address==GFX-198:
            self.uc.mem_write(self.a(1),bytes(128))
            self._return(0)
        elif address==GFX-606:
            src,p=norm_surface(self.uc,self.a(0))
            dest_ptr=self.get(self.a(1)+4)
            dst,q=norm_surface(self.uc,dest_ptr)
            sx,sy,dx,dy,w,h,minterm=(self.d(i) for i in range(7))
            assert minterm==0xc0
            copy_blitter_word_model(src,dst,sx,sy,dx,dy,w,h)
            for addr,plane in zip(q,dst.planes):uc.mem_write(addr,bytes(plane))
            self.draws+=1
            self._return(0)
        else:raise AssertionError(("unexpected OS call",hex(address)))

    def invoke(self,action,bank=11,x=8,y=4,w=24,h=16,method=2,expected=1):
        idx={"capture":ENTRY_CAPTURE,"draw":ENTRY_DRAW,
             "restore":ENTRY_RESTORE}[action]
        self.load_entry(idx)
        self.trace=[]
        def trace(uc,address,size,user):
            if self.entry<=address<self.entry+len(self.parts[idx]):
                self.trace.append(address-self.entry)
                if len(self.trace)>55:self.trace.pop(0)
        self.uc.hook_add(UC_HOOK_CODE,trace,begin=self.entry,end=self.entry+len(self.parts[idx]))
        values=(bank,x,y,w,h,method) if action=="capture" else (
                 (bank,x,y,method) if action=="draw" else (bank,method))
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        for i,arg in enumerate(reversed(values[:-1])):self.put(ARGS+4*i,arg)
        self.uc.reg_write(DR[3],method&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        # Supervisor SR must be set BEFORE A7: Unicorn swaps USP/SSP.
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK);self.put(STACK,STOP)
        try:self.uc.emu_start(self.entry,STOP,count=6000000)
        except Exception as exc:
            raise AssertionError(("R68 native crash",str(exc),
                hex(self.uc.reg_read(UC_M68K_REG_PC)),action,values,
                self.calls[-10:],list(map(hex,self.type_calls[-8:])))) from exc
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4
        assert self.a(3)==ARGS+4*(len(values)-1)
        assert self.d(2)==0
        assert self.d(3)==expected,(action,values,self.d(3),self.calls[-9:],
                                    self.type_results[-8:],
                                    "TRACE",self.trace,
                                    "LABELS",(emit_capture if idx==67 else emit_draw if idx==68 else emit_restore)()[1])
        for r,value in saved.items():
            if r not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(r)==value,("R68 clobbered register",r)
        assert bytes(self.uc.mem_read(OLD,25))==b"DO-NOT-OVERWRITE-OLD-BANK"
        return expected

def main():
    blob,meta=build()
    assert build()[0]==blob,"non-reproducible builder"
    old,_=build_r67()
    _,before=unwrap_native_parts_v2(old)
    _,parts=unwrap_native_parts_v2(blob)
    assert len(before)==67 and len(parts)==70
    assert parts[:66]==before[:66]
    assert parts[66]==before[66]+b"GetP"
    gens=(emit_capture,emit_draw,emit_restore)
    for gen,entry in zip(gens,(67,68,69)):
        native,labels=gen()
        assert parts[entry].startswith(native)
        dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
        chunks=(native[:labels["bank_name"]],
                native[labels["copy_core"]:])
        for piece in chunks:
            for marker in (GETADR,RESERVE,CHANGE,EFF):
                piece=piece.replace(marker,bytes.fromhex("4eb900030000"))
            asm=list(dis.disasm(piece,0))
            assert sum(x.size for x in asm)==len(piece),("bad 68000 opcode",gen,len(piece))
    assert meta["commands"]==64 and meta["ap20_entries"]==71

    checks=0
    for layout in ("interpreted","compiled"):
        for method,w in ((0,8),(0,24),(1,16),(1,32),(2,8),(2,24)):
            m=CBlockMachine(blob,layout)
            first_x=16 if method==1 else 8
            checks+=m.invoke("capture",x=first_x,w=w,method=method)
            assert m.reserved==1 and m.freed==0
            assert m.uc.mem_read(NEW,8)==MAGIC
            assert bytes(m.uc.mem_read(NEW+m.new_total,len(GUARD)))==GUARD
            src,ptrs=norm_surface(m.uc,BITMAP)
            actual=bytes(m.uc.mem_read(NEW,m.new_total))
            assert actual==valid_payload(w,16,DEPTH,first_x,4,src,src),(
                "capture mismatch",layout,method,w)
            if method==1:assert first_x%16==0
            # No additional Bnk.Reserve on recapture, only new pixel data.
            # Reuse same bank: no allocation or Chip Free change.
            checks+=m.invoke("capture",x=16,w=w,method=method)
            assert m.reserved==1
            before=[bytes(m.uc.mem_read(p,m.plane_size)) for p in m.planes]
            src_bm=Surface(m.stride*8,HEIGHT,DEPTH,m.stride,
                           [bytearray(p) for p in before])
            bpr=((w+15)//16)*2
            plane_bytes=bpr*16
            raw=bytes(m.uc.mem_read(NEW+40,DEPTH*plane_bytes))
            block=Surface(bpr*8,16,DEPTH,bpr,
                    [bytearray(raw[i*plane_bytes:(i+1)*plane_bytes])
                     for i in range(DEPTH)])
            expected_draw=src_bm.clone()
            copy_pixel_oracle(block,expected_draw,0,0,32,22,w,16)
            checks+=m.invoke("draw",x=32,y=22,method=method)
            assert [bytes(m.uc.mem_read(p,m.plane_size))
                    for p in m.planes]==list(expected_draw.signature()),(
                    "R68 native draw pixels differ",layout,method,w)
            assert m.freed==0
            expected_restore=expected_draw.clone()
            copy_pixel_oracle(block,expected_restore,0,0,16,4,w,16)
            checks+=m.invoke("restore",method=method)
            assert [bytes(m.uc.mem_read(p,m.plane_size))
                    for p in m.planes]==list(expected_restore.signature()),(
                    "R68 native restore pixels differ",layout,method,w)
            assert m.reserved==1
            assert bytes(m.uc.mem_read(NEW+m.new_total,len(GUARD)))==GUARD
        for invalid in (
            dict(bank=4),dict(bank=-1),dict(bank=65536),
            dict(x=1),dict(x=-1),dict(x=56),
            dict(y=40),dict(y=-1),dict(w=7),dict(w=0),dict(h=0),
            dict(h=45),dict(method=3),dict(method=-1),
            dict(method=1,w=24),dict(method=1,x=8),
        ):
            m=CBlockMachine(blob,layout)
            checks+=m.invoke("capture",expected=0,**invalid)
            assert 11 not in m.banks and m.reserved==0
        for mutate in ("magic","name","flags","len","width","stride","plane","depth"):
            m=CBlockMachine(blob,layout,corrupt=mutate)
            checks+=m.invoke("draw",method=2,expected=0)
            assert m.uc.mem_read(OLD,25)==b"DO-NOT-OVERWRITE-OLD-BANK"
        for extra in (dict(occupied=True),dict(nonchip=True)):
            m=CBlockMachine(blob,layout,**extra)
            checks+=m.invoke("capture",expected=0)
            assert m.reserved==(1 if extra.get("nonchip") else 0)
        m=CBlockMachine(blob,layout,safe=False)
        # Keep pending Safe=1: GetMsg must fail and clean up the new bank.
        m.put(DB+20,1)
        checks+=m.invoke("capture",expected=0)
        assert m.freed==1
        m=CBlockMachine(blob,layout,fail_at=NEW+40)
        checks+=m.invoke("capture",expected=0)
        assert m.freed==0 or m.freed==1
    print("M18/R68 CBLOCK RAW CHIP GATE A PASS",checks,
          "68000 native ABI/planar/Chip/Bank/collision/relocation cases")
    print("R68_CANDIDATE_SHA256",meta["sha256"],"BYTES",meta["bytes"],
          "NO WinUAE Gate B / Compiler C")


if __name__=="__main__":
    main()
