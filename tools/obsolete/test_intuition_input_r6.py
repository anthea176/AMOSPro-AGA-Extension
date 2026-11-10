"""R6 68000/ABI regression: native AMOS_WB(1) must precede native Ctrl+C Break.

Link AP20 Rjsr L_Test_PaSaut for the simulated CPU (identical strategy to R5).
Mock the graphics dispatcher AMOS_WB=72 (T_EcVect=-8 relative to A5).
The AGA Window/Screen must already be closed before AMOS_To_Front.
All other segments must be byte-identical to the R5 runtime candidate.

This is CPU simulation, NOT native WinUAE validation.
"""
from hashlib import sha256
import json
from unicorn import UC_HOOK_CODE

from build_intuition_input_r6 import build, BASE, ROOT, AMOS_TO_FRONT, R5_BREAK_STUB
from build_intuition_input_r5 import RJSR_TEST_PASAUT
from audit_ap20 import parse, inspect as audit
from test_intuition_input_r5 import NativeMachine
from test_intuition_input_r4 import (
    segment, input_case, AMOS, STATE, STATE_SIZE, AR,
    INTUI, EXEC, DR, RAWKEY_C, RAWKEY_CONTROL,
    IEQUALIFIER_CONTROL, LVO_CLOSEWINDOW, LVO_CLOSESCREEN,
    LVO_CLOSELIBRARY,
)

# Official +Equ.s AMOS_WB=72 and +WEqu.s T_EcVect=-8.
AMOS_ECVECT = AMOS - 8
GFX_VECTOR_TABLE = 0x040000
AMOS_WB_ENTRY = GFX_VECTOR_TABLE + 72 * 4


class FrontMachine(NativeMachine):
    def __init__(self, code, messages):
        super().__init__(code, messages)
        self.put(AMOS_ECVECT, GFX_VECTOR_TABLE)
        self.uc.mem_write(AMOS_WB_ENTRY, bytes.fromhex("4e75"))
        self.front_calls = 0
        self.uc.hook_add(UC_HOOK_CODE, self.on_front, begin=AMOS_WB_ENTRY, end=AMOS_WB_ENTRY)

    def on_front(self, uc, address, size, user):
        assert self.d(1) == 1, "AMOS To Front must pass D1=1"
        assert self.a(0) == GFX_VECTOR_TABLE, "Incorrect T_EcVect"
        assert self.close_window_count == 1
        assert self.close_screen_count == 1
        assert self.close_library_count == 2
        assert not self.queue
        assert all(n == 1 for n in self.reply_count.values())
        self.front_calls += 1
        self.call_sequence.append("AMOS_WB_FRONT")
        # Simulate a volatile library call; public registers MUST be restored
        # by the R5 stub after the graphics dispatcher returns.
        self.return_from_call(0)

    def native_test(self, uc, address, size, user):
        assert self.front_calls == 1, "Break executed before AMOS returned to front"
        assert self.call_sequence.index(INTUI + LVO_CLOSEWINDOW) < self.call_sequence.index(INTUI + LVO_CLOSESCREEN)
        assert self.call_sequence.index(INTUI + LVO_CLOSESCREEN) < self.call_sequence.index("AMOS_WB_FRONT")
        assert self.call_sequence.index(EXEC + LVO_CLOSELIBRARY) < self.call_sequence.index("AMOS_WB_FRONT")
        super().native_test(uc, address, size, user)


def run():
    binary, report = build()
    assert binary == build()[0]
    cur = parse(binary)
    old = parse(BASE.read_bytes())
    assert audit(cur)["issues"] == []
    result = {}

    for i in range(19):
        a,b = segment(cur,i),segment(old,i)
        if i in (17,18):
            assert b.endswith(R5_BREAK_STUB)
            assert a == b[:-16] + AMOS_TO_FRONT + R5_BREAK_STUB
        else:
            assert a == b, ("Unexpected segment delta", i)
    result["r5_non_keyboard_segments_identical"] = "PASS"
    result["ctrl_c_branch_preserved"] = "PASS"
    result["r5_window_screen_cleanup_unchanged"] = "PASS"
    result["generic_ilbm_and_picinfo_unchanged"] = "PASS"

    # Same ordinary key behavior as R5.
    for index in (17,18):
        code = segment(cur,index)
        from test_intuition_input_r5 import link_for_cpu
        plain = input_case(link_for_cpu(code),[{"code":RAWKEY_C,"qualifier":0}],RAWKEY_C,False)
        assert plain.close_screen_count == 0
    result["plain_c_does_not_restore_or_break"] = "PASS"

    for entry in (17,18):
        code = segment(cur,entry)
        events = [{"code":RAWKEY_C,"qualifier":IEQUALIFIER_CONTROL}]
        if entry == 18:
            events.insert(0,{"code":RAWKEY_CONTROL,"qualifier":IEQUALIFIER_CONTROL})
        m = FrontMachine(code,events)
        m.execute(preserve_public=True)
        assert m.front_calls == m.native_calls == 1
        assert m.d(3) == RAWKEY_C and m.d(2) == 0
        assert all(m.get(STATE+offset)==0 for offset in range(0,STATE_SIZE,4))
        result[("aga_key" if entry==17 else "aga_wait_key")+"_front_before_break"] = "PASS"

    from test_intuition_input_r5 import link_for_cpu
    wait = segment(cur,18)
    m = input_case(link_for_cpu(wait),
                   [{"code":RAWKEY_CONTROL,"qualifier":IEQUALIFIER_CONTROL}],
                   0x24,False,deferred={"code":0x24},waits=1)
    assert m.close_screen_count == 0
    result["ctrl_only_waits"] = "PASS"

    result["abi_restored_before_native_break"] = "PASS"
    out={
        "sha256":sha256(binary).hexdigest(),
        "size":len(binary),
        "tests":result,
        "limitation":"Graphics AMOS_WB and AMOS Test_PaSaut mocked, WinUAE runtime must confirm editor front and no orphaned screen.",
    }
    path = ROOT / "docs/INTUITION_INPUT_CPU_TESTS.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return out


if __name__=="__main__":
    run()
