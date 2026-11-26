"""Canonical active test candidate and SHA-pinned protected LAST_GOOD.

M19 B7-m2 is the authorized active TEST candidate (Gate A PASS; Runtime repeat-launch B pending). Historical B7-m1 remains source-built.
P0d remains source-reproducible by its frozen builder and Git history.
R88 v0.13.33 is a historical AGPC masked Blitter candidate.
R87 v0.13.32 is frozen in dist/experimental with P2.5/P2.6/P2.7 WinUAE evidence.
R86 v0.13.31 was the prior NON-PROMOTED M19 P2.3 Batch candidate; native Gate A and WinUAE Runtime B/Compiled C passed for the dedicated test. No speedup established. R84 LAST_GOOD unchanged.

R84 v0.13.29 is PROMOTED LAST_GOOD with explicit author approval: native Gate A PASS and WinUAE AMOS Compiler Gate C PASS (with a bank in the compiled program). Separate corrected Runtime Gate B NOT evidenced; physical Gate D untested.
R83 v0.13.28 is the reproducible historical LAST_GOOD with A/B/C PASS on its own WinUAE test.
R82 v0.13.27 remains the historical SHA-pinned source built from its own deterministic builder.
R81 v0.13.26 is the SHA-pinned predecessor, separately reproducible from its frozen builder.
R73 v0.13.18 remains reconstructible through its immutable builder and Git history.
R68 v0.13.13 remains SHA-pinned in its deterministic builder and Git history.
R69 OPT020/P1e passed CPU/WinUAE and interpreted/compiled benchmarks.
R70 OPT020/P2 failed WinUAE Gate B ($80000004) and remains a frozen regression.
R71 OPT020/P2 repairs relative links; WinUAE interpreted Gate B PASS.
R72 OPT020/P2 hardens late reject D3, interpreted WinUAE Gate B PASS.
R73 OPT020/P3 accelerates Fast Icon draw/capture with native 020, A/B/C PASS.
R63 remains preserved in Git history; physical Gate D has not been tested.
R65 and R64 historical candidates passed Gates A/B interpreted and visual.
Historical R60 remains reconstructible and preserved in Git history.
No synthetic 40K padding is included.
"""
from hashlib import sha256
from pathlib import Path

# M19 P0d: protected functional predecessor, Gate B/C PASS on its own test.
AP20_ISLANDS_SHA="34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56"
B7_SHA="f69e048b9478145e9dae2c5ebbdec39736ad7df5dfa0034a201feb863078ab0b"  # immutable historical B7 predecessor
B7M1_SHA="838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403"  # frozen historical source
B7M2_SHA="242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6"  # frozen historical B7-m2
B8_SHA="00969199df0be556c53a2dcce03609127810216c28a3180c1aa97795621299ae"  # frozen B8 (SafePort workaround 405 frames Runtime only)
B8S1_SHA="3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a"  # new bounded-SafePort Clear, 119 MC68020 checks PASS, WinUAE B/C pending
P1E_SHA="7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42"
P2D_SHA="ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f"
P2DL2_SHA="b2811e56c12be23697f0bb3c60dbf67f01bdecae0cfb23a787e2d349070f44a1"  # Exact L1+L2 Gate A 172 writer cases + 10 Bob suites; B/C/D pending
S1P1E_SHA="1491ad72712bdee3761f0eb74818220db5daa8aaa5be0a526dc4d0888f252106"  # Author-approved active AGSP capture test candidate; Gate A only
P2C_SHA="eebd7175035f6e6afbd7ed4d2bf5363bd6f816887993db22b848f8d5cfe48d3d"
P2B_SHA="96f4bc7e1d604d57d615e198eb43ca6abc800cdc3853c6e9ac2827ad6a86e448"
P2A_SHA="e2d149f67da9eb3a8c7222113338a8e0ad3f08fb512792a54b825987e88d92fe"  # M19 P2a test candidate; Gate A PASS, WinUAE B pending; LAST_GOOD P1e
P1D_SHA="47fc7c5d056211a62a50b5405b8952db0bb715ace72a8dc257c4a90def2eb785"
P1C_SHA="658717f41e73ea0410ddcea682929d357df1a80fefd40d8ae0dece037a37613c"
P1B_SHA="2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4"  # active M19 P1b native Safe-Blitter hotspot; Gate A MC68020 PASS, B/C/D pending
P1A_SHA="165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a"  # M19 P1a active test candidate; exact source-built, Gate A 110 PASS, B/C/D pending
P0_FREE_SHA="f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d"  # M19 P0 89 public commands; Gate A 225 PASS; Runtime B functional PASS, C deferred
# The single canonical dist/AMOSPro_AGA.Lib is now authorized for AP20 V2 island tests.
P0D_SHA="bc13229fdc38b2420f6680aa000f58e1480d867a53c32fa4290139142eb919be"
# M19 P0c is frozen previous source-built candidate.
P0C_SHA="277802d4aefbe007b86cb8a4dbb9f0703f3a24014971a1824ba38f82d7d7b51a"

