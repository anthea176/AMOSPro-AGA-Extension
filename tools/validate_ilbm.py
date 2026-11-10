"""Bounded ILBM reference decoder and recursive repository inventory (stdlib only)."""
from pathlib import Path
import argparse
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def inspect(data):
    require(len(data) >= 12 and data[:4] == b'FORM', 'missing FORM')
    end = 8 + int.from_bytes(data[4:8], 'big')
    require(12 <= end <= len(data), 'truncated/invalid FORM')
    require(data[8:12] == b'ILBM', 'not ILBM')
    chunks, properties = [], {}
    pos = 12
    while pos < end:
        require(end-pos >= 8, 'truncated chunk header')
        kind = data[pos:pos+4].decode('latin1')
        size = int.from_bytes(data[pos+4:pos+8], 'big')
        nxt = pos+8+size+(size & 1)
        require(nxt <= end, 'chunk/padding outside FORM')
        chunks.append(dict(id=kind, offset=pos, size=size, padding=size & 1))
        if kind in ('BMHD', 'CMAP', 'CAMG', 'BODY'):
            require(kind not in properties, 'duplicate '+kind)
            properties[kind] = data[pos+8:pos+8+size]
        pos = nxt
    require('BMHD' in properties and len(properties['BMHD']) == 20, 'invalid BMHD')
    names = ('width','height','x','y','depth','masking','compression','pad1',
             'transparentColor','xAspect','yAspect','pageWidth','pageHeight')
    meta = dict(zip(names, struct.unpack('>HHhhBBBBHBBhh', properties['BMHD'])))
    require(meta['width'] > 0 and meta['height'] > 0, 'empty geometry')
    require(1 <= meta['depth'] <= 8, 'unsupported depth')
    require(meta['masking'] in (0,1,2), 'unsupported masking')
    require(meta['compression'] in (0,1), 'unsupported compression')
    cmap = properties.get('CMAP', b'')
    require(bool(cmap) and len(cmap)%3 == 0 and len(cmap) <= 768, 'missing/invalid CMAP')
    camg = properties.get('CAMG', b'\0'*4)
    require(len(camg) == 4, 'invalid CAMG')
    mode = int.from_bytes(camg,'big')
    require('BODY' in properties and len(properties['BODY']) > 0, 'missing/empty BODY')
    meta.update(form_type='ILBM', form_size=end-8, file_size=len(data), trailing_bytes=len(data)-end,
                chunks=chunks, cmap_present='CMAP' in properties, cmap_entries=len(cmap)//3,
                cmap_rgb=list(map(list,zip(cmap[0::3],cmap[1::3],cmap[2::3]))),
                cmap_sha256=hashlib.sha256(cmap).hexdigest(), camg_present='CAMG' in properties,
                camg=mode, camg_hex=f'{mode:08x}', body_present=True, body_size=len(properties['BODY']),
                unknown_chunks=[c for c in chunks if c['id'] not in ('BMHD','CMAP','CAMG','BODY')],
                ehb=bool(mode&128), ham6=bool(mode&2048) and meta['depth']==6,
                ham8=bool(mode&2048) and meta['depth']==8, hires=bool(mode&32768),
                interlace=bool(mode&4), row_bytes=((meta['width']+15)//16)*2)
    return meta, properties['BODY']

def decode(meta, body):
    rb, depth, mask = meta['row_bytes'], meta['depth'], meta['masking'] == 1
    planes = [bytearray() for _ in range(depth+mask)]
    pos = 0
    for y in range(meta['height']):
        for plane in planes:
            row = bytearray()
            while len(row) < rb:
                require(pos < len(body), 'short BODY')
                if meta['compression'] == 0:
                    require(pos+rb <= len(body), 'short RAW row')
                    row.extend(body[pos:pos+rb]); pos += rb
                    break
                control = body[pos]; pos += 1
                if control == 128:
                    continue
                n = control+1 if control < 128 else 257-control
                require(n <= rb-len(row), 'ByteRun1 row overflow')
                consumed = n if control < 128 else 1
                require(pos+consumed <= len(body), 'ByteRun1 input overflow')
                row.extend(body[pos:pos+n] if control < 128 else body[pos:pos+1]*n)
                pos += consumed
            plane.extend(row)
    # NOP packets are legal even after the last output byte.
    if meta['compression'] == 1:
        while pos < len(body) and body[pos] == 128:
            pos += 1
    require(pos == len(body), 'unconsumed BODY data')
    return planes, pos

def inventory(root):
    rows = []
    for path in sorted(root.rglob('*'), key=lambda p:str(p).lower()):
        if path.suffix.lower() not in ('.iff','.ilbm') or '.git' in path.parts:
            continue
        row = {'file':path.relative_to(root).as_posix()}
        try:
            data = path.read_bytes()
            row['file_sha256'] = hashlib.sha256(data).hexdigest()
            meta, body = inspect(data)
            row.update(meta)
            planes, consumed = decode(meta,body)
            row.update(status='PASS', body_consumed=consumed,
                       planes=[dict(index=i,size=len(p),sum=sum(p),sha256=hashlib.sha256(p).hexdigest())
                               for i,p in enumerate(planes)])
        except (ValueError,OSError) as error:
            row.update(status='FAIL',error=str(error))
        rows.append(row)
    return rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/ILBM_INVENTORY.json')
    args=parser.parse_args()
    rows=inventory(args.root)
    args.output.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    lines=['# Inventaire ILBM réel','', 'Décodage de référence Python ; ne constitue pas un PASS AMOS/WinUAE.', '',
           '| Fichier | Dimensions | Plans | CMAP | CAMG | Compression | Mode | BODY consommé | Statique |',
           '|---|---|---:|---:|---|---|---|---:|---|']
    for r in rows:
        if r['status']=='FAIL':
            lines.append(f"| {r['file']} | | | | | | | | FAIL: {r['error']} |")
            continue
        mode='/'.join(k for k in ('ehb','ham6','ham8','hires','interlace') if r[k]) or 'indexed LoRes'
        lines.append(f"| {r['file']} | {r['width']}×{r['height']} | {r['depth']} | {r['cmap_entries']} | {r['camg_hex'] if r['camg_present'] else 'absent'} | {'RAW' if r['compression']==0 else 'ByteRun1'} | {mode} | {r['body_consumed']} | PASS |")
    lines += ['', 'Le JSON associé contient chaque BMHD, palette RGB complète, chunk, padding, taille et SHA256 par plan.',
              'Les octets suivant FORM sont signalés, jamais interprétés comme des chunks de cette image.']
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f"{len(rows)} images; {sum(r['status']=='PASS' for r in rows)} PASS")
    return int(not rows or any(r['status']=='FAIL' for r in rows))

if __name__=='__main__':
    raise SystemExit(main())
