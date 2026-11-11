#!/usr/bin/env python3
"""M12 R27 0.9.3: no-new-token Safe-aware Blit Copy/Fill/Clear candidate.

Build *in memory* from the immutable R26 0.9.2 WinUAE-PASS archive.
The live library, R26/R25/R24 archives and LAST_GOOD are never written.
Segments 19/20 are guarded and Clear 21's internal BSR is recalculated.
This shifts later code: R23 dispatcher BSRs (17/18/31/32) plus its
screen-open state anchor (6) and dispatcher (33) MUST be relocated too.
All other AP20 segments and all 31 token definitions remain identical.
Gate A CPU must pass before any R27 binary is published.
"""
import argparse
import base64
from pathlib import Path
from struct import pack, unpack_from

from ap20_utils import split, rebuild, digest
from audit_ap20 import parse, inspect
from build_m6_blit_copy_r13 import emit_copy
from build_m6_blit_fill_r14 import emit_fill
from build_m6_blit_clear_r15 import emit_clear
from m12_blit_safe_r27_emit import emit_copy_safe, emit_fill_safe
from build_m8_idcmp_r23 import patch_bsr, KEY_STUB, STATE_ANCHOR
from m8_idcmp_r23_emit import emit_dispatcher, emit_mouse_reader, STATE_BYTES

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"dist/experimental/AMOSPro_AGA_M11_v0.9.2_TEXT_R26.Lib"
DEST=ROOT/"dist/AMOSPro_AGA.Lib"
ARCHIVE=ROOT/"dist/experimental/AMOSPro_AGA_M12_v0.9.3_SAFE_BLITTER_R27.Lib"
LAST_GOOD=ROOT/"dist/AMOSPro_AGA_LAST_GOOD.Lib"
BASE_SHA256="0fa162a9955ab317b25a0de43d6ddc07ed082dc4fac87188d744995bccb4a287"
LAST_GOOD_SHA256="e1d64b37ff85e786562af20e8959ccb2e8bd1ffa75edd67f4b69d6847d8593b3"
COPY_ENTRY=19
FILL_ENTRY=20
CLEAR_ENTRY=21
TEXT_ENTRY=36
GETP=b"GetP"
VERSION="R27 0.9.3"
RELOCATED=(6,17,18,19,20,21,31,32,33)

def _entry_starts(segments):
    """Absolute AP20 code-relative starts, including GetP delimiters."""
    offsets=[]
    cursor=0
    for segment in segments:
        offsets.append(cursor)
        cursor+=len(segment)
    return offsets

def _relocate_r23_dispatcher(original, updated):
    """Recalculate all code-relative BSR and state pointers crossing Copy/Fill.

    R23 keyboard and mouse dispatch routines use BSR.W calls into private
    entry 33, while Screen Open and the dispatcher/readers use a PC-relative
    state anchor in the dispatcher. Expanding earlier Blitters moves both.
    These are not new features: reemit EXACT original R23 code with updated
    relocations; assert all old bytes first, and preserve the final GetP.
    """
    starts_old=_entry_starts(original)
    starts_new=_entry_starts(updated)
    assert starts_new[33]>starts_old[33], "Blitter growth not reflected"
    _, labels=emit_dispatcher(1)
    assert labels["pump"]==0 and labels["key_next"]==538
    olddelta=starts_old[33]+labels["runtime_state"]-STATE_ANCHOR
    newdelta=starts_new[33]+labels["runtime_state"]-STATE_ANCHOR
    assert 0<olddelta<32767 and 0<newdelta<32767
    assert newdelta-olddelta==starts_new[33]-starts_old[33]

    original_dispatcher, old_labels=emit_dispatcher(olddelta)
    assert old_labels==labels and len(original_dispatcher)>=STATE_BYTES
    assert original[33]==original_dispatcher+GETP, (
        "Frozen R26 dispatcher changed; explicit R23 audit needed"
    )

    screen=bytearray(original[6])
    helper_pos=len(screen)-len(GETP)-18
    assert screen.endswith(GETP) and screen[helper_pos+4:helper_pos+6]==b"\x41\xea"
    assert unpack_from(">H",screen,helper_pos+6)[0]==olddelta
    screen[helper_pos+6:helper_pos+8]=pack(">H",newdelta)
    updated[6]=bytes(screen)

    for index in (17,18):
        assert original[index][KEY_STUB:KEY_STUB+2]==b"\x61\x00"
        oldtarget=starts_old[33]+labels["key_next"]
        assert patch_bsr(original[index],KEY_STUB+2,
                         starts_old[index],oldtarget)==original[index]
        updated[index]=patch_bsr(original[index],KEY_STUB+2,
                                 starts_new[index],
                                 starts_new[33]+labels["key_next"])

    for index,mode in ((31,"pressed"),(32,"released")):
        orig_reader,ext=emit_mouse_reader(mode,olddelta)
        assert original[index]==patch_bsr(orig_reader+GETP,ext,
              starts_old[index],starts_old[33]+labels["pump"]), (
              "Frozen R26 mouse reader changed",index)
        reader,new_ext=emit_mouse_reader(mode,newdelta)
        assert ext==new_ext
        updated[index]=patch_bsr(reader+GETP,new_ext,
                                 starts_new[index],
                                 starts_new[33]+labels["pump"])

    dispatcher,new_labels=emit_dispatcher(newdelta)
    assert new_labels==labels
    assert dispatcher[-STATE_BYTES:]==bytes(STATE_BYTES)
    updated[33]=dispatcher+GETP
    changed=tuple(i for i,(x,y) in enumerate(zip(original,updated)) if x!=y)
    assert changed==RELOCATED,("unexpected relocation footprint",changed)
    return dict(old_state_delta=olddelta,new_state_delta=newdelta,
                dispatcher_growth=starts_new[33]-starts_old[33],
                labels=labels)

