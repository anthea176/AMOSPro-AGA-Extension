#!/usr/bin/env python3
"""Source-only, non-native checks for the S0 read-only AGA ViewPort AMOS probe.

The test cannot prove that AREG(5) contains a valid P2d context in WinUAE.
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


def inspect_s0b_source(raw: bytes) -> list[str]:
    """S0b is an OS channel probe only, not Sprite DMA or S1 runtime proof."""
    errors: list[str] = []
    if not raw.isascii() or b'\r' in raw:
        errors.append('S0b ASC must remain ASCII with LF only')
    code = raw.decode('ascii')
    lines = code.splitlines()
    if any(len(line) > 220 for line in lines):
        errors.append('S0b line exceeds 220 characters')
    bare = '\n'.join(line for line in lines if not line.lstrip().startswith("'"))
    if re.search(r'\b(?:MoveSprite|ChangeSprite|Sprite\s+On|Aga\s+Swap|Call|Execall|Poke)\b', bare, re.I):
        errors.append('S0b must not drive DMA or call arbitrary native code')
    anchors = (
        '_VIEWPORT=_SCREEN+44',
        '_MODEWORD=Deek(_VIEWPORT+32)',
        '(_MODEWORD and $4000)',
        'If Length(_I)=0',
        'Trap Reserve As Work _BANK,12',
        '_PTR=Start(_BANK)',
        'Doke _PTR+10,$FFFF',
        'Areg(0)=_PTR : Dreg(0)=-1',
        '_NUM_SHOW=_GET_SHOW and $FFFF',
        '_NUM_HIDE=_GET_HIDE and $FFFF',
        'If _NUM_SHOW<>65535',
        'If _NUM_HIDE<>65535',
        '_OWN=_NUM_SHOW',
        '_OWN=_NUM_HIDE',
        'If _OWN>=0',
        'Erase _BANK',
        'Aga Screen Close',
        'Amos To Front',
        'Print #1,"CLOSE_RETURNED ";_CLOSE_RETURNED',
    )
    for a in anchors:
        if a not in bare:
            errors.append('S0b source anchor missing: ' + a)
    if bare.count('Gfxcall(-408)') != 2:
        errors.append('S0b must attempt exactly two GetSprite calls')
    if bare.count('Gfxcall(-414)') != 3:
        errors.append('S0b must guard FreeSprite twice plus cleanup')
    for mode in ('INTERPRETED', 'RUNTIME', 'COMPILED', 'UNKNOWN'):
        name = f'M19_S0B_SPR_{mode}.TXT'
        if name not in code or len(name) > 30:
            errors.append('Invalid S0b RAM log name: ' + name)
    if not code.rstrip().endswith('End'):
        errors.append('S0b must terminate with End')
    return errors


class S0bSourceTests(unittest.TestCase):
    def test_one_reusable_source_and_all_guards(self):
        self.assertEqual([p.name for p in S0B.parent.glob('*.asc')], ['SPRITE_PROBE.asc'])
        self.assertEqual(inspect_s0b_source(S0B.read_bytes()), [])

    def test_reject_wrong_getsprite_offset(self):
        altered = S0B.read_bytes().replace(b'Gfxcall(-408)', b'Gfxcall(-402)')
        self.assertNotEqual(inspect_s0b_source(altered), [])

    def test_reject_missing_release_path(self):
        altered = S0B.read_bytes().replace(b'If _OWN>=0', b'If _OWN=-1')
        self.assertNotEqual(inspect_s0b_source(altered), [])

    def test_reject_dma_operation(self):
        altered = S0B.read_bytes().replace(b'\nEnd\n', b'\nChangeSprite\nEnd\n')
        self.assertNotEqual(inspect_s0b_source(altered), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
