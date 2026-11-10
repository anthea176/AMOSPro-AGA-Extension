from pathlib import Path
from struct import pack,unpack_from
from hashlib import sha256

def split(raw):
    assert unpack_from('>I',raw)[0] == 0x3F3
    assert unpack_from('>I',raw,24)[0] == 0x3E9
    count=unpack_from('>I',raw,28)[0]
    assert len(raw)==36+count*4 and raw[-4:]==pack('>I',0x3F2)
    jb,tb,cb,nz=unpack_from('>4I',raw,32)
    assert raw[48:54]==b'\x00\x00AP20'
    sizes=unpack_from('>'+str(jb//2)+'H',raw,54)
    start=54+jb;tokens=raw[start:start+tb]
    code=raw[start+tb:start+tb+cb]
    title=raw[start+tb+cb:start+tb+cb+nz]
    assert sum(sizes)*2==len(code)
    parts=[];p=0
    for s in sizes:
        parts.append(code[p:p+2*s]);p+=2*s
    return tokens,parts,title

def rebuild(base,parts,title):
    tokens,old,t=split(base)
    assert len(parts)==len(old) and not any(len(s)&1 for s in parts)
    code=b''.join(parts)
    data=(pack('>4I',len(parts)*2,len(tokens),len(code),len(title))+
          b'\x00\x00AP20'+b''.join(pack('>H',len(s)//2) for s in parts)+tokens+code+title+b'\x00\x00')
    data+=bytes(-len(data)%4)
    words=len(data)//4
    out=base[:20]+pack('>I',words)+base[24:28]+pack('>I',words)+data+base[-4:]
    assert split(out)[1]==parts
    return out

def digest(x):return sha256(x).hexdigest()

class Asm:
    def __init__(self):self.b=bytearray();self.labels={};self.fix=[]
    def emit(self,h):self.b+=bytes.fromhex(h.replace(' ',''))
    def label(self,n):assert n not in self.labels;self.labels[n]=len(self.b)
    def branch(self,op,label):
        p=len(self.b)
        self.b+=pack('>H',op)+b'\x00\x00'
        self.fix.append((p+2,label))
    def out(self):
        from struct import pack_into
        for p,n in self.fix:
            assert n in self.labels
            d=self.labels[n]-p
            assert -32768<=d<32768
            pack_into('>h',self.b,p,d)
        return bytes(self.b)
