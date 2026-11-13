"""Host-only M18 FICON8 sample ABK format and canonical mask integrity."""
from m18_ficon16_abk import binary,parse_abk,make_abk,sample_icons
from m18_ficon16_model import build_bank
def bad(fn):
    try:fn()
    except ValueError:return
    raise AssertionError("invalid FICON8 bank accepted")
def main():
    abk=binary()
    assert len(abk)==20+12+4*288
    n,flags,bank=parse_abk(abk)
    assert (n,flags,bank.count)==(10,1,4)
    assert abk==make_abk(10,build_bank(sample_icons()))
    assert parse_abk(make_abk(10,bank.raw,chip=True))[1]==3
    bad(lambda:make_abk(4,bank.raw))
    bad(lambda:make_abk(65536,bank.raw))
    bad(lambda:parse_abk(abk[:18]))
    bad(lambda:parse_abk(abk[:-1]))
    v=bytearray(abk);v[12]^=1;bad(lambda:parse_abk(bytes(v)))
    v=bytearray(abk);v[20+12+3*288]^=1;bad(lambda:parse_abk(bytes(v)))
    print("M18 FICON8 ABK HOST PASS:",len(abk),
          "bytes, 4 icons, 8 planes, corrupt size/mask/header rejected")
if __name__=="__main__":
    main()
