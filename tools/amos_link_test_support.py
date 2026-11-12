"""Independent test model of +B.s table loading and GRouJ/GRouB.

This models interpreter relocation and separately placed Compiler routines.
It is NOT the AMOS loader or Compiler running under WinUAE.
Only bank service effects are mocked; symbol numbering is fixture-derived.
"""
from struct import pack, unpack_from
from amos_main_abi import declarations

LB_SIZE=36
MAIN_TOKENS=0x48000
MAIN_BASE=0x30000
EMPTY=0x34f00

def main_table(uc):
    entries=declarations()
    names={idx:name for idx,name,*_ in entries}
    # Shuffled addresses: a mock service address cannot be inferred from index*16.
    table={i:MAIN_BASE+((i*37+19)%1024)*16 for i in names}
    # +ILib.s:5339-5350, consecutive definitions: PrintE..UsingC empty.
    for i in range(318,329):
        table[i]=EMPTY
    uc.mem_write(EMPTY,bytes.fromhex("4afc"))  # +B.s Ll_Rts is ILLEGAL
    for idx,addr in table.items():
        uc.mem_write(MAIN_TOKENS-LB_SIZE-4-4*idx,pack(">I",addr))
    # Lib_Par puts GetP BEFORE the callable label, never at the target.
    one=next(i for i,n in names.items() if n=="FnOne")
    uc.mem_write(table[one]-4,b"GetP")
    uc.mem_write(table[one],bytes.fromhex("760174004e75"))
    return table,names

def relocate(part,base,local,uc):
    out=bytearray(part)
    pos=0
    while pos+4<=len(out):
        op=unpack_from(">H",out,pos)[0]
        if op==0xfef1 and out[pos+2:pos+4]==bytes.fromhex("6543"):
            out[pos:pos+4]=bytes.fromhex("4e714e71")
            break
        if op in (0xfe11,0xfe01) and out[pos+2]==0xf7:
            if pos+6>len(out):
                raise ValueError("truncated Rjsr")
            slot=out[pos+3]
            if slot!=0:
                raise ValueError("test fixture only implements main-library calls")
            idx=unpack_from(">H",out,pos+4)[0]
            names={e[0] for e in declarations()}
            if idx not in names:
                raise ValueError("unknown main index")
            # Real negative table access from +B.s:2596-2598, not producer ID mapping.
            addr=unpack_from(">I",uc.mem_read(MAIN_TOKENS-LB_SIZE-4-4*idx,4))[0]
            out[pos:pos+6]=pack(">HI",0x4eb9 if op==0xfe11 else 0x4ef9,addr)
            pos+=6
        elif op==0xfe31:
            idx=unpack_from(">H",out,pos+2)[0]
            delta=local[idx]-(base+pos+2)
            if not -32766<delta<32766:
                raise ValueError("Rbsr signed displacement overflow")
            out[pos:pos+4]=pack(">Hh",0x6100,delta)
            pos+=4
        else:
            pos+=2
    return bytes(out)
