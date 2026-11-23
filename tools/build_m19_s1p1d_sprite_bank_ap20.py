#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S1-P1d: P2d + first candidate AMOS instruction Aga Sprite Bank N.

Public token, GETP and MC68020 dispatcher are linked IN MEMORY. No candidate
is written to disk; distribution Lib P2d and LAST_GOOD remain byte-exact.
No future Get AGA Sprite or hardware DMA APIs are claimed.
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
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import GETP,RBSR,repack_ap20,unpack_ap20

NAME='aga sprite bank'
SIGNATURE='I0'
TITLE=b'AMOSPro AGA M19 S1-P1d Sprite Bank MC68020 candidate\0$VER: AGSP S1-P1d\0'
TITLE += bytes(len(TITLE)&1)


def build_sprite_bank_candidate(native: bytes) -> tuple[bytes,dict]:
    if type(native) is not bytes or len(native)<1000 or len(native)&1:
        raise ValueError('invalid MC68020 native image')
    if len(native)+len(DISPATCH_V2)>MAX_UNIT_BYTES:
        raise ValueError('AP20 sprite unit too large')
    if not native.startswith(b'\x60\x00'):
        raise ValueError('expected native public entry BRA.W at offset 0')
    if b'\xfe\x11\xf7\x00' not in native:
        raise ValueError('AMOS Main markers missing in native image')
    p2d,base=build_p2d()
    if sha256(p2d).hexdigest()!=P2D_SHA or (base['entries'],base['commands'])!=(203,100):
        raise ValueError('authoritative P2d changed')
    tok,parts,oldtitle=unpack_ap20(p2d)
    if len(parts)!=203 or not parts[-1].startswith(DISPATCH_V2):
        raise ValueError('source V2 group unexpected')
    if NAME in [r['name'] for r in walk_tokens(tok)]:
        raise ValueError('public Sprite bank token already exists')
    marker=len(parts)
    stub=marker+1
    group=marker+2
    # GETP belongs BEFORE the following instruction stub, never behind it.
    bankstub=RBSR+pack('>HH',group,0)+b'\x4e\x75'
    newparts=[*parts,GETP,bankstub,DISPATCH_V2+native]
    updated=tok[:-6]+token(NAME,stub,1,SIGNATURE)+tok[-6:]
    candidate=repack_ap20(p2d,updated,newparts,TITLE)
    tokens,sections,title=unpack_ap20(candidate)
    if (tokens!=updated or sections!=newparts or title!=TITLE or
            sections[:203]!=parts):
        raise ValueError('AP20 round-trip or P2d code regression')
    audit=inspect(parse(candidate))
    if audit['issues']:
        raise ValueError('AP20 token/GetP audit: '+repr(audit['issues']))
    prior=list(walk_tokens(tok))
    now=list(walk_tokens(tokens))
    if len(now)!=len(prior)+1 or now[:-1]!=prior:
        raise ValueError('AP20 prior token ABI changed')
    public=now[-1]
    if (public['name'],public['instruction'],public['function'],public['signature']) != (NAME,stub,1,SIGNATURE):
        raise ValueError('new Sprite Bank instruction signature changed')
    links=pc16_displacements(sections)
    oldlinks=pc16_displacements(parts)
    if any(links.get(k)!=v for k,v in oldlinks.items()):
        raise ValueError('P2d GRouB displacement changed')
    if links.get(stub) is None:
        raise ValueError('no PC16 link from public stub to new native group')
    return candidate,dict(
        sha256=sha256(candidate).hexdigest(),bytes=len(candidate),
        previous_sha256=P2D_SHA,public_name=NAME,signature=SIGNATURE,
        native_sha256=sha256(native).hexdigest(),native_bytes=len(native),
        original_public_commands=len(prior)-1,
        candidate_public_commands=len(now)-1,
        marker_index=marker,stub_index=stub,group_index=group,
        max_pc16=max(map(abs,links.values())),
        installable=False,distributed=False,compiler_tested=False)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--native',type=Path,required=True)
    args=p.parse_args()
    _raw,report=build_sprite_bank_candidate(args.native.read_bytes())
    print('S1_P1D_PUBLIC_BANK_AP20_IN_MEMORY',report)
    print('NO_LIB_FILE; NO_P2D_PROMOTION; NO_WINUAE_OR_COMPILER_CLAIM')


if __name__=='__main__':
    main()
