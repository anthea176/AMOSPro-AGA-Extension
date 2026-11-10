#!/usr/bin/env python3
"""R20 Gate A: native 68000 ABI/stack, input.device LVOs and button bitmasks.

OS calls are emulated at their real LVO addresses; this is NOT WinUAE or
physical Amiga validation. Edge transitions are calculated in AMOS.
"""
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_D0
from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from build_m8_mouse_buttons_r20 import (
    build, emit_buttons, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256,
    ENTRY_BUTTONS, GETP, OPEN_DEVICE, CLOSE_DEVICE, PEEK_QUALIFIER
)
from test_m8_mouse_position_r19 import MouseMachine, STATE, WINDOW

EXECBASE = 0x48000
INPUTBASE = 0x49000


class ButtonMachine(MouseMachine):
    def __init__(self, binary, qualifier=0, open_error=False, null_base=False):
        super().__init__(binary)
        self.qualifier = qualifier
        self.open_error = open_error
        self.null_base = null_base
        self.calls = []
        self.ioreq = None
        self.put(4, EXECBASE)
        for addr in (EXECBASE + OPEN_DEVICE,
                     EXECBASE + CLOSE_DEVICE,
                     INPUTBASE + PEEK_QUALIFIER):
            self.uc.mem_write(addr, b'\x4e\x75')  # RTS for stub
        self.uc.hook_add(UC_HOOK_CODE, self.os_hook)

    def os_hook(self, uc, addr, size, user):
        if addr == EXECBASE + OPEN_DEVICE:
            req = uc.reg_read(UC_M68K_REG_A1)
            assert bytes(uc.mem_read(req, 48)) == bytes(48), 'Uninitialized IOStdReq'
            assert uc.reg_read(UC_M68K_REG_D0) == 0, 'Unit must be 0'
            dev = uc.reg_read(UC_M68K_REG_A0)
            assert bytes(uc.mem_read(dev, 13)) == b'input.device\0'
            self.ioreq = req
            self.calls.append('open')
            if self.open_error:
                uc.reg_write(UC_M68K_REG_D0, 5)
            else:
                self.put(req+20, 0 if self.null_base else INPUTBASE)
                uc.reg_write(UC_M68K_REG_D0, 0)
        elif addr == INPUTBASE + PEEK_QUALIFIER:
            self.calls.append('peek')
            uc.reg_write(UC_M68K_REG_D0, 0xA5A50000 | self.qualifier)
        elif addr == EXECBASE + CLOSE_DEVICE:
            assert uc.reg_read(UC_M68K_REG_A1) == self.ioreq
            assert self.ioreq is not None
            self.calls.append('close')

    def buttons(self):
        return self.sample(ENTRY_BUTTONS)


def run():
    candidate, details = build()
    assert candidate == build()[0], 'R20 builder nondeterministic'
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    oldtok, old, _ = split(BASE.read_bytes())
    newtok, new, _ = split(candidate)
    assert len(old)==30 and len(new)==31 and new[:-2]==old[:-1]
    assert new[-2]==old[-1]+GETP and new[-1]==emit_buttons()[0]
    chk=inspect(parse(candidate))
    assert chk['issues']==[]
    entries=[x for x in chk['tokens'] if x['name']=='aga mouse buttons']
    assert len(entries)==1
    assert (entries[0]['instruction'],entries[0]['function'],entries[0]['signature'])==(1,30,'0')
    diss=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    code=emit_buttons()[0]
    instructions=list(diss.disasm(code[:code.index(b'input.device\0')],0))
    assert instructions and not any(x.mnemonic in ('illegal','dc.w') for x in instructions)
    assert sum(x.size for x in instructions)==code.index(b'input.device\0')
    assert code.count(b'\x4e\xae') == 3
    assert b'\x4e\xae\xfe\x80' not in code  # Exec WaitPort forbidden
    assert b'\x4e\xae\xfe\xc2' not in code  # Exec Wait forbidden

    cases=0
    for flags in (0,0x4000,0x2000,0x1000,0x6000,0x5000,0x3000,0x7000,
                  0x0008,0x0100,0x9000,0xE000,0xFFFF,0xC000):
        m=ButtonMachine(candidate,qualifier=flags)
        expected=((1 if flags&0x4000 else 0) |
                  (2 if flags&0x2000 else 0) |
                  (4 if flags&0x1000 else 0))
        value=m.buttons()
        assert value==expected,(hex(flags),value,expected)
        assert m.calls==['open','peek','close'],m.calls
        cases+=1

    for bad in ('state','screen','window','foreign_screen'):
        m=ButtonMachine(candidate,0x7000)
        if bad=='state':m.put(0x51000+456,0)
        elif bad=='screen':m.put(STATE,0)
        elif bad=='window':m.put(STATE+36,0)
        else:m.put(WINDOW+46,0x57000)
        assert m.buttons()==-1,bad
        assert not m.calls,bad
        cases+=1

    for failure in ('open_error','null_device'):
        m=ButtonMachine(candidate,0x7000,open_error=failure=='open_error',null_base=failure=='null_device')
        assert m.buttons()==-1,failure
        assert m.calls==(['open'] if failure=='open_error' else ['open','close']),m.calls
        cases+=1

    previous=0
    presses=releases=0
    for current in (0,1,1,1,0,2,2,0,3,1,0):
        presses |= (current & (7-previous))
        releases |= (previous & (7-current))
        previous=current
    assert (presses&3)==3 and (releases&3)==3
    cases+=1

    print('R20 CPU PASS:',cases,'cases; 68000 ABI, device open/peek/close, IOStdReq stack, bitmasks, invalid screen and R19 preserved')
    print('Candidate:',details['size'],'bytes, SHA256',details['sha256'])
    print('AMOS WinUAE, Compiler and physical Amiga: NOT TESTED')


if __name__=='__main__':
    run()
