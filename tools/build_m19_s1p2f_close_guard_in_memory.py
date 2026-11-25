#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Reassemble a source-only P1i Close/End guard. No installable output."""
import argparse
from hashlib import sha256
from pathlib import Path
import shutil
from struct import unpack_from
import tempfile
from active_library import S1P1I_SHA, P2DL2B_SHA, frozen_p2d
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
WAIT='M19_UNIT142_R83_TARGET_WAIT_MC68020.s'
END='M19_UNIT142_R83_TARGET_BRA_WAIT_MC68020.s'
PATCHES=((0x9d4,bytes.fromhex('6100000e6000ff46')),
         (0x9dc,bytes.fromhex('610000066000f808')))

def build_s1p2f(vasm):
    vasm=Path(vasm).resolve()
    active=(ROOT/'dist/AMOSPro_AGA.Lib').read_bytes()
    good=(ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    assert sha256(active).hexdigest()==S1P1I_SHA
    assert sha256(good).hexdigest()==P2DL2B_SHA
    parent,_=build_s1p1i(vasm)
    assert parent==active
    tok,old,title=unpack_ap20(parent)
    assert len(old)==208 and old[:203]==unpack_ap20(good)[1]
    prior=old[UNIT]
    for offset,expected in PATCHES:
        assert prior[offset:offset+8]==expected,hex(offset)
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
            shutil.copyfile(SRC/name,folder/name)
        with master.open('a',encoding='ascii') as f:
            f.write('\n    include "'+GUARD+'"\n')
        new_image=assemble(vasm,folder)
    nt,np,ntitle=unpack_ap20(new_image)
    assert (nt,ntitle,len(np))==(bt,btitle,len(bp))
    assert all(a==b for i,(a,b) in enumerate(zip(np,bp)) if i!=UNIT)
    new=np[UNIT]
    assert len(prior)<len(new)<=MAX_UNIT_BYTES and len(new)%2==0
    assert new[-16:]==bytes(16)
    restored=bytearray(new[:len(prior)])
    targets=[]
    for offset,original in PATCHES:
        assert new[offset:offset+2]==b'\x60\xff' and new[offset+6:offset+8]==b'\x4e\x71'
        target=offset+2+unpack_from('>i',new,offset+2)[0]
        assert len(prior)<=target<len(new)-16 and target%2==0
        targets.append(target)
        restored[offset:offset+8]=original
    assert targets[0]!=targets[1] and bytes(restored)==prior
    parts=list(old)
    parts[UNIT]=new
    assert pc16_displacements(parts)==pc16_displacements(old)
    candidate_title=title.replace(b'S1-P1i',b'S1-P2f')
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
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--vasm',type=Path,required=True)
    _,info=build_s1p2f(cli.parse_args().vasm)
    print('S1P2F_CLOSE_END_SOURCE_IN_MEMORY',info,flush=True)
