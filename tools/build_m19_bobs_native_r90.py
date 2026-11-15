#!/usr/bin/env python3
"""R90 native masked, persistent AGA Bobs - independent experimental build.

Extends the exact verified R89 source in memory, preserving historical
commands and four Compiler-V2 copied code groups. No active or LAST_GOOD
writes. No claim of WinUAE/Compiler passes from the host CPU tests.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
from struct import pack,pack_into,unpack_from
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tools'/'experiments')]
from build_m19_bobs_native_r89 import build as build_r89
from audit_ap20 import parse,inspect,token
from compiler_relocation import unpack_ap20,repack_ap20,RBSR,GETP
from ap20_v3_r82_split import interpreter_rbsr_displacements
from m19_bobs_mask_native_emit import emit_masks
from m19_bobs_object_native_emit import emit_objects,MAX_BOBS

GROUP_BOBS=94
PUBLIC_START=86
API=(
    ('make aga bob mask', 86, 1, 'I0,0'),
    ('no aga bob mask', 87, 1, 'I0'),
    ('aga bob', 88, 1, 'I0,0,0,0'),
    ('aga bob off', 89, 1, 'I0'),
    ('aga bob draw', 90, 1, 'I'),
    ('aga bob update', 91, 1, 'I'),
)
TITLE=(b'AMOSPro AGA R90 v0.13.35 M19 NATIVE MASKED PERSISTENT BOBS\0'
       b'$VER: AMOSPro_AGA 0.13.35 (R90) EXPERIMENT / GATE A ONLY\0')
TITLE+=bytes(len(TITLE)&1)
OUT_NAME='AMOSPro_AGA_R90_v0.13.35_M19_MASKED_BOBS_GATE_A_ONLY.Lib'


def patch_pc_ref(raw,labels,ref,group_offset,selected_word):
    """Rewrite one LEA (d16,PC) to R89's same-unit selected bank WORD."""
    p=labels[ref]+2
    if raw[p-2:p]!=b'\x49\xfa':
        raise ValueError(('wrong selected-bank LEA',ref))
    delta=selected_word-(group_offset+p)
    if not -32768 <= delta < 0:
        raise ValueError(('selected bank not reached in signed PC span',ref,delta))
    pack_into('>h',raw,p,delta)


