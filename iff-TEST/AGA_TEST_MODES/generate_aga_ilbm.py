#!/usr/bin/env python3
"""Generate diagnostic IFF ILBM images for AMOSPro AGA, with reference PNGs.

The generated images are ORIGINAL synthetic test patterns, not borrowed assets.
HAM6/HAM8 generate genuine control/data pixels, not ordinary indexed bitmaps.
This file is included in the test pack for reproducibility (Pillow required).
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
PAL_MONITOR_ID = 0x00021000
HAM_KEY = 0x0800
SUPER_KEY = 0x8020
SUPERLACE_KEY = 0x8024
DBLPALLORES_KEY = 0x000A1000
DBLNTSCLORES_KEY = 0x00091000
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'


def txtfont(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def block(tag: bytes, payload: bytes):
    assert len(tag) == 4
    return tag + struct.pack('>I', len(payload)) + payload + (b'\0' if len(payload) % 2 else b'')


def byterun1(row: bytes):
    """ByteRun1 encode a SINGLE plane scanline, never across plane boundaries."""
    out = bytearray()
    i = 0
    while i < len(row):
        count = 1
        while i + count < len(row) and row[i + count] == row[i] and count < 128:
            count += 1
        if count >= 3:
            out += bytes(((257 - count) & 255, row[i]))
            i += count
            continue
        start = i
        i += count
        while i < len(row) and i - start < 128:
            run = 1
            while i + run < len(row) and row[i + run] == row[i] and run < 128:
                run += 1
            if run >= 3 or i + run - start > 128:
                break
            i += run
        out.append(i - start - 1)
        out += row[start:i]
    return bytes(out)


def decode_byterun1(data: bytes, start: int, row_bytes: int):
    out = bytearray()
    pos = start
    while len(out) < row_bytes:
        assert pos < len(data), 'short BODY'
        v = data[pos]
        pos += 1
        if v == 128:
            continue
        if v < 128:
            run = v + 1
            assert pos + run <= len(data) and len(out) + run <= row_bytes
            out += data[pos:pos + run]
            pos += run
        else:
            run = 257 - v
            assert pos < len(data) and len(out) + run <= row_bytes
            out += bytes((data[pos],)) * run
            pos += 1
    return bytes(out), pos


def pack_planar(indices: bytes, width: int, height: int, depth: int, compression: int):
    assert len(indices) == width * height
    rb = ((width + 15) // 16) * 2
    out = bytearray()
    for y in range(height):
        line = indices[y * width:(y + 1) * width]
        for plane in range(depth):
            row = bytearray(rb)
            for x, value in enumerate(line):
                if value & (1 << plane):
                    row[x >> 3] |= 1 << (7 - (x & 7))
            if compression:
                out.extend(byterun1(bytes(row)))
            else:
                out.extend(row)
    return bytes(out)


def unpack_planar(body: bytes, width: int, height: int, depth: int, compression: int):
    rb = ((width + 15) // 16) * 2
    pos = 0
    out = bytearray(width * height)
    for y in range(height):
        for plane in range(depth):
            if compression:
                row, pos = decode_byterun1(body, pos, rb)
            else:
                row = body[pos:pos + rb]
                pos += rb
                assert len(row) == rb
            for x in range(width):
                if row[x >> 3] & (1 << (7 - (x & 7))):
                    out[y * width + x] |= 1 << plane
    assert pos == len(body), (pos, len(body))
    return bytes(out)


def ilbm_bytes(width, height, depth, cmap, modeid, indices, compression=1):
    assert width > 0 and height > 0 and 1 <= depth <= 8
    assert len(indices) == width * height
    assert len(cmap) > 0 and len(cmap) <= 256
    assert all(len(rgb) == 3 for rgb in cmap)
    bmhd = struct.pack('>HHhhBBBBHBBhh', width, height, 0, 0, depth,
                       0, compression, 0, 0, 22 if width <= 640 else 11,
                       22, width, height)
    assert len(bmhd) == 20
    body = pack_planar(indices, width, height, depth, compression)
    cmap_bytes = bytes(n for rgb in cmap for n in rgb)
    content = b'ILBM' + b''.join((block(b'BMHD', bmhd),
                                block(b'CMAP', cmap_bytes),
                                block(b'CAMG', struct.pack('>I', modeid)),
                                block(b'BODY', body)))
    form = b'FORM' + struct.pack('>I', len(content)) + content
    # Independently parse IFF, chunk lengths, no extra data; decompress all plane rows.
    assert form[0:4] == b'FORM' and int.from_bytes(form[4:8], 'big') == len(form) - 8
    p, found = 12, {}
    while p < len(form):
        kind, size = form[p:p + 4], int.from_bytes(form[p + 4:p + 8], 'big')
        found[kind] = form[p + 8:p + 8 + size]
        p += 8 + size + (size & 1)
    assert p == len(form)
    assert struct.unpack('>I', found[b'CAMG'])[0] == modeid
    assert struct.unpack('>HH', found[b'BMHD'][:4]) == (width, height)
    assert len(found[b'CMAP']) == len(cmap) * 3
    assert unpack_planar(found[b'BODY'], width, height, depth, compression) == indices
    return form, len(body)


def ham_palette(bits: int):
    bases = [
        (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
        (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
        (128, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128),
        (128, 128, 0), (0, 128, 128), (128, 0, 128), (255, 128, 0),
    ]
    if bits == 4:
        return [tuple(round(c / 17) * 17 for c in rgb) for rgb in bases]
    # HAM8: first 16 strong anchors, followed by 4x4x3 cube and luminance anchors
    palette = list(bases)
    for r in (0, 85, 170, 255):
        for g in (0, 85, 170, 255):
            for b in (0, 128, 255):
                if len(palette) < 64:
                    palette.append((r, g, b))
    assert len(palette) == 64
    return palette


def template(w, h, title, subtitle, indexed=False):
    image = Image.new('RGB', (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    sc = w / 320
    header = 34 if w < 700 else 58
    draw.rectangle((0, 0, w - 1, header - 1), fill=(10, 18, 35))
    draw.text((int(6*sc), 3), title, font=txtfont(13 if w < 700 else 29), fill=(255, 255, 255))
    draw.text((int(6*sc), 18 if w < 700 else 33), subtitle, font=txtfont(9 if w < 700 else 16), fill=(255, 216, 70))
    # Saturated ramps, one channel at a time.
    y0 = header
    y1 = header + (h - header) * 2 // 5
    for y in range(y0, y1):
        section = (y - y0) * 3 // max(1, y1 - y0)
        for x in range(w):
            v = x * 255 // (w - 1)
            if section == 0:
                pixel = (v, 16, 16)
            elif section == 1:
                pixel = (10, v, 70)
            else:
                pixel = (80, 10, v)
            image.putpixel((x, y), pixel)
    # Second section: saturated rainbow with both horizontal/vertical variation.
    y2 = y1 + (h - header) * 3 // 10
    px = image.load()
    for y in range(y1, y2):
        for x in range(w):
            a = (x / w * 2 * math.pi * 2.7) + (y / max(1, y2 - y1) * math.pi)
            px[x, y] = (
                int(126 + 125 * math.sin(a)),
                int(126 + 125 * math.sin(a + 2.1)),
                int(126 + 125 * math.sin(a + 4.2)),
            )
    # Below: high-frequency indexed patterns and hard edges.
    draw.rectangle((0, y2, w-1, h-1), fill=(6, 8, 15))
    row = max(1, (h - y2) // 3)
    n = 16 if indexed else 8
    for i in range(n):
        x0 = i * w // n
        x1 = (i+1)*w//n - 1
        c = (255, 0, 0) if i % 4 == 0 else ((0, 255, 0) if i%4==1 else ((0, 0, 255) if i%4==2 else (250, 250, 250)))
        draw.rectangle((x0,y2,x1,y2+row-1), fill=c)
    for x in range(w):
        for y in range(y2+row, min(h,y2+row*2)):
            px[x,y] = (255,255,255) if ((x//(1 if indexed else 2))+(y//(2 if indexed else 3)))%2 == 0 else (0,0,0)
    for x in range(w):
        for y in range(y2+2*row,h):
            v = 255*x//max(1,w-1)
            px[x,y] = (v,v,v)
    return image


def ham_encode(target: Image.Image, base, precision):
    """Greedy HAM encoder: SET, modify BLUE/RED/GREEN, per-pixel RGB error.

    First pixel of every scanline is SET for deterministic reset.
    """
    w,h = target.size
    rgb=target.load()
    data=bytearray(w*h)
    decoded=Image.new('RGB',(w,h))
    out=decoded.load()
    opcount=Counter()
    nlevels=1<<precision
    shift=precision

    def level(k):
        if precision==4:
            return k*17
        return (k<<2)|(k>>4)

    def error(a,b):
        return sum((a[i]-b[i])**2 for i in range(3))

    for y in range(h):
        prev=(0,0,0)
        for x in range(w):
            dest=rgb[x,y]
            idx=min(range(len(base)),key=lambda i:error(base[i],dest))
            best=(error(base[idx],dest),0,idx,base[idx])
            if x>0:
                for op,channel in ((1,2),(2,0),(3,1)):
                    quant=min(nlevels-1,max(0,round(dest[channel]*(nlevels-1)/255)))
                    nextc=list(prev)
                    nextc[channel]=level(quant)
                    e=error(nextc,dest)
                    # Prefer SET for exact ties to limit propagation of errors.
                    if e<best[0]:
                        best=(e,op,quant,tuple(nextc))
            _,op,value,prev=best
            code=(op<<precision)|value
            assert 0<=code<1<<(precision+2)
            data[y*w+x]=code
            out[x,y]=prev
            opcount[op]+=1
    assert all(opcount[code]>100 for code in range(4)),opcount
    return bytes(data),decoded,dict(opcount)


def indexed_encode(image:Image.Image, colors):
    palette=[]
    for i in range(colors):
        # Distinct fixed colors including bright RGB and grays.
        if i==0: rgb=(0,0,0)
        elif i==1:rgb=(255,255,255)
        elif i==2:rgb=(255,0,0)
        elif i==3:rgb=(0,255,0)
        elif i==4:rgb=(0,0,255)
        elif i==5:rgb=(255,255,0)
        elif i==6:rgb=(0,255,255)
        elif i==7:rgb=(255,0,255)
        else: rgb=(int((i*77)%256),int((i*137)%256),int((i*211)%256))
        palette.append(rgb)
    w,h=image.size
    src=list(image.getdata())
    cache={}
    idx=bytearray(w*h)
    for i,rgb in enumerate(src):
        if rgb not in cache:
            cache[rgb]=min(range(colors),key=lambda k:sum((rgb[j]-palette[k][j])**2 for j in range(3)))
        idx[i]=cache[rgb]
    dec=Image.new('RGB',(w,h))
    dec.putdata([palette[k] for k in idx])
    return bytes(idx),dec,palette


def decode_ham_values(indices,w,h,base,precision):
    assert len(indices)==w*h
    image=Image.new('RGB',(w,h))
    dst=image.load()
    mask=(1<<precision)-1
    def value(n):return n*17 if precision==4 else ((n<<2)|(n>>4))
    for y in range(h):
        prev=(0,0,0)
        for x in range(w):
            v=indices[y*w+x]
            op,num=v>>precision,v&mask
            if op==0:prev=base[num]
            elif op==1:prev=(prev[0],prev[1],value(num))
            elif op==2:prev=(value(num),prev[1],prev[2])
            elif op==3:prev=(prev[0],value(num),prev[2])
            dst[x,y]=prev
    return image


def onefile(file,w,h,depth,modeid,compress,ham=False):
    title=file.replace('.iff','').replace('_',' ')
    sub=f'{w} x {h} / {depth} planes / CAMG ${modeid:08X}'
    target=template(w,h,title,sub,indexed=not ham)
    if ham:
        precision=depth-2
        palette=ham_palette(precision)
        idx,reference,ops=ham_encode(target,palette,precision)
        other=decode_ham_values(idx,w,h,palette,precision)
        assert other.tobytes()==reference.tobytes(),file
    else:
        idx,reference,palette=indexed_encode(target,1<<depth)
        ops={}
    payload,body_size=ilbm_bytes(w,h,depth,palette,modeid,idx,compression=compress)
    # External expectation with independent decoder above
    assert payload.startswith(b'FORM')
    (OUT/file).write_bytes(payload)
    png=file.replace('.iff','.png')
    reference.save(OUT/png,optimize=True)
    record={
        'file':file,'w':w,'h':h,'depth':depth,
        'camg':f'${modeid:08X}','cmap_entries':len(palette),
        'compression':{'0':'RAW','1':'ByteRun1'}[str(compress)],
        'form_bytes':len(payload),'body_bytes':body_size,
        'sha256':hashlib.sha256(payload).hexdigest(),
        'reference_png':png,'op_counts':ops,
        'status':'structure, ByteRun1, planar indices and HAM decode verified in Python; NOT WinUAE-tested'
    }
    print(file,record['form_bytes'],'bytes', 'HAM ops' if ham else 'indexed',ops)
    return record


def main():
    records=[]
    records.append(onefile('HAM6_PAL_320x256.iff',320,256,6,PAL_MONITOR_ID|HAM_KEY,1,True))
    records.append(onefile('HAM8_PAL_320x256.iff',320,256,8,PAL_MONITOR_ID|HAM_KEY,1,True))
    records.append(onefile('SHIRES_PAL_1280x256.iff',1280,256,4,PAL_MONITOR_ID|SUPER_KEY,1))
    records.append(onefile('SHIRES_LACE_PAL_1280x512.iff',1280,512,4,PAL_MONITOR_ID|SUPERLACE_KEY,1))
    records.append(onefile('DBLPAL_320x256.iff',320,256,4,DBLPALLORES_KEY,1))
    records.append(onefile('DBLNTSC_320x200.iff',320,200,4,DBLNTSCLORES_KEY,1))
    (OUT/'manifest.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
