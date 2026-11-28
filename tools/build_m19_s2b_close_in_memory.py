#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2b Close/End overlay, source-only, no active writes. Derived from P2m builder."""
import argparse
from hashlib import sha256
from pathlib import Path
import shutil
import re
from struct import unpack_from
import tempfile
from active_library import S1P1I_SHA, S1P2I_SHA, S1P2J_SHA, S1P2K_SHA, S1P2LB_SHA, S1P2LC_SHA, S1P2M_SHA, S2A_SHA, S2B_SHA, S2R_SHA, S2C_SHA, S2CD_SHA, S2CE_SHA, P2DL2B_SHA, frozen_p2d, frozen_s1p1i
from ap20_v2_island_dispatch import pc16_displacements
from audit_ap20 import inspect, parse, token_role_issues
from build_m19_s1p1i_l2b_contract_in_memory import build_s1p1i
from build_m19_p2d_l1_safeport_in_memory import (
    BASE, ROOT, OVERLAY as L1_OVERLAY, PATCHES as L1_PATCHES,
    TAIL as L1_TAIL, assemble,
)
from build_m19_p2d_l2b_pattern_in_memory import (
    OVERLAY as L2B_OVERLAY, SOURCE, ANCHOR, ENTRY, TAIL as L2B_TAIL,
    replace_once,
)
from compiler_bridge_v2_probe import MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20

UNIT=142
SRC=ROOT/'src/native/m19_s1'
S2=ROOT/'src/native/m19_s2'
GUARD='M19_S1P2F_CLOSE_GUARD_MC68020.s'
RETIRE='M19_S1P2E_RETIRE_MC68020.s'
RECLAIM='M19_S1P2G_RECLAIM_MC68020.s'
P2F_SHA='fe054ed9a55804ea5427a6b10f749f5d1329b1910520c5aaff722b0f23037279'
RECLAIM_PATCHES=((0x128,bytes.fromhex('4eaeffbe4292')),
                 (0x886,bytes.fromhex('61004a424292')))
WAIT='M19_UNIT142_R83_TARGET_WAIT_MC68020.s'
END='M19_UNIT142_R83_TARGET_BRA_WAIT_MC68020.s'
PATCHES=((0x9d4,bytes.fromhex('6100000e6000ff46')),
         (0x9dc,bytes.fromhex('610000066000f808')))

def once(s,old,new):
    assert s.count(old)==1,('source anchor',old)
    return s.replace(old,new)

def close_registry(s):
    # In UNIT142 only modes 0 (preclose) and 1 (closed reclaim) exist.
    # Keep all structural/extent/receipt checks, remove the impossible
    # public ID/bank selectors. The general source is used by UNIT207.
    s=once(s,'    cmpi.l #4,d2\n    bhi.w s2b_drain_bad','    cmpi.l #1,d2\n    bhi.w s2b_drain_bad')
    a=s.index('    cmpi.l #2,d2\n    bne.s s2b_drain_bank_arg')
    b=s.index('    tst.l 12(a2)',a)
    s=s[:a]+'''    tst.l d2
    bne.s s2b_drain_closed
'''+s[b:]
    a=s.index('    cmpi.l #2,d2\n    bne.s s2b_drain_bank')
    b=s.index('    btst #3,d0',a)
    s=s[:a]+'''    move.l 12(a3),d0
    tst.l d2
    bne.s s2b_drain_closed_flags
'''+s[b:]
    assert 's2b_drain_bank' not in s
    # Close never looks up an ID or consumes the free-slot mask.
    # Preserve the complete three-slot count/identity/extent validation.
    s=once(s,'    move.l d0,d7\n    cmpi.l #64,d7\n    bhi.w s2b_scan_bad\n','')
    s=once(s,'    cmpi.l #3,(a2)\n    bhi.w s2b_scan_bad\n','')
    s=once(s,'    moveq #0,d6          ; matching record\n    moveq #0,d5          ; free slots\n','')
    s=once(s,'    bset d3,d5\n','')
    s=once(s,'    cmp.l d7,d0\n    bne.s s2b_scan_channel\n    move.l a3,d6\ns2b_scan_channel:\n','')
    s=once(s,'    move.l d6,d0\n    move.l d5,d1\n','    moveq #1,d0\n    moveq #0,d1\n')
    s=once(s,'    move.l d1,d3\n    cmpi.l #1,d2','    cmpi.l #1,d2')
    return s

