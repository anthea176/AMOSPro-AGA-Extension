#!/usr/bin/env python3
"""R8 static 68000/code and state-machine property tests.

IMPORTANT: This is NOT a Unicorn CPU execution test. All R8 CPU and real
AmigaOS/WinUAE tests are still required before publishing this Lib for use.
"""
from pathlib import Path
import sys, json, random
from ap20_utils import split,digest
from build_r7_reconstruction import build as build_r7
from build_db_safe_r8 import build,MAX_VBL

ROOT=Path(__file__).resolve().parents[1]
R8,manifest=build()
R7=build_r7()
_,prev,_=split(R7)
_,ss,_=split(R8)
results={}

def test(name,fn):
    fn();results[name]='PASS'

def cond(p,msg):
    assert p,msg

def canary():
    assert digest(R7)=='e6dd32ceda1181ef3172dfb242a1d4fc93656c6788023d7b1333dc2561ed3dce'
    assert digest(R8)==manifest['sha256']
    assert len(R8)==manifest['size']
    assert len(ss)==19

test('r7_baseline_sha_and_r8_deterministic',canary)

def code_delta():
    assert [i for i in range(19) if ss[i]!=prev[i]]==[0,8,11,17,18]
    for i in (1,2,3,4,5,6,7,9,10,12,13,14,15,16):assert ss[i]==prev[i],i
    assert ss[8].endswith(b'GetP')
    assert ss[11].endswith(b'GetP')
    assert ss[10]==prev[10]
    assert ss[0][:0x40]==prev[0][:0x40]
    assert ss[0][0x1a0:0x1c8]==prev[0][0x1a0:0x1c8]==bytes(40)
    assert ss[0][0x1c8:] and ss[0][0x40:0x44]!=prev[0][0x40:0x44]
    for i in (17,18):
        # Only the old BRA.W to cleanup was changed inside R7 keyboard body.
        assert ss[i][:0x7e]==prev[i][:0x7e]
        assert ss[i][0x82:len(prev[i])]==prev[i][0x82:]
        assert ss[i][0x7e:0x82]!=prev[i][0x7e:0x82]

test('r7_unchanged_all_non_swap_code_and_loader',code_delta)

def patched_jump_correct():
    def branched(s,pos):
        assert s[pos:pos+2]==bytes.fromhex('6000')
        return pos+2+int.from_bytes(s[pos+2:pos+4],'big',signed=True)
    assert branched(ss[0],0x40)==len(prev[0])
    assert branched(ss[8],8)==len(prev[8])-4
    assert branched(ss[17],0x7e)==len(prev[17])
    assert branched(ss[18],0x7e)==len(prev[18])
    assert branched(ss[0],0x62)==0x9e
    assert ss[0].count(bytes.fromhex('4eaefe80'))==0  # old init WaitPort removed
    for i in (8,11,17,18):
        assert bytes.fromhex('4eaefe80') not in ss[i]
        assert bytes.fromhex('4eaefec2') not in ss[i]
    for i in (0,8,11,17,18):
        assert bytes.fromhex('4eaefef2') in ss[i] if i!=11 else True

test('all_preflight_branches_and_no_waitport',patched_jump_correct)

def pending_bit_code():
    poll=bytes.fromhex('2c2c001402860000000308060000')
    assert ss[11].count(poll)==1
    for i in (0,8,17,18):assert ss[i].count(poll)==1
    assert ss[11].count(bytes.fromhex('297c000000030014'))==1
    assert ss[11].count(bytes.fromhex('29470008'))==1
    assert bytes.fromhex('08860000') in ss[11]
    assert bytes.fromhex('08860001') in ss[11]
    assert bytes.fromhex('4eaefe86') not in ss[11]  # no ReplyMsg on DB responses
    for i in (0,8,17,18):
        helper=ss[i][len(prev[i]):] if i in (0,17,18) else ss[i][len(prev[i])-4:-4]
        assert bytes.fromhex('4eaefe86') not in helper
        assert bytes.fromhex('0c840000012d') in helper
        assert bytes.fromhex('4eaefef2') in helper
    assert bytes.fromhex('0c840000012d') in ss[8]

