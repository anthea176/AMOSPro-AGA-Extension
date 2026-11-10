from pathlib import Path
from ap20_utils import split,rebuild,Asm,digest
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.5.7_INTUITION_INPUT_R6.Lib'
OUT=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.5.8_DB_POINTER_R7.Lib'
EXPECTED='e6dd32ceda1181ef3172dfb242a1d4fc93656c6788023d7b1333dc2561ed3dce'
def assemble(fixed):
    a=Asm();a.emit('48e7effe7600246d01c84a92');a.branch(0x6700,'done')
    a.emit('286a0020200c4a80');a.branch(0x6600,'already')
    a.emit('7018223c000100012c7800044eaefd544a80');a.branch(0x6700,'done')
    a.emit('2840')
    a.emit('2c7800044eaefd664a80');a.branch(0x6700,'fail_vec')
    a.emit('2940000c')
    a.emit('2c7800044eaefd664a80');a.branch(0x6700,'fail_ports')
    a.emit('29400010')
    a.emit('205293c970012c6a00044eaefd004a80');a.branch(0x6700,'fail_ports')
    a.emit('2880')
    a.emit('205293c970022c6a00044eaefd004a80');a.branch(0x6700,'fail_sb0')
    a.emit('29400004')
    a.emit('20542068000420084a80' if fixed else '205420684a80');a.branch(0x6700,'fail_both')
    a.emit('202c000c21400016202c001021400036')
    a.emit('206c00042068000420084a80' if fixed else '206c000420684a80');a.branch(0x6700,'fail_both')
    a.emit('202c000c21400016202c001021400036')
    a.emit('254c0020')
    a.label('already');a.emit('7601');a.branch(0x6000,'done')
    a.label('fail_both');a.emit('2052226c00042c6a00044eaefcfa')
    a.label('fail_sb0');a.emit('205222542c6a00044eaefcfa')
    a.label('fail_ports');a.emit('2c780004206c001020084a80');a.branch(0x6700,'skip_disp')
    a.emit('4eaefd60')
    a.label('skip_disp');a.emit('206c000c20084a80');a.branch(0x6700,'fail_vec')
    a.emit('4eaefd60')
    a.label('fail_vec');a.emit('224c2c7800044eaefd4e')
    a.label('done');a.emit('4cdf7ff774004e75')
    return a.out()
def build():
    raw=BASE.read_bytes()
    assert len(raw)==7948 and digest(raw)=='729fc13efbaa710a371048353368ffe3dd5af0a23d0043d1e6ee3bcf2e5330d9'
    tokens,ss,title=split(raw)
    assert ss[10]==assemble(False)+b'GetP'
    new=list(ss);new[10]=assemble(True)+b'GetP'
    title=title.replace(b'Intuition Input R6 0.5.7',b'Intuition Input R7 0.5.8').replace(b'AMOSPro_AGA 0.5.7',b'AMOSPro_AGA 0.5.8')
    rebuilt=rebuild(raw,new,title)
    assert len(rebuilt)==7956 and digest(rebuilt)==EXPECTED,(len(rebuilt),digest(rebuilt))
    return rebuilt
if __name__=='__main__':
    data=build();OUT.write_bytes(data)
    print('R7 EXACT RECONSTRUCTION',len(data),digest(data))