C1_SHA="d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b"
C1_ARCHIVE="dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib"
P2DL2B_SHA="a7ed96e92b460e842772aed77ac35a303d8f663aaa456821c323109446dd19dc"  # Exact L2b MC68020 Gate A: 184 Pattern + 172 writers + 10 Bob suites
S1P1F_SHA="dffe70c5550a4387b99901a2431892a2a7d6fe67328ab7cff8f69afd7ad91931"  # Exact MC68020 Gate A run 45466155974; B/C/D pending
S1P1G_SHA="29788993d299c47d923ddce45ae2c9ae2cc3c98e510989a6975db3a3d10c6f66"  # S1-P1g AP20 instruction-signature correction, 24/11/2026
S1P1H_SHA="900646cc208cc99095c81c209276579a28dbcbbcbd43dd10c4e93be35d2e05eb"  # Historical P1h Gate A 45481353847; Runtime B FAIL ERR 9
S1P1I_SHA="2f3cb4adf56121f62aeccf9916d680ba3e2857c9bdbe0fda777d1d7eaed7ffc3"  # Full native Gate A 45492646401; real B/C/D pending
S1P2I_SHA="89b7a9ead30152d2088ca761e81f7016a47bab451024c637009426d7ba777b96"  # Exact integrated Gate A 45682158541
S1P2J_SHA="47d554866f1c04a63f9111dafd8bc64c9b937fc8e2ea9706ab6f20d12777b05a"  # Exact diagnostic Gate A 45690711843; B/C/D pending
S1P2K_SHA="ecfee351e9afbff95dfbfd16ab805b896e8c4889147f70136dd5b1c8dcbdee41"  # Exact r4 Gate A 45705955562; B/C/D pending
SPRITE_L2B_HISTORICAL_SHAS=(S1P1F_SHA, S1P1G_SHA, S1P1H_SHA, S1P1I_SHA, S1P2I_SHA, S1P2J_SHA, S1P2K_SHA)
SPRITE_L2B_HISTORICAL_SIZES=((142684,S1P1F_SHA),(142684,S1P1G_SHA),(142720,S1P1H_SHA),(142968,S1P1I_SHA),(149384,S1P2I_SHA),(148296,S1P2J_SHA),(149080,S1P2K_SHA))
LAST_GOOD_SHA=P2DL2B_SHA  # Author-approved promotion 24/11/2026; Gate A and documented Runtime B; C deferred, D untested
R55_SHA="97f48ccb946ced9bad0b661cbabff00440a4e5a07aeef49021b215b269fcf9ad"  # Historical R55 builder identity, no separate R55 binary
R56_SHA="df0bf2400eb9dc87e69e94f4472c05c8a7d57b496ef792a11125f7419d75ffef"  # R56 historical, compiler FAIL
R58_SHA="c4c3a1306058f39e336653b63cd219b2e94f539a55da837a1f03f8edb3f9fc5b"  # Historical user-tested R58 40K V2 probe
R59_SHA="00d56b03fa455c851501fe19ac98e0cea46c04a7c8c7786b94042ffcced6b08d"  # Historical deterministic R59 0.13.4, former LAST_GOOD
R60_SHA="00b884ec34e6c30ab6a8f194dc3882aa8ac7e5e53697604089d04f2f8c7ad0c8"  # M18/R60 v0.13.5 AGAPIC region, promoted LAST_GOOD
R61_SHA="ff26a7819744a8e42a64628d5e66504710835c2af812650e89cc681fb3c9050f"  # Historical R61, WinUAE A/B/C PASS
R62_SHA="9fede9f8899ff8ec3c4d978a354e30d16b7e40006c854ac96f547098d786d6f6"  # Historical R62 Gate A PASS, WinUAE interpreted RESULT 0
R63_SHA="fd3b30e6d9d7801570a5e1d46a165c95623dd02d1ff0c4fdb4127f855e3087ba"  # Promoted R63 A/B PASS; visual pixels pending, C end M18
R64_SHA="4859e67d784ad48d20b6fcce2ef39276a7005d9e834a4e76ee42e4a6d0b0de0c"  # R64 FICON8 Create Gates A/B interpreted + visual PASS, NOT PROMOTED; C end M18
R65_SHA="6a1f3228b695331a37cd2b352679a07888fe6b94dd53e6c7f15c8f76151b17f2"  # R65 FICON8 Bank Put Gates A/B interpreted + visual PASS; C end M18
R66_SHA="e57840e0c4f1379840e1254f1fb9ab800ce1ad712556efbd872047ea8822c7ca"  # R66 FICHIP8 Create+Stage Gates A/B interpreted+visual PASS
R67_SHA="ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5"  # R67 FICON8 Capture Gates A/B PASS
R68_SHA="ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed"  # R68 Chip CBlock Gates A/B/C PASS, promoted LAST_GOOD
R69_SHA="9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298"  # OPT020/P1e proven WinUAE interpreted and benchmark compiled (historical)
R70_SHA="fa69f514cd71c1490f67bc693d6a3b3afeffd26dbe0605189b57eacfc81ab7ad"  # FAILED WinUAE, never active
R71_SHA="1f4cdaabcc0e4ec641b1a60aec06e780187d66b7aaef172131fc7a7011ec85b0"  # corrected P2 links; interpreted Gate B PASS
R72_SHA="fdb98db259618fbdc3802843e2d6e836cb64acf2d68dc50bbe1133d46d36e67b"  # D3 reset; interpreted Gate B PASS
R73_SHA="c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407"  # Fast Icons capture/draw 020, Gates A/B/C PASS
R74_SHA="887f29c0350f47af9d93d1ebf64fc405c8542e897ff0e7d9d95eda6f814c2a23"  # Open-only C2P candidate; Gate A/B PASS
R75_SHA="c5a5a0e45e5b07012247937bf1af0371836f0d119577c102d62a28f4ca1ad3af"  # Open + Convert, RPG input regression (DO NOT INSTALL)
R76_SHA="9e0a77f3e69c06cfcc96b00b8dc1f23122d559f617beac8762310c5f4bb53897"  # RPG input-state relocation, Gate A 24/24 PASS; WinUAE B pending
R77_SHA="81940e4950f8c21237fb3a9a033f3df0fee4ffaae0d959231ecb20df0d51af11"  # R77 Close native and WinUAE functional Gate B PASS
R78_SHA="9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c"  # C2P Blit A/B WinUAE PASS
R79_SHA="ea6a710526f25e8d30669fb33a722d5784eb5ea7cc60df5ad10fd10626a86cab"
R80_SHA="24e05f7403c07d23db1ff65c9499a032b413fd7d0d140ce8a55e2fd6778b18c6"  # IFF->chunky, A PASS; R80 Runtime 8-plane B PASS
R81_SHA="9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4"  # C2P MC68020 optimized Blit/Zoom/IFF, Gates A/B/C PASS (8 planes / 68030)
R82_SHA="b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36"  # R82 historical former LAST_GOOD; Gates A/B Runtime/C PASS; physical D untested
R83_SHA="01cc389fc5d28f306e52c7e4ec29b653d56c92807289c51731e685b0d3469feb"  # R83 0.13.28 modular former LAST_GOOD; R82 historical pinned
R84_SHA="46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d"  # R84 0.13.29 PROMOTED LAST_GOOD, Gate A CPU/CI and C AMOS Compiler PASS (bank included); corrected B not separately evidenced
R85_SHA="4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f"  # M19 P2.2 0.13.30 historical four-group probe, Gates A/B Runtime/C Compiled PASS
R86_SHA="63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f"  # M19 P2.3 0.13.31 BOBS native A PASS, WinUAE Runtime B/Compiled C PASS per author logs; NOT LAST_GOOD
R87_SHA="02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302"  # M19 P2.5 0.13.32 no probe, native MC68020 Gate A 9/9 PASS, WinUAE B/C NOT TESTED; NOT LAST_GOOD
R88_SHA="69e47f8571dc5e7e50c1aa341bfed9f65ef3f973c015788668f2034041632fbc"  # P2.8 native MC68020 Gate A PASS, WinUAE B/C pending, NOT LAST_GOOD
P5_EXPERIMENT_SHA="db55149f19f2d4753232cb5768167f38c82e86c5e2613a056e093fa9c23897af"  # active dist on experiment branch only, NOT LAST_GOOD
R57_SHA="aee712c8fee75982c74421acc023fdaad733e3f390f3e143050765802c7925d0"  # Historical reproducible R57 0.13.2, formerly LAST_GOOD
CANDIDATE_HASHES={
    "dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib": "f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.8_IMAGE_CAPTURE_LINK_FIX_R53.Lib": "4cc7d78998720748e70a1498ec28375b03a4f5b98e02b3510d253f797af7ae26",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.3_R48_TOKEN_ABI_PROBE.Lib":
        "c30cfcc33ee50bb1f18c36225ccd7a5a6df7860e11201608d1801a0095687028",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.4_R49_GETADR_PROBE.Lib":
        "c18a0992ee148beb437aecc2c1c865338630b40e34bc989c72dfb26313d5657e",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.5_R50_RJSR_FNONE_PROBE.Lib":
        "984cbd5f6485c9f1133eafe356d23c290b2e457902d4f518df3776ffbb5f5eef",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.6_R51_RJSR_RELOCATION_PROBE.Lib":
        "04808ea9c89afb171a2c82f1ab61efd8bc912a0449d13cb20e942ad655ba7aea",
    "dist/experimental/AMOSPro_AGA_M16_v0.12.7_R52_FNONE_TARGET_PROBE.Lib":
        "09ec9797fdea8f1b4694b2c8a9052776ff5cdcf7b959f2f1533c0b41151ea82e",
}
def verify_p2d_l2(candidate: bytes, baseline: bytes):
    """Check exact Gate-A SHA and source-proven append-only ranges without vasm.

    The dedicated L2 workflow independently rebuilds and compares the
    entire installed image against the editable assembly sources.
    """
    from compiler_relocation import unpack_ap20
    from ap20_v2_island_dispatch import pc16_displacements
    from audit_ap20 import inspect, parse
    assert len(baseline) == 136020 and sha256(baseline).hexdigest() == P2D_SHA
    assert len(candidate) == 136332 and sha256(candidate).hexdigest() == P2DL2_SHA
    oldtok, old, _ = unpack_ap20(baseline)
    tok, new, title = unpack_ap20(candidate)
    assert tok == oldtok and len(new) == len(old) == 203
    assert b'$VER: AMOSPro_AGA M19 P2d-L2' in title
    assert [i for i, (a,b) in enumerate(zip(old,new)) if a != b] == [142,202]
    assert len(old[142]) == 62740 and len(new[142]) == 62960
    assert len(old[202]) == 60928 and len(new[202]) == 61008
    for group, patches in ((142, ((0xce8,6),(0xe88,6))), (202, ((48958,4),))):
        restored = bytearray(new[group][:len(old[group])])
        for offset, size in patches:
            restored[offset:offset+size] = old[group][offset:offset+size]
        assert bytes(restored) == old[group], 'L2 changed legacy code or State data'
    assert pc16_displacements(new) == pc16_displacements(old)
    assert not inspect(parse(candidate))['issues']


def verify_p2d_l2b(candidate: bytes, baseline: bytes):
    """Verify exact native Gate-A identity and reversibility to frozen L2."""
    from compiler_relocation import unpack_ap20, repack_ap20
    from ap20_v2_island_dispatch import pc16_displacements
    from audit_ap20 import inspect, parse
    assert len(candidate) == 136708 and sha256(candidate).hexdigest() == P2DL2B_SHA
    tok, parts, title = unpack_ap20(candidate)
    assert len(parts) == 203 and len(parts[142]) == 63334
    assert title.rstrip(bytes([0])).endswith(b'$VER: AMOSPro_AGA M19 P2d-L2b')
    assert parts[142][1914:1920] == bytes.fromhex('60ff0000ee74')
    prior_parts = list(parts)
    prior_unit = bytearray(parts[142][:62960])
    prior_unit[1914:1920] = bytes.fromhex('28522c6a0008')
    prior_parts[142] = bytes(prior_unit)
    prior_title = (b'AMOSPro AGA M19 P2d L2 SafePort+B8 MC68020 candidate'+bytes([0])+
                   b'$VER: AMOSPro_AGA M19 P2d-L2'+bytes([0]))
    prior_title += bytes(len(prior_title) & 1)
    prior = repack_ap20(candidate, tok, prior_parts, prior_title)
    verify_p2d_l2(prior, baseline)
    assert pc16_displacements(parts) == pc16_displacements(prior_parts)
    assert not inspect(parse(candidate))['issues']


def frozen_p2d(protected: bytes) -> bytes:
    """Source-built historical P2d, independently of the moving LAST_GOOD."""
    from build_m19_p2d_in_memory import build_p2d
    baseline, meta = build_p2d()
    assert len(baseline) == 136020 and sha256(baseline).hexdigest() == P2D_SHA
    assert meta['sha256'] == P2D_SHA
    if sha256(protected).hexdigest() == P2D_SHA:
        assert protected == baseline
    else:
        verify_p2d_l2b(protected, baseline)
    return baseline


def verify_s1p1f(candidate: bytes, protected: bytes):
    """Authenticate the Gate-A exact S1-P1f additive extension of L2b."""
    from compiler_relocation import GETP, RBSR, unpack_ap20
    from compiler_bridge_v2_probe import DISPATCH_V2
    from ap20_v2_island_dispatch import pc16_displacements
    from audit_ap20 import inspect, parse, token
    assert len(protected) == 136708 and sha256(protected).hexdigest() == P2DL2B_SHA
    assert len(candidate) == 142684 and sha256(candidate).hexdigest() == S1P1F_SHA
    oldtok, old, _ = unpack_ap20(protected)
    tok, parts, title = unpack_ap20(candidate)
    assert len(old) == 203 and len(parts) == 208 and parts[:203] == old
    assert tok == (oldtok[:-6] + token('aga sprite bank', 204, 1, 'I0')
                   + token('get aga sprite', 206, 1, '00,0,0,0,0,0') + oldtok[-6:])
    assert parts[203] == parts[205] == GETP
    assert parts[204] == RBSR + bytes.fromhex('00cf00004e75')
    assert parts[206] == RBSR + bytes.fromhex('00cf00084e75')
    assert parts[207].startswith(DISPATCH_V2)
    native = parts[207][len(DISPATCH_V2):]
    assert len(native) == 5840
    assert sha256(native).hexdigest() == '5306ac51845f03cc15d5743c84528d1cb0eff1c6f82eae4979fd14a947c735ff'
    assert b'$VER: AGSP S1-P1f L2b non-distributed' in title
    links = pc16_displacements(parts)
    baseline = pc16_displacements(old)
    assert set(links) == set(baseline) | {204, 206}
    assert all(links[k] == v for k, v in baseline.items())
    assert not inspect(parse(candidate))['issues']


