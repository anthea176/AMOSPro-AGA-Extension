#!/usr/bin/env python3
"""R77 C2P Close native Gate A on 68000/020 machine68k + real AP20 bytes.

Checks ownership, close twice, reopen, Convert after Close, automatic cleanup
after explicit Close, ABI, registers, screen/palette/swap survival. NOT WinUAE.
"""
from __future__ import annotations
from machine68k import CPUType,Register
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_000
from build_c2p_r77_close import build
from c2p_r77_close_emit import emit_close
from test_c2p_r75_convert_gate_a import ConvertHarness
from test_c2p_r74_open_gate_a import (
    Harness as OpenHarness, SAVED, CODE, STOP, STACK, STATE, DB,
    CONTEXT, C2P_LIB, AMOS, ARGS,
)
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from build_c2p_r76_rpg_fix import SITES,state_offset
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74

CLOSE_CODE=CODE+0x6000

def install(h):
    code,labels=emit_close()
    h.mem.w_block(CLOSE_CODE,code)
    return code

def run_close(h):
    h.calls=[]
    h.cpu.w_sp(STACK)
    h.mem.w32(STACK,STOP)
    for reg,value in SAVED.items():h.cpu.w_reg(reg,value)
    h.cpu.w_reg(Register.A3,ARGS)
    h.cpu.w_reg(Register.D3,0xaabbccdd)
    h.cpu.w_pc(CLOSE_CODE)
    answer=h.m.execute(2000000)
    assert answer.result is h.end,("native Close did not return",answer,h.cpu.r_pc(),h.calls)
    assert h.cpu.r_sp()==STACK+4,("stack drift",h.cpu.r_sp())
    assert h.cpu.r_reg(Register.D2)==0,"AP20 D2 must be reset"
    assert h.cpu.r_reg(Register.A3)==ARGS,"A3 ABI corruption"
    for reg,value in SAVED.items():
        assert h.cpu.r_reg(reg)==value,("register clobbered",reg,h.cpu.r_reg(reg),value)
    assert h.mem.r_block(DB+48,9)==b"DB_CANARY"
    return h.cpu.r_reg(Register.D3)

def test_normal(depth):
    h=ConvertHarness(depth=depth)
    try:
        install(h)
        assert run_close(h)==0
        assert not h.calls,"Close without Open must not call OS"
        assert h.run()==1,"Open failed"
        assert h.run_convert()==1,"pre-Close Convert failed"
        # Respect the visible scene and front/back ownership.
        prior_state=h.mem.r_block(STATE,40)
        prior_db=h.mem.r_block(DB,24)
        assert run_close(h)==1
        assert h.calls==["waitblit","destroy","closelib"],h.calls
        assert h.mem.r_block(DB+24,20)==bytes(20),"C2P ownership not cleared"
        assert h.mem.r_block(STATE,40)==prior_state,"Close modified AGA screen"
        assert h.mem.r_block(DB,24)==prior_db,"Close modified DB front/Swap/Safe"
        assert run_close(h)==0
        assert not h.calls,"Second Close did not behave idempotently"
        assert h.run_convert()==0,"Convert after Close should reject"
        reopened=h.run()
        assert reopened==1,("Reopen on SAME AGA screen failed",depth,
            "status",reopened,"OS",h.calls[-35:],
            "DB_C2P",h.mem.r_block(DB+24,20).hex(),
            "STATE",h.mem.r_block(STATE,40).hex(),
            "DB_HEADER",h.mem.r_block(DB,24).hex(),
            "CPU_FLAGS",h.mem.r16(0x8000+0x128),
            "BANK",h.bank,
            "REG_D3",h.cpu.r_reg(Register.D3),
            "REG_A5",h.cpu.r_reg(Register.A5),
            "REG_A3",h.cpu.r_reg(Register.A3))
        assert h.run_convert()==1,"Convert after reopen failed"
        assert run_close(h)==1
        assert h.calls==["waitblit","destroy","closelib"]
        # Auto cleanup after explicit Close must not release the SDK twice.
        h.calls=[]
        h.run(close=True)
        assert "destroy" not in h.calls and "closelib" not in h.calls
        return 1
    finally:
        h.cleanup()

def test_missing(kind):
    h=OpenHarness()
    try:
        install(h)
        if kind=="null_state":h.mem.w32(AMOS+0x1c8,0)
        if kind=="null_db":h.mem.w32(STATE+32,0)
        if kind=="missing_cookie":h.mem.w32(DB+40,0)
        if kind=="no_lib":h.mem.w32(DB+40,0x43325031)
        if kind=="no_ctx":
            h.mem.w32(DB+40,0x43325031)
            h.mem.w32(DB+24,C2P_LIB)
        if kind=="bad_cookie":
            h.mem.w32(DB+40,0x43325030)
            h.mem.w32(DB+24,C2P_LIB)
            h.mem.w32(DB+28,CONTEXT)
        before=h.mem.r_block(DB,48)
        assert run_close(h)==0,(kind,h.calls)
        assert not h.calls,("unexpected SDK/OS action",kind,h.calls)
        assert h.mem.r_block(DB,48)==before,("invalid Close modified DB",kind)
        return 1
    finally:
        h.cleanup()

def test_68000_release():
    h=OpenHarness(cpu=CPUType.M68000,flags=0)
    try:
        install(h)
        h.mem.w32(DB+24,C2P_LIB)
        h.mem.w32(DB+28,CONTEXT)
        h.mem.w32(DB+32,12)
        h.mem.w32(DB+36,8)
        h.mem.w32(DB+40,0x43325031)
        assert run_close(h)==1
        assert h.calls==["waitblit","destroy","closelib"]
        return 1
    finally:
        h.cleanup()

def main():
    data,meta=build()
    _,parts=unwrap_native_parts_v2(data)
    assert len(parts)==73 and meta["commands"]==67 and meta["ap20_entries"]==74
    code,_=emit_close()
    from compiler_relocation import GETP
    assert parts[72]==code and parts[71].endswith(GETP)
    assert state_offset(parts)==12070
    for e,p,op in SITES:
        assert parts[e][p:p+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
    assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    decoded=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000).disasm(code,0))
    assert sum(ins.size for ins in decoded)==len(code),"bad M68000 instruction in Close"
    cases=0
    for depth in range(4,9):
        cases+=test_normal(depth)
    for kind in ("null_state","null_db","missing_cookie","no_lib","no_ctx","bad_cookie"):
        cases+=test_missing(kind)
    cases+=test_68000_release()
    assert cases==12
    print("R77 C2P CLOSE NATIVE GATE A PASS",cases,
          "CPU000/020 ABI + lifecycle cases; WinUAE/Compiler NOT TESTED",meta["sha256"])

if __name__=="__main__":
    main()
