from pathlib import Path
import struct, hashlib
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'archive'/'AMOSPro_AGA_M4a_v0.0.5_WinUAE_OK.Lib'
DEST=ROOT/'dist'/'experimental'/'AMOSPro_AGA_M4b_v0.0.6.Lib'

def w(n): return struct.pack('>H', n & 0xffff)
def l(n): return struct.pack('>I', n & 0xffffffff)

class A:
    def __init__(self): self.b=bytearray(); self.labels={}; self.fix=[]
    def e(self,h): self.b += bytes.fromhex(h.replace(' ',''))
    def label(self,n): self.labels[n]=len(self.b)
    def br(self,op,label):
        # 16-bit displacement; 68k PC base is address of extension word
        pos=len(self.b); self.b += w(op)+b'\x00\x00'; self.fix.append((pos+2,label))
    def out(self):
        for ext,label in self.fix:
            disp=self.labels[label]-ext
            struct.pack_into('>h',self.b,ext,disp)
        return bytes(self.b)

def cleanup():
    a=A()
    a.e('48e7ffee')
    a.e('246d01c8')
    a.e('200a4a80'); a.br(0x6700,'exit')
    a.e('266a001c')
    a.e('200b4a80'); a.br(0x6700,'close_screen')
    a.e('2052')
    a.e('20084a80'); a.br(0x6700,'free_vec')
    a.e('226b0004')
    a.e('20094a80'); a.br(0x6700,'skip_sb1')
    a.e('20522c6a0004')
    a.e('4eaefcfa')
    a.label('skip_sb1')
    a.e('2253')
    a.e('20094a80'); a.br(0x6700,'free_vec')
    a.e('20522c6a0004')
    a.e('4eaefcfa')
    a.label('free_vec')
    a.e('224b')
    a.e('2c780004')
    a.e('4eaefd4e')
    a.e('42aa001c')
    a.label('close_screen')
    a.e('4a92'); a.br(0x6700,'close_gfx')
    a.e('20522c6a0004')
    a.e('4eaeffbe')
    a.e('4292')
    a.label('close_gfx')
    a.e('226a0008')
    a.e('20094a80'); a.br(0x6700,'close_intui')
    a.e('2c7800044eaefe62')
    a.e('42aa0008')
    a.label('close_intui')
    a.e('226a0004')
    a.e('20094a80'); a.br(0x6700,'clear_tail')
    a.e('2c7800044eaefe62')
    a.e('42aa0004')
    a.label('clear_tail')
    a.e('41ea000c7004429851c8fffc')
    a.label('exit')
    a.e('4cdf77ff4e75')
    return a.out()

def double_buffer():
    a=A(); a.e('48e7ffee'); a.e('7600')
    a.e('246d01c8')
    a.e('200a4a80'); a.br(0x6700,'done')
    a.e('4a92'); a.br(0x6700,'done')
    a.e('266a001c')
    a.e('200b4a80'); a.br(0x6600,'already')
    a.e('7010223c000100012c7800044eaefd54')
    a.e('4a80'); a.br(0x6700,'done')
    a.e('2640')
    a.e('205293c970012c6a00044eaefd00')
    a.e('4a80'); a.br(0x6700,'fail_vec')
    a.e('2680')
    a.e('205293c970022c6a00044eaefd00')
    a.e('4a80'); a.br(0x6700,'fail_sb0')
    a.e('27400004')
    a.e('254b001c')
    a.label('already')
    a.e('7601'); a.br(0x6000,'done')
    a.label('fail_sb0')
    a.e('205222532c6a00044eaefcfa')
    a.label('fail_vec')
    a.e('224b2c7800044eaefd4e')
    a.label('done')
    a.e('4cdf77ff74004e75')
    return a.out()

def swap():
    a=A(); a.e('48e7ffee7600')
    a.e('246d01c8')
    a.e('200a4a80'); a.br(0x6700,'done')
    a.e('4a92'); a.br(0x6700,'done')
    a.e('266a001c')
    a.e('200b4a80'); a.br(0x6700,'done')
    a.e('202b00084a80'); a.br(0x6700,'front0')
    a.e('22537e00'); a.br(0x6000,'have_target')
    a.label('front0')
    a.e('226b00047e01')
    a.label('have_target')
    a.e('20094a80'); a.br(0x6700,'done')
    a.e('2849')
    a.e('2c6a00084eaeff1c')
    a.e('2052224c2c6a00044eaefcf4')
    a.e('4a80'); a.br(0x6700,'done')
    a.e('27470008')
    a.e('7601')
    a.label('done')
    a.e('4cdf77ff74004e75')
    return a.out()

