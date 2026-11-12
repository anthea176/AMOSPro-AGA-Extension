#!/usr/bin/env python3
"""R54 Gate A: 68000 syntax, protected old API, two wrappers, bank ABI.

WinUAE Gates B/C remain untested; no promotion of R54.
"""
from __future__ import annotations
from struct import unpack_from
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from build_m16_bank_api_r54 import build,R53,API_IMAGE,API_FONT
from m16_bank_api_r54_emit import emit_bank_image_draw,emit_bank_font_select,MARKER
from compiler_relocation import unpack_ap20,unwrap_native_parts
from audit_ap20 import parse,inspect
from amos_main_abi import main_index
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_SR,UC_M68K_REG_PC
from test_m16_capture import CaptureMachine,NEW_CODE
from test_m16_image_draw_r45 import ARGS,BANK
from test_m5_generic import DR,AR,AMOS,STACK,STOP
from amos_link_test_support import relocate

def _run_native_wrapper(binary,meta,kind,layout="interpreted",bank=10,mode=1,x=23,y=17):
    """Run NEW 68000 wrapper and mock only the already validated legacy core.

    The source-derived Bnk.GetAdr is a real Rjsr relocation through the
    independent AMOS-main symbol table. A hook at the legacy function entry
    checks ABI forwarding, returns D3=1, and verifies A3 caller restoration.
    For compiled layout, the single AP20 stub is separated from the monolith.
    """
    _,parts,_=unpack_ap20(binary)
    assert len(parts)==60
    m=CaptureMachine(binary=binary,layout="interpreted")
    addresses=[]
    cursor=NEW_CODE
    for part in parts:
        addresses.append(cursor)
        cursor+=len(part)
    assert len(addresses)==60
    index=57 if kind=="image" else 58
    if layout=="interpreted":
        entry=addresses[index]
        mono=addresses[59]
    else:
        mono=0x1B8000
        entry=0x1B7000
        m.uc.mem_write(mono,relocate(parts[59],mono,{59:mono},m.uc))
        m.uc.mem_write(entry,relocate(parts[index],entry,{59:mono},m.uc))
    legacy_offset=meta["legacy_draw_offset"] if kind=="image" else meta["legacy_font_offset"]
    native_target=mono+32+legacy_offset
    expected_len=len(m.payload)
    history=[]
    def legacy_hook(uc,address,size,user):
        incoming_a3=m.a(3)
        incoming_d3=m.d(3)
        assert kind in ("image","font")
        if kind=="image":
            args=[m.get(incoming_a3+4*i) for i in range(4)]
            assert args==[y,x,expected_len,BANK],("bad delegated image args",args)
            assert incoming_d3==mode,("bad image mode",incoming_d3,mode)
            uc.reg_write(AR[3],incoming_a3+16)
        else:
            assert m.get(incoming_a3)==BANK,("bad delegated font Start",m.get(incoming_a3))
            assert incoming_d3==expected_len,("bad delegated font Length",incoming_d3,expected_len)
            uc.reg_write(AR[3],incoming_a3+4)
        history.append((kind,layout,bank,incoming_d3))
        uc.reg_write(DR[3],1)
        uc.reg_write(DR[2],0)
        m.pop_return()
    m.uc.hook_add(UC_HOOK_CODE,legacy_hook,begin=native_target,end=native_target)
    for i,reg in enumerate(DR):
        m.uc.reg_write(reg,0x1200+i)
    for i,reg in enumerate(AR[:7]):
        m.uc.reg_write(reg,0x40000+i*256)
    m.uc.reg_write(AR[5],AMOS)
    m.uc.reg_write(AR[3],ARGS)
    if kind=="image":
        for i,v in enumerate((y,x,bank)):
            m.put(ARGS+i*4,v)
        m.uc.reg_write(DR[3],mode)
    else:
        m.uc.reg_write(DR[3],bank)
    saved={reg:m.uc.reg_read(reg) for reg in DR+AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR,0x2000)
    m.uc.reg_write(AR[7],STACK)
    m.put(STACK,STOP)
    try:
        m.uc.emu_start(entry,STOP,count=200000)
    except Exception as exc:
        raise AssertionError(("R54 native wrapper exception",kind,layout,bank,
            hex(m.uc.reg_read(UC_M68K_REG_PC)),list(m.trace),
            m.main_calls)) from exc
    assert m.uc.reg_read(UC_M68K_REG_PC)==STOP
    assert m.a(7)==STACK+4
    assert m.a(3)==ARGS+(12 if kind=="image" else 0),"caller A3 mis-restored"
    assert m.d(2)==0,"AP20 integer result type lost"
    want=1 if bank==10 else 0
    assert m.d(3)==want,("R54 result",kind,layout,bank,m.d(3))
    assert len(history)==want,history
    for reg,val in saved.items():
        if reg not in (DR[2],DR[3],AR[3]):
            assert m.uc.reg_read(reg)==val,("AMOS ABI register modified",kind,reg,val)
    assert m.main_calls==["Bnk.GetAdr"] if bank>=5 else m.main_calls==[]
    assert m.reserve_count==m.erase_count==m.change_count==0
    assert m.alloc_count==m.free_count==0
    return 1

