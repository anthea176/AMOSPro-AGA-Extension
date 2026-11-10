#!/usr/bin/env python3
"""Read-only, lossless AP20/HUNK -> Motorola 68k assembly export.

A current Python builder can be executed via its build() function, without
executing its ``if __name__ == '__main__'`` publication code. The output
contains the exact original byte sequence as DC.W/DC.B and an optional
Capstone mnemonic listing. This is NOT a recovery of the original symbolic
source and it does not replace the validated Python build chain.

Only the generated output directory is written by this script.
Requires Python 3.9+. Capstone 5 is optional for instruction mnemonics.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import runpy
import struct
import sys
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]


class ExportError(ValueError):
    """Unsupported, corrupted or inconsistent input."""


def check(ok: bool, message: str) -> None:
    if not ok:
        raise ExportError(message)


def sha(data: bytes) -> str:
    return sha256(data).hexdigest()


@dataclass(frozen=True)
class Segment:
    index: int
    offset: int  # absolute offset of the first instruction in the .Lib
    data: bytes
    names: tuple[str, ...]


@dataclass(frozen=True)
class AP20:
    raw: bytes
    chunks: tuple[tuple[str, int, bytes], ...]
    segments: tuple[Segment, ...]
    tokens: tuple[dict, ...]
    title: bytes


def parse_tokens(data: bytes) -> tuple[dict, ...]:
    """Walk the AMOS AP20 table with its real two-byte alignment."""
    rows = []
    at = 0
    while True:
        check(at + 6 <= len(data), 'Truncated AP20 token table')
        instruction, function = struct.unpack_from('>HH', data, at)
        if instruction == 0:
            check(not any(data[at:]), 'Invalid AP20 token terminator')
            return tuple(rows)
        end_name = at + 4
        while end_name < len(data) and data[end_name] < 128:
            end_name += 1
        check(end_name < len(data), 'Token without an end marker')
        end_sig = end_name + 1
        while end_sig < len(data) and data[end_sig] < 128:
            end_sig += 1
        check(end_sig < len(data) and data[end_sig] == 255,
              'Token without a valid signature terminator')
        try:
            name = bytes(c & 127 for c in data[at+4:end_name+1]).decode('ascii')
            signature = data[end_name+1:end_sig].decode('ascii')
        except UnicodeError as exc:
            raise ExportError('Invalid token encoding') from exc
        rows.append({'offset': at, 'instruction': instruction,
                     'function': function, 'name': name,
                     'signature': signature})
        at = (end_sig + 2) & ~1


def parse_ap20(raw: bytes) -> AP20:
    """Strict parser for the single-HUNK AP20 container used by this repo."""
    check(len(raw) >= 64 and len(raw) % 4 == 0, 'HUNK too short or misaligned')
    h = struct.unpack_from('>8I', raw)
    check(h[:5] == (0x3F3, 0, 1, 0, 0), 'Unsupported HUNK header')
    check(h[6] == 0x3E9 and h[5] == h[7], 'Invalid HUNK_CODE size')
    check(len(raw) == 36 + h[7] * 4, 'HUNK file length mismatch')
    check(raw[-4:] == struct.pack('>I', 0x3F2), 'Missing HUNK_END')
    jump_bytes, token_bytes, code_bytes, title_bytes = struct.unpack_from('>4I', raw, 32)
    check(jump_bytes >= 4 and jump_bytes % 2 == 0, 'Invalid jump-table size')
    check(not any(n & 1 for n in (token_bytes, code_bytes, title_bytes)),
          'Odd AP20 section size')
    check(raw[48:54] == b'\x00\x00AP20', 'Missing AP20 magic')
    p = 54
    jend = p + jump_bytes
    tend = jend + token_bytes
    cend = tend + code_bytes
    zend = cend + title_bytes
    check(zend <= len(raw)-4, 'AP20 sections extend outside HUNK')
    trailer = raw[zend:-4]
    check(2 <= len(trailer) <= 4 and not any(trailer),
          'Invalid AP20 C_End or HUNK padding')
    jumps = struct.unpack_from('>' + str(jump_bytes // 2) + 'H', raw, p)
    check(sum(jumps)*2 == code_bytes, 'AP20 spans do not cover machine code')
    tokens = parse_tokens(raw[jend:tend])
    names = {i: [] for i in range(len(jumps))}
    for row in tokens:
        for role in ('instruction', 'function'):
            idx = row[role]
            if idx > 1:
                check(idx < len(jumps) and jumps[idx] != 0,
                      'Token refers to a missing AP20 entry')
                title = row['name'] + (' [fn]' if role == 'function' else ' [cmd]')
                if title not in names[idx]:
                    names[idx].append(title)
    entries = []
    off = tend
    for index, nwords in enumerate(jumps):
        data = raw[off:off+nwords*2]
        entries.append(Segment(index, off, data, tuple(names[index])))
        off += len(data)
    check(off == cend, 'Segment lengths inconsistent')
    chunks = (
        ('HUNK_HEADER', 0, raw[:32]),
        ('AP20_LENGTHS', 32, raw[32:48]),
        ('AP20_MAGIC', 48, raw[48:54]),
        ('AP20_JUMPS', p, raw[p:jend]),
        ('AP20_TOKENS', jend, raw[jend:tend]),
        ('AP20_TITLE', cend, raw[cend:zend]),
        ('AP20_TRAILER', zend, raw[zend:]),
    )
    return AP20(raw, chunks, tuple(entries), tokens, raw[cend:zend])


def path_arg(raw: str) -> Path:
    p = Path(raw)
    return p.resolve() if p.is_absolute() else (ROOT / p).resolve()


def builder_archive(builder: Path) -> Optional[Path]:
    """Extract a literal ARCHIVE = ROOT / '...' without importing the builder."""
    try:
        tree = ast.parse(builder.read_text(encoding='utf-8'), filename=str(builder))
    except (OSError, SyntaxError, UnicodeError):
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == 'ARCHIVE'
                   for t in node.targets):
            continue
        value = node.value
        if (isinstance(value, ast.BinOp) and isinstance(value.op, ast.Div)
                and isinstance(value.left, ast.Name)
                and value.left.id == 'ROOT'
                and isinstance(value.right, ast.Constant)
                and isinstance(value.right.value, str)):
            return path_arg(value.right.value)
    return None


def find_matching_builder(lib_data: bytes) -> Optional[Path]:
    folder = ROOT / 'tools'
    for builder in sorted(folder.glob('build_*.py')):
        archive = builder_archive(builder)
        if archive and archive.is_file() and archive.read_bytes() == lib_data:
            return builder
    return None


def build_in_memory(builder: Path) -> tuple[bytes, object]:
    check(builder.is_file(), 'Builder Python missing: ' + str(builder))
    sys.path.insert(0, str(builder.parent))
    try:
        # Deliberately not __main__: no publication block, no .Lib writes.
        scope = runpy.run_path(str(builder), run_name='aga_asm_readonly_export')
        check(callable(scope.get('build')), 'No callable build() in builder')
        result = scope['build']()
        if isinstance(result, tuple) and result:
            data, report = result[0], (result[1] if len(result) > 1 else None)
        else:
            data, report = result, None
        check(isinstance(data, (bytes, bytearray)),
              'Builder build() did not return HUNK bytes')
        return bytes(data), report
    finally:
        sys.path.remove(str(builder.parent))


def capstone_decoder():
    try:
        import capstone
        mode = capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000
        cs = capstone.Cs(capstone.CS_ARCH_M68K, mode)
        cs.skipdata = True
        return cs
    except (ImportError, AttributeError):
        return None


def disassemble(data: bytes, cs):
    """Return (offset, raw bytes, mnemonic) preserving every code byte."""
    if not data:
        return []
    if cs is None:
        return [(i, data[i:i+12], 'hex data (install capstone for 68000 mnemonics)')
                for i in range(0, len(data), 12)]
    rows = []
    end = 0
    try:
        for ins in cs.disasm(data, 0):
            offset = int(ins.address)
            if offset < end or offset + ins.size > len(data):
                break
            if offset > end:
                rows.append((end, data[end:offset], 'unrecognized bytes'))
            mnemonic = (ins.mnemonic + ' ' + ins.op_str).strip()
            rows.append((offset, data[offset:offset+ins.size], mnemonic))
            end = offset + ins.size
    except Exception as exc:
        rows.append((end, data[end:], 'decoder stopped: ' + str(exc)))
        end = len(data)
    if end < len(data):
        rows.append((end, data[end:], 'unrecognized bytes'))
    check(b''.join(row[1] for row in rows) == data,
          'Disassembler omitted machine-code bytes')
    return rows


def asm_bytes(data: bytes, comment: str = '', indent: str = '    ') -> list[str]:
    if not data:
        return []
    safe_comment = re.sub(r'\s+', ' ', comment).strip()
    if len(data) % 2 == 0:
        words = [int.from_bytes(data[i:i+2], 'big') for i in range(0, len(data), 2)]
        # Keep lines short; decoded instructions stay on one line when possible.
        if len(words) <= 12:
            return [indent + 'dc.w ' + ','.join('$%04X' % w for w in words) +
                    (('  ; ' + safe_comment[:130]) if safe_comment else '')]
    return [indent + 'dc.b ' + ','.join('$%02X' % v for v in data[i:i+12]) +
            (('  ; ' + safe_comment[:130]) if safe_comment and i == 0 else '')
            for i in range(0, len(data), 12)]


def lines_for_data(data: bytes, label: str, off: int, note: str = '') -> list[str]:
    out = ['', label + ':  ; file +$%06X' % off + ((' - '+note) if note else '')]
    for i in range(0, len(data), 12):
        out += asm_bytes(data[i:i+12])
    return out


def export_asm(ap: AP20, builder: Optional[Path], cs) -> tuple[str, str, dict]:
    raw_sha = sha(ap.raw)
    title = ap.title.decode('latin1', errors='replace').replace('\x00', ' | ').strip()
    names = ['; AUTO-GENERATED / READ ONLY - NOT ORIGINAL SYMBOLIC ASSEMBLY',
             '; Builder identified: ' + (str(builder.relative_to(ROOT)) if builder and builder.is_relative_to(ROOT) else str(builder or 'none (existing .Lib)')),
             '; HUNK/AP20 SHA256: ' + raw_sha,
             '; Assemble as flat binary with vasm motorola: vasmm68k_mot -Fbin -o check.Lib thisfile.s',
             '; DC.W/DC.B contain EXACT original bytes. Instruction mnemonics are COMMENTS.',
             '; No claim of full reassemblable human-authored instructions or relocations.',
             '; Verify byte-for-byte against the input .Lib after assembly.',
             '; Decoder: ' + ('Capstone M68K (heuristic for embedded data)' if cs is not None else 'none; exact hex only'),
             '']
    listing = ['; 68000 listing from AP20/HUNK; heuristic wherever code contains data',
               '; HUNK SHA256: ' + raw_sha, '; ' + title, '']
    by = {name: (at, data) for name, at, data in ap.chunks}
    for name in ('HUNK_HEADER', 'AP20_LENGTHS', 'AP20_MAGIC', 'AP20_JUMPS', 'AP20_TOKENS'):
        off, data = by[name]
        names += lines_for_data(data, name, off)
    names += ['', 'AP20_CODE:  ; code follows in jump-table order']
    segments_json = []
    for seg in ap.segments:
        idx = seg.index
        title_name = ', '.join(seg.names) if seg.names else '(reserved / internal)'
        names += ['', 'AP20_ENTRY_%02d:  ; file +$%06X, %d bytes, %s' %
                  (idx, seg.offset, len(seg.data), title_name)]
        listing += ['', '[Entry %02d] file +$%06X | %d bytes | %s' %
                    (idx, seg.offset, len(seg.data), title_name)]
        has_getp = seg.data.endswith(b'GetP')
        code = seg.data[:-4] if has_getp else seg.data
        for rel, chunk, ins in disassemble(code, cs):
            if not chunk:
                continue
            off = seg.offset + rel
            raw_hex = chunk.hex(' ').upper()
            suffix = '+$%04X %s' % (rel, ins)
            for line in asm_bytes(chunk, suffix):
                names.append(line)
            listing.append('%06X: %-33s %s' % (off, raw_hex[:33], ins))
        if has_getp:
            names += asm_bytes(b'GetP', 'GetP parameter-dispatch delimiter, NOT CPU code')
            listing.append('%06X: 47 65 74 50                       [GetP delimiter]' %
                           (seg.offset + len(seg.data) - 4))
        segments_json.append({'index': idx, 'offset': seg.offset,
                              'length': len(seg.data), 'names': list(seg.names),
                              'getp_at_end': has_getp, 'sha256': sha(seg.data)})
    for name in ('AP20_TITLE', 'AP20_TRAILER'):
        off, data = by[name]
        names += lines_for_data(data, name, off)
    manifest = {'format': 'single-HUNK AP20', 'source_kind': 'linked builder/checked binary (see build report)' if builder else 'existing library',
                'builder': str(builder) if builder else None,
                'sha256': raw_sha, 'size_bytes': len(ap.raw),
                'title': title, 'number_of_entries': len(ap.segments),
                'tokens': list(ap.tokens), 'segments': segments_json,
                'capstone_used': cs is not None,
                'warning': 'Disassembly is heuristic. Exact .s uses literal DC.W/DC.B; historical symbols are not recoverable.'}
    return '\n'.join(names) + '\n', '\n'.join(listing) + '\n', manifest


def decode_exact_asm(source: str) -> bytes:
    """Independent round-trip check of our DC.W/DC.B emission."""
    out = bytearray()
    for line in source.splitlines():
        line = line.split(';', 1)[0].strip()
        if line.startswith('dc.w '):
            for piece in line[5:].split(','):
                out += struct.pack('>H', int(piece.strip().replace('$','0x'), 0))
        elif line.startswith('dc.b '):
            for piece in line[5:].split(','):
                v = int(piece.strip().replace('$','0x'), 0)
                check(0 <= v <= 255, 'Bad byte in generated source')
                out.append(v)
    return bytes(out)


def read_source(args):
    input_lib = path_arg(args.lib)
    check(input_lib.is_file(), 'Input library does not exist: ' + str(input_lib))
    expected = input_lib.read_bytes()
    before = sha(expected)
    builder = None
    report = None
    if args.builder.lower() == 'auto':
        builder = find_matching_builder(expected)
        if builder is None:
            print('[INFO] No matching Python builder archive; exporting current .Lib only.')
    elif args.builder.lower() not in ('none', 'lib'):
        builder = path_arg(args.builder)
    if builder:
        # In auto mode the matching archive has ALREADY been compared byte
        # for byte to the requested .Lib. Do not needlessly call build():
        # some historic builders assert on local paths, repository revisions,
        # or require tools not installed on this Windows machine.
        if args.builder.lower() == 'auto' and not args.verify_builder:
            archive = builder_archive(builder)
            check(archive is not None and archive.is_file() and
                  archive.read_bytes() == expected,
                  'Builder archive changed since automatic discovery')
            print('[INFO] Identical versioned archive: ' + str(archive))
            print('[INFO] Python builder: ' + str(builder))
            print('[INFO] Exporting checked .Lib without executing build().')
            print('[INFO] To also rebuild in memory: --verify-builder')
            return expected, builder, {'mode': 'verified-archive',
                                       'archive': str(archive),
                                       'sha256': before}
        print('[INFO] Running in-memory build(): ' + str(builder), flush=True)
        try:
            data, report = build_in_memory(builder)
        except Exception as exc:
            raise ExportError(
                'Builder build() failed (%s: %s). The full Python traceback '
                'appears below. For an export of the exact existing .Lib, '
                'rerun without --verify-builder or use --builder none.' %
                (type(exc).__name__, str(exc) or '<no assertion message>')
            ) from exc
        check(sha(input_lib.read_bytes()) == before,
              'Builder modified the input .Lib - unsafe build(); export aborted')
        if args.builder.lower() == 'auto' or args.check_dist:
            check(data == expected,
                  'Builder output differs from --lib; no export generated')
        elif data != expected:
            print('[INFO] Explicit builder differs from active .Lib (historical build).')
        return data, builder, report
    if args.verify_builder and args.builder.lower() == 'auto':
        raise ExportError('No builder/archive pair matches this .Lib; cannot verify build()')
    return expected, None, None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lib', default='dist/AMOSPro_AGA.Lib',
                        help='AP20/HUNK .Lib to inspect (default: dist/AMOSPro_AGA.Lib)')
    parser.add_argument('--builder', default='auto',
                        help='auto, none, or an explicit tools/build_*.py path')
    parser.add_argument('--check-dist', action='store_true',
                        help='require explicit --builder output to equal --lib')
    parser.add_argument('--verify-builder', action='store_true',
                        help='in auto mode additionally call build() in memory and compare its HUNK')
    parser.add_argument('--out', default='asm_export',
                        help='output directory (default: asm_export)')
    parser.add_argument('--no-capstone', action='store_true',
                        help='force exact hex listing; never load optional Capstone')
    args = parser.parse_args(argv)
    try:
        data, builder, report = read_source(args)
        ap = parse_ap20(data)
        cs = None if args.no_capstone else capstone_decoder()
        source, listing, manifest = export_asm(ap, builder, cs)
        # Prevent a partial or lossy export, including AP20 header and padding.
        check(decode_exact_asm(source) == data,
              'Generated assembler failed exact-byte round-trip')
        target = path_arg(args.out)
        target.mkdir(parents=True, exist_ok=True)
        match = re.search(r'\bR(\d+)\s+(\d+\.\d+\.\d+)\b',
                          manifest['title'], re.IGNORECASE)
        label = ('R%s_v%s' % match.groups()) if match else sha(data)[:12]
        basename = 'AMOSPro_AGA_' + label
        (target / (basename + '.s')).write_text(source, encoding='utf-8', newline='\n')
        (target / (basename + '.lst')).write_text(listing, encoding='utf-8', newline='\n')
        manifest['input_lib'] = str(path_arg(args.lib))
        manifest['in_memory_build_report'] = str(report) if report else None
        (target / (basename + '.json')).write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n',
                                                    encoding='utf-8', newline='\n')
        print('OK: ' + str(target / (basename + '.s')))
        print('OK: ' + str(target / (basename + '.lst')))
        print('OK: ' + str(target / (basename + '.json')))
        print('SHA256: ' + sha(data))
        if cs is None:
            print('[INFO] Capstone not installed; mnemonic listing is hex-only.')
            print('       Optional: py -3 -m pip install capstone')
        print('[INFO] Source is exact DC.W/DC.B, not the original Genam code.')
        return 0
    except Exception as exc:
        import traceback
        print('[ERROR] %s: %s' % (type(exc).__name__, str(exc) or '<no details>'),
              file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
