#!/usr/bin/env python3
"""R23 native 68000 preflight — not a substitute for WinUAE.

Exercises IDCMP mouse DOWN+UP queued entirely before a poll, RAWKEY FIFO
ordering and backpressure, exact one ReplyMsg, focus, reopen state contract,
and compatibility of the old Key/Wait Key body including Ctrl+C code path.
Does NOT assume GUI event delivery or prove live Ctrl+C in AMOS.
"""
import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_D0
from audit_ap20 import parse, inspect
from ap20_utils import split, digest
from build_m8_idcmp_r23 import (
    build, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256,
    ENTRY_KEY, ENTRY_WAIT_KEY, ENTRY_PRESSED, ENTRY_RELEASED,
    ENTRY_DISPATCH, ENTRY_SCREEN_OPEN, STATE_ANCHOR, GETP
)
from m8_idcmp_r23_emit import (
    emit_dispatcher, emit_mouse_reader, STATE_BYTES, KEY_CAP,
    IDCMP_RAWKEY, IDCMP_MOUSEBUTTONS, IDCMP_ACTIVEWINDOW,
    IDCMP_INACTIVEWINDOW, KEY_FIFO, FAKE_CODEQUAL
)
from test_m8_mouse_position_r19 import (
    MouseMachine, CODE, AMOS, SCREEN, WINDOW, STACK, STOP, DR, AR
)
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

EXECBASE = 0x48000
PORT = 0x59000
MESSAGE = 0x78000


