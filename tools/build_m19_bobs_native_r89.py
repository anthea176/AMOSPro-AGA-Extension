#!/usr/bin/env python3
"""M19 R89 native multi-image AGA Bob Bank + Get AGA Bob experiment.

R84 LAST_GOOD and R88 are SHA-pinned, read-only inputs. All native code
and token additions stay inside the existing compiler-safe BOBS copied unit.
This builder never writes the active extension or promotes a candidate.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack, pack_into, unpack_from
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'tools' / 'experiments')]

from active_library import R84_SHA, R88_SHA
from audit_ap20 import inspect, parse, token
from compiler_relocation import unpack_ap20, repack_ap20, RBSR, GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements
from m19_bobs_ap20_feasibility import emit_bank_select
from m19_bobs_capture_emit import emit_get_bob, GETADR

R84 = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
R88 = ROOT / 'dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib'
BANK_INDEX = 84
GET_INDEX = 85
GROUP_C2P = 86
GROUP_IFF = 87
GROUP_BOBS = 88
GROUP_AGA = 89
BANK_API = ('aga bob bank', BANK_INDEX, 1, 'I0')
GET_API = ('get aga bob', GET_INDEX, 1, 'I0,0,0,0,0')
TITLE = (b'AMOSPro AGA R89 v0.13.34 M19 NATIVE BOB BANK AND CAPTURE\0'
         b'$VER: AMOSPro_AGA 0.13.34 (R89) EXPERIMENT ONLY / NOT VALIDATED\0')
TITLE += bytes(len(TITLE) & 1)
OUT_NAME = 'AMOSPro_AGA_R89_v0.13.34_M19_BOB_CAPTURE_UNVALIDATED.Lib'


def build():
    good = R84.read_bytes()
    old = R88.read_bytes()
    if len(good) != 67904 or sha256(good).hexdigest() != R84_SHA:
        raise ValueError('R84 protected library differs')
    if len(old) != 75040 or sha256(old).hexdigest() != R88_SHA:
        raise ValueError('R88 predecessor differs')
    orig = inspect(parse(old))
    if orig['issues'] or len(orig['tokens']) != 79:
        raise ValueError('R88 baseline ABI invalid')
    orig_tokens, parts, _ = unpack_ap20(old)
    if len(parts) != 88 or not parts[86].startswith(DISPATCH_V2):
        raise ValueError('R88 Compiler V2 BOBS layout changed')

    bank, bank_labels = emit_bank_select()
    capture_unlinked, capture_labels = emit_get_bob()
    capture = bytearray(capture_unlinked)
    # Repoint LEA (d16,PC) from capture into the prior Bank routine's word.
    disp_pos = capture_labels['selection_reference'] + 2
    target = bank_labels['selected_bank']
    origin = len(bank) + disp_pos
    disp = target - origin
    if disp >= -2 or not -32768 <= disp <= 32767:
        raise ValueError('selected bank PC displacement invalid')
    if capture[disp_pos-2:disp_pos] != bytes.fromhex('49fa'):
        raise ValueError('PC-relative LEA not at expected instruction')
    pack_into('>h',capture,disp_pos,disp)
    capture = bytes(capture)
    if capture.count(GETADR) != 1:
        raise ValueError('new capture bank lookup not resolved once')

    entry_bank = len(parts[86]) - len(DISPATCH_V2)
    entry_get = entry_bank + len(bank)
    if entry_get + len(capture) > 65534:
        raise ValueError('Bob native compiler-safe copied unit overflow')
    new_bobs = parts[86] + bank + capture

    stubs=[]
    for index, old_stub in enumerate(parts[:BANK_INDEX]):
        if old_stub in (b'',GETP):
            stubs.append(old_stub)
            continue
        if old_stub[:2] != RBSR or len(old_stub) not in (8,12) or old_stub[6:8] != b'\x4e\x75':
            raise ValueError(f'unexpected R88 public stub at {index}')
        group, offset = unpack_from('>HH', old_stub, 2)
        if group not in (84,85,86,87):
            raise ValueError(f'unexpected native group {group}')
        stubs.append(RBSR + pack('>HH',group + 2,offset) + old_stub[6:])
    if stubs[-1].endswith(GETP):
        raise ValueError('last R88 stub already ends in GetP')
    stubs[-1] += GETP
    stubs.append(RBSR + pack('>HH',GROUP_BOBS,entry_bank) + b'\x4e\x75' + GETP)
    stubs.append(RBSR + pack('>HH',GROUP_BOBS,entry_get) + b'\x4e\x75')
    groups=[parts[84],parts[85],new_bobs,parts[87]]
    entries=stubs+groups
    if len(entries)!=90 or any(len(group)>65534 or len(group)&1 for group in groups):
        raise ValueError('AP20 group sizing')
    tokens = orig_tokens[:-6] + token(*BANK_API) + token(*GET_API) + bytes(6)
    packed = repack_ap20(old,tokens,entries,TITLE)
    check = inspect(parse(packed))
    if check['issues'] or check['tokens'][:-2] != orig['tokens']:
        raise ValueError(('prior token regression',check['issues']))
    for expected, actual in zip((BANK_API,GET_API),check['tokens'][-2:]):
        if (actual['name'],actual['instruction'],actual['function'],
            actual['signature']) != expected:
            raise ValueError(('new token ABI mismatch',expected,actual))
    for idx, n in ((BANK_INDEX,1),(GET_INDEX,5)):
        if not any(v['index']==idx and v['parameters']==n and v['getp']
                   for v in check['parameter_checks']):
            raise ValueError(('GetP marker mismatch',idx))
    new_toks,new_parts,new_title=unpack_ap20(packed)
    if (new_toks,new_parts,new_title)!=(tokens,entries,TITLE):
        raise ValueError('packed library mismatch')
    if any(new_parts[g] != old_part for g,old_part in (
            (GROUP_C2P,parts[84]),(GROUP_IFF,parts[85]),
            (GROUP_AGA,parts[87]))):
        raise ValueError('unrelated native unit changed')
    links = interpreter_rbsr_displacements(entries)
    if max(map(abs,links.values()))>=32766:
        raise ValueError('Interpreter negative signed displacement overflow')
    return packed, dict(sha256=sha256(packed).hexdigest(),
                        bytes=len(packed),commands=len(check['tokens'])-1,
                        ap20_entries=len(entries),
                        bob_unit_bytes=len(new_bobs),
                        native_bank_bytes=len(bank),native_capture_bytes=len(capture),
                        selected_word_offset=entry_bank+target,
                        capture_offset=entry_get,
                        max_interpreter_displacement=max(map(abs,links.values())),
                        version='R89 v0.13.34 EXPERIMENT ONLY',
                        native_gate_a='NOT TESTED',
                        winuae_b='NOT TESTED',compiler_c='NOT TESTED')


if __name__=='__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path)
    args=cli.parse_args()
    binary, report=build()
    if args.output:
        out=args.output.resolve()
        for unsafe in (R84.resolve(), R88.resolve(),
                       (ROOT/'dist/AMOSPro_AGA.Lib').resolve()):
            if out==unsafe:
                raise SystemExit('refuse writing protected or active library')
        if out.name != OUT_NAME:
            raise SystemExit(f'output file must be named {OUT_NAME}')
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_bytes(binary)
        print('WRITTEN EXPERIMENTAL ARTIFACT:',out)
    print('R89 NATIVE BOB BANK + CAPTURE STRUCTURAL REPORT:',report)
    print('No WinUAE Interpreter / AMOS Compiler execution claimed.')
