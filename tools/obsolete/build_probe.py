#!/usr/bin/env python3
"""Reproducible M0 AMOS 365 no-op extension HUNK patcher (NOT Genam).
Reference: AMOS 365 AMOSPro_Request.Lib / +Request.s (public domain).
Test fixture only: does not detect AGA or use 68020 instructions.
"""
import base64
import hashlib
import struct
from pathlib import Path

REFERENCE_B64 = '''
AAAD8wAAAAAAAAABAAAAAAAAAAAAAAA5AAAD6QAAADkAAAAOAAAAPgAAAFoA
AAAmAABBUDIwABUAAgAIAAgABgAAAAAAAQAAgP8AAwABcmVxdWVzdCBv7kn/
AAQAAXJlcXVlc3Qgb2bmSf8AAAIAAXJlcXVlc3Qgd+JJ/wAAAAAAALK8QVBl
eGYYSOcAHkH6ABgrSAEcTN94AHACMjwCAE51cP+RyE51/iEAA0dldFBwASBt
//xOqAGQTnVHZXRQcP8gbf/8TqgBkE51R2V0UHAAIG3//E6oAZBOdUFNT1NQ
cm8gUmVxdWVzdGVyIFYgMi4wMAAAJFZFUjogMi4wMAAAAAAAAAPy
'''

def single_replace(data, old, new):
    assert len(old) == len(new) and data.count(old) == 1, repr(old)
    return data.replace(old, new)

def build():
    src = base64.b64decode(REFERENCE_B64)
    git_sha = hashlib.sha1(b'blob ' + str(len(src)).encode() + b'\0' + src).hexdigest()
    assert git_sha == '0d22cf3365e008413a2d56b920294fda3931a9db'
    assert len(src) == 264 and src[:4] == bytes.fromhex('000003f3')
    assert src[24:28] == bytes.fromhex('000003e9') and src[-4:] == bytes.fromhex('000003f2')
    code = src[32:-4]
    assert len(code) == 228 and struct.unpack_from('>4I',code) == (14,62,90,38)
    # 22 byte extension header + 14 byte jump table + 62 byte token table.
    prefix, lib, title = code[:36], code[98:188], code[188:226]
    assert code[226:228] == b'\0\0'
    # New token: AGA PROBE -> old library entry #3 (in-request-on).
    token = (b'\x00\x01\x00\x00\x80\xff' + b'\x00\x03\x00\x01'
             + b'aga prob\xe5I\xff' + b'\0'*6 + b'\0')
    assert len(token) == 28
    lib = single_replace(lib,bytes.fromhex('2b48011c'),bytes.fromhex('2b4801cc'))
    lib = single_replace(lib,bytes.fromhex('7002323c0200'),bytes.fromhex('700d323c0200'))
    lib = single_replace(lib,bytes.fromhex('fe210003'),bytes.fromhex('4e754e71'))
    for arg in (1,255,0):
        lib = single_replace(lib,b'GetP\x70'+bytes([arg]),b'GetP\x4e\x75')
    title = single_replace(title,b'AMOSPro Requester V 2.00',b'AMOSPro AGA probe V 0.01')
    title = single_replace(title,b'$VER: 2.00',b'$VER: 0.01')
    code = bytearray(prefix + token + lib + title + b'\0\0')
    struct.pack_into('>4I',code,0,14,len(token),len(lib),len(title))
    while len(code) % 4:
        code.append(0)
    longs = len(code)//4
    assert longs == 49
    result = src[:20] + struct.pack('>I',longs) + src[24:28] + struct.pack('>I',longs) + code + src[-4:]
    assert len(result) == 232
    assert hashlib.sha256(result).hexdigest() == '5cbb8937b377d39314fafae98eb1030b0ada4bd1b05b828eb0e87ee6cffc28c5'
    return result

if __name__ == '__main__':
    target = Path(__file__).resolve().parent.parent / 'dist' / 'AMOSPro_AGA.Lib'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(build())
    print(f'{target}: {target.stat().st_size} bytes, structural checks OK')
    print('Native WinUAE test: NOT DONE')
