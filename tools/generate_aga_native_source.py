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

def analyze_entries(parsed):
    sections=parsed['section']
    base=parsed['code_start']
    # Shared private helpers can live after the first RTS of another AP20
    # entry. R23 calls IDCMP key_next inside entry 33 from entries 17/18.
    # Discover cross-entry seeds exclusively from decoded CALL targets.
    seeds={s['id']:set(KNOWN_SEEDS.get(sha(s['core']),())) for s in sections}
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
        data=input_path.read_bytes(); parsed=parse_lib(data)
        source,report=output(parsed)
        validate_structure(source,parsed)
        unresolved=unclassified_gaps(parsed)
        report['unclassified_regions']=unresolved
        if args.strict and unresolved:
            raise ExportError('Unclassified bytes: '+json.dumps(unresolved[:10])+                              '. A new instruction form/manual source audit is required.')
        m=re.search(r'\bR(\d+)\s+(\d+\.\d+\.\d+)',report['title'],re.I)
        version='R'+m.group(1) if m else sha(data)[:12]
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
            baseline_path,builder=find_baseline(root,data)
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
        print('NOTE: native assembly/rebuild not yet proven; do not replace any .Lib')
        if args.verify_vasm:
            binary=target/('AMOSPro_AGA_'+version+'_ASSEMBLED.Lib')
            cmd=[args.verify_vasm,'-Fbin','-m68020','-quiet','-o',str(binary),str(path)]
            try:r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
            except (OSError,subprocess.TimeoutExpired) as e:raise ExportError('Assembler launch failed: '+str(e)) from e
            if r.returncode:
                print(r.stdout,r.stderr,file=sys.stderr)
                raise ExportError('Native assembler reported an error; source not verified')
            if binary.read_bytes()!=data:
                raise ExportError('Native assembler output DOES NOT match source library; do not use')
            report['native_reassembly_verified']=True
            man.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            print('VERIFIED: native assembly is byte-for-byte identical to input .Lib')
        return 0
    except (OSError,ExportError,ValueError,struct.error) as exc:
        import traceback
        print('ERROR:',exc or type(exc).__name__,file=sys.stderr)
        traceback.print_exc()
        return 1
if __name__=='__main__':raise SystemExit(main())
