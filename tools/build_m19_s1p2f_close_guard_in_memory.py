#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Reassemble a source-only P1i Close/End guard. No installable output."""
import argparse
from hashlib import sha256
from pathlib import Path
import shutil
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

def build_s1p2f(vasm, reclaim=False, persistent=False, probe=False):
    assert not persistent or reclaim
    assert not probe or persistent
    vasm=Path(vasm).resolve()
    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert sha256(active).hexdigest() in (S1P1I_SHA,S1P2I_SHA,S1P2J_SHA,S1P2K_SHA,S1P2LB_SHA,S1P2LC_SHA,S1P2M_SHA,S2A_SHA,S2B_SHA,S2R_SHA, S2C_SHA, S2CD_SHA, S2CE_SHA)
    assert sha256(good).hexdigest()==P2DL2B_SHA
    parent,_=build_s1p1i(vasm)
    assert parent==(active if sha256(active).hexdigest()==S1P1I_SHA else frozen_s1p1i(active,good))
    tok,old,title=unpack_ap20(parent)
    assert len(old)==208 and old[:203]==unpack_ap20(good)[1]
    prior=old[UNIT]
    patches=PATCHES+RECLAIM_PATCHES if reclaim else PATCHES
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
        for name in (GUARD,RETIRE):
            origin='M19_S1P2J_RETIRE_MC68020.s' if probe and name==RETIRE else name
            shutil.copyfile(SRC/origin,folder/name)
        with master.open('a',encoding='ascii') as f:
            f.write('\n    include "'+GUARD+'"\n')
        if reclaim:
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
            origin='M19_S1P2J_RECLAIM_MC68020.s' if probe else RECLAIM
            shutil.copyfile(SRC/origin,folder/RECLAIM)
            replace_once(folder/GUARD,'p2f_root:\n',
                         '    include "'+RECLAIM+'"\np2f_root:\n')
        if persistent:
            glue='M19_S1P2I_CLOSE_ROOT_MC68020.s'
            shutil.copyfile(SRC/glue,folder/glue)
            g=folder/GUARD
            s=g.read_text(encoding='ascii')
            anchor_text='    lea p2f_root(pc),a3\n    move.l (a3),d0\n    beq.w p2f_allow\n'
            new=('    movea.l p2f_root(pc),a3\n    move.l a3,d0\n    beq.w p2f_allow\n'
                 '    movea.l $0004.w,a6\n    suba.l a1,a1\n    jsr -294(a6)\n'
                 '    tst.l d0\n    beq.w p2f_deny\n'
                 '    cmp.l 16(a3),d0\n    bne.w p2f_deny\n'
                 '    cmp.l -16(a3),d0\n    bne.w p2f_deny\n'
                 '    move.l a5,d0\n    cmp.l 4(a3),d0\n    bne.w p2f_deny\n'
                 '    move.l a2,d0\n    beq.w p2f_deny\n'
                 '    cmp.l 8(a3),d0\n    bne.w p2f_deny\n'
                 '    move.l (a2),d0\n    beq.w p2f_deny\n'
                 '    cmp.l 12(a3),d0\n    bne.w p2f_deny\n'
                 '    move.l (a3),d0\n    beq.w p2f_deny\n')
            assert s.count(anchor_text)==1
            s=s.replace(anchor_text,new)
            anchor_text='p2f_root:\n    dcb.b 16,0\n'
            new='    include "'+glue+'"\np2f_root:\n    dc.l 0,$41475349,$00010010,0\n'
            assert s.count(anchor_text)==1
            g.write_text(s.replace(anchor_text,new),encoding='ascii')
            g=folder/RECLAIM
            replace_once(g,'    lea p2f_root(pc),a3\n    tst.l (a3)\n',
                '    movea.l p2f_root(pc),a3\n    move.l a3,d0\n')
            replace_once(g,'    bsr.w AGSP_P2G_RECLAIM\n    ; If pending',
                '    bsr.w AGSP_P2G_RECLAIM\n    bsr.w p2i_close_leave\n    ; If pending')
        new_image=assemble(vasm,folder)
    nt,np,ntitle=unpack_ap20(new_image)
    assert (nt,ntitle,len(np))==(bt,btitle,len(bp))
    assert all(a==b for i,(a,b) in enumerate(zip(np,bp)) if i!=UNIT)
    new=np[UNIT]
    assert len(prior)<len(new)<=MAX_UNIT_BYTES and len(new)%2==0
    assert new[-16:]==(bytes.fromhex('00000000414753490001001000000000') if persistent else bytes(16))
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
    candidate_title=title.replace(b'S1-P1i',b'S1-P2j' if probe else (b'S1-P2i' if persistent else (b'S1-P2g' if reclaim else b'S1-P2f')))
    assert candidate_title!=title
    candidate=repack_ap20(parent,tok,parts,candidate_title)
    assert unpack_ap20(candidate)==(tok,parts,candidate_title)
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert [i for i,(a,b) in enumerate(zip(parts,old)) if a!=b]==[UNIT]
    assert (ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()==active
    assert (ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()==good
    if not reclaim:
        assert sha256(candidate).hexdigest()==P2F_SHA, 'P2f source reconstruction drift'
    return candidate,dict(sha256=sha256(candidate).hexdigest(),bytes=len(candidate),
        unit142=len(new),root=len(new)-16,targets=targets,commands=102,entries=208,
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm',type=Path,required=True)
    cli.add_argument('--reclaim',action='store_true')
    args=cli.parse_args()
    _,info=build_s1p2f(args.vasm,reclaim=args.reclaim)
    print('S1P2G_RECLAIM_SOURCE_IN_MEMORY' if args.reclaim else 'S1P2F_CLOSE_END_SOURCE_IN_MEMORY',info,flush=True)