class IdcmpMachine(MouseMachine):
    def __init__(self, library, state_delta):
        super().__init__(library)
        self.state_delta = state_delta
        self.state = CODE + STATE_ANCHOR + state_delta
        self.queue = []
        self.inflight = set()
        self.replied = []
        self.seq = 0
        anchor = CODE + STATE_ANCHOR
        self.put(AMOS+456, anchor)
        self.put(anchor, SCREEN)
        self.put(anchor+36, WINDOW)
        self.put(WINDOW+46, SCREEN)
        self.put(WINDOW+24, 0x2000)
        self.put(WINDOW+86, PORT)
        self.put(4, EXECBASE)
        for addr in (EXECBASE-372, EXECBASE-378):
            self.uc.mem_write(addr, bytes.fromhex('4e75'))
        self.uc.hook_add(UC_HOOK_CODE, self.os_hook)

    def inject(self, klass, code=0, qualifier=0):
        ptr = MESSAGE + self.seq * 0x60
        self.seq += 1
        self.put(ptr+20, klass)
        self.uc.mem_write(ptr+24, struct.pack('>HH',code,qualifier))
        self.queue.append(ptr)
        return ptr

    def os_hook(self, uc, addr, size, userdata):
        if addr == EXECBASE - 372:
            assert uc.reg_read(UC_M68K_REG_A0) == PORT
            ptr = self.queue.pop(0) if self.queue else 0
            if ptr:
                assert ptr not in self.inflight
                self.inflight.add(ptr)
            uc.reg_write(UC_M68K_REG_D0, ptr)
        elif addr == EXECBASE - 378:
            ptr = uc.reg_read(UC_M68K_REG_A1)
            assert ptr in self.inflight, ("unexpected/double ReplyMsg", hex(ptr))
            self.inflight.remove(ptr)
            self.replied.append(ptr)

    def run_entry(self, entry):
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x1200+i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x40000+i*256)
        self.uc.reg_write(AR[5], AMOS)
        self.uc.reg_write(AR[3], 0x5a000)
        before = {reg:self.uc.reg_read(reg) for reg in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE+self.p.starts[entry], STOP, count=75000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.uc.reg_read(AR[7]) == STACK+4
        for reg, initial in before.items():
            if reg in (DR[2], DR[3]):
                continue
            assert self.uc.reg_read(reg) == initial, ("ABI",entry,reg)
        assert self.uc.reg_read(DR[2]) == 0
        v = self.uc.reg_read(DR[3])
        return v-(1<<32) if v & 0x80000000 else v

    def pressed(self): return self.run_entry(ENTRY_PRESSED)
    def released(self): return self.run_entry(ENTRY_RELEASED)
    def key(self): return self.run_entry(ENTRY_KEY)
    def pending(self, off): return self.get(self.state+off)


def run():
    binary, info = build()
    assert binary == build()[0]
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    bt, old, _ = split(BASE.read_bytes())
    nt, new, _ = split(binary)
    assert bt == nt and len(old) == 33 and len(new) == 34
    assert [i for i in range(33) if old[i] != new[i]] == [6,17,18,31,32]
    assert all(old[i] == new[i] for i in (0, 1, 2, 8, 9, 10, 11, 13, 16,
                                          19, 20, 21, 22, 23, 24, 25,
                                          26, 27, 28, 29, 30))
    assert not inspect(parse(binary))["issues"]
    dispatcher, labels = emit_dispatcher(info['state_delta'])
    assert new[ENTRY_DISPATCH] == dispatcher
    assert new[ENTRY_DISPATCH][-STATE_BYTES:] == bytes(STATE_BYTES)
    for mode, entry in [('pressed',31),('released',32)]:
        raw, off = emit_mouse_reader(mode,info['state_delta'])
        assert new[entry].endswith(GETP)
        assert new[entry][:off] == raw[:off]
        assert new[entry][off+2:] == raw[off+2:] + GETP

    dis = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    executable = list(dis.disasm(dispatcher[:labels['runtime_state']], 0))
    assert sum(ins.size for ins in executable) == labels['runtime_state'], 'Illegal 68000 dispatcher opcode'
    assert all(x.mnemonic not in ('dc.w','illegal') for x in executable)
    assert dispatcher.count(bytes.fromhex('4eaefe8c')) == 1  # GetMsg
    assert dispatcher.count(bytes.fromhex('4eaefe86')) == 1  # ReplyMsg
    assert bytes.fromhex('4eaefe80') not in dispatcher  # WaitPort
    assert bytes.fromhex('4eaefec2') not in dispatcher  # Exec Wait
    assert all(new[i][0x4e:0x52] == bytes.fromhex('4e714e71') for i in (17,18))
    # Ctrl+C parser and cleanup code untouched after fake-reply call.
    assert all(new[i][0x52:] == old[i][0x52:] for i in (17,18))

    cases=0
    m=IdcmpMachine(binary, info['state_delta'])
    assert m.pressed() == 0 and m.released() == 0; cases+=1
    a=m.inject(IDCMP_MOUSEBUTTONS,0x68)
    b=m.inject(IDCMP_MOUSEBUTTONS,0xE8)
    assert m.pressed() == 1 and m.released() == 1; cases+=1
    assert m.pressed() == 0 and m.released() == 0; cases+=1
    assert m.replied == [a,b] and not m.inflight; cases+=1

    m=IdcmpMachine(binary,info['state_delta'])
    m.inject(IDCMP_RAWKEY,64,0)
    m.inject(IDCMP_MOUSEBUTTONS,0x69)
    m.inject(IDCMP_MOUSEBUTTONS,0xE9)
    assert m.pressed()==2 and m.released()==2; cases+=1
    assert m.key()==64; cases+=1
    assert m.key()==-1; cases+=1
    assert len(m.replied)==3 and not m.inflight; cases+=1

    m=IdcmpMachine(binary,info['state_delta'])
    for key in (21,22,23):
        m.inject(IDCMP_RAWKEY,key)
    m.inject(IDCMP_MOUSEBUTTONS,0x68)
    m.inject(IDCMP_MOUSEBUTTONS,0xE8)
    assert m.pressed()==1 and m.released()==1; cases+=1
    assert [m.key() for _ in range(3)] == [21,22,23]; cases+=1

    m=IdcmpMachine(binary,info['state_delta'])
    for code in range(1,KEY_CAP+2):
        m.inject(IDCMP_RAWKEY,code)
    m.inject(IDCMP_MOUSEBUTTONS,0x68)
    m.inject(IDCMP_MOUSEBUTTONS,0xE8)
    assert m.pressed() == 0  # stopped before reading the 17th key
    assert m.pending(24)==KEY_CAP
    assert m.key()==1
    # Backpressure: 17th RAWKEY can refill the FIFO before the mouse
    # messages become reachable. Drain all buffered keys first.
    assert [m.key() for _ in range(KEY_CAP)] == list(range(2,KEY_CAP+2))
    assert m.pressed()==1 and m.released()==1
    assert not m.queue and not m.inflight; cases+=1

    m=IdcmpMachine(binary,info['state_delta'])
    m.inject(IDCMP_RAWKEY,0x33,0x08)  # original Ctrl+C (no unsafe Break emulation)
    assert m.pressed()==0
    assert m.pending(24)==1
    assert m.pending(KEY_FIFO) == 0x00330008
    assert not m.inflight; cases+=1

    m=IdcmpMachine(binary,info['state_delta'])
    m.inject(IDCMP_MOUSEBUTTONS,0x68)
    m.inject(IDCMP_MOUSEBUTTONS,0xE8)
    assert m.pressed()==1
    m.put(WINDOW+24,0)
    assert m.released()==-1
    m.put(WINDOW+24,0x2000)
    m.inject(IDCMP_INACTIVEWINDOW)
    m.inject(IDCMP_MOUSEBUTTONS,0x68)
    m.inject(IDCMP_MOUSEBUTTONS,0xE8)
    m.inject(IDCMP_ACTIVEWINDOW)
    m.inject(IDCMP_MOUSEBUTTONS,0x69)
    m.inject(IDCMP_MOUSEBUTTONS,0xE9)
    assert m.pressed()==2 and m.released()==2; cases+=1

    m=IdcmpMachine(binary,info['state_delta'])
    m.put(WINDOW+46,0x5ffff)
    m.inject(IDCMP_MOUSEBUTTONS,0x68)
    assert m.pressed()==-1 and len(m.queue)==1 and m.replied==[]; cases+=1
    m.put(WINDOW+46,SCREEN)
    assert m.pressed()==1; cases+=1
    print("M8 R23 PRE-FLIGHT CPU PASS:",cases,"cases; short press+release"
          " before polling, RAWKEY FIFO and backpressure, Ctrl+C queued,"
          " focus events, GetMsg/ReplyMsg once, 68000 ABI HUNK/AP20")
    print("R23:",info)
    print("WinUAE/AMOS Compiler/real Amiga and live Ctrl+C: NOT TESTED")


if __name__ == '__main__':
    run()
