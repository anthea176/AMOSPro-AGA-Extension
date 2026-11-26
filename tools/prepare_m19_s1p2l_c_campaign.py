#!/usr/bin/env python3
"""Prepare one future P2l-c ASC in temporary storage, never activate it."""
import argparse
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARENT='a4ab96585d9e95c65dfaf42b76d9ba8b764c4e50e5cbd2d97d56a1947712d239'

def prepare(raw):
    assert sha256(raw).hexdigest()==PARENT
    crlf=b'\r\n' in raw
    s=raw.decode('ascii').replace('\r\n','\n')
    def edit(old,new):
        nonlocal s
        assert s.count(old)==1,old
        s=s.replace(old,new,1)
    edit("' M19 S1-P2l-b - diagnostic only, two launches.","' M19 S1-P2l-c - detailed idle refusal, two launches.")
    edit('M19_S1P2LB_DMA_DIAG_V1','M19_S1P2LC_IDLE_DETAIL_V1')
    edit('_LOG$="RAM:M19_S1P2LB_PHASE1.TXT"','_LOG$="RAM:M19_P2LC_P1_"+_MODE$+".TXT"')
    edit('_LOG$="RAM:M19_S1P2LB_PHASE2.TXT"','_LOG$="RAM:M19_P2LC_P2_"+_MODE$+".TXT"')
    s=s.replace('RAM:M19_S1P2LB_','RAM:M19_P2LC_')
    flags=[]
    for field,ok in (('START','_DS_OK'),('ACTIVE','_DA_OK'),('CLOSE','_DC_OK'),('FRONT','_DF_OK')):
        v='_DIAG_'+field
        flags.extend([ok+'=0',f'If {v}<=-180 and {v}>=-190',f'   {ok}=1','End If',
                      f'If {v}<=-257 and {v}>=-319',f'   {ok}=1','End If'])
        if field in ('START','ACTIVE'):
            edit(f'{v}<=-180 and {v}>=-190',ok+'=1')
        else:
            edit(f'{v}>-180 or {v}<-190',ok+'=0')
    edit("' Keep sequence and diagnostic verdicts independent.",
         "' Keep sequence and diagnostic verdicts independent.\n"+'\n'.join(flags))
    # Do not confuse a detailed refusal with evidence of DMA release.
    assert s.count('Aga Sprite Bank Free(-19000)')==4
    assert s.count('Aga Sprite Bank Free(29)')==1
    assert s.count('Aga Screen Close')==1
    assert 'DMA_FREE_PROVEN 0' in s
    assert all(len(line)<=200 for line in s.splitlines())
    for mode in ('RUNTIME','INTERPRETED','COMPILED','UNKNOWN'):
        assert len('M19_P2LC_P1_'+mode+'.TXT')<=30
    return (s.replace('\n','\r\n') if crlf else s).encode('ascii')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    raw=a.source.read_bytes()
    out=prepare(raw);a.output.write_bytes(out)
    assert a.source.read_bytes()==raw
    print('P2LC_ASC_PREPARED',len(out),sha256(out).hexdigest(),flush=True)
