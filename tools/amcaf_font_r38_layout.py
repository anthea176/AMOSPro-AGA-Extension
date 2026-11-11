"""Read-only AMCAF V1.31+ monochrome BankFont reference format.

This is a format model for R38, not an AMOS memory-bank authenticator. A
loaded ABK has a native AMOS header at Start(bank)-24 and begins its payload
at Start(bank), unlike the 20-byte AmBk file envelope.
"""
from dataclasses import dataclass
from struct import unpack_from

MAGIC = b'FONT'
TYPE = b'BankFont'
FONT_AT = 24
NAME_AT = 76
MAX_BYTES = 65535


@dataclass(frozen=True)
class BankFont:
    total: int
    bitmap_at: int
    loc_at: int
    ysize: int
    xsize: int
    baseline: int
    modulo: int
    lo: int
    hi: int
    glyphs: int
    name: bytes
    proportional: bool


def read_bankfont(data: bytes) -> BankFont:
    if not isinstance(data, (bytes, bytearray)) or not 112 <= len(data) <= MAX_BYTES:
        raise ValueError('bank size')
    if data[:4] != MAGIC:
        raise ValueError('AMCAF FONT signature')
    bitmap_at, loc_at = unpack_from('>H', data, 10)[0], unpack_from('>H', data, 14)[0]
    if not NAME_AT + 2 <= bitmap_at < loc_at < len(data):
        raise ValueError('table offsets')
    ysize, xsize, baseline = (unpack_from('>H', data, off)[0] for off in (44, 48, 50))
    modulo = unpack_from('>H', data, 62)[0]
    lo, hi, style = data[56], data[57], data[46]
    if not (1 <= ysize <= 255 and 1 <= xsize <= 255 and 0 <= baseline < ysize):
        raise ValueError('font metrics')
    if not 0 < modulo < 32768 or modulo % 2:
        raise ValueError('bitmap stride')
    glyphs = hi - lo + 2
    proportional = bool(data[47] & 0x20)
    # Fixed-width BankFont stores only CharLoc. Proportional BankFont
    # additionally stores CharSpace (2 bytes/glyph) and CharKern (2).
    expected_end = loc_at + glyphs * (8 if proportional else 4)
    if lo > hi or expected_end != len(data):
        raise ValueError('character tables (fixed or proportional)')
    if (loc_at - bitmap_at) != ysize * modulo:
        raise ValueError('bitmap byte extent')
    if style & 0x40 or data[68:76] != b'\0' * 8:
        raise ValueError('color/proportional font unsupported in R38')
    if data[32] != 12:
        raise ValueError('invalid TextFont node type')
    terminator = data.find(b'\0', NAME_AT, bitmap_at)
    if terminator <= NAME_AT:
        raise ValueError('missing font name')
    name = data[NAME_AT:terminator]
    if any(c < 32 or c >= 127 for c in name):
        raise ValueError('invalid font name')
    for i in range(hi - lo + 2):
        bit, width = unpack_from('>HH', data, loc_at + i*4)
        if width > (256 if proportional else xsize) or bit + width > modulo * 8:
            raise ValueError('glyph out of bitmap bounds')
    return BankFont(len(data), bitmap_at, loc_at, ysize, xsize, baseline,
                    modulo, lo, hi, glyphs, name, proportional)


def synthetic_abk() -> bytes:
    """Original test glyph bits; reproduces AMCAF layout without redistributing Topaz."""
    from struct import pack, pack_into
    data = bytearray(2860)
    data[0:4] = MAGIC
    pack_into('>H', data, 10, 106)
    pack_into('>H', data, 14, 1960)
    data[32] = 12               # NT_FONT
    pack_into('>I',data,34,0x00abc100)  # old stale ln_Name (must be patched)
    pack_into('>I',data,38,0x00abc200)  # stale tf_Extension (must be cleared)
    pack_into('>H',data,44,9)       # tf_YSize
    data[46:48] = b'\x00\x48'   # font style + harmless attributes
    pack_into('>H',data,48,10)      # tf_XSize
    pack_into('>H',data,50,6)       # tf_Baseline
    pack_into('>H',data,52,1)       # tf_BoldSmear
    pack_into('>H',data,54,0x270f)  # stale accessors (must be cleared)
    data[56:58] = bytes((32,255))
    pack_into('>I',data,58,0x00abc300) # stale CharData
    pack_into('>H',data,62,206)
    pack_into('>I',data,64,0x00abc400) # stale CharLoc
    data[76:76+len(b'r38test.font')+1] = b'r38test.font\0'
    for i in range(1854):
        data[106+i] = ((i*73 + 39) ^ (i>>3)) & 0xff
    for i in range(225):
        pack_into('>HH',data,1960+i*4,(i*7)%1631,10)
    header=pack('>4sHHI8s',b'AmBk',10,0,0x80000000|(len(data)+8),TYPE)
    result=header+data
    assert len(result)==2880
    return result


def read_abk(raw: bytes) -> tuple[int, BankFont]:
    if len(raw) < 20 or raw[:4] != b'AmBk':
        raise ValueError('not AMOS bank file')
    bank, flags = unpack_from('>HH', raw, 4)
    length = unpack_from('>I', raw, 8)[0]
    if not 5 <= bank <= 65535 or flags & ~2 or raw[12:20] != TYPE:
        raise ValueError('not a BankFont bank')
    if (length & 0x7fffffff) != len(raw) - 12:
        raise ValueError('invalid AmBk envelope size')
    return bank, read_bankfont(raw[20:])


if __name__ == '__main__':
    from pathlib import Path
    p = Path(__file__).resolve().parent / 'AMCAF_FONT9.abk'
    print(read_abk(p.read_bytes()))
