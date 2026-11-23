#!/usr/bin/env python3
"""Deterministic generic AMOS DATA AGSP v1 single-image fixture (no DMA)."""
from __future__ import annotations
from pathlib import Path
import argparse
from m19_s1_agsp_bank import empty_bank, make_abk, parse_abk, put_capture

DEST = Path(__file__).resolve().parents[1] / 'tests/proto/agsp_bank/AGSP_1IMG_16X16.ABK'


def expected_fixture():
    pixels=bytes(((x+y)%4 for y in range(16) for x in range(16)))
    # Source indices 0=transparent, 1..3 -> RGB24. Remaining 252 palette slots exist.
    cmap=bytes(3) + bytes((255,80,56,237,198,66,61,199,182)) + bytes(252*3)
    payload=put_capture(empty_bank(),1,pixels,16,16,0,0,16,16,cmap,0,mode='s1')
    return make_abk(10,payload)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--check',action='store_true')
    p.add_argument('--out',type=Path,default=DEST)
    args=p.parse_args()
    expected=expected_fixture()
    number, flags, bank = parse_abk(expected)
    assert (number,flags,len(bank.raw),bank.image(1).opaque_count)==(10,1,192,3)
    if args.check:
        assert args.out.read_bytes()==expected, 'AGSP test fixture differs from the pinned format model'
        print('AGSP_FIXTURE_BYTE_EXACT_PASS',len(expected),args.out)
    else:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_bytes(expected)
        print('AGSP_FIXTURE_WRITTEN',len(expected),args.out)


if __name__=='__main__': main()
