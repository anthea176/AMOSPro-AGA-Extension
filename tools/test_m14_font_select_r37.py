#!/usr/bin/env python3
"""R37 Gate A: AP20 ABI and real 68000 Font Select/Text/Close lifecycle.

Mock AmigaOS LVOs exercise the actual candidate bytes. This does NOT
constitute interpreted AMOS/WinUAE, Compiler, or physical-Amiga validation.
"""
import struct
from capstone import Cs, CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, CS_MODE_M68K_000
from unicorn.m68k_const import UC_M68K_REG_PC, UC_M68K_REG_SR
from ap20_utils import split, digest
from audit_ap20 import parse, inspect
from build_m14_font_select_r37 import (
    build, BASE, BASE_SHA256, LAST_GOOD, LAST_GOOD_SHA256, API,
    ENTRY_FONT_SELECT, ENTRY_TEXT, ENTRY_SCREEN_CLOSE, CLOSE_SCREEN_CALL_OFFSET,
)
from m14_font_select_r37_emit import emit_font_select
from test_m11_text_r26 import TextMachine, TEXT_PTR, ARGS, FONT
from test_m5_generic import CODE, STOP, STACK, DR, AR, AMOS, STATE, SCREEN, GFX, EXEC, INTUI

DISK = 0x23000
NAME_PTR = 0x5e800
FIRST_FONT = 0x5a000


