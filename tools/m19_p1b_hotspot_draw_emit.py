#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P1b: wire AGBO v1 image hotspots into the EXISTING Safe Blitter.

Keep the exact BOBS source from P0 Bank Free as bytes, except a SINGLE
source-identified BRA.W displacement after verified explicit_image_resolve.
The branch diverts to an append-only private join which re-checks the live
AGBO bank through original explicit_bank_lookup_entry, finds the validated
image directory record, calls the tested P1b MC68020 signed-origin helper
and rejoins the ORIGINAL draw_live_image_resolved SafePort/Blitter.

No AP20 command or public signature changes. Logical P0e Bob X/Y remains
untouched. An entirely clipped Bob succeeds without calling the Blitter.
Caller already established P0 checked AGBO image/staging, AGA screen, owner
and Safe back buffer. Does not create a second installable library.
"""
from __future__ import annotations
from struct import pack,unpack_from
from hashlib import sha256
from m68k_emit import Code,A,D,I,M
from m19_b8_s1_bank_free_emit import emit_b8_s1_bank_free
from m19_p0j_explicit_safe_draw_emit import emit_explicit_bob_draw
from m19_p0d_safe_bank_blit_emit import F as SAFE
from m19_p1b_hotspot_origin_emit import emit_hotspot_origin

SCRATCH=128               # 28-byte checked bank-lookup result in 256B frame
MAX_IMAGES=4096
ENTRY_BYTES=40
assert SCRATCH+28<=256 and SAFE['screen_h']==SAFE['screen_w']+4
assert SAFE['saved_a3']+4<=SCRATCH


def _original_join_branch(raw:bytes,labels:dict[str,int])->int:
    """Locate one BRA.W from original source label to original source label."""
    start=labels['explicit_safe_blit_entry']
    stop=labels['explicit_frame_draw_entry']
    target=labels['draw_live_image_resolved']
    positions=[]
    for p in range(start,stop-3,2):
        if raw[p:p+2]!=b'\x60\x00':
            continue
        delta=unpack_from('>h',raw,p+2)[0]
        if p+2+delta==target:
            positions.append(p)
    if len(positions)!=1 or positions[0]<=labels['explicit_image_resolve_entry']:
        raise ValueError('P1b: original Safe-Blit join BRA not unique/source verified')
    return positions[0]


def emit_p1b_hotspot_draw()->tuple[bytes,dict[str,int]]:
    old,labels=emit_b8_s1_bank_free()
    base,base_labels=emit_explicit_bob_draw()
    if not old.startswith(base) or any(labels[k]!=base_labels[k] for k in
         ('explicit_safe_blit_entry','explicit_frame_draw_entry','draw_live_image_resolved')):
        raise ValueError('P1b: P0j Safe/Blit source was not a byte-exact ancestor')
    patch=_original_join_branch(old,labels)
    hotspot,hotlabs=emit_hotspot_origin()
    if hotlabs['p1b_hotspot_origin_entry']!=0:
        raise ValueError('P1b origin native entry drift')
    c=Code();c.raw(old.hex());c.labels.update(labels)
    B,L=c.branch,c.label
    def S(src,key): c.move(src,M(4,SAFE[key]))
    def G(key,dst):c.move(M(4,SAFE[key]),dst)

    L('p1b_image_hotspot_join')
    # P0j-b3 has already checked the ENTIRE image (and mask) and published
    # its Chip descriptor into the original 36-byte local frame at A4+0.
    # Resolve the ORIGINAL bank again for metadata, never infer hotspot
    # from the staged Chip pixels (the stage deliberately excludes it).
    G('bank',D(3))
    c.move(A(4),D(0));c.imm('add',SCRATCH,D(0))
    c.move(D(0),A(1))
    B(1,'explicit_bank_lookup_entry')
    c.tst(D(3));B(7,'draw_reject')       # fail-closed, not no-op
    c.move(M(4,SCRATCH),D(0))
    c.tst(D(0));B(7,'draw_reject')
    c.move(D(0),A(0))
    # AGBO v1 header: image count U16 at payload+8, directory starts +32.
    c.move(I(0),D(5))
    c.move(M(0,8),D(5),'w')
    c.imm('cmp',1,D(5));B(5,'draw_reject')
    c.imm('cmp',MAX_IMAGES,D(5));B(2,'draw_reject')
    c.move(A(0),D(0))
    c.imm('add',32,D(0));B(5,'draw_reject')
    c.move(D(0),A(0))
    L('p1b_find_image')
    c.move(I(0),D(0))
    c.move(M(0,0),D(0),'w')
    G('image',D(1))
    c.alu('cmp',D(1),0)
    B(7,'p1b_image_found')
    c.move(A(0),D(0))
    c.imm('add',ENTRY_BYTES,D(0));B(5,'draw_reject')
    c.move(D(0),A(0))
    c.quick(1,D(5),sub=True)
    B(6,'p1b_find_image')
    B(0,'draw_reject')     # checked P0 image resolver said found: refuse drift
    L('p1b_image_found')
    # The stand-alone P1b helper consumes A0 -> verified 40B AGBO entry,
    # A3 -> the original checked logical screen width/height pair.
    c.move(A(4),D(0))
    c.imm('add',SAFE['screen_w'],D(0))
    c.move(D(0),A(3))
    G('x',D(1));G('y',D(4))
    B(1,'p1b_hotspot_origin_entry')
    G('saved_a3',A(3))  # preserve AMOS A3 on all outcomes
    c.tst(D(3));B(7,'p1b_fully_clipped')
    # Only the local Safe painter coordinates change; the 64 Bob records
    # and P1a numeric X/Y getter values retain the logical anchor.
    S(D(1),'x');S(D(4),'y')
    B(0,'draw_live_image_resolved')
    L('p1b_fully_clipped')
    S(I(1),'result')     # valid offscreen Bob is successful no-op: no DMA
    B(0,'draw_reject')

    L('p1b_hotspot_origin_entry')
    c.raw(hotspot.hex())
    emitted=c.out()
    native=bytearray(emitted)
    dest=c.labels['p1b_image_hotspot_join']
    displacement=dest-(patch+2)
    if not -32768<=displacement<=32767 or displacement==0:
        raise ValueError('P1b Safe join is beyond signed PC16')
    if native[patch:patch+2]!=b'\x60\x00':
        raise ValueError('Original BRA.W at pinned source has changed')
    native[patch+2:patch+4]=pack('>h',displacement)
    out=bytes(native)
    changed=[i for i in range(len(old)) if out[i]!=old[i]]
    if (changed!=[patch+2,patch+3] and changed not in ([patch+2],[patch+3])):
        raise ValueError(('P1b changed unapproved P0 bytes',changed[:16]))
    if (len(out)>=32766 or len(out)&1 or
            out[:patch+2]!=old[:patch+2] or
            out[patch+4:len(old)]!=old[patch+4:]):
        raise ValueError('P1b native prefix/PC16/size integrity failed')
    c.labels['p1b_source_patch_site']=patch
    c.labels['p1b_native_base_len']=len(old)
    c.labels['p1b_join_disp']=displacement
    return out,c.labels


if __name__=='__main__':
    code,labels=emit_p1b_hotspot_draw()
    print('M19 P1b Safe Blitter HOTSPOT JOIN native MC68020',len(code),
        sha256(code).hexdigest(),'old',labels['p1b_native_base_len'],
        'patched',labels['p1b_source_patch_site'],
        'join',labels['p1b_image_hotspot_join'],
        'hot',labels['p1b_hotspot_origin_entry'])
