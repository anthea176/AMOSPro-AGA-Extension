#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2g P1b: expose the exact native P1a five-integer entry via AP20 chain.

Read-only source build. Candidate not installed, real AMOS grammar execution
and Compiler remain separate gates. Official sources: +Compact.s, +Verif.s
VerC4, extensions/Intuition-41.95/Intuition/src/itokens.s.
"""
import argparse
import json
from hashlib import sha1,sha256
from struct import pack
from pathlib import Path
from audit_ap20 import inspect,parse,walk_tokens,token,token_role_issues,FormatError
from compiler_relocation import unpack_ap20,repack_ap20,GETP
from build_m19_s2g_in_memory import build_s2g,protected,PRIVATE_ENTRY

P1A_SHA='e45e5cc3ba951f2216d50c3a752a6bc9d0a6d4fec9e13ee5cec59b3df1a37de0'
SIG4='00,0,0,0'
SIG5='00,0,0,0,0'

def overload(tokens,index):
    rows=list(walk_tokens(tokens))
    target=[i for i,row in enumerate(rows) if row['name']=='aga sprite']
    assert len(target)==1
    i=target[0];row=rows[i]
    assert row['signature']==SIG4 and row['instruction']==1
    start,end=row['offset'],rows[i+1]['offset'] if i+1<len(rows) else len(tokens)-6
    assert tokens[start:end]==token('aga sprite',1,row['function'],SIG4)
    head=token('!aga sprite',1,row['function'],SIG4).replace(b'\xff',b'\xfe')
    # Function-only entries keep the same instruction sentinel as the parent.
    tail=pack('>HH',1,index)+b'\x80'+SIG5.encode('ascii')+b'\xff'
    tail+=bytes(len(tail)%2)
    out=tokens[:start]+head+tail+tokens[end:]
    parsed=list(walk_tokens(out))
    assert len(parsed)==len(rows)+1
    before=[(r['name'],r['instruction'],r['function'],r['signature']) for r in rows]
    after=[(r['name'],r['instruction'],r['function'],r['signature']) for r in parsed
           if not r.get('continuation')]
    assert before==after
    assert parsed[i]['more'] and parsed[i+1]['continuation']
    assert parsed[i+1]['signature']==SIG5 and parsed[i+1]['function']==index
    assert parsed[i+1]['name']=='aga sprite' and not parsed[i+1]['more']
    assert out[:start]==tokens[:start] and out[start+len(head)+len(tail):]==tokens[end:]
    return out

def grammar_tests():
    dummy=b'\0\1\0\0\x80\xff'
    original=dummy+token('aga sprite',1,208,SIG4)+token('aga sprite off',1,210,'00')+bytes(6)
    result=overload(original,PRIVATE_ENTRY)
    rows=list(walk_tokens(result))
    assert [(r['name'],r['signature'],r['function']) for r in rows[1:]]==[
        ('aga sprite',SIG4,208),('aga sprite',SIG5,PRIVATE_ENTRY),('aga sprite off','00',210)]
    head,tail=rows[1],rows[2]
    for bad in (
        result[:tail['offset']]+bytes(6),
        result[:head['offset']]+result[tail['offset']:],
        result[:tail['offset']]+token('other',1,PRIVATE_ENTRY,SIG5)+result[rows[3]['offset']:],
        result[:tail['offset']+5]+b'1'+result[tail['offset']+6:],
        result[:tail['offset']+5]+SIG4.encode()+b'\xff'+bytes(6)
    ):
        try:list(walk_tokens(bad))
        except FormatError:pass
        else:raise AssertionError('invalid overload accepted')
    print('S2G_OVERLOAD_GRAMMAR_STATIC_PASS',flush=True)

def build_s2g_public(vasm):
    before=protected()
    private,info=build_s2g(vasm)
    assert sha256(private).hexdigest()==P1A_SHA
    tok,parts,title=unpack_ap20(private)
    assert parts[PRIVATE_ENTRY-1]==GETP
    nt=overload(tok,PRIVATE_ENTRY)
    ntit=title.replace(b'0.15.0-alpha.4.p1a',b'0.15.0-alpha.4')
    assert ntit!=title and len(ntit)%2==0
    image=repack_ap20(private,nt,parts,ntit)
    assert unpack_ap20(image)==(nt,parts,ntit)
    a=inspect(parse(image))
    assert not a['issues'] and not token_role_issues(a['tokens'])
    named=[r for r in a['tokens'] if r['signature']]
    assert len(named)==106 and len({r['name'] for r in named})==105
    assert len(parts)==221 and protected()==before
    return image,dict(info,sha256=sha256(image).hexdigest(),bytes=len(image),
        git_blob=sha1(f'blob {len(image)}'.encode()+b'\0'+image).hexdigest(),
        private_sha=P1A_SHA,commands=105,signatures=106,public_overload=True,
        new_group=216,remapped={'aga bank image info':218,'aga bank image capture':220},
        installable=False,runtime_tested=False,compiler_tested=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--vasm',type=Path,required=True)
    a=p.parse_args()
    grammar_tests()
    image,meta=build_s2g_public(a.vasm)
    other,second=build_s2g_public(a.vasm)
    assert image==other and meta==second
    print('S2G_PUBLIC_EXACT_BUILD_PASS '+json.dumps(meta,sort_keys=True),flush=True)