def build():
    frozen=BASE.read_bytes()
    assert digest(frozen)==BASE_SHA256, "R26 WinUAE-PASS archive changed"
    assert digest(LAST_GOOD.read_bytes())==LAST_GOOD_SHA256, "LAST_GOOD changed"
    tokens,original,_=split(frozen)
    assert len(original)==37 and original[TEXT_ENTRY], "R26 AP20 layout changed"
    copy_orig,_=emit_copy()
    fill_orig,_=emit_fill()
    clear_orig,_=emit_clear(len(fill_orig))
    assert original[COPY_ENTRY]==copy_orig+GETP, "R26 Copy not R13 byte-exact"
    assert original[FILL_ENTRY]==fill_orig+GETP, "R26 Fill not R14 byte-exact"
    assert original[CLEAR_ENTRY]==clear_orig, "R26 Clear wrapper changed"
    copy_safe,labels_copy=emit_copy_safe()
    fill_safe,labels_fill=emit_fill_safe()
    clear_safe,details_clear=emit_clear(len(fill_safe))
    assert len(copy_safe)>len(copy_orig), "Copy guard missing"
    assert len(fill_safe)>len(fill_orig), "Fill guard missing"
    assert clear_safe!=clear_orig, "Clear BSR was not updated"
    updated=list(original)
    updated[COPY_ENTRY]=copy_safe+GETP
    updated[FILL_ENTRY]=fill_safe+GETP
    updated[CLEAR_ENTRY]=clear_safe
    links=_relocate_r23_dispatcher(original,updated)
    assert all(updated[i]==original[i] for i in range(37) if i not in RELOCATED), (
        "unrelated AP20 code mutated"
    )
    title=(b"AMOSPro AGA M12 Safe Blitter R27 0.9.3\0"
           b"$VER: AMOSPro_AGA 0.9.3\0")
    if len(title)&1: title+=b"\0"
    candidate=rebuild(frozen,updated,title)
    new_tokens,new_parts,_=split(candidate)
    assert new_tokens==tokens and new_parts==updated
    audit=inspect(parse(candidate))
    assert not audit["issues"],audit["issues"]
    named=[r for r in audit["tokens"] if r["name"].startswith("aga ")]
    assert len(named)==31 and len([r for r in named if r["name"]=="aga text"])==1
    assert len(updated)==37
    return candidate,{
        "version":VERSION,"size":len(candidate),"sha256":digest(candidate),
        "segments":len(updated),"named_commands":len(named),
        "changed_segments":RELOCATED,
        "r23_dispatcher_relocation":links,
        "copy_guard_labels":labels_copy,"fill_guard_labels":labels_fill,
        "clear_wrapper":details_clear,
        "Gate_A":"REQUIRES_CPU_CI","Gate_B_WinUAE":"NOT_TESTED",
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-base64",action="store_true")
    args=parser.parse_args()
    binary,info=build()
    assert binary==build()[0], "R27 not deterministic"
    print("M12 R27 in-memory candidate:",info,flush=True)
    if args.emit_base64:
        print("R27_BASE64_BEGIN",flush=True)
        print(base64.b64encode(binary).decode("ascii"),flush=True)
        print("R27_BASE64_END",flush=True)
