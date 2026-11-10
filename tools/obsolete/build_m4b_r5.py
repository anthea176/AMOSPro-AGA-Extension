#!/usr/bin/env python3
"""M4b v0.0.6 R5: safe blocking ChangeScreenBuffer protocol.

R5 keeps the R4 AP20 token table but replaces:
- explicit M4b cleanup: delete the DB MsgPort before FreeVec
- Aga Double Buffer: create/store an Exec MsgPort in DBState +12
- Aga Swap: set dbi_SafeMessage.mn_ReplyPort, retry ChangeScreenBuffer
  until accepted, then WaitPort/GetMsg before returning.

Aga Back Fill is intentionally unchanged and must not be used in the R5
swap-synchronisation validation.
"""
from pathlib import Path
import struct

from audit_ap20 import inspect, parse

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dist" / "experimental" / "AMOSPro_AGA_M4b_v0.0.6_R4.Lib"
DEST = ROOT / "dist" / "experimental" / "AMOSPro_AGA_M4b_v0.0.6_R5.Lib"

def w(n): return struct.pack(">H", n & 0xffff)
def l(n): return struct.pack(">I", n & 0xffffffff)

class A:
    def __init__(self):
        self.b=bytearray(); self.labels={}; self.fix=[]
    def e(self,h):
        self.b += bytes.fromhex(h.replace(" ",""))
    def label(self,n):
        self.labels[n]=len(self.b)
    def br(self,op,label):
        pos=len(self.b); self.b += w(op)+b"\0\0"; self.fix.append((pos+2,label))
    def out(self):
        for ext,label in self.fix:
            struct.pack_into(">h",self.b,ext,self.labels[label]-ext)
        return bytes(self.b)

def cleanup():
    a=A()
    a.e("48e7ffee246d01c8200a4a80"); a.br(0x6700,"exit")
    a.e("266a001c200b4a80"); a.br(0x6700,"close_screen")
    a.e("205220084a80"); a.br(0x6700,"delete_port")
    a.e("226b000420094a80"); a.br(0x6700,"skip_sb1")
    a.e("20522c6a00044eaefcfa")
    a.label("skip_sb1")
    a.e("225320094a80"); a.br(0x6700,"delete_port")
    a.e("20522c6a00044eaefcfa")
    a.label("delete_port")
    a.e("206b000c20084a80"); a.br(0x6700,"free_vec")
    a.e("2c7800044eaefd60")              # DeleteMsgPort -672
    a.label("free_vec")
    a.e("224b2c7800044eaefd4e42aa001c")  # FreeVec -690
    a.label("close_screen")
    a.e("4a92"); a.br(0x6700,"close_gfx")
    a.e("20522c6a00044eaeffbe4292")
    a.label("close_gfx")
    a.e("226a000820094a80"); a.br(0x6700,"close_intui")
    a.e("2c7800044eaefe6242aa0008")
    a.label("close_intui")
    a.e("226a000420094a80"); a.br(0x6700,"clear_tail")
    a.e("2c7800044eaefe6242aa0004")
    a.label("clear_tail")
    a.e("41ea000c7004429851c8fffc")
    a.label("exit")
    a.e("4cdf77ff4e75")
    return a.out()