def native_abi_cases(binary,meta):
    n=0
    for layout in ("interpreted","compiled"):
        for kind in ("image","font"):
            for bank in (10,11,4):
                n+=_run_native_wrapper(binary,meta,kind,layout,bank)
    print("R54 Unicorn native AP20 ABI PASS:",n,
          "cases with source-derived AMOS GetAdr, delegated legacy args, separate Compiler relocation")

def check():
    raw,meta=build()
    assert (raw,meta)==build()
    old=R53.read_bytes()
    oldtok,original=unwrap_native_parts(old)
    tok,parts=unwrap_native_parts(raw)
    assert len(parts)==59 and parts[:56]==original[:56]
    assert parts[56]==original[56]+b"GetP"
    start=meta["image_labels"]["native_start"]
    legacy=meta["image_labels"]["native_target"]
    d,labels=emit_bank_image_draw(start,legacy)
    assert parts[57]==d+b"GetP"
    start=meta["font_labels"]["native_start"]
    legacy=meta["font_labels"]["native_target"]
    f,flabels=emit_bank_font_select(start,legacy)
    assert parts[58]==f
    assert d.count(MARKER)==f.count(MARKER)==1
    assert main_index("Bnk.GetAdr")==797
    for name,code,lab in (("image",d,labels),("font",f,flabels)):
        patched=code.replace(MARKER,bytes.fromhex("4eb9000e0000"))
        assert len(patched)==len(code)
        dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
        instructions=list(dis.disasm(patched,0))
        assert sum(x.size for x in instructions)==len(code),(name,instructions[-5:])
        starts={x.address for x in instructions}
        assert all(x in starts for x in lab.values() if isinstance(x,int) and 0<=x<len(code))
        assert "bsr.w" in " ".join(x.mnemonic for x in instructions) or any(x.mnemonic=="bsr" for x in instructions)
        offset=lab["delegate"]
        assert unpack_from(">h",code,offset+2)[0]==lab["delegate_displacement"]
        assert lab["native_start"]+offset+4+lab["delegate_displacement"]==lab["native_target"]
    old_tokens=[t for t in inspect(parse(old))["tokens"] if t["name"].startswith("aga ")]
    new_tokens=[t for t in inspect(parse(raw))["tokens"] if t["name"].startswith("aga ")]
    assert new_tokens[:len(old_tokens)]==old_tokens
    assert [x["name"] for x in new_tokens[-2:]]==[API_IMAGE[0],API_FONT[0]]
    wrapped=unpack_ap20(raw)[1]
    assert len(wrapped)==60 and len(wrapped[-1])<32768
    native_abi_cases(raw,meta)
    print("R54 Gate A AP20 68000 relocation PASS: 53 commands, two additive wrappers",
      len(d),len(f),"bytes")
    print("AMOS WinUAE Gate B/C: NOT TESTED; R53 last tested source remains immutable")
if __name__=="__main__": check()