class FontMachine(TextMachine):
    def __init__(self, candidate, *, fail_diskfont=False, fail_openlibrary=False, **kwargs):
        super().__init__(candidate, **kwargs)
        self.uc.mem_write(EXEC-552, b"\x4e\x75")
        self.uc.mem_write(EXEC-414, b"\x4e\x75")
        self.uc.mem_write(DISK-30, b"\x4e\x75")
        self.uc.mem_write(GFX-78, b"\x4e\x75")
        self.uc.mem_write(GFX-66, b"\x4e\x75")
        self.uc.mem_write(INTUI-66, b"\x4e\x75")
        self.fail_diskfont = fail_diskfont
        self.fail_openlibrary = fail_openlibrary
        self.fonts = {}             # opened font pointer -> requested size
        self.open_requests = []
        self.closed_fonts = []
        self.set_font = []
        self.closed_screens = 0
        self.first_font = FIRST_FONT
        self.selected_text_extents = []
        self.fontcode, self.fontlabels = emit_font_select()
        self.state_address = CODE+self.p.starts[ENTRY_FONT_SELECT]+self.fontlabels['font_state']
        assert self.uc.mem_read(self.state_address,8) == bytes(8)

    def os_call(self, uc, address, size, user):
        if address == EXEC-552:
            assert self.cstring(self.a(1)) == b'diskfont.library', 'wrong library opened'
            assert self.d(0) == 0
            self.open_requests.append('lib')
            if self.fail_openlibrary:
                self._ret(0)
            else:
                self.open_libraries += 1
                self._ret(DISK)
            return
        if address == DISK-30:
            assert self.open_libraries == 1, 'OpenDiskFont after CloseLibrary'
            attr = self.a(0)
            name_ptr = self.get(attr)
            name = self.cstring(name_ptr)
            size = struct.unpack('>H',uc.mem_read(attr+4,2))[0]
            assert uc.mem_read(attr+6,2)==b'\0\0', 'style/flags not initialised'
            assert name and len(name)<=127
            self.open_requests.append((name,size))
            if self.fail_diskfont:
                self._ret(0)
            else:
                ptr = self.first_font
                self.first_font += 0x100
                self.fonts[ptr] = size
                self._ret(ptr)
            return
        if address == EXEC-414:
            assert self.a(1)==DISK, 'CloseLibrary not diskfont'
            assert self.open_libraries==1
            self.open_libraries -= 1
            self._ret()
            return
        if address == GFX-78:
            ptr=self.a(1)
            assert ptr in self.fonts,('CloseFont unowned',hex(ptr))
            self.closed_fonts.append(ptr)
            self.fonts.pop(ptr)
            self._ret()
            return
        if address == GFX-66:
            ptr, rp = self.a(0), self.a(1)
            assert ptr in self.fonts,('SetFont stale pointer',hex(ptr))
            assert STACK-1024 <= rp < STACK
            self.put(rp+52,ptr)
            self.set_font.append(ptr)
            self._ret()
            return
        if address == GFX-690:
            rp, src, count, target = self.a(1),self.a(0),self.d(0)&0xffff,self.a(2)
            assert STACK-1024<=rp<STACK and target==rp+128
            assert self.get(rp+4)==self.expected_bitmap
            assert bytes(uc.mem_read(src,count))==self.string
            used_font=self.get(rp+52)
            size=self.fonts.get(used_font,8)
            self.selected_text_extents.append((used_font,size))
            extent=self.ext if self.ext is not None else (count*8,size,0,2-size,count*8-1,1)
            uc.mem_write(target,struct.pack('>HHhhhh',*extent))
            self._ret()
            return
        if address == INTUI-66:
            assert self.a(0)==SCREEN,'CloseScreen wrong private Screen'
            self.closed_screens+=1
            self._ret(1)
            return
        return super().os_call(uc,address,size,user)

    def font_state(self):
        return self.get(self.state_address),self.get(self.state_address+4)

    def select(self,name=b'topaz.font',ysize=8):
        if name is None:
            descriptor=0
        else:
            descriptor=NAME_PTR
            self.uc.mem_write(descriptor,struct.pack('>H',len(name))+name)
        for i,reg in enumerate(DR): self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]): self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[3],ARGS)
        self.put(ARGS,descriptor)
        self.uc.reg_write(DR[3],ysize&0xffffffff)
        saved={r:self.uc.reg_read(r) for r in DR+AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        self.uc.emu_start(CODE+self.p.starts[ENTRY_FONT_SELECT],STOP,count=200000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,'no font select RTS'
        assert self.a(7)==STACK+4,'stack unbalanced'
        assert self.a(3)==ARGS+4,'missing AMOS argument consumption'
        for reg,value in saved.items():
            if reg not in (DR[2],DR[3],AR[3]):
                assert self.uc.reg_read(reg)==value,('changed register',reg)
        assert self.d(2)==0
        assert self.open_libraries==0,'leaked diskfont.library handle'
        return self.d(3)

    def call_close_helper(self):
        for i,reg in enumerate(DR): self.uc.reg_write(reg,0x1200+i)
        for i,reg in enumerate(AR[:7]): self.uc.reg_write(reg,0x40000+i*256)
        self.uc.reg_write(AR[5],AMOS)
        self.uc.reg_write(AR[0],SCREEN)
        self.uc.reg_write(AR[2],STATE)
        self.uc.reg_write(AR[6],INTUI)
        saved={r:self.uc.reg_read(r) for r in (AR[2],AR[6])}  # A0 is caller-scratch across CloseScreen
        self.uc.reg_write(UC_M68K_REG_SR,0x2000)
        self.uc.reg_write(AR[7],STACK)
        self.put(STACK,STOP)
        start=CODE+self.p.starts[ENTRY_FONT_SELECT]+self.fontlabels['font_close']
        self.uc.emu_start(start,STOP,count=50000)
        assert self.uc.reg_read(UC_M68K_REG_PC)==STOP,'no close helper RTS'
        assert self.a(7)==STACK+4,'close helper stack unbalanced'
        for r,v in saved.items():
            assert self.uc.reg_read(r)==v,'close helper clobbered caller context'


def run():
    raw,report=build()
    assert raw==build()[0]
    assert digest(BASE.read_bytes())==BASE_SHA256
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256
    old_tok,old,_=split(BASE.read_bytes())
    tokens,parts,_=split(raw)
    assert len(old)==48 and len(parts)==49
    assert all(old[i]==parts[i] for i in range(48) if i not in (8,36,47))
    assert parts[47]==old[47]+b'GetP'
    assert tokens.startswith(old_tok[:-6])
    audited=inspect(parse(raw))
    assert audited['issues']==[],audited['issues']
    named=[x for x in audited['tokens'] if x['name'].startswith('aga ')]
    assert len(named)==43
    assert [x for x in named if x['name']==API[0][0]][0]['signature']=='02,0'

    code,labels=emit_font_select()
    assert parts[48]==code
    dis=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
    instructions=list(dis.disasm(code[:labels['font_state']],0))
    assert sum(i.size for i in instructions)==labels['font_state'],'non-68000 R37 instruction'
    boundaries={i.address for i in instructions}
    assert all(v in boundaries for k,v in labels.items() if k!='font_state')
    assert all(i.mnemonic not in ('dc.w','illegal','trap') for i in instructions)
    # Native LVO sanity, including diskfont load and balanced release.
    for opcode in ('4eaefdd8','4eaefe62','4eaeffe2','4eaeffb2','4eaeffbe','4eaef fbe'):
        if ' ' in opcode: continue
        assert bytes.fromhex(opcode) in code,(opcode,'missing expected LVO')
    assert code[-8:]==bytes(8)
    assert parts[8][0x8c:0x8e]==b'\x61\x00','old CloseScreen call not hooked'

    cases=0
    for first,second in ((8,9),(9,8),(8,8)):
        m=FontMachine(raw)
        assert m.select(b'topaz.font',first)==1
        original_font=m.font_state()[1]
        assert m.font_state()[0]==SCREEN and original_font in m.fonts
        assert m.select(b'topaz.font',second)==1
        active=m.font_state()[1]
        assert active!=original_font and original_font in m.closed_fonts
        assert original_font not in m.fonts
        assert m.text(value=b'AGA TEXT')==1
        assert m.set_font[-1]==active
        assert m.selected_text_extents[-1]==(active,second)
        assert m.select(b'',0)==1
        assert m.font_state()==(0,0) and not m.fonts
        assert m.select(b'',0)==1,'reset must be idempotent'
        cases+=1

    invalid=((b'topaz.font',0),(b'',8),(b'topaz.font',-1),
             (b'topaz.font',256),(b'A'*128,8),(b'A\0B',8),
             (b'anything.font',0),(None,8),(b'x'*256,8))
    for name,size in invalid:
        m=FontMachine(raw)
        assert m.select(name,size)==0,(name,size)
        assert not m.fonts and m.font_state()==(0,0)
        assert not m.open_requests
        cases+=1

    for failure in ('diskfont','library','no_screen','no_gfx'):
        m=FontMachine(raw,fail_diskfont=failure=='diskfont',
                      fail_openlibrary=failure=='library')
        if failure=='no_screen':m.put(STATE,0)
        if failure=='no_gfx':m.put(STATE+8,0)
        assert m.select()==0,failure
        assert m.font_state()==(0,0) and not m.fonts
        assert m.open_libraries==0
        cases+=1

    for failure in ('diskfont','library'):
        m=FontMachine(raw)
        assert m.select()==1
        previous=m.font_state()[1]
        setattr(m,'fail_diskfont' if failure=='diskfont' else 'fail_openlibrary',True)
        assert m.select(b'different.font',16)==0
        assert m.font_state()==(SCREEN,previous)
        assert list(m.fonts)==[previous]
        assert not m.closed_fonts
        cases+=1

    for with_font in (False,True):
        m=FontMachine(raw)
        if with_font:
            assert m.select()==1
            ptr=m.font_state()[1]
        m.call_close_helper()
        assert m.closed_screens==1
        assert m.font_state()==(0,0)
        assert not m.fonts
        if with_font:assert m.closed_fonts==[ptr]
        else:assert not m.closed_fonts
        cases+=1

    print('R37 Font Select CPU 68000 Gate A PASS:',cases,'lifecycle groups',flush=True)
    print('R37 candidate:',{k:v for k,v in report.items() if not k.endswith('labels')},flush=True)
    print('R37 Gate B interpreted/WinUAE, C Compiler, D physical AGA: NOT TESTED')

if __name__=='__main__':
    run()
