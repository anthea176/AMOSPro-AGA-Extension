#!/usr/bin/env python3
"""Source-only, non-native checks for the S0 read-only AGA ViewPort AMOS probe.

The test cannot prove that AREG(5) contains a valid P2d context in WinUAE.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ASC = ROOT / 'tests/sprite_s0/M19_S0_VIEWPORT_PROBE.asc'


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
