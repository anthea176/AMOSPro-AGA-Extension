"""Extract selected diagnostic facts from an AMD64 WinUAE minidump locally.

Standard library only. Does not export raw memory, paths, full logs or config.
Uses the EXCEPTION stream context, not the later thread snapshot context.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def inspect_dump(raw):
    def block(offset, length):
        if offset < 0 or length < 0 or offset+length > len(raw):
            raise ValueError('truncated minidump')
        return raw[offset:offset+length]
    if block(0,4) != b'MDMP':
        raise ValueError('not a minidump')
    count, directory=struct.unpack('<II',block(8,8))
    block(directory,count*12)
    streams={}
    for i in range(count):
        kind,size,offset=struct.unpack('<III',block(directory+i*12,12))
        if kind:
            streams[kind]=block(offset,size)
    if struct.unpack_from('<H',streams[7])[0] != 9:
        raise ValueError('only AMD64 contexts supported')
    e=streams[6]
    thread,=struct.unpack_from('<I',e)
    code,=struct.unpack_from('<I',e,8)
    address,=struct.unpack_from('<Q',e,24)
    n,=struct.unpack_from('<I',e,32)
    if n>15:
        raise ValueError('bad exception parameter count')
    params=struct.unpack_from('<'+'Q'*n,e,40)
    size,offset=struct.unpack_from('<II',e,160)
    context=block(offset,size)
    regs={name:hex(struct.unpack_from('<Q',context,p)[0])
          for name,p in [('rax',120),('rsp',152),('r9',192),('rip',248)]}
    allowed=('cpu_model=','fpu_model=','cachesize=','cpu_compatible=',
             'cpu_cycle_exact=','cpu_memory_cycle_exact=','comp_catchfault=')
    config=streams.get(65538,b'').decode('utf-8',errors='replace')
    return dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                exception_code=hex(code),thread_id=hex(thread),
                exception_address=hex(address),parameters=[hex(v) for v in params],
                exception_context=regs,has_full_memory_stream=9 in streams,
                selected_config=[s for s in config.splitlines() if s.startswith(allowed)],
                limitation='Host exception only; no automatic guest-PC attribution')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('dump',type=Path)
    args=p.parse_args()
    print(json.dumps(inspect_dump(args.dump.read_bytes()),indent=2))