def back_fill():
    a=A(); a.e('48e7ffee2e03')
    a.e('246d01c8')
    a.e('200a4a80'); a.br(0x6700,'done')
    a.e('4a92'); a.br(0x6700,'done')
    a.e('266a001c')
    a.e('200b4a80'); a.br(0x6700,'done')
    a.e('202b00084a80'); a.br(0x6700,'front0')
    a.e('2253'); a.br(0x6000,'have_sb')
    a.label('front0')
    a.e('226b0004')
    a.label('have_sb')
    a.e('20094a80'); a.br(0x6700,'done')
    a.e('2851')
    a.e('2052')
    a.e('2c280058')
    a.e('214c0058')
    a.e('0287000000ff')
    a.e('43e80054')
    a.e('2007')
    a.e('2c6a0008')
    a.e('4eaeff16')
    a.e('4eaeff1c')
    a.e('2052')
    a.e('21460058')
    a.label('done')
    a.e('4cdf77ff4e75')
    return a.out()

def token(name,statement,index,params=''):
    name=name.encode('ascii'); tn=name[:-1]+bytes((name[-1]|128,))
    return ((w(index)+w(1)) if statement else (w(1)+w(index)))+tn+(b'I' if statement else b'0')+params.encode()+b'\xff'

def build():
    old=BASE.read_bytes(); assert hashlib.sha256(old).hexdigest()=='ae4b863083e32c38e85192ac760aa143d3585c51d600449056075111da213b0e'
    d=old[32:-4]; off,toklen,liblen,titlelen=struct.unpack_from('>4I',d); assert off==22
    oj=list(struct.unpack_from('>11H',d,22)); assert oj==[94,2,8,8,48,167,193,75,52,13,0]
    tok=d[44:44+toklen]; lib=d[44+toklen:44+toklen+liblen]
    seg=[]; p=0
    for n in oj:
        seg.append(lib[p:p+n*2]); p += n*2
    assert p==len(lib)
    cl=cleanup(); db=double_buffer(); sw=swap(); bf=back_fill()
    init=bytearray(seg[0][:56]); assert seg[0][-32:]==b'\0'*32
    state_start=56+len(cl)
    struct.pack_into('>h',init,12,state_start-12)
    struct.pack_into('>h',init,32,state_start-32)
    newcold=bytes(init)+cl+b'\0'*32
    assert seg[8][-4:]==b'GetP'
    new8=cl+b'GetP'
    new9=seg[9]+b'GetP'
    new10=db+b'GetP'
    new11=sw+b'GetP'
    new12=bf
    newsegs=[newcold]+seg[1:8]+[new8,new9,new10,new11,new12,b'']
    assert all(len(x)%2==0 for x in newsegs)
    jumps=[len(x)//2 for x in newsegs]
    newlib=b''.join(newsegs)
    newtok=(tok[:-6]
            +token('aga double buffer',False,10)
            +token('aga swap',False,11)
            +token('aga back fill',True,12,'0')
            +b'\0'*6)
    if len(newtok)&1:newtok+=b'\0'
    title=b'AMOSPro AGA M4b experimental 0.0.6\0$VER: AMOSPro_AGA 0.0.6\0'
    if len(title)&1:title+=b'\0'
    jumpbytes=len(jumps)*2
    header=l(jumpbytes)+l(len(newtok))+l(len(newlib))+l(len(title))+b'\0\0AP20'
    payload=bytearray(header+b''.join(w(v) for v in jumps)+newtok+newlib+title+b'\0\0')
    while len(payload)&3:payload+=b'\0'
    n=len(payload)//4
    return old[:20]+l(n)+old[24:28]+l(n)+payload+old[-4:]

M4B_SHA='03d48deefc90345f6d8cb9c109ba9a53b8046a6041f93fc9cb8fab91b3a95e20'

if __name__=='__main__':
    b=build()
    assert hashlib.sha256(b).hexdigest()==M4B_SHA
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_bytes(b)
    print('Generated',DEST)
    print('SHA256',M4B_SHA)
    print('Runtime validation required: WinUAE interpreted, then compiled.')
