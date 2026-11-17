#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""One-shot read-only verified B7 delta to canonical Git blob, not an artefact.

Does NOT create a .Lib, file, ZIP, release or commit. Pure stdout XOR
difference against the already canonical dist Lib. The receiver reconstructs
and SHA-verifies the *single* authorized dist/AMOSPro_AGA.Lib Git blob.
Remove this transport after canonical delivery; never run as a release.
"""
from __future__ import annotations
import base64
import hashlib
from pathlib import Path
import sys
sys.path.insert(0,"tools")
from build_m19_p0j_end_lifecycle_in_memory import build

BASE_SHA="34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56"
TARGET_SHA="f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b"
old=Path("dist/AMOSPro_AGA.Lib").read_bytes()
new,meta=build()
assert len(old)==96908 and hashlib.sha256(old).hexdigest()==BASE_SHA
assert len(new)==102072 and hashlib.sha256(new).hexdigest()==TARGET_SHA
assert meta["public_commands"]==86 and meta["ap20_entries"]==181
assert meta["native_groups"]==[142,153,156,177]
assert meta["pc16_max"]==28600
git_sha=hashlib.sha1(b"blob "+str(len(new)).encode()+b"\0"+new).hexdigest()
print("B7_DELTA_META|"+BASE_SHA+"|"+TARGET_SHA+"|"+str(len(new))+"|"+git_sha,flush=True)
count=0
for start in range(0,len(new),3072):
    block=new[start:start+3072]
    diff=bytes(b^(old[start+i] if start+i<len(old) else 0) for i,b in enumerate(block))
    if any(diff):
        print("B7_DELTA|"+str(start)+"|"+base64.b64encode(diff).decode("ascii"),flush=True)
        count+=1
print("B7_DELTA_END|"+str(count)+"|"+git_sha,flush=True)
