"""Gate A documentation: strict AP20 R19 + real ASM source verification.

Run: python -m unittest discover -s tests -p 'test_native_source.py' -v
No HUNK or archived .Lib is changed.
"""
from __future__ import annotations
from pathlib import Path
import json
import re
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import decoder68k as d
import generate_aga_native_source as x
import m68k_emit_reference as e

R19=ROOT/'reference'/'AMOSPro_AGA_R19.lib'
# The reference .Lib is provided by the user for local tests only, and is
# deliberately not shipped in this source package. On a checkout use dist/.
if not R19.is_file():R19=ROOT/'dist'/'AMOSPro_AGA.Lib'

REGEX_EA=re.compile(r'^(.+?)\(a([0-7])\)$')


def compile_r19_mouse(source,axis):
    """Assemble the ACTUAL .s statements through the builder's 68k emitter.

    Unlike checking disassembly comments, this proves that the explicitly
    written mnemonics/operands in AGA_MOUSE_R19_NATIVE.s encode to exactly
    the bytes contained in AP20 entry 28/29.
    """
    start='Aga_Mouse_'+axis.upper()+':'
    stop='Aga_Mouse_'+('Y' if axis=='x' else 'X')+':'
    lines=source.splitlines()
    begun=False; c=e.Code();ending=False;getp=False
    equ={}
    branches={'bra':0,'bne':6,'beq':7,'bmi':11,'bcc':4}
    for raw in lines:
        line=raw.split(';',1)[0].strip()
        if not line:continue
        m=re.match(r'^([A-Za-z_]\w*)\s+equ\s+(\$[0-9A-Fa-f]+|\d+)$',line,re.I)
        if m:equ[m[1].lower()]=int(m[2].replace('$','0x'),0);continue
        if line==start:begun=True;continue
        if not begun:continue
        if line==stop:break
        if line.endswith(':'):
            c.label((line[1:-1] if line.startswith('.') else line[:-1]).lower());continue
        if line=='dc.b "GetP"':getp=True;continue
        if ending:raise AssertionError('unexpected instruction after RTS: '+line)
        parts=line.split(None,1)
        op=parts[0].lower();a=parts[1].strip().lower() if len(parts)>1 else ''
        if op=='movem.l':
            if a.endswith(',-(sp)'):c.raw('48e7efee');continue
            if a.startswith('(sp)+,'):c.raw('4cdf77f7');continue
        if op=='rts':c.raw('4e75');ending=True;continue
        if op=='moveq' and a=='#0,d2':c.raw('7400');continue
        if op=='ext.l' and a in ('d1','d3'):
            c.raw('48c'+('1' if a=='d1' else '3'));continue
        if op in ('beq.w','bne.w','bmi.w','bcc.w','bra.w'):
            c.branch(branches[op.split('.')[0]],a.lstrip('.'));continue
        if op=='tst.l':
            assert a.startswith('d');c.tst(e.D(int(a[1])));continue
        if op in ('cmp.l','add.l'):
            a1,a2=a.split(',')
            assert a1.startswith('d') and a2.startswith('d')
            c.alu(op.split('.')[0],e.D(int(a1[1])),int(a2[1]));continue
        if op in ('movea.l','move.l','move.w'):
            # Source has no indexed EA / PCs in R19 M8 functions.
            left,right=a.split(',')
            def operand(p):
                if p.startswith('#'):return e.I(int(p[1:]),'l')
                if re.fullmatch(r'[da][0-7]',p):return (e.D if p[0]=='d' else e.A)(int(p[1]))
                m=REGEX_EA.match(p)
                assert m,('Unrecognized EA',p)
                field,areg=m.groups()
                field=equ.get(field, int(field) if field.lstrip('-').isdigit() else None)
                if field is None:raise AssertionError('Unknown field '+p)
                return e.M(int(areg),field)
            left=operand(left);right=operand(right)
            c.move(left,right,'w' if op.endswith('.w') else 'l');continue
        raise AssertionError('Unsupported R19 instruction '+line)
    if not begun:raise AssertionError('Missing R19 function '+start)
    if axis=='x' and not getp:raise AssertionError('Missing AP20 GetP delimiter')
    return c.out()


