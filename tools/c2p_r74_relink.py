"""Source-backed cross-entry link audit for R74, including the 2 close hooks.

In R74 only entry08 gains bytes in the middle of the old monolith. The
following three R57 verified calls precede it or sit inside it and jump to
later entries. They must be repaired even if the original branch opcode
still looks syntactically valid (R70 incident).
"""
from __future__ import annotations
from struct import pack_into, unpack_from

CROSS=(
    # (name, source_entry, branch_instruction_offset, target_entry, target_offset)
    ('Init cleanup -> DB draining helper',0,0x18e,54,0xde),
    ('Screen Close -> font cleanup helper',8,0x08c,48,0x17a),
    ('Screen Close -> DB draining helper',8,0x114,54,0xde),
)

def starts(parts):
    out=[];at=0
    for part in parts:
        if len(part)&1:raise AssertionError('odd native entry')
        out.append(at);at+=len(part)
    if at>=65534:raise AssertionError('AP20 Compiler V2 monolith overflow')
    return out


def patch_word_branch(parts,source_entry,source_offset,target_entry,target_offset, *, opcode, require_target=False):
    begin=starts(parts)
    source=bytearray(parts[source_entry])
    if unpack_from('>H',source,source_offset)[0]!=opcode:
        raise AssertionError(f'wrong opcode at {source_entry}:{source_offset:#x}')
    origin=begin[source_entry]+source_offset+2  # PC of branch extension word
    dest=begin[target_entry]+target_offset
    displacement=dest-origin
    if not -32768<=displacement<=32767:
        raise AssertionError(f'PC16 out of range: {source_entry}:{source_offset:#x} -> {target_entry}:{target_offset:#x}')
    if require_target and parts[target_entry][target_offset:target_offset+2]==b'\0\0':
        raise AssertionError('uninitialized target bytes')
    pack_into('>h',source,source_offset+2,displacement)
    parts[source_entry]=bytes(source)
    return displacement


def expect_word_branch(parts,src,off,dst,to,opcode):
    begin=starts(parts)
    got=unpack_from('>H',parts[src],off)[0]
    if got!=opcode:raise AssertionError(f'bad branch opcode {got:#x} != {opcode:#x}')
    disp=unpack_from('>h',parts[src],off+2)[0]
    actual=begin[src]+off+2+disp
    want=begin[dst]+to
    if actual!=want:
        raise AssertionError(f'{src}:{off:#x} reaches {actual:#x}, expected {want:#x}')


def patch_cross_r74(parts):
    for name,src,off,dst,to in CROSS:
        patch_word_branch(parts,src,off,dst,to,opcode=0x6100)
    check_cross_r74(parts)


def check_cross_r74(parts):
    for name,src,off,dst,to in CROSS:
        expect_word_branch(parts,src,off,dst,to,0x6100)
