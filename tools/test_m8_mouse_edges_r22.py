#!/usr/bin/env python3
"""R22 Gate A: actual 68000 mouse-edge code, sticky masks and focus safety.

This is a mocked input.device test, NOT Intuition/WinUAE. Rapid clicks
fully between samples remain unobservable and outside the R22 contract.
"""
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from build_m8_mouse_edges_r22 import (
    build, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256,
    ENTRY_PRESSED, ENTRY_RELEASED, ENTRY_SCREEN_OPEN, STATE_ANCHOR,
    patch_open_reset, emit_edge, GETP
)
from test_m8_mouse_buttons_r20 import ButtonMachine
from test_m8_mouse_position_r19 import CODE, AMOS, SCREEN, WINDOW
from test_m8_rmbtrap_r21 import RMBTrapOpenMachine
from test_ntsc_pal_r10 import NTSC, PAL, FALLOUT


class EdgeMachine(ButtonMachine):
    def __init__(self, lib, qualifier=0, open_error=False, null_base=False):
        super().__init__(lib, qualifier=qualifier, open_error=open_error,
                         null_base=null_base)
        # AP20 C_Lib actually sets AMOS+456 to a data area within entry 0.
        # Exercise that in-HUNK relationship rather than a synthetic pointer.
        anchor = CODE + STATE_ANCHOR
        self.put(AMOS+456, anchor)
        self.put(anchor+0, SCREEN)
        self.put(anchor+12, 320)
        self.put(anchor+16, 256)
        self.put(anchor+36, WINDOW)
        self.put(WINDOW+24, 0x00002000)  # WFLG_WINDOWACTIVE
    def pressed(self):
        return self.sample(ENTRY_PRESSED)
    def released(self):
        return self.sample(ENTRY_RELEASED)
    def sampled(self, qualifier):
        self.qualifier = qualifier
        return self.pressed(), self.released()


def run():
    lib, info = build()
    assert lib == build()[0], 'Nondeterministic builder'
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    before_tok, before, _ = split(BASE.read_bytes())
    after_tok, after, _ = split(lib)
    assert len(before) == 31 and len(after) == 33
    assert after[:6] == before[:6]
    assert [i for i in range(31) if before[i] != after[i]] == [6, 30]
    assert after[30] == before[30] + GETP
    assert after[6] == patch_open_reset(before[6], info['state_delta'])
    for name, entry in [('aga mouse pressed', 31), ('aga mouse released', 32)]:
        matches = [x for x in inspect(parse(lib))['tokens'] if x['name'] == name]
        assert len(matches) == 1
        assert (matches[0]['instruction'], matches[0]['function'],
                matches[0]['signature']) == (1, entry, '0')
    assert after_tok.startswith(before_tok[:-6])
    assert not inspect(parse(lib))['issues']
    cs = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000)
    for mode, index in [('pressed', 31), ('released', 32)]:
        raw, labels = emit_edge(mode, info['state_delta'],
                                with_state=mode == 'pressed')
        assert after[index] == raw + (GETP if mode == 'pressed' else b'')
        instructions = list(cs.disasm(raw[:labels['device_name']], 0))
        assert sum(x.size for x in instructions) == labels['device_name'], mode
        assert all(x.mnemonic not in ('illegal', 'dc.w') for x in instructions)
        assert raw.count(bytes.fromhex('4eaefe86')) == 0  # Exec ReplyMsg
        assert raw.count(bytes.fromhex('4eaefe8c')) == 0  # Exec GetMsg
        assert raw.count(bytes.fromhex('4eaefe80')) == 0  # Exec WaitPort
    count = 0

    m = EdgeMachine(lib)
    assert m.sampled(0) == (0, 0); count += 1
    assert m.sampled(0x4000) == (1, 0); count += 1
    for _ in range(3):
        assert m.sampled(0x4000) == (0, 0); count += 1
    assert m.pressed() == 0; count += 1
    m.qualifier = 0
    assert m.pressed() == 0
    assert m.released() == 1; count += 1
    assert m.released() == 0; count += 1

    m.qualifier = 0x3000
    assert m.pressed() == 6 and m.released() == 0; count += 1
    m.qualifier = 0x7000
    assert m.pressed() == 1 and m.released() == 0; count += 1
    m.qualifier = 0x2000
    assert m.released() == 5 and m.pressed() == 0; count += 1
    m.qualifier = 0
    assert m.released() == 2 and m.pressed() == 0; count += 1

    m = EdgeMachine(lib)
    assert m.pressed() == 0
    m.qualifier = 0x4000
    assert m.pressed() == 1
    m.qualifier = 0
    assert m.pressed() == 0
    assert m.pressed() == 0 and m.released() == 1; count += 1

    m = EdgeMachine(lib)
    assert m.sampled(0) == (0, 0)
    m.qualifier = 0x4000
    assert m.pressed() == 1
    m.put(WINDOW+24, 0)
    assert m.pressed() == -1 and m.released() == -1; count += 1
    m.put(WINDOW+24, 0x2000)
    assert m.sampled(0x4000) == (0, 0)
    assert m.sampled(0) == (0, 1); count += 1

    for err in ('open_error', 'null_device'):
        m = EdgeMachine(lib, open_error=err == 'open_error',
                        null_base=err == 'null_device')
        assert m.pressed() == -1
        assert m.calls == (['open'] if err == 'open_error'
                           else ['open', 'close'])
        count += 1
    for field in ('state', 'screen', 'window', 'foreign_screen'):
        m = EdgeMachine(lib)
        if field == 'state':
            m.put(AMOS+456, 0)
        elif field == 'screen':
            m.put(CODE+STATE_ANCHOR+0, 0)
        elif field == 'window':
            m.put(CODE+STATE_ANCHOR+36, 0)
        else:
            m.put(WINDOW+46, 0x57000)
        assert m.pressed() == -1 and m.released() == -1
        assert m.calls == []
        count += 1

    # New Screen opens must discard pending edges even when Intuition
    # reuses a Window pointer from an earlier instance.
    for mode, accepted, window_ok, expected in (
        (NTSC, {NTSC}, True, 1), (NTSC, {PAL}, True, 1),
        (FALLOUT, {FALLOUT}, True, 1), (NTSC, {NTSC}, False, 0),
    ):
        m = RMBTrapOpenMachine(lib, accepted=accepted, window_ok=window_ok)
        target = 0x50000 + info['state_delta']
        for i in range(4):
            m.put(target+i*4, 0xABBA0000+i)
        result = m.execute(ENTRY_SCREEN_OPEN,
                           open_args=(320, 256, 16, mode))
        assert result == expected
        # R22 reset trampoline executes after the screen helper is entered,
        # including when OpenWindow subsequently fails. This is intentional:
        # a failed window acquisition must never retain pending old clicks.
        assert all(m.get(target+4*i) == 0 for i in range(4)), (
            mode, expected, [m.get(target+4*i) for i in range(4)])
        count += 1

    print('M8 R22 CPU PASS', count, 'cases; sticky edges, focus loss/reacquire,'
          ' screen reopen, device failures, keyboard queue untouched,'
          ' HUNK/AP20 reproducible')
    print('R22', info['bytes'], 'bytes SHA256', info['sha256'])
    print('Rapid taps between polls, WinUAE/AMOS Compiler/Amiga real: NOT TESTED')


if __name__ == '__main__':
    run()
