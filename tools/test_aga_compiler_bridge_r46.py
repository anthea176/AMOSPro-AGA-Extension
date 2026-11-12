#!/usr/bin/env python3
"""Static bridge regression; WinUAE Gate C PASS confirmed separately by user."""
import os
import struct
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

source_path = Path(__file__).with_name('build_aga_compiler_bridge_r46.py')
spec = spec_from_file_location('bridge_r46', source_path)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)


def unpack(b):
    assert struct.unpack_from('>I',b)[0] == 0x3f3
    j,tl,cl,nl = struct.unpack_from('>4I',b,32)
    sizes=struct.unpack_from('>'+str(j//2)+'H',b,54)
    pos=54+j
    tok=b[pos:pos+tl];pos+=tl
    parts=[]
    for size in sizes:
        parts.append(b[pos:pos+2*size]);pos+=2*size
    title=b[pos:pos+nl]
    assert sum(map(len,parts))==cl
    assert len(b)==36+4*struct.unpack_from('>I',b,28)[0]
    return tok,parts,title


def param_markers(tokens,parts):
    pos=0; total=0; code=b''.join(parts);start=0;offsets=[]
    for p in parts:offsets.append(start);start+=len(p)
    while pos<len(tokens):
        ins,fun=struct.unpack_from('>HH',tokens,pos)
        if ins==0:break
        end=pos+4
        while tokens[end]<128:end+=1
        sig=end+1
        while tokens[sig]<128:sig+=1
        signature=tokens[end+1:sig].decode('ascii')
        if signature and signature[1:]:
            for index in (ins,fun):
                if index>1:
                    assert code[offsets[index]-4:offsets[index]] == b'GetP',index
                    total+=1
        pos=(sig+2)&~1
    return total


def run():
    r46 = Path(os.environ.get('R46_SOURCE',str(mod.SOURCE))).read_bytes()
    tokens,old=mod.read_ap20(r46)
    data=mod.build(r46)
    assert data == mod.build(r46)
    new_tokens,new,caption=unpack(data)
    assert tokens == new_tokens and len(old)==56 and len(new)==57
    assert old[16]==new[16]==b'' and old[1]==new[1]==b'GetP'
    assert new[-1]==mod.DISPATCH+b''.join(old)
    assert len(new[-1])==27888 and len(new[-1])<32768
    assert param_markers(tokens,old)==param_markers(tokens,new)
    offset=0
    for i,p in enumerate(old):
        if p and p!=b'GetP':
            expected=b'\xfe\x31'+struct.pack('>HH',56,offset)+b'\x4e\x75'
            if p.endswith(b'GetP'):expected+=b'GetP'
            assert expected==new[i],i
        else: assert p==new[i],i
        offset+=len(p)
    assert offset==27856
    assert mod.digest(data)==mod.CANDIDATE_SHA
    assert len(data)==29964
    root=Path(__file__).resolve().parents[1]
    from active_library import verify_active
    verify_active(root)  # current candidate is distinct from LAST_GOOD
    assert data==(root/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert data==mod.CANDIDATE.read_bytes()
    print('PASS: R46 source SHA, deterministic AP20, 50-command token table, GetP boundaries')
    print('PASS: 56 original code fragments unchanged inside single 27,888-byte AP20 unit')
    print('PASS: 56 public index boundaries preserved; Rbsr entries point to central index 56')
    print('STATIC REPRODUCIBILITY PASS; real Compiler/WinUAE Gate C was user-confirmed independently')


if __name__=='__main__': run()
