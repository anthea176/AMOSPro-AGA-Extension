"""CPU/static regression for native AMOS Ctrl+C forwarding in R5.

Relocation note: AMOS's AP20 loader rewrites FE11F700008C (Rjsr
L_Test_PaSaut) to JSR absolute.l. The mock applies only that documented
relocation, then executes the real entry bytecode on the 68000 CPU.

A mocked native test proves call/ABI/cleanup order. It cannot prove
the real AMOS editor receives an interruption: runtime test is mandatory.
"""
import hashlib
import json
import struct

from unicorn import UC_HOOK_CODE
from unicorn.m68k_const import UC_M68K_REG_PC

from audit_ap20 import parse, inspect as audit
from build_intuition_input_r5 import (
    build, ROOT, BASE, RJSR_TEST_PASAUT,
    CTRL_OR_FORCED, RESTORE, D2_INT, MOVE_D5_D3,
)
from test_intuition_input_r4 import (
    Machine, input_case, segment,
    AMOS, STATE, STATE_SIZE, STATE_DB, STATE_WINDOW,
    INTUI, EXEC, GFX, DR, AR, RAWKEY_C, RAWKEY_CONTROL,
    IEQUALIFIER_CONTROL, T_ACTUALISE, BITCONTROL_WORD,
    LVO_CLOSESCREEN, LVO_CLOSEWINDOW, LVO_CLOSELIBRARY,
)

NATIVE_ADDR = 0x030000
LINKED_JSR = bytes.fromhex("4eb9") + struct.pack(">I", NATIVE_ADDR)
BITVBL_WORD = 0x8000


def link_for_cpu(seg):
    assert seg.count(RJSR_TEST_PASAUT) == 1
    return seg.replace(RJSR_TEST_PASAUT, LINKED_JSR)


class NativeMachine(Machine):
    def __init__(self, code, events, deferred=None):
        super().__init__(link_for_cpu(code), events, deferred=deferred, strict_close=True)
        self.native_calls = 0
        self.native_snapshots = []
        self.uc.mem_write(NATIVE_ADDR, bytes.fromhex("4e75"))
        self.uc.hook_add(UC_HOOK_CODE, self.native_test, begin=NATIVE_ADDR, end=NATIVE_ADDR)

    def native_test(self, uc, address, size, user):
        assert address == NATIVE_ADDR
        # Entry has already restored registers and D2=integer ABI.
        assert self.d(2) == 0
        assert self.d(3) == RAWKEY_C
        assert self.a(5) == AMOS
        flags = self.getw(AMOS + T_ACTUALISE)
        assert flags & (BITCONTROL_WORD | BITVBL_WORD) == (BITCONTROL_WORD | BITVBL_WORD)
        assert self.close_window_count == 1
        assert self.close_screen_count == 1
        assert self.close_library_count == 2
        assert all(self.get(STATE + off) == 0 for off in range(0, STATE_SIZE, 4))
        assert all(n == 1 for n in self.reply_count.values())
        self.native_calls += 1
        self.native_snapshots.append({
            "break_flag": bool(flags & BITCONTROL_WORD),
            "force_test": bool(flags & BITVBL_WORD),
            "window_closed": self.close_window_count == 1,
            "screen_closed": self.close_screen_count == 1,
        })
        # Simulate only Break Off / return from L_Test_PaSaut. Actual BREAK
        # ON must be checked with the AMOS interpreter and WinUAE.
        sp = self.a(7)
        pc = self.get(sp)
        uc.reg_write(AR[7], sp + 4)
        uc.reg_write(UC_M68K_REG_PC, pc)


def run():
    raw, report = build()
    assert build()[0] == raw
    lib = parse(raw)
    prev = parse(BASE.read_bytes())
    assert audit(lib)["issues"] == []
    assert len(lib.jumps) == len(prev.jumps) == 19
    tests = {}

    for i in range(19):
        a = segment(lib, i)
        b = segment(prev, i)
        if i in (17, 18):
            assert a != b and a.endswith(MOVE_D5_D3 + RESTORE + D2_INT +
                                         RJSR_TEST_PASAUT + bytes.fromhex("4e75"))
            assert a.count(CTRL_OR_FORCED) == 1
            assert len(a) == len(b) + 16
        else:
            assert a == b, ("Unexpected R4 segment change", i)
    tests["all_non_input_segments_unchanged"] = "PASS"
    tests["loader_picinfo_byte_for_byte"] = "PASS"
    tests["official_rjsr_link_marker"] = "PASS"

    wait_key = segment(lib, 18)
    key = segment(lib, 17)

    # Control alone does not exit Wait Key, even if Control qualifier present.
    m = input_case(link_for_cpu(wait_key),
                   [{"code": RAWKEY_CONTROL, "qualifier": IEQUALIFIER_CONTROL}],
                   0x24, False, deferred={"code": 0x24}, waits=1)
    assert m.close_screen_count == 0
    tests["ctrl_alone_waits"] = "PASS"

    # A plain C (without Control qualifier) returns 51, does not break.
    plain = input_case(link_for_cpu(wait_key),
                       [{"code": RAWKEY_C, "qualifier": 0}], RAWKEY_C, False, waits=0)
    assert plain.close_screen_count == 0
    tests["plain_c_no_native_break"] = "PASS"

    # Ctrl then C with correct Intuition qualifier must go through AMOS
    # native test, not only set BitControl and return raw 51.
    for entry_name, entry in (("aga_wait_key", wait_key), ("aga_key", key)):
        m = NativeMachine(entry, [
            {"code": RAWKEY_CONTROL, "qualifier": IEQUALIFIER_CONTROL},
            {"code": RAWKEY_C, "qualifier": IEQUALIFIER_CONTROL},
        ])
        if entry_name == "aga_key":
            # Aga Key returns the first queued raw key (99), unchanged.
            # Poll again in a separate execution with C still queued.
            m = NativeMachine(entry, [{"code": RAWKEY_C,
                                       "qualifier": IEQUALIFIER_CONTROL}])
        m.execute(preserve_public=True)
        assert m.native_calls == 1
        assert m.d(3) == RAWKEY_C
        assert m.d(2) == 0
        assert m.close_window_count == m.close_screen_count == 1
        tests[entry_name + "_native_test_invoked"] = "PASS"

    # Ctrl+key-up+C without control must NOT invoke the native break.
    m = input_case(link_for_cpu(wait_key), [
        {"code": RAWKEY_CONTROL, "qualifier": IEQUALIFIER_CONTROL},
        {"code": RAWKEY_CONTROL | 0x80, "qualifier": 0},
        {"code": RAWKEY_C, "qualifier": 0},
    ], RAWKEY_C, False, waits=0)
    assert m.close_screen_count == 0
    tests["ctrl_release_plain_c"] = "PASS"

    # Test close path remains the same as R4.
    assert segment(lib, 8) == segment(prev, 8)
    assert segment(lib, 0) == segment(prev, 0)
    tests["r3_window_before_screen_fix_kept"] = "PASS"

    out = {
        "candidate_sha256": hashlib.sha256(raw).hexdigest(),
        "candidate_size": len(raw),
        "tests": tests,
        "native_test": "L_Test_PaSaut #140 called with Break and VBL flags set, "
                       "after full AGA cleanup and with restored caller registers.",
        "limitation": "The AMOS Test_PaSaut handler is mocked only. BREAK ON/OFF "
                      "and editor return MUST pass native runtime testing; "
                      "do not report them as CPU-proven.",
    }
    path = ROOT / "docs/INTUITION_INPUT_CPU_TESTS.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    run()
