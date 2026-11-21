#!/usr/bin/env python3
"""M19 B8 sole ASC static contract; NOT actual WinUAE/AMOS Compiler validation."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import re
import sys

NAME="M19_B8_BOB_CLEAR_UPDATE_BC_01.asc"
LIB="7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42"
SIZE=27351
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
    assert LIB in s and 'RAM:M19_P1E_BANK_EDIT.TXT' in s
    assert 'Dim _SEEN(1)' in s and '_SEEN(0)=0 : _SEEN(1)=0' in s
    assert 'NO TIMER OR BENCHMARK' in s
    assert len(re.findall(r'\b_CLEAR=Aga Bob Clear',s))==1
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
    assert 'P1e CANDIDATE SHA256' in s
    edit=s[s.index("' P1e: delete image"):s.index('Next _ED_STEP')]
    assert edit.index('Aga Del Bob(_BANK2,1,2)') < edit.index('_ED_UP=Aga Bob Update')
    assert edit.index('_ED_UP=Aga Bob Update') < edit.index('Gosub _EDIT_PROBE') < edit.index('Gosub _DO_SWAP')
    assert 'Length(_BANK2)<>32' in edit and edit.count('Aga Ins Bob(_BANK2,3,8,2,8)') == 3
    assert '_ED_FRAMES<>3 or _ED_PIXELS<>9 or _ED_REJECTS<>2' in s
    assert 'Aga Bob Draw' not in s
    assert 'Trap Load "M19_P1B_HOTSPOT_BANK26.abk",_HOTBANK' in s
    assert 'Deek(_HOT_PTR+60)<>4 or Deek(_HOT_PTR+62)<>3' in s
    assert 'For _HPHASE=1 To 4' in s
    assert '_HX=32767 : _HY=32767' in s
    assert 'If _HOT_STEPS<>4 or _HOT_CLEAR_OK<>4 or _HOT_UPD_OK<>4' in s
    assert 'If _HOT_SWAP_OK<>4 or _HOT_Q_OK<>12' in s
    assert 'If _CLOSE_CALLED=1 and _BANKS_ERASED=4' in s
    assert 'HOTSPOT_FRAMES_OK' in s and 'HOTSPOT_GETTERS_OK' in s
    assert 'HOTSPOT_LOAD_ERR' in s
    assert 'If _ERR=0 and _PR_STEP>0' in s  # Probe the real default on first frame.
    assert 'For _PR_STEP=0 To 7' in s and '_PR_MODE=Int(_PR_STEP/2)' in s
    assert 'For _LIMIT_STEP=0 To 7' in s and '_LIMIT_CASE=Int(_LIMIT_STEP/2)' in s
    for call in ('Aga Limit Bob(0,113,103,1,1)', 'Aga Limit Bob(1,114,103,1,1)',
                 'Aga Limit Bob(0,0,0,1,1)', 'Aga Limit Bob(0,0,0,0,0)',
                 'Aga Limit Bob(0,113,103,0,1)'):
        assert call in s
    phases = s[s.index('For _LIMIT_STEP=0 To 7'):s.index('Next _LIMIT_STEP')]
    assert phases.index('_LIMIT_CL=Aga Bob Clear') < phases.index('_LIMIT_UP=Aga Bob Update')
    assert phases.index('_LIMIT_UP=Aga Bob Update') < phases.index('Gosub _LIMIT_PROBE') < phases.index('Gosub _DO_SWAP')
    assert '_LIMIT_FRAMES<>8 or _LIMIT_PIXELS<>24 or _LIMIT_REJECTS<>8' in s
    assert '_LIMIT_MASK=128' in s and '_LIMIT_MASK=_LIMIT_MASK/2' in s
    from build_m19_p1b_hotspot_fixture import ROWS
    # P1c mode 1 draws opaque Bob 2 before masked Bob 1, using logical Y.
    # Bob 1 origins and mask match the established priority phases.
    actual = []
    for case in range(4):
        colors = []
        for x in (112, 113, 114):
            global_ok = case == 3 or (case in (0, 1) and x == 113)
            bob1_ok = global_ok and (case != 1 or x == 114)
            colors.append((ROWS[2][x-112] or 5) if bob1_ok else (5 if global_ok else 1))
        actual.append(tuple(colors))
    assert actual == [(1, 4, 1), (1, 5, 1), (1, 1, 1), (5, 4, 5)]

    assert '_PR_SET=Aga Bob Priority(_PR_MODE)' in s
    assert '_PR_NEG=Aga Bob Priority(-1)' in s and '_PR_HIGH=Aga Bob Priority(4)' in s
    assert 'Aga Bob 1,116,104,1' in s and 'Aga Bob 2,112,102,1' in s
    assert 'Aga C Block Capture(_PROBE_BANK,112,103,8,1,0)' in s
    assert '(_PR_BYTE and 64)<>0' in s and 'Peek(_PR_PTR+40+2*_PR_PLANE)' in s
    assert '_PR_EXPECT=5' in s and '_PR_EXPECT=4' in s
    assert '_PR_CAPTURE_OK<>8 or _PR_PIXELS_OK<>8 or _PR_SWAP_OK<>8' in s
    assert '_PR_SET_OK<>7 or _PR_REJECT_OK<>16 or _PR_DEFAULT_OK<>1' in s
    from build_m19_p1b_hotspot_fixture import PIXELS, VISIBLE
    assert VISIBLE[2*8+1] and PIXELS[2*8+1] == 4  # Visible pixel at (113,103).
    assert 'Aga Blit Fill(62,16,37,8,5)' in s and 'No AGA Bob Mask 1' in s
    phases=s[s.index('For _PR_STEP=0 To 7'):s.index('Next _PR_STEP')]
    assert phases.index('_PR_CLEAR=Aga Bob Clear') < phases.index('_PR_UP=Aga Bob Update')
    assert phases.index('_PR_UP=Aga Bob Update') < phases.index('Gosub _PRIORITY_PIXEL') < phases.index('Gosub _DO_SWAP')

    regression = s[:s.index('Next _STAGE')]
    assert regression.count('Aga Bob Off 1')==1 and regression.count('Aga Bob Off 2')==1
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
