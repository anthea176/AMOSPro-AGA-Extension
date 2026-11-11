#!/usr/bin/env python3
"""R38 Gate A: real 68000 AP20 ABI, AMCAF fixture, lifetime and failure atomicity.

System LVOs are mocked; this is not WinUAE, the AMOS compiler or hardware.
"""
from pathlib import Path
from struct import pack, unpack_from

from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR

from ap20_utils import split, digest
from audit_ap20 import inspect, parse
from build_m14_font_bank_r38 import (build, BASE, BASE_SHA256, LAST_GOOD,
    LAST_GOOD_SHA256, ENTRY_INDEX, GETP, API)
from m14_font_bank_r38_emit import (emit_bank_select, FONT_AT, NAME_AT,
    MEMF_PUBLIC_CHIP_CLEAR)
from m14_font_select_r37_emit import emit_font_select
from amcaf_font_r38_layout import read_abk, read_bankfont, synthetic_abk
from test_m14_font_select_r37 import FontMachine
from test_m5_generic import (CODE, STOP, STACK, DR, AR, AMOS, STATE, SCREEN,
                             EXEC, GFX, INTUI)
from test_m11_text_r26 import ARGS

ROOT=Path(__file__).resolve().parents[1]
FIXTURE_BYTES=synthetic_abk()  # original glyph art, no Amiga ROM font redistributed
BANK=0x62000


class BankMachine(FontMachine):
    def __init__(self,raw,payload=None,*,type_header=True,type_last=True,
                 alloc_fail=False,flags=0,bank_name=b'BankFont',**kw):
        super().__init__(raw,**kw)
        image=FIXTURE_BYTES
        bank,desc=read_abk(image)
        self.payload=bytearray(image[20:] if payload is None else payload)
        self.type_header=type_header
        self.type_last=type_last
        self.alloc_fail=alloc_fail
        self.allocations={}
        self.copied=[]
        self.stripped=[]
        self.freed=[]
        self.type_calls=[]
        self.closed_bank_fonts=[]
        self.uc.mem_write(EXEC-534,b'\x4e\x75')
        self.uc.mem_write(EXEC-624,b'\x4e\x75')
        self.uc.mem_write(GFX-822,b'\x4e\x75')
        self.uc.mem_write(BANK-24,pack('>IIIHH8s',0,len(self.payload)+16,bank,flags,0,bank_name))
        self.uc.mem_write(BANK,bytes(self.payload))
        code,labels=emit_bank_select()
        self.bank_labels=labels
        self.bank_state_address=CODE+self.p.starts[ENTRY_INDEX]+labels['bank_state']
        assert self.uc.mem_read(self.bank_state_address,8)==bytes(8)

    def bank_state(self):
        return self.get(self.bank_state_address),self.get(self.bank_state_address+4)

    def os_call(self,uc,address,size,user):
        if address==EXEC-534:
            addr=self.a(1)
            self.type_calls.append(addr)
            if addr==BANK-24: res=4 if self.type_header else 0
            elif addr==BANK+len(self.payload)-1: res=4 if self.type_last else 0
            else: res=0
            self._ret(res)
            return
        if address==EXEC-684:
            self.alloc_calls+=1
            assert self.d(1)==MEMF_PUBLIC_CHIP_CLEAR,'R38 copied font must be CHIP owned memory'
            count=self.d(0)
            assert 112<=count<=65535
            if self.alloc_fail:
                self._ret(0)
                return
            ptr=self.next
            self.next+=(count+15)&~15
            self.allocations[ptr]=count
            uc.mem_write(ptr,b'\0'*count)
            self._ret(ptr)
            return
        if address==EXEC-624:
            src,dst,n=self.a(0),self.a(1),self.d(0)
            assert src==BANK and n==len(self.payload)
            assert dst in self.allocations and self.allocations[dst]==n
            uc.mem_write(dst,bytes(uc.mem_read(src,n)))
            self.copied.append((src,dst,n))
            self._ret()
            return
        if address==EXEC-690:
            ptr=self.a(1)
            assert ptr in self.allocations,('FreeVec of non-own bank font',hex(ptr))
            assert self.stripped.count(ptr+FONT_AT)==1,('FreeVec before StripFont',hex(ptr))
            self.allocations.pop(ptr)
            self.freed.append(ptr)
            self.fonts.pop(ptr+FONT_AT,None)
            self._ret()
            return
        if address==GFX-822:
            ptr=self.a(0)
            assert any(x+FONT_AT==ptr for x in self.allocations),('StripFont of non-own font',hex(ptr))
            self.stripped.append(ptr)
            self.put(ptr+14,0)
            self._ret()
            return
        if address==GFX-78:
            assert self.a(1) not in (x+FONT_AT for x in self.allocations), 'bank fonts must NOT CloseFont'
            return super().os_call(uc,address,size,user)
        if address==GFX-66:
            ptr,rp=self.a(0),self.a(1)
            if ptr in (x+FONT_AT for x in self.allocations):
                assert STACK-1024<=rp<STACK
                assert self.get(ptr+10)==ptr-FONT_AT+NAME_AT
                assert self.get(ptr+34)>ptr
                assert self.get(ptr+40)>ptr
                assert self.get(ptr+14)==0
                self.fonts[ptr]=unpack_from('>H',uc.mem_read(ptr+20,2))[0]
                self.put(rp+52,ptr)
                self.set_font.append(ptr)
                self._ret()
                return
            return super().os_call(uc,address,size,user)
        return super().os_call(uc,address,size,user)

    def select_bank(self,ptr=BANK,length=None):
        n=len(self.payload) if length is None else length
        for i,r in enumerate(DR):self.uc.reg_write(r,0x1200+i)
        for i,r in enumerate(AR[:7]):self.uc.reg_write(r,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS,ptr)
        self.uc.reg_write(DR[3],n&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_INDEX],STOP,count=1000000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,'R38 RTS did not return'
        assert self.a(7)==STACK+4,'unbalanced R38 stack'
        assert self.a(3)==ARGS+4,'R38 did not consume Start(bank) parameter'
        for reg,value in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==value,('R38 clobbered register',reg)
        assert self.d(2)==0
        return self.d(3)


