#!/usr/bin/env python3
"""M19 native AGA Bob Bank selector/creator, AP20 in-memory experiment.

Adds only Aga Bob Bank to a SHA-pinned R88 snapshot, never installs it.
Native runtime/AMOS Compiler behavior is NOT validated by structural checks.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack_from
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'tools' / 'experiments')]
from audit_ap20 import inspect, parse, token
from compiler_relocation import unpack_ap20, repack_ap20, RBSR, GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements
from active_library import R84_SHA, R88_SHA

PROTECTED = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
EXPERIMENT = ROOT / 'dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib'
# R88 public indices 0..83; append one real Bank command at 84.
BANK = 84
GROUP_BOBS = 87
CAPACITY = 131072
DATA_OFFSET = 40 + 128 * 24
NAME = b'AGABOB  '
COMMAND = ('aga bob bank', BANK, 1, 'I0')
TITLE = b'M19 AGA BOB BANK NATIVE EXPERIMENT - UNINSTALLED\0'
TITLE += bytes(len(TITLE) & 1)

from m68k_emit import Code, D, A, M, POST, I
from amos_main_abi import main_index, rjsr

GETADR = rjsr(main_index('Bnk.GetAdr'))
RESERVE = rjsr(main_index('Bnk.Reserve'))
CHANGE = rjsr(main_index('Bnk.Change'))
EFF = rjsr(main_index('Bnk.Eff'))
LVO_TYPEOFMEM = -534


def emit_bank_select() -> tuple[bytes, dict]:
    """Actual native Bank selector/creator, not a placeholder or installed API.

    D3 receives the AMOS bank number; A3 has no stacked arguments.
    Only publish the chosen WORD after complete validation/initialization.
    No bank pointer survives Erase or Load, no extra numbered bank is used.
    """
    c = Code()
    B, L = c.branch, c.label

    def bankcall(marker):
        c.raw(marker.hex())

    def mem_ok(src, failure):
        c.move(src, A(1))
        c.raw('2c780004')             # MOVEA.L 4.W,A6 (ExecBase)
        c.call_os(LVO_TYPEOFMEM)
        c.tst(D(0))
        B(7, failure)                 # BEQ: unmapped

    # Existing AP20 ABI: D2=integer type, D3=result, A3 unchanged.
    c.raw('48e7efee')                # standard preserved registers
    c.raw('4fefffe0')                # LEA -32(SP),SP
    c.move(A(7), A(2))
    c.move(D(3), M(2, 0))            # bank number
    c.move(I(0), D(3))               # default rejection

    c.move(M(2, 0), D(0))
    c.imm('cmp', 5, D(0))
    B(5, 'return')
    c.imm('cmp', 65535, D(0))
    B(2, 'return')

    # Bnk.Reserve is destructive when the number already exists.
    c.move(M(2, 0), D(0))
    bankcall(GETADR)
    c.move(A(0), D(0))
    c.tst(D(0))
    B(6, 'existing')
    c.move(M(2, 0), D(0))
    bankcall(GETADR)                 # repeat immediately before Reserve
    c.move(A(0), D(0))
    c.tst(D(0))
    B(6, 'existing')

    # AMOS-owned permanent DATA, Fast preferred; fixed payload for in-place
    # future multi-image updates without replacing the bank itself.
    c.move(M(2, 0), D(0))
    c.move(I(1), D(1))
    c.move(I(CAPACITY), D(2))
    c.lea(0, 'bank_name')
    bankcall(RESERVE)
    c.tst(D(0))
    B(7, 'return')                   # no bank created
    c.move(D(0), M(2, 4))            # new base
    c.imm('cmp', 24, D(0))
    B(3, 'erase_new')
    c.move(D(0), D(1))
    c.imm('and', 1, D(1))
    B(6, 'erase_new')
    c.move(M(2, 4), D(0))
    c.imm('sub', 24, D(0))
    mem_ok(D(0), 'erase_new')
    c.move(M(2, 4), D(0))
    c.imm('add', CAPACITY - 1, D(0))
    B(5, 'erase_new')                # address overflow
    mem_ok(D(0), 'erase_new')

    # Canonical zero-filled payload; publish the header last.
    c.move(M(2, 4), A(1))
    c.move(I(CAPACITY // 4), D(6))
    L('zero_bank')
    c.raw('4299')                    # CLR.L (A1)+
    c.quick(1, D(6), sub=True)
    B(6, 'zero_bank')
    c.move(M(2, 4), A(1))
    for word in (
        0x41474142, 0x4f423031,  # "AGABOB01"
        0x00010080,              # VERSION=1, SLOTS=128
        0x00000000,              # COUNT=0, FLAGS=0
        CAPACITY, DATA_OFFSET, 40, 24, DATA_OFFSET, 0
    ):
        c.move(I(word), POST(1))
    bankcall(CHANGE)
    B(0, 'select')

    L('existing')
    c.move(A(0), M(2, 4))
    c.move(A(0), D(0))
    c.imm('cmp', 24, D(0))
    B(3, 'return')
    c.move(D(0), D(1))
    c.imm('and', 1, D(1))
    B(6, 'return')
    c.move(M(2, 4), D(0))
    c.imm('sub', 24, D(0))
    mem_ok(D(0), 'return')
    c.move(M(2, 4), D(0))
    c.imm('add', CAPACITY - 1, D(0))
    B(5, 'return')
    mem_ok(D(0), 'return')
    c.move(M(2, 4), A(0))
    c.move(M(0, -20), D(0))
    c.imm('cmp', CAPACITY + 16, D(0))
    B(6, 'return')                   # reject foreign bank/size
    c.move(M(0, -16), D(0))
    c.alu('cmp', M(2, 0), 0)
    B(6, 'return')
    c.move(I(0), D(0))
    c.move(M(0, -12), D(0), 'w')     # Reload may normalize DATA flags to 0
    c.tst(D(0))
    B(7, 'flags_ok')
    c.imm('and', 0xfffd, D(0), 'w')
    c.imm('cmp', 1, D(0), 'w')
    B(6, 'return')
    L('flags_ok')
    for offset, expected in (
        (-8, 0x41474142), (-4, 0x4f422020),
        (0, 0x41474142), (4, 0x4f423031),
        (8, 0x00010080), (16, CAPACITY),
        (24, 40), (28, 24), (32, DATA_OFFSET), (36, 0)
    ):
        c.move(M(0, offset), D(0))
        c.imm('cmp', expected, D(0))
        B(6, 'return')
    c.move(M(0, 12), D(0))          # COUNT (high WORD), FLAGS (low WORD)
    c.move(D(0), D(1))
    c.imm('and', 65535, D(1))
    B(6, 'return')                  # flags must be zero
    c.raw('4840')                   # SWAP D0
    c.imm('and', 65535, D(0))
    c.imm('cmp', 128, D(0))
    B(2, 'return')
    c.move(M(0, 20), D(0))          # used bytes, including header/directory
    c.imm('cmp', DATA_OFFSET, D(0))
    B(5, 'return')
    c.imm('cmp', CAPACITY, D(0))
    B(2, 'return')
    B(0, 'select')

    L('erase_new')
    c.move(M(2, 0), D(0))
    bankcall(EFF)
    B(0, 'return')

    L('select')
    # Intra-unit PC-relative state, stored as an ID (never as a bank pointer).
    # Compiler relocation/writability remain to be validated in real Gate C.
    c.lea(4, 'selected_bank')
    c.move(M(2, 0), D(0))
    c.move(D(0), M(4), 'w')
    c.move(I(1), D(3))
    L('return')
    c.raw('4fef0020')                # release local stack
    c.raw('4cdf77f7')                # restore preserved registers
    c.raw('74004e75')                # D2=0, RTS
    L('selected_bank')
    c.word(0)
    L('bank_name')
    c.raw(NAME.hex())
    native = c.out()
    if any(native.count(marker) != count for marker, count in (
        (GETADR, 2), (RESERVE, 1), (CHANGE, 1), (EFF, 1)
    )):
        raise ValueError('unexpected AMOS bank API calls')
    if native[c.labels['selected_bank']:c.labels['selected_bank'] + 2] != b'\0\0':
        raise ValueError('native selected-bank state not zero-initialized')
    return native, c.labels


def build() -> tuple[bytes, dict]:
    protected = PROTECTED.read_bytes()
    old = EXPERIMENT.read_bytes()
    if sha256(protected).hexdigest() != R84_SHA:
        raise ValueError('R84 LAST_GOOD differs')
    if sha256(old).hexdigest() != R88_SHA:
        raise ValueError('R88 candidate differs')
    source = inspect(parse(old))
    if source['issues'] or len(source['tokens']) != 79:
        raise ValueError('original AP20 contract differs')
    original_tokens, original_parts, _ = unpack_ap20(old)
    if len(original_parts) != 88 or original_parts[83].endswith(GETP):
        raise ValueError('R88 public entry mismatch')
    if not original_parts[86].startswith(DISPATCH_V2):
        raise ValueError('not a R88 Compiler V2 Bob unit')

    native, labels = emit_bank_select()
    stubs = []
    for i, old_stub in enumerate(original_parts[:BANK]):
        if old_stub in (b'', GETP):
            stubs.append(old_stub)
            continue
        if not (old_stub[:2] == RBSR and len(old_stub) in (8, 12)
                and old_stub[6:8] == bytes.fromhex('4e75')):
            raise ValueError(f'unsupported original AP20 stub {i}')
        group, offset = unpack_from('>HH', old_stub, 2)
        if group not in (84, 85, 86, 87):
            raise ValueError(f'unknown native group {group}')
        stubs.append(RBSR + pack('>HH', group + 1, offset) + old_stub[6:])
    bank_offset = len(original_parts[86]) - len(DISPATCH_V2)
    stubs.append(RBSR + pack('>HH', GROUP_BOBS, bank_offset)
                 + bytes.fromhex('4e75') + GETP)
    groups = [original_parts[84], original_parts[85],
              original_parts[86] + native, original_parts[87]]
    packed = repack_ap20(
        old, original_tokens[:-6] + token(*COMMAND) + bytes(6),
        stubs + groups, TITLE)
    report = inspect(parse(packed))
    if report['issues'] or report['tokens'][:-1] != source['tokens']:
        raise ValueError(('prior ABI/token regression', report['issues']))
    observed = report['tokens'][-1]
    if (observed['name'], observed['instruction'],
            observed['function'], observed['signature']) != COMMAND:
        raise ValueError('new Bank token differs')
    if not any(p['index'] == BANK and p['parameters'] == 1 and
               p['getp'] for p in report['parameter_checks']):
        raise ValueError('GetP missing on Bank instruction')
    if any(len(group) > 65534 for group in groups):
        raise ValueError('AP20 V2 unit overflow')
    links = interpreter_rbsr_displacements(stubs + groups)
    if max(map(abs, links.values())) >= 32766:
        raise ValueError('Interpreter BSR.W out of range')
    if packed == old or original_parts[87] != groups[-1]:
        raise ValueError('baseline mutation')
    return packed, {
        'sha256': sha256(packed).hexdigest(),
        'bytes': len(packed),
        'commands': len(report['tokens']) - 1,
        'ap20_entries': len(stubs) + len(groups),
        'bob_unit_bytes': len(groups[2]),
        'bob_unit_margin': 65534 - len(groups[2]),
        'max_interpreter_displacement': max(map(abs, links.values())),
        'selected_bank_offset': bank_offset + labels['selected_bank'],
        'verdict': 'NATIVE BANK CODE EMITTED; STATIC AP20 ONLY; NOT INSTALLED'
    }


if __name__ == '__main__':
    _, report = build()
    print('M19 AGA BOB BANK NATIVE UNINSTALLED:', report)