test('pending_flags_exactly_two_and_no_db_replymsg',pending_bit_code)

class DBModel:
    def __init__(self):
        self.front=0;self.pending=0
        self.safe=[];self.disp=[]
        self.received_safe=0;self.received_disp=0
        self.swap_success=0;self.close_success=0
        self.window_open=True;self.screen_open=True
        self.breaks=0;self.vbl=0
    def reply_safe(self):
        if self.pending&1:self.safe.append('safe')
    def reply_disp(self):
        if self.pending&2:self.disp.append('disp')
    def poll(self):
        if self.pending&1 and self.safe:
            msg=self.safe.pop(0);assert msg=='safe'
            self.received_safe+=1;self.pending&=~1
        if self.pending&2 and self.disp:
            msg=self.disp.pop(0);assert msg=='disp'
            self.received_disp+=1;self.pending&=~2
        return self.pending
    def swap(self,success=True):
        if not self.screen_open:return False
        if self.poll():return False
        if not success:return False
        self.front ^=1;self.pending=3;self.swap_success+=1;return True
    def finish(self,ctrl=False,arrivals=None):
        if arrivals is None:arrivals={}
        for frame in range(MAX_VBL):
            arrivals.get(frame,lambda:None)()
            if not self.poll():
                self.window_open=False;self.screen_open=False
                self.close_success+=1
                if ctrl:self.breaks+=1
                return True
            self.vbl+=1
        assert self.window_open and self.screen_open
        assert self.breaks==0
        return False


def model_corner_cases():
    m=DBModel();assert m.swap();assert m.pending==3
    assert not m.swap(), 'must not overwrite pending before replies'
    m.reply_safe();assert not m.swap() and m.pending==2
    m.reply_disp();assert m.swap() and m.pending==3
    assert m.front==0
    m.reply_disp();m.reply_safe();assert m.finish(ctrl=True)
    assert m.breaks==1 and not m.window_open and not m.screen_open
    assert m.received_safe==2 and m.received_disp==2
    t=DBModel();assert t.swap(False)==False and t.pending==0
    assert t.finish() and t.close_success==1
    t=DBModel();assert t.swap();assert t.finish(ctrl=True)==False
    assert t.pending==3 and t.window_open and t.screen_open and t.breaks==0
    assert t.vbl==MAX_VBL
    t.reply_disp();t.reply_safe();assert t.finish(ctrl=True)
    assert t.breaks==1
    t=DBModel();assert t.swap()
    assert t.finish(arrivals={5:t.reply_disp,35:t.reply_safe})
    assert t.vbl==35

test('model_delayed_replies_failed_swap_and_timeout_fail_closed',model_corner_cases)

def randomized_model():
    rng=random.Random(8112026)
    for trial in range(2000):
        m=DBModel()
        for _ in range(rng.randint(1,20)):
            if m.pending:
                if rng.randrange(3):m.reply_safe()
                if rng.randrange(3):m.reply_disp()
            result=m.swap(success=rng.randrange(7)!=0)
            if result:assert m.pending==3
            else:assert m.pending in (0,1,2,3)
            assert m.swap_success >=m.received_safe and m.swap_success >=m.received_disp
            assert m.received_safe <= m.swap_success
            assert m.received_disp <= m.swap_success
        if m.pending:
            m.reply_safe();m.reply_disp()
        assert m.finish(ctrl=True), trial
        assert m.breaks==1
        assert m.received_safe==m.swap_success and m.received_disp==m.swap_success

test('model_2000_randomized_swap_and_close_sequences',randomized_model)

out={
    'candidate_sha256':digest(R8),'candidate_size':len(R8),
    'results':results,
    'critical_limitations':[
        'Static byte-level and reference state-machine tests only, not actual MC68000 execution.',
        'Unicorn CPU tests not executed in local environment (unavailable).',
        'AmigaOS/WinUAE runtime including Ctrl+C with pending swap not tested.',
        'R8 synced to GitHub; WinUAE single Swap/Close without IFF passed five times; repeated Swap, in-flight Ctrl+C and Fallout IFF remain untested.',
    ],
}
(ROOT/'docs/DB_SYNC_R8_STATIC_TESTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
