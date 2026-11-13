"""P5 host cache: format, stage, reuse, opaque/transparent and clipping."""
from random import Random
from m18_ficon_chip_cache import (
    empty_payload,make_abk,parse_abk,parse_cache,stage,draw_model,HEADER,SLOT
)
from m18_ficon16_model import build_bank,parse_bank,draw_cpu
from test_m18_ficon16_native_aligned import as_planar,WIDTH,HEIGHT,STRIDE

def fail(fn):
    try:fn()
    except ValueError:return
    raise AssertionError("malformed cache/source accepted")

def main():
    rng=Random(0xFACE2026)
    icons=(bytes(256),bytes([255])*256,
           bytes((19*x+9*y)&255 for y in range(16) for x in range(16)),
           bytes(rng.randrange(256) if (x+y)%3 else 0
                 for y in range(16) for x in range(16)))
    src=build_bank(icons)
    cache=empty_payload(4)
    assert len(cache)==12+4*289 and len(make_abk())==20+len(cache)
    assert parse_abk(make_abk())[0]==11
    fail(lambda: parse_cache(cache[:-1]))
    fail(lambda: parse_abk(make_abk()[:-1]))
    fail(lambda: parse_cache(cache[:12]+bytes([7])*4*289))
    fail(lambda: stage(cache,src,5))
    fail(lambda: parse_cache(cache).slot(1))
    # Every icon staged exactly once; repeated rendering does NOT re-stage.
    for n in (1,2,3,4):cache=stage(cache,src,n)
    assert parse_cache(cache).count==4
    malformed=bytearray(cache);malformed[12]=0xff
    fail(lambda:parse_cache(bytes(malformed)))
    cases=0
    bank=parse_bank(src)
    for index in range(1,5):
        for x in (-17,-16,-15,-1,0,1,7,15,16,49,64,65,72):
            for y in (-17,-15,-1,0,17,42,43,54):
                for mode in (0,1):
                    raw=bytes(rng.randrange(256) for _ in range(WIDTH*HEIGHT))
                    a=as_planar(raw);b=[bytearray(z) for z in a]
                    draw_model(cache,index,x,y,mode,a,WIDTH,HEIGHT,STRIDE)
                    draw_cpu(bank,index,x,y,mode,b,WIDTH,HEIGHT,STRIDE)
                    assert a==b,(index,x,y,mode)
                    cases+=1
    # Re-stage after source bank changed, with validity tracked independently.
    changed=build_bank((icons[1],icons[1],icons[2],icons[3]))
    after=stage(cache,changed,1)
    assert after!=cache and parse_cache(after).slot(2)==parse_cache(cache).slot(2)
    fail(lambda:draw_model(empty_payload(4),1,0,0,0,[],WIDTH,HEIGHT,STRIDE))
    fail(lambda:draw_model(after,1,0,0,2,as_planar(bytes(WIDTH*HEIGHT)),WIDTH,HEIGHT,STRIDE))
    print("M18/P5 CHIP CACHE HOST PASS:",cases,
          "pixel-equivalence cases; 4 independent persistent slots; guards/invalids")
if __name__=="__main__":
    main()
