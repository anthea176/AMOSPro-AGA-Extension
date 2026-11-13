#!/usr/bin/env python3
"""R61 P4 full 68000 AP20/Compiler V2 bank/Safe/FIcon native Gate A.

Symbolic AMOS GetAdr and Exec OS hooks are simulated. Real machine-code
wrapper and real P3 renderer run; output is checked with independent pixels.
No installed R61 Lib or actual WinUAE validation is claimed.
"""
from random import Random
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_PC
from test_m16_capture import CaptureMachine,NEW_CODE
from test_m16_image_draw_r45 import BANK,ARGS,sample_pixels
from test_m5_generic import AMOS,AR,DR,STACK,STOP,DB
from amos_link_test_support import relocate
from m18_ficon16_model import build_bank,parse_bank
from compiler_relocation import unpack_ap20,GETP
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from m18_ficon_ap20_emit import emit_ficon_ap20,GETADR_MARKER,ENTRY_INDEX
from build_m18_r61_ficon import build
from audit_ap20 import inspect,parse

SW,SH=65,43
rng=Random(0x16002026)
ICONS=(
    bytes([0]*256),bytes([255]*256),
    bytes((3*x+5*y)&255 for y in range(16) for x in range(16)),
    bytes((rng.randrange(256) if (x+y)%4 else 0)
          for y in range(16) for x in range(16)),
)
PAYLOAD=build_bank(ICONS)
assert parse_bank(PAYLOAD).count==4

def oracle(before,*,x,y,icon,mode):
    out=bytearray(before)
    source=ICONS[icon-1]
    for iy in range(16):
        for ix in range(16):
            dx,dy=x+ix,y+iy
            if 0<=dx<SW and 0<=dy<SH:
                colour=source[iy*16+ix]
                if mode==0 or colour:
                    out[dy*SW+dx]=colour
    return bytes(out)

def damage_selected_mask(m):
    addr=BANK+12+3*288
    old=m.uc.mem_read(addr,1)[0]
    m.uc.mem_write(addr,bytes((old^0x80,)))

def case(binary,*,layout="interpreted",mode=1,bank=10,icon=4,
         x=1,y=2,front=0,pending=0,safe_ready=True,
         mutation=None,expect_ok=True):
    m=CaptureMachine(binary=binary,width=SW,height=SH,depth=8,
                     front=front,pending=pending,safe_ready=safe_ready)
    m.install_bank(PAYLOAD)
    m.uc.mem_write(BANK-8,b"FICON8  ")
    m.uc.mem_write(BANK-12,b"\0\1")
    if mutation:mutation(m)
    _,parts,_=unpack_ap20(binary)
    assert len(parts)==ENTRY_INDEX+2==62
    if layout=="interpreted":
        entry=NEW_CODE+sum(len(part) for part in parts[:ENTRY_INDEX])
    elif layout=="compiled":
        mono=0x1B8000
        entry=0x1B7000
        m.uc.mem_write(mono,relocate(parts[-1],mono,{61:mono},m.uc))
        m.uc.mem_write(entry,relocate(parts[ENTRY_INDEX],entry,{61:mono},m.uc))
    else:raise ValueError(layout)
    before=m.snapshot()
    background=sample_pixels(before,SW,SH,8,m.stride)
    for idx,reg in enumerate(DR):m.uc.reg_write(reg,0x1200+idx)
    for idx,reg in enumerate(AR[:7]):m.uc.reg_write(reg,0x40000+idx*256)
    m.uc.reg_write(AR[5],AMOS)
    m.uc.reg_write(AR[3],ARGS)
    for idx,value in enumerate((y,x,icon,bank)):
        m.put(ARGS+idx*4,value&0xffffffff)
    m.uc.reg_write(DR[3],mode&0xffffffff)
    saved={reg:m.uc.reg_read(reg) for reg in DR+AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR,0x2000)
    m.uc.reg_write(AR[7],STACK)
    m.put(STACK,STOP)
    try:
        m.uc.emu_start(entry,STOP,count=2_000_000)
    except Exception as exc:
        raise AssertionError(("FIcon native exception",str(exc),layout,icon,
                              x,y,mode,bank,front,pending,
                              hex(m.uc.reg_read(UC_M68K_REG_PC)),
                              list(m.trace),m.main_calls,m.os_calls)) from exc
    assert m.uc.reg_read(UC_M68K_REG_PC)==STOP
    assert m.a(7)==STACK+4 and m.a(3)==ARGS+16,"AP20 SP/A3"
    assert m.d(2)==0 and m.d(3)==int(expect_ok),(
        "return result",m.d(2),m.d(3),layout,icon,x,y,mode,bank)
    for reg,value in saved.items():
        if reg not in (DR[2],DR[3],AR[3]):
            assert m.uc.reg_read(reg)==value,("clobbered ABI register",reg)
    assert [bytes(m.uc.mem_read(a,m.plane_size)) for a in m.frontplanes]==m.front_before
    assert m.alloc_count==m.free_count==m.reserve_count==m.erase_count==0
    prevalid=(5<=bank<=65535 and 1<=icon<=4096 and 0<=mode<=1
              and -32768<=x<=32767 and -32768<=y<=32767)
    assert m.main_calls==(["Bnk.GetAdr"] if prevalid else []),(
        "wrong bank call ordering",m.main_calls,bank,icon,x,y,mode)
    if expect_ok:
        got=sample_pixels(m.snapshot(),SW,SH,8,m.stride)
        expected=oracle(background,x=x,y=y,icon=icon,mode=mode)
        assert got==expected,("wrong pixels",layout,icon,x,y,mode,
                              next((i for i,(a,b) in enumerate(zip(got,expected))
                                    if a!=b),None))
        visible=(-16<x<SW and -16<y<SH)
        check=int(bool(pending&1) and visible)
        assert m.getmsg_calls==check,("wrong Safe polling",m.getmsg_calls,check)
        assert m.get(DB+20)==(pending & (~1 if check else 0xffffffff))
    else:
        assert before==m.snapshot(),"rejected call modified back buffer"
        if not(pending&1 and not safe_ready):
            assert m.getmsg_calls==0,"preflight failure consumed Safe"
    return 1

