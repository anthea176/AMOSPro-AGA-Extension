#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""P3a source-only sizing probe; no AP20 or active artifact writes.

Extract the exact P2d Retire/Reclaim implementation and its three shared
helpers, omitting Show/Move/Exchange and their dependencies. The five-entry
test shim keeps the existing CPU harness's +12/+16 ABI. Its first three
entries refuse without touching a receipt. This is NOT yet UNIT142 code.
"""
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
S2=ROOT/'src/native/m19_s2'

def section(source,start,end=None):
    assert source.count(start)==1,(start,source.count(start))
    i=source.index(start)
    if end is None:return source[i:]
    assert source.count(end)==1,(end,source.count(end))
    j=source.index(end)
    assert i<j
    return source[i:j]


def compact_retire(source):
    """Bounded loops replacing only six-pointer unrolled blocks.
    Check the precise original operands before substitution.
    """
    offsets=(4,8,52,56,72,76)
    frees='s2d_r_reclaim_start:\n    move.l #32,24(a3)       ; terminal before any void OS free\n'
    allocs='s2d_r_check_allocs:\n'
    scans='s2d_r_no_refs:\n    move.l d7,-(sp)\n'
    for o in offsets:
        frees+=f"""    move.l {o}(a3),d0
    beq.s s2d_r_free_skip_{o}
    movea.l d0,a2
    clr.l {o}(a3)
    jsr -1032(a6)
s2d_r_free_skip_{o}:
"""
        height='    moveq #1,d0' if o<52 else '    move.l d7,d0'
        allocs+=f"""    move.l {o}(a3),d0
    beq.s s2d_r_skip_alloc_{o}
    movea.l d0,a0
{height}
    bsr.w s2d_r_alloc
    tst.l d0
    beq.w s2d_c_no
s2d_r_skip_alloc_{o}:
"""
        height='    moveq #1,d7' if o<52 else '    move.l (sp),d7'
        scans+=f"""    move.l {o}(a3),d0
    beq.s s2d_r_scan_skip_{o}
    movea.l d0,a0
{height}
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.w s2d_r_scan_no
s2d_r_scan_skip_{o}:
"""
    frees+='    clr.l 80(a3)\n    bra.w s2d_r_done\n'
    allocs+='    ; No aliased ExtSprite or identical stream base across any pair.\n'
    for i,o in enumerate(offsets[1:],1):
        allocs+=f"""    move.l {o}(a3),d0
    beq.w s2d_r_alias_done_{o}
    movea.l d0,a0
"""
        for p in offsets[:i]:
            allocs+=f"""    move.l {p}(a3),d1
    beq.s s2d_r_alias_skip_{o}_{p}
    cmp.l d0,d1
    beq.w s2d_c_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.w s2d_c_no
