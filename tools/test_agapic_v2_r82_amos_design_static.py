#!/usr/bin/env python3
"""R82 WinUAE design-only ASC + ABK deterministic structural preflight.

Checks source blocks, required v1/v2 tests, RAM logging and byte-exact
fixtures without AMOS/WinUAE. NOT a runtime Gate B validation.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from m16_agapic_v2_winuae_fixture import samples,OUT,MODE_ID
from m16_agapic_v2 import parse_abk_any
from test_current_amos_blocks import scan
from test_current_ram_log import verify as verify_ram

ROOT=Path(__file__).resolve().parents[1]
ASC=ROOT/'tests/design/AGAPIC_R82_V2_BANK_PALETTE_01.asc'
EXPECTED={
 'R82_AGAPIC_V2_BANK10.abk':'11a5102f05bfda8372ccdcf2a5b8eec2c5d1a5c80d2cbb83b5d563e0abc667f0',
 'R82_AGAPIC_V1_BANK12.abk':'09b3badeec687732010c00c2152fa51df609d2000d64e915a64f4dbd10fa71e8',
}


def main():
    assert MODE_ID==0x00021000
    assert OUT==ROOT/'tests/design'
    source=ASC.read_bytes().decode('ascii')
    issues=scan(ASC)
    assert issues==[],('AMOS block-syntax heuristic',issues)
    verify_ram(source)
    checks=(
      'Load "R82_AGAPIC_V2_BANK10.abk",10',
      'Load "R82_AGAPIC_V1_BANK12.abk",12',
      'Reserve As Data 11,1568',
      '_OPEN=Aga Screen Open(320,256,256,$00021000)',
      '_DB=Aga Double Buffer',
      'Aga Bank Palette Init(11,2)',
      'Aga Bank Palette Apply(10,0)',
      'Aga Bank Palette Capture(11,0)',
      'Aga Bank Palette Capture(11,1)',
      'Aga Bank Palette Apply(11,0)',
      'Aga Bank Palette Fade(11,1,5)',
      'Aga Bank Palette Fade(10,0,5)',
      'Aga Bank Palette Apply(10,1)',
      'Aga Bank Palette Fade(10,1,3)',
      'Aga Bank Palette Apply(12,0)',
      'Aga Bank Palette Init(10,1)',
      'Aga Bank Palette Capture(10,0)',
      'Aga Bank Image Draw(10,12,28,0)',
      'Aga Bank Image Draw(12,208,28,0)',
      'Aga Image Draw(Start(10),Length(10),12,118,0)',
      'Aga Image Region(10,8,8,48,32,126,145,0)',
      'Aga Image Region(12,8,8,48,32,206,145,1)',
      '_SWAP_OK=Aga Swap',
      'Aga Screen Close',
      'RAM:AGAPIC_R82_INTERPRETED.TXT',
      'RAM:AGAPIC_R82_COMPILED.TXT',
      'CLOSE_RETURNED',
      'End',
    )
    for fragment in checks:
        assert fragment in source,('missing expected native API scenario',fragment)
    assert source.count('CLEANUP:')==1
    assert source.index('Aga Screen Open')<source.index('Aga Bank Palette Apply(10,0)')
    assert source.index('Aga Bank Palette Apply(10,0)')<source.index('Aga Bank Image Draw(10,12,28,0)')
    assert source.rstrip().endswith('End')
    produced=samples()
    assert set(produced)==set(EXPECTED)
    for name,generated in produced.items():
        path=OUT/name
        assert path.read_bytes()==generated,('fixture drift',name)
        assert sha256(generated).hexdigest()==EXPECTED[name]
        bank,flags,img=parse_abk_any(generated)
        assert (bank,img.version)==((10,2) if 'V2' in name else (12,1))
        assert (img.image.width,img.image.height,img.image.depth)==(96,64,8)
        if img.version==2:
            assert img.mode_id==MODE_ID and len(img.palette)==768
        else:
            assert img.mode_id is None and img.palette is None
    print('R82 AGAPIC v1/v2 AMOS DESIGN STATIC PASS:',len(checks),
          'API/source checks + 2 byte-exact fixture hashes + RAM log')
    print('The ASC is in tests/design/, NOT an active WinUAE Gate B test.')


if __name__=='__main__': main()
