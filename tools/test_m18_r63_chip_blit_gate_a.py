#!/usr/bin/env python3
"""R63 Gate A: real 68000 AP20 bank flags 0/1/3 in Chip vs invalid types.

R62 remains pinned. The new option must create a DIFFERENT source body and
accept genuine reloaded AMOS DATA banks with native header flags 0, but
must still reject actual Fast RAM before any DMA. No WinUAE compilation.
"""
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from m18_ficon_chip_ap20_emit import emit_ficon_chip_ap20,GETADR_MARKER
from build_m18_r62_chip_blit import build as build_r62
from build_m18_r63_chip_blit import build as build_r63
from test_m18_r62_chip_blit_gate_a import case,BANK

def flags(value):
    return lambda machine:machine.uc.mem_write(BANK-12,bytes((value>>8,value&255)))

def main():
    old,oldmeta=build_r62()
    new,info=build_r63()
    assert build_r62()[0]==old and build_r63()[0]==new
    assert new!=old,"R63 should differ from R62"
    _,oldparts=unwrap_native_parts_v2(old)
    _,newparts=unwrap_native_parts_v2(new)
    assert len(oldparts)==len(newparts)==62
    assert oldparts[:61]==newparts[:61] and oldparts[61]!=newparts[61]
    assert oldparts[61]==emit_ficon_chip_ap20()[0]
    native,labels=emit_ficon_chip_ap20(allow_reloaded_flags_zero=True)
    assert newparts[61]==native and native.count(GETADR_MARKER)==1
    clean=native.replace(GETADR_MARKER,bytes.fromhex("4eb900030000"))
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(clean,0))
    assert sum(x.size for x in ins)==len(native),"R63 68000 instruction decode"
    assert labels["loaded_data_flags_ok"]<labels["core"]
    count=0
    for layout in ("interpreted","compiled"):
        # The actual AMOS bank header can be normalized to flags=0
        # after Load, regardless of the on-disk Chip ABK header flags.
        # TypeOfMem proving Chip is mandatory in all accepted cases.
        for bank_flags in (0,1,3):
            for icon in (1,2,3,4):
                for mode in (0,1):
                    for x,y in ((0,0),(7,3),(-7,21),(64,42),(65,1)):
                        count+=case(new,layout=layout,index=icon,
                                    x=x,y=y,mode=mode,
                                    mutation=flags(bank_flags))
        # Non-DATA native bank classes must not be accepted.
        for bank_flags in (2,4,5,9):
            count+=case(new,layout=layout,expect_ok=False,
                        mutation=flags(bank_flags))
        # A Chip flag 3 or normalized 0 never overrides physical Fast:
        for bank_flags in (0,1,3):
            count+=case(new,layout=layout,expect_ok=False,chip=False,
                        mutation=flags(bank_flags))
        # Preserve Safe rejection, invalid bank, invalid icon.
        count+=case(new,layout=layout,pending=1,safe_ready=False,
                    expect_ok=False,mutation=flags(0))
        count+=case(new,layout=layout,bank=10,expect_ok=False,
                    mutation=flags(0))
        count+=case(new,layout=layout,index=0,expect_ok=False,
                    mutation=flags(0))
    print("M18/R63 FICHIP8 RELOADED BANK FLAGS GATE A PASS:",count,
          "real 68000 cases, flags 0/1/3, real Chip guard, Compiler V2 emulator")
    print("In memory only, R62 and R60 LAST_GOOD untouched. WinUAE B/C NOT DONE.")
if __name__=="__main__":
    main()
