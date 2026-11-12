#!/usr/bin/env python3
"""R38 v0.11.0 deterministic in-memory AMCAF BankFont candidate.

Base is frozen WinUAE PASS R37. Only existing entry 48 receives three
size-preserving calls to the R38 font release helper; entry 48 gets its
GetP delimiter and entry 49 is appended. R38 and LAST_GOOD are not written.
"""
import argparse
import base64
from pathlib import Path
from struct import pack

from ap20_utils import split, digest
from audit_ap20 import parse, inspect, token
from m14_font_select_r37_emit import emit_font_select
from m14_font_bank_r38_emit import emit_bank_select, ENTRY_INDEX

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'dist/experimental/AMOSPro_AGA_M14_v0.10.9_FONT_SELECT_R37.Lib'
BASE_SHA256 = 'bc6e7535ef300551298edae1a205ffdffa38db81e4126a5a42b36a0261b5e58a'
LAST_GOOD = ROOT / 'dist/AMOSPro_AGA_LAST_GOOD.Lib'
LAST_GOOD_SHA256 = '9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf'
DEST = ROOT / 'dist/AMOSPro_AGA.Lib'
ARCHIVE = ROOT / 'dist/experimental/AMOSPro_AGA_M14_v0.11.0_AMCAF_BANK_R38.Lib'
GETP = b'GetP'
API = (('aga font bank select',ENTRY_INDEX,'00,0'),)
VERSION = 'R38 0.11.0'


def offsets(segments):
    a=[]; pos=0
    for s in segments:
        a.append(pos); pos+=len(s)
    return a


def patch_pc16(segment, operand_at, caller, target, opcode):
    assert segment[operand_at-2:operand_at] == opcode, (operand_at,opcode)
    delta = target-(caller+operand_at)
    assert -32768 <= delta <= 32767, (operand_at,delta)
    return segment[:operand_at] + pack('>h',delta) + segment[operand_at+2:]


def build():
    frozen=BASE.read_bytes()
    assert digest(frozen)==BASE_SHA256,'frozen R37 archive changed'
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256,'R38 LAST_GOOD changed'
    tokens, old, _ = split(frozen)
    assert len(old)==ENTRY_INDEX==49
    assert not old[-1].endswith(GETP)
    assert not inspect(parse(frozen))['issues']
    assert len([x for x in inspect(parse(frozen))['tokens'] if x['name'].startswith('aga ')])==43

    oldfont, old_labels=emit_font_select()
    assert old[48]==oldfont,'R37 selector has changed'
    release_calls = []
    needle=bytes.fromhex('4eaeffb2') # JSR -78(A6) CloseFont
    pos=0
    while (pos:=oldfont.find(needle,pos))>=0:
        release_calls.append(pos)
        pos+=len(needle)
    assert len(release_calls)==3,release_calls
    bank_code, bank_labels=emit_bank_select()
    assert bank_code[-8:]==bytes(8)
    assert bank_labels['bank_state']==len(bank_code)-8

    parts=list(old)
    parts[48]=oldfont+GETP
    parts.append(bank_code)
    starts=offsets(parts)
    target_release=starts[49]+bank_labels['font_release']
    target_state=starts[48]+old_labels['font_state']
    for site in release_calls:
        seg=parts[48]
        assert seg[site:site+4]==needle
        seg=seg[:site]+b'\x61\x00\x00\x00'+seg[site+4:]
        parts[48]=patch_pc16(seg,site+2,starts[48],target_release,b'\x61\x00')
    for tag in ('r37_state_lookup','r37_state_commit'):
        parts[49]=patch_pc16(parts[49],bank_labels[tag],starts[49],target_state,b'\x43\xfa')
    assert parts[:48]==old[:48],'R38 changed R37 core / previous functions'
    assert parts[48][:-4] != old[48]
    assert parts[48][-4:]==GETP
    assert parts[49][-8:]==bytes(8)

    new_tokens=tokens[:-6]+token(API[0][0],1,API[0][1],API[0][2])+bytes(6)
    title=b'AMOSPro AGA M14 AMCAF Bank Font R38 0.11.0\0$VER: AMOSPro_AGA 0.11.0\0'
    if len(title)&1:title+=b'\0'
    code=b''.join(parts)
    payload=(pack('>4I',len(parts)*2,len(new_tokens),len(code),len(title))
        +b'\0\0AP20'+b''.join(pack('>H',len(x)//2) for x in parts)
        +new_tokens+code+title+b'\0\0')
    payload+=bytes(-len(payload)%4)
    words=pack('>I',len(payload)//4)
    candidate=frozen[:20]+words+frozen[24:28]+words+payload+frozen[-4:]
    assert split(candidate)[:2]==(new_tokens,parts)
    audited=inspect(parse(candidate))
    assert audited['issues']==[],audited['issues']
    named=[x for x in audited['tokens'] if x['name'].startswith('aga ')]
    assert len(named)==44
    matches=[x for x in named if x['name']==API[0][0]]
    assert len(matches)==1 and (matches[0]['instruction'],matches[0]['function'],matches[0]['signature'])==(1,49,'00,0')
    assert any(x['index']==49 and x['parameters']==2 and x['getp'] for x in audited['parameter_checks'])
    return candidate,dict(version=VERSION,sha256=digest(candidate),size=len(candidate),
                          named_commands=44,segments=50,new_command=API[0],
                          changed_segments=[48,49],release_calls=release_calls,
                          bank_labels=bank_labels,Gate_A='REQUIRES_NATIVE_CPU_CI',
                          Gate_B='NOT_TESTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-base64',action='store_true')
    args=parser.parse_args()
    binary,meta=build()
    assert binary==build()[0],'R38 not deterministic'
    print('R38 in-memory:',{k:v for k,v in meta.items() if k!='bank_labels'},flush=True)
    if args.emit_base64:
        print('R38_BASE64_BEGIN',flush=True)
        s=base64.b64encode(binary).decode('ascii')
        for i in range(0,len(s),76):print(s[i:i+76],flush=True)
        print('R38_BASE64_END',flush=True)
