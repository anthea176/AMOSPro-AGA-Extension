#!/usr/bin/env python3
"""Deterministic R75 C2P Convert AP20 Compiler V2 build, no writes by default.

Starts only from byte-pinned R74 (Gate A/B PASS for Open) and appends one
self-contained no-parameter integer function. Does not alter R74 native code
or R73 LAST_GOOD. No Compiler Gate C or WinUAE Gate B claimed.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256

from audit_ap20 import inspect,parse,token
from build_c2p_r74_open import build as build_r74
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from c2p_r75_convert_emit import emit_convert,BANK

R74_SHA='887f29c0350f47af9d93d1ebf64fc405c8542e897ff0e7d9d95eda6f814c2a23'
API=('aga c2p convert',1,71,'0')
TITLE=b'AMOSPro AGA C2P Convert R75 0.13.20 candidate\0$VER: AMOSPro_AGA 0.13.20\0'
TITLE+=bytes(len(TITLE)&1)


def build():
    old,oldmeta=build_r74()
    assert sha256(old).hexdigest()==R74_SHA,'R74 Gate A/B base changed'
    tokens,original=unwrap_native_parts_v2(old)
    assert len(original)==71 and original[-1][:4]==bytes.fromhex('48e7efee')
    assert not original[-1].endswith(GETP)
    assert_native_links(original[:70]);check_cross_r74(original[:70])
    parts=list(original)
    parts[-1]=parts[-1]+GETP
    code,labels=emit_convert()
    assert len(code)<10000 and code.count(BANK)==1
    assert code[:8]==bytes.fromhex('48e7efee4fefff40')
    assert code[-4:]==bytes.fromhex('74004e75')
    assert not code.endswith(GETP)
    parts.append(code)
    assert len(parts)==72
    assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    assert parts[:70]==original[:70]
    assert parts[70]==original[70]+GETP
    ntokens=tokens[:-6]+token(*API)+bytes(6)
    native=repack_ap20(old,ntokens,parts,TITLE)
    result=wrap_native_ap20_v2(native,TITLE)
    read_tokens,read_parts=unwrap_native_parts_v2(result)
    assert read_tokens==ntokens and read_parts==parts
    _,entries,title=unpack_ap20(result)
    assert title==TITLE and len(entries)==73
    assert_native_links(read_parts[:70]);check_cross_r74(read_parts[:70])
    findings=inspect(parse(result))
    assert not findings['issues'],findings['issues']
    apis=[row for row in findings['tokens'] if row['name'].startswith('aga ')]
    assert len(apis)==66
    assert (apis[-1]['name'],apis[-1]['function'],apis[-1]['signature'])==(
        API[0],API[2],API[3])
    return result,dict(version='R75 v0.13.20 C2P Convert (4..8 planes)',
       sha256=sha256(result).hexdigest(),size=len(result),
       commands=66,ap20_entries=73,code_bytes=len(code),
       old_native_changed=[70],R74_sha=R74_SHA,
       monolith_bytes=len(entries[-1]),
       gate_a='PENDING native CPU tests',gate_b='NOT TESTED')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-base64',action='store_true',help='print binary base64 chunks to GitHub Actions output')
    args=parser.parse_args()
    data,info=build()
    assert data==build()[0],'non-deterministic candidate'
    print('R75 C2P CONVERT IN-MEMORY BUILD',info,flush=True)
    if args.emit_base64:
        print('R75_B64_BEGIN',flush=True)
        b64=base64.b64encode(data).decode('ascii')
        for i in range(0,len(b64),120):print('R75_B64 '+b64[i:i+120],flush=True)
        print('R75_B64_END',flush=True)

if __name__=='__main__':main()
