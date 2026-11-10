#!/usr/bin/env python3
"""M4b v0.0.7 R6A — audited allocation foundation, no Swap/Back Fill yet.

R6A intentionally validates only:
- corrected shared state layout (+28 depth, +32 DBState*)
- A3 preservation
- real two-ScreenBuffer allocation
- explicit/RESET/END cleanup
- Open/Close and allocation lifecycle

Aga Swap returns 0 and Aga Back Fill is a no-op in this candidate.
"""
from pathlib import Path
import hashlib
import struct

from audit_ap20 import inspect, parse

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist" / "experimental" / "AMOSPro_AGA_M4b_v0.0.6_R4.Lib"
DEST = ROOT / "dist" / "experimental" / "AMOSPro_AGA_M4b_v0.0.7_R6A.Lib"

BASE_SHA = "1f982aea0ffb29112a1a4c8b28d71810bf0e8dad2391da3c95dd6902ca9a2da1"
R6A_SHA = "cce0104e1cecf6842de008b58df0533e126cf6b1402f1bedfdc1a45ee88cf784"

def w(n):
    return struct.pack(">H", n & 0xffff)

def l(n):
    return struct.pack(">I", n & 0xffffffff)

class A:
    def __init__(self):
        self.b=bytearray(); self.labels={}; self.fix=[]
    def e(self,h):
        self.b += bytes.fromhex(h.replace(" ",""))
    def label(self,n):
        self.labels[n]=len(self.b)
    def br(self,op,label):
        pos=len(self.b)
        self.b += w(op)+b"\0\0"
        self.fix.append((pos+2,label))
    def out(self):
        for ext,label in self.fix:
            struct.pack_into(">h",self.b,ext,self.labels[label]-ext)
        return bytes(self.b)

def cleanup():
    a=A()
    # Statement cleanup: preserve A3 and all ordinary AMOS registers.
    a.e("48e7fffe")
    a.e("246d01c8")              # A2 = extension state
    a.e("286a0020")              # A4 = DBState* at +32
    a.e("200c4a80"); a.br(0x6700,"close_screen")

    a.e("2c6a0008")              # A6 = GfxBase
    a.e("200e4a80"); a.br(0x6700,"skip_waitblit")
    a.e("4eaeff1c")              # WaitBlit()
    a.label("skip_waitblit")

    a.e("2052")                  # A0 = Screen*
    a.e("20084a80"); a.br(0x6700,"free_vec")
    a.e("2c6a0004")              # A6 = IntuitionBase

    a.e("226c0004")              # A1 = sb1
    a.e("20094a80"); a.br(0x6700,"skip_sb1")
    a.e("4eaefcfa")              # FreeScreenBuffer(screen,sb1)
    a.label("skip_sb1")

    a.e("2254")                  # A1 = sb0
    a.e("20094a80"); a.br(0x6700,"free_vec")
    a.e("2052")
    a.e("4eaefcfa")              # FreeScreenBuffer(screen,sb0)

    a.label("free_vec")
    a.e("224c")                  # A1 = DBState*
    a.e("2c780004")              # A6 = ExecBase
    a.e("4eaefd4e")              # FreeVec
    a.e("42aa0020")              # state+32 = NULL

    a.label("close_screen")
    a.e("4a92"); a.br(0x6700,"close_gfx")
    a.e("2052")
    a.e("2c6a0004")
    a.e("4eaeffbe")              # CloseScreen
    a.e("4292")

    a.label("close_gfx")
    a.e("226a0008")
    a.e("20094a80"); a.br(0x6700,"close_intui")
    a.e("2c7800044eaefe62")      # CloseLibrary(GfxBase)
    a.e("42aa0008")

    a.label("close_intui")
    a.e("226a0004")
    a.e("20094a80"); a.br(0x6700,"clear_tail")
    a.e("2c7800044eaefe62")      # CloseLibrary(IntuitionBase)
    a.e("42aa0004")

    a.label("clear_tail")
    # width,height,colors,modeID,depth (+12..+28)
    a.e("41ea000c7004429851c8fffc")
    a.e("4cdf7fff4e75")          # restore including A3
    return a.out()

