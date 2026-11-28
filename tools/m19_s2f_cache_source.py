#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Source-only P2a assembly. Keep S2d/e source and shared conversion tail exact."""
import argparse,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
S2=ROOT/'src/native/m19_s2'
PREP='M19_S2D_EXT_PREPARE_MC68020.s'
RAW='M19_S2F_PREPARE_PLANES_MC68020.s'
CACHE='M19_S2F_CACHE_MC68020.s'
KERNEL='M19_S2F_CLIP_KERNEL_MC68020.s'
ATTACH='M19_S2D_EXT_ATTACH_V39_MC68020.s'
VALIDATE='M19_S1P1C_AGSP_VALIDATE_MC68020.s'
def once(source,old,new):
    assert source.count(old)==1,old
    return source.replace(old,new,1)
def transform(source):
    source=once(source,'AGSP_S2D_PREPARE_EXT:\n',
                '    include "'+RAW+'"\n\nAGSP_S2D_PREPARE_EXT:\n')
    marker='    ; A standard BitMap descriptor, initialized by graphics.library.\n'
    return once(source,marker,'s2d_ext_planes_ready:\n'+marker)
def build(vasm):
    with tempfile.TemporaryDirectory(prefix='s2f_cache_') as td:
        work=Path(td)
        for name in (RAW,CACHE,KERNEL,ATTACH):
            shutil.copyfile(S2/name,work/name)
        shutil.copyfile(ROOT/'src/native/m19_s1'/VALIDATE,work/VALIDATE)
        (work/PREP).write_text(transform((S2/PREP).read_text(encoding='ascii')),encoding='ascii')
        master=work/'s2f_cache.s'
        master.write_text(
            '    bra.w AGSP_S2F_CACHE_CREATE\n'
            '    bra.w AGSP_S2F_CACHE_RENDER\n'
            '    bra.w AGSP_S2F_CACHE_FREE\n'
            '    bra.w AGSP_S2F_CACHE_CHECK\n'
            '    bra.w AGSP_S2F_PREPARE_PLANES\n'
            '    bra.w AGSP_S2D_PREPARE_EXT\n'
            +''.join('    include "'+name+'"\n' for name in (CACHE,KERNEL,PREP)),encoding='ascii')
        out=work/'cache.bin'
        subprocess.run([str(Path(vasm).resolve()),'-Fbin','-m68020','-no-opt','-quiet',
                        '-o',str(out),str(master)],cwd=work,check=True)
        return out.read_bytes()
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    data=build(a.vasm)
    assert data==build(a.vasm)
    with a.output.open('xb') as f:f.write(data)
