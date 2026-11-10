#!/usr/bin/env python3
"""Actual emitted MC68000 instruction-subset execution for R8 new paths.

Independent tiny interpreter for the exact 68000 opcode subset used by R8's
new Swap, Safe/Disp poll and preflight. Full AMOS/Linux/hardware emulation
is NOT claimed; original close/CTRL-C routines are trapped at the untouched
entry to check preflight outcomes only. This is complementary to Unicorn CI.
"""
import struct,json
from pathlib import Path
from ap20_utils import split,digest
from build_db_safe_r8 import build,MAX_VBL,ROOT

EXEC=0x10000;GFX=0x20000;INTUI=0x30000;AMOS=0x50000;STATE=0x60000;DB=0x70000
SCREEN=0x80000;SB0=0x81000;SB1=0x82000;SAFE=0x83000;DISP=0x84000

def u32(n):return n&0xffffffff

def signed(n):return n if n<0x80000000 else n-0x100000000

class Machine:
 def __init__(self, code, queues=None, notify_safe=1,notify_disp=2,csb_ok=True):
  self.code=code;self.mem={};self.d=[0]*8;self.a=[0]*8
  self.a[5]=AMOS;self.a[7]=0xA0000
  self.mem[4]=EXEC;self.mem[AMOS+0x1c8]=STATE
  self.mem[STATE+0]=SCREEN;self.mem[STATE+4]=INTUI;self.mem[STATE+8]=GFX
  self.mem[STATE+32]=DB
  self.mem[DB+0]=SB0;self.mem[DB+4]=SB1;self.mem[DB+8]=0
  self.mem[DB+12]=SAFE;self.mem[DB+16]=DISP;self.mem[DB+20]=0
  self.queues={SAFE:list((queues or {}).get('safe',[])),DISP:list((queues or {}).get('disp',[]))}
  self.notify_safe=notify_safe;self.notify_disp=notify_disp;self.csb_ok=csb_ok
  self.vbl=0;self.events=[];self.stack=[];self.n=0;self.pc=0
  self.z=False;self.nflag=False;self.v=False;self.c=False;self.x=False
  self.arrivals=[];self.stopped=None
 def read(self,addr):return self.mem.get(addr,0)
 def write(self,addr,value):self.mem[addr]=u32(value)
 def word(self,p):return int.from_bytes(self.code[p:p+2],'big')
 def long(self,p):return int.from_bytes(self.code[p:p+4],'big')
 def immw(self):v=self.word(self.pc);self.pc+=2;return v
 def imml(self):v=self.long(self.pc);self.pc+=4;return v
 def signw(self,w):return w if w<32768 else w-65536
 def flags(self,v):v=u32(v);self.z=(v==0);self.nflag=bool(v&0x80000000);self.v=False;self.c=False
 def oscall(self,off):
  if off==-372:
   assert self.a[6]==EXEC,('GetMsg lib',hex(self.a[6]))
   port=self.a[0];assert port in self.queues,hex(port)
   msg=self.queues[port].pop(0) if self.queues[port] else 0
   self.d[0]=msg
   self.events.append(('GetMsg',port,bool(msg)))
  elif off==-270:
   assert self.a[6]==GFX,('WaitTOF lib',hex(self.a[6]))
   self.vbl+=1;self.events.append(('WaitTOF',self.vbl))
   for time,port,ptr in self.arrivals[:]:
    if self.vbl>=time:self.queues[port].append(ptr);self.arrivals.remove((time,port,ptr))
  elif off==-228:
   assert self.a[6]==GFX
   self.events.append(('WaitBlit',))
  elif off==-780:
   assert self.a[6]==INTUI
   assert self.a[0]==SCREEN and self.a[1] in (SB0,SB1)
   self.d[0]=1 if self.csb_ok else 0
   self.events.append(('ChangeScreenBuffer',self.a[1],bool(self.d[0])))
   if self.csb_ok:
    if self.notify_safe is not None:self.arrivals.append((self.vbl+self.notify_safe,SAFE,0xAA00))
    if self.notify_disp is not None:self.arrivals.append((self.vbl+self.notify_disp,DISP,0xBB00))
  else:raise AssertionError(('unexpected OS call',off))
 def step(self):
  p=self.pc;op=self.immw();self.n+=1
  if op==0x48e7:
   assert self.immw()==0xeffe
   self.events.append(('MOVEM_PUSH',))
  elif op==0x4cdf:
   assert self.immw()==0x7ff7
   self.events.append(('MOVEM_POP',))
  elif op==0x4e75:
   if self.stack:self.pc=self.stack.pop()
   else:self.stopped='RTS'
  elif op==0x4eae:
   off=self.signw(self.immw());self.oscall(off)
  elif op in (0x6000,0x6100,0x6700,0x6600,0x6c00):
   extpos=self.pc;disp=self.signw(self.immw());target=extpos+disp
   assert 0<=target<len(self.code),(hex(p),hex(target))
   take=op in (0x6000,0x6100) or (op==0x6700 and self.z) or (op==0x6600 and not self.z) or (op==0x6c00 and self.nflag==self.v)
   if take:
    if op==0x6100:self.stack.append(self.pc)
    self.pc=target
  elif (op&0xf100)==0x7000:
   reg=(op>>9)&7;v=op&255;self.d[reg]=u32(v if v<128 else v-256);self.flags(self.d[reg])
  elif op in (0x4a80,0x4a87):
   self.flags(self.d[op&7])
  elif op==0x4a92:
   self.flags(self.read(self.a[2]))
  elif op==0x0286:
   v=self.imml();self.d[6]&=v;self.flags(self.d[6])
  elif op==0x0806:
   bit=self.immw();self.z=not bool(self.d[6]&(1<<bit))
  elif op==0x0886:
   bit=self.immw();self.z=not bool(self.d[6]&(1<<bit));self.d[6]&=~(1<<bit)
  elif op==0x5284:
   self.d[4]=u32(self.d[4]+1);self.flags(self.d[4])
  elif op==0x0c84:
   rhs=self.imml();lhs=self.d[4];ans=u32(lhs-rhs)
   self.z=ans==0;self.nflag=bool(ans&0x80000000)
   self.v=bool(((lhs^rhs)&(lhs^ans)&0x80000000)!=0)
   self.c=lhs<rhs
  elif op==0x4a87:self.flags(self.d[7])
  elif op==0x4a80:self.flags(self.d[0])
  elif op==0x2006:self.d[0]=self.d[6];self.flags(self.d[0])
  elif op in (0x2008,0x2009,0x200c,0x200e):
   self.d[0]=self.a[op&7];self.flags(self.d[0])
  elif op in (0x202c,0x2c2c):
   displacement=self.signw(self.immw());reg=(op>>9)&7
   self.d[reg]=self.read(self.a[4]+displacement);self.flags(self.d[reg])
  elif op in (0x2946,0x2947):
   displacement=self.signw(self.immw());self.write(self.a[4]+displacement,self.d[op&7]);self.flags(self.d[op&7])
  elif op==0x297c:
   v=self.imml();off=self.signw(self.immw());self.write(self.a[4]+off,v);self.flags(v)
  elif op==0x2052:self.a[0]=self.read(self.a[2])
  elif op==0x2254:self.a[1]=self.read(self.a[4])
  elif op in (0x226c,0x206c):
   v=self.signw(self.immw());self.a[(op>>9)&7]=self.read(self.a[4]+v)
  elif op==0x246d:
   off=self.signw(self.immw());self.a[2]=self.read(self.a[5]+off)
  elif op==0x286a:
   off=self.signw(self.immw());self.a[4]=self.read(self.a[2]+off)
  elif op==0x2c6a:
   off=self.signw(self.immw());self.a[6]=self.read(self.a[2]+off)
  elif op==0x2c78:
   src=self.signw(self.immw());self.a[6]=self.read(src)
  elif op==0x4e71:pass
  else:raise AssertionError(('unknown opcode',hex(op),'at',hex(p),'pc',hex(self.pc)))
 def run(self,start=0,limit=200000,traps=None):
  traps=traps or {}
  self.pc=start
  for _ in range(limit):
   if self.pc in traps:
    kind=traps[self.pc]
    if kind=='RET_FROM_CLOSE_WINDOW':
     assert self.stack
     self.events.append(('CloseWindowHelperReached',))
     self.pc=self.stack.pop();continue
    self.stopped=kind;break
   if self.stopped:return self.stopped
   self.step()
   if self.stopped:return self.stopped
  else:raise AssertionError(('instruction limit exceeded',self.pc,self.vbl))
  return self.stopped

