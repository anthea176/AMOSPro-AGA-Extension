#!/usr/bin/env python3
"""R82 in-memory only: image v2 plus four shared Bank Palette API entries.

Never writes a library file or changes LAST_GOOD. The R82 Region v2 native
path is still separate; this builder is a targeted structural experiment,
NOT a complete installable candidate. MC68020 CPU Gate A/WinUAE/Compiler
are independent qualification gates.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect,parse,token
from build_c2p_r81_opt020 import build as build_r81
from active_library import R82_SHA, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA, P1A_SHA, P1B_SHA, P1C_SHA, P1D_SHA, P1E_SHA, P2A_SHA, P2B_SHA, P2C_SHA, P2D_SHA, S1P1E_SHA
from build_c2p_r76_rpg_fix import SITES,state_offset
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from native_relative_links import assert_native_links,relink_native_parts
from c2p_r74_relink import check_cross_r74
from m16_image_draw_r45_emit import emit_image_draw
from m16_agapic_v2_draw_emit import emit_image_draw_v2
from m16_agapic_v2_bank_wrap_emit import emit_bank_palette_init,emit_bank_palette_capture
from m16_agapic_v2_palette_emit import emit_bank_palette_apply,emit_bank_palette_fade
from aga_compiler_capacity import inspect_library

ROOT=Path(__file__).resolve().parents[1]
R81_SHA='9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4'
TITLE=(b'AMOSPro AGA AGAPIC v2 Palette Bank R82 0.13.27 in-memory preview\0'
       b'$VER: AMOSPro_AGA 0.13.27 in-memory preview\0')
TITLE+=bytes(len(TITLE)&1)
APIS=(
    ('aga bank palette init',1,76,'00,0'),
    ('aga bank palette capture',1,77,'00,0'),
    ('aga bank palette apply',1,78,'00,0'),
    ('aga bank palette fade',1,79,'00,0,0'),
)


def build():
    baseline,_=build_r81()
    assert sha256(baseline).hexdigest()==R81_SHA
    assert sha256((ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()).hexdigest() in (R81_SHA,R82_SHA,R83_SHA,R84_SHA,P0_FREE_SHA,P1E_SHA,P2D_SHA), 'unrecognized SHA-pinned LAST_GOOD'
    tok,old=unwrap_native_parts_v2(baseline)
    assert len(old)==76 and not old[-1].endswith(GETP)
    assert state_offset(old)==12070
    old_draw,_=emit_image_draw(accept_loaded_flags_zero=True,
                               opt020=True,reset_failure_d3=True)
    assert old[55]==old_draw+GETP
    newer,_=emit_image_draw_v2()
    parts=list(old)
    parts[55]=newer+GETP
    parts[:70]=relink_native_parts(parts[:70])
    assert_native_links(parts[:70])
    check_cross_r74(parts[:70])
    assert state_offset(parts)==12070
    assert {i for i,(x,y) in enumerate(zip(old,parts)) if x!=y}=={20,55,57,58}
    for entry,at,opcode in SITES:
        assert parts[entry][at:at+4]==opcode.to_bytes(2,'big')+bytes.fromhex('2f26')
    # Transition to a new public API requires a GetP marker after the old
    # last native entry. Keep every existing entry's original argument ABI.
    parts[-1]+=GETP
    offset=0
    old_starts=[]
    for part in parts:
        old_starts.append(offset)
        offset+=len(part)
    assert offset==sum(map(len,parts))
    emitters=(emit_bank_palette_init,emit_bank_palette_capture,
              emit_bank_palette_apply,emit_bank_palette_fade)
    emitted=[]
    for idx,(emitter,target) in enumerate(zip(emitters,(41,42,43,44))):
        native,labels=emitter(offset,old_starts[target])
        assert 0<len(native)<2000 and not len(native)%2
        assert labels['native_start']==offset
        assert labels['native_target']==old_starts[target]
        emitted.append((native,labels))
        parts.append(native+(GETP if idx<3 else b''))
        offset+=len(parts[-1])
    assert len(parts)==80
    assert parts[:75]==(parts[:70]+old[70:75])
    assert parts[75]==old[75]+GETP
    assert all(parts[76+i].startswith(out[0]) for i,out in enumerate(emitted))
    ntok=tok[:-6]+b''.join(token(*info) for info in APIS)+bytes(6)
    image=wrap_native_ap20_v2(repack_ap20(baseline,ntok,parts,TITLE),TITLE)
    assert unwrap_native_parts_v2(image)==(ntok,parts)
    actual_token,entries,title=unpack_ap20(image)
    assert actual_token==ntok and len(entries)==81 and title==TITLE
    report=inspect(parse(image))
    assert not report['issues'],report['issues']
    oldpublic=[x for x in inspect(parse(baseline))['tokens'] if x['name'].startswith('aga ')]
    newpublic=[x for x in report['tokens'] if x['name'].startswith('aga ')]
    assert len(oldpublic)==70 and len(newpublic)==74
    assert newpublic[:70]==oldpublic
    assert [x['name'] for x in newpublic[-4:]]==[api[0] for api in APIS]
    assert [x['function'] for x in newpublic[-4:]]==[76,77,78,79]
    assert len([x for x in report['parameter_checks'] if x['index'] in (76,77,78,79)
                and x['getp']])==4
    budget=inspect_library(image)
    assert budget['margin']>2048,'Insufficient 16-bit capacity for further R82 work'
    active_sha=sha256((ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()).hexdigest()
    if active_sha in (R83_SHA,R84_SHA,R85_SHA,R86_SHA,R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1A_SHA,P1B_SHA,P1C_SHA, P1D_SHA, P1E_SHA, P2A_SHA, P2B_SHA, P2C_SHA, P2D_SHA,S1P1E_SHA):
        assert sha256((ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()).hexdigest() in (R82_SHA,R83_SHA,R84_SHA,P0_FREE_SHA,P1E_SHA,P2D_SHA), 'R83/R84 requires known SHA-pinned LAST_GOOD'
    assert active_sha in (R81_SHA,R82_SHA,R83_SHA,R84_SHA,R85_SHA,R86_SHA,R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1A_SHA,P1B_SHA,P1C_SHA, P1D_SHA, P1E_SHA, P2A_SHA, P2B_SHA, P2C_SHA, P2D_SHA,S1P1E_SHA), 'unrecognized active historical/R84/R85/R86'
    return image,dict(
        kind='R82 experimental FOUR-API in-memory structural preview',
        size=len(image),sha256=sha256(image).hexdigest(),
        commands=len(newpublic),ap20_entries=len(entries),
        compiler_unit_bytes=budget['monolith_bytes'],
        compiler_margin_bytes=budget['margin'],
        native_image_growth=len(newer)-len(old_draw),
        bank_api_bytes=[len(x[0]) for x in emitted],
        native_changed=[20,55,57,58,75,76,77,78,79],
        gate_a='SEPARATE NATIVE TESTS ONLY',gate_b='NOT TESTED',
        gate_c='NOT TESTED',installable=False)


if __name__=='__main__':
    b,meta=build()
    assert b==build()[0],'non-deterministic in-memory builder'
    print('R82 FOUR BANK PALETTE AP20 IN-MEMORY STRUCTURE PASS:',meta,flush=True)
