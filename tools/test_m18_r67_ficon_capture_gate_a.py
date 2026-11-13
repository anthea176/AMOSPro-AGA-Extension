#!/usr/bin/env python3
"""R67 Gate A: actual 68000 FICON8 capture from private AGA back buffer.

Builds exact R67 AP20 binary in memory; executes the native entry for
interpreted and separately placed Compiler-V2-style relocations.
Mocks AMOS GetAdr, Exec TypeOfMem/GetMsg, graphics WaitBlit and checks
pixel-exact 16x16x8 planar output via independent chunky-source oracle.
NO actual WinUAE/AMOS Interpreter/Compiler Gate B/C is claimed.
"""
from struct import pack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC,UC_M68K_REG_SR
from test_m5_generic import Machine,DR,AR,AMOS,EXEC,GFX,STATE,DB,SB,BITMAP,STACK,STOP
from amos_link_test_support import main_table,relocate,MAIN_BASE
from amos_main_abi import declarations
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from m18_ficon16_model import build_bank,parse_bank
from m18_ficon_bank_put_model import put_chunky
from build_m18_r67_ficon_capture import build,API
from build_m18_r66_fichip_dynamic import build as build_r66
from m18_ficon_capture_emit import emit_ficon_capture,ENTRY_INDEX,GETADR_MARKER

WIDTH,HEIGHT,DEPTH=65,45,8
ROW_BYTES=10
DEST=0xe00000
ARGUMENTS=0x58000
ENTRY=0x180000
COMPILED=0x1a0000
SB_ALT=0x5b100
BMP_ALT=0x5b000
SAFE_PORT=0x5c000
SAFE_MSG=0x5c100
PLANES_ALT=tuple(0xa00000+i*0x50000 for i in range(8))
GUARD=b"R67-BANK-CANARY"
PENDING=1
OLDPIX=(bytes([0])*256,bytes([255])*256,
        bytes(range(256)),bytes((x*19+y*3)&255 for y in range(16) for x in range(16)))
BANK_DATA=build_bank(OLDPIX)

def screen_pixel(x,y,front):
    if (x+y)%11==0:return 0
    if front==1:
        return ((x*23+y*17+31) ^ 0x80)&255
    return (x*17+y*29+5*(x>>2))&255

def encode_planes(stride,height,front):
    planes=[bytearray([0x3c]*stride*height) for _ in range(8)]
    for plane in range(8):
        for y in range(height):
            for x in range(WIDTH):
                off=y*stride+(x>>3)
                mask=1<<(7-(x&7))
                if screen_pixel(x,y,front)&(1<<plane):
                    planes[plane][off]|=mask
                else:planes[plane][off]&=~mask
    return tuple(bytes(p) for p in planes)

