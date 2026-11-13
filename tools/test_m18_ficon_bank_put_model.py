"""R65 host oracle for bulk FICON8 chunky import (not native Gate A/B)."""
from m18_ficon16_model import build_bank,parse_bank
from m18_ficon_bank_put_model import chunky_to_slot,put_chunky

def main():
    zero=bytes(256)
    blank=build_bank((zero,)*4)
    samples=(
        bytes([0]*256),
        bytes([255]*256),
        bytes((x*17+y*11)&255 for y in range(16) for x in range(16)),
        bytes((0 if (x+y)%3==0 else ((x*13+y*7)&255)) for y in range(16) for x in range(16)),
        bytes((1<<(x%8)) if (x+y)%2 else 0 for y in range(16) for x in range(16)),
        bytes(128 if x in (0,15) or y in (0,15) else 0 for y in range(16) for x in range(16)),
    )
    checks=0
    for pix in samples:
        slot=chunky_to_slot(pix)
        assert slot==parse_bank(build_bank((pix,)*4)).icon(1)
        source=b"header"+pix+b"sentinel"
        for target in (1,2,3,4):
            out=put_chunky(blank,target,source,6)
            parsed=parse_bank(out)
            assert parsed.icon(target)==slot
            for k in (1,2,3,4):
                if k!=target: assert parsed.icon(k)==parse_bank(blank).icon(k)
            checks+=1
    # Cross-slot and large-bank end; no data outside the target 288 bytes.
    large=build_bank((zero,)*4096)
    pattern=samples[3]
    final=put_chunky(large,4096,pattern,0)
    assert final[:-288]==large[:-288] and final[-288:]==chunky_to_slot(pattern)
    checks+=1
    def invalid(fn):
        nonlocal checks
        try: fn()
        except (ValueError,TypeError):checks+=1;return
        raise AssertionError("expected non-destructive rejection")
    for options in [
        dict(icon_id=0),dict(icon_id=5),dict(icon_id=-1),dict(icon_id=1.0),
        dict(offset=-1),dict(offset=1),dict(offset=2**32),dict(offset=1.0),
        dict(dest_number=4),dict(dest_number=65536),dict(dest_number=-1),
        dict(source_number=4),dict(source_number=65536),dict(source_number=12),
        dict(source=b""),dict(source=b"short"),dict(source=bytearray(256)),
    ]:
        args=dict(bank=blank,icon_id=1,source=zero,offset=0)
        args.update(options)
        invalid(lambda args=args:put_chunky(**args))
    corrupted=bytearray(blank);corrupted[12]=0
    invalid(lambda:put_chunky(bytes(corrupted),1,zero,0))
    invalid(lambda:chunky_to_slot(b"\0"*255))
    print("M18/R65 FICON8 BANK PUT HOST MODEL PASS",checks,"cases, no native implementation yet")
if __name__=="__main__":main()
