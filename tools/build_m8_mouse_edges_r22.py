#!/usr/bin/env python3
"""R22 0.8.6: native mouse pressed/released edges with focus-safe state.

Reads input.device/PeekQualifier (not IDCMP) to leave the existing RAWKEY
queue untouched. This stage does NOT guarantee taps wholly between polls.
First focused read primes state, and a loss of focus returns -1 while
resetting sticky edges. Entry 6 clears state on every new screen open.

Only AP20 entry 6's success BSR is intercepted; all previously validated
entry bytes except entry 30's new GetP are frozen. Screen close is unchanged.
"""
from pathlib import Path
from struct import pack
from ap20_utils import split, digest
from audit_ap20 import inspect, parse, token
from m8_mouse_edges_emit import emit_edge

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'dist/experimental/AMOSPro_AGA_M8_v0.8.5_RMBTRAP_R21.Lib'
DEST = ROOT / 'dist/AMOSPro_AGA.Lib'
ARCHIVE = ROOT / 'dist/experimental/AMOSPro_AGA_M8_v0.8.6_MOUSE_EDGES_R22.Lib'
LAST_GOOD = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
BASE_SHA256 = 'a72e3046df64e3ff8ebe12a5b4b0db45efebe27e17056919d31d11ca61e9c644'
LAST_GOOD_SHA256="f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225"
R22_SHA256 = '96e38d478bd97e7a65801e16e96ce08c0bbd4aaacb4a8a6644e4bc1289a0c997'
ENTRY_SCREEN_OPEN = 6
ENTRY_PRESSED = 31
ENTRY_RELEASED = 32
STATE_ANCHOR = 0x1A0
ENTRY6_ORIGINAL_BSR = 0x13A
ENTRY6_TARGET = 0x19A
GETP = b'GetP'
SHARED_BYTES = 16


def patch_open_reset(entry, delta):
    """Call existing screen initialization, then reset 16-byte mouse history."""
    assert entry.endswith(GETP)
    old = entry[:-4]
    assert old[ENTRY6_ORIGINAL_BSR:ENTRY6_ORIGINAL_BSR+4] == bytes.fromhex('6100005e')
    assert old[ENTRY6_TARGET:ENTRY6_TARGET+4] == bytes.fromhex('25470018')  # MOVE.L D7,24(A2)
    helper_off = len(old)
    callsite = pack('>H', 0x6100) + pack('>h', helper_off-(ENTRY6_ORIGINAL_BSR+2))
    bsrold = pack('>H', 0x6100) + pack('>h', ENTRY6_TARGET-(helper_off+2))
    assert 0 < delta < 32767
    # BSR original helper; LEA R22 history(A2),A0; 4x CLR.L (A0)+; RTS.
    helper = (bsrold + pack('>HH', 0x41EA, delta) +
              bytes.fromhex('4298')*4 + bytes.fromhex('4e75'))
    out = (old[:ENTRY6_ORIGINAL_BSR] + callsite +
           old[ENTRY6_ORIGINAL_BSR+4:] + helper + GETP)
    assert len(out) == len(entry) + len(helper)
    assert out[0x1EE:0x1F6] == entry[0x1EE:0x1F6], 'R21 RMBTRAP changed'
    return out


def build():
    frozen = BASE.read_bytes()
    assert digest(frozen) == BASE_SHA256, 'R21 archive must remain immutable'
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    oldtok, original, _ = split(frozen)
    assert len(original) == 31
    assert original[0][STATE_ANCHOR:STATE_ANCHOR+40] == bytes(40), 'R21 state anchor moved'
    assert original[-1].endswith(b'input.device\0\0'), 'R21 Buttons entry changed'
    assert oldtok.endswith(bytes(6))

    # Entry 6 gains an 18-byte reset helper, entry 30 gets a GetP delimiter.
    # Pressed contains a 16-byte initialized shared state immediately after
    # the null-terminated input.device string.
    add6 = 18
    sample, labels = emit_edge('pressed', 1, with_state=True)
    state_off = labels['shared_state']
    assert state_off == sample.index(b'input.device\0')+14
    press_start = sum(map(len, original)) + add6 + len(GETP)
    state_delta = press_start + state_off - STATE_ANCHOR
    assert 0 < state_delta < 32767

    press, labels = emit_edge('pressed', state_delta, with_state=True)
    release, _ = emit_edge('released', state_delta, with_state=False)
    assert labels['shared_state'] == state_off
    assert press[state_off:state_off+SHARED_BYTES] == bytes(SHARED_BYTES)

    parts = list(original)
    parts[ENTRY_SCREEN_OPEN] = patch_open_reset(parts[ENTRY_SCREEN_OPEN], state_delta)
    parts[30] += GETP
    parts.extend([press+GETP, release])
    assert len(parts) == 33
    assert [i for i in range(31) if original[i] != parts[i]] == [6, 30]
    tokens = (oldtok[:-6] + token('aga mouse pressed', 1, ENTRY_PRESSED, '0')
              + token('aga mouse released', 1, ENTRY_RELEASED, '0') + bytes(6))
    title = b'AMOSPro AGA M8 Mouse Edges R22 0.8.6\0$VER: AMOSPro_AGA 0.8.6\0'
    if len(title) & 1:
        title += b'\0'
    code = b''.join(parts)
    payload = (pack('>4I', 2*len(parts), len(tokens), len(code), len(title)) +
               b'\0\0AP20' +
               b''.join(pack('>H', len(part)//2) for part in parts) +
               tokens + code + title + b'\0\0')
    payload += bytes(-len(payload) % 4)
    words = pack('>I', len(payload)//4)
    lib = frozen[:20]+words+frozen[24:28]+words+payload+frozen[-4:]
    audit = inspect(parse(lib))
    assert not audit['issues'], audit['issues']
    tok2, parts2, _ = split(lib)
    assert tok2 == tokens and parts2 == parts
    for name, entry in [('aga mouse pressed', 31), ('aga mouse released', 32)]:
        found = [x for x in audit['tokens'] if x['name'] == name]
        assert len(found) == 1
        assert (found[0]['instruction'], found[0]['function'],
                found[0]['signature']) == (1, entry, '0')
    assert digest(lib) == R22_SHA256, 'R22 binary checkpoint changed'
    return lib, dict(version='0.8.6', bytes=len(lib), sha256=digest(lib),
                     state_delta=state_delta, pressed_code_bytes=len(press),
                     released_code_bytes=len(release), runtime='NOT_TESTED')


if __name__ == '__main__':
    assert len({x.resolve() for x in (BASE, DEST, ARCHIVE, LAST_GOOD)}) == 4
    built, report = build()
    assert build()[0] == built
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_bytes(built)
    DEST.write_bytes(built)
    assert DEST.read_bytes() == ARCHIVE.read_bytes() == built
    assert digest(BASE.read_bytes()) == BASE_SHA256
    assert digest(LAST_GOOD.read_bytes()) == LAST_GOOD_SHA256
    print('R22 Mouse Edges CPU candidate (WinUAE NOT TESTED):', report)
