#!/usr/bin/env python3
"""Source-only, non-native checks for the S0 read-only AGA ViewPort AMOS probe.

Static checks never prove WinUAE display, DMA detachment or AMOS Compiler behavior.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / 'examples/sprite_s0_viewport/VIEWPORT_PROBE.asc'
S0B = ROOT / 'tests/design/sprites_aga/SPRITE_PROBE.asc'


def inspect_source(raw: bytes) -> list[str]:
    errors: list[str] = []
    if not raw.isascii() or b'\r' in raw:
        errors.append('ASC must remain ASCII with LF only')
    code = raw.decode('ascii')
    lines = code.splitlines()
    if any(len(line) > 220 for line in lines):
        errors.append('AMOS line longer than 220 characters')
    if any(re.search(r'\b(?:Poke|Doke|Loke|Call|Pload|Exec)\b', line, re.I)
           for line in lines if not line.lstrip().startswith("'")):
        errors.append('S0 must never write memory or call native code')
    anchors = (
        '_A5=Areg(5)',
        '_STATE=Leek(_A5+456)',
        '_SCREEN=Leek(_STATE)',
        '_WINDOW=Leek(_STATE+36)',
        '_WSCREEN=Leek(_WINDOW+46)',
        '_SW=Deek(_SCREEN+12) : _SH=Deek(_SCREEN+14)',
        '_VIEWPORT=_SCREEN+44',
        '_VPW=Deek(_VIEWPORT+24) : _VPH=Deek(_VIEWPORT+26)',
        '_MODES_OPEN=Deek(_VIEWPORT+32)',
        '_SPRINS=Leek(_VIEWPORT+12)',
        '_UCOPINS=Leek(_VIEWPORT+20)',
        '(_MODES_OPEN and $4000)',
        '(_MODES_DB and $4000)',
        '(_MODES_SWAP and $4000)',
        'Amos To Back',
        'Amos To Front',
        'Aga Screen Close',
        '_CLEANUP:',
        'Print #1,"MODES_OPEN ";_MODES_OPEN',
        'Print #1,"MODES_SWAP ";_MODES_SWAP',
        'Print #1,"SPRITES_OPEN ";_SPRITES_OPEN',
        'Print #1,"SPRITES_SWAP ";_SPRITES_SWAP',
        'Print #1,"CLOSE_RETURNED ";_CLOSE_RETURNED',
    )
    for anchor in anchors:
        if anchor not in code:
            errors.append('Missing/altered anchor: ' + anchor)
    for mode in ('INTERPRETED', 'RUNTIME', 'COMPILED'):
        if f'RAM:M19_S0_VP_{mode}.TXT' not in code:
            errors.append('Missing mode-specific RAM log: ' + mode)
    if 'SPRITES_SWAP=1' not in code or 'SPRITES_OPEN=1' not in code:
        errors.append('Sprite mode flag must be recorded, not assumed')
    if not code.rstrip().endswith('End'):
        errors.append('Missing final AMOS End')
    return errors


class SourceTests(unittest.TestCase):
    def test_current_source_anchors(self):
        self.assertEqual(inspect_source(ASC.read_bytes()), [])

    def test_mutated_struct_offset_is_rejected(self):
        raw = ASC.read_bytes().replace(b'_VIEWPORT=_SCREEN+44',
                                       b'_VIEWPORT=_SCREEN+40')
        self.assertTrue(any('offset' in e or 'anchor' in e for e in inspect_source(raw)))

    def test_invalid_mask_is_rejected(self):
        raw = ASC.read_bytes().replace(b'(_MODES_OPEN and $4000)',
                                       b'(_MODES_OPEN and $2000)')
        self.assertNotEqual(inspect_source(raw), [])

    def test_native_memory_write_is_rejected(self):
        raw = ASC.read_bytes().replace(b'\nEnd\n', b'\nPoke $DFF000,1\nEnd\n', 1)
        self.assertIn('S0 must never write memory or call native code', inspect_source(raw))

    def test_no_mode_mixing(self):
        raw = ASC.read_bytes().replace(b'RAM:M19_S0_VP_COMPILED.TXT',
                                       b'RAM:M19_S0_VP_RUNTIME.TXT')
        self.assertNotEqual(inspect_source(raw), [])


def inspect_s0c_source(raw: bytes) -> list[str]:
    """S0c static guards: bounded Chip data, OS ownership and deferred memory release.

    These checks do not prove real display, hardware DMA detachment or Compiler.
    """
    errors: list[str] = []
    if not raw.isascii() or b'\r' in raw:
        errors.append('S0c ASC must be ASCII with LF only')
    code = raw.decode('ascii')
    lines = code.splitlines()
    if any(len(line) > 220 for line in lines):
        errors.append('S0c has AMOS lines longer than 220 characters')
    bare = '\n'.join(line for line in lines if not line.lstrip().startswith("'"))
    if re.search(r'\b(?:OFF_SPRITE|ON_SPRITE|Aga\s+Swap|Poke|Call|Execall|Pload)\b', bare, re.I):
        errors.append('S0c must not touch hardware DMA registers or use arbitrary machine code')
    anchors = (
        '_VIEWPORT=_SCREEN+44',
        '_MODES=Deek(_VIEWPORT+32)',
        '(_MODES and $4000)',
        'If _SPRITES_FLAG<>1',
        'If Length(_I)=0',
        'Trap Reserve As Chip Work _BANK,156',
        '_PTR=Start(_BANK) : _IMAGE=_PTR+12 : _BLANK=_IMAGE+72',
        'Loke _PTR,0 : Doke _PTR+4,16 : Doke _PTR+6,0',
        'For _I=0 To 70 Step 2',
        'Doke _IMAGE+_I,0',
        'Doke _BLANK+_I,0',
        'Doke _IMAGE+4+_ROW*4,_PL0',
        'Doke _IMAGE+6+_ROW*4,_PL1',
        'Areg(0)=_PTR : Dreg(0)=-1',
        'If _CHANNEL=65535',
        'If _CHANNEL>7',
        '_OWN=_CHANNEL',
        'If _STRUCT_NUM<>_CHANNEL',
        '_COLOR_BASE=16+((_CHANNEL and 6)*2)',
        '_P1=Aga Palette Set(_COLOR_BASE+1,255,70,50)',
        'Areg(0)=_VIEWPORT : Areg(1)=_PTR : Areg(2)=_IMAGE',
        '_PIXELS_ARMED=1',
        'Dreg(0)=35+_FRAME*2 : Dreg(1)=96',
        'For _FRAME=1 To 100',
        'If _OWN>=0',
        'Areg(0)=_VIEWPORT : Areg(1)=_PTR : Areg(2)=_BLANK',
        '_BLANK_SET=1',
        'For _J=1 To 2',
        'If _PIXELS_ARMED=1',
        'Dreg(0)=_OWN',
        '_FREE=1 : _OWN=-1',
        'Aga Screen Close',
        'Amos To Front',
        'For _J=1 To 3',
        'If _OPEN=0 or (_CLOSE_RETURNED=1 and _POSTWAIT=3 and _OWN=-1)',
        'Erase _BANK',
        '_BANK_HELD=1',
        'If _PREWAIT=2 and _CLOSE_RETURNED=1 and _POSTWAIT=3 and _BANK_CLEAN=1',
        'Print #1,"VERDICT ";_VERDICT$',
    )
    for a in anchors:
        if a not in bare:
            errors.append('Missing S0c guard: ' + a)
    for off, count in ((-408, 1), (-420, 2), (-426, 1), (-414, 1), (-270, 1)):
        if bare.count(f'Gfxcall({off})') != count:
            errors.append(f'Wrong number of graphics.library calls at LVO {off}')
    order = (
        'Gfxcall(-408)', 'Areg(2)=_IMAGE', 'Gfxcall(-426)',
        'Areg(2)=_BLANK', 'Gfxcall(-414)', 'Aga Screen Close',
        'Gfxcall(-270)', 'Erase _BANK',
    )
    if all(s in bare for s in order):
        pos = [bare.index(s) for s in order]
        if pos != sorted(pos):
            errors.append('Unsafe S0c order: image/blank/free/close/TOF/erase')
    for mode in ('UNKNOWN', 'INTERPRETED', 'RUNTIME', 'COMPILED'):
        name = f'M19_S0C_VIS_{mode}.TXT'
        if name not in code or len(name) > 30:
            errors.append('S0c log name missing or too long: ' + name)
    if not code.rstrip().endswith('End'):
        errors.append('S0c missing AMOS End')
    return errors


class S0cSourceTests(unittest.TestCase):
    def test_one_reusable_source_with_s0c_cleanup_guards(self):
        self.assertEqual([p.name for p in S0B.parent.glob('*.asc')], ['SPRITE_PROBE.asc'])
        self.assertEqual(inspect_s0c_source(S0B.read_bytes()), [])

    def test_wrong_bank_type_detected(self):
        altered = S0B.read_bytes().replace(b'Reserve As Chip Work', b'Reserve As Work')
        self.assertNotEqual(inspect_s0c_source(altered), [])

    def test_wrong_change_sprite_detected(self):
        altered = S0B.read_bytes().replace(b'Areg(2)=_BLANK', b'Areg(2)=_IMAGE')
        self.assertNotEqual(inspect_s0c_source(altered), [])

    def test_unsafe_release_detected(self):
        altered = S0B.read_bytes().replace(b'If _OWN>=0', b'If _OWN=-1')
        self.assertNotEqual(inspect_s0c_source(altered), [])

    def test_without_post_close_to_f_detected(self):
        altered = S0B.read_bytes().replace(b'Gfxcall(-270)', b'Gfxcall(-420)')
        self.assertNotEqual(inspect_s0c_source(altered), [])

    def test_missing_view_transition_gate_detected(self):
        altered = S0B.read_bytes().replace(
            b'_CLOSE_RETURNED=1 and _POSTWAIT=3 and _OWN=-1',
            b'_CLOSE_RETURNED=1 and _OWN=-1')
        self.assertNotEqual(inspect_s0c_source(altered), [])

    def test_forbidden_hardware_register_write_detected(self):
        altered = S0B.read_bytes().replace(b'\nEnd\n', b'\nPoke $DFF096,1\nEnd\n')
        self.assertNotEqual(inspect_s0c_source(altered), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
