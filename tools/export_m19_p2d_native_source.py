#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""Generate 68020 mnemonic source from the SHA-verified M19 P2d source build.

This is an audited migration from Python emitters to editable Motorola syntax.
It refuses unknown binaries. Raw AP20 linker words and embedded data are
retained as data; no generated source or assembly replaces a shipped library.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from struct import unpack_from
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from active_library import P2D_SHA, verify_active
from build_m19_p2d_in_memory import build_p2d
from build_m19_p1e_bank_edit_in_memory import build_p1e
from compiler_bridge_v2_probe import DISPATCH_V2
from compiler_relocation import GETP, RBSR, unpack_ap20
from export_aga_asm import decode_exact_asm, export_asm, parse_ap20
from generate_aga_multiunit_source import (
    _assemble, _source_lines_for_data, digest, native_unit_source,
    trace_unit_code,
)
from m19_p2d_bob_auto_update_emit import emit_bob_auto_update

EXPECTED_SIZE = 136020
EXPECTED_ENTRIES = 203
EXPECTED_COMMANDS = 100


def need(condition: bool, description: str) -> None:
    if not condition:
        raise ValueError("M19 P2d source: " + description)


def validate_source_build(data: bytes, root: Path):
    """Authorize ONLY the one known immutable P2d build and its real emitter."""
    need(len(data) == EXPECTED_SIZE and digest(data) == P2D_SHA,
         "unknown .Lib; expected exact M19 P2d 136020-byte SHA")
    _active, last_good, _label = verify_active(root)
    need(bytes(last_good) == data,
         "LAST_GOOD does not match promoted P2d")
    rebuilt, info = build_p2d()
    need(rebuilt == data and info['sha256'] == P2D_SHA,
         "deterministic P2d Python builder does not match selected .Lib")
    need(info['entries'] == EXPECTED_ENTRIES and
         info['commands'] == EXPECTED_COMMANDS,
         "unexpected P2d table layout")
    return info


def parse_native_groups(data: bytes):
    tokens, parts, title = unpack_ap20(data)
    need(len(parts) == EXPECTED_ENTRIES, "wrong AP20 entry count")
    groups = tuple(i for i, part in enumerate(parts)
                   if len(part) > len(DISPATCH_V2) and part.startswith(DISPATCH_V2))
    need(len(groups) in (4, 5, 6), "unexpected V2 unit count")
    references = defaultdict(list)
    for i, part in enumerate(parts):
        if i in groups or part in (b"", GETP):
            continue
        need(len(part) in (8, 12) and part[:2] == RBSR and
             part[6:8] == b"\x4e\x75" and
             (len(part) == 8 or part[8:] == GETP),
             "nonstandard public AP20 entry %d" % i)
        target, rel = unpack_from(">HH", part, 2)
        need(target in groups, "public entry %d references missing group %d" % (i, target))
        need(not (rel & 1) and rel < len(parts[target]) - len(DISPATCH_V2),
             "public entry %d has invalid group offset" % i)
        references[target].append((i, len(DISPATCH_V2) + rel))
    need(all(references.get(i) for i in groups), "unreferenced native group")
    need(decode_exact_asm(export_asm(parse_ap20(data), None, None)[0]) == data,
         "independent AP20/HUNK exact-byte source check failed")
    return tokens, parts, title, groups, references


def p2d_symbolic_labels(parts, info):
    """Recover human procedure names from LIVE Python emitter symbol table."""
    _, prev = build_p1e()
    bobs, labels, service_offset = emit_bob_auto_update(prev['context_delta'])
    unit_id = info['group']
    need(parts[unit_id].endswith(bobs),
         "P2d source emitter does not match compiled BOBS group suffix")
    prefix = len(parts[unit_id]) - len(bobs)
    symbols = defaultdict(list)
    for name, pos in labels.items():
        abspos = prefix + pos
        need(0 <= abspos < len(parts[unit_id]) and not(abspos & 1),
             "invalid source label " + name)
        symbols[abspos].append(name)
    return unit_id, symbols


