#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S1-P1e: link TWO public AP20 commands against source-built P2d in memory.

   Aga Sprite Bank N
   Get AGA Sprite I,X1,Y1,X2,Y2,TransparentPen

The raw MC68020 unit contains native bank select at offset 0, the
private pipeline at offset 4 and public Get at offset 8. These are real
RBSR/GetP AP20 entries, NOT new commands in dist/AMOSPro_AGA.Lib.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack

from active_library import P2D_SHA
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect,parse,token,walk_tokens
from build_m19_p2d_in_memory import build_p2d
from compiler_bridge_v2_probe import DISPATCH_V2,MAX_UNIT_BYTES
from compiler_relocation import GETP,RBSR,repack_ap20,unpack_ap20

S1_APIS=(
    ('aga sprite bank',204,1,'I0',0),
    ('get aga sprite',206,1,'00,0,0,0,0,0',8),
)
TITLE=(b'AMOSPro AGA M19 S1-P1e Get AGA Sprite MC68020 candidate\0'
       b'$VER: AGSP S1-P1e non-distributed\0')
TITLE += bytes(len(TITLE)&1)


def build_get_aga_sprite_candidate(native:bytes)->tuple[bytes,dict]:
    if type(native) is not bytes or len(native)<1000 or len(native)&1:
        raise ValueError('native Sprite source is missing, short or unaligned')
    if len(native)+len(DISPATCH_V2)>MAX_UNIT_BYTES:
        raise ValueError('native Sprite code too large for AP20/Compiler PC16')
    if not native.startswith(b'\x60\x00'):
        raise ValueError('bank selector must start at BRA.W offset zero')
    if native[4:6]!=b'\x60\x00' or native[8:10]!=b'\x60\x00':
        raise ValueError('native private pipeline and Get entries not at 4,8')
    if b'\xfe\x11\xf7\x00' not in native:
        raise ValueError('AMOS Main pseudo ABI marker missing')
    base,meta=build_p2d()
    if sha256(base).hexdigest()!=P2D_SHA or (meta['commands'],meta['entries'])!=(100,203):
        raise ValueError('P2d source/ABI no longer matches authority')
    tok,parts,_=unpack_ap20(base)
    if len(parts)!=203 or not parts[-1].startswith(DISPATCH_V2):
        raise ValueError('source AP20 group layout drift')
    prior=list(walk_tokens(tok))
    names={x['name'] for x in prior}
    if any(api[0] in names for api in S1_APIS):
        raise ValueError('unexpected duplicate Sprite token')
    group=207
    original_203=list(parts)
    newparts=[*parts,
              GETP,RBSR+pack('>HH',group,0)+b'\x4e\x75',
              GETP,RBSR+pack('>HH',group,8)+b'\x4e\x75',
              DISPATCH_V2+native]
    updated=tok[:-6]
    for name,instruction,function,signature,offset in S1_APIS:
        updated+=token(name,instruction,function,signature)
    updated+=tok[-6:]
    candidate=repack_ap20(base,updated,newparts,TITLE)
    ct,cp,title=unpack_ap20(candidate)
    if ct!=updated or cp!=newparts or title!=TITLE or cp[:203]!=original_203:
        raise ValueError('AP20 exact HUNK roundtrip mismatch')
    audit=inspect(parse(candidate))
    if audit['issues']:
        raise ValueError('AP20 audit issues: '+repr(audit['issues']))
    after=list(walk_tokens(ct))
    if len(after)!=len(prior)+2 or after[:-2]!=prior:
        raise ValueError('public P2d token interface changed')
    if any((x['name'],x['instruction'],x['function'],x['signature'])!=api[:4]
           for x,api in zip(after[-2:],S1_APIS)):
        raise ValueError('Sprite API token signatures invalid')
    links=pc16_displacements(cp)
    original_links=pc16_displacements(parts)
    if any(links.get(k)!=value for k,value in original_links.items()):
        raise ValueError('P2d original native PC16 displacement changed')
    if set((204,206))-set(links):
        raise ValueError('public bank/Get Sprite RBSR offsets not resolved')
    return candidate,{
        'sha256':sha256(candidate).hexdigest(),
        'candidate_bytes':len(candidate),
        'P2d_sha256':P2D_SHA,
        'native_sha256':sha256(native).hexdigest(),
        'native_size':len(native),
        'original_AP20_entries':203,
        'candidate_AP20_entries':len(cp),
        'P2d_commands':100,
        'candidate_commands':102,
        'public':[(n,s,o) for n,_,_,s,o in S1_APIS],
        'native_group':group,
        'PC16_max':max(map(abs,links.values())),
        'installable':False,
        'runtime_tested':False,
        'compiler_tested':False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--native',type=Path,required=True)
    args=p.parse_args()
    _image,metadata=build_get_aga_sprite_candidate(args.native.read_bytes())
    print('S1_P1E_GET_AGA_SPRITE_IN_MEMORY',metadata)
    print('NO_FILE_WRITTEN; NO_DIST; NO_LAST_GOOD; NO_WINUAE_OR_COMPILER_CLAIM')


if __name__=='__main__':
    main()
