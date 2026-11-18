#!/usr/bin/env python3
"""Verify immutable R88 Gate-A test fixtures before archiving to main.

R88 is an experimental, unpromoted candidate. These checks do NOT confer
WinUAE Runtime/Compiler (Gates B/C) approval.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

R84_SHA = '46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d'
R87_SHA = '02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302'
R88_SHA = '69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc'
R88_NAME = 'AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib'
FILES = {
    R88_NAME: (75040, '69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc'),
    'AGAPIC_P28_V1_BANK10.abk': (424, 'ec0dab3ddca999ae1cad8908ea020a46cac3e98409d8d0a4716e39ba5c40a1d7'),
    'AGPC_P28_V1_BANK11.abk': (380, 'e32a2263f44bf22412bc0dd4cca72eb98381cf80865a9780a9a51256e88ff0b8'),
    'AGAPIC_P28_V2_BANK12.abk': (1224, '3c2c3d880ea1b9ca46ee5e748f854493ca40589bef970e16e6ceb8abf0dddaaf'),
    'AGPC_P28_V2_BANK13.abk': (380, 'dd3c4e32baa2a5e5e8408c5cbf8a2a53842403d077384b2e4b537e99386d996f'),
}


def verify(path: Path, name: str) -> None:
    size, digest = FILES[name]
    raw = path.read_bytes()
    assert len(raw) == size, f'Unexpected size for {path}: {len(raw)} (expected {size})'
    actual = sha256(raw).hexdigest()
    assert actual == digest, f'Unexpected SHA256 for {path}: {actual}'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--bundle', type=Path, help='Check CI-generated inputs before archival')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.bundle is not None:
        src = args.bundle.resolve()
        # Raw bundle uses the install-facing basename, but only here.
        verify_raw = src / 'AMOSPro_AGA.Lib'
        raw = verify_raw.read_bytes()
        assert (len(raw), sha256(raw).hexdigest()) == FILES[R88_NAME], verify_raw
        for filename in FILES:
            if filename != R88_NAME:
                verify(src / filename, filename)
    else:
        verify(root / 'dist/experimental' / R88_NAME, R88_NAME)
        for filename in FILES:
            if filename != R88_NAME:
                verify(root / 'tests/fixtures/m19_p28' / filename, filename)
    for filename, length, digest in [
        ('dist/AMOSPro_AGA.Lib', 102400, '242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6'),
        ('dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib', 73184, R87_SHA),
        ('dist/AMOSPro_AGA_LAST_GOOD.Lib', 67904, R84_SHA),
    ]:
        path = root / filename
        if path.exists():
            raw = path.read_bytes()
            assert len(raw) == length and sha256(raw).hexdigest() == digest, path
    print('P2.8 ARCHIVE INTEGRITY PASS: 5 byte-exact artifacts; R88 unpromoted, B/C NOT TESTED')


if __name__ == '__main__':
    main()