def run():
    image=FIXTURE_BYTES
    assert len(image)==2880
    bank,info=read_abk(image)
    assert bank==10 and info.total==2860 and info.name==b'r38test.font'
    assert (info.ysize,info.xsize,info.baseline,info.modulo)==(9,10,6,206)
    assert (info.bitmap_at,info.loc_at,info.glyphs)==(106,1960,225)
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    raw,report=build();assert raw==build()[0]
    old_tokens,old,_=split(BASE.read_bytes())
    tokens,parts,_=split(raw)
    assert len(old)==49 and len(parts)==50
    assert parts[:48]==old[:48]
    assert parts[48][-4:]==GETP
    assert tokens.startswith(old_tokens[:-6])
    audit=inspect(parse(raw))
    assert not audit['issues'],audit['issues']
    named=[x for x in audit['tokens'] if x['name'].startswith('aga ')]
    assert len(named)==44
    found=[x for x in named if x['name']==API[0][0]]
    assert len(found)==1 and found[0]['signature']=='00,0'
    assert any(x['index']==49 and x['parameters']==2 and x['getp'] for x in audit['parameter_checks'])

    code,labels=emit_bank_select()
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions=list(dis.disasm(code[:labels['bank_state']],0))
    assert sum(i.size for i in instructions)==labels['bank_state'], 'invalid 68000 R38 instruction'
    boundaries={i.address for i in instructions}
    assert all(v in boundaries for key,v in labels.items() if key not in ('bank_state','r37_state_lookup','r37_state_commit'))
    assert all(i.mnemonic not in ('dc.w','illegal','trap') for i in instructions)
    assert b'\x4e\xae\xfc\xca' in code, 'StripFont LVO -822 missing'
    assert b'\x4e\xae\xfd\x4e' in code, 'FreeVec LVO -690 missing'
    assert b'\x4e\xae\xfd\x54' in code, 'AllocVec LVO -684 missing'

    groups=0
    m=BankMachine(raw)
    initial=bytes(m.uc.mem_read(BANK,len(m.payload)))
    assert m.select_bank()==1
    ptr,alloc=m.bank_state()
    assert ptr==alloc+24 and m.font_state()==(SCREEN,ptr)
    assert bytes(m.uc.mem_read(BANK,len(m.payload)))==initial
    private=bytes(m.uc.mem_read(alloc,len(m.payload)))
    assert private[:24]==initial[:24]
    assert m.get(ptr+34)==alloc+info.bitmap_at
    assert m.get(ptr+40)==alloc+info.loc_at
    assert m.get(ptr+10)==alloc+NAME_AT
    assert m.get(ptr+14)==0 and m.get(ptr+44)==m.get(ptr+48)==0
    assert private[info.bitmap_at:info.loc_at]==initial[info.bitmap_at:info.loc_at]
    assert private[info.loc_at:]==initial[info.loc_at:]
    m.uc.mem_write(BANK,b'\0'*len(m.payload))    # Erase 10 in AMOS
    assert m.text(value=b'AMCAF BANK FONT')==1 and m.set_font[-1]==ptr
    assert m.select(b'',0)==1
    assert m.bank_state()==(0,0) and m.font_state()==(0,0)
    assert m.stripped==[ptr] and m.freed==[alloc] and not m.allocations
    groups+=1

    # R37 diskfont selection -> R38 bank -> R37 selection must CloseFont/StripFont correctly.
    m=BankMachine(raw)
    assert m.select(b'topaz.font',8)==1
    oldptr=m.font_state()[1]
    assert m.select_bank()==1
    assert m.closed_fonts==[oldptr] and oldptr not in m.fonts
    ptr,alloc=m.bank_state()
    assert m.select(b'topaz.font',9)==1
    assert m.stripped==[ptr] and m.freed==[alloc]
    assert m.bank_state()==(0,0)
    assert m.font_state()[1] in m.fonts
    m.call_close_helper()
    assert m.closed_screens==1 and not m.fonts
    groups+=1

    m=BankMachine(raw)
    assert m.select_bank()==1
    ptr,alloc=m.bank_state()
    m.call_close_helper()
    assert m.closed_screens==1 and m.stripped==[ptr] and m.freed==[alloc]
    assert m.font_state()==m.bank_state()==(0,0)
    groups+=1

    m=BankMachine(raw)
    assert m.select_bank()==1
    first,first_alloc=m.bank_state()
    assert m.select_bank()==1
    second,second_alloc=m.bank_state()
    assert first!=second and first_alloc!=second_alloc
    assert m.stripped==[first] and m.freed==[first_alloc]
    assert m.select(b'',0)==1
    assert m.stripped==[first,second] and m.freed==[first_alloc,second_alloc]
    groups+=1

    for invalid in (dict(ptr=0),dict(ptr=1),dict(ptr=23),dict(ptr=BANK+1),
                    dict(length=0),dict(length=111),dict(length=65536),
                    dict(length=-1),dict(length=2861),dict(length=2868)):
        m=BankMachine(raw)
        assert m.select_bank(**invalid)==0,invalid
        assert m.bank_state()==m.font_state()==(0,0)
        assert not m.allocations and not m.copied
        groups+=1

    invalid_offsets=((0,b'BLAH'),(10,b'\0\0'),(14,b'\xff\xff'),
                     (32,b'\x01'),(44,b'\0\0'),(48,b'\0\0'),
                     (50,b'\0\xff'),(56,b'\xff'),(57,b'\x01'),
                     (46,b'\x40'),(62,b'\0\0'),(62,b'\0\xcf'),
                     (68,b'\0\0\x10\0'),(72,b'\0\0\x10\0'),
                     (1960,b'\xff\xff'))
    for offset,bad in invalid_offsets:
        payload=bytearray(image[20:])
        payload[offset:offset+len(bad)]=bad
        m=BankMachine(raw,payload)
        assert m.select_bank()==0,offset
        assert m.bank_state()==m.font_state()==(0,0)
        assert not m.allocations and not m.copied
        groups+=1

    for overrides in (dict(flags=1),dict(flags=4),dict(bank_name=b'NOTFONTS'),
                      dict(type_header=False),dict(type_last=False),
                      dict(alloc_fail=True)):
        m=BankMachine(raw,**overrides)
        assert m.select_bank()==0,overrides
        assert not m.allocations and m.bank_state()==(0,0)
        groups+=1

    for kind in ('no_screen','no_gfx','bad_bank_with_font'):
        m=BankMachine(raw)
        if kind=='bad_bank_with_font':
            assert m.select(b'topaz.font',8)==1
            previous=m.font_state()
            m.uc.mem_write(BANK,b'BLAH')
        if kind=='no_screen':m.put(STATE,0)
        if kind=='no_gfx':m.put(STATE+8,0)
        assert m.select_bank()==0,kind
        if kind=='bad_bank_with_font':
            assert m.font_state()==previous and previous[1] in m.fonts
            assert not m.closed_fonts
        groups+=1

    print('R38 AMCAF BankFont CPU 68000 Gate A PASS:',groups,'lifecycle/rejection groups')
    print('R38 built candidate:',{k:v for k,v in report.items() if k!='bank_labels'})
    print('R38 WinUAE Gate B, Compiler Gate C and physical AGA Gate D: NOT TESTED')


if __name__=='__main__':run()