def sanitize_illegal_pc_dest(text: str, report: dict) -> str:
    """Do not invent a MOVE to a PC-relative destination (illegal on 68020).

    The generic decoder accepts destination EA reg=2/3, mode=7, which is
    legal as a source but NOT as MOVE's destination. Literal source-backed
    bytes remain intact until a real instruction/data source can be proven.
    """
    import re
    out=[]
    rejected=[]
    for line in text.splitlines():
        if re.search(r"^\s*move\.[bwl]\s+[^;]*,\s*[-+]?\d+\(pc(?:,[^)]*)?\)",line):
            m=re.search(r";\s*\+\$([0-9A-F]{5}):\s*([0-9A-F]+)$",line)
            need(m is not None, 'unrecoverable source-backed illegal MOVE encoding')
            raw=bytes.fromhex(m.group(2))
            out.append('    dc.b '+','.join('$%02X'%b for b in raw)+
                       '  ; +$'+m.group(1)+': invalid MOVE destination; audit')
            rejected.append((m.group(1),len(raw)))
        else:
            out.append(line)
    if rejected:
        report['illegal_move_dest_bytes_preserved']=sum(s for _,s in rejected)
        report['illegal_move_dest_source_offsets']=[x for x,_ in rejected]
        report['mnemonic_bytes']-=sum(s for _,s in rejected)
        report['raw_dc_bytes']+=sum(s for _,s in rejected)
        report['unresolved_instruction_encodings']+=len(rejected)
    return '\n'.join(out)+'\n'


def enrich_labels(text: str, name: str, symbols: dict[int, list[str]]) -> tuple[str, int]:
    """Publish Python emitter labels as ASSEMBLER labels, not binary offsets.

    Place names at proven instruction/data boundaries. For a symbol inside a
    DC.B block, publish an EQU relative to the native group's UNIT label;
    this does not split the original byte sequence or break the assembler.
    """
    import re
    out=[]
    defined=set()
    for line in text.splitlines():
        # Both mnemonic and data lines carry an audited +$00000 offset.
        match=re.search(r"\+\$([0-9A-F]{5}):",line)
        if match:
            off=int(match.group(1),16)
            for alias in sorted(symbols.get(off,())):
                if alias not in defined:
                    out.append(alias + ':')
                    defined.add(alias)
        out.append(line)
    # If a verified emitter label points into the middle of an untouched data
    # block, retain it as an exact offset EQU rather than adding a fake opcode.
    rest=[]
    for off, aliases in symbols.items():
        for alias in sorted(aliases):
            if alias not in defined:
                rest.append('%s equ UNIT_%s+$%05X' % (alias,name,off))
                defined.add(alias)
    if rest:
        out[0:0]=['; Verified external emitter aliases (relative to native group):',
                   *rest,'']
    return "\n".join(out) + "\n",len(defined)


def linked_source(data: bytes, parts, title, files: dict[int,str]) -> str:
    """AP20/HUNK envelope, each live unit INCLUDED as 68020 instructions."""
    from generate_aga_multiunit_source import _source_lines_for_data
    raw_tokens, _, _ = unpack_ap20(data)
    lines = [
        '; AGA_NATIVE_MIN_CPU: MC68020',
        '; AGA_NATIVE_PURPOSE: AUDIT_ONLY',
        '; Source-verified M19 P2d; AMOS AP20 FE31 stubs are link DATA.',
        '; All executable group sources are in INCLUDE files, not DC.W dumps.',
        '; DO NOT replace installed .Lib without an exact vasm comparison.',
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
    ]
    lines += [f'    dc.w (Entry_{i+1:03d}-Entry_{i:03d})/2'
              for i in range(len(parts))]
    lines += ['', 'C_Tk:']
    lines += _source_lines_for_data(raw_tokens, 0, len(raw_tokens))
    lines += ['', 'C_Lib:']
    for i, part in enumerate(parts):
        lines += ['', f'Entry_{i:03d}:']
        if i in files:
            lines.append('    include "' + files[i] + '"')
        else:
            # FE31 AP20 linker pseudo-words are NOT Motorola instructions.
            lines += _source_lines_for_data(part, 0, len(part))
    lines += ['',f'Entry_{len(parts):03d}:', 'C_Title:']
    lines += _source_lines_for_data(title,0,len(title))
    lines += ['C_End:', '    dc.w 0',
              '    dcb.b (-(*-HUNK_DATA))&3,0',
              'HUNK_DATA_END:', '    dc.l $000003F2', '']
    return "\n".join(lines)


