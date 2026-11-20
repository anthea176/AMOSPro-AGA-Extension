#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1b real native AGBO -> checked cache -> Hot Spot -> Safe Blitter Gate A.

Runs actual source-generated MC68020 BOBS code with mocked AMOS, Exec, Gfx
and Blitter on TWO disjoint native layouts. Tests pixel-exact masked/Opaque
output on the non-displayed AGA back buffer. NOT WinUAE, NOT real Compiler.
"""
from __future__ import annotations
from hashlib import sha256
from struct import pack,unpack_from
from capstone import Cs,CS_ARCH_M68K,CS_MODE_BIG_ENDIAN,CS_MODE_M68K_020
from build_m19_p1b_hotspot_in_memory import build_p1b
from m19_p1b_hotspot_draw_emit import emit_p1b_hotspot_draw
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free
from m19_p0j_explicit_safe_draw_emit import emit_explicit_bob_draw
from test_m19_p0j_explicit_safe_draw_gate_a import NoShadowMachine
from test_m19_p0d_safe_bank_blit_native import oracle,SIZE
from build_m19_p0c_screen_close_in_memory import build as build_p0c
from m19_p0a_multi_bob_abk import parse_payload,set_hotspot
from test_m19_p0a_r88_get_gate_a import SCREEN_W, SCREEN_H
from m19_p1b_hotspot_draw_model import clipped_origin
from amos_link_test_support import relocate

def machine(layout,hot10=(0,0),hot11=(0,0),all64=False):
    source,_=build_p0c()
    m=NoShadowMachine(source,layout)
    raw,labels=emit_p1b_hotspot_draw()
    m.draw_native=raw
    m.labels=labels
    m.labels['routed_paint_all_entry']=labels['explicit_frame_draw_entry']
    m.uc.mem_write(m.entry,relocate(raw,m.entry,{},m.uc))
    assert m.run_select(10)==1
    assert m.run_get(1,4,5,20,8)==1
    assert m.mask(True,1,0)==1
    assert m.run_select(11)==1
    assert m.run_get(1,7,8,16,15)==1
    # Edit the live original AGBO BEFORE any object registration or
    # Chip staging; preserve byte length, images, mask and all plane bits.
    for bank,hot in ((10,hot10),(11,hot11)):
        original=m.bank_payload(bank)
        changed=set_hotspot(original,1,*hot)
        assert len(original)==len(changed)
        assert parse_payload(changed).image(1).hotspot_x==hot[0]
        assert parse_payload(changed).image(1).hotspot_y==hot[1]
        m.uc.mem_write(m.find(bank)+24,changed)
    m.activate_aga_state()
    m.configure_real_state()
    if not all64:
        assert m.run_select(10)==1
        assert m.public('bob',ident=1,x=5,y=7,image=1)==1
        assert m.run_select(11)==1
        assert m.public('bob',ident=2,x=9,y=11,image=1)==1
    else:
        for ident in range(1,65):
            bank=10 if ident<=32 else 11
            assert m.run_select(bank)==1
            assert m.public('bob',ident=ident,image=1,
                            x=(ident*7)%65,y=(ident*11)%45)==1
    assert m.run_select(11)==1
    return m

def check_frame(m,hot10,hot11,all64=False):
    i10=parse_payload(m.bank_payload(10)).image(1)
    i11=parse_payload(m.bank_payload(11)).image(1)
    selected=m.selected_triple()
    front=tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)
    before=m.read_back()
    expected=before
    if not all64:
        expected=oracle(expected,i10,5-hot10[0],7-hot10[1])
        expected=oracle(expected,i11,9-hot11[0],11-hot11[1])
    else:
        for ident in range(1,65):
            if ident<=32:
                img,hot=i10,hot10
            else:
                img,hot=i11,hot11
            x=(ident*7)%65-hot[0];y=(ident*11)%45-hot[1]
            expected=oracle(expected,img,x,y)
    assert m.frame()==1,('P1b integrated frame refused',m.route_trace[-12:])
    assert m.read_back()==expected,'P1b native Blitter drew wrong offset/mask/pixel'
    assert m.selected_triple()==selected
    assert m.get(0x53000+8)==0,'P1b implicitly swapped'
    assert tuple(bytes(m.uc.mem_read(p,SIZE)) for p in m.screen_planes)==front
    return len([c for c in m.paint_blits if c[0] in ('BltMask','BltOpaque')])

def main():
    image,meta=build_p1b()
    assert meta['public_commands']==92 and meta['ap20_entries']==188
    assert meta['native_groups']==[142,153,156,177,181]
    assert meta['pc16_max']<32766 and image==build_p1b()[0]
    raw,lab=emit_p1b_hotspot_draw()
    old,_=emit_b8_s1_bank_free()
    site=lab['p1b_source_patch_site']
    assert raw[:site+2]==old[:site+2]
    assert raw[site+4:len(old)]==old[site+4:]
    assert raw[site:site+2]==b'\x60\x00'
    assert site+2+unpack_from('>h',raw,site+2)[0]==lab['p1b_image_hotspot_join']
    ins=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_020).
             disasm(raw[lab['p1b_image_hotspot_join']:],
                    0x120000+lab['p1b_image_hotspot_join']))
    assert sum(i.size for i in ins)==len(raw)-lab['p1b_image_hotspot_join']
    assert all(not i.mnemonic.startswith('dc.') for i in ins)
    checks=10
    profiles=[
        ((0,0),(0,0),2),                  # P1a/P0 exact zero-hotspot
        ((3,2),(-4,5),2),                 # masked+opaque, mixed sign
        ((10,8),(0,0),2),                 # negative origin, partial clip
        ((32767,32767),(0,0),1),          # one fully clipped
        ((32767,32767),(-32768,-32768),0),# both clipped, no DMA/no swap
        ((-3,-5),(4,7),2)                # positive shift, transparency
    ]
    for layout in ('interpreted','compiled'):
        for h10,h11,expected_blits in profiles:
            m=machine(layout,h10,h11)
            found=check_frame(m,h10,h11)
            assert found==expected_blits,('unexpected Blitter calls',layout,h10,h11,found)
            checks+=5
            # Original source pointer / generation / metadata are unchanged.
            assert (parse_payload(m.bank_payload(10)).image(1).hotspot_x,
                    parse_payload(m.bank_payload(10)).image(1).hotspot_y)==h10
            checks+=1

        m=machine(layout,(2,1),(-2,1),all64=True)
        images={n:parse_payload(m.bank_payload(n)).image(1) for n in (10,11)}
        visible=0
        for ident in range(1,65):
            bank=10 if ident<=32 else 11
            hot=(2,1) if bank==10 else (-2,1)
            img=images[bank]
            if clipped_origin((ident*7)%65,(ident*11)%45,*hot,
                              img.width,img.height,SCREEN_W,SCREEN_H) is not None:
                visible+=1
        assert visible<64 and visible>=60,('expected clipped Bobs',visible)
        assert check_frame(m,(2,1),(-2,1),True)==visible
        allocations,copies=m.chip_allocs,m.chip_copies
        assert check_frame(m,(2,1),(-2,1),True)==2*visible
        assert (m.chip_allocs,m.chip_copies)==(allocations,copies)
        checks+=4

        # Invalid mask metadata in live bank MUST fail complete P0 image
        # preflight before any Safe Blitter call.
        m=machine(layout,(4,1),(0,0),all64=True)
        entry=m.find(10)+24+32
        size=m.get(entry+24)
        assert size>1
        m.put(entry+24,size-1)
        oldback=m.read_back()
        assert m.frame()==0 and m.read_back()==oldback
        assert not any(t[0] in ('BltMask','BltOpaque') for t in m.paint_blits)
        m.put(entry+24,size)
        assert check_frame(m,(4,1),(0,0),True)==64
        checks+=4

    print('P1B_NATIVE_SAFE_BLIT_GATE_A_PASS',checks,
          'two native placements, signed hot spots, actual Chip Mask Blitter,',
          'zero-hot P0 equivalence, fully offscreen no-op, 64 Bob cache,',
          'invalid bank fail-before-DMA, original API 92/188,',
          'bytes',len(image),'SHA256',meta['sha256'],flush=True)

if __name__=='__main__':
    main()
