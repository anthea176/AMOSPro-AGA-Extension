#!/usr/bin/env python3
"""R82 AGAPIC v2 + four Bank Palette APIs, in-memory structural preview.

No output file. No API installation. Native Image Draw, Image Region and
Bank Palette handlers require independent CPU Gate A and WinUAE Gate B.
The R81 source builder remains frozen and SHA pinned; R82 may be the active promoted LAST_GOOD.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from audit_ap20 import inspect,parse
from build_agapic_v2_r82_api_preview import build as build_api_preview, APIS
from build_c2p_r81_opt020 import build as build_r81
from active_library import R82_SHA, R83_SHA, R84_SHA, R85_SHA, R86_SHA, R87_SHA, R88_SHA, P0C_SHA, P0D_SHA, AP20_ISLANDS_SHA, B7_SHA, B7M1_SHA, B7M2_SHA, B8_SHA, B8S1_SHA, P0_FREE_SHA
from build_c2p_r76_rpg_fix import SITES,state_offset
from compiler_bridge_v2_probe import unwrap_native_parts_v2,wrap_native_ap20_v2
from compiler_relocation import GETP,repack_ap20,unpack_ap20
from native_relative_links import assert_native_links
from c2p_r74_relink import check_cross_r74
from aga_compiler_capacity import inspect_library
from m18_image_region_emit import emit_image_region
from m18_image_region_v2_emit import emit_image_region_v2
from m16_agapic_v2_bank_wrap_emit import emit_bank_palette_init,emit_bank_palette_capture
from m16_agapic_v2_palette_emit import emit_bank_palette_apply,emit_bank_palette_fade

ROOT=Path(__file__).resolve().parents[1]
R81_SHA='9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4'
TITLE=(b'AMOSPro AGA AGAPIC v2 Palette and Region R82 0.13.27 candidate\0'
       b'$VER: AMOSPro_AGA 0.13.27\0')
TITLE+=bytes(len(TITLE)&1)


def native_starts(parts):
    pos=0
    out=[]
    for part in parts:
        assert not len(part)&1
        out.append(pos)
        pos+=len(part)
    return out


def build():
    parent,_=build_r81()
    assert sha256(parent).hexdigest()==R81_SHA
    assert sha256((ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()).hexdigest() in (R81_SHA,R82_SHA,R83_SHA,R84_SHA,P0_FREE_SHA), 'unrecognized SHA-pinned LAST_GOOD'
    current_sha=sha256((ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()).hexdigest()
    if current_sha in (R83_SHA,R84_SHA,R85_SHA,R86_SHA,R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA):
        assert sha256((ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()).hexdigest() in (R82_SHA,R83_SHA,R84_SHA,P0_FREE_SHA), 'R83/R84 requires known SHA-pinned LAST_GOOD'
    assert current_sha in (R81_SHA,R82_SHA,R83_SHA,R84_SHA,R85_SHA,R86_SHA,R87_SHA,R88_SHA,P0C_SHA,P0D_SHA,AP20_ISLANDS_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA),'unrecognized active historical/R84/R85/R86 binary'
    proto,proto_meta=build_api_preview()
    tokens,parts=unwrap_native_parts_v2(proto)
    _t,orig=unwrap_native_parts_v2(parent)
    assert len(parts)==80 and len(orig)==76
    old_region,_=emit_image_region(opt020=True)
    newer_region,labels=emit_image_region_v2()
    assert len(newer_region)&1==0 and len(newer_region)>0
    assert parts[59]==orig[59]==old_region+GETP, 'R81 Region changed'
    assert newer_region!=old_region and 'v2_mode_ok' in labels
    parts[59]=newer_region+GETP

    # Region body changes the offsets of the four newly appended Bank
    # Palette wrapper entries. Re-emit their REAL BSR.L displacements.
    # Existing links within the first 70 entries are unaffected by a
    # source-and-target before entry 59; prove them explicitly anyway.
    assert_native_links(parts[:70])
    check_cross_r74(parts[:70])
    assert state_offset(parts)==12070
    for entry,pos,opcode in SITES:
        assert parts[entry][pos:pos+4]==opcode.to_bytes(2,'big')+bytes.fromhex('2f26')
    emitters=(emit_bank_palette_init,emit_bank_palette_capture,
              emit_bank_palette_apply,emit_bank_palette_fade)
    starts=native_starts(parts)
    sizes=[]
    for i,(emitter,target) in enumerate(zip(emitters,(41,42,43,44))):
        entry=76+i
        new,labels=emitter(starts[entry],starts[target])
        assert labels['native_start']==starts[entry]
        assert labels['native_target']==starts[target]
        assert 0<len(new)<2500 and not len(new)&1
        last=entry==79
        oldlen=len(parts[entry])
        parts[entry]=new+(b'' if last else GETP)
        sizes.append(len(new))
        assert len(parts[entry])==oldlen, (
           'R82 palette wrapper length drift after Region relocation',entry,len(parts[entry]),oldlen)
    changed={i for i,(old,p) in enumerate(zip(orig,parts)) if old!=p}
    assert {20,55,57,58,59,75} <= changed, changed
    assert parts[:20]==orig[:20]
    assert all(parts[i]==orig[i] for i in range(60,75))
    assert_native_links(parts[:70]);check_cross_r74(parts[:70])
    binary=wrap_native_ap20_v2(repack_ap20(parent,tokens,parts,TITLE),TITLE)
    assert unwrap_native_parts_v2(binary)==(tokens,parts)
    tok,entries,returned_title=unpack_ap20(binary)
    assert tok==tokens and returned_title==TITLE and len(entries)==81
    report=inspect(parse(binary))
    assert not report['issues'],report['issues']
    public=[t for t in report['tokens'] if t['name'].startswith('aga ')]
    assert len(public)==74 and [p['name'] for p in public[-4:]]==[a[0] for a in APIS]
    assert [p['function'] for p in public[-4:]]==[76,77,78,79]
    for i,argc in ((76,2),(77,2),(78,2),(79,3)):
        assert any(x['index']==i and x['parameters']==argc and x['getp']
                   for x in report['parameter_checks']),('GetP ABI',i)
    limit=inspect_library(binary)
    assert limit['margin']>2048,('insufficient 16-bit headroom',limit)
    assert len(newer_region) < 6000
    return binary,{
      'status':'R82 full API+Region in-memory structural preview, NOT installable',
      'size':len(binary),'sha256':sha256(binary).hexdigest(),
      'commands':len(public),'ap20_entries':len(entries),
      'native_image_growth':proto_meta['native_image_growth'],
      'native_region_growth':len(newer_region)-len(old_region),
      'native_region_bytes':len(newer_region),
      'palette_bank_native_bytes':sizes,
      'monolith_bytes':limit['monolith_bytes'],
      'compiler_margin':limit['margin'],
      'gate_a':'requires complete native tests',
      'gate_b':'NOT TESTED','gate_c':'NOT TESTED',
      'R81_SHA':R81_SHA}


if __name__=='__main__':
    import argparse
    import base64
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--emit-base64',action='store_true',
                   help='Emit AP20 bytes to an explicitly gated CI log; never write a .Lib')
    args=p.parse_args()
    a,m=build()
    assert a==build()[0], 'in-memory builder nondeterminism'
    print('R82 FULL AGAPIC V2 API+REGION STRUCTURAL PASS:',m,flush=True)
    if args.emit_base64:
        print('R82_AP20_B64_BEGIN',flush=True)
        encoded=base64.b64encode(a).decode('ascii')
        for at in range(0,len(encoded),120):
            print('R82_AP20_B64 '+encoded[at:at+120],flush=True)
        print('R82_AP20_B64_END',flush=True)
