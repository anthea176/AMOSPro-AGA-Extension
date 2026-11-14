#!/usr/bin/env python3
"""R84 AGAPIC v1/v2 extension candidate: build in memory from immutable R83.

Adds _VALUE=Aga Bank Image Info(Bank,Field) and
_OK=Aga Bank Image Capture(Bank,X,Y,W,H,TransparentIndex,Version).
The original Aga Image Capture(...,TransparentIndex) is unchanged.

Uses the existing three native AP20 groups. Moves group IDs 80..82 to
82..84 while preserving their original C2P/IFF/AGA bytecode, and appends
only new native code to the AGA group (no fourth group and no padding).
Never touches the R83 LAST_GOOD; no dist write is offered by this builder.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from struct import pack,unpack_from
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"/"experiments"))
from active_library import R83_SHA
from build_aga_r83_modular import build as build_r83
from compiler_relocation import unpack_ap20,repack_ap20,RBSR,GETP
from compiler_bridge_v2_probe import DISPATCH_V2
from ap20_v3_r82_split import interpreter_rbsr_displacements,assert_reaches_entry_on_mc68020
from audit_ap20 import inspect,parse,token
from m16_agapic_info_emit import emit_bank_image_info
from m16_agapic_capture_v2_emit import emit_capture_versioned

TITLE=(b"AMOSPro AGA R84 v0.13.29 AGAPIC v1/v2 - 3 NATIVE UNITS\0"
       b"$VER: AMOSPro_AGA 0.13.29 (R84) MC68020+ candidate\0")
TITLE+=bytes(len(TITLE)&1)
API=(
    ("aga bank image info",1,80,"00,0"),
    ("aga bank image capture",1,81,"00,0,0,0,0,0,0"),
)
GROUPS={80:82,81:83,82:84}
PREVIOUS=ROOT/"dist"/"AMOSPro_AGA_LAST_GOOD.Lib"
ACTIVE=ROOT/"dist"/"AMOSPro_AGA.Lib"

def build()->tuple[bytes,dict]:
    frozen=PREVIOUS.read_bytes()
    if len(frozen)!=64188 or sha256(frozen).hexdigest()!=R83_SHA:
        raise AssertionError("R83 promoted LAST_GOOD was modified")
    baseline,info=build_r83()
    if baseline!=frozen or info["sha256"]!=R83_SHA:
        raise AssertionError("Pinned deterministic R83 ancestor changed")
    original_tokens, old, _=unpack_ap20(frozen)
    if len(old)!=83 or tuple(len(v) for v in old[80:])!=(5558,2508,52974):
        raise AssertionError("Unexpected R83 three-unit layout")
    new_info,labels_info=emit_bank_image_info()
    new_capture,labels_capture=emit_capture_versioned()
    if not new_info or not new_capture or len(new_info)&1 or len(new_capture)&1:
        raise AssertionError("Unaligned native AGAPIC source")
    old_core=old[82]
    info_off=len(old_core)-len(DISPATCH_V2)+len(GETP)
    capture_off=info_off+len(new_info)+len(GETP)
    aga=old_core+GETP+new_info+GETP+new_capture
    if len(aga)>65534 or len(aga)&1:
        raise AssertionError("Compiler V2 native AGA unit exceeds 65534 bytes")
    stubs=[]
    for i,old_stub in enumerate(old[:80]):
        if old_stub in (b"",GETP):
            stubs.append(old_stub)
            continue
        if old_stub[:2]!=RBSR or len(old_stub) not in (8,12):
            raise AssertionError(("Malformed R83 RBSR",i))
        group,off=unpack_from(">HH",old_stub,2)
        if group not in GROUPS:
            raise AssertionError(("Unexpected original R83 group",i,group))
        candidate=old_stub[:2]+pack(">HH",GROUPS[group],off)+old_stub[6:]
        stubs.append(candidate)
    if not stubs[-1].endswith(b"\x4e\x75"):
        raise AssertionError("R83 final public entry is not last-token RTS")
    stubs[-1]+=GETP
    for off,has_next in ((info_off,True),(capture_off,False)):
        if off>=65536 or off&1:
            raise AssertionError("Invalid native AGA entry offset")
        stub=RBSR+pack(">HH",84,off)+bytes.fromhex("4e75")
        stubs.append(stub+(GETP if has_next else b""))
    segments=stubs+[old[80],old[81],aga]
    if len(segments)!=85:
        raise AssertionError("Expected 82 public entries and 3 native groups")
    tokens=original_tokens[:-6]+b"".join(token(*api) for api in API)+bytes(6)
    candidate=repack_ap20(frozen,tokens,segments,TITLE)
    rt,parts,title=unpack_ap20(candidate)
    if (rt,parts,title)!=(tokens,segments,TITLE):
        raise AssertionError("AP20 repack changed new native code")
    report=inspect(parse(candidate))
    if report["issues"]:
        raise AssertionError(("Broken R84 public ABI",report["issues"]))
    old_api=[t for t in inspect(parse(frozen))["tokens"] if t["name"].startswith("aga ")]
    new_api=[t for t in report["tokens"] if t["name"].startswith("aga ")]
    if len(old_api)!=74 or new_api[:74]!=old_api or len(new_api)!=76:
        raise AssertionError("R83 74 public commands changed")
    if new_api[-2:]:
        if [t["name"] for t in new_api[-2:]]!=[x[0] for x in API]:
            raise AssertionError("R84 new tokens do not match ABI")
    if not all(any(x["index"]==i and x["parameters"]==n and x["getp"]
                   for x in report["parameter_checks"]) for i,n in ((80,2),(81,7))):
        raise AssertionError("GetP ABI for R84 commands is incorrect")
    links=interpreter_rbsr_displacements(parts)
    if len(links)!=80:
        raise AssertionError("R84 must have exactly 80 live native stubs")
    if parts[82]!=old[80] or parts[83]!=old[81] or not parts[84].startswith(old[82]):
        raise AssertionError("R83 native C2P/IFF/AGA bytes not preserved")
    if ACTIVE.read_bytes()!=frozen:
        raise AssertionError("R84 is source-only pending native validation; active must remain R83")
    return candidate,dict(
        version="R84 v0.13.29",status="IN MEMORY ONLY: native Gate A pending",
        commands=76,ap20_entries=len(parts),sha256=sha256(candidate).hexdigest(),
        bytes=len(candidate),units=tuple(len(p) for p in parts[82:]),
        source_r83_sha256=R83_SHA,
        added_info_bytes=len(new_info),added_capture_bytes=len(new_capture),
        new_offsets=(info_off,capture_off),
        max_abs_loader_bsr_w=max(map(abs,links.values())),
        labels_info=labels_info,labels_capture=labels_capture,
    )

class R84Layout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image,cls.meta=build()
    def test_exact_r83_last_good(self):
        self.assertEqual(sha256(PREVIOUS.read_bytes()).hexdigest(),R83_SHA)
        self.assertEqual(ACTIVE.read_bytes(),PREVIOUS.read_bytes())
    def test_new_api_and_layout(self):
        self.assertEqual(self.meta["commands"],76)
        self.assertEqual(self.meta["ap20_entries"],85)
        self.assertLess(self.meta["units"][2],65534)
        self.assertEqual(self.meta["units"][:2],(5558,2508))
    def test_deterministic_rebuild(self):
        candidate,meta=build()
        self.assertEqual(candidate,self.image)
        self.assertEqual(meta,self.meta)
    def test_native_020_loader_reaches_both_new_entries(self):
        for entry in (80,81):
            with self.subTest(entry=entry):
                assert_reaches_entry_on_mc68020(self.image,entry)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate-a",action="store_true")
    args=parser.parse_args()
    if args.gate_a:
        result=unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(R84Layout))
        if not result.wasSuccessful():
            raise SystemExit("R84 structural/dispatch Gate A FAIL")
    image,meta=build()
    print("R84 AGAPIC NATIVE CANDIDATE IN MEMORY ONLY",
          {k:v for k,v in meta.items() if not k.startswith("labels_")})
    print("No dist/ write, no WinUAE B/C claim, R83 LAST_GOOD protected")

if __name__=="__main__":
    main()
