#!/usr/bin/env python3
"""R50 68k control: one mocked harmless FnOne Rjsr, no bank writes."""
from struct import pack
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_D3,UC_M68K_REG_D2
from test_m16_capture_r47_unicorn import CaptureMachine,NEW_CODE,MAIN_BASE
from build_m16_r50_fnone_probe import native_probe,build,IDX_FNONE
class FnoneMachine(CaptureMachine):
    def __init__(self):
        super().__init__()
        self.uc.mem_write(MAIN_BASE+IDX_FNONE*16,b"\x4e\x75")
    def main_call(self,uc,address,size,user):
        if address==MAIN_BASE+IDX_FNONE*16:
            self.main_calls.append(IDX_FNONE)
            self.uc.reg_write(UC_M68K_REG_D3,1)
            self.uc.reg_write(UC_M68K_REG_D2,0)
            self.pop_return()
            return
        super().main_call(uc,address,size,user)
def run():
    raw=native_probe()
    marker=b"\xfe\x11\xf7\x00"+pack(">H",IDX_FNONE)
    assert raw.count(marker)==1
    code=raw.replace(marker,b"\x4e\xb9"+pack(">I",MAIN_BASE+IDX_FNONE*16))
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    assert sum(i.size for i in dis.disasm(code,0))==len(code)
    tests=[({},1,[IDX_FNONE]),({"bank":12},0,[]),({"x":0},0,[]),
           ({"index":0},0,[]),({"w":2},0,[]),({"h":17},0,[])]
    for cfg,want,calls in tests:
        m=FnoneMachine()
        m.uc.mem_write(NEW_CODE,code)
        initial=dict(m.banks)
        result,_=m.run_capture(bank=cfg.get("bank",11),x=cfg.get("x",16),
          y=cfg.get("y",16),w=cfg.get("w",16),h=cfg.get("h",16),
          index=cfg.get("index",-1))
        assert result==want and m.main_calls==calls,(cfg,result,m.main_calls)
        assert m.banks==initial and not m.alloc_count and not m.reserve_count
        assert not m.erase_count and not m.change_count
    a,info=build()
    assert (a,info)==build()
    print("R50 FnOne Rjsr 68000 Gate A PASS: six control cases")
    print("WinUAE interpreted Gate B not tested")
if __name__=="__main__":
    run()