def main():
    binary,meta=build()
    assert build()[0]==binary,"nondeterministic build"
    tokens,parts=unwrap_native_parts_v2(binary)
    assert len(parts)==61 and parts[59].endswith(GETP)
    native,labels=emit_ficon_ap20()
    assert parts[60]==native and native.count(GETADR_MARKER)==1
    replace=native.replace(GETADR_MARKER,bytes.fromhex("4eb900030000"))
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
             .disasm(replace,0))
    assert sum(i.size for i in ins)==len(native),"not valid 68000 code"
    assert not any(i.mnemonic.lower() in ("illegal","dc.w","trap","stop")
                   for i in ins)
    assert {"core","safe","check_row","reject"} <= set(labels)
    assert meta["new_entry_index"]==60 and meta["ap20_entries"]==62
    assert len([x for x in inspect(parse(binary))["tokens"]
                if x["name"]=="aga f icon"])==1
    cases=0
    for layout in ("interpreted","compiled"):
        for icon in range(1,5):
            for mode in (0,1):
                for x,y in ((0,0),(1,1),(7,3),(15,0),(16,16),
                            (49,2),(-1,-1),(-15,3),(64,42),
                            (65,2),(-16,-16),(17,42)):
                    cases+=case(binary,layout=layout,icon=icon,mode=mode,
                                x=x,y=y,front=icon&1)
        for args in (
            dict(bank=4),dict(bank=11),dict(bank=65536),
            dict(icon=0),dict(icon=-1),dict(icon=5),
            dict(mode=-1),dict(mode=2),dict(x=32768),dict(y=-32769),
            dict(mutation=lambda m:m.uc.mem_write(BANK-8,b"AGAPIC  ")),
            dict(mutation=lambda m:m.uc.mem_write(BANK+6,b"\0\0")),
            dict(mutation=lambda m:m.uc.mem_write(BANK+10,b"\0\4")),
            dict(mutation=damage_selected_mask),
            dict(mutation=lambda m:m.put(BANK-20,len(PAYLOAD)+17)),
        ):
            cases+=case(binary,layout=layout,expect_ok=False,**args)
        cases+=case(binary,layout=layout,pending=1,safe_ready=False,
                    expect_ok=False)
        cases+=case(binary,layout=layout,pending=3,safe_ready=True)
    print("R61 Fast Icon AP20 GATE A PASS:",cases,
          "real M68000 cases, BOTH interpreted/Compiler V2 layouts.")
    print("Verified: canonical bank, 8-plane back only, Safe, pixel oracle,"
          " invalid calls refuse before mutation; NO WinUAE Gate B/C.")
if __name__=="__main__":
    main()
