#!/usr/bin/env python3
"""Verify promoted R82 V2, historical R81/R73 builders and frozen R46 C1.

Future revisions MUST unwrap the V2 LAST_GOOD via
compiler_bridge_v2_probe.unwrap_native_parts_v2(), change only audited
native parts and rewrap with wrap_native_ap20_v2(). The old V1 wrapper is
historical and must not be silently applied to the current R59 image.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from ap20_utils import digest
from audit_ap20 import inspect, parse
from build_aga_compiler_bridge_r46 import build as bridge_r46, SOURCE, CANDIDATE, TITLE, CANDIDATE_SHA
from compiler_relocation import unwrap_native_parts, unpack_ap20, is_compiler_wrapped, native_from_promoted
from active_library import verify_active

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "dist/AMOSPro_AGA.Lib"
LAST_GOOD = ROOT / "dist/AMOSPro_AGA_LAST_GOOD.Lib"
C1_ARCHIVE = ROOT / "dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
HISTORICAL_RAW = SOURCE


def build() -> tuple[bytes, dict]:
    raw = HISTORICAL_RAW.read_bytes()
    promoted = bridge_r46(raw)
    assert promoted == CANDIDATE.read_bytes(), "C1 evidence archive changed"
    assert is_compiler_wrapped(promoted), "unwrapped R46 may not be promoted"
    raw_tokens, raw_parts, raw_title = unpack_ap20(raw)
    token, segments, title = unpack_ap20(promoted)
    assert token == raw_tokens and len(raw_parts) == 56 and len(segments) == 57
    assert title == TITLE and segments[-1][32:] == b"".join(raw_parts)
    assert unwrap_native_parts(promoted) == (raw_tokens, raw_parts)
    assert native_from_promoted(promoted, raw_title) == raw
    report = inspect(parse(promoted))
    assert not report["issues"] and len([t for t in report["tokens"] if t["name"].startswith("aga ")]) == 50
    assert len(promoted) == 29964 and digest(promoted) == CANDIDATE_SHA
    return promoted, dict(version="R46 v0.12.1-C1", segments=57,
                          commands=50, bytes=len(promoted), sha256=digest(promoted),
                          gates="A/B + Gate C integrated WinUAE PASS; D NOT TESTED")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", action="store_true",
                    help="verify reproducible historical C1 and current pinned Compiler-safe release")
    args = ap.parse_args()
    data, details = build()
    current,_,active=verify_active(ROOT)
    if active.startswith("M19 S2f"):
        from active_library import verify_s2f
        verify_s2f(current,LAST_GOOD.read_bytes())
        print("CURRENT 0.15.0-alpha.3 S2f: exact clipping candidate; 105 commands / 219 AP20; Gate A PASS, B/C/D pending; L2b protected")
    elif active.startswith("M19 S2e"):
        from active_library import verify_s2e
        verify_s2e(current,LAST_GOOD.read_bytes())
        print("CURRENT 0.15.0-alpha.2 S2e: exact signed hotspot candidate; 105 commands / 219 AP20; Gate A PASS, B/C/D pending; L2b protected")
    elif active.startswith("M19 S2d-P3e"):
        from active_library import verify_s2d
        verify_s2d(current,LAST_GOOD.read_bytes())
        print("CURRENT 0.15.0-alpha.1 S2d-P3e: exact 16/32/64 Sprite candidate; 105 commands / 219 AP20; Gate A and Runtime B PASS; Compiler C deferred, D untested; L2b protected")
    elif active.startswith("M19 S2c-P1e"):
        from active_library import verify_s2c
        verify_s2c(current,LAST_GOOD.read_bytes())
        print("CURRENT S2c-P1e: exact ViewPort chain correction Gate A candidate; 105 commands / 219 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S2c-P1d"):
        from active_library import verify_s2c
        verify_s2c(current,LAST_GOOD.read_bytes())
        print("CURRENT S2c-P1d: exact diagnostic Sprite Gate A candidate; 105 commands / 219 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S2c-P1c"):
        from active_library import verify_s2c
        verify_s2c(current,LAST_GOOD.read_bytes())
        print("CURRENT S2c-P1c: exact mixed Sprite Gate A candidate; 105 commands / 219 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S2r-P1"):
        from active_library import verify_s2r
        verify_s2r(current,LAST_GOOD.read_bytes())
        print("CURRENT S2r-P1: exact AP20 repartition Gate A candidate; 105 commands / 219 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S2b-P1"):
        from active_library import verify_s2b
        verify_s2b(current,LAST_GOOD.read_bytes())
        print("CURRENT S2b-P1: exact multi-Sprite Gate A candidate; 105 commands / 214 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S2a-P1"):
        from active_library import verify_s2a
        verify_s2a(current,LAST_GOOD.read_bytes())
        print("CURRENT S2a-P1: exact frame-change Gate A candidate; 105 commands / 214 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S1-P2m"):
        from active_library import verify_s1p2m
        verify_s1p2m(current,LAST_GOOD.read_bytes())
        print("CURRENT S1-P2m: exact functional Gate A candidate; 105 commands / 214 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S1-P2l-c"):
        from active_library import verify_s1p2lc
        verify_s1p2lc(current,LAST_GOOD.read_bytes())
        print("CURRENT S1-P2l-c: exact diagnostic Gate A candidate; 105 commands / 214 AP20; B/C/D pending; DMA retained; L2b protected")
    elif active.startswith("M19 S1-P2l-b"):
        from active_library import verify_s1p2lb
        verify_s1p2lb(current,LAST_GOOD.read_bytes())
        print("CURRENT S1-P2l-b: exact diagnostic Gate A candidate; 105 commands / 214 AP20; B/C/D pending; DMA retained; L2b protected")
    elif active.startswith("M19 S1-P2k"):
        from active_library import verify_s1p2k
        verify_s1p2k(current, LAST_GOOD.read_bytes())
        print("CURRENT S1-P2k r4: exact transaction Gate A candidate, 105 commands / 214 AP20; B/C/D pending; DMA retained; L2b protected")
    elif active.startswith("M19 S1-P2j"):
        from active_library import verify_s1p2j
        verify_s1p2j(current, LAST_GOOD.read_bytes())
        print("CURRENT S1-P2j: exact diagnostic Gate A candidate, 105 commands / 214 AP20; B/C/D pending; DMA retained; L2b protected")
    elif active.startswith("M19 S1-P2i"):
        from active_library import verify_s1p2i
        verify_s1p2i(current, LAST_GOOD.read_bytes())
        print("CURRENT S1-P2i: exact integrated Gate A candidate, 105 commands / 214 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S1-P1i"):
        from active_library import verify_s1p1i
        verify_s1p1i(current, LAST_GOOD.read_bytes())
        print("CURRENT S1-P1i: exact full Gate A candidate, 102 commands / 208 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S1-P1h"):
        from active_library import verify_s1p1h
        verify_s1p1h(current, LAST_GOOD.read_bytes())
        print("CURRENT S1-P1h: exact native Gate A candidate, 102 commands / 208 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S1-P1g"):
        from active_library import verify_s1p1g
        verify_s1p1g(current, LAST_GOOD.read_bytes())
        print("CURRENT S1-P1g: exact AP20 token correction, 102 commands / 208 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 S1-P1f"):
        from active_library import verify_s1p1f
        verify_s1p1f(current, LAST_GOOD.read_bytes())
        print("CURRENT S1-P1f: exact Gate A candidate, 102 commands / 208 AP20; B/C/D pending; L2b protected")
    elif active.startswith("M19 P2d-L2b"):
        from active_library import P2DL2B_SHA, verify_p2d_l2b, frozen_p2d
        assert sha256(current).hexdigest() == P2DL2B_SHA
        assert current == LAST_GOOD.read_bytes()
        verify_p2d_l2b(current, frozen_p2d(LAST_GOOD.read_bytes()))
        print("CURRENT M19 P2d-L2b: exact promoted LAST_GOOD, 100 commands / 203 AP20; see qualification for Runtime evidence")
    elif active.startswith("M19 P2d-L2"):
        from active_library import verify_p2d_l2
        verify_p2d_l2(current, LAST_GOOD.read_bytes())
        print("CURRENT M19 P2d-L2: exact Gate A candidate, 100 commands / 203 AP20; B/C/D pending")
    elif active.startswith("M19 S1-P1e"):
        from active_library import S1P1E_SHA,P2D_SHA
        assert sha256(current).hexdigest()==S1P1E_SHA and len(current)==142000
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()==P2D_SHA
        print("CURRENT M19 S1-P1e AGSP: 102 commands / 208 AP20 entries, Gate A PASS; WinUAE B / Compiler C PENDING; P2d LAST_GOOD protected")
    elif active.startswith("M19 P0 Bank Free"):
        from active_library import P0_FREE_SHA
        from build_m19_b8_s1_bank_free_in_memory import build_bank_free
        candidate,meta=build_bank_free()
        assert current==candidate and meta['sha256']==P0_FREE_SHA
        assert len(candidate)==117896 and meta['public_commands']==89
        assert meta['ap20_entries']==185 and meta['pc16_max']==31092
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()==P0_FREE_SHA and LAST_GOOD.read_bytes()==current
        print('CURRENT M19 P0 BANK FREE PROMOTED: native Gate A 225 checks PASS; WinUAE Runtime B functional PASS; AMOS Compiler C NOT TESTED',meta)
    elif active.startswith("M19 B8 S1"):
        from active_library import B8S1_SHA,R84_SHA
        from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
        candidate,meta=build_b8_safe_retry()
        assert current==candidate and meta["sha256"]==B8S1_SHA
        assert len(candidate)==116104 and meta["public_commands"]==88
        assert meta["ap20_entries"]==184 and meta["pc16_max"]==29962
        assert meta["new_native_bytes"]==360 and meta["wait_tof_max"]==3
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()==R84_SHA
        print("CURRENT M19 B8 S1 BOUNDED SAFE GATE A PASS; WINUAE B/COMPILER C NOT TESTED; R84 LAST_GOOD PROTECTED",meta)
    elif active.startswith("M19 B8 Clear/Update"):
        from active_library import B8_SHA,R84_SHA
        from build_m19_b8_first_update_in_memory import build_b8_first_update
        candidate,meta=build_b8_first_update()
        assert current==candidate and meta["sha256"]==B8_SHA
        assert len(candidate)==115744 and meta["public_commands"]==88
        assert meta["ap20_entries"]==184 and meta["pc16_max"]==29962
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()==R84_SHA
        print("CURRENT M19 B8 NATIVE GATE A PASS; WINUAE B/COMPILER C NOT TESTED; R84 LAST_GOOD PROTECTED",meta)
    elif active.startswith("R88 v0.13.33"):
        from active_library import R84_SHA,R88_SHA
        from build_m19_p28_r88_in_memory import build as build_r88
        candidate,meta=build_r88()
        assert current==candidate and meta["sha256"]==R88_SHA
        assert len(current)==75040 and meta["commands"]==78 and meta["entries"]==88
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()==R84_SHA
        print("CURRENT R88 P2.8 UNPROMOTED CANDIDATE: native Gate A PASS; WinUAE B/C NOT TESTED; R84 LAST_GOOD protected")
    elif active.startswith("R85 v0.13.30"):
        from active_library import R84_SHA, R85_SHA
        from build_m19_p22_fourth_unit_probe import build as build_r85
        candidate, meta=build_r85()
        assert current==candidate and meta["sha256"]==R85_SHA
        assert meta["size"]==67988 and meta["commands"]==77 and meta["ap20_entries"]==87
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()==R84_SHA
        assert current!=LAST_GOOD.read_bytes()
        print("CURRENT M19 P2.2 R85 EXPERIMENTAL FOURTH AP20 BOBS UNIT: native Gate A PASS, Runtime B / Compiler C pending, LAST_GOOD R84 protected",meta)
    elif active.startswith("R84 v0.13.29"):
        from build_aga_r84_agapic import build as build_r84
        candidate,meta=build_r84()
        assert candidate==current and meta["sha256"]=="46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d"
        assert meta["bytes"]==67904 and meta["commands"]==76 and meta["ap20_entries"]==85
        assert current==LAST_GOOD.read_bytes() and sha256(LAST_GOOD.read_bytes()).hexdigest()=="46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d"
        print("CURRENT R84 PROMOTED LAST_GOOD: native A and AMOS Compiler C PASS (bank included); corrected Runtime B not separately evidenced",meta)
    elif active.startswith("R83 v0.13.28"):
        from build_aga_r83_modular import build as build_r83
        candidate,meta=build_r83()
        assert candidate==current and meta["sha256"]=="01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb"
        assert meta["size"]==64188 and meta["commands"]==74 and meta["ap20_entries"]==83
        assert current==LAST_GOOD.read_bytes() and sha256(LAST_GOOD.read_bytes()).hexdigest()=="01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb"
        print("CURRENT R83 THREE-MODULE PROMOTED LAST_GOOD, native A and WinUAE Runtime B / Compiler C PASS; physical D untested",meta)
    elif active.startswith("R82 0.13.27"):
        from build_agapic_v2_r82_full_preview import build as build_r82
        candidate,meta=build_r82()
        assert candidate==current==LAST_GOOD.read_bytes() and meta["sha256"]=="b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36"
        assert meta["size"]==64112 and meta["commands"]==74
        assert meta["ap20_entries"]==81 and meta["compiler_margin"]==4562
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()=="b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36"
        print("CURRENT R82 PROMOTED LAST_GOOD: native A PASS; Runtime B PASS; Compiler C PASS; physical D NOT TESTED",meta)
    elif active.startswith("R81 0.13.26"):
        from build_c2p_r81_opt020 import build as build_r81
        candidate,meta=build_r81()
        assert candidate==current, "Historical R81 must equal exact SHA-pinned builder"
        assert meta["sha256"]=="9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4" and meta["size"]==59972
        assert meta["commands"]==70 and meta["ap20_entries"]==77
        from build_opt020_p3_r73 import build as build_r73
        assert sha256(build_r73()[0]).hexdigest()=="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407", "Historical R73 builder drift"
        print("CURRENT R81 PROMOTED LAST_GOOD: native Gate A / Runtime B / Compiler C PASS; Gate D physical untested",meta)
    elif active.startswith("R80 0.13.25"):
        from build_c2p_r80_iff_chunky import build as build_r80
        candidate,meta=build_r80()
        assert candidate==current and meta["sha256"]=="24e05f7403c07d23db1ff65c9499a032b413fd7d0d140ce8a55e2fd6778b18c6"
        assert meta["size"]==59708 and meta["commands"]==70 and meta["ap20_entries"]==77
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()=="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        print("CURRENT R80 IFF TO CHUNKY; Gate A CPU PASS (11 frames); WinUAE B/Compiler C PENDING",meta)
    elif active.startswith("R79 0.13.24"):
        from build_c2p_r79_zoom import build as build_r79
        candidate,meta=build_r79()
        assert candidate==current and meta["sha256"]=="ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab"
        assert meta["commands"]==69 and meta["ap20_entries"]==76
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()=="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        print("CURRENT R79 C2P ZOOM; native CPU pixel Gate A PASS (62); WinUAE B/Compiler C NOT TESTED",meta)
    elif active.startswith("R78 0.13.23"):
        from build_c2p_r78_blit import build as build_r78
        candidate,meta=build_r78()
        assert candidate==current and meta["sha256"]=="9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c"
        assert meta["commands"]==68 and meta["ap20_entries"]==75
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()=="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        print("CURRENT R78 C2P BLIT; native Gate A 46 PASS; WinUAE Gate B/Compiler Gate C NOT TESTED",meta)
    elif active.startswith("R77 0.13.22"):
        from build_c2p_r77_close import build as build_r77
        candidate,meta=build_r77()
        assert candidate==current and meta["sha256"]=="81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11"
        assert meta["commands"]==67 and meta["ap20_entries"]==74
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()=="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        print("CURRENT R77 C2P CLOSE; native Gate A PASS; WinUAE B/Compiler C NOT TESTED",meta)
    elif active.startswith("R76 0.13.21"):
        from build_c2p_r76_rpg_fix import build as build_r76
        candidate,meta=build_r76()
        assert candidate==current and meta["sha256"]=="9e0a77f3e69c06cfcc96b00b8dc1f23122d559f617beac8762310c5f4bb53897"
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()=="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        print("CURRENT R76 RPG INPUT-STATE FIX; Gate A 24 PASS; WinUAE B/C NOT TESTED",meta)
    elif active.startswith("R75 0.13.20"):
        from build_c2p_r75_convert import build as build_r75
        candidate,meta=build_r75()
        assert candidate==current and meta["sha256"]=="c5a5a0e45e5b07012247937bf1af0371836f0d119577c102d62a28f4ca1ad3af"
        assert sha256(LAST_GOOD.read_bytes()).hexdigest()=="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        print("CURRENT R75 C2P OPEN+CONVERT CANDIDATE; R73 LAST_GOOD intact; WinUAE B/C NOT TESTED",meta)
    elif active.startswith("R74 0.13.19"):
        from build_c2p_r74_open import build as build_r74
        candidate, meta = build_r74()
        assert candidate == current and meta["sha256"] == "887f29c0350f47af9d93d1ebf64fc405c8542e897ff0e7d9d95eda6f814c2a23"
        assert sha256(LAST_GOOD.read_bytes()).hexdigest() == "c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        print("CURRENT R74 C2P OPEN CANDIDATE; R73 LAST_GOOD intact; WinUAE B/C NOT TESTED", meta)
    elif active.startswith("R73 0.13.18"):
        from build_opt020_p3_r73 import build as build_r73
        candidate, meta = build_r73()
        assert candidate == current == LAST_GOOD.read_bytes() and meta["sha256"] == "c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"
        print("CURRENT R73 PROMOTED LAST_GOOD: OPT020 P1e/P2/P3 Gates A/B/C PASS; D physical untested", meta)
    elif active.startswith("R72 0.13.17"):
        from build_opt020_p2_r72 import build as build_r72
        candidate, meta = build_r72()
        assert candidate == current and meta["sha256"] == "fdb98db259618fbdc3802843e2d6e836cb64acf2d68dc50bbe1133d46d36e67b"
        print("CURRENT R72 OPT020/P2 late D3 fix: native Gate A PASS; WinUAE B/Compiler C PENDING", meta)
    elif active.startswith("R71 0.13.16"):
        from build_opt020_p2_r71 import R71_SHA, build as build_r71
        candidate, meta = build_r71()
        assert candidate == current and meta["sha256"] == R71_SHA
        print("CURRENT R71 OPT020/P2 link repair Gate A; WinUAE B and Compiler C pending", meta)
    elif active.startswith("R70 0.13.15"):
        from build_opt020_p2_r70 import build as build_r70
        candidate, meta = build_r70()
        assert candidate == current and meta["sha256"] == "fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"
        assert sha256(LAST_GOOD.read_bytes()).hexdigest() == "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
        print("CURRENT R70 OPT020/P2 Gate A; WinUAE B and Compiler C pending", meta)
    elif active.startswith("R69 0.13.14"):
        from build_opt020_p1e_r69 import build as build_r69
        candidate,meta=build_r69()
        assert candidate == current and meta["sha256"] == "9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"
        assert sha256(LAST_GOOD.read_bytes()).hexdigest() == "ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
        print("CURRENT R69 OPT020/P1e tested: WinUAE Gate B and interpreted/compiled Region benchmark PASS; P2/R70 Gate B failed",meta)
    elif active.startswith("R68 0.13.13"):
        from build_m18_r68_cblock import build as build_r68
        candidate,meta=build_r68()
        assert candidate==current and meta["sha256"]=="ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"
        assert candidate == LAST_GOOD.read_bytes(), "Promoted R68 differs from LAST_GOOD"
        print("CURRENT R68 PROMOTED LAST_GOOD; Gates A/B/C PASS, D physical untested",meta)
    elif active.startswith("R67 0.13.12"):
        from build_m18_r67_ficon_capture import build as build_r67
        candidate,meta=build_r67()
        assert candidate==current,"R67 active differs from exact native builder"
        print("CURRENT R67 FICON8 SCREEN CAPTURE Gate A 240 PASS; WinUAE interpreted B pending",meta)
    elif active.startswith("R66 0.13.11"):
        from build_m18_r66_fichip_dynamic import build as build_r66
        candidate,meta=build_r66()
        assert candidate==current,"R66 current differs from deterministic native builder"
        print("CURRENT R66 CHIP CACHE CREATE+STAGE GATE A 122 PASS; WinUAE B pending",meta)
    elif active.startswith("R65 0.13.10"):
        from build_m18_r65_ficon_bank_put import build as build_r65
        candidate,meta=build_r65()
        assert candidate==current,"R65 must match exact deterministic source builder"
        print("CURRENT R65 FICON8 BANK PUT GATE A CPU PASS, B pending, C end M18",meta)
    elif active.startswith("R64 0.13.9"):
        from build_m18_r64_ficon_bank_create import build as build_r64
        candidate,meta=build_r64()
        assert candidate==current,"R64 current differs from deterministic source"
        print("CURRENT R64 FICON8 BANK CREATE A/B PASS (interpreted+visual); Compiler C end M18",meta)
    elif active.startswith("R63 0.13.8"):
        from build_m18_r63_chip_blit import build as build_r63
        candidate,meta=build_r63()
        assert candidate==current, "R63 candidate differs from exact deterministic source"
        print("CURRENT R63 CHIP BLIT PROMOTED LAST_GOOD A/B PASS (pixels pending, C end M18)",meta)
    elif active.startswith("R62 0.13.7"):
        from build_m18_r62_chip_blit import build as build_r62
        candidate,meta=build_r62()
        assert candidate==current, "R62 does not match pinned source builder"
        print("CURRENT R62 CHIP BLIT GATE A BUILDER PASS, B/C pending",meta)
    elif active.startswith("R61 0.13.6"):
        from build_m18_r61_ficon import build as build_r61
        candidate,meta=build_r61()
        assert candidate==current, "R61 candidate differs from deterministic builder"
        print("CURRENT M18 R61 FICON V2 GATE A BUILDER PASS (B/C pending)",
              {k:v for k,v in meta.items() if k!="labels"})
    elif active.startswith(("R60 0.13.5", "promoted R60 v0.13.5")):
        from build_m18_r60_image_region import build as build_r60
        candidate,meta = build_r60()
        assert candidate==current, "R60 candidate must be byte-exact to deterministic builder"
        print("CURRENT M18 R60 AGAPIC REGION V2 GATE A BUILDER PASS",
              {k:v for k,v in meta.items() if k!="labels"})
    elif active.startswith(("R59 0.13.4", "promoted R59 v0.13.4")):
        from build_m17_r59_compact_v2 import build as build_r59
        candidate,meta=build_r59()
        assert candidate==current, "R59 candidate not byte-exact to deterministic builder"
        print("CURRENT M17 R59 COMPACT V2 BUILDER PASS",meta)
    elif active.startswith("R58 0.13.3"):
        from build_m17_r58_compiler_bridge import build as build_r58
        candidate,meta=build_r58()
        assert candidate==current, "R58 candidate not byte-exact to deterministic builder"
        print("CURRENT M17 R58 V2 40K BUILDER PASS",meta)
    elif active.startswith(("R57 v0.13.2", "promoted R57 v0.13.2")):
        from build_m17_r57_rastport import build as r57_build
        candidate,meta=r57_build()
        assert candidate==current,"Current R57 differs from deterministic builder"
        print("CURRENT M17 R57 IN-PLACE RASTPORT BUILDER PASS",
              {k:v for k,v in meta.items() if k!="labels"})
    elif active.startswith("R56 v0.13.1"):
        from build_m17_r56_rastport import build as r56_build
        candidate,meta = r56_build()
        assert candidate == current, "Current R56 differs from deterministic Compiler-safe build"
        print("CURRENT M17 R56 RASTPORT BUILDER PASS",
              {k:v for k,v in meta.items() if k!="labels"})
    elif active.startswith("R55 v0.13.0"):
        from build_m17_blit_group_r55 import build as r55_build
        candidate,meta = r55_build()
        assert candidate==current, "R55 current dist library differs from deterministic builder"
        print("CURRENT M17 R55 FILL/CLEAR BUILDER PASS",
              {k:v for k,v in meta.items() if k!="helper_labels"})
    elif active=="promoted R54 v0.12.9" or "BANK_NUMBER_R54" in active:
        from build_m16_bank_api_r54 import build as bank_build
        candidate,details_candidate=bank_build()
        assert candidate==current, "R54 candidate does not match its compiler-safe builder"
        print("ACTIVE R54 BANK NUMBER BUILDER PASS",
              {k:v for k,v in details_candidate.items() if not k.endswith("_labels")})
    elif "IMAGE_CAPTURE_LINK_FIX_R53" in active:
        from build_m16_capture import build as capture_build
        candidate,details_candidate=capture_build()
        assert candidate==current, "Active capture is not reproducible"
        print("ACTIVE CAPTURE BUILDER PASS",{k:v for k,v in details_candidate.items() if k!="labels"})
    assert C1_ARCHIVE.read_bytes() == data, "Archived compiler-safe R46 C1 diverged"
    # verify_active() separately checks the pinned LAST_GOOD release.
    print("HISTORICAL R46 C1 BRIDGE PASS", details)
    print("CURRENT INSTALLABLE LIBRARY PASS:", active)
    print("Current modular R83 source: frozen R82 -> tools/build_aga_r83_modular.py")
    print("Future changes: extend audited R83 native units, do not replace with old monolith")


if __name__ == "__main__":
    main()
