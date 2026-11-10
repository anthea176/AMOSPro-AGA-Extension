"""Minimal reproduction of the project's current 68000 emitter for an independent R19 check."""
import struct

def w(n): return struct.pack('>H', n & 0xffff)
def l(n): return struct.pack('>I', n & 0xffffffff)
def D(n): return (n,b'')
def A(n): return (8+n,b'')
def M(n,off=0): return (40+n,w(off)) if off else (16+n,b'')
def I(value,size='l'): return (60,l(value) if size=='l' else w(value))
class Code:
    def __init__(self): self.b=bytearray(); self.labels={}; self.fix=[]
    def raw(self,s): self.b.extend(bytes.fromhex(s))
    def word(self,n): self.b.extend(w(n))
    def label(self,name):
        assert name not in self.labels,name
        self.labels[name]=len(self.b)
    def branch(self,condition,label):
        self.word(0x6000|(condition<<8)); self.fix.append((len(self.b),label)); self.word(0)
    def move(self,src,dst,size='l'):
        se,sx=src; de,dx=dst
        self.word({'b':0x1000,'w':0x3000,'l':0x2000}[size]|(de&7)<<9|(de>>3)<<6|se)
        self.b.extend(sx); self.b.extend(dx)
    def alu(self,op,src,reg,size='l'):
        se,sx=src
        self.word({'sub':0x9000,'cmp':0xb000,'and':0xc000,'add':0xd000,'or':0x8000}[op]|reg<<9|{'b':0,'w':0x40,'l':0x80}[size]|se)
        self.b.extend(sx)
    def tst(self,src,size='l'):
        se,sx=src; self.word(0x4a00|{'b':0,'w':0x40,'l':0x80}[size]|se); self.b.extend(sx)
    def out(self):
        for pos,label in self.fix:
            displacement=self.labels[label]-pos
            assert not self.labels[label]&1 and -32768<=displacement<=32767,(pos,label)
            self.b[pos:pos+2]=w(displacement)
        return bytes(self.b)

def mouse_routine(axis):
    """Exact public R19 emitter transcribed from validated builder (no HUNK writes)."""
    assert axis in ('x','y')
    STATE_PTR=0x1c8
    c=Code()
    c.raw('48e7efee')
    c.move(M(5, STATE_PTR), A(2))
    c.move(A(2), D(0))
    c.tst(D(0))
    c.branch(7, 'bad')
    c.move(M(2, 0), A(4))
    c.move(A(4), D(0))
    c.tst(D(0))
    c.branch(7, 'bad')
    c.move(M(2, 36), A(1))
    c.move(A(1), D(0))
    c.tst(D(0))
    c.branch(7, 'bad')
    c.move(M(1, 46), D(0))
    c.move(A(4), D(1))
    c.alu('cmp',D(1),0)
    c.branch(6,'bad')
    max_off,mouse_off,edge_off=((12,14,4) if axis=='x' else (16,12,6))
    c.move(M(2,max_off),D(0))
    c.tst(D(0))
    c.branch(7,'bad')
    c.branch(11,'bad')
    c.move(M(1,mouse_off),D(3),size='w')
    c.raw('48c3')
    c.move(M(1,edge_off),D(1),size='w')
    c.raw('48c1')
    c.alu('add',D(1),3)
    c.tst(D(3))
    c.branch(11,'bad')
    c.alu('cmp',D(0),3)
    c.branch(4,'bad')
    c.branch(0,'done')
    c.label('bad')
    c.move(I(-1),D(3))
    c.label('done')
    c.raw('4cdf77f7')
    c.raw('74004e75')
    return c.out(),c.labels
