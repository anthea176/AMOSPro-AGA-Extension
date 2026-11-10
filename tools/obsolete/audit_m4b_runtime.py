"""Read-only M4b regression checks, scoped to the audited 68k routines.

Not a general disassembler/emulator. AP20 validity alone is not runtime safety.
Exit 1 means a known unsafe pattern was found; no binary is produced.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from audit_ap20 import parse, inspect


def segment(lib, index):
    p = lib.starts[index]
    return lib.code[p:p+2*lib.jumps[index]]


def compare(before, after):
    return dict(tokens_equal=before.tokens == after.tokens,
                parameter_dispatch=inspect(after)['parameter_checks'],
                segments=[dict(index=i, before_start=before.starts[i],
                               after_start=after.starts[i],
                               before_bytes=before.jumps[i]*2,
                               after_bytes=after.jumps[i]*2,
                               equal=segment(before, i) == segment(after, i),
                               sha256_after=hashlib.sha256(segment(after, i)).hexdigest())
                          for i in range(len(before.jumps))])


def open_contract(before, after):
    """Assert exact Open bytes, entry, signature, parameter dispatcher and Cold."""
    if inspect(after)['issues']:
        raise ValueError('AP20-invalid')
    for lib in (before, after):
        row = next(t for t in inspect(lib)['tokens'] if t['name'] == 'aga screen open')
        if (row['instruction'], row['function'], row['signature']) != (1, 6, '00,0,0,0'):
            raise ValueError('Open-token-changed')
        if lib.code[lib.starts[6]-4:lib.starts[6]] != b'GetP':
            raise ValueError('Open-GetP-missing')
    if before.starts[6] != after.starts[6] or segment(before, 6) != segment(after, 6):
        raise ValueError('Open-span-or-code-changed')
    if segment(before, 0) != segment(after, 0):
        raise ValueError('Cold-changed')


def findings(lib):
    issues = []
    op = segment(lib, 6)
    # Proven by disassembly: Open stores its computed depth in state+28.
    # This is a diagnostic for this implementation, not generic dataflow analysis.
    if op[0xc4:0xda] == bytes.fromhex('22067000e28952800c81000000016600fff42540001c'):
        if bytes.fromhex('266a001c') in segment(lib, 10):
            issues.append(dict(id='depth-as-db-pointer', entry=6, offset=0xd6,
                               detail='Open writes depth to +28; DoubleBuffer treats +28 as DBState*'))
    for i in (8, 10, 11, 12):
        code = segment(lib, i)
        if bytes.fromhex('266a001c') not in code:
            continue
        if code[:2] != bytes.fromhex('48e7'):
            issues.append(dict(id='unreviewed-prologue', entry=i))
            continue
        save = struct.unpack_from('>H', code, 2)[0]
        tails = [p for p in range(0, len(code)-3, 2) if code[p:p+2] == bytes.fromhex('4cdf')]
        restore = struct.unpack_from('>H', code, tails[-1]+2)[0] if tails else 0
        # MOVEM predecrement uses reversed register numbering: A3 is bit 4;
        # normal postincrement uses bit 11. D3 is bit 12 / bit 3 respectively.
        if not save & (1 << 4) or not restore & (1 << 11):
            issues.append(dict(id='a3-not-preserved', entry=i, save=hex(save), restore=hex(restore)))
    return issues


def trace_db_already(code, state_pointer, original_a3=0x123456):
    """Execute the audited already-initialized branch, with no OS emulation.

    Requires nonzero state[0] (screen) and state[28]. Validates the actual
    branch displacement and MOVEM masks. Rejects unknown instruction shapes.
    """
    if state_pointer == 0 or code[:4] != bytes.fromhex('48e7efee'):
        raise ValueError('unsupported path')
    if code[0x18:0x22] != bytes.fromhex('266a001c200b4a806600'):
        raise ValueError('unexpected DBState branch')
    target = 0x22 + struct.unpack_from('>h', code, 0x22)[0]
    if code[target:target+4] != bytes.fromhex('76016000'):
        raise ValueError('unexpected already target')
    epilogue = target+4+struct.unpack_from('>h', code, target+4)[0]
    if code[epilogue:epilogue+8] != bytes.fromhex('4cdf77f774004e75'):
        raise ValueError('unexpected epilogue')
    return dict(d3=1, d2=0, a3=state_pointer, original_a3=original_a3,
                os_calls=0, branch_target=target, epilogue=epilogue)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('file', type=Path)
    args = p.parse_args()
    lib = parse(args.file.read_bytes())
    result = dict(ap20_issues=inspect(lib)['issues'], runtime_findings=findings(lib))
    print(json.dumps(result, indent=2))
    return int(bool(result['ap20_issues'] or result['runtime_findings']))


if __name__ == '__main__':
    raise SystemExit(main())
