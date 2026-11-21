#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 AP20 V2 grouped dispatch experiment FROM the frozen P0f source.

Gate A only; no alternate installed .Lib, no new ASC and no P0d promotion.
The 4 actual native P0f groups are copied unchanged into local AP20 islands.
Compiler acceptance of INTERLEAVED entries and groups still needs Gate C.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path

from ap20_v2_island_dispatch import dispatch_islands, pc16_displacements
from compiler_relocation import unpack_ap20
from audit_ap20 import inspect, parse
from build_m19_p0f_public_bound_in_memory import build as build_p0f
from active_library import P1E_SHA

P0F_SHA = '6175705e22ed0c3f52c1ba317b2fad7aaca5af0db507c63a1ed629a724609a45'
P0D_SHA = 'bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be'
ISLAND_SHA = '34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56'
B7_SHA = 'f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b'
B7M1_SHA = '838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403'
B7M2_SHA = '242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'
B8_SHA = '00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae'
B8S1_SHA = '3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a'
P0_FREE_SHA = 'f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d'
UNIT5_SHA = '967a03f7a955f295f41b9391f8743d6e081305ca96084cd907b9d7603039dbe1'
LAST_GOOD_SHA = P1E_SHA
TITLE = (b'AMOSPro AGA M19 AP20 V2 ISLAND DISPATCH MC68020 SOURCE ONLY\0'
         b'$VER: AGA M19 AP20 islands UNINSTALLED P0f foundation\0')
TITLE += bytes(len(TITLE) & 1)


def build():
    root = Path(__file__).resolve().parents[1]
    current = (root/'dist/AMOSPro_AGA.Lib').read_bytes()
    good = (root/'dist/AMOSPro_AGA_LAST_GOOD.Lib').read_bytes()
    if (sha256(current).hexdigest() not in (P0D_SHA,ISLAND_SHA,UNIT5_SHA,B7_SHA,B7M1_SHA,B7M2_SHA,B8_SHA,B8S1_SHA,P0_FREE_SHA,P1E_SHA)
            or sha256(good).hexdigest()!=LAST_GOOD_SHA
            or (sha256(current).hexdigest()==P1E_SHA and current!=good)):
        raise ValueError('Unknown active P0d/AP20 islands/five-unit/B7 candidate or LAST_GOOD changed: refuse reconstruction')
    source, old_meta = build_p0f()
    if sha256(source).hexdigest()!=P0F_SHA or len(source)!=96744:
        raise ValueError('P0f source provenance mismatch')
    candidate, layout = dispatch_islands(source, title=TITLE)
    if sha256(candidate).hexdigest()!=ISLAND_SHA or len(candidate)!=96908:
        raise ValueError('AP20 islands candidate byte drift')
    if sha256(current).hexdigest()==ISLAND_SHA and candidate!=current:
        raise ValueError('Installed test candidate differs from pinned builder')
    token, parts, _ = unpack_ap20(candidate)
    original_tokens, original, _ = unpack_ap20(source)
    for i,j in layout.group_map.items():
        if parts[j]!=original[i]:
            raise ValueError(f'Native unit {i} modified')
    old = inspect(parse(source))
    new = inspect(parse(candidate))
    if new['issues'] or len(old['tokens'])!=len(new['tokens']):
        raise ValueError('Incompatible public AP20 token table')
    for before, after in zip(old['tokens'], new['tokens']):
        if (before['name'],before['signature'])!=(after['name'],after['signature']):
            raise ValueError('Public command changed')
    if len(token)!=len(original_tokens):
        raise ValueError('Token string encoding was modified')
    if layout.max_pc16 >= 32000:
        raise ValueError('Islands did not remove the PC16 bottleneck')
    return candidate, dict(
        sha256=sha256(candidate).hexdigest(), size=len(candidate),
        source_sha=P0F_SHA, source_entries=len(original),
        ap20_entries=len(parts), native_groups=layout.group_map,
        old_pc16=max(map(abs, pc16_displacements(original).values())),
        new_pc16=layout.max_pc16, added_getp_markers=layout.added_getp_markers,
        entries_rebound=len(layout.entry_map), tokens=len(new['tokens']),
        gate_a='PENDING CPU/CI', gate_b='NOT TESTED', gate_c='NOT TESTED',
        distribution='IN MEMORY ONLY', layout=layout)


if __name__=='__main__':
    _out,_meta=build()
    print('M19 AP20 V2 DISPATCH ISLANDS SOURCE-ONLY',
          {k:v for k,v in _meta.items() if k!='layout'})
