#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Reconstruct P1i from exact P1h source; no distributed file writes."""
from pathlib import Path
from hashlib import sha1, sha256
from active_library import P2DL2B_SHA, S1P1H_SHA, S1P1I_SHA, S1P2I_SHA, S1P2J_SHA, S1P2K_SHA, S1P2LB_SHA, frozen_s1p1i, verify_s1p1i
from audit_ap20 import inspect, parse, token_role_issues
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_s1p1h_l2b_bank_fix_ap20 import assemble, build_s1p1h
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20

ROOT=Path(__file__).resolve().parents[1]
MASTER='M19_S1P1I_BANK_PUBLIC_MC68020.s'

def build_s1p1i(vasm):
    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert sha256(active).hexdigest() in (S1P1H_SHA,S1P1I_SHA,S1P2I_SHA,S1P2J_SHA,S1P2K_SHA,S1P2LB_SHA)
    assert sha256(good).hexdigest()==P2DL2B_SHA
    parent,meta=build_s1p1h(vasm)
    assert sha256(parent).hexdigest()==S1P1H_SHA
    if sha256(active).hexdigest()==S1P1H_SHA:
        assert parent==active
    tok,old,title=unpack_ap20(parent)
    native=assemble(vasm,MASTER)
    assert native[:2]==b'\x60\x00' and len(native)%2==0
    assert len(native)+len(DISPATCH_V2)<=MAX_UNIT_BYTES
    parts=old[:207]+[DISPATCH_V2+native]
    assert len(parts)==208 and parts[:203]==unpack_ap20(good)[1]
    assert [i for i,(a,b) in enumerate(zip(parts,old)) if a!=b]==[207]
    assert pc16_displacements(parts)==pc16_displacements(old)
    new_title=title.replace(b'S1-P1h',b'S1-P1i')
    assert new_title!=title
    image=repack_ap20(parent,tok,parts,new_title)
    assert unpack_ap20(image)==(tok,parts,new_title)
    verify_s1p1i(image,good)
    if sha256(active).hexdigest()==S1P1I_SHA:
        assert image==active
    elif sha256(active).hexdigest() in (S1P2I_SHA,S1P2J_SHA,S1P2K_SHA,S1P2LB_SHA):
        assert image==frozen_s1p1i(active,good)
    audit=inspect(parse(image))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert (ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()==active
    assert (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()==good
    return image,dict(meta,sha256=sha256(image).hexdigest(),bytes=len(image),
                      native_sha256=sha256(native).hexdigest(),native_size=len(native),
                      token_parent_sha256=S1P1H_SHA,commands=102,entries=208,
                      git_blob=sha1(f'blob {len(image)}'.encode()+bytes([0])+image).hexdigest(),
                      installable=False,runtime_tested=False,compiler_tested=False)