def generate(target: Path, *, assembler: str|None=None, root: Path=ROOT):
    input_file = root/'dist/AMOSPro_AGA_LAST_GOOD.Lib'
    active_file = root/'dist/AMOSPro_AGA.Lib'
    data = input_file.read_bytes()
    previous_active_sha = digest(active_file.read_bytes())
    info = validate_source_build(data, root)
    _, parts, title, groups, refs = parse_native_groups(data)
    bobs_group, labels = p2d_symbolic_labels(parts, info)
    need(bobs_group in groups, "BOBS group's native V2 dispatcher missing")
    names = {}
    for index in groups:
        if index == bobs_group:
            names[index] = 'BOBS'
        else:
            # SOURCE-derived groups are recognized by their public label APIs.
            names[index] = 'UNIT%03d' % index
    sources = {}
    files = {}
    reports=[]
    for index in groups:
        name=names[index]
        source, report = native_unit_source(name,parts[index],refs[index])
        source = sanitize_illegal_pc_dest(source,report)
        source = ('; AGA_NATIVE_MIN_CPU: MC68020\n'
                  '; AGA_NATIVE_PURPOSE: AUDIT_ONLY\n' + source)
        if index==bobs_group:
            source,symbol_count = enrich_labels(source,name,labels)
            report['source_labels_provided_by_python_emitters'] = sum(map(len,labels.values()))
            report['source_labels_annotated'] = symbol_count
        fname='M19_P2D_%s_MC68020.s' % name
        files[index]=fname
        sources[fname]=source
        report['file']=fname
        report['ap20_entry']=index
        reports.append(report)
    mainfile='M19_P2D_AP20_SOURCE.s'
    sources[mainfile]=linked_source(data,parts,title,files)
    # No mainfile or assembly edits can overwrite src canonical or dist.
    destination=target.resolve()
    forbidden=(root/'dist').resolve()
    need(destination!=forbidden and forbidden not in destination.parents,
         'refusing to write source into dist/')
    destination.mkdir(parents=True,exist_ok=True)
    for filename,content in sources.items():
        (destination/filename).write_text(content,encoding='ascii',errors='backslashreplace',newline='\n')
    manifest={
        'release':'M19 P2d', 'cpu':'MC68020', 'origin':'verified Python emitters',
        'input_bytes':len(data), 'input_sha256':digest(data),
        'builder':'tools/build_m19_p2d_in_memory.py',
        'ap20_entries':len(parts), 'commands':info['commands'],
        'native_groups':reports, 'linked_file':mainfile,
        'no_output_in_dist':True, 'builder_exact_match':True,
        'verified_native_asm':False,
        'warning': 'Source mnemonic restoration: unclassified instructions remain DC.B. ' 
                   'Assembly may not be bit-exact until --vasm is successful.',
    }
    if assembler:
        for report in reports:
            result=_assemble(assembler,destination/report['file'],
                             destination/(Path(report['file']).stem+'.bin'))
            reference=parts[report['ap20_entry']]
            if result!=reference:
                at=next((i for i,(a,b) in enumerate(zip(reference,result))
                         if a!=b),min(len(reference),len(result)))
                raise ValueError(
                    'native unit %s mismatch at $%05X: original=%s vasm=%s '
                    'sizes=%d/%d' % (report['file'],at,
                    reference[at:at+12].hex(),result[at:at+12].hex(),
                    len(reference),len(result)))
            report['native_assembler_verified']=True
        result=_assemble(assembler,destination/mainfile,
                         destination/'M19_P2D_ASSEMBLED_TEST.Lib')
        need(result==data,'linked source is not binary-identical to P2d')
        manifest['verified_native_asm']=True
    manifest_file=destination/'M19_P2D_SOURCE_MANIFEST.json'
    manifest_file.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',
                             encoding='utf-8',newline='\n')
    need(digest(input_file.read_bytes())==P2D_SHA and
         digest(active_file.read_bytes())==previous_active_sha,
         'source export modified protected libraries')
    return manifest


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',default='src/generated/p2d_source')
    ap.add_argument('--vasm',default=None,
                    help='Full path to vasmm68k_mot.exe; verify all units and linked file')
    args=ap.parse_args(argv)
    target=Path(args.out)
    if not target.is_absolute():target=ROOT/target
    try:
        info=generate(target,assembler=args.vasm)
    except (AssertionError,ValueError,OSError,RuntimeError) as exc:
        print('[ERREUR] '+str(exc),file=sys.stderr)
        return 1
    for r in info['native_groups']:
        print('  %-8s %6d bytes: %6d vrai assembleur (%4.1f%%); %5d data/raw' % (
            Path(r['file']).stem, r['bytes'],r['mnemonic_bytes'],
            100*r['mnemonic_bytes']/r['bytes'],r['raw_dc_bytes']))
    print('[OK] Source MC68020:',target)
    print('[OK] Validation exact builder:',info['input_sha256'])
    print('[OK] vasm linked:',info['verified_native_asm'])
    return 0

if __name__=='__main__':
    raise SystemExit(main())