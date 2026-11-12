#!/usr/bin/env python3
"""R60 Gate A: real M68000 AGAPIC region draw under two AP20 layouts.

Run new byte-exact V2 dispatcher+new native routine through Unicorn; the
AMOS-main Bnk.GetAdr is independently relocated and mocked by symbolic
identity. Pixels and result are compared to a separate byte-oriented oracle.
No WinUAE/AMOS Gate B/C or real hardware Gate D is claimed.
"""
from __future__ import annotations

import struct

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from amos_link_test_support import relocate
from audit_ap20 import inspect, parse
from build_m18_r60_image_region import API, build
from compiler_bridge_v2_probe import unwrap_native_parts_v2
from compiler_relocation import GETP, unpack_ap20
from m16_agapic import pack_image, parse_payload, unpack_image
from m18_image_region_emit import GETADR_MARKER, emit_image_region
from test_m16_capture import CaptureMachine, NEW_CODE
from test_m16_image_draw_r45 import BANK, ARGS, DB, sample_pixels
from test_m5_generic import AMOS, AR, DR, STACK, STOP


def oracle(background: bytes, image, sx: int, sy: int, width: int,
           height: int, x: int, y: int, screen_w: int, screen_h: int,
           mode: int) -> bytes:
    pixels, mask = unpack_image(image)
    out = bytearray(background)
    for row in range(height):
        dy = y + row
        if not 0 <= dy < screen_h:
            continue
        for col in range(width):
            dx = x + col
            ix = (sy + row) * image.width + sx + col
            if 0 <= dx < screen_w and (mode == 0 or mask[ix]):
                out[dy * screen_w + dx] = pixels[ix]
    return bytes(out)


def run_case(binary: bytes, payload: bytes, *, layout: str = "interpreted",
             depth: int = 4, front: int = 0, flag: int = 0,
             bank: int = 10, sx: int = 0, sy: int = 0, width: int = 19,
             height: int = 11, x: int = 5, y: int = 7, mode: int = 0,
             pending: int = 0, safe_ready: bool = True,
             expect_ok: bool = True) -> int:
    image = parse_payload(payload)
    sw, sh = 64, 42
    assert image.depth == depth
    m = CaptureMachine(binary=binary,layout="interpreted",
                       width=sw,height=sh,depth=depth,front=front,
                       pending=pending,safe_ready=safe_ready)
    m.install_bank(payload)
    m.uc.mem_write(BANK-12,struct.pack(">H",flag))
    _,parts,_ = unpack_ap20(binary)
    assert len(parts) == 61
    assert len(parts[-1]) > 32768, "R60 must validate an above-32K V2 monolith"
    if layout == "interpreted":
        entry = NEW_CODE + sum(map(len, parts[:59]))
    elif layout == "compiled":
        # AMOS Compiler copies the used stub and the shared monolith
        # separately. The V2 bridge must still dispatch correctly.
        mono = 0x1B8000
        entry = 0x1B7000
        m.uc.mem_write(mono, relocate(parts[-1],mono,{60:mono},m.uc))
        m.uc.mem_write(entry,relocate(parts[59],entry,{60:mono},m.uc))
    else:
        raise ValueError(layout)

    before = m.snapshot()
    background = sample_pixels(before,sw,sh,depth,m.stride)
    for idx,reg in enumerate(DR):
        m.uc.reg_write(reg,0x1200+idx)
    for idx,reg in enumerate(AR[:7]):
        m.uc.reg_write(reg,0x40000+idx*256)
    m.uc.reg_write(AR[5],AMOS)
    m.uc.reg_write(AR[3],ARGS)
    for i,arg in enumerate((y,x,height,width,sy,sx,bank)):
        m.put(ARGS+i*4,arg)
    m.uc.reg_write(DR[3],mode & 0xffffffff)
    saved={reg:m.uc.reg_read(reg) for reg in DR+AR[:7]}
    m.uc.reg_write(UC_M68K_REG_SR,0x2000)
    m.uc.reg_write(AR[7],STACK)
    m.put(STACK,STOP)
    try:
        m.uc.emu_start(entry,STOP,count=14_000_000)
    except Exception as exc:
        raise AssertionError(("R60 68000 exception",str(exc),layout,depth,
                              sx,sy,width,height,x,y,mode,bank,
                              hex(m.uc.reg_read(UC_M68K_REG_PC)),
                              list(m.trace),m.main_calls,m.os_calls)) from exc
    assert m.uc.reg_read(UC_M68K_REG_PC)==STOP
    assert m.a(7)==STACK+4, "M68000 return stack corrupt"
    assert m.a(3)==ARGS+28, "seven LONG stack parameters not consumed"
    assert m.d(2)==0, "AP20 result must be integer"
    got=m.d(3)
    assert got in (0,1)
    assert got==int(expect_ok),("result",got,expect_ok,layout,sx,sy,width,height,x,y)
    for reg,initial in saved.items():
        if reg not in (DR[2],DR[3],AR[3]):
            assert m.uc.reg_read(reg)==initial,("damaged ABI register",reg)
    assert [bytes(m.uc.mem_read(a,m.plane_size))
            for a in m.frontplanes]==m.front_before, "front buffer modified"
    assert m.alloc_count==m.free_count==m.reserve_count==m.erase_count==0
    assert m.main_calls == (["Bnk.GetAdr"] if bank>=5 else []),m.main_calls

    if expect_ok:
        expected=oracle(background,image,sx,sy,width,height,x,y,sw,sh,mode)
        after=sample_pixels(m.snapshot(),sw,sh,depth,m.stride)
        assert after==expected,(
            "wrong R60 pixels",layout,depth,front,sx,sy,width,height,x,y,mode,
            next((i for i,(a,b) in enumerate(zip(after,expected))
                  if a!=b),None))
        assert m.get(DB+20)==(pending & ~1)
        assert m.getmsg_calls==int(bool(pending & 1))
    else:
        assert before==m.snapshot(), "invalid region modified back buffer"
        assert m.get(DB+20)==pending
        if not (pending & 1 and not safe_ready):
            assert m.getmsg_calls==0, "preflight invalidity must not consume Safe"
    return 1


