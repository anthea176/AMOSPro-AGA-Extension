#!/usr/bin/env python3
"""M19 B8 sole ASC static contract; NOT actual WinUAE/AMOS Compiler validation."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import re
import sys

NAME="M19_B8_BOB_CLEAR_UPDATE_BC_01.asc"
LIB="2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4"
SIZE=17566
STAGES=(2,1,0,2,4,8,16,64,16)


def model():
    seen=[False,False]
    page=0
    clear_count=update_count=swap_count=off_count=0
    for stage,expected_bobs in enumerate(STAGES,1):
        off_count+=(1 if stage in (2,3) else 48 if stage==9 else 0)
        for step in range(1,46):
            if seen[page]:
                clear_count+=1
            x=(step*5+stage*13)%288
            assert 0<=x<=287
            update_count+=1
            seen[page]=True
            swap_count+=1
            page=1-page
    assert (seen,clear_count,update_count,swap_count,off_count)==(
        [True,True],403,405,405,50)
    return clear_count,update_count,swap_count,off_count


def verify(path:Path):
    data=path.read_bytes()
    assert len(data)==SIZE,("B8 ASC length",len(data),SIZE)
    s=data.decode("ascii")
    assert s.endswith("Return\n") and max(map(len,s.splitlines()))<=200
    assert LIB in s and 'RAM:M19_P1B_HOTSPOT.TXT' in s
    assert 'Dim _SEEN(1)' in s and '_SEEN(0)=0 : _SEEN(1)=0' in s
    assert 'NO TIMER OR BENCHMARK' in s
    assert s.count('_CLEAR=Aga Bob Clear')==1
    assert s.count('_UPDATE=Aga Bob Update')==1
    assert s.count('Aga Bob Bank Free _BANK1')==2
    assert s.count('Aga Bob Bank Free _BANK2')==1
    assert 'Aga Bob 1,124,88,1' in s
    assert s.count('_BFC=Aga Bob Clear')==1
    assert s.count('_BFU=Aga Bob Update')==1
    assert s.count('Gosub _QUERY_CHECK')==14
    assert 'QUERY_CASES' in s and 'QUERY_VALUES_OK' in s and 'QUERY_VALUES_BAD' in s
    assert 'If _Q_CASES<>14 or _Q_OK<>42 or _Q_BAD<>0' in s
    assert s.count('Aga X Bob(_QID)')==1
    assert s.count('Aga Y Bob(_QID)')==1
    assert s.count('Aga I Bob(_QID)')==1
    assert s.index('_QX=Aga X Bob(_QID)') < s.index('_QY=Aga Y Bob(_QID)') < s.index('_QI=Aga I Bob(_QID)')
    assert 'P1b CANDIDATE SHA256' in s
    assert 'Aga Bob Draw' not in s
    assert 'Trap Load "M19_P1B_HOTSPOT_BANK26.abk",_HOTBANK' in s
    assert 'Deek(_HOT_PTR+60)<>4 or Deek(_HOT_PTR+62)<>3' in s
    assert 'For _HPHASE=1 To 4' in s
    assert '_HX=32767 : _HY=32767' in s
    assert 'If _HOT_STEPS<>4 or _HOT_CLEAR_OK<>4 or _HOT_UPD_OK<>4' in s
    assert 'If _HOT_SWAP_OK<>4 or _HOT_Q_OK<>12' in s
    assert 'If _CLOSE_CALLED=1 and _BANKS_ERASED=3' in s
    assert 'HOTSPOT_FRAMES_OK' in s and 'HOTSPOT_GETTERS_OK' in s
    assert 'HOTSPOT_LOAD_ERR' in s
    assert s.count('Aga Bob Off 1')==1 and s.count('Aga Bob Off 2')==1
    assert 'For _ID=17 To 64' in s
    assert 'Make AGA Bob Mask 1,0' in s and 'No AGA Bob Mask 1' in s
    assert 'If _PRG=-1\n   _MODE$="COMPILED"\nEnd If' in s
    assert 'If _PRG=1\n   _MODE$="RUNTIME"\nEnd If' in s
    assert 'If _MODE$="UNKNOWN"\n   _ERR=1 : Goto _CLEANUP\nEnd If' in s
    assert '_CLEAR_OK=403 and _UPDATE_OK=405' in s
    assert '_BF_CALLS<>3 or _BF_CLEAR_OK<>3 or _BF_UPD_OK<>3' in s
    assert '_BF_SWAP_OK<>3 or _BF_REARM<>1' in s
    f=s[s.index('For _STEP=1 To 45'):s.index('   Next _STEP')]
    assert f.index('_CLEAR=Aga Bob Clear')<f.index('Gosub _DYNAMIC_DECOR')
    assert f.index('Gosub _DYNAMIC_DECOR')<f.index('Aga Bob _ID,_X,_Y,1')
    assert f.index('Aga Bob _ID,_X,_Y,1')<f.index('_UPDATE=Aga Bob Update')
    assert f.index('_UPDATE=Aga Bob Update')<f.index('Gosub _DO_SWAP')
    assert '_SEEN(_PAGE)=1' in f and '_PAGE=1-_PAGE' in f
    assert 'Aga Wait Vbl' not in f, 'Diagnostic VBL workaround must NOT be shipped as campaign'
    assert '_COPY_TILE_RECT' not in f
    assert 'If _ERR=0 and _SEEN(_PAGE)=1' in f
    assert '_CLEAR_BAD=_CLEAR_BAD+1 : _ERR=18' in f
    assert '_UPDATE_BAD=_UPDATE_BAD+1 : _ERR=14' in f
    assert s.index('_CLEANUP:')<s.index('Aga Screen Close',s.index('_CLEANUP:'))
    assert s.index('Aga Screen Close',s.index('_CLEANUP:'))<s.index('Erase _BANK1',s.index('_CLEANUP:'))
    for field in ('CLEAR_OK','CLEAR_FAILS','UPDATE_OK','UPDATE_FAILS',
                  'FRAMES_OK','STAGES_OK','VERDICT','RUN_MODE','PRG_STATE',
                  'CLOSE_RETURNED','BANKS_ERASED','BANK_FREE_CALLS',
                  'BANK_FREE_CLEAR_OK','BANK_FREE_UPDATE_OK',
                  'BANK_FREE_SWAP_OK','BANK_FREE_REARM'):
        assert 'Print #1,"'+field+' ' in s,(field,'RAM log missing')
    assert 'Trap Open Out 1,_LOG$' in s and 'Trap Close 1' in s
    executable='\n'.join(x.split("'",1)[0] for x in s.splitlines())
    assert not re.search(r'\bTimer\b|\bFPS\b|Erase All|\bThen\b|\bElseIf\b',executable,re.I)
    for name,end in (('If','End If'),('For','Next'),('Repeat','Until')):
        assert len(re.findall(r'(?m)^\s*'+re.escape(name)+r'\b',s))==len(
            re.findall(r'(?m)^\s*'+re.escape(end)+r'\b',s)),name
    assert model()==(403,405,405,50)
    tail=s[s.index('Next _STAGE'):s.index('_CLEANUP:')]
    assert tail.index('Aga Bob Bank Free _BANK1')<tail.index('_BFC=Aga Bob Clear')
    assert tail.index('_BFC=Aga Bob Clear')<tail.index('_BFU=Aga Bob Update')
    assert tail.index('_BFU=Aga Bob Update')<tail.index('Gosub _DO_SWAP')
    assert tail.index('Aga Bob Bank Free _BANK2')<tail.index('Aga Bob 1,124,88,1')
    print('M19 B8 ASC PREFLIGHT PASS',path,'SHA256',sha256(data).hexdigest(),
          'bytes',len(data),'403 Clear / 405 Update / 405 Swap / 50 Off modelled')


if __name__=='__main__':
    verify(Path(sys.argv[1]) if len(sys.argv)>1 else Path('tests/current')/NAME)
