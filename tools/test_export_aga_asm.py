#!/usr/bin/env python3
"""Independent synthetic AP20 smoke tests for lossless export."""
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from struct import pack
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent))
import export_aga_asm as x


def token(name, instr, fn, sig):
    name = name.encode('ascii')
    v = pack('>HH', instr, fn) + name[:-1] + bytes([name[-1] | 0x80]) + sig.encode('ascii') + b'\xff'
    return v + bytes(len(v) % 2)


def fixture():
    # The GetP delimiter belongs to the preceding AP20 entry.
    segments = [b'\x4e\x75', b'\x4e\x75GetP', b'\x70\x01\x4e\x75']
    codes = b''.join(segments)
    tokens = b'\x00\x01\x00\x00\x80\xff' + token('aga smoke', 1, 2, '0') + b'\0'*6
    title = b'AMOSPro AGA TEST R88 0.8.8\0'
    title += bytes(len(title) % 2)
    payload = (pack('>4I', len(segments)*2, len(tokens), len(codes), len(title)) +
               b'\0\0AP20' + b''.join(pack('>H', len(s)//2) for s in segments) +
               tokens + codes + title + b'\0\0')
    payload += bytes(-len(payload) % 4)
    words = len(payload)//4
    return pack('>8I', 0x3f3, 0, 1, 0, 0, words, 0x3e9, words) + payload + pack('>I', 0x3f2)


def test():
    binary = fixture()
    ap = x.parse_ap20(binary)
    assert len(ap.segments) == 3
    assert ap.segments[1].data.endswith(b'GetP')
    assert ap.segments[2].names == ('aga smoke [fn]',)
    src, lst, manifest = x.export_asm(ap, None, None)
    assert x.decode_exact_asm(src) == binary
    assert 'GetP parameter-dispatch' in src
    assert 'aga smoke [fn]' in lst
    assert manifest['sha256'] == x.sha(binary)

    broken = binary[:-4] + b'XXXX'
    try:
        x.parse_ap20(broken)
    except x.ExportError:
        pass
    else:
        raise AssertionError('truncated header was accepted')

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / 'dist/experimental').mkdir(parents=True)
        (root / 'tools').mkdir()
        archive = root / 'dist/experimental/TEST.Lib'
        archive.write_bytes(binary)
        builder = root / 'tools/build_test.py'
        builder.write_text("ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]\n"
                           "ARCHIVE = ROOT / 'dist/experimental/TEST.Lib'\n"
                           "def build():\n"
                           "    return ARCHIVE.read_bytes(), {'status': 'fixture'}\n"
                           "if __name__ == '__main__':\n"
                           "    raise RuntimeError('publication path should not run')\n")
        previous_root = x.ROOT
        try:
            x.ROOT = root
            assert x.find_matching_builder(binary) == builder
            created, report = x.build_in_memory(builder)
            assert created == binary and report['status'] == 'fixture'

            # Real-world regression: a builder may throw an empty AssertionError
            # on the local Windows checkout. Auto export must still succeed
            # because the archive has already been verified byte-for-byte.
            builder.write_text(
                "from pathlib import Path\n"
                "ROOT = Path(__file__).resolve().parents[1]\n"
                "ARCHIVE = ROOT / 'dist/experimental/TEST.Lib'\n"
                "def build():\n"
                "    assert False  # no error message\n", encoding='utf-8')
            (root / 'dist/AMOSPro_AGA.Lib').write_bytes(binary)
            out = root / 'asm_export'
            arg = ['--lib', 'dist/AMOSPro_AGA.Lib', '--out', str(out), '--no-capstone']
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                assert x.main(arg) == 0  # automatic archive-based mode bypasses build()
            assert x.decode_exact_asm(next(out.glob('*.s')).read_text()) == binary

            # Explicit rebuild must fail informatively and print a traceback.
            failure = StringIO()
            with redirect_stdout(StringIO()), redirect_stderr(failure):
                assert x.main(arg + ['--verify-builder']) == 1
            assert 'AssertionError' in failure.getvalue()
            assert 'Traceback' in failure.getvalue()
            assert 'Builder build() failed' in failure.getvalue()
        finally:
            x.ROOT = previous_root
    print('PASS: AP20/token, GetP, lossless roundtrip, auto builder archive, empty-assert regression, full traceback')


if __name__ == '__main__':
    test()
