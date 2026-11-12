#!/usr/bin/env python3
"""Independent ABI regression: omitted include, empty entry, FnOne, GetP."""
from struct import unpack_from,pack
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UcError
from unicorn.m68k_const import *
from amos_main_abi import declarations,main_index,rjsr
from amos_link_test_support import main_table,relocate,EMPTY
from compiler_relocation import unwrap_native_parts
from build_m16_capture import ROOT,build
from m16_capture_emit import emit_capture

def main():
    entries=declarations()
    names={e[0]:e[1] for e in entries}
    expected={"Bnk.GetAdr":797,"Bnk.Eff":800,"Bnk.Reserve":816,
              "Bnk.Change":819,"FnOne":822}
    assert {s:main_index(s) for s in expected}==expected
    assert [names[n] for n in (297,300,316,319,322)]==[
        "InSort","AdSort","InLPrint","PrintF","LPrintX"]
    assert names[500]=="MainLibrary"
    uc=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN)
    uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    uc.mem_map(0,0x100000)
    table,_=main_table(uc)
    def execute(index):
        code=relocate(rjsr(index)+bytes.fromhex("4e75"),0x60000,{},uc)
        uc.mem_write(0x60000,code)
        uc.ctl_remove_cache(0x60000,0x60008)
        uc.reg_write(UC_M68K_REG_SR,0x2000)
        uc.reg_write(UC_M68K_REG_A7,0x80000)
        uc.mem_write(0x80000,pack(">I",0x70000))
        uc.emu_start(0x60000,0x70000,count=30)
        return code
    # Genuine FnOne CPU body; no hook substitutes its return.
    for reg,value in ((UC_M68K_REG_A3,0x81000),(UC_M68K_REG_A5,0x82000),
                      (UC_M68K_REG_A6,0x83000),(UC_M68K_REG_D0,7),
                      (UC_M68K_REG_D1,9)):
        uc.reg_write(reg,value)
    code=execute(822)
    assert unpack_from(">I",code,2)[0]==table[822]
    assert uc.reg_read(UC_M68K_REG_D3)==1 and uc.reg_read(UC_M68K_REG_D2)==0
    assert uc.reg_read(UC_M68K_REG_A7)==0x80004
    for reg,value in ((UC_M68K_REG_A3,0x81000),(UC_M68K_REG_A5,0x82000),
                      (UC_M68K_REG_A6,0x83000),(UC_M68K_REG_D0,7),
                      (UC_M68K_REG_D1,9)):
        assert uc.reg_read(reg)==value
    assert bytes(uc.mem_read(table[822]-4,4))==b"GetP"
    # The old index still produces a valid JSR (R51), but an ILLEGAL target (R52/R50).
    old=relocate(rjsr(322),0x60000,{},uc)
    assert old[:2]==bytes.fromhex("4eb9")
    assert unpack_from(">I",old,2)[0]==EMPTY
    assert bytes(uc.mem_read(EMPTY,6))!=bytes.fromhex("760174004e75")
    try:
        execute(322)
    except UcError:
        assert uc.reg_read(UC_M68K_REG_PC)==EMPTY
    else:
        raise AssertionError("historical wrong FnOne index did not trap")
    # Source correction changes ONLY the five index WORDs, not core or branches.
    oldraw=(ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.2_IMAGE_CAPTURE_R47_CANDIDATE.Lib").read_bytes()
    _,oldparts=unwrap_native_parts(oldraw)
    new,labels=emit_capture()
    patched=bytearray(oldparts[-1])
    positions=[]
    for pos in range(0,len(patched)-5,2):
        if patched[pos:pos+4]==bytes.fromhex("fe11f700"):
            idx=unpack_from(">H",patched,pos+4)[0]
            assert idx in (297,300,316,319)
            patched[pos+4:pos+6]=pack(">H",idx+500)
            positions.append(pos)
    assert len(positions)==5 and bytes(patched)==new
    candidate,meta=build()
    assert candidate==build()[0]
    print("AMOS linkage PASS: include order, 5 symbols, wrong targets, real FnOne CPU,")
    print("GetP-before-label, R51 valid JSR with wrong index, R50 ILLEGAL reproduced.")
    print("Native delta: exactly five relocation index WORDs; no runtime WinUAE claim.")
if __name__=="__main__":
    main()