def double_buffer():
    a=A()
    a.e("48e7efee7600246d01c8200a4a80"); a.br(0x6700,"done")
    a.e("4a92"); a.br(0x6700,"done")
    a.e("266a001c200b4a80"); a.br(0x6600,"already")

    a.e("7010223c000100012c7800044eaefd54")  # AllocVec(16,MEMF_PUBLIC|CLEAR)
    a.e("4a80"); a.br(0x6700,"done")
    a.e("2640")

    a.e("2c7800044eaefd66")              # CreateMsgPort -666
    a.e("4a80"); a.br(0x6700,"fail_vec")
    a.e("2740000c")                     # DBState +12 = port

    a.e("205293c970012c6a00044eaefd00")  # SB_SCREEN_BITMAP
    a.e("4a80"); a.br(0x6700,"fail_port")
    a.e("2680")

    a.e("205293c970022c6a00044eaefd00")  # SB_COPY_BITMAP
    a.e("4a80"); a.br(0x6700,"fail_sb0")
    a.e("27400004254b001c")              # sb1 / publish DBState

    a.label("already")
    a.e("7601"); a.br(0x6000,"done")

    a.label("fail_sb0")
    a.e("205222532c6a00044eaefcfa")      # FreeScreenBuffer(sb0)
    a.label("fail_port")
    a.e("206b000c2c7800044eaefd60")      # DeleteMsgPort
    a.label("fail_vec")
    a.e("224b2c7800044eaefd4e")          # FreeVec

    a.label("done")
    a.e("4cdf77f774004e75")              # preserve D3 result
    return a.out()

def swap_safe():
    a=A()
    a.e("48e7efee7600246d01c8200a4a80"); a.br(0x6700,"done")
    a.e("4a92"); a.br(0x6700,"done")
    a.e("266a001c200b4a80"); a.br(0x6700,"done")
    a.e("202b000c4a80"); a.br(0x6700,"done")  # MsgPort required

    a.e("202b00084a80"); a.br(0x6700,"front0")
    a.e("22537e00"); a.br(0x6000,"have_target")
    a.label("front0")
    a.e("226b00047e01")
    a.label("have_target")
    a.e("20094a80"); a.br(0x6700,"done")

    a.e("2849")                         # A4 = target ScreenBuffer
    a.e("206c000420084a80"); a.br(0x6700,"done") # A0 = sb_DBufInfo
    a.e("202b000c21400016")             # SafeMessage.mn_ReplyPort = port

    a.label("retry")
    a.e("2052224c2c6a00044eaefcf4")      # ChangeScreenBuffer(screen,target)
    a.e("4a80"); a.br(0x6600,"changed")
    a.e("2c6a00084eaefef2")              # WaitTOF only while held off
    a.br(0x6000,"retry")

    a.label("changed")
    a.e("27470008")                     # publish current front index

    a.label("waitmsg")
    a.e("206b000c2c7800044eaefe80")      # WaitPort -384
    a.e("206b000c2c7800044eaefe8c")      # GetMsg -372
    a.e("4a80"); a.br(0x6700,"waitmsg")

    a.e("7601")
    a.label("done")
    a.e("4cdf77f774004e75")
    return a.out()

def build():
    raw=BASE.read_bytes()
    lib=parse(raw)
    d=raw[32:-4]
    off,nt,nc,nz=lib.lengths
    token_start=22+off
    code_start=token_start+nt
    title_start=code_start+nc

    seg=[]; p=0
    for n in lib.jumps:
        seg.append(lib.code[p:p+n*2]); p+=n*2

    seg[8]=cleanup()+b"GetP"
    seg[10]=double_buffer()+b"GetP"
    seg[11]=swap_safe()+b"GetP"

    jumps=[len(s)//2 for s in seg]
    assert all(len(s)%2==0 for s in seg)
    code=b"".join(seg)
    tokens=d[token_start:token_start+nt]
    title=d[title_start:title_start+nz]

    header=l(off)+l(nt)+l(len(code))+l(nz)+b"\0\0AP20"+b"".join(w(x) for x in jumps)
    payload=bytearray(header+tokens+code+title+b"\0\0")
    while len(payload)&3: payload+=b"\0"
    n=len(payload)//4
    out=raw[:20]+l(n)+raw[24:28]+l(n)+payload+raw[-4:]

    parsed=parse(out)
    assert parsed.jumps == (94,2,8,8,48,167,193,75,101,15,90,89,56,0)
    assert inspect(parsed)["issues"] == []
    return out

if __name__ == "__main__":
    out=build()
    DEST.write_bytes(out)
    print("Generated",DEST)
    print("Size",len(out))
    print("First runtime test: tests/M4B_R5_SWAP_STRESS.asc")
