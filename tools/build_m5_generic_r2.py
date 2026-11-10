"""R2 0.5.1: synchronize pending bitmap blits before CPU decoding.

Rebuilt from the authoritative R5 archive by the common generator. Only the
loader's pre-write barrier differs from Generic R1; no palette/decode/DB edits.
R1 remains archived; --promote updates the current experimental candidate after tests.
"""
import hashlib
import json
import argparse
from build_m5_generic import ROOT, build as generate
from audit_ap20 import parse

DEST=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.5.1_GENERIC_R2.Lib'
OUT_SHA='18fdfd059bd6f15f5a0d42eeb9d628a71ee4110849d8bb781a67db9575f93803'

def build():
    raw,report=generate(synchronize=True)
    r1,_=generate(); before=parse(r1); after=parse(raw)
    for i,n in enumerate(before.jumps):
        if i!=13:
            assert before.code[before.starts[i]:before.starts[i]+2*n]==after.code[after.starts[i]:after.starts[i]+2*after.jumps[i]]
    assert len(raw)==6444 and hashlib.sha256(raw).hexdigest()==OUT_SHA
    report['delta_from_r1']='WaitBlit before CPU bitplane writes; palette and decoder unchanged'
    return raw,report

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--promote',action='store_true'); args=parser.parse_args()
    raw,report=build(); assert build()[0]==raw
    DEST.write_bytes(raw)
    (ROOT/'docs/GENERIC_R2_BUILD.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if args.promote:
        from test_m5_generic_r2 import run
        run()
        (ROOT/'dist/AMOSPro_AGA.Lib').write_bytes(raw)
    print(DEST.name,len(raw),report['sha256'])