class CaptureMachine(Machine):
    def __init__(self,lib,layout="interpreted",front=0,pending=0,
                 safe_ready=True,bank_flags=1,mutate=None,fail_at=None):
        super().__init__(lib,None,meta=dict(width=WIDTH,height=HEIGHT,
            depth=DEPTH,row_bytes=ROW_BYTES,camg=0x21000))
        self.front=front
        self.pending=pending
        self.main_calls=[]
        self.type_calls=[]
        self.getmsg_count=0
        self.waitblit_count=0
        self.safe_ready=safe_ready
        self.fail_at=fail_at
        self.dest=BANK_DATA
        self.uc.mem_write(DEST-24,pack(">IIIHH8s",0,len(self.dest)+16,12,
                                          bank_flags,0,b"FICON8  "))
        self.uc.mem_write(DEST,self.dest)
        self.uc.mem_write(DEST+len(self.dest),GUARD)
        self.banks={12:DEST}
        self.put(DB,SB_ALT);self.put(DB+4,SB)
        self.put(DB+8,front);self.put(DB+12,SAFE_PORT)
        self.put(DB+20,pending)
        self.put(SB_ALT,BMP_ALT)
        self.uc.mem_write(BMP_ALT,pack(">HHBBH",self.stride,HEIGHT,0,DEPTH,0))
        self.expected_planes={}
        for i,p in enumerate(self.planes):
            self.put(BITMAP+8+i*4,p)
        for i,p in enumerate(PLANES_ALT):
            self.put(BMP_ALT+8+i*4,p)
        for key,pointers in ((0,self.planes),(1,PLANES_ALT)):
            expected=encode_planes(self.stride,HEIGHT,key)
            self.expected_planes[key]=expected
            for address,plane in zip(pointers,expected):
                self.uc.mem_write(address,plane)
        self.physical_before=tuple(tuple(
            bytes(self.uc.mem_read(pointer,self.plane_size))
            for pointer in pointers)
            for pointers in (self.planes,PLANES_ALT))
        table,_=main_table(self.uc)
        idx=next(i for i,name,*_ in declarations() if name=="Bnk.GetAdr")
        self.getadr=table[idx]
        self.uc.mem_write(self.getadr,b"\x4e\x75")
        for a in (EXEC-534,EXEC-372,GFX-228):
            self.uc.mem_write(a,b"\x4e\x75")
        self.uc.hook_add(UC_HOOK_CODE,self.main_call,begin=MAIN_BASE,end=MAIN_BASE+0x5000)
        _,parts=unwrap_native_parts_v2(lib)
        assert len(parts)==ENTRY_INDEX+1
        self.entry=ENTRY if layout=="interpreted" else COMPILED
        self.uc.mem_write(self.entry,relocate(parts[ENTRY_INDEX],self.entry,
                 {ENTRY_INDEX+1:self.entry+0x2000},self.uc))
        if mutate:mutate(self)
        self.before=bytes(self.uc.mem_read(DEST,len(self.dest)))
        self.guard_before=bytes(self.uc.mem_read(DEST+len(self.dest),len(GUARD)))

    def _return(self,val,ptr=None):
        self.uc.reg_write(DR[0],val&0xffffffff)
        self.uc.reg_write(DR[1],0xdeadbeef)
        self.uc.reg_write(AR[0],0xbad000 if ptr is None else ptr)
        self.uc.reg_write(AR[1],0xbad100 if ptr is None else ptr)
        sp=self.a(7)
        self.uc.reg_write(AR[7],sp+4)
        self.uc.reg_write(UC_M68K_REG_PC,self.get(sp))

    def main_call(self,uc,address,size,user):
        assert address==self.getadr,("unexpected main service",hex(address))
        self.main_calls.append("Bnk.GetAdr")
        assert self.a(5)==AMOS
        ptr=self.banks.get(self.d(0),0)
        self._return(ptr,ptr=ptr)

    def os_call(self,uc,address,size,user):
        if address==EXEC-534:
            p=self.a(1)
            self.type_calls.append(p)
            bank=(DEST-24<=p<DEST+len(self.dest))
            bitmap=any(start<=p<start+self.plane_size
                       for start in (*self.planes,*PLANES_ALT))
            val=1 if bank else 3 if bitmap else 0
            if p==self.fail_at:val=0
            self._return(val)
        elif address==EXEC-372:
            self.getmsg_count+=1
            assert self.a(0)==SAFE_PORT
            self._return(SAFE_MSG if self.safe_ready else 0)
        elif address==GFX-228:
            self.waitblit_count+=1
            self._return(0)
        else:raise AssertionError(("unexpected OS call",hex(address)))

    def check(self,bank=12,icon=2,x=7,y=3,expected=True,limit=4_000_000):
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGUMENTS)
        for i,v in enumerate((x,icon,bank)):
            self.put(ARGUMENTS+i*4,v&0xffffffff)
        self.uc.reg_write(DR[3],y&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        try:self.uc.emu_start(self.entry,STOP,count=limit)
        except Exception as err:
            raise AssertionError(("R67 68000 exception",str(err),
              hex(self.uc.reg_read(UC_M68K_REG_PC)),bank,icon,x,y,
              self.front,self.main_calls,list(map(hex,self.type_calls[-10:])))) from err
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP
        assert self.a(7)==STACK+4 and self.a(3)==ARGUMENTS+12
        assert self.d(2)==0 and self.d(3)==int(expected),(
             "wrong capture status",self.d(3),bank,icon,x,y,self.main_calls,
             list(map(hex,self.type_calls[-10:])))
        for r,v in saved.items():
            if r not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(r)==v,("register clobbered",r)
        for pointers,before in zip((self.planes,PLANES_ALT),self.physical_before):
            assert all(bytes(self.uc.mem_read(p,self.plane_size))==b for p,b in zip(pointers,before)),("screen modified",bank,x,y)
        assert bytes(self.uc.mem_read(DEST+len(self.dest),len(GUARD)))==self.guard_before
        after=bytes(self.uc.mem_read(DEST,len(self.dest)))
        assert self.main_calls==(["Bnk.GetAdr"] if 5<=bank<=65535
             and 1<=icon<=4096 and 0<=x<=4096 and 0<=y<=4096 else [])
        if expected:
            current=bytes(screen_pixel(xx,yy,self.front)
                          for yy in range(y,y+16) for xx in range(x,x+16))
            expected_payload=put_chunky(self.before,icon,current,0)
            assert after==expected_payload,(
                "pixel mismatch",self.front,icon,x,y,
                next((k for k,(a,b) in enumerate(zip(after,expected_payload)) if a!=b),None))
            assert parse_bank(after).count==4
            assert self.waitblit_count==1
            assert self.getmsg_count==int(bool(self.pending & 1))
            assert self.get(DB+20)==(self.pending & ~1)
        else:
            assert after==self.before,("rejected capture modified bank",bank,icon,x,y)
            assert self.waitblit_count==0
        return 1

def mutated(kind):
    def mutate(m):
        if kind=="name":m.uc.mem_write(DEST-8,b"AGAPIC  ")
        elif kind=="count":m.uc.mem_write(DEST+4,b"\x00\x03")
        elif kind=="flags":m.uc.mem_write(DEST-12,b"\x00\x02")
        elif kind=="length":m.put(DEST-20,len(BANK_DATA)+17)
        elif kind=="header_w":m.uc.mem_write(DEST+6,b"\x00\x20")
        elif kind=="bank_num":m.put(DEST-16,13)
        elif kind=="no_bank":m.banks.pop(12)
        elif kind=="no_state":m.put(AMOS+456,0)
        elif kind=="no_db":m.put(STATE+32,0)
        elif kind=="no_screen":m.put(STATE+0,0)
        elif kind=="screen_depth":m.put(STATE+28,7)
        elif kind=="small_width":m.put(STATE+12,15)
        elif kind=="small_height":m.put(STATE+16,15)
        elif kind=="bad_back":m.put(DB+4,0)
        elif kind=="front_index":m.put(DB+8,2)
        elif kind=="bitmap_depth":m.uc.mem_write(BITMAP+5,b"\x04")
        elif kind=="bitmap_stride":m.uc.mem_write(BITMAP,b"\x00\x02")
        elif kind=="bitmap_rows":m.uc.mem_write(BITMAP+2,b"\x00\x0f")
        elif kind=="missing_plane":m.put(BITMAP+8+7*4,0)
        elif kind=="odd_plane":m.put(BITMAP+8+7*4,m.planes[-1]+1)
        else:raise ValueError(kind)
    return mutate

def main():
    lib,meta=build()
    assert build()[0]==lib,"R67 nondeterministic"
    old,_=build_r66()
    _,previous=unwrap_native_parts_v2(old)
    _,parts=unwrap_native_parts_v2(lib)
    assert len(previous)==66 and len(parts)==67
    assert parts[:65]==previous[:65] and parts[65]==previous[65]+b"GetP"
    native,labels=emit_ficon_capture()
    assert parts[66]==native and native.count(GETADR_MARKER)==1
    assert {"check_plane","safe","pixel","row","fail"}<=set(labels)
    replaced=native[:].replace(GETADR_MARKER,bytes.fromhex("4eb900030000"))
    inst=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(replaced,0))
    assert sum(x.size for x in inst)==len(native),("invalid M68000 opcode",len(native),sum(x.size for x in inst))
    assert not any(x.mnemonic.lower() in ("illegal","dc.w","trap","stop") for x in inst)
    assert meta["commands"]==61 and meta["ap20_entries"]==68
    cases=0
    for layout in ("interpreted","compiled"):
        for front in (0,1):
            for x,y in ((0,0),(1,1),(7,3),(8,8),(15,3),(16,4),
                        (31,11),(49,29),(0,29),(49,0)):
                for icon in (1,2,3,4):
                    cases+=CaptureMachine(lib,layout,front).check(icon=icon,x=x,y=y)
        for flag in (0,1,3):
            cases+=CaptureMachine(lib,layout,bank_flags=flag).check()
        for args in (dict(bank=4),dict(bank=65536),dict(bank=-1),
                     dict(icon=0),dict(icon=5),dict(icon=-1),dict(icon=4097),
                     dict(x=-1),dict(y=-1),dict(x=50),dict(y=30),
                     dict(x=4097),dict(y=4097)):
            cases+=CaptureMachine(lib,layout).check(expected=False,**args)
        for kind in ("name","count","flags","length","header_w",
                     "bank_num","no_bank","no_state","no_db","no_screen",
                     "screen_depth","small_width","small_height",
                     "bad_back","front_index","bitmap_depth",
                     "bitmap_stride","bitmap_rows","missing_plane","odd_plane"):
            cases+=CaptureMachine(lib,layout,mutate=mutated(kind)).check(expected=False)
        cases+=CaptureMachine(lib,layout,pending=1,safe_ready=False).check(expected=False)
        cases+=CaptureMachine(lib,layout,pending=1,safe_ready=True).check()
        cases+=CaptureMachine(lib,layout,fail_at=DEST+len(BANK_DATA)-1).check(expected=False)
        cases+=CaptureMachine(lib,layout,fail_at=0x600000+7*0x80000+44*18+8).check(expected=False,
                                           x=49,y=29)
    print("M18/R67 FICON8 SCREEN CAPTURE GATE A PASS",cases,
          "native 68000 tests, 2 ABI layouts; planar/edge/mask/flags/safe guards")
    print("R67_CANDIDATE_SHA256",meta["sha256"],"BYTES",meta["bytes"],
          "NO WinUAE Gate B OR Compiler C")
if __name__=="__main__":
    main()
