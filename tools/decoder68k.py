"""Conservative built-in 68000 instruction decoder for AP20 source restoration.

Not a complete Motorola disassembler: an unsupported encoding is returned as
None and must be emitted as *labelled data*, not invented instructions. The
assembler still needs an independent native validation (vasm/Genam).
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Insn:
    size:int
    op:str
    args:str=''
    target:int|None=None
    stop:bool=False
    call:bool=False
    data_refs:tuple[int,...]=()
    @property
    def text(self):return (self.op+' '+self.args).strip()

SZ={0:'b',1:'w',2:'l'}
CC=['t','f','hi','ls','cc','cs','ne','eq','vc','vs','pl','mi','ge','lt','gt','le']

class DecodeError(Exception):pass

class Decoder:
    def __init__(self,data:bytes,base:int=0):
        self.data,self.base=data,base
        self.end=base+len(data)
    def u16(self,p):
        i=p-self.base
        if i<0 or i+2>len(self.data):raise DecodeError
        return int.from_bytes(self.data[i:i+2],'big')
    def u32(self,p):return (self.u16(p)<<16)|self.u16(p+2)
    def s16(self,p):
        x=self.u16(p);return x-65536 if x&32768 else x
    def s32(self,p):
        x=self.u32(p);return x-4294967296 if x&0x80000000 else x
    def ea(self,mode,reg,p,size='l',allow_imm=True):
        if mode==0:return f'd{reg}',p,()
        if mode==1:return f'a{reg}',p,()
        if mode==2:return f'(a{reg})',p,()
        if mode==3:return f'(a{reg})+',p,()
        if mode==4:return f'-(a{reg})',p,()
        if mode==5:return f'{self.s16(p)}(a{reg})',p+2,()
        if mode==6:
            ext=self.u16(p);idx=('a' if ext&0x8000 else 'd')+str((ext>>12)&7)
            indsz='l' if ext&0x800 else 'w'; disp=ext&255
            if disp>=128:disp-=256
            if ext&0x100:return None,p,()
            return f'{disp}(a{reg},{idx}.{indsz})',p+2,()
        if mode==7:
            if reg==0:return f'${self.u16(p):04X}.w',p+2,()
            if reg==1:return f'${self.u32(p):08X}.l',p+4,()
            if reg==2:
                off=self.s16(p);return f'{off}(pc)',p+2,(p+off,)
            if reg==3:
                ext=self.u16(p)
                if ext&0x100:return None,p,()
                idx=('a' if ext&0x8000 else 'd')+str((ext>>12)&7)
                indsz='l' if ext&0x800 else 'w';disp=ext&255
                if disp>=128:disp-=256
                return f'{disp}(pc,{idx}.{indsz})',p+2,()
            if reg==4 and allow_imm:
                if size=='l':return f'#${self.u32(p):08X}',p+4,()
                v=self.u16(p)
                if size=='b':v&=255;return f'#${v:02X}',p+2,()
                return f'#${v:04X}',p+2,()
        return None,p,()
    def decode(self,p):
        try:return self._decode(p)
        except (DecodeError,ValueError,IndexError):return None
    def _decode(self,p):
        w=self.u16(p);g=w>>12
        if w==0x4e75:return Insn(2,'rts',stop=True)
        if w==0x4e73:return Insn(2,'rte',stop=True)
        if w==0x4e77:return Insn(2,'rtr',stop=True)
        if w==0x4e71:return Insn(2,'nop')
        if w==0x4e70:return Insn(2,'reset')
        if w==0x4e72:return Insn(4,'stop',f'#${self.u16(p+2):04X}',stop=True)
        if w==0x4e76:return Insn(2,'trapv')
        if (w&0xfff0)==0x4e40:return Insn(2,'trap',f'#{w&15}')
        if (w&0xfff8)==0x4e50:return Insn(4,'link.w',f'a{w&7},#{self.s16(p+2)}')
        if (w&0xfff8)==0x4e58:return Insn(2,'unlk',f'a{w&7}')
        if (w&0xfff8)==0x4e60:return Insn(2,'move.l',f'a{w&7},usp')
        if (w&0xfff8)==0x4e68:return Insn(2,'move.l',f'usp,a{w&7}')
        if w==0x4e74:return Insn(4,'rtd',f'#{self.s16(p+2)}',stop=True)
        if (w&0xfff8)==0x4840:return Insn(2,'swap',f'd{w&7}')
        if (w&0xfff8)==0x4880:return Insn(2,'ext.w',f'd{w&7}')
        if (w&0xfff8)==0x48c0:return Insn(2,'ext.l',f'd{w&7}')
        if (w&0xfff8)==0x49c0:return Insn(2,'extb.l',f'd{w&7}') # 68020
        if (w&0xfff8)==0x4e80:return None
        if (w&0xffc0) in (0x4e80,0x4ec0):
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'l',False)
            if ea is None:return None
            name='jsr' if (w&0xffc0)==0x4e80 else 'jmp'
            return Insn(end-p,name,ea,ref[0] if ref else None,stop=(name=='jmp'),call=name=='jsr')
        if (w&0xf1c0)==0x41c0:
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'l',False)
            if ea:return Insn(end-p,'lea',f'{ea},a{(w>>9)&7}',data_refs=ref)
        if (w&0xffc0)==0x4840:
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'l',False)
            if ea:return Insn(end-p,'pea',ea,data_refs=ref)
        if (w&0xffc0)==0x40c0:
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'w',False)
            if ea:return Insn(end-p,'move.w',f'sr,{ea}',data_refs=ref)
        if (w&0xffc0)==0x42c0:
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'w',False)
            if ea:return Insn(end-p,'move.w',f'ccr,{ea}',data_refs=ref)
        if (w&0xffc0)==0x44c0:
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'w',False)
            if ea:return Insn(end-p,'move.w',f'{ea},ccr',data_refs=ref)
        if (w&0xffc0)==0x46c0:
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'w',False)
            if ea:return Insn(end-p,'move.w',f'{ea},sr',data_refs=ref)
        if (w&0xfb80)==0x4880 and ((w>>3)&7)!=0:
            is_mem_reg=bool(w&0x400);size='l' if w&0x40 else 'w'
            mask=self.u16(p+2);mode=(w>>3)&7
            ea,end,ref=self.ea(mode,w&7,p+4,size,False)
            if ea is None:return None
            registers=[]
            for bit in range(16):
                if mask&(1<<bit):
                    rr=15-bit if mode==4 and not is_mem_reg else bit
                    registers.append(rr)
            # Canonical register ordering (Motorola order, independent of
            # the reverse MOVEM predecrement encoding).
            registers.sort()
            ranges=[]
            k=0
            while k<len(registers):
                j=k
                while j+1<len(registers) and registers[j+1]==registers[j]+1 and (registers[j]//8)==(registers[j+1]//8):
                    j+=1
                def rn(r):return ('d' if r<8 else 'a')+str(r%8)
                ranges.append(rn(registers[k]) + ('-'+rn(registers[j]) if j>k else ''))
                k=j+1
            rs='/'.join(ranges)
            args=f'{ea},{rs}' if is_mem_reg else f'{rs},{ea}'
            return Insn(end-p,'movem.'+size,args,data_refs=ref)
        if (w&0xff00)==0x4200 or (w&0xff00)==0x4400 or (w&0xff00)==0x4600 or (w&0xff00)==0x4a00 or (w&0xff00)==0x4000:
            sz=(w>>6)&3
            if sz==3:return None
            ops={0x42:'clr',0x44:'neg',0x46:'not',0x4a:'tst',0x40:'negx'}
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,SZ[sz],False)
            if ea:return Insn(end-p,ops[w>>8]+'.'+SZ[sz],ea,data_refs=ref)
        if (w&0xffc0)==0x4ac0:
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'b',False)
            if ea:return Insn(end-p,'tas',ea,data_refs=ref)
        if (w&0xffc0)==0x4800:
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'b',False)
            if ea:return Insn(end-p,'nbcd',ea,data_refs=ref)
        if g in (1,2,3):
            size={1:'b',2:'l',3:'w'}[g]
            dreg=(w>>9)&7;dmode=(w>>6)&7;smode=(w>>3)&7;sreg=w&7
            src,pos,ref1=self.ea(smode,sreg,p+2,size)
            if src is None:return None
            if dmode==1:
                if size=='b':return None
                return Insn(pos-p,'movea.'+size,f'{src},a{dreg}',data_refs=ref1)
            dst,end,ref2=self.ea(dmode,dreg,pos,size,False)
            if dst:return Insn(end-p,'move.'+size,f'{src},{dst}',data_refs=ref1+ref2)
        if g==6:
            condition=(w>>8)&15;d8=w&255
            if d8==0:
                disp=self.s16(p+2);end=p+4;suf='.w'
            elif d8==255:
                disp=self.s32(p+2);end=p+6;suf='.l'
            else:
                disp=d8-256 if d8>=128 else d8;end=p+2;suf='.s'
            dst=p+2+disp
            m='bra' if condition==0 else ('bsr' if condition==1 else 'b'+CC[condition])
            return Insn(end-p,m+suf,f'@${dst:06X}',target=dst,stop=condition==0,call=condition==1)
        if g==7 and not (w&0x100):
            val=w&255
            if val>=128:val-=256
            return Insn(2,'moveq',f'#{val},d{(w>>9)&7}')
        if g==5:
            if (w&0xf0f8)==0x50c8:
                cc=(w>>8)&15;target=p+2+self.s16(p+2)
                return Insn(4,'db'+('ra' if cc==1 else CC[cc]),f'd{w&7},@${target:06X}',target=target)
            if (w&0xf0c0)==0x50c0:
                ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'b',False)
                if ea:return Insn(end-p,'s'+CC[(w>>8)&15],ea,data_refs=ref)
            sz=(w>>6)&3
            if sz==3:return None
            amount=(w>>9)&7
            if amount==0:amount=8
            ea,end,ref=self.ea((w>>3)&7,w&7,p+2,SZ[sz],False)
            if ea:return Insn(end-p,('subq' if w&0x100 else 'addq')+'.'+SZ[sz],f'#{amount},{ea}',data_refs=ref)
        if g in (8,9,11,12,13):
            reg=(w>>9)&7;opmode=(w>>6)&7;smode=(w>>3)&7;sreg=w&7
            family={8:'or',9:'sub',11:'cmp',12:'and',13:'add'}[g]
            if opmode in (3,7):
                size='w' if opmode==3 else 'l'
                if g in (9,13,11):
                    ea,end,ref=self.ea(smode,sreg,p+2,size)
                    if ea:return Insn(end-p,{'sub':'suba','add':'adda','cmp':'cmpa'}[family]+'.'+size,f'{ea},a{reg}',data_refs=ref)
                if g in (8,12):
                    ea,end,ref=self.ea(smode,sreg,p+2,'w')
                    if ea:return Insn(end-p,('divu' if g==8 else 'mulu')+('' if opmode==3 else 's')+'.w',f'{ea},d{reg}',data_refs=ref)
            if opmode in (0,1,2):
                size=SZ[opmode]
                ea,end,ref=self.ea(smode,sreg,p+2,size)
                if ea:return Insn(end-p,family+'.'+size,f'{ea},d{reg}',data_refs=ref)
            if opmode in (4,5,6):
                size=SZ[opmode-4]
                ea,end,ref=self.ea(smode,sreg,p+2,size,False)
                if ea:return Insn(end-p,('eor' if family=='cmp' else family)+'.'+size,f'd{reg},{ea}',data_refs=ref)
        if g==0:
            # Immediate arithmetic; extension words before EA displacement.
            imms={0x0000:'ori',0x0200:'andi',0x0400:'subi',0x0600:'addi',0x0a00:'eori',0x0c00:'cmpi'}
            if (w&0xff00) in imms:
                sz=(w>>6)&3
                if sz==3:return None
                size=SZ[sz]
                imm,pos,refs=self.ea(7,4,p+2,size)
                ea,end,ref=self.ea((w>>3)&7,w&7,pos,size,False)
                if ea:return Insn(end-p,imms[w&0xff00]+'.'+size,f'{imm},{ea}',data_refs=ref)
            if w in (0x003c,0x007c,0x023c,0x027c,0x0a3c,0x0a7c):
                register='sr' if (w&0x40) else 'ccr'
                op={0:'ori',2:'andi',10:'eori'}[w>>8]
                return Insn(4,op+('.w' if register=='sr' else '.b'),f'#${self.u16(p+2):04X},{register}')
            if (w&0xf100)==0x0100 or (w&0xff00)==0x0800:
                im=(w&0x100)==0
                op={0:'btst',1:'bchg',2:'bclr',3:'bset'}[(w>>6)&3]
                source=f'#{self.u16(p+2)}' if im else f'd{(w>>9)&7}'
                ea,end,ref=self.ea((w>>3)&7,w&7,p+(4 if im else 2),'b',False)
                if ea:return Insn(end-p,op,source+','+ea,data_refs=ref)
        if g==14 and (w&0xfff8) in (0xe9d0,0xefd0):
            # OPT020: validated BFEXTU/BFINS register-indexed fields.
            # Restrict to (An); do not reinterpret unknown 020 encodings.
            ext=self.u16(p+2)
            if ext&0x8600:return None  # reserved bit15 + bits10/9
            reg=(ext>>12)&7
            offset=(f'd{(ext>>6)&7}' if ext&0x0800
                    else str((ext>>6)&31))
            width=(f'd{ext&7}' if ext&0x20
                   else str((ext&31) or 32))
            if ext&0x20 and ext&0x18:return None
            ea,end,ref=self.ea(2,w&7,p+4,'l',False)
            if not ea:return None
            field=f'{ea}{{{offset}:{width}}}'
            if (w&0xfff8)==0xe9d0:
                return Insn(end-p,'bfextu',f'{field},d{reg}',data_refs=ref)
            return Insn(end-p,'bfins',f'd{reg},{field}',data_refs=ref)
        if g==14:
            if (w&0x00c0)==0x00c0:
                direction='l' if w&0x100 else 'r';typ=['as','ls','rox','ro'][(w>>9)&3]
                ea,end,ref=self.ea((w>>3)&7,w&7,p+2,'w',False)
                if ea:return Insn(end-p,typ+direction+'.w',ea,data_refs=ref)
            else:
                sz=(w>>6)&3
                if sz==3:return None
                direction='l' if w&0x100 else 'r';typ=['as','ls','rox','ro'][(w>>3)&3]
                count=f'd{(w>>9)&7}' if w&0x20 else f'#{((w>>9)&7) or 8}'
                return Insn(2,typ+direction+'.'+SZ[sz],count+',d'+str(w&7))
        return None


def flow_decode(data:bytes,base:int=0,extra_seeds:tuple[int,...]=()):
    """Conservative recursive traversal from the AP20 entry start."""
    decoder=Decoder(data,base)
    end=base+len(data)
    instructions={}
    stack=[base,*extra_seeds]
    # All entry points start at offset zero; unknown data regions are left raw.
    while stack:
        pc=stack.pop()
        while base<=pc<end-1 and pc not in instructions:
            ins=decoder.decode(pc)
            if ins is None or pc+ins.size>end:break
            if any(a<=pc<a+x.size or pc<a<pc+ins.size for a,x in instructions.items()):break
            instructions[pc]=ins
            if ins.target is not None and base<=ins.target<end and not (ins.target&1):stack.append(ins.target)
            if ins.stop:break
            pc+=ins.size
    return instructions
