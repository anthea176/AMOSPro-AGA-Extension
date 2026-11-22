#!/usr/bin/env python3
"""Source-only, non-native checks for the S0 read-only AGA ViewPort AMOS probe.

Static checks never prove WinUAE display, DMA detachment or AMOS Compiler behavior.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / 'examples/sprite_s0_viewport/VIEWPORT_PROBE.asc'
S0D = ROOT / 'tests/design/sprites_aga/SPRITE_PROBE.asc'


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


def inspect_s0d_source(raw: bytes) -> list[str]:
    """Source-only S0d checks; no WinUAE, compiler or hardware claim."""
    problems: list[str] = []
    if not raw.isascii() or b'\r' in raw:
        problems.append('S0d must be ASCII LF')
    text = raw.decode('ascii', errors='replace')
    lines = text.splitlines()
    if any(len(line) > 220 for line in lines):
        problems.append('AMOS line exceeds 220 characters')
    bare = '\n'.join(line for line in lines if not line.lstrip().startswith("'"))
    if re.search(r'\b(?:Poke|Call|Execall|Pload|Aga\s+Swap)\b|\$DFF[0-9A-Fa-f]+', bare, re.I):
        problems.append('direct hardware access or unapproved code')
    anchors = (
        'For _CYCLE=1 To 3',
        '_OPEN=0 : _BANK=0 : _BANK_OWN=0 : _BANK_CLEAN=0',
        'If Aga Detect=0',
        '_OPEN=Aga Screen Open(320,256,256,$00021000)',
        '_VIEWPORT=_SCREEN+44',
        '_MODES=Deek(_VIEWPORT+32)',
        '(_MODES and $4000)=0',
        '_DB=Aga Double Buffer',
        'If Length(_I)=0',
        'Trap Reserve As Chip Work _BANK,156',
        '_PTR=Start(_BANK) : _IMAGE=_PTR+12 : _BLANK=_IMAGE+72',
        'Doke _PTR+4,16',
        'Doke _IMAGE+4+_ROW*4,_PL0',
        'Doke _BLANK+_I,0',
        'Areg(0)=_PTR : Dreg(0)=-1',
        'If _CHANNEL=65535 or _CHANNEL>7',
        '_OWN=_CHANNEL : _GETS=_GETS+1',
        '_COLOR_BASE=16+((_CHANNEL and 6)*2)',
        'Areg(0)=_VIEWPORT : Areg(1)=_PTR : Areg(2)=_IMAGE',
        'For _FRAME=1 To 36',
        'Dreg(0)=35+_FRAME*5 : Dreg(1)=70+_CYCLE*28',
        'If _ERR=0 and _CYCLE=2 and _FRAME=12',
        'If _ERR=0 and _CYCLE=2 and _FRAME=24',
        'If _ERR=0 and _CYCLE=3 and _FRAME=8',
        '_CC=Aga Copper Clear',
        '_CW1=Aga Copper Wait(30,0)',
        '_CM1=Aga Copper Move($180,$F00)',
        '_CW2=Aga Copper Wait(180,0)',
        '_CM2=Aga Copper Move($180,$008)',
        '_CE=Aga Copper End',
        '_CON=Aga Copper On',
        'If _ERR=0 and _CYCLE=3 and _FRAME=25',
        '_COFF=Aga Copper Off',
        'If _COPPER_TOUCHED=1',
        'If _OWN>=0',
        'Areg(0)=_VIEWPORT : Areg(1)=_PTR : Areg(2)=_BLANK',
        'For _J=1 To 2',
        'Dreg(0)=_OWN',
        '_FREE=1 : _FREES=_FREES+1 : _OWN=-1',
        'If _OPEN=1',
        'Aga Screen Close',
        'Amos To Front',
        'For _J=1 To 3',
        '_IGNORE=Gfxcall(-270)',
        'If _CLOSE_RETURNED=1 and _POSTWAIT=3 and _OWN=-1 and _COPPER_TOUCHED=0',
        'Erase _BANK',
        '_BANK_HELD=1 : _BANK_HELD_ANY=1',
        'If _ERR<>0 and _BAD_CYCLE=0',
        'If _COP_ON_OK=1 and _COP_OFF_OK=1 and _HIDE_OK=2 and _SHOW_OK=7 and _DBS=3',
        'Print #1,"VERDICT ";_VERDICT$',
    )
    for anchor in anchors:
        if anchor not in bare:
            problems.append('Missing S0d guard: ' + anchor)
    for lvo, expected in ((-408, 1), (-420, 2), (-426, 1), (-414, 1), (-270, 1)):
        if bare.count(f'Gfxcall({lvo})') != expected:
            problems.append(f'Wrong graphics.library call count: LVO {lvo}')
    if bare.count('_COFF=Aga Copper Off') != 2:
        problems.append('Copper Off required during animation and cleanup')
    order = ('_GET=Gfxcall(-408)', 'Areg(2)=_IMAGE',
             '_IGNORE=Gfxcall(-426)', 'Areg(2)=_BLANK',
             '_IGNORE=Gfxcall(-414)', 'Aga Screen Close',
             '_IGNORE=Gfxcall(-270)', 'Erase _BANK')
    if all(s in bare for s in order):
        positions = [bare.index(s) for s in order]
        if positions != sorted(positions):
            problems.append('unsafe image/blank/free/close/TOF/erase ordering')
    for mode in ('INTERPRETED', 'RUNTIME', 'COMPILED', 'UNKNOWN'):
        name = f'M19_S0D_ROB_{mode}.TXT'
        if name not in text or len(name) > 30:
            problems.append('Invalid RAM log: ' + name)
    if not text.rstrip().endswith('End'):
        problems.append('Missing program End')
    return problems


class S0dSourceTests(unittest.TestCase):
    def test_only_one_source_and_all_guards(self):
        self.assertEqual([p.name for p in S0D.parent.glob('*.asc')], ['SPRITE_PROBE.asc'])
        self.assertEqual(inspect_s0d_source(S0D.read_bytes()), [])

    def test_chip_work_is_required(self):
        self.assertNotEqual(inspect_s0d_source(S0D.read_bytes().replace(b'Chip Work', b'Work')), [])

    def test_off_must_be_present(self):
        self.assertNotEqual(inspect_s0d_source(S0D.read_bytes().replace(b'Aga Copper Off', b'Aga Copper On')), [])

    def test_transparent_image_is_required(self):
        self.assertNotEqual(inspect_s0d_source(S0D.read_bytes().replace(b'Areg(2)=_BLANK', b'Areg(2)=_IMAGE')), [])

    def test_bank_erase_is_required(self):
        self.assertNotEqual(inspect_s0d_source(S0D.read_bytes().replace(b'Erase _BANK', b'Erase _IMAGE')), [])

    def test_release_must_be_guarded(self):
        self.assertNotEqual(inspect_s0d_source(S0D.read_bytes().replace(b'If _OWN>=0', b'If _OWN=-1')), [])

    def test_hardware_register_write_forbidden(self):
        self.assertNotEqual(inspect_s0d_source(S0D.read_bytes().replace(b'\nEnd\n', b'\nPoke $DFF096,1\nEnd\n')), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