s2d_r_alias_skip_{o}_{p}:
"""
        allocs+=f's2d_r_alias_done_{o}:\n'
    allocs+='    moveq #1,d0\n    rts\n\n'
    scans+='    moveq #1,d0\n    bra.s s2d_r_scan_return\ns2d_r_scan_no:\n    moveq #0,d0\ns2d_r_scan_return:\n    move.l (sp)+,d7\n    rts\n'
    replacements=(
        (frees,'''s2d_r_reclaim_start:
    move.l #32,24(a3)
    lea s2d_r_offsets(pc),a4
    moveq #5,d2
s2d_r_free_loop:
    moveq #0,d1
    move.b (a4)+,d1
    move.l 0(a3,d1.w),d0
    beq.s s2d_r_free_next
    movea.l d0,a2
    clr.l 0(a3,d1.w)
    jsr -1032(a6)
s2d_r_free_next:
    dbra d2,s2d_r_free_loop
    clr.l 80(a3)
    bra.w s2d_r_done
'''),
        (allocs,'''s2d_r_check_allocs:
    movem.l d2-d3/a4,-(sp)
    lea s2d_r_offsets(pc),a4
    moveq #5,d2
s2d_r_alloc_loop:
    moveq #0,d1
    move.b (a4)+,d1
    move.l 0(a3,d1.w),d0
    beq.s s2d_r_alloc_next
    movea.l d0,a0
    moveq #1,d0
    cmpi.w #8,d1
    bls.s s2d_r_alloc_height
    move.l d7,d0
s2d_r_alloc_height:
    bsr.w s2d_r_alloc
    tst.l d0
    beq.s s2d_r_compact_no
s2d_r_alloc_next:
    dbra d2,s2d_r_alloc_loop
    lea s2d_r_offsets(pc),a4
    moveq #1,d2
s2d_r_alias_outer:
    moveq #0,d1
    move.b 0(a4,d2.w),d1
    move.l 0(a3,d1.w),d0
    beq.s s2d_r_alias_outer_next
    movea.l d0,a0
    moveq #0,d3
s2d_r_alias_inner:
    moveq #0,d1
    move.b 0(a4,d3.w),d1
    move.l 0(a3,d1.w),d1
    beq.s s2d_r_alias_inner_next
    cmp.l d0,d1
    beq.s s2d_r_compact_no
    movea.l d1,a1
    move.l (a0),d1
    cmp.l (a1),d1
    beq.s s2d_r_compact_no
s2d_r_alias_inner_next:
    addq.w #1,d3
    cmp.w d2,d3
    bcs.s s2d_r_alias_inner
s2d_r_alias_outer_next:
    addq.w #1,d2
    cmpi.w #6,d2
    bcs.s s2d_r_alias_outer
    moveq #1,d0
    bra.s s2d_r_compact_return
s2d_r_compact_no:
    moveq #0,d0
s2d_r_compact_return:
    movem.l (sp)+,d2-d3/a4
    rts

'''),
        (scans,'''s2d_r_no_refs:
    movem.l d2/d7/a4,-(sp)
    lea s2d_r_offsets(pc),a4
    moveq #5,d2
s2d_r_scan_loop:
    moveq #0,d1
    move.b (a4)+,d1
    move.l 0(a3,d1.w),d0
    beq.s s2d_r_scan_next
    movea.l d0,a0
    moveq #1,d7
    cmpi.w #8,d1
    bls.s s2d_r_scan_height
    move.l 4(sp),d7
s2d_r_scan_height:
    bsr.w s2d_x_unreferenced
    tst.l d0
    beq.s s2d_r_scan_no
s2d_r_scan_next:
    dbra d2,s2d_r_scan_loop
    moveq #1,d0
    bra.s s2d_r_scan_return
s2d_r_scan_no:
    moveq #0,d0
s2d_r_scan_return:
    movem.l (sp)+,d2/d7/a4
    rts
s2d_r_offsets:
    dc.b 4,8,52,56,72,76
'''))
    for old,new in replacements:
        assert source.count(old)==1,'unexpected source block; refuse compact transform'
        source=source.replace(old,new,1)
    return source

def emit(compact=False):
    read=lambda n:(S2/('M19_S2D_EXT_'+n+'_MC68020.s')).read_text(encoding='ascii')
    retire=section(read('RETIRE'),'AGSP_S2D_EXT_RETIRE:\n',
                   '    include "M19_S2D_EXT_FRAME_MC68020.s"')
    if compact:retire=compact_retire(retire)
    refs=section(read('FRAME'),'s2d_x_unreferenced:\n',
                 '    include "M19_S2D_EXT_HIDDEN_SHOW_MC68020.s"')
    show=read('HIDDEN_SHOW')
    no=section(show,'s2d_c_no:\n','s2d_c_hidden_refs:\n')
    span=section(show,'s2d_c_span:\n')
    return ('; AGA_NATIVE_MIN_CPU: MC68020\n'+
            '    bra.w s2d_c_no\n'*3+
            '    bra.w AGSP_S2D_EXT_RETIRE\n'
            '    bra.w AGSP_S2D_EXT_RECLAIM\n'+retire+refs+no+span)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    p.add_argument('--compact',action='store_true')
    args=p.parse_args()
    out=args.output.resolve()
    assert not out.is_relative_to(ROOT),'probe must be outside repository'
    out.write_text(emit(args.compact),encoding='ascii')
if __name__=='__main__':main()