def verify_s1p1g(candidate: bytes, protected: bytes) -> bytes:
    """Verify the corrected identity and restore the exact P1f oracle in RAM.

    P1f is retained as historical evidence only: its instruction signature
    is invalid in AMOS. P1g changes no machine code, jumps or ABI entries.
    """
    from audit_ap20 import inspect, parse, token, token_role_issues, walk_tokens
    from compiler_relocation import repack_ap20, unpack_ap20
    from build_m19_s1p1f_l2b_get_sprite_ap20 import TITLE as parent_title

    assert len(candidate) == 142684 and sha256(candidate).hexdigest() == S1P1G_SHA
    assert len(protected) == 136708 and sha256(protected).hexdigest() == P2DL2B_SHA
    oldtok, old, _ = unpack_ap20(protected)
    tok, parts, title = unpack_ap20(candidate)
    assert len(parts) == 208 and parts[:203] == old
    bank = token('aga sprite bank', 204, 1, 'I0')
    assert tok == oldtok[:-6] + bank + token(
        'get aga sprite', 206, 1, 'I0,0,0,0,0,0') + oldtok[-6:]
    assert title == parent_title.replace(b'S1-P1f', b'S1-P1g')
    audit = inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([row for row in walk_tokens(tok) if row['signature']]) == 102
    historical_tokens = oldtok[:-6] + bank + token(
        'get aga sprite', 206, 1, '00,0,0,0,0,0') + oldtok[-6:]
    parent = repack_ap20(candidate, historical_tokens, parts, parent_title)
    verify_s1p1f(parent, protected)
    return parent


def verify_s1p1h(candidate: bytes, protected: bytes):
    """Verify the exact source-assembled P1h candidate, independently of P1g."""
    from audit_ap20 import inspect, parse, token, token_role_issues, walk_tokens
    from compiler_relocation import GETP, RBSR, unpack_ap20
    from compiler_bridge_v2_probe import DISPATCH_V2
    from ap20_v2_island_dispatch import pc16_displacements
    from build_m19_s1p1f_l2b_get_sprite_ap20 import TITLE as parent_title

    assert len(candidate) == 142720 and sha256(candidate).hexdigest() == S1P1H_SHA
    assert len(protected) == 136708 and sha256(protected).hexdigest() == P2DL2B_SHA
    oldtok, old, _ = unpack_ap20(protected)
    tok, parts, title = unpack_ap20(candidate)
    assert len(old) == 203 and len(parts) == 208 and parts[:203] == old
    assert tok == oldtok[:-6] + token('aga sprite bank', 204, 1, 'I0') + token(
        'get aga sprite', 206, 1, 'I0,0,0,0,0,0') + oldtok[-6:]
    assert title == parent_title.replace(b'S1-P1f', b'S1-P1h')
    assert parts[203] == parts[205] == GETP
    assert parts[204] == RBSR + bytes.fromhex('00cf00004e75')
    assert parts[206] == RBSR + bytes.fromhex('00cf00084e75')
    assert parts[207].startswith(DISPATCH_V2)
    native = parts[207][len(DISPATCH_V2):]
    assert len(native) == 5878
    assert sha256(native).hexdigest() == '5aa8554db81399699a7e943066084f00753750e6fc93194906a3ce6db6b90be5'
    links = pc16_displacements(parts)
    baseline = pc16_displacements(old)
    assert set(links) == set(baseline) | {204, 206}
    assert all(links[k] == v for k, v in baseline.items())
    audit = inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([row for row in walk_tokens(tok) if row['signature']]) == 102


def verify_s1p1i(candidate: bytes, protected: bytes):
    """Verify the exact source-assembled P1i candidate, independently of P1h."""
    from audit_ap20 import inspect, parse, token, token_role_issues, walk_tokens
    from compiler_relocation import GETP, RBSR, unpack_ap20
    from compiler_bridge_v2_probe import DISPATCH_V2
    from ap20_v2_island_dispatch import pc16_displacements
    from build_m19_s1p1f_l2b_get_sprite_ap20 import TITLE as parent_title

    assert len(candidate) == 142968 and sha256(candidate).hexdigest() == S1P1I_SHA
    assert len(protected) == 136708 and sha256(protected).hexdigest() == P2DL2B_SHA
    oldtok, old, _ = unpack_ap20(protected)
    tok, parts, title = unpack_ap20(candidate)
    assert len(old) == 203 and len(parts) == 208 and parts[:203] == old
    assert tok == oldtok[:-6] + token('aga sprite bank', 204, 1, 'I0') + token(
        'get aga sprite', 206, 1, 'I0,0,0,0,0,0') + oldtok[-6:]
    assert title == parent_title.replace(b'S1-P1f', b'S1-P1i')
    assert parts[203] == parts[205] == GETP
    assert parts[204] == RBSR + bytes.fromhex('00cf00004e75')
    assert parts[206] == RBSR + bytes.fromhex('00cf00084e75')
    assert parts[207].startswith(DISPATCH_V2)
    native = parts[207][len(DISPATCH_V2):]
    assert len(native) == 6126
    assert sha256(native).hexdigest() == '8b4b9b2c664d152fea4d516c936877e87e133bc79cfb6dbdea8bc9953ba3a245'
    links = pc16_displacements(parts)
    baseline = pc16_displacements(old)
    assert set(links) == set(baseline) | {204, 206}
    assert all(links[k] == v for k, v in baseline.items())
    audit = inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([row for row in walk_tokens(tok) if row['signature']]) == 102


def frozen_s1p1i(candidate: bytes, protected: bytes) -> bytes:
    """Recover exact historical P1i from protected L2b and the pinned P2i prefix."""
    from audit_ap20 import token
    from compiler_relocation import repack_ap20, unpack_ap20
    from compiler_bridge_v2_probe import DISPATCH_V2
    from build_m19_s1p1f_l2b_get_sprite_ap20 import TITLE as parent_title
    assert sha256(candidate).hexdigest() in (S1P2I_SHA, S1P2J_SHA, S1P2K_SHA)
    assert sha256(protected).hexdigest() == P2DL2B_SHA
    oldtok, old, _ = unpack_ap20(protected)
    _, parts, _ = unpack_ap20(candidate)
    assert len(old)==203 and len(parts)==214
    tok=oldtok[:-6]+token('aga sprite bank',204,1,'I0')+token(
        'get aga sprite',206,1,'I0,0,0,0,0,0')+oldtok[-6:]
    p=[*old,*parts[203:207],parts[207][:len(DISPATCH_V2)+6126]]
    prior=repack_ap20(protected,tok,p,parent_title.replace(b'S1-P1f',b'S1-P1i'))
    verify_s1p1i(prior,protected)
    return prior


def verify_s1p2i(candidate: bytes, protected: bytes):
    """Verify the exact integrated Sprite binary qualified by Gate A."""
    from audit_ap20 import inspect, parse, token, token_role_issues, walk_tokens
    from compiler_relocation import GETP, RBSR, unpack_ap20
    from compiler_bridge_v2_probe import DISPATCH_V2
    from ap20_v2_island_dispatch import pc16_displacements
    from struct import pack
    assert len(candidate)==149384 and sha256(candidate).hexdigest()==S1P2I_SHA
    prior=frozen_s1p1i(candidate,protected)
    ot,old,otitle=unpack_ap20(prior)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==214 and len(parts[142])==65194
    assert [i for i,(x,y) in enumerate(zip(old,parts)) if x!=y]==[142,207]
    assert parts[207].startswith(old[207])
    assert len(parts[207])==len(DISPATCH_V2)+10558
    assert parts[142][-16:]==bytes.fromhex('00000000414753490001001000000000')
    assert title==otitle.replace(b'S1-P1i',b'S1-P2i')
    apis=(('aga sprite','00,0,0,0'),('aga sprite off','00'),('aga sprite bank free','00'))
    assert tok==ot[:-6]+b''.join(token(n,1,209+2*j,sig) for j,(n,sig) in enumerate(apis))+ot[-6:]
    for j in range(3):
        assert parts[208+j*2]==GETP
        assert parts[209+j*2]==RBSR+pack('>HH',207,6126+4*j)+bytes.fromhex('4e75')
    baseline=pc16_displacements(old)
    links=pc16_displacements(parts)
    assert set(links)==set(baseline)|{209,211,213}
    assert all(links[k]==v for k,v in baseline.items())
    assert max(map(abs,links.values()))==10622
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([row for row in walk_tokens(tok) if row['signature']])==105

def verify_s1p2j(candidate: bytes, protected: bytes):
    """Verify the exact one-shot diagnostic Sprite binary qualified by Gate A."""
    from audit_ap20 import inspect, parse, token, token_role_issues, walk_tokens
    from compiler_relocation import GETP, RBSR, unpack_ap20
    from compiler_bridge_v2_probe import DISPATCH_V2
    from ap20_v2_island_dispatch import pc16_displacements
    from struct import pack
    assert len(candidate)==148296 and sha256(candidate).hexdigest()==S1P2J_SHA
    prior=frozen_s1p1i(candidate,protected)
    ot,old,otitle=unpack_ap20(prior)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==214 and len(parts[142])==64560
    assert [i for i,(x,y) in enumerate(zip(old,parts)) if x!=y]==[142,207]
    assert parts[207].startswith(old[207])
    assert len(parts[207])==len(DISPATCH_V2)+10104
    assert parts[142][-16:]==bytes.fromhex('00000000414753490001001000000000')
    assert title==otitle.replace(b'S1-P1i',b'S1-P2j')
    apis=(('aga sprite','00,0,0,0'),('aga sprite off','00'),('aga sprite bank free','00'))
    assert tok==ot[:-6]+b''.join(token(n,1,209+2*j,sig) for j,(n,sig) in enumerate(apis))+ot[-6:]
    for j in range(3):
        assert parts[208+j*2]==GETP
        assert parts[209+j*2]==RBSR+pack('>HH',207,6126+4*j)+bytes.fromhex('4e75')
    baseline=pc16_displacements(old)
    links=pc16_displacements(parts)
    assert set(links)==set(baseline)|{209,211,213}
    assert all(links[k]==v for k,v in baseline.items())
    assert max(map(abs,links.values()))==10168
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([row for row in walk_tokens(tok) if row['signature']])==105


