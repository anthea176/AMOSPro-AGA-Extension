#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S1-P1c: package verified MC68020 AGSP pipeline as a PRIVATE AP20 V2 unit.

Input is actual assembled pipeline bytes from VASM. Result is an in-memory
AP20 HUNK candidate with one additional UNREFERENCED private native group.
All 100 P2d public commands, GetP entries and 203 original code entries
are byte-exact unchanged. This does NOT create a new public token, an
installable Lib, a Runtime proof or a Compiler validation.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import argparse

from active_library import P2D_SHA
from audit_ap20 import inspect, parse, walk_tokens
from ap20_v2_island_dispatch import pc16_displacements
from build_m19_p2d_in_memory import build_p2d
from compiler_bridge_v2_probe import DISPATCH_V2, MAX_UNIT_BYTES
from compiler_relocation import repack_ap20, unpack_ap20

TITLE=b'AMOSPro AGA M19 S1-P1c PRIVATE AGSP MC68020\0$VER: AGSP S1-P1c non-installable\0'
TITLE += bytes(len(TITLE) & 1)


def build_private_agsp(raw: bytes) -> tuple[bytes, dict]:
    if type(raw) is not bytes or len(raw) < 1000 or len(raw) & 1:
        raise ValueError('invalid compiled MC68020 pipeline length/alignment')
    if len(raw) + len(DISPATCH_V2) > MAX_UNIT_BYTES:
        raise ValueError('AP20 native group over 16-bit Compiler size')
    if not raw.startswith(b'\x60\x00'):  # BRA.W to first code body
        raise ValueError('pipeline raw entry must begin with verified BRA.W')
    if b'\xfe\x11\xf7\x00' not in raw:
        raise ValueError('native pipeline missing verified AMOS Main markers')
    original, baseline = build_p2d()
    if (sha256(original).hexdigest() != P2D_SHA or
            baseline['commands'] != 100 or baseline['entries'] != 203):
        raise ValueError('P2d authoritative source/builder drift')
    tokens, parts, _oldtitle = unpack_ap20(original)
    if len(parts) != 203 or parts[-1][:len(DISPATCH_V2)] != DISPATCH_V2:
        raise ValueError('P2d V2 AP20 group layout drift')
    all_parts = [*parts, DISPATCH_V2 + raw]
    candidate = repack_ap20(original, tokens, all_parts, TITLE)
    new_tokens, new_parts, new_title = unpack_ap20(candidate)
    if (new_tokens != tokens or new_parts[:-1] != parts or
            new_parts[-1] != DISPATCH_V2 + raw or new_title != TITLE):
        raise ValueError('AP20 HUNK candidate not exactly reversible')
    problems = inspect(parse(candidate))['issues']
    if problems:
        raise ValueError('AP20 audit failed: ' + repr(problems))
    d = pc16_displacements(new_parts)
    if set(d) != set(pc16_displacements(parts)):
        raise ValueError('protected public PC16 links changed')
    original_tokens = [(x['name'],x['instruction'],x['function'],x['signature'])
                       for x in walk_tokens(tokens)]
    new_tokens_parsed = [(x['name'],x['instruction'],x['function'],x['signature'])
                         for x in walk_tokens(new_tokens)]
    if original_tokens != new_tokens_parsed:
        raise ValueError('P2d token/GetP entry map changed')
    return candidate, {
        'sha256': sha256(candidate).hexdigest(),
        'bytes': len(candidate),
        'private_code_sha256': sha256(raw).hexdigest(),
        'private_code_bytes': len(raw),
        'group': len(parts),
        'groups': len(all_parts),
        'protected_entries': 203,
        'protected_commands': 100,
        'max_pc16': max(map(abs,d.values())),
        'installable': False,
        'api_exported': False,
    }


def main() -> None:
    args=argparse.ArgumentParser()
    args.add_argument('--pipeline',type=Path,required=True)
    argv=args.parse_args()
    image, report = build_private_agsp(argv.pipeline.read_bytes())
    assert len(image)==report['bytes']
    print('S1_P1C_PRIVATE_AP20_IN_MEMORY', report)
    print('NO_FILE_WRITTEN; NO_AP20_TOKEN; NO_DIST_PROMOTION; NOT_RUNTIME_TESTED')


if __name__ == '__main__':
    main()