def build():
    old,old_report=build_r89()
    old_tokens,parts,_=unpack_ap20(old)
    orig=inspect(parse(old))
    if orig['issues'] or len(orig['tokens'])!=81 or len(parts)!=90:
        raise ValueError('R89 ABI baseline changed')
    if old_report['sha256']!=sha256(old).hexdigest():
        raise ValueError('R89 integrity mismatch')
    masks,mask_labels=emit_masks()
    objects,obj_labels=emit_objects()
    maskcode=bytearray(masks)
    objcode=bytearray(objects)
    old_bobs=parts[88]
    sel=old_report['selected_word_offset']
    start_mask=len(old_bobs)
    start_object=start_mask+len(maskcode)
    for ref in ('mask_bank_reference','no_mask_bank_reference'):
        patch_pc_ref(maskcode,mask_labels,ref,start_mask,sel)
    patch_pc_ref(objcode,obj_labels,'set_bank_reference',start_object,sel)
    bobs=old_bobs+bytes(maskcode)+bytes(objcode)
    if len(bobs)>65534 or len(bobs)&1:
        raise ValueError('BOBS compiler unit size exceeds range')

    # Old public tokens 0..85 get two more group slots per new API.
    stub=[]
    for i,original in enumerate(parts[:PUBLIC_START]):
        if original in (b'',GETP):
            stub.append(original)
            continue
        if original[:2]!=RBSR or original[6:8]!=b'\x4e\x75' or len(original) not in (8,12):
            raise ValueError(('invalid original R89 stub',i))
        group,at=unpack_from('>HH',original,2)
        if group not in (86,87,88,89):
            raise ValueError(('invalid existing native group',group))
        stub.append(RBSR+pack('>HH',group+len(API),at)+original[6:])
    if stub[-1].endswith(GETP):
        raise ValueError('last R89 public stub already includes GetP')
    stub[-1]+=GETP
    for (name,idx,inst,sig),entry in zip(API,(
            start_mask+mask_labels['make_mask'],
            start_mask+mask_labels['no_mask'],
            start_object+obj_labels['bob_set'],
            start_object+obj_labels['bob_off'],
            start_object+obj_labels['bob_draw'],
            start_object+obj_labels['bob_draw'])):
        newstub=RBSR+pack('>HH',GROUP_BOBS,entry)+b'\x4e\x75'
        # Native AMOS GetP prefixes the NEXT entry, not the current entry.
        if idx in (86,87,88):
            newstub+=GETP
        stub.append(newstub)
    entries=stub+[parts[86],parts[87],bobs,parts[89]]
    if len(entries)!=96:
        raise ValueError('wrong AP20 entry count')
    tokens=old_tokens[:-6]+b''.join(token(*api) for api in API)+bytes(6)
    packed=repack_ap20(old,tokens,entries,TITLE)
    actual=inspect(parse(packed))
    if actual['issues'] or actual['tokens'][:-6]!=orig['tokens']:
        raise ValueError(('R90 AP20 ABI or prior commands changed',actual['issues']))
    for req,got in zip(API,actual['tokens'][-len(API):]):
        if (got['name'],got['instruction'],got['function'],got['signature'])!=req:
            raise ValueError(('new token changed',req,got))
    for i,n in ((86,2),(87,1),(88,4),(89,1)):
        if not any(p['index']==i and p['parameters']==n and p['getp']
                   for p in actual['parameter_checks']):
            raise ValueError(('GetP invalid',i))
    links=interpreter_rbsr_displacements(entries)
    max_link=max(map(abs,links.values()))
    if max_link>=32766:
        raise ValueError('Interpreter Rbsr signed word overflow')
    new_tokens,new_parts,new_title=unpack_ap20(packed)
    if (new_tokens,new_parts,new_title)!=(tokens,entries,TITLE):
        raise ValueError('repacked source mismatch')
    if any(new_parts[i]!=original for i,original in (
            (92,parts[86]),(93,parts[87]),(95,parts[89]))):
        raise ValueError('unrelated native code modified')
    return packed,{
        'version':'R90 v0.13.35 GATE A ONLY / UNINSTALLED',
        'sha256':sha256(packed).hexdigest(),'bytes':len(packed),
        'commands':len(actual['tokens'])-1,'entries':len(entries),
        'native_bobs_bytes':len(bobs),
        'max_interpreter_displacement':max_link,
        'selected_word_offset':sel,
        'mask_offset':start_mask,
        'no_mask_offset':start_mask+mask_labels['no_mask'],
        'bob_set_offset':start_object+obj_labels['bob_set'],
        'bob_off_offset':start_object+obj_labels['bob_off'],
        'bob_draw_offset':start_object+obj_labels['bob_draw'],
        'bob_table_offset':start_object+obj_labels['bob_table'],
        'masks_bytes':len(maskcode),'objects_bytes':len(objcode),
        'max_bobs':MAX_BOBS,
        'gate_a':'NOT TESTED','gate_b':'NOT TESTED','gate_c':'NOT TESTED',
    }


if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--output',type=Path)
    args=cli.parse_args()
    binary,report=build()
    if args.output:
        out=args.output.resolve()
        protected={
            ROOT/'dist/AMOSPro_AGA_LAST_GOOD.Lib',
            ROOT/'dist/AMOSPro_AGA.Lib',
            ROOT/'dist/experimental/AMOSPro_AGA_R88_v0.13.33_M19_P28_GATE_A_ONLY.Lib',
        }
        if any(out==p.resolve() for p in protected):
            raise SystemExit('refusing protected candidate overwrite')
        if out.name!=OUT_NAME:
            raise SystemExit('output name must be '+OUT_NAME)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_bytes(binary)
        print('EXPERIMENTAL R90 BINARY:',out)
    print('R90 Native persistent masked Bobs AP20:',report)