def main() -> None:
    binary,meta=build()
    assert binary==build()[0], "R60 not deterministic"
    token_bytes,parts=unwrap_native_parts_v2(binary)
    report=inspect(parse(binary))
    assert not report["issues"]
    assert len(parts)==60
    assert parts[58].endswith(GETP)
    native,labels=emit_image_region()
    assert parts[59]==native
    assert native.count(GETADR_MARKER)==1
    disasm=native.replace(GETADR_MARKER,bytes.fromhex("4eb900030000"))
    instructions=list(Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN | CS_MODE_M68K_000).
                      disasm(disasm,0))
    assert sum(i.size for i in instructions)==len(native)
    starts={i.address for i in instructions}
    assert all(off in starts for off in labels.values())
    assert not any(i.mnemonic in ("illegal","dc.w","trap","bkpt")
                   for i in instructions)
    assert meta["public_commands"]==54 and meta["ap20_entries"]==61
    assert meta["new_entry_index"]==59
    assert meta["compiler_v2_bytes"]>32768
    names=[x for x in report["tokens"] if x["name"]=="aga image region"]
    assert len(names)==1
    assert (names[0]["function"],names[0]["signature"]) == (59,API[3])
    total=0
    aw,ah=57,22
    # Independently cover both AP20 layouts, multiple depths, masks,
    # unaligned source X, destination X, screen clipping and source tiles.
    for depth in (1,4,8):
        pix=bytes(((x*3+y*5)^(x//4)) % (1<<depth)
                  for y in range(ah) for x in range(aw))
        mask=bytes(int((x+y)%5!=0) for y in range(ah) for x in range(aw))
        for masked in (False,True):
            payload=pack_image(aw,ah,depth,pix,mask if masked else None)
            for layout in ("interpreted","compiled"):
                for sx,sy,w,h,x,y in ((0,0,19,11,0,0),
                                     (19,0,19,11,15,7),
                                     (38,11,19,11,-7,-4),
                                     (3,4,29,15,49,37),
                                     (2,2,21,9,80,60)):
                    total+=run_case(binary,payload,layout=layout,
                                    depth=depth,front=1 if y<0 else 0,
                                    sx=sx,sy=sy,width=w,height=h,x=x,y=y,
                                    mode=1 if masked else 0)
                if masked:
                    total+=run_case(binary,payload,layout=layout,
                                    depth=depth,sx=9,sy=3,width=15,height=9,
                                    x=1,y=1,mode=0,flag=3)
    # Explicit refusal BEFORE any destination write or Safe mutation:
    pix=bytes((x+y)%16 for y in range(ah) for x in range(aw))
    opaque=pack_image(aw,ah,4,pix)
    masked=pack_image(aw,ah,4,pix,
                      bytes(int(i%3!=0) for i in range(aw*ah)))
    for kw in (
        dict(bank=4),dict(bank=11),dict(bank=65536),
        dict(sx=-1),dict(sy=-1),dict(sx=56,width=2),
        dict(sy=21,height=2),dict(width=0),dict(height=0),
        dict(width=58),dict(height=23),
        dict(sx=0x7fffffff),dict(width=-1),dict(mode=-1),
        dict(mode=2),dict(x=32768),dict(y=-32769),
    ):
        total+=run_case(binary,opaque,expect_ok=False,**kw)
    total+=run_case(binary,opaque,expect_ok=False,mode=1)
    total+=run_case(binary,masked,expect_ok=False,
                    pending=1,safe_ready=False)
    total+=run_case(binary,masked,pending=3,safe_ready=True,
                    flag=1)
    print("R60 GATE A NATIVE CPU/CI PASS:",total,
          "actual 68000 pixel/ABI cases (interpreted/compiled layouts)")
    print("R60 additive 54 tokens, 61 AP20 entries, V2 >32K,",
          meta["region_routine_bytes"],"bytes new 68000 code")
    print("R59 LAST_GOOD untouched; R60 Gate B/C WinUAE NOT TESTED")


if __name__=="__main__":
    main()