def validate():
 raw,rep=build();_,ss,_=split(raw)
 tests={}
 def test(name,fn):fn();tests[name]='PASS'
 def initial():
  m=Machine(ss[11]);assert m.run()=='RTS';assert m.d[3]==1 and m.d[2]==0
  assert m.read(DB+20)==3 and m.read(DB+8)==1
  assert len([e for e in m.events if e[0]=='ChangeScreenBuffer'])==1
  assert len([e for e in m.events if e[0]=='GetMsg'])==0
  return m
 test('cpu_subset_swap_initial_marks_both_pending',initial)
 def delayed_and_repeat():
  m=initial();m.events=[]
  m.stopped=None;m.run()
  assert m.d[3]==0 and m.read(DB+20)==3
  assert not any(e[0]=='ChangeScreenBuffer' for e in m.events)
  m.vbl=3;m.queues[SAFE]=[0xAA00];m.queues[DISP]=[0xBB00]
  m.stopped=None;m.run();assert m.d[3]==1 and m.read(DB+20)==3 and m.read(DB+8)==0
  assert sum(e[0]=='ChangeScreenBuffer' for e in m.events)==1
 test('cpu_subset_rejects_swap_while_pending_and_consumes_replies',delayed_and_repeat)
 def failure():
  m=Machine(ss[11],csb_ok=False);m.run()
  assert m.d[3]==0 and m.read(DB+20)==0
  assert sum(e[0]=='ChangeScreenBuffer' for e in m.events)==1
 test('cpu_subset_failed_changescreenbuffer_no_pending',failure)
 def close_idx(i):
  src=ss[i];orig_len={0:456,8:298,17:508,18:548}[i]
  if i==0:return 0x40,{0x14e:'RET_FROM_CLOSE_WINDOW',0x44:'CLOSE_CONTINUE',0x148:'CLOSE_ABORT'}
  if i==8:return 0x08,{0xd4:'RET_FROM_CLOSE_WINDOW',0x0c:'CLOSE_CONTINUE',0xce:'CLOSE_ABORT'}
  if i==17:return 0x7e,{0x8c:'CTRL_C_CLEANUP',0x1da:'CTRL_C_ABORT'}
  return 0x7e,{0x8c:'CTRL_C_CLEANUP',0x1ee:'CTRL_C_ABORT'}
 def preflight_immediate():
  for i in (0,8,17,18):
   start,traps=close_idx(i);m=Machine(ss[i]);m.a[2]=STATE
   assert m.run(start,traps=traps)==('CLOSE_CONTINUE' if i in (0,8) else 'CTRL_C_CLEANUP'),i
   assert m.vbl==0 and m.read(DB+20)==0
 test('cpu_subset_no_pending_close_and_ctrl_c_path',preflight_immediate)
 def preflight_queued():
  for i in (0,8,17,18):
   start,traps=close_idx(i);m=Machine(ss[i]);m.a[2]=STATE;m.write(DB+20,3)
   m.queues[SAFE]=[0xAA00];m.queues[DISP]=[0xBB00]
   assert m.run(start,traps=traps)==('CLOSE_CONTINUE' if i in (0,8) else 'CTRL_C_CLEANUP')
   assert m.read(DB+20)==0 and m.vbl==0
   assert len([e for e in m.events if e[0]=='GetMsg'])==2
 test('cpu_subset_two_immediate_replies_allow_cleanup',preflight_queued)
 def preflight_delayed():
  for i in (0,8,17,18):
   start,traps=close_idx(i);m=Machine(ss[i]);m.a[2]=STATE;m.write(DB+20,3)
   m.arrivals=[(2,DISP,0xBB00),(11,SAFE,0xAA00)]
   assert m.run(start,traps=traps)==('CLOSE_CONTINUE' if i in (0,8) else 'CTRL_C_CLEANUP')
   assert m.read(DB+20)==0 and m.vbl==11
 test('cpu_subset_delayed_notifications_waittof_cooperatively',preflight_delayed)
 def preflight_timeout():
  for i in (0,8,17,18):
   start,traps=close_idx(i);m=Machine(ss[i]);m.a[2]=STATE;m.write(DB+20,3)
   assert m.run(start,traps=traps)==('CLOSE_ABORT' if i in (0,8) else 'CTRL_C_ABORT')
   assert m.read(DB+20)==3 and m.vbl==MAX_VBL
   assert not any(e[0]=='CloseWindowHelperReached' for e in m.events)
 test('cpu_subset_timeout_does_not_free_or_trigger_ctrl_c',preflight_timeout)
 def partial_timeout():
  for i in (8,17):
   start,traps=close_idx(i);m=Machine(ss[i]);m.a[2]=STATE;m.write(DB+20,3)
   m.queues[SAFE]=[0xAA00]
   assert m.run(start,traps=traps)==('CLOSE_ABORT' if i==8 else 'CTRL_C_ABORT')
   assert m.read(DB+20)==2 and m.vbl==MAX_VBL
 test('cpu_subset_partial_reply_preserves_missing_disp_pending',partial_timeout)
 result={'candidate_sha256':digest(raw),'candidate_size':len(raw),'tests':tests,
 'limitation':'CPU instruction-subset test of newly emitted code paths with mocked OS calls. Not independent Unicorn, not real AmigaOS / WinUAE runtime. Existing close and Ctrl+C core are trapped at untouched entry points.'}
 path=ROOT/'docs/DB_SYNC_R8_CPU_SUBSET_TESTS.json';path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':validate()
