#!/usr/bin/env python3
"""Deterministic M3a binary generator, no native assembler required.

Derives the AP20 HUNK from the WinUAE-validated 365 AGA M2 binary.
The new self-contained routine is documented in src/M3_DEMO_68020.s.
The machine-code instructions are encoded directly in the DEMO_HEX.
No 68k emulator/compiler test is performed by this script.
"""
from pathlib import Path
import hashlib
import struct

BASE = Path(__file__).resolve().parents[1]
M2_PATH = BASE / 'archive' / 'AMOSPro_AGA_v0.0.2_R1_M2_OK.Lib'
OUT_PATH = BASE / 'dist' / 'experimental' / 'AMOSPro_AGA_M3a.Lib'
SHA_M2 = '69ace1d90a39a19cf47105fce8ef14fa44f7c6cca98d0a068f0d9f80abb21cfc'
SHA_M3 = 'ea2c3d970569e870952f843b96264a27bce79a2dc337115d738e4e6d3e6ee2aa'
DEMO_HEX = '''
48e7cffe76002c780004082e000101296700010c43fa011070274eaefdd84a80
670000fc28402c78000443fa010c70274eaefdd84a80670000dc2a40102d00ec
0200000c0c00000c660000c04fefffd8224f22fc8000002322fc0000014022fc
8000002422fc0000010022fc8000002522fc0000000822fc8000003222fc0002
1000700022c022c091c8224f2c4c4eaefd9c4fef00284a806700007026407c00
20062206e1894841243c000000ff9486e18a4842263c3000000041eb002c2c4d
4eaefcac200643eb00544eaefeaa70002206243c0000013f260643eb00544eae
fece52860c86000001006600ffb43e3c00962c4d4eaefef251cffff8204b2c4c
4eaeffbe760160000002224d2c7800044eaefe62224c2c7800044eaefe624cdf
7ff374004e75696e74756974696f6e2e6c696272617279006772617068696373
2e6c6962726172790000
'''

def u16(n): return struct.pack('>H',n&0xFFFF)
def u32(n): return struct.pack('>I',n&0xFFFFFFFF)

def build():
    m2=M2_PATH.read_bytes()
    assert len(m2)==340 and hashlib.sha256(m2).hexdigest()==SHA_M2
    p=m2[32:-4]
    assert struct.unpack_from('>4I',p)==(14,44,170,52)
    old_toks=p[36:80]; old_lib=p[80:250]
    demo=bytes.fromhex(DEMO_HEX)
    assert len(demo)==330 and demo[:4]==bytes.fromhex('48e7cffe')
    assert demo[-18:]==b'graphics.library\x00\x00'
    # AMOS token: L_Nul(1), L_FnAgaDemo(5), "aga demo" with final
    # character bit 7 set, integer result type "0", entry terminator 0xff.
    new_token=b'\x00\x01\x00\x05aga dem\xEF0\xFF'
    toks=old_toks[:-6]+new_token+b'\0'*6
    assert len(toks)==58
    lib=old_lib+b'GetP'+demo
    assert len(lib)==504 and lib[:170]==old_lib
    jumps=[21,2,8,8,48,165,0,0]
    assert sum(jumps)*2==len(lib)
    title=b'AMOSPro AGA demo V 0.0.3\x00$VER: AMOSPro_AGA 0.0.3\x00'
    if len(title)%2: title+=b'\0'
    assert len(title)==50
    data=u32(16)+u32(len(toks))+u32(len(lib))+u32(len(title))+b'\0\0AP20'
    data+=b''.join(u16(j) for j in jumps)+toks+lib+title+b'\0\0'
    data+=b'\0'*((-len(data))%4)
    hunk=m2[:20]+u32(len(data)//4)+m2[24:28]+u32(len(data)//4)+data+m2[-4:]
    assert len(hunk)==688
    assert hashlib.sha256(hunk).hexdigest()==SHA_M3
    return hunk

if __name__=='__main__':
    OUT_PATH.parent.mkdir(parents=True,exist_ok=True)
    OUT_PATH.write_bytes(build())
    print('M3a HUNK regenerated:',OUT_PATH,'688 bytes')
    print('5 static tests: run tools/test_m3_static.py separately')
    print('Native WinUAE test: NOT DONE')
