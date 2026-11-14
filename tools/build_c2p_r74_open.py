#!/usr/bin/env python3
"""Deterministic R74 Open-only AP20 V2 builder; no file writes by default.

Rebuilds immutable R73 v0.13.18, extends the WinUAE-tested DBState from
24 to 48 bytes IN PLACE, and hooks BOTH normal Screen Close and program
exit, with explicit PC-relative relink repairs before appending API 65.

No C2P Convert or Close command is exposed at R74, and no Gate B is claimed.
"""
from __future__ import annotations

import argparse
import base64
from hashlib import sha256

from audit_ap20 import inspect, parse, token
from build_opt020_p3_r73 import build as build_r73
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from native_relative_links import assert_native_links, relink_native_parts
from c2p_r74_open_emit import emit_open, emit_cleanup_hooks
from c2p_r74_relink import (
    CROSS, check_cross_r74, expect_word_branch, patch_cross_r74,
    patch_word_branch,
)

R73_SHA='c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407'
API=('aga c2p open',1,70,'00')
TITLE=(b'AMOSPro AGA C2P Open R74 0.13.19 candidate\0'
       b'$VER: AMOSPro_AGA 0.13.19\0')
TITLE+=bytes(len(TITLE)&1)


def patch_screen_close(parts):
    """Use instruction locations from SHA-pinned R57 68k source export."""
    assert len(parts)==70
    # Baseline MUST already target these exact (source-verified) calls.
    for name,src,off,dst,to in CROSS:
        expect_word_branch(parts,src,off,dst,to,0x6100)
    expect_word_branch(parts,0,0x40,0,0x1c8,0x6000)
    expect_word_branch(parts,8,0x08,8,0x126,0x6000)
    assert parts[10][0x1c:0x1e]==bytes.fromhex('7018')
    assert parts[8].endswith(GETP)

    code,labels=emit_cleanup_hooks()
    pre8=len(parts[8])-len(GETP)
    # Keep all existing instructions at identical entry-relative offsets.
    parts[8]=parts[8][:-len(GETP)]+code+GETP
    p=bytearray(parts[10])
    p[0x1c:0x1e]=bytes.fromhex('7030') # MOVEQ #48,D0, MEMF_CLEAR preserved
    parts[10]=bytes(p)
    # Entry00 AMOS-exit path -> helper. Entry08 normal close -> helper.
    patch_word_branch(parts,0,0x40,8,pre8+labels['program_exit_hook'],opcode=0x6000)
    patch_word_branch(parts,8,0x08,8,pre8+labels['screen_hook'],opcode=0x6000)
    # Both hook entrances run idempotent cleanup then resume existing code.
    patch_word_branch(parts,8,pre8+labels['jmp_normal'],8,0x126,opcode=0x6000)
    patch_word_branch(parts,8,pre8+labels['jmp_program_exit'],0,0x1c8,opcode=0x6000)
    # The enlarged entry08 displaced THREE previously valid cross-entry BSRs.
    patch_cross_r74(parts)
    # R70's older three native links must also remain exact after changes.
    parts[:]=relink_native_parts(parts)
    assert_native_links(parts)
    check_cross_r74(parts)
    for src,off,dst,to in (
        (0,0x40,8,pre8+labels['program_exit_hook']),
        (8,0x08,8,pre8+labels['screen_hook']),
        (8,pre8+labels['jmp_normal'],8,0x126),
        (8,pre8+labels['jmp_program_exit'],0,0x1c8),
    ):
        expect_word_branch(parts,src,off,dst,to,0x6000)
    return dict(old_close_size=pre8+4,new_close_size=len(parts[8]),
                close_cleanup_bytes=len(code),close_labels=labels)


def build():
    old,old_meta=build_r73()
    assert sha256(old).hexdigest()==R73_SHA,'Protected R73 changed'
    tokens,original=unwrap_native_parts_v2(old)
    assert len(original)==70
    assert_native_links(original)
    parts=list(original)
    hook_info=patch_screen_close(parts)
    op,labels=emit_open()
    assert op[:4]==bytes.fromhex('48e7efee') and op.count(bytes.fromhex('fe11f700031d'))==1
    assert labels['release']<labels['reject']<labels['c2p_library_name']
    assert not parts[-1].endswith(GETP)
    parts[-1]=parts[-1]+GETP
    parts.append(op)
    assert len(parts)==71 and parts[70]==op
    changed={i for i in range(70) if parts[i]!=original[i]}
    assert changed=={0,8,10,69},changed
    check_cross_r74(parts)
    assert_native_links(parts[:70])

    ntokens=tokens[:-6]+token(*API)+bytes(6)
    native=repack_ap20(old,ntokens,parts,TITLE)
    candidate=wrap_native_ap20_v2(native,TITLE)
    t,extract=unwrap_native_parts_v2(candidate)
    title=unpack_ap20(candidate)[2]
    assert t==ntokens and extract==parts and title==TITLE
    assert len(extract)==71
    assert_native_links(extract[:70])
    check_cross_r74(extract)
    audit=inspect(parse(candidate))
    assert not audit['issues'],audit['issues']
    api=[row for row in audit['tokens'] if row['name'].startswith('aga ')]
    assert len(api)==65
    assert api[-1]['name']=='aga c2p open' and api[-1]['function']==70 and api[-1]['signature']=='00'
    assert len(unpack_ap20(candidate)[1])==72
    return candidate,dict(
        version='R74 v0.13.19 Aga C2P Open (4..8 planes)',
        sha256=sha256(candidate).hexdigest(),size=len(candidate),
        commands=65,ap20_entries=72,code_bytes=len(op),
        original_native_changed=sorted(changed),
        compiler_v2_bytes=len(unpack_ap20(candidate)[1][-1]),
        source_sha=R73_SHA,**hook_info,
        gate_a='PENDING native CPU validation',gate_b='NOT TESTED')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-base64',action='store_true')
    args=parser.parse_args()
    data,info=build()
    assert data==build()[0],'Non-deterministic R74 builder'
    print('R74 OPEN-ONLY IN-MEMORY BUILD',info,flush=True)
    if args.emit_base64:
        print('R74_B64_BEGIN',flush=True)
        value=base64.b64encode(data).decode('ascii')
        for i in range(0,len(value),120):print('R74_B64 '+value[i:i+120],flush=True)
        print('R74_B64_END',flush=True)


if __name__=='__main__':main()