def compact_retire(s):
    # Exact same permitted receipt states as the long compare chain.
    old="""    cmpi.l #4,d2
    beq.s s2b_p2e_validate_gfx
    cmpi.l #5,d2
    beq.s s2b_p2e_validate_gfx
    cmpi.l #7,d2
    beq.s s2b_p2e_validate_gfx
    cmpi.l #13,d2
    beq.s s2b_p2e_validate_gfx
    cmpi.l #15,d2
    bne.w s2b_p2e_bad_flags
"""
    s=once(s,old,"""    cmpi.l #15,d2
    bhi.w s2b_p2e_bad_flags
    move.l #$0000a0b0,d0 ; bits 4,5,7,13,15 only
    btst d2,d0
    beq.w s2b_p2e_bad_flags
""")
    s=once(s,"""    cmp.w (a0),d1
    bne.s s2b_p2m_bad
    addq.w #2,d1
    cmp.w 4(a0),d1
    bne.s s2b_p2m_bad
    addq.w #2,d1
    cmp.w 8(a0),d1
    bne.s s2b_p2m_bad
    addq.w #2,d1
    cmp.w 12(a0),d1
    bne.s s2b_p2m_bad
""","""    moveq #3,d0
s2b_neutral_regs:
    cmp.w (a0),d1
    bne.s s2b_p2m_bad
    addq.w #2,d1
    addq.l #4,a0
    dbra d0,s2b_neutral_regs
    lea -16(a0),a0
""")
    return s

def compact_root(s):
    old="""    tst.l 56(a4)
    bne.s s2b_p2h_unlock
    tst.l 60(a4)
    bne.s s2b_p2h_unlock
    tst.l 64(a4)
    bne.s s2b_p2h_unlock
    tst.l 68(a4)
    bne.s s2b_p2h_unlock
    tst.l 104(a4)
    bne.s s2b_p2h_unlock
"""
    return once(s,old,"""    move.l 56(a4),d0
    or.l 60(a4),d0
    or.l 64(a4),d0
    or.l 68(a4),d0
    or.l 104(a4),d0
    bne.s s2b_p2h_unlock
""")

def relax_local(s):
    # Only branches wholly inside the new Sprite tail. The legacy prefix,
    # four fixed dispatch spans and long branches to old labels stay exact.
    return re.sub(r'(?m)^(\s+b[a-z]+)\.w(\s+(?:s2b_|p2[fgk]_|AGSP_S2B_)[A-Za-z0-9_]+)',r'\1\2',s)