class Tests(unittest.TestCase):
    def setUp(self):
        self.src=(ROOT/'src'/'AGA_MOUSE_R19_NATIVE.s').read_text(encoding='ascii')
        data=R19.read_bytes() if R19.exists() else None
        self.lib=data if data is not None and x.sha(data)==x.R19_SHA else None

    def test_source_is_actual_mnemonics(self):
        self.assertIn('movem.l',self.src)
        self.assertIn('movea.l',self.src)
        self.assertIn('beq.w',self.src)
        self.assertNotIn('dc.w $48E7',self.src)

    def test_mouse_machine_code_matches_actual_source(self):
        p=x.parse_lib(self.lib) if self.lib is not None else None
        for name,index in [('x',28),('y',29)]:
            rebuilt=compile_r19_mouse(self.src,name)
            expected=(ROOT/'tests'/'fixtures'/('R19_MOUSE_'+name.upper()+'.bin')).read_bytes()
            self.assertEqual(len(rebuilt),108)
            self.assertEqual(rebuilt,expected)
            if p is not None:self.assertEqual(rebuilt,p['section'][index]['core'])

    def test_complete_r19_restoration_strict(self):
        if self.lib is None:self.skipTest('R19 .Lib fixture not mounted')
        p=x.parse_lib(self.lib)
        asm,meta=x.output(p)
        self.assertEqual(meta['entries'],30)
        self.assertGreater(meta['recognized_percent'],98)
        self.assertFalse(x.unclassified_gaps(p))
        self.assertIn('Aga_Mouse_X:',asm)
        self.assertIn('Aga_Mouse_Y:',asm)
        self.assertIn('movem.l',asm)
        self.assertIn('C_Tk:',asm)
        self.assertIn('C_Lib:',asm)
        self.assertIn('C_Title:',asm)
        self.assertIn('dc.b "GetP"',asm)
        self.assertNotIn('\x00',asm)

    def test_cli_writes_only_export_directory(self):
        if self.lib is None:self.skipTest('R19 .Lib fixture not mounted')
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)
            self.assertEqual(x.main(['--lib',str(R19),'--out',str(output),'--strict',
                                     '--baseline','none']),0)
            r=next(output.glob('*.json'))
            m=json.loads(r.read_text())
            self.assertEqual(m['sha256'],x.R19_SHA)
            self.assertEqual(m['unclassified_regions'],[])
            self.assertFalse(m['native_reassembly_verified'])
            self.assertEqual(R19.read_bytes(),self.lib)

    def test_dont_accept_tampered_hunk(self):
        if self.lib is None:self.skipTest('R19 .Lib fixture not mounted')
        broken=bytearray(self.lib);broken[-1]=0
        with self.assertRaises(x.ExportError):x.parse_lib(bytes(broken))

    def test_r23_idcmp_cross_entry_source_is_strict_and_complete(self):
        # Frozen R23 catches regressions even when active Lib advances.
        archive=ROOT/'dist'/'experimental'/'AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib'
        raw=archive.read_bytes()
        self.assertEqual(x.sha(raw),'899cb283d710fb4096bae4353f301a3ed40d2280b3ca90bf6ab48a323c8bfa23')
        parsed=x.parse_lib(raw)
        self.assertEqual(len(parsed['section']),34)
        self.assertEqual(len(parsed['section'][33]['core']),788)
        self.assertEqual(parsed['section'][33]['core'][-144:],bytes(144))
        block,labels,_,_=x.analyze_entries(parsed)

        # Key and Wait Key BSR to key_next after the first dispatcher RTS.
        helper=parsed['section'][33]['file_offset']+538
        self.assertIn(helper,block[33])
        self.assertEqual(block[33][helper].op,'bsr.w')
        self.assertIn(helper,labels)
        for idx,offset,mnemonic in (
            (6,322,'nop'),(17,506,'rts'),
            (18,108,'nop'),(18,546,'rts')
        ):
            absolute=parsed['section'][idx]['file_offset']+offset
            self.assertEqual(block[idx][absolute].op,mnemonic)
        for idx,marker in ((17,500),(18,540)):
            self.assertEqual(parsed['section'][idx]['core'][marker:marker+6],
                             bytes.fromhex('FE11F700008C'))
        self.assertFalse(x.unclassified_gaps(parsed))
        asm,meta=x.output(parsed)
        self.assertEqual(meta['entries'],34)
        self.assertIn('dcb.b 144,0',asm)
        self.assertIn('bsr.w',asm)

    def test_r23_strict_export_does_not_touch_lib(self):
        archive=ROOT/'dist'/'experimental'/'AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib'
        original=archive.read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'out'
            self.assertEqual(x.main(['--lib',str(archive),'--out',str(folder),
                                     '--strict','--baseline','none']),0)
            asm=folder/'AMOSPro_AGA_R23_NATIVE.s'
            meta=json.loads((folder/'AMOSPro_AGA_R23_NATIVE.json').read_text())
            self.assertTrue(asm.is_file())
            self.assertEqual(meta['sha256'],x.sha(original))
            self.assertEqual(meta['unclassified_regions'],[])
            self.assertFalse(meta['native_reassembly_verified'])
        self.assertEqual(archive.read_bytes(),original)

    def test_r23_unknown_helper_opcode_still_fails_strict(self):
        archive=ROOT/'dist'/'experimental'/'AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib'
        raw=bytearray(archive.read_bytes())
        parsed=x.parse_lib(raw)
        pos=parsed['section'][33]['file_offset']+538
        self.assertEqual(raw[pos:pos+2],bytes.fromhex('6100'))
        raw[pos:pos+2]=bytes.fromhex('ffff')
        mutated=bytes(raw)
        gaps=x.unclassified_gaps(x.parse_lib(mutated))
        self.assertTrue(any(region['entry']==33 and region['offset']==538
                            for region in gaps))
        with tempfile.TemporaryDirectory() as temp:
            input_file=Path(temp)/'mutated.Lib'
            folder=Path(temp)/'out'
            input_file.write_bytes(mutated)
            self.assertEqual(x.main(['--lib',str(input_file),'--out',str(folder),
                                     '--strict','--baseline','none']),1)
            self.assertFalse(folder.exists())
            self.assertEqual(input_file.read_bytes(),mutated)

    def test_r24_strict_export_preserves_frozen_r23_keyboard_exits(self):
        r23 = ROOT/'dist'/'experimental'/'AMOSPro_AGA_M8_v0.8.7_IDCMP_MOUSE_R23.Lib'
        r24 = ROOT/'dist'/'experimental'/'AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib'
        raw = r24.read_bytes()
        self.assertEqual(
            x.sha(raw),
            'cc8776e7303c529492fe6761544f4b2be1180063f3787fa840f44129766e3671')
        old, current = x.parse_lib(r23.read_bytes()), x.parse_lib(raw)
        self.assertEqual(len(old['section']),34)
        self.assertEqual(len(current['section']),35)
        for idx in (17,18,33):
            self.assertEqual(current['section'][idx]['core'],old['section'][idx]['core'])
        self.assertEqual(current['section'][33]['data'][-4:],b'GetP')
        self.assertFalse(x.unclassified_gaps(current))
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)/'out'
            self.assertEqual(x.main(['--lib',str(r24),'--out',str(out),
                                      '--strict','--baseline','none']),0)
            report = json.loads((out/'AMOSPro_AGA_R24_NATIVE.json').read_text())
            self.assertEqual(report['unclassified_regions'],[])
            self.assertEqual(report['entries'],35)
        self.assertEqual(r24.read_bytes(),raw)

    def test_r27_relocated_r23_dispatcher_strict_and_tamper_guard(self):
        # A larger R27 Blitter shifts entry33: R23 keyboard BSR.W calls
        # have to move too. The strict exporter must recognize the exact
        # relocation, while still rejecting unrelated keyboard edits.
        from build_m12_blit_safe_r27 import build
        candidate, details = build()
        parsed = x.parse_lib(candidate)
        self.assertEqual(len(parsed['section']), 37)
        changed = details['changed_segments']
        self.assertEqual(changed, (6, 17, 18, 19, 20, 21, 31, 32, 33))
        key_target = parsed['section'][33]['file_offset'] + 538
        for idx in (17,18):
            core = parsed['section'][idx]['core']
            self.assertEqual(core[0x30:0x32],bytes.fromhex('6100'))
            disp = __import__('struct').unpack_from('>h',core,0x32)[0]
            self.assertEqual(parsed['section'][idx]['file_offset']+0x32+disp,
                             key_target)
        self.assertFalse(x.unclassified_gaps(parsed))
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            binary=folder/'fixed-r27.Lib'
            binary.write_bytes(candidate)
            out=folder/'asm-export'
            self.assertEqual(x.main(['--lib',str(binary),'--out',str(out),
                                     '--strict','--baseline','none']),0)
            report=json.loads(next(out.glob('*.json')).read_text())
            self.assertEqual(report['unclassified_regions'],[])
            self.assertEqual(binary.read_bytes(),candidate)
        modified=bytearray(candidate)
        pos=parsed['section'][17]['file_offset']+0x32
        modified[pos+1]^=0x02   # target misses key_next; NOT an audited relocation
        self.assertTrue(any(p['entry']==17 or p['entry']==33
                            for p in x.unclassified_gaps(
                                x.parse_lib(bytes(modified)))))
        modified=bytearray(candidate)
        pos=parsed['section'][17]['file_offset']+500
        modified[pos]^=0x01  # R23 keyboard exit marker tampered
        self.assertTrue(any(p['entry']==17 for p in x.unclassified_gaps(
            x.parse_lib(bytes(modified)))))

    def test_r28_palette_exact_core_strict_and_tamper_guard(self):
        # R28 Palette Load inherits the M5 DOS reader and two valid 68000
        # MOVE.L #0,D0 error-return instructions after unconditional branches.
        # This exact hash alone authorizes entrypoint seeds for strict ASM export.
        from build_m13_palette_r28 import build
        candidate,_=build()
        parsed=x.parse_lib(candidate)
        self.assertEqual(len(parsed['section']),40)
        load=parsed['section'][37]
        core=load['core']
        self.assertEqual(x.sha(core),
                         '567c652d07ff770b0f72690f766c401dca9595d9830834f8bb08583b6445d620')
        for pos in (1170,1298):
            self.assertEqual(core[pos:pos+6],bytes.fromhex('203c00000000'))
        self.assertFalse(x.unclassified_gaps(parsed))
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            lib=folder/'R28-test.Lib'
            lib.write_bytes(candidate)
            export=folder/'asm'
            self.assertEqual(x.main(['--lib',str(lib),'--out',str(export),
                                     '--strict','--baseline','none']),0)
            report=json.loads(next(export.glob('*.json')).read_text())
            self.assertEqual(report['unclassified_regions'],[])
            self.assertEqual(lib.read_bytes(),candidate)
        mutated=bytearray(candidate)
        at=load['file_offset']+1170+4
        mutated[at]=0x01  # change MOVE.L immediate while preserving HUNK layout
        rejected=x.unclassified_gaps(x.parse_lib(bytes(mutated)))
        self.assertTrue(any(row['entry']==37 for row in rejected),
                        'Non-exact R28 reader must not inherit vetted code seeds')

    def test_r24_altered_keyboard_core_does_not_inherit_r23_rts_seed(self):
        path=ROOT/'dist'/'experimental'/'AMOSPro_AGA_M9_v0.9.0_HOTSPOT_HIT_R24.Lib'
        raw=bytearray(path.read_bytes())
        parsed=x.parse_lib(raw)
        pos=parsed['section'][17]['file_offset']+500
        self.assertEqual(raw[pos:pos+8],bytes.fromhex('FE11F700008C4E75'))
        raw[pos]=0xFF
        gaps=x.unclassified_gaps(x.parse_lib(bytes(raw)))
        self.assertTrue(any(row['entry']==17 for row in gaps))

    def test_future_release_adds_entry_automatically(self):
        if self.lib is None:self.skipTest('R19 .Lib fixture not mounted')
        p=x.parse_lib(self.lib)
        # M8 R20 toy fixture: AP20 entry 30 = RTS, no source hardcoding.
        token_name=b'aga smoke'
        def token(name,cmd,fn,sig):
            b=name.encode('ascii');o=__import__('struct').pack('>HH',cmd,fn)
            o+=b[:-1]+bytes([b[-1]|128])+sig.encode('ascii')+b'\xff'
            return o+b'\0'*(len(o)%2)
        tk=p['token_data'][:-6]+token(token_name.decode(),1,len(p['section']),'0')+b'\0'*6
        parts=[a['data'] for a in p['section']]+[b'\x4e\x75']
        title=b'AMOSPro AGA M8 R20 0.8.4 source test\0'
        if len(title)&1:title+=b'\0'
        from struct import pack
        payload=pack('>4I',2*len(parts),len(tk),sum(map(len,parts)),len(title))
        payload+=b'\0\0AP20'+b''.join(pack('>H',len(b)//2) for b in parts)+tk+b''.join(parts)+title+b'\0\0'
        payload+=bytes(-len(payload)%4)
        words=len(payload)//4
        raw=pack('>8I',0x3f3,0,1,0,0,words,0x3e9,words)+payload+pack('>I',0x3f2)
        newer=x.parse_lib(raw)
        asm,meta=x.output(newer)
        self.assertEqual(meta['entries'],31)
        self.assertIn('Entry_30:',asm)
        self.assertIn('aga smoke',asm)
        self.assertFalse(x.unclassified_gaps(newer))

if __name__=='__main__':unittest.main()
