"""Small explicit 68000 encoder. No instruction scanning or heuristic relocation.

Only encodes the addressing modes/instructions used by the ILBM builder.
Branch targets are labels, resolved and range checked after generation.
"""
import struct

def w(n): return struct.pack('>H', n & 0xffff)
def l(n): return struct.pack('>I', n & 0xffffffff)
def D(n): return (n,b'')
def A(n): return (8+n,b'')
def M(n,off=0): return (40+n,w(off)) if off else (16+n,b'')
def POST(n): return (24+n,b'')
def PRE(n): return (32+n,b'')
def I(value,size='l'): return (60,l(value) if size=='l' else w(value))

class Code:
    def __init__(self): self.b=bytearray(); self.labels={}; self.fix=[]
    def raw(self,s): self.b.extend(bytes.fromhex(s))
    def word(self,n): self.b.extend(w(n))
    def label(self,name):
        assert name not in self.labels, name
        self.labels[name]=len(self.b)
    def branch(self,condition,label):
        self.word(0x6000 | (condition<<8)); self.fix.append((len(self.b),label)); self.word(0)
    def lea(self,reg,label):
        self.word(0x41fa | reg<<9); self.fix.append((len(self.b),label)); self.word(0)
    def move(self,src,dst,size='l'):
        se,sx=src; de,dx=dst
        self.word({'b':0x1000,'w':0x3000,'l':0x2000}[size] | (de&7)<<9 | (de>>3)<<6 | se)
        self.b.extend(sx); self.b.extend(dx)
    def imm(self,op,n,dst,size='l'):
        de,dx=dst
        self.word({'or':0,'and':0x200,'sub':0x400,'add':0x600,'cmp':0xc00}[op] | {'b':0,'w':0x40,'l':0x80}[size] | de)
        self.b.extend(l(n) if size=='l' else w(n)); self.b.extend(dx)
    def alu(self,op,src,reg,size='l'):
        se,sx=src
        self.word({'sub':0x9000,'cmp':0xb000,'and':0xc000,'add':0xd000,'or':0x8000}[op] | reg<<9 | {'b':0,'w':0x40,'l':0x80}[size] | se)
        self.b.extend(sx)
    def quick(self,n,dst,sub=False,size='l'):
        de,dx=dst
        self.word(0x5000 | (n&7)<<9 | (0x100 if sub else 0) | {'b':0,'w':0x40,'l':0x80}[size] | de); self.b.extend(dx)
    def tst(self,src,size='l'):
        se,sx=src; self.word(0x4a00 | {'b':0,'w':0x40,'l':0x80}[size] | se); self.b.extend(sx)
    def shift(self,reg,n,left=False): self.word(0xe088 | (n&7)<<9 | (0x100 if left else 0) | reg)
    def call_os(self,offset): self.word(0x4eae); self.word(offset)
    def out(self):
        for pos,label in self.fix:
            displacement=self.labels[label]-pos
            assert not self.labels[label]&1 and -32768<=displacement<=32767,(pos,label)
            self.b[pos:pos+2]=w(displacement)
        return bytes(self.b)