def verify_s1p2k(candidate: bytes, protected: bytes):
    """Verify the exact r4 transactional Sprite binary qualified by Gate A."""
    from audit_ap20 import inspect, parse, token, token_role_issues, walk_tokens
    from compiler_relocation import GETP, RBSR, unpack_ap20
    from compiler_bridge_v2_probe import DISPATCH_V2
    from ap20_v2_island_dispatch import pc16_displacements
    from struct import pack
    assert len(candidate)==149080 and sha256(candidate).hexdigest()==S1P2K_SHA
    prior=frozen_s1p1i(candidate,protected)
    ot,old,otitle=unpack_ap20(prior)
    tok,parts,title=unpack_ap20(candidate)
    assert len(parts)==214 and len(parts[142])==65276
    assert [i for i,(x,y) in enumerate(zip(old,parts)) if x!=y]==[142,207]
    assert parts[207].startswith(old[207])
    assert len(parts[207])==len(DISPATCH_V2)+10174
    assert parts[142][-16:]==bytes.fromhex('00000000414753490001001000000000')
    assert title==otitle.replace(b'S1-P1i',b'S1-P2k')
    apis=(('aga sprite','00,0,0,0'),('aga sprite off','00'),('aga sprite bank free','00'))
    assert tok==ot[:-6]+b''.join(token(n,1,209+2*j,sig) for j,(n,sig) in enumerate(apis))+ot[-6:]
    for j in range(3):
        assert parts[208+j*2]==GETP
        assert parts[209+j*2]==RBSR+pack('>HH',207,6126+4*j)+bytes.fromhex('4e75')
    baseline=pc16_displacements(old)
    links=pc16_displacements(parts)
    assert set(links)==set(baseline)|{209,211,213}
    assert all(links[k]==v for k,v in baseline.items())
    assert max(map(abs,links.values()))==10238
    audit=inspect(parse(candidate))
    assert not audit['issues'] and not token_role_issues(audit['tokens'])
    assert len([row for row in walk_tokens(tok) if row['signature']])==105


