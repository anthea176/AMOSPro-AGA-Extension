#!/usr/bin/env python3
"""R82 experimental image-draw-only AP20 integration, IN MEMORY.

This is NOT an installable R82: the approved Bank Palette API and AGAPIC v2
Region implementation are still missing. Protect R81 LAST_GOOD and all
existing test files. Do not emit a candidate .Lib from this builder.
"""
from __future__ import annotations

from hashlib import sha256

from audit_ap20 import inspect, parse
from build_c2p_r81_opt020 import build as build_r81
from build_c2p_r76_rpg_fix import SITES, state_offset
from compiler_bridge_v2_probe import unwrap_native_parts_v2, wrap_native_ap20_v2
from compiler_relocation import GETP, repack_ap20, unpack_ap20
from native_relative_links import assert_native_links, relink_native_parts
from c2p_r74_relink import check_cross_r74
from m16_image_draw_r45_emit import emit_image_draw
from m16_agapic_v2_draw_emit import emit_image_draw_v2
from aga_compiler_capacity import inspect_library

R81_SHA = '9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4'
NEW_TITLE = (b'AMOSPro AGA AGAPIC v2 R82 0.13.27 in-memory design preview\0'
             b'$VER: AMOSPro_AGA 0.13.27 preview\0')
NEW_TITLE += bytes(len(NEW_TITLE) & 1)


def build():
    baseline, _ = build_r81()
    assert sha256(baseline).hexdigest() == R81_SHA
    tokens, original = unwrap_native_parts_v2(baseline)
    assert len(original) == 76
    assert state_offset(original) == 12070
    old, _ = emit_image_draw(accept_loaded_flags_zero=True,
                             opt020=True, reset_failure_d3=True)
    assert original[55] == old + GETP, 'unrecognized R81 image draw entry'
    new, labels = emit_image_draw_v2()
    assert new != old and new[:4] == old[:4] == bytes.fromhex('48e7efee')
    assert len(new) % 2 == 0 and len(new) < len(old) + 2500
    parts = list(original)
    parts[55] = new + GETP
    parts[:70] = relink_native_parts(parts[:70])
    assert_native_links(parts[:70])
    check_cross_r74(parts[:70])
    assert state_offset(parts) == 12070
    for entry, pos, opcode in SITES:
        assert parts[entry][pos:pos + 4] == opcode.to_bytes(2,'big') + bytes.fromhex('2f26')
    changed = {i for i,(a,b) in enumerate(zip(original,parts)) if a!=b}
    assert changed == {20,55,57,58}, ('unexpected native changes',changed)
    assert parts[:20] == original[:20]
    assert all(parts[i] == original[i] for i in range(70,76))
    native = repack_ap20(baseline,tokens,parts,NEW_TITLE)
    image = wrap_native_ap20_v2(native,NEW_TITLE)
    assert unwrap_native_parts_v2(image) == (tokens,parts)
    tok, entries, title = unpack_ap20(image)
    assert tok == tokens and len(entries) == 77 and title == NEW_TITLE
    report=inspect(parse(image))
    assert report['issues'] == []
    assert len([x for x in report['tokens'] if x['name'].startswith('aga ')]) == 70
    budget = inspect_library(image)
    assert budget['margin'] > 0
    return image, {
        'version':'R82 experimental image-draw-only',
        'size':len(image),
        'sha256':sha256(image).hexdigest(),
        'native_image_bytes':len(new),
        'native_growth':len(new)-len(old),
        'changed_entries':sorted(changed),
        'ap20_entries':77,
        'public_commands':70,
        'compiler_unit_size':budget['monolith_bytes'],
        'compiler_margin':budget['margin'],
        'validation':'in-memory structural ONLY; no full R82, no Gate B/C'
    }


if __name__=='__main__':
    a,metadata=build()
    assert build()[0]==a
    print('R82 IMAGE-ONLY STRUCTURAL PROBE',metadata)
