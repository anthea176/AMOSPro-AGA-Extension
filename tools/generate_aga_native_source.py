#!/usr/bin/env python3
"""AMOS Professional AGA AP20 -> native-looking Motorola 68k source.

This exporter reconstructs *instruction mnemonics* and PC labels for the
validated AP20/HUNK image; it never calls build() or overwrites a .Lib. It is
intended as a migration bridge from the original Python byte emitters to a
single maintainable assembly source. A separate assembler comparison is still
required before claiming bit-identical native reassembly.

Python 3.10+, standard library only. Test with tests/test_native_source.py.
"""
from __future__ import annotations
import argparse
import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
from decoder68k import Decoder,Insn,flow_decode

ROOT=Path(__file__).resolve().parents[1]
R19_SHA='32c99d9d83affda67058fede26731dace6511ebc033b7974330e6f9eef39e295'
R23_SHA='899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23'
# Known SAFE code-entry seeds, keyed by exact SHA of each AP20 core routine.
# This preserves the historic R19 reconstructed flow on later releases when
# unchanged entries are inherited without rerunning old Python builders.
# New/modified code MUST independently classify all its instructions/data.
KNOWN_SEEDS={
 'c501b69e02cf8c35113685a07562e85e90adb7090f9ee1e6c4d1cc69afa0bb5c':(0x38,0x66),
 'ccd97367b13e187d8b5b050d803cf8b80071dac59e53ca66bafca8717f15ac08':(2,),
 '10c13c1b3f27cda1d346e241e66f90a53a80827f8606f64699990e6c41acd8d7':(0x142,),
 'e0b0024c87623a949a1ff5a82827cfa699f3a90ff85769611c11d4c8f43636a8':(0x7fe,0x87e),
 'e525530f8387e1166824b766c26c8a4cdc7e567d85b35ddbf22ba7d59595f1b6':(0x5ec,),
 '940ee56ece0ae255b7ebb8fba46a5366d67fb242a5ee5f369463a42a1927023e':(0x1fa,),
 '771af389042a9199b16cecbaf3d643d65fc5e80755017ac51607083f5efb5185':(0x6c,0x222),
 # M13 R28 Palette Load: exact audited core. Two MOVE.L #0,D0 instructions
 # in the inherited M5 file-reader error-return helpers are valid 68000 code,
 # but unreachable from the naive entrypoint-only CFG. Never trust altered code.
 '567c652d07ff770b0f72690f766c401dca9595d9830834f8bb08583b6445d620':(1170,1298),
  # M13 R29 Save: one source-confirmed but unreachable MOVE.L #0,D0 in
  # the cleanup_save helper's generic failure-return epilogue. Exact core
  # SHA only; altered code must still fail --strict, as for R28.
  '36feed62fafa7f66065b36b2bec2c12275331af7d75599abc68ac19e0ffd5d3f':(1206,),
}

class ExportError(ValueError):pass

def need(c,msg):
    if not c:raise ExportError(msg)

def sha(b):return hashlib.sha256(b).hexdigest()
def U16(b,p):return struct.unpack_from('>H',b,p)[0]
def U32(b,p):return struct.unpack_from('>I',b,p)[0]

def tokens_parse(raw):
    rows=[];p=0
    while True:
        need(p+6<=len(raw),'Unterminated AP20 token table')
        a,b=struct.unpack_from('>HH',raw,p)
        if a==0:
            need(not any(raw[p:]),'Bad token terminator')
            return rows
        start=p;end=p+4
        while end<len(raw) and raw[end]<128:end+=1
        need(end<len(raw),'Bad token name')
        s=end+1
        while s<len(raw) and raw[s]<128:s+=1
        need(s<len(raw) and raw[s]==255,'Bad token signature')
        name=bytes(c&127 for c in raw[p+4:end+1]).decode('ascii')
        signature=raw[end+1:s].decode('ascii')
        p=(s+2)&~1
        rows.append({'instruction':a,'function':b,'name':name,'signature':signature,
                     'start':start,'end':p})