def double_buffer():
    a=A()
    # Function result is D3: preserve A3, deliberately do not restore D3.
    a.e("48e7effe")
    a.e("7600")                  # failure by default
    a.e("246d01c8")
    a.e("4a92"); a.br(0x6700,"done")

    a.e("286a0020")              # A4 = DBState* at +32, never depth +28
    a.e("200c4a80"); a.br(0x6600,"already")

    a.e("7010")
    a.e("223c00010001")          # MEMF_PUBLIC|MEMF_CLEAR
    a.e("2c780004")
    a.e("4eaefd54")              # AllocVec(16,...)
    a.e("4a80"); a.br(0x6700,"done")
    a.e("2840")                  # A4 private until fully initialized

    a.e("205293c97001")
    a.e("2c6a0004")
    a.e("4eaefd00")              # AllocScreenBuffer(...,SB_SCREEN_BITMAP)
    a.e("4a80"); a.br(0x6700,"fail_vec")
    a.e("2880")                  # DBState+0 = sb0

    a.e("205293c97002")
    a.e("2c6a0004")
    a.e("4eaefd00")              # AllocScreenBuffer(...,SB_COPY_BITMAP)
    a.e("4a80"); a.br(0x6700,"fail_sb0")
    a.e("29400004")              # DBState+4 = sb1

    # +8/+12 remain zero from MEMF_CLEAR. Publish only after both allocations.
    a.e("254c0020")              # state+32 = A4
    a.label("already")
    a.e("7601")
    a.br(0x6000,"done")

    a.label("fail_sb0")
    a.e("20522254")
    a.e("2c6a0004")
    a.e("4eaefcfa")

    a.label("fail_vec")
    a.e("224c2c7800044eaefd4e")

    a.label("done")
    a.e("4cdf7ff774004e75")
    return a.out()

def swap_stub():
    return bytes.fromhex("760074004e75")

def backfill_stub():
    return bytes.fromhex("4e75")

def build():
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA
    base=parse(raw)
    assert list(base.jumps)==[94,2,8,8,48,167,193,75,91,15,75,57,56,0]

    seg=[]
    p=0
    for n in base.jumps:
        seg.append(base.code[p:p+2*n])
        p += 2*n
    assert p == len(base.code)

    cl=cleanup()
    init=bytearray(seg[0][:56])
    state_start=56+len(cl)
    struct.pack_into(">h",init,12,state_start-12)
    struct.pack_into(">h",init,32,state_start-32)
    cold=bytes(init)+cl+b"\0"*36

    assert seg[8][-4:] == b"GetP"
    assert seg[10][-4:] == b"GetP"
    assert seg[11][-4:] == b"GetP"

    seg[0]=cold
    seg[8]=cl+b"GetP"
    seg[10]=double_buffer()+b"GetP"
    seg[11]=swap_stub()+b"GetP"
    seg[12]=backfill_stub()

    jumps=[len(s)//2 for s in seg]
    assert jumps == [136,2,8,8,48,167,193,75,92,15,71,5,1,0]
    code=b"".join(seg)

    title=b"AMOSPro AGA M4b R6A experimental 0.0.7\0$VER: AMOSPro_AGA 0.0.7\0"
    if len(title)&1:
        title += b"\0"

    off,nt,_,_=base.lengths
    header=(l(off)+l(nt)+l(len(code))+l(len(title))+b"\0\0AP20"
            + b"".join(w(v) for v in jumps))
    payload=bytearray(header+base.tokens+code+title+b"\0\0")
    while len(payload)&3:
        payload += b"\0"
    n=len(payload)//4
    out=raw[:20]+l(n)+raw[24:28]+l(n)+payload+raw[-4:]

    parsed=parse(out)
    assert inspect(parsed)["issues"] == []
    assert len(out) == 2004
    assert hashlib.sha256(out).hexdigest() == R6A_SHA
    return out

if __name__ == "__main__":
    DEST.write_bytes(build())
    print("Generated",DEST)
    print("SHA256",R6A_SHA)