def verify_active(root: Path):
    """Return (current bytes, LAST_GOOD bytes, version label). Fail closed."""
    from audit_ap20 import parse,inspect
    from compiler_relocation import is_compiler_wrapped
    root=Path(root)
    c1=(root/C1_ARCHIVE).read_bytes()
    assert sha256(c1).hexdigest()==C1_SHA,"Archived R46 C1 changed"
    good=(root/"dist/AMOSPro_AGA_LAST_GOOD.Lib").read_bytes()
    assert sha256(good).hexdigest()==LAST_GOOD_SHA,"LAST_GOOD protected hash mismatch"
    cur=(root/"dist/AMOSPro_AGA.Lib").read_bytes()
    current_sha=sha256(cur).hexdigest()
    if current_sha == S1P2K_SHA:
        frozen_p2d(good)
        verify_s1p2k(cur, good)
        return cur, good, "M19 S1-P2k r4 transactional Sprite ACTIVE TEST CANDIDATE; full MC68020 Gate A PASS; B/C/D NOT TESTED; DMA retained; L2b LAST_GOOD protected"
    if current_sha == S1P2J_SHA:
        frozen_p2d(good)
        verify_s1p2j(cur, good)
        return cur, good, "M19 S1-P2j diagnostic Sprite ACTIVE TEST CANDIDATE; full MC68020 Gate A PASS; limited B PASS after reset; C/D NOT TESTED; DMA retained; L2b LAST_GOOD protected"
    if current_sha == S1P2I_SHA:
        frozen_p2d(good)
        verify_s1p2i(cur, good)
        return cur, good, "M19 S1-P2i integrated Sprite REJECTED Runtime ERR 10; historical MC68020 Gate A PASS; C/D NOT TESTED; L2b LAST_GOOD protected"
    if current_sha == S1P1I_SHA:
        frozen_p2d(good)
        verify_s1p1i(cur, good)
        return cur, good, "M19 S1-P1i L2b Get AGA Sprite ACTIVE TEST CANDIDATE; full MC68020 Gate A PASS; B/C/D NOT TESTED; L2b LAST_GOOD protected"
    if current_sha == S1P1H_SHA:
        frozen_p2d(good)
        verify_s1p1h(cur, good)
        return cur, good, "M19 S1-P1h L2b Get AGA Sprite REJECTED Runtime ERR 9; historical Gate A PASS; C/D NOT TESTED; L2b LAST_GOOD protected"
    if current_sha == S1P1G_SHA:
        frozen_p2d(good)
        verify_s1p1g(cur, good)
        return cur, good, "M19 S1-P1g L2b Get AGA Sprite ACTIVE TEST CANDIDATE; AP20 instruction correction; identical P1f native code; B/C/D NOT TESTED; L2b LAST_GOOD protected"
    if current_sha == S1P1F_SHA:
        frozen_p2d(good)
        verify_s1p1f(cur, good)
        return cur, good, "M19 S1-P1f L2b Get AGA Sprite ACTIVE TEST CANDIDATE; MC68020 Gate A PASS; B/C/D NOT TESTED; L2b LAST_GOOD protected"
    if current_sha == P2DL2B_SHA:
        from build_m19_p2d_in_memory import build_p2d
        expected, meta = build_p2d()
        assert meta['sha256'] == P2D_SHA and cur == good
        verify_p2d_l2b(cur, expected)
        return cur, good, "M19 P2d-L2b PROMOTED LAST_GOOD; Gate A MC68020 184 Pattern + 172 writers + 10 Bob suites PASS; Runtime B documented; C deferred, D untested"
    if current_sha == P2DL2_SHA:
        from build_m19_p2d_in_memory import build_p2d
        expected, meta = build_p2d()
        assert good == expected and meta['sha256'] == P2D_SHA
        verify_p2d_l2(cur, good)
        return cur, good, "M19 P2d-L2 ACTIVE TEST CANDIDATE; Gate A MC68020 172 writer cases + 10 Bob suites PASS; WinUAE B, true Compiler C and physical D NOT TESTED; P2d LAST_GOOD protected"
    if current_sha == S1P1E_SHA:
        from build_m19_p2d_in_memory import build_p2d
        from compiler_relocation import GETP, RBSR, unpack_ap20
        from audit_ap20 import walk_tokens
        baseline, baseline_meta=build_p2d()
        assert sha256(baseline).hexdigest()==P2D_SHA
        assert (baseline_meta['commands'],baseline_meta['entries'])==(100,203)
        assert good==baseline and len(good)==136020, "P2d LAST_GOOD must remain byte-exact"
        assert len(cur)==142000 and cur!=good, "S1-P1e candidate bytes changed"
        old_tokens,old_parts,_=unpack_ap20(baseline)
        new_tokens,new_parts,title=unpack_ap20(cur)
        assert len(new_parts)==208 and new_parts[:203]==old_parts
        assert new_parts[203]==GETP and new_parts[205]==GETP
        assert new_parts[204].startswith(RBSR) and new_parts[206].startswith(RBSR)
        old_api=list(walk_tokens(old_tokens))
        api=list(walk_tokens(new_tokens))
        assert len(api)==len(old_api)+2 and api[:-2]==old_api
        assert [(t['name'],t['instruction'],t['function'],t['signature']) for t in api[-2:]]==[
            ('aga sprite bank',204,1,'I0'),
            ('get aga sprite',206,1,'00,0,0,0,0,0'),
        ]
        assert b'$VER: AGSP S1-P1e' in title
        assert inspect(parse(cur))['issues']==[], "S1-P1e HUNK/AP20 audit failed"
        return cur,good,"M19 S1-P1e Get AGA Sprite ACTIVE TEST CANDIDATE; Gate A MC68020 CPU/CI PASS; WinUAE B, true Compiler C and physical D NOT TESTED; P2d LAST_GOOD protected"
    if current_sha == P2D_SHA:
        from build_m19_p2d_in_memory import build_p2d
        expected, meta = build_p2d()
        assert cur == expected and len(cur) == 136020 and meta['sha256'] == P2D_SHA
        assert (meta['commands'], meta['entries'], meta['pc16_max']) == (100, 203, 854)
        assert good == cur and len(good) == 136020
        assert sha256(good).hexdigest() == P2D_SHA
        return cur, good, "M19 P2d PROMOTED LAST_GOOD; native Gate A PASS, integrated P2a-P2e WinUAE Runtime B and true AMOS Compiler C PASS; physical D NOT TESTED"
    if current_sha == P2C_SHA:
        from build_m19_p2c_in_memory import build_p2c
        expected, meta = build_p2c()
        assert cur == expected and len(cur) == 135596 and meta['sha256'] == P2C_SHA
        assert (meta['commands'], meta['entries'], meta['bob_group']) == (99, 202, 194)
        assert len(good) == 124444 and sha256(good).hexdigest() == P1E_SHA
        return cur, good, "M19 P2c Aga Bob Planes TEST CANDIDATE; WinUAE Runtime PASS; Compiler pending; P1e LAST_GOOD"
    if current_sha == P2B_SHA:
        from build_m19_p2b_in_memory import build_p2b
        expected, meta = build_p2b()
        assert cur == expected and len(cur) == 135352 and meta['sha256'] == P2B_SHA
        assert (meta['commands'], meta['entries'], meta['bob_group']) == (98, 200, 192)
        assert len(good) == 124444 and sha256(good).hexdigest() == P1E_SHA
        return cur, good, "M19 P2b Aga Bob Flip TEST CANDIDATE; WinUAE Runtime/Compiler PASS; P1e LAST_GOOD"
    if current_sha == P2A_SHA:
        from build_m19_p2a_public_in_memory import build_p2a
        expected, meta = build_p2a()
        assert cur == expected and len(cur) == 129544 and meta['sha256'] == P2A_SHA
        assert (meta['public_commands'],meta['entries'],meta['bob_group']) == (97,198,190)
        assert len(good) == 124444 and sha256(good).hexdigest() == P1E_SHA and cur != good
        return cur,good,"M19 P2a Aga Bob Col TEST CANDIDATE; Gate A source/native PASS; WinUAE Runtime B, real Compiler C and physical D NOT TESTED; P1e LAST_GOOD protected"
    if current_sha == P1E_SHA:
        from build_m19_p1e_bank_edit_in_memory import build_p1e
        expected, meta = build_p1e()
        assert cur == expected and len(cur) == 124444 and meta['sha256'] == P1E_SHA
        assert (meta['commands'], meta['entries'], meta['pc16_max']) == (96, 196, 14130)
        assert len(good) == 124444 and cur == good and sha256(good).hexdigest() == P1E_SHA
        return cur, good, "M19 P1e PROMOTED LAST_GOOD; native Gate A PASS, WinUAE Runtime B PASS x2; AMOS Compiler C and physical D NOT TESTED"
    if current_sha == P1D_SHA:
        from build_m19_p1d_limit_bob_in_memory import build_p1d
        expected, meta = build_p1d()
        assert cur == expected and len(cur) == 121432 and meta['sha256'] == P1D_SHA
        assert (meta['public_commands'], meta['ap20_entries'], meta['pc16_max']) == (94, 192, 32530)
        assert meta['native_groups'] == [142, 153, 156, 181, 185]
        assert len(good) == 117896 and cur != good
        return cur, good, "M19 P1d Limit Bob test candidate, MC68020 Gate A PASS"
    if current_sha == P1C_SHA:
        from build_m19_p1c_bob_priority_in_memory import build_p1c
        expected, meta = build_p1c()
        assert cur == expected and len(cur) == 119916 and meta['sha256'] == P1C_SHA
        assert (meta['public_commands'], meta['ap20_entries'], meta['pc16_max']) == (93, 190, 32144)
        assert meta['native_groups'] == [142, 153, 156, 179, 183]
        assert len(good) == 117896 and cur != good
        return cur, good, "M19 P1c Bob Priority test candidate, MC68020 Gate A PASS"
    if current_sha == P1B_SHA:
        from build_m19_p1b_hotspot_in_memory import build_p1b
        from compiler_relocation import unpack_ap20
        expected,meta=build_p1b()
        assert cur==expected and len(cur)==119176
        assert meta['sha256']==P1B_SHA and meta['predecessor_sha']==P1A_SHA
        assert (meta['public_commands'],meta['ap20_entries'],meta['native_groups'])==(
            92,188,[142,153,156,177,181])
        assert meta['pc16_max']==31444
        assert len(good)==117896 and sha256(good).hexdigest()==P0_FREE_SHA
        assert cur!=good,'P1b must never overwrite promoted P0 LAST_GOOD'
        _,parts,title=unpack_ap20(cur)
        assert len(parts)==188 and b'M19 P1b Bob Hot Spot Safe Blitter' in title
        audit=inspect(parse(cur))
        assert not audit['issues']
        named=[t for t in audit['tokens']
               if t['name'].startswith(('aga ','get aga ','make aga ','no aga '))]
        assert len(named)==92
        for field,index in (('x',185),('y',186),('i',187)):
            row=named[-(188-index)]
            assert (row['name'],row['instruction'],row['function'],row['signature'])==(
                f'aga {field} bob',1,index,'00')
        return cur,good,'M19 P1b HOTSPOT ACTIVE WINUAE CANDIDATE, 92 commands /188 AP20; native MC68020 Gate A PASS; Runtime B, Compiler C, physical D NOT TESTED; P0 LAST_GOOD protected'
    if current_sha == P1A_SHA:
        from build_m19_p1a_getters_in_memory import build_p1a
        from compiler_relocation import unpack_ap20
        candidate,meta=build_p1a()
        assert cur==candidate and len(cur)==118816, "P1a active Lib builder/size mismatch"
        assert meta['sha256']==P1A_SHA and meta['p0_sha']==P0_FREE_SHA
        assert (meta['public_commands'],meta['ap20_entries'],meta['native_groups'])==(
            92,188,[142,153,156,177,181])
        assert meta['pc16_max']==31092 and meta['refusal_sentinel']==-32769
        assert len(good)==117896 and sha256(good).hexdigest()==P0_FREE_SHA
        assert cur!=good, "Do not promote P1a to LAST_GOOD"
        _,parts,title=unpack_ap20(cur)
        assert len(parts)==188 and b"M19 P1a Bob X/Y/I getters" in title
        audit=inspect(parse(cur))
        named=[t for t in audit['tokens']
               if t['name'].startswith(('aga ','get aga ','make aga ','no aga '))]
        assert not audit['issues'] and len(named)==92
        for field,index in (('x',185),('y',186),('i',187)):
            row=named[-(188-index)]
            assert (row['name'],row['instruction'],row['function'],row['signature'])==(
                f'aga {field} bob',1,index,'00')
        return cur,good,"M19 P1a X/Y/I BOB ACTIVE WINUAE TEST CANDIDATE; MC68020 Gate A PASS 110; Runtime B, Compiler C, physical D NOT TESTED; P0 LAST_GOOD protected"
    if current_sha == P0_FREE_SHA:
        from build_m19_b8_s1_bank_free_in_memory import build_bank_free
        from compiler_relocation import unpack_ap20
        expected,meta=build_bank_free()
        assert cur==expected and len(cur)==117896, "M19 P0 Bank Free differs from SHA-pinned builder"
        assert meta['sha256']==P0_FREE_SHA and meta['predecessor_sha']=='577fe698f040a13ea0a12c88fc80f31fd316eed011a305955eb5be635c8613bf'
        assert (meta['public_commands'],meta['ap20_entries'],meta['native_groups'])==(
            89,185,[142,153,156,177,181])
        assert meta['pc16_max']==31092 and meta['bank_free_index']==184
        _,parts,title=unpack_ap20(cur)
        assert len(parts)==185 and b"M19 P0 Bank Chip Select+Free" in title
        audit=inspect(parse(cur))
        named=[t for t in audit['tokens']
               if t['name'].startswith(('aga ','get aga ','make aga ','no aga '))]
        assert not audit['issues'] and len(named)==89
        assert named[-1]['name']=='aga bob bank free' and named[-1]['instruction']==184
        assert named[-1]['signature']=='I0'
        assert len(good)==117896 and sha256(good).hexdigest()==P0_FREE_SHA and cur==good, "Promoted P0 LAST_GOOD differs from active source-built Lib"
        return cur,good,"M19 P0 Bank Free PROMOTED LAST_GOOD; native Gate A PASS 225 checks; WinUAE Runtime B functional PASS on author logs; AMOS Compiler C NOT TESTED; Amiga physical D NOT TESTED"
    if current_sha == B8S1_SHA:
        from build_m19_b8_safe_retry_in_memory import build_b8_safe_retry
        from compiler_relocation import unpack_ap20
        expected,meta=build_b8_safe_retry()
        assert cur==expected and len(cur)==116104, "B8 S1 active differs from exact source builder"
        assert meta['sha256']==B8S1_SHA and meta['predecessor_sha']==B8_SHA
        assert (meta['public_commands'],meta['ap20_entries'],meta['native_groups'])==(
            88,184,[142,153,156,177,181])
        assert (meta['pc16_max'],meta['wait_tof_max'],meta['new_native_bytes'])==(
            29962,3,360)
        _,parts,title=unpack_ap20(cur)
        assert len(parts)==184 and b"M19 B8 S1 bounded SafePort Clear retry" in title
        audit=inspect(parse(cur))
        named=[t for t in audit['tokens']
               if t['name'].startswith(("aga ","get aga ","make aga ","no aga "))]
        assert not audit['issues'] and len(named)==88
        assert [(t['name'],t['function'],t['signature']) for t in named[-2:]]==[
            ("aga bob clear",182,"0"),("aga bob update",183,"0")]
        assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA and cur!=good
        return cur,good,"M19 B8 S1 Clear/Update ACTIVE TEST CANDIDATE; bounded SafePort VBL; native Gate A MC68020 PASS 119; WinUAE Runtime B and Compiler C NOT TESTED; R84 LAST_GOOD unchanged"
    if current_sha == B8_SHA:
        from build_m19_b8_first_update_in_memory import build_b8_first_update
        from compiler_relocation import unpack_ap20
        expected,meta=build_b8_first_update()
        assert cur==expected and len(cur)==115744, "B8 active differs from verified builder"
        assert meta["sha256"]==B8_SHA
        assert (meta["public_commands"],meta["ap20_entries"],meta["native_groups"]) == (
            88,184,[142,153,156,177,181])
        assert meta["pc16_max"]==29962
        _,parts,title=unpack_ap20(cur)
        assert len(parts)==184 and b"M19 B8 candidate first Clear Update" in title
        audit=inspect(parse(cur))
        named=[t for t in audit["tokens"]
               if t["name"].startswith(("aga ","get aga ","make aga ","no aga "))]
        assert not audit["issues"] and len(named)==88
        assert [(t["name"],t["function"],t["signature"]) for t in named[-2:]] == [
            ("aga bob clear",182,"0"),("aga bob update",183,"0")]
        assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA and cur!=good
        return cur,good,"M19 B8 Clear/Update ACTIVE TEST CANDIDATE; Gate A MC68020 PASS; WinUAE Runtime B and Compiler C NOT TESTED; LAST_GOOD unchanged"
    if current_sha == B7M2_SHA:
        from build_m19_b7m2_close_reset_in_memory import build_close_reset
        from compiler_relocation import unpack_ap20
        expected, meta = build_close_reset()
        assert cur == expected and len(cur) == 102400, "B7-m2 candidate differs from exact source"
        assert meta["sha256"] == B7M2_SHA and meta["predecessor_sha"] == B7M1_SHA
        assert (meta["public_commands"], meta["ap20_entries"], meta["native_groups"]) == (
            86, 181, [142,153,156,177])
        assert meta["pc16_max"] < 32766 and meta["appended_bytes"] == 34
        assert (meta["close_stub"], meta["close_group"], meta["close_native_offset"]) == (
            179, 177, 28852)
        _, parts, title = unpack_ap20(cur)
        assert len(parts) == 181 and b"M19 B7-m2 Close reset" in title
        audit = inspect(parse(cur))
        named = [t for t in audit["tokens"]
                 if t["name"].startswith(("aga ","get aga ","make aga ","no aga "))]
        assert not audit["issues"] and len(named) == 86
        assert len(good) == 67904 and sha256(good).hexdigest() == R84_SHA and cur != good
        return cur, good, "M19 B7-m2 Close/reset ACTIVE TEST CANDIDATE; Gate A MC68020 PASS (75 groups); repeat-launch WinUAE B PENDING; real Compiler C NOT TESTED; R84 LAST_GOOD unchanged"
    if current_sha == B7M1_SHA:
        from build_m19_p0j_end_lifecycle_in_memory import build_multiframe
        from compiler_relocation import unpack_ap20
        expected, meta = build_multiframe()
        assert cur == expected and len(cur) == 102360, "B7-m1 active candidate differs from exact native source"
        assert meta["sha256"] == B7M1_SHA and meta["predecessor_sha"] == B7_SHA
        assert (meta["public_commands"], meta["ap20_entries"], meta["native_groups"]) == (
            86, 181, [142,153,156,177])
        assert meta["pc16_max"] < 32766 and meta["appended_bytes"] == 304
        tokens, parts, title = unpack_ap20(cur)
        assert len(parts)==181 and b"M19 P0j-b7-m1" in title and b"UNINSTALLED" not in title
        audit = inspect(parse(cur))
        named = [t for t in audit["tokens"]
                 if t["name"].startswith(("aga ","get aga ","make aga ","no aga "))]
        assert not audit["issues"] and len(named) == 86
        draw = [t for t in named if t["name"] == "aga bob draw"]
        assert len(draw)==1 and draw[0]["signature"]=="0" and draw[0]["function"]==180
        assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA and cur!=good
        return cur, good, "M19 P0j-b7-m1 multiframe Draw/Swap/End ACTIVE TEST CANDIDATE; Gate A MC68020 PASS (793 checks); WinUAE Runtime B NOT TESTED; real Compiler C NOT TESTED; R84 LAST_GOOD unchanged"
    if current_sha == B7_SHA:
        from build_m19_p0j_end_lifecycle_in_memory import build as build_b7
        from compiler_relocation import unpack_ap20
        expected, meta = build_b7()
        assert cur == expected and len(cur) == 102072, "B7 active candidate is not source-built byte-exact"
        assert meta["sha256"] == B7_SHA and meta["predecessor_sha"] == (
            "3843a3ea3fac05365d7773ed803ca4ab2c288db6fcecce0210b966151c6d2b91"
        ), "B7 provenance chain changed"
        assert (meta["public_commands"],meta["ap20_entries"],meta["native_groups"],meta["pc16_max"]) == (
            86,181,[142,153,156,177],28600
        ), "B7 AP20/MC68020 ABI or PC16 layout changed"
        tokens, parts, title = unpack_ap20(cur)
        assert len(parts)==181 and b"M19 P0j-b7" in title, "B7 HUNK/native title mismatch"
        audit = inspect(parse(cur))
        named = [t for t in audit["tokens"]
                 if t["name"].startswith(("aga ","get aga ","make aga ","no aga "))]
        assert not audit["issues"] and len(named)==86, "B7 public API invalid"
        draw = [t for t in named if t["name"]=="aga bob draw"]
        assert len(draw)==1 and draw[0]["signature"]=="0" and draw[0]["function"]==180
        assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA and cur!=good
        return cur, good, "M19 P0j-b7 BOBS multibank Draw/Swap/End ACTIVE TEST CANDIDATE; Gate A MC68020 PASS (88 cases); WinUAE Runtime B / true AMOS Compiler C NOT TESTED; R84 LAST_GOOD unchanged"
    if current_sha == AP20_ISLANDS_SHA:
        from build_m19_ap20_islands_in_memory import build as build_islands
        from compiler_relocation import unpack_ap20
        expected, meta = build_islands()
        assert cur==expected and len(cur)==96908, "AP20 island candidate differs from source"
        assert meta["sha256"]==AP20_ISLANDS_SHA and meta["ap20_entries"]==178, "AP20 island layout drift"
        assert meta["tokens"]==86 and meta["new_pc16"]==854, "AP20 island ABI/PC16 drift"
        _,units,title=unpack_ap20(cur)
        assert len(units)==178 and b"AP20 V2 ISLAND" in title, "AP20 test version header drift"
        audit=inspect(parse(cur))
        named=[t for t in audit["tokens"] if t["name"].startswith(("aga ","get aga ","make aga ","no aga "))]
        assert not audit["issues"] and len(named)==85, "AP20 island public API drift"
        assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA and cur!=good
        return cur, good, "M19 AP20 V2 ISLANDS TEST CANDIDATE; CPU020 Gate A PASS, Runtime B and real Compiler C NOT TESTED; R84 LAST_GOOD unchanged"
    if current_sha == P0D_SHA:
        from compiler_relocation import unpack_ap20
        from build_m19_p0d_bob_blit_in_memory import build as build_p0d
        expected,meta=build_p0d()
        assert cur==expected and len(cur)==91300 and meta["sha256"]==P0D_SHA, "P0d builder/SHA drift"
        assert (meta["previous_sha"],meta["commands"],meta["entries"]) == (
            P0C_SHA,83,93), "P0d API/source provenance drift"
        assert meta["public_signature"]==("aga bob blit",1,88,"00,0,0")
        assert (meta["group"],meta["entry"])==(91,22688)
        _,parts,title=unpack_ap20(cur)
        assert len(parts)==93 and b"M19 P0d" in title
        audit=inspect(parse(cur))
        named=[t for t in audit["tokens"]
               if t["name"].startswith(("aga ","get aga ","make aga ","no aga "))]
        assert not audit["issues"] and len(named)==83
        assert named[-1]["name"]=="aga bob blit"
        assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA and cur!=good
        return cur,good,"M19 P0d MC68020 public Aga Bob Blit ACTIVE TEST CANDIDATE; native Gate A PASS; Runtime B / real Compiler C NOT TESTED; R84 LAST_GOOD unchanged"
    if current_sha == P0C_SHA:
        # Public Close bridge + PRIVATE End hook. Byte-exact builder, not an
        # unchecked fallback to a historical "Compiler-safe" monolith.
        from compiler_relocation import unpack_ap20
        from build_m19_p0c_screen_close_in_memory import build as build_p0c
        expected,meta=build_p0c()
        assert cur==expected and len(cur)==87020 and meta["sha256"]==P0C_SHA, "P0c builder/SHA drift"
        assert (meta["provenance"],meta["public_commands"],meta["ap20_entries"]) == (
            "f272a98a9d07eb66dc515fc4598b16f9fd64cb55d84c36ec29068f9f074a44d9",82,92), "P0c API/source drift"
        assert (meta["screen_close_index"],meta["bridge_group"],meta["old_aga_group"],
                meta["old_aga_offset"],meta["rel_aga_close"]) == (8,90,91,2008,0x638)
        assert meta["program_end_hook"].startswith("PRIVATE"), "End arm must remain private"
        _,parts,title=unpack_ap20(cur)
        assert len(parts)==92 and b"Screen Close bridge EXPERIMENT UNINSTALLED" in title
        audit=inspect(parse(cur))
        assert not audit["issues"] and len([t for t in audit["tokens"]
                if t["name"].startswith(("aga ","get aga ","make aga ","no aga "))])==82
        assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA and cur!=good
        return cur,good,"M19 P0c MC68020 Screen Close bridge ACTIVE TEST CANDIDATE; Gate A PASS; WinUAE Runtime B / real Compiler C NOT TESTED; End arm PRIVATE; R84 LAST_GOOD unchanged"
    if current_sha == R88_SHA:
        from compiler_relocation import unpack_ap20
        from build_m19_p28_r88_in_memory import build as build_r88
        historical=(root/"dist/experimental/AMOSPro_AGA_R87_v0.13.32_M19_P25_BC_PASS.Lib").read_bytes()
        assert len(historical)==73184 and sha256(historical).hexdigest()==R87_SHA, "R87 predecessor archive changed"
        candidate,meta=build_r88()
        assert cur==candidate and len(cur)==75040 and meta["sha256"]==R88_SHA, "R88 active differs from pinned builder"
        assert len(good)==67904 and sha256(good).hexdigest()==R84_SHA and cur!=good
        _,segments,title=unpack_ap20(cur)
        assert len(segments)==88 and tuple(map(len,segments[84:]))==(5558,2508,7038,56580), "R88 native unit layout differs"
        assert b"R88 v0.13.33" in title
        audit=inspect(parse(cur))
        assert not audit["issues"],audit["issues"]
        names=[x["name"] for x in audit["tokens"]]
        assert "aga cache blit" in names and "aga bob batch" in names and "aga bob probe" not in names
        assert len([x for x in names if x.startswith("aga ")])==78
        return cur,good,"R88 v0.13.33 M19 P2.8 AGPC masked Blitter ACTIVE CANDIDATE: MC68020 Gate A PASS; WinUAE Runtime B / Compiled C NOT TESTED; R84 LAST_GOOD protected"
    if current_sha == R87_SHA:
        # Pinned R87 candidate, reconstructed byte-exact from protected R84.
        from compiler_relocation import unpack_ap20
        from build_m19_p25_no_probe import build as build_r87
        image,meta=build_r87()
        assert cur==image and cur!=good and meta["sha256"]==R87_SHA
        assert len(cur)==73184 and meta["native_units"]["BOBS"]==5220
        assert meta["commands"]==77 and meta["ap20_entries"]==87
        assert sha256(good).hexdigest()==R84_SHA and len(good)==67904
        _,segments,title=unpack_ap20(cur)
        assert len(segments)==87
        assert tuple(map(len,segments[83:])) == (
            5558,2508,meta["native_units"]["BOBS"],56580)
        assert b"R87 v0.13.32" in title
        audit=inspect(parse(cur))
        assert not audit["issues"],audit["issues"]
        names=[x["name"] for x in audit["tokens"]]
        assert "aga bob probe" not in names and "aga bob batch" in names
        assert len([x for x in names if x.startswith("aga ")])==77
        return cur,good,"R87 v0.13.32 M19 P2.5 BOBS native Batch without diagnostic probe: MC68020 Gate A 9/9 PASS; WinUAE Runtime B / Compiled C NOT TESTED; R84 LAST_GOOD protected"
    if current_sha == R86_SHA:
        from compiler_relocation import unpack_ap20
        from build_m19_p23_bob_batch import build as build_r86
        image,meta=build_r86()
        assert cur==image and cur!=good and meta["sha256"]==R86_SHA
        assert len(cur)==73232 and meta["commands"]==78 and meta["ap20_entries"]==88
        assert sha256(good).hexdigest()==R84_SHA and len(good)==67904
        _,segments,title=unpack_ap20(cur)
        assert len(segments)==88 and tuple(map(len,segments[84:]))==(5558,2508,5226,56580)
        assert b"R86 v0.13.31" in title
        audit=inspect(parse(cur))
        assert not audit["issues"], audit["issues"]
        assert len([row for row in audit["tokens"] if row["name"].startswith("aga ")])==78
        return cur,good,"R86 v0.13.31 M19 P2.3 BOBS native Batch: MC68020 Gate A PASS, WinUAE Runtime B / Compiled C PASS on author test logs (13/13 ticks, no speedup demonstrated); R84 LAST_GOOD protected"
    if current_sha == R85_SHA:
        from compiler_relocation import unpack_ap20
        from build_m19_p22_fourth_unit_probe import build as build_r85
        image,meta=build_r85()
        assert cur==image and cur!=good and meta["sha256"]==R85_SHA
        assert len(cur)==67988 and meta["commands"]==77 and meta["ap20_entries"]==87
        assert sha256(good).hexdigest()==R84_SHA and len(good)==67904
        _,segments,title=unpack_ap20(cur)
        assert len(segments)==87 and tuple(map(len,segments[83:]))==(5558,2508,40,56580)
        assert b"R85 v0.13.30" in title and b"TEST ONLY" in title
        audit=inspect(parse(cur))
        assert not audit["issues"], audit["issues"]
        assert len([row for row in audit["tokens"] if row["name"].startswith("aga ")])==77
        return cur,good,"R85 v0.13.30 M19 P2.2 EXPERIMENTAL FOUR-UNIT BOBS PROBE: native MC68020 Gate A PASS; WinUAE Runtime B, AMOS Compiler C, physical D NOT TESTED; R84 LAST_GOOD protected"
    if current_sha == R84_SHA:
        from compiler_relocation import unpack_ap20
        from build_aga_r84_agapic import build as build_r84
        expected, meta=build_r84()
        assert cur==expected and meta["sha256"]==R84_SHA, "R84 binary differs from pinned native builder"
        assert len(cur)==67904 and meta["bytes"]==67904
        assert meta["commands"]==76 and meta["ap20_entries"]==85
        assert cur==good and sha256(good).hexdigest()==R84_SHA and len(good)==67904, "Promoted R84 LAST_GOOD must match active exactly"
        tok, seg, title=unpack_ap20(cur)
        assert len(seg)==85 and tuple(map(len,seg[82:]))==meta["units"]
        assert b"R84 v0.13.29" in title and b"TEST ONLY" not in title
        report=inspect(parse(cur))
        assert not report["issues"],report["issues"]
        assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==76, "R84 API changed"
        return cur,good,"R84 v0.13.29 AGAPIC v1/v2 PROMOTED LAST_GOOD: native Gate A CPU/CI PASS; WinUAE AMOS Compiler C PASS (with a compiled bank); corrected Runtime B NOT separately evidenced; Gate D physical untested"
    if current_sha == R83_SHA:
        from compiler_relocation import unpack_ap20
        tok, seg, title = unpack_ap20(cur)
        assert len(cur)==64188 and len(seg)==83, "R83 layout changed"
        assert [len(seg[i]) for i in (80,81,82)]==[5558,2508,52974], "R83 native unit sizes changed"
        assert b"R83 v0.13.28" in title and b"TEST ONLY" not in title, "Wrong R83 title"
        report=inspect(parse(cur))
        assert not report["issues"],report["issues"]
        assert len([x for x in report["tokens"] if x["name"].startswith("aga ")])==74, "R83 public API changed"
        from build_aga_r83_modular import build as build_r83
        expected, meta=build_r83()
        assert cur==expected and meta["sha256"]==R83_SHA, "R83 binary differs from deterministic builder"
        assert sha256(good).hexdigest()==R84_SHA, "R84 LAST_GOOD protected; historical R83 rebuilt independently"
        return cur,good,"R83 v0.13.28 HISTORICAL former LAST_GOOD; Gates A CPU/CI, B Runtime and C Compiler PASS on its own 68030 test; physical D and strict PRG_STATE 0 untested"
    if current_sha == P5_EXPERIMENT_SHA:
        raise AssertionError("Historical P5 TEST ONLY cannot be installed as main active binary")
    if current_sha in (R58_SHA, R59_SHA, R60_SHA, R61_SHA, R62_SHA, R63_SHA, R64_SHA, R65_SHA, R66_SHA, R67_SHA, R68_SHA, R69_SHA, R70_SHA, R71_SHA, R72_SHA, R73_SHA, R74_SHA, R75_SHA, R76_SHA, R77_SHA, R78_SHA, R79_SHA, R80_SHA, R81_SHA, R82_SHA):
        from compiler_bridge_v2_probe import is_v2_wrapped
        assert is_v2_wrapped(cur), "R58/R59/R60 must use audited V2 Compiler bridge"
    else:
        assert is_compiler_wrapped(cur), "Active library must be Compiler-safe"
    report=inspect(parse(cur))
    assert not report["issues"],report["issues"]
    if current_sha==R70_SHA:
        # Fail closed: exact SHA/structural CI cannot override a fatal WinUAE
        # illegal instruction. Keep the P2 builder in memory until fixed.
        raise AssertionError("R70 FAILED WinUAE Gate B (Guru $80000004); restore the pinned R69 working library")
    if current_sha==R82_SHA:
        from build_agapic_v2_r82_full_preview import build as build_r82
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from build_c2p_r76_rpg_fix import state_offset,SITES
        from native_relative_links import assert_native_links
        from c2p_r74_relink import check_cross_r74
        candidate,meta=build_r82()
        assert cur==candidate==good,"Promoted R82 must equal active, LAST_GOOD and deterministic builder"
        assert sha256(good).hexdigest()==R82_SHA
        assert len(cur)==64112 and meta["commands"]==74 and meta["ap20_entries"]==81
        assert meta["monolith_bytes"]==60972 and meta["compiler_margin"]==4562
        _,parts=unwrap_native_parts_v2(cur)
        assert len(parts)==80 and state_offset(parts)==12070
        assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                   for i,pos,op in SITES),"R82 keyboard/mouse LEA drift"
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert len([t for t in report["tokens"] if t["name"].startswith("aga ")])==74
        return cur,good,"R82 0.13.27 AGAPIC v2 PROMOTED LAST_GOOD; native A PASS; WinUAE Runtime B PASS; Compiler C PASS; physical D NOT TESTED; pure PRG_STATE 0 not evidenced"
    if current_sha==R81_SHA:
        from build_c2p_r81_opt020 import build as build_r81
        from build_c2p_r76_rpg_fix import SITES, state_offset
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        from c2p_r74_relink import check_cross_r74
        candidate,meta=build_r81()
        _,parts=unwrap_native_parts_v2(cur)
        assert cur==candidate,"Historical R81 must equal deterministic MC68020 builder"
        assert len(cur)==59972 and meta["commands"]==70 and meta["ap20_entries"]==77
        assert len(parts)==76 and state_offset(parts)==12070
        assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                   for i,pos,op in SITES),"R81 7 LEA input-state regression"
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert sha256(good).hexdigest()==LAST_GOOD_SHA
        return cur,good,"R81 0.13.26 historical former LAST_GOOD; native A PASS; Runtime B PASS; Compiler C PASS; physical D NOT TESTED"
    if current_sha==R80_SHA:
        from build_c2p_r80_iff_chunky import build as build_r80
        from build_c2p_r76_rpg_fix import SITES, state_offset
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        from c2p_r74_relink import check_cross_r74
        candidate,meta=build_r80()
        _,parts=unwrap_native_parts_v2(cur)
        assert cur==candidate and cur!=good,"R80 must equal SHA-pinned native builder"
        assert len(cur)==59708 and meta["commands"]==70 and meta["ap20_entries"]==77
        assert len(parts)==76 and state_offset(parts)==12070
        assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                   for i,pos,op in SITES),"R80 7 LEA input-state regression"
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert sha256(good).hexdigest()==LAST_GOOD_SHA
        return cur,good,"R80 0.13.25 IFF to Chunky candidate; native Gate A CPU PASS; Runtime 68030 Gate B PASS (8 planes); Compiler C NOT REQUESTED"
    if current_sha==R79_SHA:
        from build_c2p_r79_zoom import build as build_r79
        from build_c2p_r76_rpg_fix import SITES,state_offset
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        from c2p_r74_relink import check_cross_r74
        candidate,meta=build_r79()
        _,parts=unwrap_native_parts_v2(cur)
        assert cur==candidate and cur!=good,"R79 must match exact append-only builder"
        assert len(cur)==57344 and meta["commands"]==69 and meta["ap20_entries"]==76
        assert len(parts)==75 and state_offset(parts)==12070
        assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                   for i,pos,op in SITES),"R79 mouse/key LEA regression"
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert sha256(good).hexdigest()==LAST_GOOD_SHA
        return cur,good,"R79 0.13.24 C2P Zoom candidate; native CPU pixel Gate A PASS (62); WinUAE Gate B NOT TESTED; R73 LAST_GOOD protected"
    if current_sha==R78_SHA:
        from build_c2p_r78_blit import build as build_r78
        from build_c2p_r76_rpg_fix import SITES,state_offset
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        from c2p_r74_relink import check_cross_r74
        candidate,meta=build_r78()
        _,parts=unwrap_native_parts_v2(cur)
        assert cur==candidate and cur!=good, "R78 must match byte-exact builder"
        assert len(cur)==55772 and meta["commands"]==68 and meta["ap20_entries"]==75
        assert len(parts)==74 and state_offset(parts)==12070
        assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                   for i,pos,op in SITES),"R78 keyboard LEA regression"
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert sha256(good).hexdigest()==LAST_GOOD_SHA
        return cur,good,"R78 0.13.23 C2P Blit candidate; native CPU pixel Gate A PASS; WinUAE Gate B NOT TESTED; R73 LAST_GOOD protected"
    if current_sha==R77_SHA:
        from build_c2p_r77_close import build as build_r77
        from build_c2p_r76_rpg_fix import SITES,state_offset
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        from c2p_r74_relink import check_cross_r74
        candidate,meta=build_r77()
        _,parts=unwrap_native_parts_v2(cur)
        assert cur==candidate and cur!=good,"R77 must match exact source with R73 protected"
        assert len(cur)==54360 and meta["commands"]==67 and meta["ap20_entries"]==74
        assert len(parts)==73 and state_offset(parts)==12070
        assert all(parts[i][pos:pos+4]==op.to_bytes(2,"big")+bytes.fromhex("2f26")
                   for i,pos,op in SITES),"R77 input LEA regression"
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert sha256(good).hexdigest()==LAST_GOOD_SHA
        return cur,good,"R77 0.13.22 C2P Close candidate; native Gate A PASS; WinUAE Gate B NOT TESTED; R73 LAST_GOOD protected"
    if current_sha==R76_SHA:
        from build_c2p_r76_rpg_fix import build as build_r76, SITES, state_offset
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from c2p_r74_relink import check_cross_r74
        from native_relative_links import assert_native_links
        candidate,meta=build_r76()
        _,parts=unwrap_native_parts_v2(cur)
        assert cur==candidate and cur!=good, "R76 active must match exact native rebuilt source"
        assert len(cur)==54144 and meta["commands"]==66 and meta["ap20_entries"]==73
        assert len(parts)==72 and state_offset(parts)==12070
        assert all(parts[i][pos+2:pos+4]==bytes.fromhex("2f26") for i,pos,_ in SITES)
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert sha256(good).hexdigest()==LAST_GOOD_SHA, "R73 LAST_GOOD changed"
        return cur,good,"R76 0.13.21 C2P Open+Convert RPG mouse state fix; native Gate A PASS; WinUAE B/C NOT TESTED; R73 LAST_GOOD protected"
    if current_sha==R75_SHA:
        from build_c2p_r75_convert import build as build_r75
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from c2p_r74_relink import check_cross_r74
        from c2p_r75_convert_emit import emit_convert
        from native_relative_links import assert_native_links
        candidate,meta=build_r75()
        _,parts=unwrap_native_parts_v2(cur)
        assert cur==candidate and cur!=good, "R75 must match its byte-pinned builder"
        assert len(cur)==54144 and meta["commands"]==66 and meta["ap20_entries"]==73
        assert len(parts)==72 and parts[71]==emit_convert()[0]
        assert_native_links(parts[:70]);check_cross_r74(parts[:70])
        assert sha256(good).hexdigest()==LAST_GOOD_SHA, "R73 LAST_GOOD changed"
        return cur,good,"R75 0.13.20 C2P Open+Convert 4-8 planes candidate; native Gate A PASS; WinUAE B/C NOT TESTED; R73 LAST_GOOD protected"
    if current_sha==R74_SHA:
        from build_c2p_r74_open import build as build_r74
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        from c2p_r74_relink import check_cross_r74
        candidate,meta=build_r74()
        tokens,parts=unwrap_native_parts_v2(cur)
        assert cur==candidate and cur!=good, "R74 must match its builder, not promoted R73"
        assert len(cur)==52612 and meta["commands"]==65 and meta["ap20_entries"]==72
        assert len(parts)==71
        assert_native_links(parts[:70]);check_cross_r74(parts)
        assert sha256(good).hexdigest()==LAST_GOOD_SHA, "R73 LAST_GOOD changed"
        return cur,good,"R74 0.13.19 C2P Open 4-8 bitplanes candidate; native Gate A pending; WinUAE B/C NOT TESTED; R73 LAST_GOOD protected"
    if current_sha==R73_SHA:
        from build_opt020_p3_r73 import build as build_r73
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        candidate, meta = build_r73()
        assert cur == candidate == good, "Promoted R73 must match current, LAST_GOOD and its deterministic builder"
        assert len(cur)==51608 and meta["ap20_entries"]==71 and meta["commands"]==64
        assert meta["changed_native"]==[60,66]
        assert_native_links(unwrap_native_parts_v2(cur)[1])
        assert sha256(good).hexdigest()==R73_SHA
        return cur,good,"R73 0.13.18 OPT020/P3 Fast Icon CAP+DRAW CPU020 PROMOTED LAST_GOOD; Gates A/B/C PASS, D physical untested"
    if current_sha==R72_SHA:
        from build_opt020_p2_r72 import build as build_r72
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        candidate, meta = build_r72()
        assert cur == candidate and cur != good, "R72 differs from deterministic builder"
        assert len(cur) == 51468 and meta["ap20_entries"] == 71 and meta["commands"] == 64
        assert_native_links(unwrap_native_parts_v2(cur)[1])
        assert sha256(good).hexdigest() == LAST_GOOD_SHA
        return cur, good, "R72 0.13.17 OPT020/P2 late D3 fixed; Gates A/B interpreted PASS; Compiler C NOT TESTED"
    if current_sha==R71_SHA:
        from build_opt020_p2_r71 import build as build_r71
        from compiler_bridge_v2_probe import unwrap_native_parts_v2
        from native_relative_links import assert_native_links
        candidate, meta = build_r71()
        assert cur == candidate and cur != good, "R71 differs from deterministic builder"
        assert len(cur) == 51460 and meta["ap20_entries"] == 71 and meta["commands"] == 64
        assert_native_links(unwrap_native_parts_v2(cur)[1])
        assert sha256(good).hexdigest() == LAST_GOOD_SHA
        return cur, good, "R71 0.13.16 OPT020/P2 repaired links; Gate A/CI candidate, WinUAE B and Compiler C NOT TESTED"
    if current_sha==R69_SHA:
        from build_opt020_p1e_r69 import build as build_r69
        candidate,meta=build_r69()
        assert cur == candidate and cur != good, "R69 active differs from exact builder"
        assert sha256(good).hexdigest() == LAST_GOOD_SHA, "Promoted LAST_GOOD protection lost"
        assert len(cur) == 51240 and meta["ap20_entries"] == 71 and meta["commands"] == 64
        return cur,good,"R69 0.13.14 OPT020/P1e tested candidate; Gate B and interpreted/compiled Region benchmarks PASS"
    if current_sha==R68_SHA:
        from build_m18_r68_cblock import build as build_r68
        candidate,meta=build_r68()
        assert candidate==cur and sha256(good).hexdigest()==LAST_GOOD_SHA
        assert len(cur)==51064 and meta["commands"]==64 and meta["ap20_entries"]==71
        return cur,good,"R68 0.13.13 historical CBlock; Gates A/B/C PASS, D physical untested"
    if current_sha==R67_SHA:
        from build_m18_r67_ficon_capture import build as build_r67
        candidate,meta=build_r67()
        assert candidate==cur and cur!=good and sha256(good).hexdigest()==R63_SHA, (
            "R67 candidate differs from exact builder or R63 LAST_GOOD changed")
        return cur,good,"R67 0.13.12 FICON8 screen Capture Gate A 240 CPU PASS; WinUAE B pending, Compiler C end M18"
    if current_sha==R66_SHA:
        from build_m18_r66_fichip_dynamic import build as build_r66
        candidate,meta=build_r66()
        assert candidate==cur and cur!=good and sha256(good).hexdigest()==R63_SHA, (
            "R66 must match its deterministic builder and preserve R63 LAST_GOOD")
        return cur,good,"R66 0.13.11 Chip Cache Create+Stage Gate A 122 CPU PASS; WinUAE B pending, Compiler C end M18"
    if current_sha==R65_SHA:
        from build_m18_r65_ficon_bank_put import build as build_r65
        candidate,meta=build_r65()
        assert candidate==cur and cur!=good and sha256(good).hexdigest()==R63_SHA, (
            "R65 candidate must match pinned builder and preserve R63 LAST_GOOD")
        return cur,good,"R65 0.13.10 FICON8 Bank Put Gates A/B PASS (interpreted+visual), Compiler C end M18"
    if current_sha==R64_SHA:
        from build_m18_r64_ficon_bank_create import build as build_r64
        candidate,meta=build_r64()
        assert candidate==cur and cur!=good and sha256(good).hexdigest()==R63_SHA, (
            "R64 builder mismatch or protected R63 LAST_GOOD changed")
        return cur,good,"R64 0.13.9 FICON8 Create Gates A/B PASS (interpreted+visual), NOT PROMOTED; Compiler C end M18"
    if current_sha==R63_SHA:
        from build_m18_r63_chip_blit import build as build_r63
        candidate,meta=build_r63()
        assert candidate==cur and cur==good, "Promoted R63 must equal deterministic candidate and LAST_GOOD"
        return cur,good,"R63 0.13.8 M18 Chip masked Blitter PROMOTED LAST_GOOD; A/B PASS, visual pending, C end M18"
    if current_sha==R62_SHA:
        from build_m18_r62_chip_blit import build as build_r62
        candidate,meta=build_r62()
        assert candidate==cur and cur!=good, "R62 must match deterministic builder and preserve R60 LAST_GOOD"
        return cur,good,"R62 0.13.7 M18 masked Chip Blitter Gate A PASS; WinUAE B/C NOT TESTED"
    if current_sha==R61_SHA:
        from build_m18_r61_ficon import build as build_r61
        candidate,meta=build_r61()
        assert candidate==cur and cur!=good, "R61 must be byte-exact to builder and separate from LAST_GOOD"
        return cur,good,"R61 0.13.6 M18 Fast Icon Gate A candidate; WinUAE B/C NOT TESTED"
    if current_sha==R60_SHA:
        assert cur==good, "Promoted R60 LAST_GOOD must match active byte-for-byte"
        return cur,good,"promoted R60 v0.13.5 image region A/B/C + full regression PASS"
    if current_sha==R59_SHA:
        assert cur!=good, "Historical R59 must not replace promoted R60"
        return cur,good,"historical R59 v0.13.4 compact V2"
    if current_sha==R58_SHA:
        assert cur!=good, "R58 must not overwrite promoted R59 LAST_GOOD"
        return cur,good,"R58 0.13.3 V2 Gate A candidate"
    if current_sha==R57_SHA:
        return cur,good,"historical R57 v0.13.2 (not current LAST_GOOD)"
    if sha256(cur).hexdigest()==R56_SHA:
        assert cur!=good,"R56 must not overwrite validated R57 LAST_GOOD"
        return cur,good,"R56 v0.13.1 current Gate A candidate"
    if sha256(cur).hexdigest()==R55_SHA:
        assert cur!=good,"R55 candidate must not overwrite R57 LAST_GOOD"
        return cur,good,"R55 v0.13.0 current Gate A candidate"
    if cur==good:
        r54=(root/"dist/experimental/AMOSPro_AGA_M16_v0.12.9_BANK_NUMBER_R54_CANDIDATE.Lib").read_bytes()
        assert r54==cur,"Promoted R54 differs from immutable 0.12.9 archive"
        return cur,good,"promoted R54 v0.12.9"
    for path,digest in CANDIDATE_HASHES.items():
        p=root/path
        if p.is_file() and sha256(cur).hexdigest()==digest:
            assert p.read_bytes()==cur,("Candidate differs from its immutable archive",path)
            return cur,good,path
    raise AssertionError("Unrecognized active binary; require matching versioned/pinned candidate archive")