def parse_lib(data):
    need(len(data)>64 and len(data)%4==0,'Too short or unaligned HUNK')
    h=struct.unpack_from('>8I',data)
    need(h[:5]==(0x3f3,0,1,0,0) and h[6]==0x3e9 and h[5]==h[7],'Unsupported HUNK structure')
    need(len(data)==36+4*h[7] and U32(data,len(data)-4)==0x3f2,'HUNK size/end mismatch')
    jump_size,tok_size,code_size,title_size=struct.unpack_from('>4I',data,32)
    need(jump_size>0 and jump_size%2==0 and data[48:54]==b'\x00\x00AP20','Bad AP20 header')
    jump_start=54
    tok_start=jump_start+jump_size
    code_start=tok_start+tok_size
    title_start=code_start+code_size
    end=title_start+title_size
    need(end+2<=len(data)-4 and not any(data[end:len(data)-4]),'AP20 length/padding mismatch')
    jumps=struct.unpack_from('>'+str(jump_size//2)+'H',data,jump_start)
    need(sum(jumps)*2==code_size,'AP20 entry sizes do not cover code')
    tokens=tokens_parse(data[tok_start:code_start])
    names={i:[] for i in range(len(jumps))}
    for t in tokens:
        for n in ('instruction','function'):
            index=t[n]
            if index>1:
                need(index<len(jumps),'Token entry outside jump table')
                if t['name'] not in names[index]:names[index].append(t['name'])
    sections=[];off=code_start
    for i,n in enumerate(jumps):
        b=data[off:off+n*2]
        need(len(b)==n*2,'Truncated code entry')
        getp=b.endswith(b'GetP')
        sections.append({'id':i,'file_offset':off,'data':b,
                         'core':b[:-4] if getp else b,'getp':getp,'names':names[i]})
        off+=len(b)
    need(off==title_start,'Bad code end')
    return {'raw':data,'jumps':jumps,'tokens':tokens,'token_data':data[tok_start:code_start],
            'title':data[title_start:end],'section':sections,'code_start':code_start,
            'code_end':title_start,'trailer':data[end:len(data)-4],'end':end}

# R46 C1 adds AMOS Compiler Rbsr ($FE31) entry stubs and a monolithic
# dispatcher. These are AP20 linker pseudo-operations, not 68000 instructions.
# Reconstruct the trusted native source layout IN MEMORY, without ever editing
# official, LAST_GOOD or historical .Lib binaries.
PROMOTED_R46_C1_SHA = 'd2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b'
NATIVE_R46_SHA = '5214f444b3b6e0ed1b1d2a354da0b44fb44ed4cbbc4787634415308a4d099580'
NATIVE_R46_ARCHIVE = ROOT/'dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib'


def source_binary_from_input(raw):
    """Recover native AP20 segments from SHA-pinned Compiler-safe releases.

    R46 C1 uses its frozen native archive; later releases use the current and
    LAST_GOOD hashes verified in active_library. Never treat FE31 as 68000.
    """
    parsed = parse_lib(raw)
    from compiler_relocation import is_compiler_wrapped, native_from_promoted, wrap_native_ap20
    from compiler_bridge_v2_probe import is_v2_wrapped, unwrap_native_parts_v2, wrap_native_ap20_v2
    if is_v2_wrapped(raw):
        # Accept only the exact SHA-pinned, reproducible V2 releases.
        # R58 is the 40K witness; R59 is LAST_GOOD; R60 is the next candidate.
        # Unknown FE31/dispatcher bytes MUST fail closed.
        from active_library import R58_SHA, R59_SHA, R60_SHA, R61_SHA
        from compiler_relocation import repack_ap20
        if sha(raw) == R61_SHA:
            from build_m18_r61_ficon import build as pinned_build
            release = "R61"
        elif sha(raw) == R60_SHA:
            from build_m18_r60_image_region import build as pinned_build
            release = "R60"
        elif sha(raw) == R59_SHA:
            from build_m17_r59_compact_v2 import build as pinned_build
            release = 'R59'
        elif sha(raw) == R58_SHA:
            from build_m17_r58_compiler_bridge import build as pinned_build
            release = 'R58'
        else:
            raise ExportError('Unsupported V2 compiler wrapper; source audit required')
        expected, _meta = pinned_build()
        need(raw == expected, 'Unsupported V2 compiler wrapper; source audit required')
        try:
            tokens, parts = unwrap_native_parts_v2(raw)
            native = repack_ap20(raw, tokens, parts, parsed['title'])
        except (AssertionError, ValueError) as exc:
            raise ExportError('Malformed deterministic ' + release + ' V2 source') from exc
        need(wrap_native_ap20_v2(native, parsed['title']) == raw,
             release + ' V2 source rewrap not byte-exact')
        return native, {
            'format': 'Compiler-safe AP20 V2 unsigned-offset monolith',
            'provenance': 'verified deterministic ' + release + ' builder from SHA-pinned R57',
            'official_sha256': sha(raw),
            'official_bytes': len(raw),
            'official_entries': len(parsed['section']),
            'native_sha256': sha(native),
            'native_bytes': len(native),
            'native_entries': len(parse_lib(native)['section']),
            'native_archive': None,
            'verified_extract_and_rewrap': True,
            'warning': 'Native ASM output is NOT an installable .Lib; ' + release +
                       ' requires the V2 AP20 bridge (never the C1 wrapper).',
        }
    if not is_compiler_wrapped(raw):
        need(not any(sec['core'].startswith(b'\xfe\x31') for sec in parsed['section']),
             'Rbsr entry without audited compiler dispatcher: '
             'refusing to decode AMOS linker words as 68000')
        return raw, None

    is_r46 = sha(raw) == PROMOTED_R46_C1_SHA
    native_archive = None
    if is_r46:
        need(len(parsed['section']) == 57,
             'Official R46 C1 export: unexpected Compiler entry count')
        need(NATIVE_R46_ARCHIVE.is_file(), 'Official R46 C1 export: frozen native archive missing')
        frozen = NATIVE_R46_ARCHIVE.read_bytes()
        need(sha(frozen) == NATIVE_R46_SHA,
             'Official R46 C1 export: native archive SHA changed')
        native_title = parse_lib(frozen)['title']
        provenance = 'frozen R46 C1 archive'
        native_archive = str(NATIVE_R46_ARCHIVE.relative_to(ROOT))
    else:
        # The protected active/library module pins the exact current and
        # LAST_GOOD SHA256, preserving the fail-closed policy across releases.
        from active_library import verify_active
        try:
            active, last_good, active_label = verify_active(ROOT)
        except (OSError, AssertionError, ValueError) as exc:
            raise ExportError(
                'Cannot verify SHA-pinned active/LAST_GOOD libraries; '
                'refusing untrusted Compiler wrapper') from exc
        if raw == active:
            provenance = 'verified active library: ' + active_label
        elif raw == last_good:
            provenance = 'verified LAST_GOOD library'
        else:
            raise ExportError(
                'Unsupported compiler-wrapped AP20 library: not the pinned '
                'active, LAST_GOOD or R46 C1 archive; source audit required')
        native_title = parsed['title']  # preserve title for byte-exact rewrap

    try:
        native = native_from_promoted(raw, native_title)
    except (ValueError, AssertionError) as exc:
        raise ExportError('Compiler wrapper has invalid Rbsr offsets or dispatcher') from exc
    if is_r46:
        need(native == frozen,
             'Official R46 C1 export: native code differs from frozen R46 archive')
    need(len(parse_lib(native)['section']) + 1 == len(parsed['section']),
         'Compiler wrapper: native/dispatcher entry count mismatch')
    need(wrap_native_ap20(native, parsed['title']) == raw,
         'Compiler wrapper: native-to-Compiler rewrap is not byte-exact')
    return native, {
        'format': 'Compiler-safe AP20 Rbsr monolith',
        'provenance': provenance,
        'official_sha256': sha(raw),
        'official_bytes': len(raw),
        'official_entries': len(parsed['section']),
        'native_sha256': sha(native),
        'native_bytes': len(native),
        'native_entries': len(parse_lib(native)['section']),
        'native_archive': native_archive,
        'verified_extract_and_rewrap': True,
        'warning': 'Native ASM output is NOT an installable .Lib; the Compiler-safe '
                   'AP20 bridge must be added again to any release build.'
    }


def sanitize(s):
    if s.lower().startswith('aga '):s=s[4:]
    s=re.sub('[^A-Za-z0-9]+','_',s.strip().title()).strip('_')
    return s or 'Private'

def col(bytes_,width=12):
    for i in range(0,len(bytes_),width):
        yield '    dc.b '+','.join('$%02X'%x for x in bytes_[i:i+width])

def byte_data(buf):
    """Source directives for *non-executable* ranges (no instruction masquerading)."""
    lines=[];j=0
    while j<len(buf):
        if buf[j]==0:
            k=j
            while k<len(buf) and buf[k]==0:k+=1
            if k-j>=6:lines.append(f'    dcb.b {k-j},0');j=k;continue
        k=j
        while k<len(buf) and 32<=buf[k]<127 and buf[k] not in (34,92):k+=1
        if k-j>=4:
            lines.append('    dc.b "'+buf[j:k].decode('ascii')+'"')
            j=k;continue
        n=min(12,len(buf)-j)
        lines.append('    dc.b '+','.join('$%02X'%x for x in buf[j:j+n]));j+=n
    return lines

def token_lines(tok_data,tokens):
    o=['C_Tk:','    ; AP20 token table: pointers are AP20 entry indices, not addresses']
    p=0
    for t in tokens:
        if t['start']>p:
            o+=list(col(tok_data[p:t['start']]))
        comment=(t['name'].replace('\0','<dummy>') or '<dummy>')
        o.append('Tk_%02d:  ; %s : %s'% (len([x for x in o if x.startswith('Tk_')]),comment,t['signature']))
        o.append('    dc.w %s,%s'%(t['instruction'],t['function']))
        name=t['name']
        sig=t['signature']
        if (name and len(name)>=2 and all(32<=ord(c)<127 and c not in '"\\' for c in name)
                and all(32<=ord(c)<127 and c not in '"\\' for c in sig)):
            # AMOS AP20 name: final letter has bit 7 set; the token
            # signature ends with 255 and entries are aligned on words.
            directive=('    dc.b "'+name[:-1]+'","'+name[-1]+'"+$80')
            if sig:directive+=',"'+sig+'"'
            directive+=',$FF'
            encoded=4+len(name)+len(sig)+1
            padding=t['end']-t['start']-encoded
            if padding==1:directive+=',0'
            elif padding!=0:raise ExportError('Bad token alignment')
            o.append(directive)
        else:
            o+=list(col(tok_data[t['start']+4:t['end']]))
        p=t['end']
    if p<len(tok_data):o+=list(col(tok_data[p:]))
    return o

def verified_r44_inherited_seeds(parsed):
    """Carry R43 CFG seeds across ONLY the four source-proven R44 BSR hooks.

    Source provenance is checked against the immutable R43 SHA, exact old
    entries, the complete new emitter output, exact call-site deltas and BSR
    targets. This never teaches the decoder to accept arbitrary changed code,
    nor trusts unverified claims in the binary title or a loose byte pattern.
    """
    sections=parsed['section']
    if len(sections)!=55 or b'M15bis Mouse Cursor R44 0.11.5' not in parsed['title']:
        return {}
    reference=ROOT/'dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib'
    need(reference.is_file(),'R44 strict source: R43 reference archive missing')
    frozen=reference.read_bytes()
    need(sha(frozen)=='9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf',
         'R44 strict source: R43 frozen SHA changed')
    old=parse_lib(frozen)['section']
    from m15bis_cursor_r44_emit import emit_cursor
    from build_m15bis_cursor_r44 import OWNED_CLOSES
    emitted,labels=emit_cursor()
    need(sections[54]['core']==emitted,'R44 strict source: new code changed from audited emitter')
    need(sections[53]['core']==old[53]['core'] and sections[53]['getp'],
         'R44 strict source: Circle core or GetP delimiter altered')
    target=sections[54]['file_offset']+labels['close_window_hook']
    for i in range(53):
        before=old[i]['core']
        after=sections[i]['core']
        if i not in OWNED_CLOSES:
            need(before==after, f'R44 strict source: unrelated historical entry changed: {i}')
            continue
        at=OWNED_CLOSES[i]
        need(len(before)==len(after) and before[at:at+4]==bytes.fromhex('4eaeffb8')
             and after[:at]==before[:at] and after[at+4:]==before[at+4:]
             and after[at:at+2]==bytes.fromhex('6100'),
             f'R44 strict source: invalid CloseWindow patch entry {i}')
        delta=struct.unpack_from('>h',after,at+2)[0]
        need(sections[i]['file_offset']+at+2+delta==target,
             f'R44 strict source: unexpected cleanup call target in entry {i}')
    # Known R43 state-bearing entry 0 contains executable secondary code
    # beyond its first RTS; its exact pre-R44 core is the sole provenance.
    seeds={0:set(KNOWN_SEEDS.get(sha(old[0]['core']),()))}
    need(seeds[0], 'R44 strict source: R43 state initialization seed not audited')
    for idx,marker in ((17,500),(18,540)):
        need(old[idx]['core'][marker:marker+8]==bytes.fromhex('FE11F700008C4E75')
             and sections[idx]['core'][marker:marker+8]==bytes.fromhex('FE11F700008C4E75'),
             'R44 strict source: AMOS keyboard return marker changed')
        seeds[idx]={marker+6}
    return seeds


def verified_r45_inherited_seeds(parsed):
    """Strict source-backed inheritance from the exact published R44 binary.

    R45 changes only the R44 last GetP delimiter and appends the NEW R45
    entry. Validate SHA, every former core, the complete emitter output,
    API token prefix and GetP. Never authorize arbitrary R44 byte changes.
    Inherited unreachable code seeds are independently verified by the
    already-audited R44/R43 provenance rules.
    """
    sections=parsed["section"]
    if len(sections)!=56 or b"M16 Image Draw R45 0.12.0" not in parsed["title"]:
        return {}
    frozen_path=ROOT/"dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib"
    need(frozen_path.is_file(), "R45 strict source: R44 frozen archive missing")
    frozen=frozen_path.read_bytes()
    need(sha(frozen)=="0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc",
         "R45 strict source: R44 archive SHA changed")
    original=parse_lib(frozen)
    old=original["section"]
    need(len(old)==55, "R45 strict source: wrong R44 archive segment count")
    for index in range(55):
        need(sections[index]["core"] == old[index]["core"],
             f"R45 strict source: inherited core changed at entry {index}")
        expected_getp=(True if index==54 else old[index]["getp"])
        need(sections[index]["getp"]==expected_getp,
             f"R45 strict source: unexpected GetP at entry {index}")
    from m16_image_draw_r45_emit import emit_image_draw
    new_core,_=emit_image_draw()
    need(sections[55]["core"]==new_core and not sections[55]["getp"],
         "R45 strict source: new CPU entry differs from audited emitter")
    from audit_ap20 import token
    from ap20_utils import split
    old_tokens=split(frozen)[0]
    new_tokens=parsed["token_data"]
    expected=(old_tokens[:-6]
              +token("aga image draw",1,55,"00,0,0,0,0")
              +bytes(6))
    need(new_tokens==expected, "R45 strict source: AP20 token ABI changed")
    return verified_r44_inherited_seeds(original)



def verified_r46_inherited_seeds(parsed):
    """Require exact frozen failed R45 provenance before decoding repaired R46.

    No generic whitelisting: 55 old AP20 segments and all token bytes must
    match the published R45 SHA, with exactly one revised source-backed R46
    segment 55. Cross-entry seeds are inherited from R45 only after its
    independent R44/R43 checks pass.
    """
    sections=parsed["section"]
    if len(sections)!=56 or b"M16 Image Draw R46 0.12.1" not in parsed["title"]:
        return {}
    old_path=ROOT/"dist/experimental/AMOSPro_AGA_M16_v0.12.0_IMAGE_DRAW_R45.Lib"
    need(old_path.is_file(),"R46 strict source: failed R45 frozen archive missing")
    frozen=old_path.read_bytes()
    need(sha(frozen)=="0d780b4648214c36e8f291d9575390462d174cd8ba22cac2188324b75bd220d7",
         "R46 strict source: R45 failed archive SHA changed")
    old=parse_lib(frozen)
    need(len(old["section"])==56,"R46 strict source: R45 segment count changed")
    for index in range(55):
        need(sections[index]["core"]==old["section"][index]["core"] and
             sections[index]["getp"]==old["section"][index]["getp"],
             f"R46 strict source: inherited AP20 entry {index} changed")
    from m16_image_draw_r45_emit import emit_image_draw
    new_core,_=emit_image_draw(accept_loaded_flags_zero=True)
    need(sections[55]["core"]==new_core and not sections[55]["getp"],
         "R46 strict source: candidate differs from explicit flags-zero repair emitter")
    need(parsed["token_data"]==old["token_data"],
         "R46 strict source: AP20 token/signature changed")
    return verified_r45_inherited_seeds(old)


def verified_current_compiler_seeds(parsed):
    """Source-backed CFG entrypoints for the exact pinned R54/R57 native images.

    The R46 native archive authenticates inherited routines; active_library
    authenticates the current and LAST_GOOD Compiler wrappers. No altered,
    independently rebuilt, or future unknown binary receives these seeds.
    """
    from active_library import verify_active
    from compiler_relocation import native_from_promoted, repack_ap20
    from compiler_bridge_v2_probe import is_v2_wrapped, unwrap_native_parts_v2
    current, last_good, _ = verify_active(ROOT)
    def reconstruct(blob):
        if is_v2_wrapped(blob):
            tok, parts = unwrap_native_parts_v2(blob)
            return repack_ap20(blob, tok, parts, parse_lib(blob)['title'])
        return native_from_promoted(blob, parse_lib(blob)['title'])
    frozen = NATIVE_R46_ARCHIVE.read_bytes()
    need(sha(frozen) == NATIVE_R46_SHA,
         'Strict source: inherited R46 native archive changed')
    original = parse_lib(frozen)['section']
    current_native = reconstruct(current)
    protected_native = reconstruct(last_good)
    # Reproduce historical R54 from its immutable archive, not the mutable
    # "LAST_GOOD" pointer: the author promoted R57 after its WinUAE Gates.
    r54_archive = ROOT/'dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib'
    r54_blob = r54_archive.read_bytes()
    need(sha(r54_blob) == 'f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0', 'R54 provenance archive changed')
    good_native = native_from_promoted(r54_blob, parse_lib(r54_blob)['title'])
    raw = parsed['raw']
    sections = parsed['section']
    r61_case = False
    if len(sections) == 61:
        from build_m18_r61_ficon import build as build_r61
        r61_blob,_=build_r61()
        r61_case = (raw == reconstruct(r61_blob))
    r58_case = (len(sections) == 61 and not r61_case)
    r60_case = (len(sections) == 60)
    # R59 is now historical: it is no longer the current/LAST_GOOD.
    # Trust only its deterministic SHA-pinned reconstruction, not
    # any arbitrary 59-entry image.
    r59_case = False
    if len(sections) == 59:
        from build_m17_r59_compact_v2 import build as build_r59
        r59_blob, _ = build_r59()
        r59_case = (raw == reconstruct(r59_blob))
    region_getadr_pos = None
    if r61_case:
        # Entire R61 image must match the deterministic source-backed builder.
        from m18_ficon_ap20_emit import emit_ficon_ap20,GETADR_MARKER as FICON_MARKER
        from m18_image_region_emit import emit_image_region,GETADR_MARKER as REGION_MARKER
        from build_m18_r61_ficon import build as build_r61
        candidate,_=build_r61()
        need(raw==reconstruct(candidate),'Strict source: R61 differs from builder')
        region,_=emit_image_region()
        ficon,ficon_labels=emit_ficon_ap20()
        need(sections[59]['core']==region and sections[59]['getp'],
             'Strict source: R61 changed old R60 native or GetP')
        need(sections[60]['core']==ficon,
             'Strict source: R61 FIcon emitter mismatch')
        need(region.count(REGION_MARKER)==1 and ficon.count(FICON_MARKER)==1,
             'Strict source: R61 GetAdr marker count changed')
    if r60_case:
        # SHA-authenticated, reproducible native R60 with one additive
        # source-backed routine and its source-derived Rjsr marker.
        from build_m18_r60_image_region import build as build_r60
        from m18_image_region_emit import emit_image_region, GETADR_MARKER
        v2_blob, _meta = build_r60()
        need(raw == reconstruct(v2_blob),
             'Strict source: R60 native differs from deterministic builder')
        region_core, _labels = emit_image_region()
        need(sections[59]['core'] == region_core,
             'Strict source: R60 image region body changed')
        need(region_core.count(GETADR_MARKER) == 1,
             'Strict source: R60 Bnk.GetAdr relocation marker changed')
        region_getadr_pos = region_core.index(GETADR_MARKER)
    if r58_case:
        # Treat the new padding as DATA, never a speculative 68000 routine.
        from build_m17_r58_compiler_bridge import build as build_r58, FAR_PROBE
        v2_blob, info = build_r58()
        need(raw == reconstruct(v2_blob),
             'Strict source: R58 native code differs from exact in-memory builder')
        need(len(sections[59]['core']) == 9252 and not any(sections[59]['core']),
             'Strict source: R58 data padding changed')
        need(sections[60]['core'] == FAR_PROBE,
             'Strict source: R58 far diagnostic marker changed')
    elif not r60_case and not r61_case and len(sections) != 59:
        return {}
    if raw not in (current_native, good_native, protected_native) and not (r58_case or r59_case or r60_case or r61_case):
        return {}
    for i in (0, 17, 18):
        need(sections[i]['core'] == original[i]['core'],
             f'Strict source: inherited native entry {i} changed')
    need(sections[0]['core'][56:60] == bytes.fromhex('48e7fffe'),
         'Strict source: R46 embedded private helper moved')
    for i, offset in ((17,500),(18,540)):
        need(sections[i]['core'][offset:offset+8] ==
             bytes.fromhex('fe11f700008c4e75'),
             f'Strict source: AMOS keyboard marker changed at entry {i}')
    # R46 inherited entry 0 has TWO audited helper starts (0x38/0x66).
    seeds = {0: {56, 102}, 17: {506}, 18: {546}, 56: {1192}}
    need(sections[56]['core'][1192:1196] == bytes.fromhex('206a0020'),
         'Strict source: R54 image helper moved')
    # R53 Bnk.GetAdr / Reserve / Change / Eff AMOS linker indices.
    # Pin the complete 6-byte marker at every position, not just FE11.
    linked = ((56,586,0x031d),(56,818,0x031d),(56,848,0x0330),
              (56,1118,0x0333),(56,1138,0x0320),
              (57,58,0x031d),(58,38,0x031d))
    for i, offset, index in linked:
        expected = bytes.fromhex('fe11f700') + struct.pack('>H', index)
        need(sections[i]['core'][offset:offset+6] == expected,
             f'Strict source: AMOS Rjsr marker changed at entry {i} +{offset}')
        seeds.setdefault(i,set()).add(offset+6)
    if raw == good_native:
        need(sections[20]['core'] == original[20]['core'],
             'Strict source: R54 inherited Back Fill changed')
        need(len(sections[58]['core']) == 110,
             'Strict source: R54 native final entry changed')
    else:
        good = parse_lib(good_native)['section']
        need(sections[20]['core'][:4] == bytes.fromhex('600052fa') and
             sections[20]['core'][4:] == good[20]['core'][4:],
             'Strict source: R57 Back Fill forwarding patch changed')
        need(sections[58]['core'][:len(good[58]['core'])] == good[58]['core'] and
             len(sections[58]['core']) == len(good[58]['core'])+620 and
             sections[58]['core'][110:114] == bytes.fromhex('48e7efee'),
             'Strict source: R57 in-place RastPort helper changed')
        seeds[20] = {4}
        seeds[58].add(110)
    if r58_case:
        seeds[60] = {0}  # only the two source-proven NOP/RTS instructions
    if r60_case:
        # Decode after the literal AMOS linker marker; never interpret
        # FE11 as Motorola code or trust an arbitrary candidate.
        seeds[59] = {region_getadr_pos + 6}
    if r61_case:
        # Exact source-proven AMOS linker boundaries in both native sections.
        seeds[59] = {region.index(REGION_MARKER)+6}
        seeds[60] = {ficon.index(FICON_MARKER)+6, ficon_labels["core"]}
    return seeds


def analyze_entries(parsed):
    sections=parsed['section']
    base=parsed['code_start']
    # Shared private helpers can live after the first RTS of another AP20
    # entry. R23 calls IDCMP key_next inside entry 33 from entries 17/18.
    # Discover cross-entry seeds exclusively from decoded CALL targets.
    seeds={s['id']:set(KNOWN_SEEDS.get(sha(s['core']),())) for s in sections}
    inherited=verified_r44_inherited_seeds(parsed)
    for index, extra in verified_current_compiler_seeds(parsed).items():
        inherited.setdefault(index,set()).update(extra)
    for verifier in (verified_r45_inherited_seeds, verified_r46_inherited_seeds):
        for index,extra in verifier(parsed).items():
            inherited.setdefault(index,set()).update(extra)
    for index,extra in inherited.items():seeds[index].update(extra)
    # In R23, legacy keyboard exits contain an AMOS Rjsr linking marker
    # (6 bytes of non-CPU data) followed by a real RTS. Seeds must be tied
    # to the exact audited R23 keyboard CORE, not to the whole HUNK SHA:
    # R24 adds one later AP20 entry while leaving these key routines intact.
    # For descendants, validate the source archive's complete SHA and the
    # FULL keyboard entry bytes before accepting the RTS seeds. A modified
    # keyboard entry is NOT trusted, even if the eight marker bytes match.
    golden = None
    if sha(parsed['raw']) != R23_SHA and len(sections) > 34:
        archived = ROOT/'dist'/'experimental'/'AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib'
        if archived.is_file():
            frozen = archived.read_bytes()
            if sha(frozen) == R23_SHA:
                golden = parse_lib(frozen)['section']
    for idx,marker in ((17,500),(18,540)):
        is_frozen = sha(parsed['raw']) == R23_SHA
        current_core = sections[idx]['core']
        is_unchanged = (golden is not None and
                        current_core == golden[idx]['core'])
        # M12/R27 grows earlier Copy/Fill entries. The original R23
        # keyboard BSR.W (at 0x30) MUST be recalculated to entry33 key_next.
        # Permit the already-audited RTS exit seed ONLY when its entire
        # keyboard core is byte-exact R23 APART from those two displacement
        # bytes, and the new BSR targets the exact known private helper.
        # Never accept arbitrary keyboard changes or a relocated call
        # pointing anywhere else, even when the exit marker is present.
        is_relocated = False
        if (golden is not None and len(sections) > 33 and
                len(current_core) == len(golden[idx]['core']) and
                current_core[0x30:0x32] == b'\x61\x00' and
                current_core[:0x32] == golden[idx]['core'][:0x32] and
                current_core[0x34:] == golden[idx]['core'][0x34:] and
                len(sections[33]['core']) > 540 and
                sections[33]['core'][538:540] == b'\x61\x00'):
            relative = struct.unpack_from('>h', current_core, 0x32)[0]
            target = sections[idx]['file_offset'] + 0x32 + relative
            is_relocated = (target == sections[33]['file_offset'] + 538)
        if is_frozen or is_unchanged or is_relocated:
            need(sections[idx]['core'][marker:marker+8]
                 ==bytes.fromhex('FE11F700008C4E75'),
                 'Unexpected audited R23 keyboard exit bytes')
            seeds[idx].add(marker+6)
    for _ in range(len(sections)+1):
        blocks={}
        for s in sections:
            core=s['core']; off=s['file_offset']
            blocks[s['id']]=flow_decode(
                core,off,tuple(off+x for x in sorted(seeds[s['id']]))
            ) if core else {}
        changed=False
        for decoded in blocks.values():
            for op in decoded.values():
                if not op.call or op.target is None or (op.target & 1):
                    continue
                for dest in sections:
                    begin=dest['file_offset']
                    if begin<=op.target<begin+len(dest['core']):
                        relative=op.target-begin
                        if relative not in seeds[dest['id']]:
                            seeds[dest['id']].add(relative)
                            changed=True
                        break
        if not changed:break
    else:
        raise ExportError('Non-convergent AP20 cross-entry control flow')

    # An existing branch can bypass a single NOP/RTS left by a patch.
    # Only classify an aligned 2-byte gap that is precisely one known
    # instruction AND borders independently decoded code. Do not guess
    # arbitrary code from bytes; --strict still rejects every other gap.
    for s in sections:
        core=s['core']; off=s['file_offset']; decoded=blocks[s['id']]
        covered=bytearray(len(core))
        for p,op in decoded.items():
            covered[p-off:p-off+op.size]=bytes([1])*op.size
        decoder=Decoder(core,off)
        cursor=0
        while cursor<len(core):
            if covered[cursor]:
                cursor+=1
                continue
            begin=cursor
            while cursor<len(core) and not covered[cursor]:
                cursor+=1
            if (cursor-begin==2 and begin%2==0
                    and core[begin:cursor] in (b'\x4e\x71',b'\x4e\x75')
                    and ((begin>0 and covered[begin-1])
                         or (cursor<len(core) and covered[cursor]))):
                op=decoder.decode(off+begin)
                if op is not None and op.size==2 and op.op in ('nop','rts'):
                    decoded[off+begin]=op

    ins={p:obj for decoded in blocks.values() for p,obj in decoded.items()}
    coverage=sum(obj.size for obj in ins.values())
    count=len(ins)
    labels={}
    for s in sections:
        idx=s['id'];off=s['file_offset']
        label='Aga_'+sanitize(s['names'][0]) if s['names'] else ('Internal_%02d'%idx)
        labels[off]=label
    for obj in ins.values():
        for dest in [obj.target,*obj.data_refs]:
            if dest is None:continue
            if base<=dest<parsed['code_end'] and dest%2==0:
                if dest not in labels:labels[dest]=f'L_{dest:06X}'
    return blocks,labels,coverage,count

def output(parsed,stem='AMOSPro_AGA'):
    raw=parsed['raw'];block,labels,coverage,nins=analyze_entries(parsed)
    total=sum(len(s['core']) for s in parsed['section'])
    hasha=sha(raw)
    title=parsed['title'].decode('latin1').replace('\0',' | ').strip()
    result=[
        '; AMOS Professional 365 — AGA extension native 68000 source restoration',
        '; Generated from the actual AP20/HUNK image, NOT the historical M1 source.',
        '; All recognized executable instructions are real Motorola mnemonics.',
        '; Remaining dc.b/dcb.b encode strings, state/data, AMOS Rjsr markers,',
        '; or code that cannot be safely identified. They are never silently lost.',
        '; A native assembler comparison is REQUIRED before treating this file',
        '; as byte-identical or using it as the replacement build authority.',
        '; SHA256 original: '+hasha,
        '; Build: '+title,
        '; Syntax target: vasm mot / Genam-style source (68020-capable).',
        '',
        '    cpu 68020',
        '',
        'AGA_StatePtr equ $01C8',
        'AGA_Width equ 12',
        'AGA_Height equ 16',
        'AGA_Window equ 36',
        'WD_LeftEdge equ 4',
        'WD_TopEdge equ 6',
        'WD_MouseY equ 12',
        'WD_MouseX equ 14',
        'WD_Screen equ 46',
        '',
        '; Standalone binary HUNK wrapper: -Fbin, NOT -Fhunk',
        'HUNK_HEADER:',
        '    dc.l $000003F3,0,1,0,0',
        '    dc.l (HUNK_DATA_END-HUNK_DATA)/4',
        '    dc.l $000003E9',
        '    dc.l (HUNK_DATA_END-HUNK_DATA)/4',
        'HUNK_DATA:',
        '    dc.l C_Tk-C_Off,C_Lib-C_Tk,C_Title-C_Lib,C_End-C_Title',
        '    dc.w 0',
        '    dc.b "AP20"',
        'C_Off:',
        '    ; Entry sizes in WORDS (not offsets). The last marker is an end label.',
    ]
    n=len(parsed['section'])
    for i in range(n):result.append(f'    dc.w (Entry_{i+1:02d}-Entry_{i:02d})/2')
    result+=token_lines(parsed['token_data'],parsed['tokens'])
    result+=['','C_Lib:']
    # Build map of code positions to support branch and data refs.
    all_ins={p:ins for blocki in block.values() for p,ins in blocki.items()}
    labelAt={int(k):v for k,v in labels.items()}
    for s in parsed['section']:
        idx=s['id'];file_base=s['file_offset'];core=s['core'];dec=block[idx]
        result+=['','; -------- AP20 entry %02d : %s --------'% (idx,', '.join(s['names']) or 'private/reserved'),
                 f'Entry_{idx:02d}:']
        if core and file_base in labelAt:
            result.append(labelAt[file_base]+':')
        at=0
        while at<len(core):
            pos=file_base+at
            if pos in labelAt and pos!=file_base:result.append(labelAt[pos]+':')
            obj=dec.get(pos)
            if obj:
                line=obj.text
                if obj.target is not None and obj.target in labelAt and ('@' in line):
                    line=re.sub(r'@\$[0-9A-Fa-f]+',labelAt[obj.target],line)
                if obj.data_refs and obj.data_refs[0] in labelAt and '(pc)' in line:
                    line=re.sub(r'-?\d+\(pc\)',labelAt[obj.data_refs[0]]+'(pc)',line, count=1)
                original=core[at:at+obj.size]
                if idx in (28,29) and sha(parsed['raw'])==R19_SHA:
                    # Symbolic field names are grounded in the *exact* R19
                    # source builder, never generalized by guessed offsets.
                    field_map={'456(a5)':'AGA_StatePtr(a5)',
                               '36(a2)':'AGA_Window(a2)',
                               '46(a1)':'WD_Screen(a1)'}
                    field_map.update({'12(a2)':'AGA_Width(a2)','14(a1)':'WD_MouseX(a1)',
                                      '4(a1)':'WD_LeftEdge(a1)'} if idx==28 else
                                     {'16(a2)':'AGA_Height(a2)','12(a1)':'WD_MouseY(a1)',
                                      '6(a1)':'WD_TopEdge(a1)'})
                    for old,new in field_map.items():line=line.replace(old,new)
                result.append(f'    {line:<49} ; +${at:04X} : {original.hex().upper()}')
                at+=obj.size
            else:
                start=at
                while at<len(core) and file_base+at not in dec and (at==start or file_base+at not in labelAt):at+=1
                b=core[start:at]
                # AMOS Rjsr linking marker is a macro expansion, not a CPU opcode.
                if b.startswith(bytes.fromhex('FE11F700008C')):
                    result.append('    dc.w $FE11,$F700,$008C  ; AMOS Rjsr L_Test_PaSaut')
                    b=b[6:]
                result+=byte_data(b)
        if s['getp']:
            result.append('    dc.b "GetP"                       ; AP20 parameter delimiter, NOT 68000 code')
    result+=['',f'Entry_{n:02d}:','C_Title:']
    result+=byte_data(parsed['title'])
    result+=['C_End:','    dc.w 0','    cnop 0,4','HUNK_DATA_END:','    dc.l $000003F2','']
    manifest={
      'source':'AP20 binary reconstructed using safe 68000 CFG disassembly',
      'native_reassembly_verified':False,
      'sha256':hasha,'size':len(raw),'title':title,
      'entries':n,'decoded_instructions':nins,'decoded_code_bytes':coverage,
      'total_segment_code_bytes':total,'recognized_percent':round(100*coverage/total,2),
      'warning':'No native vasm/Genam byte-for-byte roundtrip proven. Data and unrecognized opcodes remain dc.b.',
      'entry_reports':[{ 'id':s['id'],'api':s['names'],'size':len(s['data']),
                'decoded_bytes':sum(x.size for x in block[s['id']].values()),
                'getp':s['getp'] }for s in parsed['section']],
    }
    return '\n'.join(result),manifest

def validate_structure(src,parsed):
    for entry in parsed['section']:
        i=entry['id']
        need(f'Entry_{i:02d}:' in src, f'Missing entry label {i}')
        if entry['getp']:need(src.count('dc.b "GetP"')>=1,'Missing GetP')
    need(src.count('AP20 entry')>=len(parsed['section']),'Missing entry description')

def unclassified_gaps(parsed):
    """Treat zeros, identifiable ASCIIZ, and AMOS Rjsr markers as data.

    A non-text gap is NOT automatically recast as DC.B code in strict mode.
    This ensures future releases refuse silent code regressions.
    """
    block,_,_,_=analyze_entries(parsed)
    trusted_r54_r57 = bool(verified_current_compiler_seeds(parsed))
    problems=[]
    for sec in parsed['section']:
        core=sec['core'];loc=sec['file_offset'];instructions=block[sec['id']]
        covered=set()
        for offset,insn in instructions.items():covered.update(range(offset,offset+insn.size))
        gaps=[];seq=[]
        for j in range(len(core)):
            if loc+j in covered:
                if seq:gaps.append((seq[0],bytes(core[x] for x in seq)));seq=[]
            else:seq.append(j)
        if seq:gaps.append((seq[0],bytes(core[x] for x in seq)))
        for pos,b in gaps:
            # Remove exact AMOS Rjsr pseudo-ops; they are machine-level
            # AMOS link markers but not executable Motorola opcodes.
            b=b.replace(bytes.fromhex('FE11F700008C'),b'')
            if trusted_r54_r57:
                for index in (0x031d, 0x0330, 0x0333, 0x0320):
                    b=b.replace(bytes.fromhex('FE11F700') +
                                struct.pack('>H', index),b'')
            # Report a problematic region once, not once per zero-delimited
            # fragment (the old exporter repeated the R23 250-byte gap).
            fragments=[part for part in b.split(b'\0') if part]
            if any(not (len(part)>=3 and all(32<=x<127 for x in part))
                   for part in fragments):
                problems.append({'entry':sec['id'],'offset':pos,'length':len(b),
                                 'bytes':b.hex()[:64]})
    return problems

def find_baseline(root:Path,current:bytes):
    """Find a matching current builder by ARCHIVE literal, read BASE literal.

    Reading Python AST is safe; the builder is NOT executed, and LAST_GOOD or
    archived .Libs are never modified.
    """
    for p in sorted((root/'tools').glob('build_*.py')):
        try: ast_tree=ast.parse(p.read_text(encoding='utf-8'))
        except (OSError,SyntaxError,UnicodeError):continue
        values={}
        for node in ast_tree.body:
            if not isinstance(node,ast.Assign):continue
            if not isinstance(node.value,ast.BinOp) or not isinstance(node.value.op,ast.Div):continue
            if not isinstance(node.value.left,ast.Name) or node.value.left.id!='ROOT':continue
            if not isinstance(node.value.right,ast.Constant) or not isinstance(node.value.right.value,str):continue
            for target in node.targets:
                if isinstance(target,ast.Name): values[target.id]=root/node.value.right.value
        archive=values.get('ARCHIVE')
        base=values.get('BASE')
        if archive is None or base is None or not archive.is_file():continue
        if archive.read_bytes()==current and base.is_file():return base,p
    return None,None

def main(argv=None):
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument('--lib',default='dist/AMOSPro_AGA.Lib',help='Current candidate .Lib (read-only)')
    pa.add_argument('--out',default='src/generated',help='Generated assembler directory')
    pa.add_argument('--verify-vasm',default=None,metavar='VASMM68K_MOT',help='Optional native assembler binary for byte-exact comparison')
    pa.add_argument('--baseline',default='auto',help='Optional previous .Lib, or auto (default) for changed entry report')
    pa.add_argument('--strict',action='store_true',help='Reject any nondecoded range that cannot be classified as data/AMOS marker')
    args=pa.parse_args(argv)
    root=Path(__file__).resolve().parents[1]
    input_path=Path(args.lib)
    if not input_path.is_absolute():input_path=root/input_path
    try:
        data=input_path.read_bytes()
        source_data,compiler_context=source_binary_from_input(data)
        parsed=parse_lib(source_data)
        source,report=output(parsed)
        if compiler_context:
            source=('; Restored from SHA-pinned Compiler-safe Rbsr wrapper, in memory only.\n'
                    '; Native assembler source is NOT an installable AMOS Compiler library.\n'
                    '; Production builds MUST apply compiler_relocation.wrap_native_ap20().\n\n'
                    +source)
            report['compiler_wrapper']=compiler_context
        report['input_sha256']=sha(data)
        report['input_size']=len(data)
        validate_structure(source,parsed)
        unresolved=unclassified_gaps(parsed)
        report['unclassified_regions']=unresolved
        if args.strict and unresolved:
            raise ExportError('Unclassified bytes: '+json.dumps(unresolved[:10])+                              '. A new instruction form/manual source audit is required.')
        m=re.search(r'\bR(\d+)\s+(\d+\.\d+\.\d+)',report['title'],re.I)
        version='R'+m.group(1) if m else sha(source_data)[:12]
        if compiler_context:version += '_C1'
        target=Path(args.out)
        if not target.is_absolute():target=root/target
        target=target.resolve()
        protected=(root/'dist').resolve()
        if target==protected or protected in target.parents:
            raise ExportError('Refusing to write any generated source inside dist/')
        target.mkdir(parents=True,exist_ok=True)
        path=target/('AMOSPro_AGA_'+version+'_NATIVE.s')
        path.write_text(source.replace(chr(0x2014),'-').encode('ascii','backslashreplace').decode('ascii'),encoding='ascii',newline='\n')
        report['input_file']=str(input_path)
        report['output_file']=str(path)
        baseline_path=None
        if args.baseline=='auto':
            baseline_path,builder=find_baseline(root,source_data)
            report['matched_builder']=str(builder) if builder else None
        elif args.baseline and args.baseline.lower()!='none':baseline_path=Path(args.baseline)
        if baseline_path:
            older=parse_lib(baseline_path.read_bytes())
            report['baseline']=str(baseline_path)
            changes=[]
            for s in parsed['section']:
                i=s['id'];before=older['section'][i]['core'] if i<len(older['section']) else None
                if s['core']!=before:changes.append({'entry':i,'api':s['names']})
            report['modified_or_new_entries']=changes
        man=target/('AMOSPro_AGA_'+version+'_NATIVE.json')
        man.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print('Assembler source:',path)
        print('Manifest:',man)
        print('Recognized code bytes: %d/%d (%.2f%%)'%(report['decoded_code_bytes'],report['total_segment_code_bytes'],report['recognized_percent']))
        print('Input SHA256:',sha(data))
        if compiler_context:
            print('Compiler-safe: %d wrapped AP20 entries -> %d native source entries (verified)' %
                      (compiler_context['official_entries'], compiler_context['native_entries']))
            print('Extracted native SHA256:',sha(source_data))
            print('IMPORTANT: do not install native output; Compiler-safe wrapping is mandatory')
        print('NOTE: native assembly/rebuild not yet proven; do not replace any .Lib')
        if args.verify_vasm:
            binary=target/('AMOSPro_AGA_'+version+'_ASSEMBLED.Lib')
            cmd=[args.verify_vasm,'-Fbin','-m68020','-quiet','-o',str(binary),str(path)]
            try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
            except (OSError,subprocess.TimeoutExpired) as e:raise ExportError('Assembler launch failed: '+str(e)) from e
            if r.returncode:
                print(r.stdout,r.stderr,file=sys.stderr)
                raise ExportError('Native assembler reported an error; source not verified')
            if binary.read_bytes()!=source_data:
                raise ExportError('Native assembler output DOES NOT match extracted source code; do not use')
            if compiler_context:
                from compiler_relocation import wrap_native_ap20
                rewrapped=wrap_native_ap20(binary.read_bytes(),parse_lib(data)['title'])
                need(rewrapped==data,
                     'Native assembly succeeds but Compiler rewrap differs from official .Lib')
                report['compiler_rewrap_verified']=True
            report['native_reassembly_verified']=True
            man.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            if compiler_context:
                print('VERIFIED: native assembly and Compiler rewrap match official .Lib byte-for-byte')
            else:
                print('VERIFIED: native assembly is byte-for-byte identical to input .Lib')
        return 0
    except (OSError,ExportError,ValueError,struct.error) as exc:
        import traceback
        print('ERROR:',exc or type(exc).__name__,file=sys.stderr)
        traceback.print_exc()
        return 1
if __name__=='__main__':raise SystemExit(main())