def build_s2b_close(vasm, *, source_observer=None):
    vasm=Path(vasm).resolve()
    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert sha256(active).hexdigest() in (S1P2J_SHA,S1P2K_SHA,S1P2LB_SHA,S1P2LC_SHA,S1P2M_SHA,S2A_SHA,S2B_SHA,S2R_SHA, S2C_SHA, S2CD_SHA, S2CE_SHA)
    assert sha256(good).hexdigest()==P2DL2B_SHA
    # The full editable L2b UNIT142 is reassembled below. The S2a
    # integrated builder separately authenticates and reconstructs UNIT207.
    from verify_m19_s2b_delivery import pre_s2b_library
    parent_active=pre_s2b_library(active,good)
    assert sha256(parent_active).hexdigest()==S2A_SHA
    from verify_m19_s2a_delivery import verify_library
    verify_library(parent_active,good)
    parent=frozen_s1p1i(parent_active,good)
    tok,old,title=unpack_ap20(parent)
    assert len(old)==208 and old[:203]==unpack_ap20(good)[1]
    prior=old[UNIT]
    patches=PATCHES+RECLAIM_PATCHES
    for offset,expected in patches:
        assert prior[offset:offset+len(expected)]==expected, (hex(offset), prior[offset:offset+len(expected)].hex(), expected.hex())
    assert prior[0x5a:0x66]==bytes.fromhex('48e7fffe246d01c860000978')
    assert prior[0x7fa:0x806]==bytes.fromhex('48e7fffe246d01c8600001d0')
    with tempfile.TemporaryDirectory(prefix='aga-s1p2f-') as temp:
        folder=Path(temp)/'source'
        shutil.copytree(BASE,folder)
        for filename,anchor,snippet,_,_ in L1_PATCHES:
            replacement='    include "'+snippet+'"\n'
            if filename.endswith('IFF_LOAD_BODY_MC68020.s'):
                replacement+='    jsr -228(a6)\n'
            replace_once(folder/filename,anchor,replacement)
            shutil.copyfile(L1_OVERLAY/snippet,folder/snippet)
        replace_once(folder/SOURCE,ANCHOR,'    include "'+ENTRY+'"\n')
        for origin,name in ((L1_OVERLAY,L1_TAIL),(L2B_OVERLAY,ENTRY),
                            (L2B_OVERLAY,L2B_TAIL)):
            shutil.copyfile(origin/name,folder/name)
        master=folder/'M19_P2D_UNIT142_EDITABLE.s'
        with master.open('a',encoding='ascii') as f:
            for name in (L1_TAIL,L2B_TAIL):
                f.write('\n    include "'+name+'"\n')
        # Independently reassemble exact L2b UNIT142 before any P2f edit.
        base_image=assemble(vasm,folder)
        bt,bp,btitle=unpack_ap20(base_image)
        assert bp[UNIT]==prior
        ft,fp,ftitle=unpack_ap20(frozen_p2d(good))
        assert bt==ft and btitle==ftitle and len(bp)==len(fp)==203
        assert all(a==b for i,(a,b) in enumerate(zip(bp,fp)) if i!=UNIT)

        # Preserve the two 8-byte dispatch spans and both upstream prologues.
        f=folder/WAIT
        s=f.read_text(encoding='ascii')
        anchor='L_LEGACY_CLOSE_TARGET_001DE:\n'
        assert s.count(anchor)==1
        prefix=s.split(anchor)[0]
        assert s.endswith('    bsr.w L_LEGACY_CLOSE_TARGET_001EE                  ; +$001E6: 61000006\n')
        f.write_text(prefix+anchor+
            '    bra.l p2f_screen_close\n    nop\n'
            'ENTRY_LEGACY_CLOSE_TARGET_001E6:\n',encoding='ascii')
        # The second span crosses the two original include files.
        f=folder/END
        s=f.read_text(encoding='ascii')
        assert s.count('    bra.w ENTRY_LEGACY_CLOSE_CORE_00190+UNIT142_R83_TARGET_WAIT_BRA_DELTA')==1
        f.write_text('    bra.l p2f_program_end\n    nop\n',encoding='ascii')
        for name in ('M19_S2B_CLOSE_GUARD_MC68020.s',
                     'M19_S2B_RETIRE_PAIR_MC68020.s',
                     'M19_S2B_CLOSE_RECLAIM_MC68020.s',
                     'M19_S2B_PERSIST_ROOT_MC68020.s',
                     'M19_S2B_REGISTRY_MC68020.s'):
            shutil.copyfile(S2/name,folder/name)
        p=folder/'M19_S2B_REGISTRY_MC68020.s'
        p.write_text(close_registry(p.read_text(encoding='ascii')),encoding='ascii')
        p=folder/'M19_S2B_PERSIST_ROOT_MC68020.s'
        p.write_text(once(p.read_text(encoding='ascii'),
             '    bra.w s2b_p2h_enter\n    bra.w s2b_p2h_leave\n',''),encoding='ascii')
        p=folder/'M19_S2B_RETIRE_PAIR_MC68020.s'
        p.write_text(compact_retire(p.read_text(encoding='ascii')),encoding='ascii')
        p=folder/'M19_S2B_PERSIST_ROOT_MC68020.s'
        p.write_text(compact_root(p.read_text(encoding='ascii')),encoding='ascii')
        for p in folder.glob('M19_S2B_*.s'):
            p.write_text(relax_local(p.read_text(encoding='ascii')),encoding='ascii')
        with master.open('a',encoding='ascii') as f:
            # VASM pinned source supports Devpac OPT directives. Limit
            # branch/displacement/quick optimizations to this new tail.
            f.write('\n    opt o-,o1+,o2+,o4+,o5+,o8+,o9+,o10+,o11+,o12+\n')
            f.write('    include "M19_S2B_CLOSE_GUARD_MC68020.s"\n')
            f.write('    opt o-\n')
        # Source-only, preserve each legacy six-byte span.
        file=folder/'M19_UNIT142_R83_CLOSE_CLEANUP_MC68020.s'
        old_close=('    jsr -66(a6)                                        ; +$000CE: 4EAEFFBE\n'
                   '    clr.l (a2)                                         ; +$000D2: 4292\n')
        replace_once(file,old_close,'    bra.l p2g_end_close\n')
        file=folder/'M19_UNIT142_R83_TARGET_BSR_52CA_MC68020.s'
        replace_once(file,
            '    bsr.w ENTRY_LEGACY_HELPER_052CA_00000+UNIT142_R83_TARGET_BSR_52CA_DELTA\n',
            '    bra.l p2g_public_close\n')
        file=folder/'M19_UNIT142_R83_TARGET_BODY_MC68020.s'
        replace_once(file,'    clr.l (a2)                                         ; +$00094: 4292\n','')
        new_image=assemble(vasm,folder)
        if source_observer is not None:
            source_observer(folder,new_image)
    nt,np,ntitle=unpack_ap20(new_image)
    assert (nt,ntitle,len(np))==(bt,btitle,len(bp))
    assert all(a==b for i,(a,b) in enumerate(zip(np,bp)) if i!=UNIT)
    new=np[UNIT]
    print(f'S2B_UNIT142 prior={len(prior)} new={len(new)} max={MAX_UNIT_BYTES} free={MAX_UNIT_BYTES-len(new)}', flush=True)
    assert len(prior)<len(new)<=MAX_UNIT_BYTES and len(new)%2==0, (
        'UNIT142 size/alignment', len(prior), len(new), MAX_UNIT_BYTES)
    assert new[-16:]==bytes.fromhex('00000000414753490001001000000000')
    restored=bytearray(new[:len(prior)])
    targets=[]
    for offset,original in patches:
        assert new[offset:offset+2]==b'\x60\xff'
        if len(original)==8:
            assert new[offset+6:offset+8]==b'\x4e\x71'
        target=offset+2+unpack_from('>i',new,offset+2)[0]
        assert len(prior)<=target<len(new)-16 and target%2==0
        targets.append(target)
        restored[offset:offset+len(original)]=original
    assert len(set(targets))==len(targets) and bytes(restored)==prior
    parts=list(old)
    parts[UNIT]=new
    assert pc16_displacements(parts)==pc16_displacements(old)
    candidate_title=title.replace(b'S1-P1i',b'S2b-P1')
    assert candidate_title!=title
    candidate=repack_ap20(parent,tok,parts,candidate_title)
    assert unpack_ap20(candidate)==(tok,parts,candidate_title)
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert [i for i,(a,b) in enumerate(zip(parts,old)) if a!=b]==[UNIT]
    assert (ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()==active
    assert (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()==good
    return candidate,dict(sha256=sha256(candidate).hexdigest(),bytes=len(candidate),
        unit142=len(new),root=len(new)-16,targets=targets,commands=102,entries=208,
        installable=False,runtime_tested=False,compiler_tested=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    _,meta=build_s2b_close(p.parse_args().vasm)
    print('S2B_CLOSE_OVERLAY_BUILT',meta,flush=True)
