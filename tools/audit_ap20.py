"""Read-only, bounded audit of the single-HUNK AP20 format used by this repo.

Models token stepping and parameter-entry selection from AMOS365 +B.s;
not a CPU emulator or a general AMOS token grammar implementation.
"""
from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import struct


class FormatError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise FormatError(message)


@dataclass
class Library:
    raw: bytes
    lengths: tuple
    jumps: tuple
    tokens: bytes
    code: bytes
    title: bytes

    @property
    def starts(self):
        result, offset = [], 0
        for size in self.jumps:
            result.append(offset)
            offset += size * 2
        return result


def parse(raw):
    require(len(raw) >= 64, 'truncated HUNK')
    h = struct.unpack_from('>8I', raw)
    require(h[:5] == (0x3f3, 0, 1, 0, 0), 'unsupported HUNK header')
    require(h[6] == 0x3e9 and h[5] == h[7], 'HUNK_CODE size mismatch')
    require(len(raw) == 36 + 4*h[7], 'HUNK file length mismatch')
    require(raw[-4:] == struct.pack('>I', 0x3f2), 'missing HUNK_END')
    d = raw[32:-4]
    lengths = off, nt, nc, nz = struct.unpack_from('>4I', d)
    require(d[16:22] == b'\0\0AP20', 'missing AP20 header')
    require(off >= 4 and all(n % 2 == 0 for n in lengths), 'odd section size')
    end = 22 + sum(lengths)
    require(end + 2 <= len(d), 'section outside HUNK / missing C_End')
    require(len(d)-end <= 4 and not any(d[end:]), 'invalid C_End/padding')
    jumps = struct.unpack_from('>' + str(off//2) + 'H', d, 22)
    require(sum(jumps)*2 == nc, 'routine spans do not cover code')
    ts = 22 + off
    return Library(raw, lengths, jumps, d[ts:ts+nt],
                   d[ts+nt:ts+nt+nc], d[ts+nt+nc:end])


def walk_tokens(tokens):
    """Use the loader's even alignment, never a search for command substrings."""
    pos = 0
    while True:
        require(pos + 6 <= len(tokens), 'missing six-byte token terminator')
        instruction, function = struct.unpack_from('>HH', tokens, pos)
        if instruction == 0:
            require(not any(tokens[pos:]), 'early terminator or unsupported metadata')
            return
        name_end = pos + 4
        while name_end < len(tokens) and tokens[name_end] < 128:
            name_end += 1
        require(name_end < len(tokens), 'unterminated token name')
        sig_end = name_end + 1
        while sig_end < len(tokens) and tokens[sig_end] < 128:
            sig_end += 1
        require(sig_end < len(tokens), 'unterminated token signature')
        require(tokens[sig_end] == 255, 'unsupported signature terminator')
        name = bytes(x & 127 for x in tokens[pos+4:name_end+1]).decode('ascii')
        signature = tokens[name_end+1:sig_end].decode('ascii')
        yield dict(offset=pos, instruction=instruction, function=function,
                   name=name, signature=signature)
        pos = (sig_end + 2) & ~1


def inspect(lib):
    rows, issues, parameter_checks = list(walk_tokens(lib.tokens)), [], []
    for row in rows:
        if not row['signature']:  # initial dummy token
            continue
        sig = row['signature']
        require(sig[0] in 'I012' and all(c in '0123,' for c in sig[1:]),
                'unsupported token signature: ' + sig)
        count = len(sig[1:].split(',')) if sig[1:] else 0
        # +B.s .RInst also sets the function flag when both words exceed 1.
        for role in ('instruction', 'function'):
            index = row[role]
            if index <= 1:
                continue
            valid = index < len(lib.jumps) and lib.jumps[index] != 0
            if not valid:
                issues.append(dict(offset=row['offset'], name=row['name'],
                                   role=role, index=index,
                                   kind='out-of-range-or-empty-entry'))
            if count:
                check = dict(offset=row['offset'], name=row['name'], role=role,
                             index=index, parameters=count)
                if valid:
                    start = lib.starts[index]
                    check['getp'] = lib.code[start-4:start] == b'GetP'
                    if not check['getp']:
                        issues.append(dict(check, kind='missing-GetP'))
                else:
                    check['getp'] = False
                parameter_checks.append(check)
    return dict(lengths=lib.lengths, jumps=lib.jumps, tokens=rows,
                issues=issues, parameter_checks=parameter_checks)


def token(name, instruction, function, signature):
    encoded = name.encode('ascii')
    require(bool(encoded), 'empty token name')
    result = (struct.pack('>HH', instruction, function) + encoded[:-1]
              + bytes([encoded[-1] | 128]) + signature.encode('ascii') + b'\xff')
    return result + b'\0' * (len(result) % 2)


def structural_candidate(raw):
    """In-memory test fixture only: rebuild the documented M4b token table.

    Preserves all code, title and jump spans. Never writes a .Lib file.
    Also repairs inherited Probe/Detect misalignment, without editing M4a.
    """
    lib = parse(raw)
    require(len(lib.jumps) == 14, 'expected M4b fixture')
    commands = [('aga probe', 3, 1, 'I'), ('aga detect', 1, 4, '0'),
                ('aga demo', 1, 5, '0'), ('aga screen open', 1, 6, '00,0,0,0'),
                ('aga screen pattern', 7, 1, 'I'), ('aga screen close', 8, 1, 'I'),
                ('aga wait vbl', 9, 1, 'I'), ('aga double buffer', 1, 10, '0'),
                ('aga swap', 1, 11, '0'), ('aga back fill', 12, 1, 'I0')]
    tokens = b'\0\1\0\0\x80\xff' + b''.join(token(*c) for c in commands) + b'\0'*6
    d = (struct.pack('>4I', lib.lengths[0], len(tokens), len(lib.code), len(lib.title))
         + b'\0\0AP20' + struct.pack('>'+str(len(lib.jumps))+'H', *lib.jumps)
         + tokens + lib.code + lib.title + b'\0\0')
    d += b'\0' * (-len(d) % 4)
    n = struct.pack('>I', len(d)//4)
    return raw[:20] + n + raw[24:28] + n + d + raw[-4:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.files:
        try:
            result = inspect(parse(path.read_bytes()))
            failed |= bool(result['issues'])
        except (FormatError, OSError) as exc:
            result = dict(error=str(exc))
            failed = True
        print(json.dumps(dict(file=str(path), **result), indent=2))
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
