#!/usr/bin/env python3
"""M8 R20 0.8.4: nonblocking mouse button snapshot from input.device.

Aga Mouse Buttons returns 0..7, L=1, R=2, M=4; -1 when no owned
Screen/Window or input.device cannot be opened. Uses PeekQualifier() V36,
which reads qualifiers without consuming Intuition's keyboard event queue.
OpenDevice/CloseDevice are paired around a zeroed stack-local IOStdReq:
no allocation, no persistent global state, no IDCMP changes. This is a
snapshot of global input qualifiers, NOT queued window-owned click events;
edge detection by comparison is performed in AMOS and can miss fast taps.

Build only from R19 WinUAE PASS frozen archive. Its 30 AP20 entries remain
byte-for-byte unchanged, save final GetP delimiter. Never promote LAST_GOOD.
Runtime WinUAE, AMOS Compiler, real hardware: NOT TESTED for R20.
"""
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import inspect, parse, token
from m68k_emit import Code, A, D, M, I

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib'
ARCHIVE = ROOT / 'dist/experimental/AMOSPro_AGA_M8_v0.8.4_MOUSE_BUTTONS_R20.Lib'
DEST = ROOT / 'dist/AMOSPro_AGA.Lib'
LAST_GOOD = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
BASE_SHA256 = '32c99d9d83affda67058fede26731dace6511ebc033b7974330e6f9eef39e295'
LAST_GOOD_SHA256="09b23a6cd1b8f8eb91b836b43a98ede4da2b16e0b6fb2173ac43ab54d684f366"
ENTRY_BUTTONS = 30
GETP = b'GetP'
STATE_PTR = 0x1C8
IO_SIZE = 48
IO_DEVICE = 20
OPEN_DEVICE = -444
CLOSE_DEVICE = -450
PEEK_QUALIFIER = -42


def emit_buttons():
    """Returns native 68000 code and branch map; D3 result, D2=0, A3 unchanged."""
    c = Code()
    c.raw('48e7efee')   # preserve ordinary registers except D3/A3
    c.move(M(5, STATE_PTR), A(2))
    c.move(A(2), D(0)); c.tst(D(0)); c.branch(7, 'bad')
    c.move(M(2, 0), A(1))
    c.move(A(1), D(0)); c.tst(D(0)); c.branch(7, 'bad')
    c.move(M(2, 36), A(4))
    c.move(A(4), D(0)); c.tst(D(0)); c.branch(7, 'bad')
    c.move(M(4, 46), D(0))  # Window.WScreen, reject foreign Screen
    c.move(A(1), D(1)); c.alu('cmp', D(1), 0); c.branch(6, 'bad')

    # Stack-local IOStdReq: no IO command is sent, so no reply port needed.
    c.raw('4fefffd0')  # LEA -48(SP),SP
    c.move(A(7), A(4))
    c.move(A(4), A(0))
    for _ in range(IO_SIZE // 4):
        c.raw('4298')  # CLR.L (A0)+
    c.raw('2c780004')  # MOVEA.L (4).W,A6, ExecBase
    c.lea(0, 'device_name')
    c.move(I(0), D(0)); c.move(A(4), A(1)); c.move(I(0), D(1))
    c.call_os(OPEN_DEVICE)
    c.tst(D(0)); c.branch(6, 'fail_stack')  # zero means OpenDevice success
    c.move(M(4, IO_DEVICE), A(6))
    c.move(A(6), D(0)); c.tst(D(0)); c.branch(7, 'close_fail')
    c.call_os(PEEK_QUALIFIER)
    c.imm('and', 0x7000, D(0), size='w')  # low UWORD only
    c.move(I(0), D(3))
    for qualifier, bit, label in ((0x4000, 1, 'left_done'),
                                  (0x2000, 2, 'right_done'),
                                  (0x1000, 4, 'mid_done')):
        c.move(D(0), D(1))
        c.imm('and', qualifier, D(1), size='w')
        c.branch(7, label)
        c.quick(bit, D(3))
        c.label(label)
    c.branch(0, 'close_success')
    c.label('close_fail')
    c.move(I(-1), D(3))
    c.label('close_success')
    c.raw('2c780004')
    c.move(A(4), A(1))
    c.call_os(CLOSE_DEVICE)
    c.branch(0, 'free_stack')
    c.label('fail_stack')
    c.move(I(-1), D(3))
    c.label('free_stack')
    c.raw('4fef0030')  # LEA 48(SP),SP
    c.branch(0, 'done')
    c.label('bad')
    c.move(I(-1), D(3))
    c.label('done')
    c.raw('4cdf77f7')  # MOVEM restore, except D3 and A3
    c.raw('74004e75')  # MOVEQ #0,D2 ; RTS
    c.label('device_name')
    c.raw('696e7075742e6465766963650000')  # input.device NUL + pad
    return c.out(), c.labels


def build():
    raw = BASE.read_bytes()
    assert digest(raw) == BASE_SHA256, 'Frozen R19 archive changed'
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    old_tokens, original, _ = split(raw)
    assert len(original) == ENTRY_BUTTONS and old_tokens.endswith(bytes(6))
    code, labels = emit_buttons()
    assert len(code) % 2 == 0
    parts = list(original)
    parts[-1] += GETP
    parts.append(code)
    tokens = (old_tokens[:-6] +
              token('aga mouse buttons', 1, ENTRY_BUTTONS, '0') +
              bytes(6))
    title = b'AMOSPro AGA M8 Mouse Buttons R20 0.8.4\0$VER: AMOSPro_AGA 0.8.4\0'
    if len(title) % 2:
        title += b'\0'
    code_all = b''.join(parts)
    payload = (pack('>4I', len(parts)*2, len(tokens), len(code_all), len(title)) +
               b'\0\0AP20' +
               b''.join(pack('>H', len(p)//2) for p in parts) +
               tokens + code_all + title + b'\0\0')
    payload += bytes(-len(payload) % 4)
    size_words = pack('>I', len(payload)//4)
    lib = raw[:20] + size_words + raw[24:28] + size_words + payload + raw[-4:]
    audit = inspect(parse(lib))
    assert not audit['issues'], audit['issues']
    tok2, part2, _ = split(lib)
    assert tok2 == tokens and part2 == parts
    assert part2[:-2] == original[:-1]  # all other R19 segments unchanged
    assert part2[-2] == original[-1] + GETP
    assert part2[-1] == code
    found = [x for x in audit['tokens'] if x['name'] == 'aga mouse buttons']
    assert len(found) == 1
    assert (found[0]['instruction'], found[0]['function'],
            found[0]['signature']) == (1, ENTRY_BUTTONS, '0')
    return lib, dict(version='0.8.4', size=len(lib), sha256=digest(lib),
                     buttons_bytes=len(code), labels=labels, runtime='NOT_TESTED')


if __name__ == '__main__':
    assert len({p.resolve() for p in (BASE, ARCHIVE, DEST, LAST_GOOD)}) == 4
    result, report = build()
    assert result == build()[0], 'Nondeterministic build'
    # Historical frozen R20: do not overwrite active R21 candidate or archive.
    assert ARCHIVE.read_bytes() == result
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print('M8 R20 frozen (buttons function PASS WinUAE, menu defect fixed in R21):', report)
