#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Assemble mixed v5 registry with the previously qualified attached source.

The v5 receipt has the legacy 44-byte prefix, type +44, and five immutable
snapshots +48..64. No second mutable state. Produce temporary source variants
only; preserve P0c/P0d standalone sources and all historical builders.
"""
import argparse,re,shutil,subprocess
from pathlib import Path
from hashlib import sha256
from active_library import S2R_SHA
from build_m19_s2r_in_memory import ROOT,protected
from verify_m19_s2r_delivery import verify_library

S2=ROOT/'src/native/m19_s2'
NAMES=('M19_S2C_PERSIST_ROOT_MC68020.s','M19_S2C_REGISTRY_MC68020.s',
       'M19_S2C_RETIRE_MIXED_MC68020.s','M19_S2C_ALLOCATE_MC68020.s')
OFFSETS={16:48,20:52,24:56,28:60,32:64,36:68,40:40}

def prepare_lifecycle(folder):
    life=(S2/'M19_S2C_ATTACHED_LIFECYCLE_MC68020.s').read_text(encoding='ascii')
    frame=(S2/'M19_S2C_ATTACHED_FRAME_MC68020.s').read_text(encoding='ascii')
    # All a3 references in these files refer to the pinned receipt;
    # perform one simultaneous substitution, never cascading offsets.
    pattern=r'\b(16|20|24|28|32|36|40)\(a3\)'
    seen={int(x) for x in re.findall(pattern,life)}
    assert seen==set(OFFSETS)
    life=re.sub(pattern,lambda m:str(OFFSETS[int(m[1])])+'(a3)',life)
    assert life.count('    moveq #43,d0')==1
    life=life.replace('    moveq #43,d0','    moveq #71,d0')
    anchor='    tst.l 68(a3)\n'
    assert life.count(anchor)==1
    life=life.replace(anchor,'    cmpi.l #4,44(a3)\n    bne.w s2c_l_no\n'+anchor)
    anchor='    move.w d0,28(a4)\n'
    assert frame.count(anchor)==1 and not re.search(pattern,frame)
    frame=frame.replace(anchor,anchor+'    move.l d0,36(a3)\n')
    life=life.replace('include "M19_S2C_ATTACHED_FRAME_MC68020.s"',
                      'include "s2c_v5_frame.s"')
    (folder/'s2c_v5_lifecycle.s').write_text(life,encoding='ascii')
    (folder/'s2c_v5_frame.s').write_text(frame,encoding='ascii')

def build(vasm,folder):
    before=protected()
    assert sha256(before[0]).hexdigest()==S2R_SHA
    verify_library(before[0],before[1])
    for name in NAMES:shutil.copyfile(S2/name,folder/name)
    prepare_lifecycle(folder)
    labels=('s2b_p2h_enter','s2b_p2h_leave','AGSP_S2B_SCAN','AGSP_S2B_PICK',
            'AGSP_S2B_INSERT','AGSP_S2B_ACQUIRE','AGSP_S2B_DRAIN','AGSP_S2B_PALETTE_MASK',
            'AGSP_S2C_INSERT_ATTACHED','AGSP_S2C_ACQUIRE','AGSP_S2C_SHOW',
            'AGSP_S2C_MOVE','AGSP_S2C_CHANGE')
    master=folder/'s2c_v5_master.s'
    master.write_text('; AGA_NATIVE_MIN_CPU: MC68020\n' +
        ''.join('    bra.w '+x+'\n' for x in labels) +
        ''.join('    include "'+x+'"\n' for x in NAMES+('s2c_v5_lifecycle.s',)),
        encoding='ascii')
    out=folder/'s2c_v5.bin'
    subprocess.run([str(vasm.resolve()),'-I',str(folder),'-Fbin','-m68020','-no-opt',
                    '-quiet','-o',str(out),str(master)],cwd=folder,check=True,timeout=120)
    raw=out.read_bytes()
    assert all(raw[i:i+2]==b'\x60\x00' for i in range(0,4*len(labels),4))
    assert protected()==before
    print('S2C_V5_COMPONENT_BUILT',len(raw),sha256(raw).hexdigest(),flush=True)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path);p.add_argument('--temp',required=True,type=Path)
    a=p.parse_args();build(a.vasm,a.temp.resolve())
