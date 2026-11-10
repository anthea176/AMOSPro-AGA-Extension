"""Execute actual candidate 68k instructions with mocked DOS/Exec/graphics calls.

Requires unicorn and capstone (pip install unicorn capstone). This is CPU/ABI
validation, NOT Intuition/Copper/WinUAE visual validation. System calls deliberately
clobber D1/A0/A1 to expose accidental reliance on volatile registers.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys
import unittest
from audit_ap20 import parse
from build_m5_generic import build, ROOT
from validate_ilbm import inspect, decode

try:
    from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
    from unicorn.m68k_const import *
    from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
except ImportError as error:
    raise SystemExit('Install test dependencies: python -m pip install unicorn capstone') from error

DR=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7]
AR=[UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
CODE=0x100000; EXEC=0x20000; DOSLIB=0x22000; GFX=0x24000; INTUI=0x26000
STATE=0x50000; AMOS=0x51000; NAME=0x52000; DB=0x53000; SB=0x54000; BITMAP=0x55000; SCREEN=0x56000
STACK=0xf00000; STOP=0x10000

class Machine:
    def __init__(self,raw,data,meta=None,allocation_failure=0,pending_blit=False):
        self.p=parse(raw); self.data=data; self.meta=meta; self.cursor=0
        self.uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        self.uc.mem_map(0,0x1000000); self.uc.mem_write(CODE,self.p.code)
        self.uc.mem_write(STOP,b'\x4e\x71')
        self.next=0x200000; self.owned={}; self.allocation_failure=allocation_failure; self.alloc_calls=0
        self.palette=None; self.plane_writes=0; self.planes=[]; self.stride=0; self.plane_size=0
        self.open_files=0; self.open_libraries=0
        self.pending_blit=pending_blit
        self.put(4,EXEC); self.put(AMOS+456,STATE)
        self.uc.mem_write(NAME,b'\0\x08test.iff')
        self.uc.mem_write(EXEC+297,b'\x02'); self.uc.mem_write(GFX+236,b'\x0c')
        if meta:
            w,h,d=meta['width'],meta['height'],meta['depth']
            mode=meta['camg']; mode=mode if mode&0xffff0000 else mode&0x8efd
            for off,v in ((0,SCREEN),(4,INTUI),(8,GFX),(12,w),(16,h),(20,1<<d),(24,mode),(28,d),(32,DB)):
                self.put(STATE+off,v)
            self.put(DB,SB); self.put(DB+4,SB); self.put(DB+8,0); self.put(SB,BITMAP)
            # Larger physical stride exercises row padding (including 724 px).
            self.stride=meta['row_bytes']+8; self.plane_size=self.stride*h
            self.uc.mem_write(BITMAP,struct.pack('>HHBBH',self.stride,h,0,d,0))
            for i in range(d):
                address=0x600000+i*0x80000; self.planes.append(address); self.put(BITMAP+8+4*i,address)
                self.uc.mem_write(address,b'\xa5'*self.plane_size)
        for base,offsets in ((EXEC,(-684,-690,-552,-414)),(DOSLIB,(-30,-42,-36)),(GFX,(-882,-270,-228)),(INTUI,(-612,))):
            for offset in offsets: self.uc.mem_write(base+offset,b'\x4e\x75')
        self.uc.hook_add(UC_HOOK_CODE,self.os_call,begin=0x1f000,end=0x26fff)
        self.uc.hook_add(UC_HOOK_MEM_WRITE,self.write_guard,begin=0x600000,end=0xa00000)

    def put(self,address,value): self.uc.mem_write(address,struct.pack('>I',value&0xffffffff))
    def get(self,address): return struct.unpack('>I',self.uc.mem_read(address,4))[0]
    def d(self,n): return self.uc.reg_read(DR[n])
    def a(self,n): return self.uc.reg_read(AR[n])
    def cstring(self,address):
        out=bytearray()
        while True:
            b=self.uc.mem_read(address,1)[0]; address+=1
            if not b:return bytes(out)
            out.append(b)
    def write_guard(self,uc,access,address,size,value,user):
        assert any(p<=address and address+size<=p+self.plane_size for p in self.planes),hex(address)
        self.plane_writes+=1

    def os_call(self,uc,address,size,user):
        result=0
        if address==EXEC-684:
            self.alloc_calls+=1
            if self.alloc_calls!=self.allocation_failure:
                n=self.d(0); assert 0<n<=0x200000,n
                result=self.next; self.next+=(n+15)&~15
                self.owned[result]=n; uc.mem_write(result,b'\0'*n)
        elif address==EXEC-690:
            assert self.a(1) in self.owned,hex(self.a(1)); del self.owned[self.a(1)]
        elif address==EXEC-552:
            name=self.cstring(self.a(1)); result={b'dos.library':DOSLIB,b'graphics.library':GFX,b'intuition.library':INTUI}[name]
            self.open_libraries+=1
        elif address==EXEC-414:
            self.open_libraries-=1
        elif address==DOSLIB-30:
            if self.data is not None: result=7; self.open_files+=1
        elif address==DOSLIB-42:
            n=self.d(3); block=self.data[self.cursor:self.cursor+n]; self.cursor+=len(block)
            uc.mem_write(self.d(2),block); result=len(block)
        elif address==DOSLIB-36:
            self.open_files-=1
        elif address==GFX-882:
            assert self.a(0)==SCREEN+44
            table=self.a(1); header=self.get(table); count=header>>16
            assert header&65535==0 and 0<count<=256
            self.palette=[self.get(table+4+4*i) for i in range(count*3)]
            assert self.get(table+4+count*12)==0
        elif address in (GFX-270,GFX-228):
            # Model the final asynchronous SB_COPY_BITMAP plane completing
            # at the next synchronization. CPU work alone is not a barrier.
            if self.pending_blit:
                for row in range(self.meta['height']):
                    uc.mem_write(self.planes[-1]+row*self.stride,b'\0'*self.meta['row_bytes'])
                self.pending_blit=False
        elif address==INTUI-612:
            table=self.a(1); tags={}
            while self.get(table):
                tags[self.get(table)]=self.get(table+4); table+=8
            assert tags[0x8000003b]==1 and tags[0x80000039]==1
            self.open_tags=tags; result=SCREEN
        else: raise AssertionError('Unexpected OS call '+hex(address))
        # Amiga library ABI: D0,D1,A0,A1 volatile; everything else preserved.
        uc.reg_write(DR[0],result)
        uc.reg_write(DR[1],0xdeadbeef); uc.reg_write(AR[0],0xbad000); uc.reg_write(AR[1],0xbad100)
        pc=self.get(self.a(7)); uc.reg_write(AR[7],self.a(7)+4); uc.reg_write(UC_M68K_REG_PC,pc)

    def execute(self,index,field=None,open_args=None,a3_delta=0):
        for i,r in enumerate(DR): self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]): self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS); self.uc.reg_write(AR[3],0x58000)
        if index==14:
            self.put(0x58000,NAME); self.uc.reg_write(DR[3],field)
        elif index==6:
            w,h,colors,mode=open_args
            self.put(0x58000,colors); self.put(0x58004,h); self.put(0x58008,w); self.uc.reg_write(DR[3],mode)
        else:self.uc.reg_write(DR[3],NAME)
        before={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(AR[7],STACK); self.put(STACK,STOP)
        # Supervisor mode prevents an implicit A7 bank switch by the emulator.
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.uc.emu_start(CODE+self.p.starts[index],STOP,count=20000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,hex(self.uc.reg_read(UC_M68K_REG_PC))
        assert self.a(7)==STACK+4,hex(self.a(7))
        for r,v in before.items():
            if r==AR[3] and a3_delta:
                assert self.uc.reg_read(r)==((v+a3_delta)&0xffffffff),(r,hex(v),hex(self.uc.reg_read(r)))
                continue
            if r in (DR[2],DR[3]) or (index==6 and r==AR[3]):continue
            assert self.uc.reg_read(r)==v,(r,hex(v),hex(self.uc.reg_read(r)))
        assert self.d(2)==0
        if index!=6: assert not self.owned and self.open_files==0 and self.open_libraries==0
        return self.d(3)

    def assert_pixels(self,expected):
        for p,source in zip(self.planes,expected):
            actual=self.uc.mem_read(p,self.plane_size)
            rb=self.meta['row_bytes']
            for row in range(self.meta['height']):
                assert actual[row*self.stride:row*self.stride+rb]==source[row*rb:(row+1)*rb]
                assert actual[row*self.stride+rb:(row+1)*self.stride]==b'\xa5'*(self.stride-rb)
        flat=bytes(v for rgb in self.meta['cmap_rgb'] for v in rgb)
        assert self.palette==[v*0x01010101 for v in flat]

def chunk(k,data): return k+struct.pack('>I',len(data))+data+(b'\0' if len(data)&1 else b'')
def fixture(width=17,height=2,depth=2,compression=1,mask=0,camg=0):
    rb=((width+15)//16)*2
    raw=bytes((i*19)&255 for i in range(rb*height*(depth+(mask==1))))
    body=raw if compression==0 else b''.join(b'\x80'+bytes([rb-1])+raw[i:i+rb] for i in range(0,len(raw),rb))
    chunks=chunk(b'JUNK',b'x')+chunk(b'BMHD',struct.pack('>HHhhBBBBHBBhh',width,height,0,0,depth,mask,compression,0,0,1,1,width,height))
    chunks+=chunk(b'CAMG',struct.pack('>I',camg))+chunk(b'CMAP',bytes(i&255 for i in range(3*(1<<depth))))+chunk(b'BODY',body)
    return b'FORM'+struct.pack('>I',len(chunks)+4)+b'ILBM'+chunks

def replace_chunk(data,kind,payload):
    meta,_=inspect(data)
    parts=[]
    for ch in meta['chunks']:
        k=ch['id'].encode('latin1'); start=ch['offset']+8
        if k==kind:
            if payload is not None: parts.append(chunk(k,payload))
        else: parts.append(chunk(k,data[start:start+ch['size']]))
    content=b'ILBM'+b''.join(parts)
    return b'FORM'+struct.pack('>I',len(content))+content

def run(builder=build, report_name='GENERIC_CPU_TESTS.json'):
    raw,report=builder(); results=[]
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    parsed=parse(raw)
    for index,labels in ((13,report['loader_labels']),(14,report['info_labels'])):
        code=parsed.code[parsed.starts[index]:parsed.starts[index]+labels['dosname']]
        instructions=list(dis.disasm(code,0)); boundaries={i.address for i in instructions}
        assert sum(i.size for i in instructions)==len(code)
        assert all(v in boundaries for k,v in labels.items() if k!='dosname')
        assert all(i.mnemonic!='dc.w' for i in instructions)
    paths=sorted((p for p in ROOT.rglob('*') if p.suffix.lower() in ('.iff','.ilbm') and '.git' not in p.parts),
                 key=lambda p:p.relative_to(ROOT).as_posix().lower())
    for path in paths:
        data=path.read_bytes(); meta,body=inspect(data); planes,_=decode(meta,body)
        m=Machine(raw,data,meta); assert m.execute(13)==1,path; m.assert_pixels(planes)
        mode=meta['camg']; mode=mode if mode&0xffff0000 else mode&0x8efd
        values=(meta['width'],meta['height'],meta['depth'],meta['cmap_entries'],meta['compression'],meta['camg'],mode,1<<meta['depth'])
        for field,value in enumerate(values): assert Machine(raw,data).execute(14,field)==value,(path,field)
        o=Machine(raw,None); assert o.execute(6,open_args=(meta['width'],meta['height'],1<<meta['depth'],mode))==1
        assert o.open_tags[0x80000023]==meta['width'] and o.open_tags[0x80000024]==meta['height']
        assert o.open_tags[0x80000025]==meta['depth'] and o.open_tags[0x80000032]==mode
        results.append(dict(file=path.relative_to(ROOT).as_posix(),cpu_decode='PASS',all_palette_indices='PASS',picinfo_fields='PASS',open_tags='PASS'))
        print('68k PASS',path.name,flush=True)
    data=fixture(); meta,body=inspect(data)
    malformed=[None,b'',data[:11],data[:30],data[:-1],data[:8]+b'NOPE'+data[12:]]
    # Every truncation of a compact valid ILBM is rejected, including padding.
    malformed.extend(data[:n] for n in range(12,len(data)))
    # Valid FORM/read lengths but hostile inner chunks and ByteRun1 streams.
    bmhd=next(ch for ch in meta['chunks'] if ch['id']=='BMHD')
    header=data[bmhd['offset']+8:bmhd['offset']+28]
    for kind,payload in ((b'BMHD',None),(b'BODY',None),(b'CMAP',None),(b'CMAP',b'12'),
                         (b'CAMG',b'123'),(b'CAMG',b'\x12\x34\0\0'),
                         (b'BODY',b'\x7f'+b'x'*128),(b'BODY',b'\x81x'),
                         (b'BODY',b'\x80'),(b'BODY',b'\x03x'),
                         (b'BODY',body+b'\0x')):
        malformed.append(replace_chunk(data,kind,payload))
    for off,value in ((8,0),(8,9),(9,3),(10,2)):
        h=bytearray(header); h[off]=value; malformed.append(replace_chunk(data,b'BMHD',bytes(h)))
    for off in (0,2):
        h=bytearray(header); h[off:off+2]=b'\0\0'; malformed.append(replace_chunk(data,b'BMHD',bytes(h)))
    corrupt=bytearray(data); corrupt[16:20]=b'\xff'*4; malformed.append(bytes(corrupt))
    duplicate=data+chunk(b'BMHD',header)
    malformed.append(duplicate[:4]+struct.pack('>I',len(duplicate)-8)+duplicate[8:])
    for bad in malformed:
        m=Machine(raw,bad,meta); assert m.execute(13)==0; assert m.plane_writes==0 and m.palette is None
    for off,value in ((12,meta['width']+1),(16,meta['height']+1),(28,meta['depth']+1),(24,0x8000),(32,0)):
        m=Machine(raw,data,meta); m.put(STATE+off,value); assert m.execute(13)==0
        assert m.plane_writes==0 and m.palette is None
    for failure in (1,2,3):
        m=Machine(raw,data,meta,allocation_failure=failure); assert m.execute(13)==0; assert m.plane_writes==0
    for comp in (0,1):
        for mask in (0,1,2):
            data=fixture(compression=comp,mask=mask); meta,body=inspect(data); planes,_=decode(meta,body)
            m=Machine(raw,data,meta); assert m.execute(13)==1; m.assert_pixels(planes)
    for depth,mode in ((6,0x80),(6,0x800),(8,0x800),(1,0),(8,0)):
        data=fixture(depth=depth,camg=mode); meta,body=inspect(data); planes,_=decode(meta,body)
        m=Machine(raw,data,meta); assert m.execute(13)==1; m.assert_pixels(planes)
    # The complete stream may end with legal NOPs, but never extra output.
    data=fixture(); meta,body=inspect(data); data=replace_chunk(data,b'BODY',body+b'\x80\x80')
    m=Machine(raw,data,meta); assert m.execute(13)==1; m.assert_pixels(decode(meta,body)[0])
    output=dict(candidate_sha256=hashlib.sha256(raw).hexdigest(),files=results,malformed_cases=len(malformed),
                mismatch_cases=5,allocation_failures=3,synthetic_cases=12,
                limitation='Mocked AmigaOS calls: not a visual/WinUAE/AMOS Compiler validation.')
    (ROOT/'docs'/report_name).write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print('PASS:',len(results),'repository images; malformed, mismatch, allocation and synthetic cases')
    return output

if __name__=='__main__': run()
