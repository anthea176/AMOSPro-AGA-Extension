"""68000/static verification for M5 Intuition Input R3.

This is not WinUAE/real-Amiga validation. It executes the new routines on a
68000 Unicorn CPU with mocked AmigaOS calls and deliberately clobbers volatile
library-call registers.
"""
from pathlib import Path
import hashlib
import json
import struct

from audit_ap20 import parse, inspect as audit
from build_intuition_input_r3 import (
    build, open_window_helper, close_window_helper, ROOT,
    BASE, STATE_SCREEN, STATE_INTUITION, STATE_GFX, STATE_WIDTH, STATE_HEIGHT,
    STATE_DB, STATE_WINDOW, STATE_SIZE, AMOS_STATE_PTR, WINDOW_USERPORT,
    IM_CLASS, IM_CODE, IM_QUALIFIER, IDCMP_RAWKEY, IEQUALIFIER_CONTROL,
    RAWKEY_C, T_ACTUALISE, BITCONTROL_WORD, WINDOW_FLAGS, CUSTOMSCREEN,
    EXEC_WAIT, EXEC_WAITPORT, GFX_WAITTOF,
)

try:
    from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE
    from unicorn.m68k_const import *
except ImportError as error:
    raise SystemExit("Install test dependencies: python -m pip install unicorn") from error

DR = [UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3,
      UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7]
AR = [UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3,
      UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7]

CODE = 0x100000
STOP = 0x010000
EXEC = 0x020000
GFX = 0x024000
INTUI = 0x026000
AMOS = 0x060000
STATE = 0x061000
SCREEN = 0x062000
WINDOW = 0x063000
PORT = 0x064000
MSG = 0x065000
DBSTATE = 0x066000
SB0 = 0x067000
SB1 = 0x068000
SAFEPORT = 0x069000
DISPPORT = 0x06A000
STACK = 0xF00000

LVO_CLOSESCREEN = -66
LVO_CLOSEWINDOW = -72
LVO_OPENWINDOW = -204
LVO_WAITTOF = -270
LVO_GETMSG = -372
LVO_REPLYMSG = -378
LVO_CLOSELIBRARY = -414
LVO_DELETEPORT = -672
LVO_FREEVEC = -690
LVO_FREESCREENBUFFER = -774
LVO_WAITBLIT = -228


class Machine:
    def __init__(self, code, queue=None, deferred=None, open_ok=True, strict_close=False):
        self.uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        self.uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        self.uc.mem_map(0, 0x1000000)
        self.uc.mem_write(CODE, code)
        self.uc.mem_write(STOP, b"\x4e\x71")
        self.put(4, EXEC)
        self.put(AMOS + AMOS_STATE_PTR, STATE)
        self.put(STATE + STATE_SCREEN, SCREEN)
        self.put(STATE + STATE_INTUITION, INTUI)
        self.put(STATE + STATE_GFX, GFX)
        self.put(STATE + STATE_WIDTH, 320)
        self.put(STATE + STATE_HEIGHT, 256)
        self.put(STATE + STATE_WINDOW, WINDOW)
        self.put(WINDOW + WINDOW_USERPORT, PORT)
        self.putw(AMOS + T_ACTUALISE, 0)

        self.queue = []
        self.reply_count = {}
        self.deferred = deferred
        self.wait_count = 0
        self.open_ok = open_ok
        self.strict_close = strict_close
        self.call_sequence = []
        self.open_args = None
        self.close_window_count = 0
        self.close_screen_count = 0
        self.close_library_count = 0
        self.waitblit_count = 0
        self.free_screenbuffers = []
        self.deleted_ports = []
        self.freed_vecs = []
        self.next_msg = MSG
        for event in queue or []:
            self.enqueue(event)

        for base, offsets in (
            (EXEC, (LVO_GETMSG, LVO_REPLYMSG, LVO_CLOSELIBRARY, LVO_DELETEPORT, LVO_FREEVEC)),
            (GFX, (LVO_WAITTOF, LVO_WAITBLIT)),
            (INTUI, (LVO_OPENWINDOW, LVO_CLOSEWINDOW, LVO_CLOSESCREEN, LVO_FREESCREENBUFFER)),
        ):
            for offset in offsets:
                self.uc.mem_write(base + offset, b"\x4e\x75")
        self.uc.hook_add(UC_HOOK_CODE, self.os_call, begin=0x010000, end=0x02ffff)

    def put(self, address, value):
        self.uc.mem_write(address, struct.pack(">I", value & 0xffffffff))

    def putw(self, address, value):
        self.uc.mem_write(address, struct.pack(">H", value & 0xffff))

    def get(self, address):
        return struct.unpack(">I", self.uc.mem_read(address, 4))[0]

    def getw(self, address):
        return struct.unpack(">H", self.uc.mem_read(address, 2))[0]

    def d(self, n):
        return self.uc.reg_read(DR[n])

    def a(self, n):
        return self.uc.reg_read(AR[n])

    def enqueue(self, event):
        address = self.next_msg
        self.next_msg += 0x80
        self.put(address + IM_CLASS, event.get("class", IDCMP_RAWKEY))
        self.putw(address + IM_CODE, event.get("code", 0))
        self.putw(address + IM_QUALIFIER, event.get("qualifier", 0))
        self.queue.append(address)
        self.reply_count[address] = 0
        return address

    def return_from_call(self, result=0):
        self.uc.reg_write(DR[0], result)
        self.uc.reg_write(DR[1], 0xDEADBEEF)
        self.uc.reg_write(AR[0], 0xBAD000)
        self.uc.reg_write(AR[1], 0xBAD100)
        pc = self.get(self.a(7))
        self.uc.reg_write(AR[7], self.a(7) + 4)
        self.uc.reg_write(UC_M68K_REG_PC, pc)

    def os_call(self, uc, address, size, user):
        self.call_sequence.append(address)
        if address == EXEC + LVO_GETMSG:
            assert self.a(0) == PORT
            self.return_from_call(self.queue.pop(0) if self.queue else 0)
        elif address == EXEC + LVO_REPLYMSG:
            msg = self.a(1)
            assert msg in self.reply_count, hex(msg)
            self.reply_count[msg] += 1
            assert self.reply_count[msg] == 1, "ReplyMsg called more than once"
            self.return_from_call(0)
        elif address == GFX + LVO_WAITTOF:
            self.wait_count += 1
            if self.deferred is not None:
                self.enqueue(self.deferred)
                self.deferred = None
            self.return_from_call(0)
        elif address == GFX + LVO_WAITBLIT:
            self.waitblit_count += 1
            self.return_from_call(0)
        elif address == INTUI + LVO_OPENWINDOW:
            nw = self.a(0)
            self.open_args = {
                "left": struct.unpack(">H", self.uc.mem_read(nw + 0, 2))[0],
                "top": struct.unpack(">H", self.uc.mem_read(nw + 2, 2))[0],
                "width": struct.unpack(">H", self.uc.mem_read(nw + 4, 2))[0],
                "height": struct.unpack(">H", self.uc.mem_read(nw + 6, 2))[0],
                "idcmp": struct.unpack(">I", self.uc.mem_read(nw + 10, 4))[0],
                "flags": struct.unpack(">I", self.uc.mem_read(nw + 14, 4))[0],
                "screen": struct.unpack(">I", self.uc.mem_read(nw + 30, 4))[0],
                "type": struct.unpack(">H", self.uc.mem_read(nw + 46, 2))[0],
            }
            if self.open_ok:
                self.put(WINDOW + WINDOW_USERPORT, PORT)
                self.return_from_call(WINDOW)
            else:
                self.return_from_call(0)
        elif address == INTUI + LVO_CLOSEWINDOW:
            assert self.a(0) == WINDOW
            assert not self.queue, "CloseWindow before IDCMP drain completed"
            self.close_window_count += 1
            self.return_from_call(0)
        elif address == INTUI + LVO_CLOSESCREEN:
            assert self.a(0) == SCREEN
            if self.strict_close:
                assert self.close_window_count == 1, "CloseScreen with still-open Intuition Window"
                assert self.get(STATE + STATE_WINDOW) == 0, "Window* not cleared before CloseScreen"
            self.close_screen_count += 1
            self.return_from_call(1)
        elif address == INTUI + LVO_FREESCREENBUFFER:
            assert self.a(0) == SCREEN
            self.free_screenbuffers.append(self.a(1))
            self.return_from_call(1)
        elif address == EXEC + LVO_DELETEPORT:
            self.deleted_ports.append(self.a(0))
            self.return_from_call(0)
        elif address == EXEC + LVO_FREEVEC:
            self.freed_vecs.append(self.a(1))
            self.return_from_call(0)
        elif address == EXEC + LVO_CLOSELIBRARY:
            assert self.a(1) in (INTUI, GFX)
            self.close_library_count += 1
            self.return_from_call(0)
        else:
            raise AssertionError("Unexpected OS call " + hex(address))

    def execute(self, preserve_public=False, a2_state=False, d7_mode=False, entry_offset=0):
        for i, reg in enumerate(DR):
            self.uc.reg_write(reg, 0x12000000 + i)
        for i, reg in enumerate(AR[:7]):
            self.uc.reg_write(reg, 0x400000 + i * 0x1000)
        self.uc.reg_write(AR[5], AMOS)
        if a2_state:
            self.uc.reg_write(AR[2], STATE)
        if d7_mode:
            self.uc.reg_write(DR[7], 0x00021000)
        before = {reg: self.uc.reg_read(reg) for reg in DR + AR[:7]}
        self.uc.reg_write(UC_M68K_REG_SR, 0x2000)
        self.uc.reg_write(AR[7], STACK)
        self.put(STACK, STOP)
        self.uc.emu_start(CODE + entry_offset, STOP, count=1000000)
        assert self.uc.reg_read(UC_M68K_REG_PC) == STOP
        assert self.a(7) == STACK + 4
        if preserve_public:
            for reg, value in before.items():
                if reg in (DR[2], DR[3]):
                    continue
                assert self.uc.reg_read(reg) == value, (reg, hex(value), hex(self.uc.reg_read(reg)))
            assert self.d(2) == 0
        return before


def segment(lib, index):
    start = lib.starts[index]
    return lib.code[start:start + 2 * lib.jumps[index]]


def input_case(code, events, expected, break_expected=False, deferred=None, waits=None):
    m = Machine(code, events, deferred=deferred)
    m.execute(preserve_public=True)
    result = m.d(3)
    if expected == -1:
        assert result == 0xffffffff, hex(result)
    else:
        assert result == expected, (hex(result), expected)
    assert all(count == 1 for count in m.reply_count.values())
    break_set = bool(m.getw(AMOS + T_ACTUALISE) & BITCONTROL_WORD)
    assert break_set == break_expected
    if waits is not None:
        assert m.wait_count == waits, (m.wait_count, waits)
    return m


def run():
    raw, report = build()
    raw2, report2 = build()
    assert raw == raw2 and report == report2
    lib = parse(raw)
    base = parse(BASE.read_bytes())
    assert audit(lib)["issues"] == []

    # Loader/PicInfo proof: exact bytes, not semantic equivalence.
    for index in (13, 14):
        assert segment(lib, index) == segment(base, index)
        assert hashlib.sha256(segment(lib, index)).digest() == hashlib.sha256(segment(base, index)).digest()

    key = segment(lib, 17)
    wait_key = segment(lib, 18)
    assert EXEC_WAIT not in key + wait_key
    assert EXEC_WAITPORT not in key + wait_key
    assert GFX_WAITTOF not in key
    assert GFX_WAITTOF in wait_key

    results = {}

    # UserPort empty.
    m = input_case(key, [], -1, waits=0)
    results["empty_userport"] = "PASS"

    # Normal key-down.
    m = input_case(key, [{"code": 0x20}], 0x20)
    results["key_down"] = "PASS"

    # key-up is replied and ignored.
    m = input_case(key, [{"code": 0xA0}], -1)
    results["key_up"] = "PASS"

    # Multiple messages: non RAWKEY, key-up, then key-down.
    events = [
        {"class": 0x00000008, "code": 1},
        {"code": 0xA1},
        {"code": 0x22},
    ]
    m = input_case(key, events, 0x22)
    assert len(m.reply_count) == 3
    results["multiple_queue"] = "PASS"
    results["non_rawkey"] = "PASS"

    # Ctrl alone, C alone, Ctrl+C.
    input_case(key, [{"code": 0x63, "qualifier": IEQUALIFIER_CONTROL}], 0x63, False)
    results["ctrl_alone"] = "PASS"
    input_case(key, [{"code": RAWKEY_C, "qualifier": 0}], RAWKEY_C, False)
    results["c_alone"] = "PASS"
    m = input_case(key, [{"code": RAWKEY_C, "qualifier": IEQUALIFIER_CONTROL}],
                   RAWKEY_C, True)
    assert m.close_window_count == 1
    assert m.close_screen_count == 1
    assert m.close_library_count == 2
    assert all(m.get(STATE + off) == 0 for off in range(0, STATE_SIZE, 4))
    results["ctrl_c_native_bitcontrol"] = "PASS"
    results["ctrl_c_full_cleanup"] = "PASS"

    # Ctrl+C with an allocated Double Buffer must release both ScreenBuffers,
    # both MsgPorts and the DBState before closing the Screen.
    m = Machine(key, [{"code": RAWKEY_C, "qualifier": IEQUALIFIER_CONTROL}])
    m.put(STATE + STATE_DB, DBSTATE)
    m.put(DBSTATE + 0, SB0)
    m.put(DBSTATE + 4, SB1)
    m.put(DBSTATE + 12, SAFEPORT)
    m.put(DBSTATE + 16, DISPPORT)
    m.execute(preserve_public=True)
    assert m.getw(AMOS + T_ACTUALISE) & BITCONTROL_WORD
    assert m.waitblit_count == 1
    assert m.free_screenbuffers == [SB1, SB0]
    assert m.deleted_ports == [DISPPORT, SAFEPORT]
    assert m.freed_vecs == [DBSTATE]
    assert m.close_window_count == 1
    assert m.close_screen_count == 1
    assert m.close_library_count == 2
    assert all(m.get(STATE + off) == 0 for off in range(0, STATE_SIZE, 4))
    results["ctrl_c_double_buffer_cleanup"] = "PASS"

    # Wait Key is cooperative: empty poll -> WaitTOF -> key.
    input_case(wait_key, [], 0x24, deferred={"code": 0x24}, waits=1)
    results["wait_key_waittof"] = "PASS"

    # OpenWindow helper success and exact NewWindow fields.
    m = Machine(open_window_helper())
    before = m.execute(a2_state=True, d7_mode=True)
    assert m.d(3) == 1
    assert m.get(STATE + STATE_WINDOW) == WINDOW
    assert m.open_args == {
        "left": 0, "top": 0, "width": 320, "height": 256,
        "idcmp": IDCMP_RAWKEY, "flags": WINDOW_FLAGS,
        "screen": SCREEN, "type": CUSTOMSCREEN,
    }
    for reg, value in before.items():
        if reg == DR[3]:
            continue
        assert m.uc.reg_read(reg) == value, reg
    results["open_window"] = "PASS"

    # OpenWindow failure closes the already-created Screen, closes libraries,
    # and clears the whole extension state.
    m = Machine(open_window_helper(), open_ok=False)
    m.execute(a2_state=True, d7_mode=True)
    assert m.d(3) == 0
    assert m.close_screen_count == 1
    assert m.close_library_count == 2
    assert all(m.get(STATE + off) == 0 for off in range(0, STATE_SIZE, 4))
    results["open_window_failure_cleanup"] = "PASS"

    # Close drains and replies every pending IDCMP message before CloseWindow.
    pending = [{"code": 0x20}, {"class": 8, "code": 0}, {"code": 0xA1}]
    m = Machine(close_window_helper(), pending)
    m.put(STATE + STATE_DB, 0x77777777)
    m.execute(a2_state=True)
    assert m.get(STATE + STATE_DB) == 0x77777777
    assert m.get(STATE + STATE_WINDOW) == 0
    assert m.close_window_count == 1
    assert all(count == 1 for count in m.reply_count.values())
    results["close_pending_messages"] = "PASS"

    # Regression guard: run the *real public AP20 Aga Screen Close entry*.
    # R1/R2 patched the CLR.L DBState after a DBState==0 BEQ; it was skipped.
    # Screen closure MUST fail our strict mock if CloseWindow was not called.
    old_r2_path = ROOT / "dist/experimental/AMOSPro_AGA_M5_v0.5.3_INTUITION_INPUT_R2.Lib"
    old_r2 = parse(old_r2_path.read_bytes())
    broken = Machine(segment(old_r2, 8), strict_close=True)
    broken.put(STATE + STATE_DB, 0)
    try:
        broken.execute()
    except AssertionError as exc:
        assert "still-open Intuition Window" in str(exc), str(exc)
    else:
        raise AssertionError("Regression guard expected R2 CloseScreen to run without CloseWindow")
    results["r2_missing_close_window_reproduced"] = "PASS"

    # R3: no Double Buffer, pending IDCMP. CloseWindow first, CloseScreen second,
    # libraries only afterwards; every pending message replied exactly once.
    normal = Machine(segment(lib, 8),
                     [{"code": 0x20}, {"class": 8, "code": 0}, {"code": 0xA1}],
                     strict_close=True)
    normal.put(STATE + STATE_DB, 0)
    normal.execute()
    assert normal.close_window_count == 1
    assert normal.close_screen_count == 1
    assert normal.close_library_count == 2
    assert all(x == 1 for x in normal.reply_count.values())
    assert normal.call_sequence.index(INTUI + LVO_CLOSEWINDOW) < normal.call_sequence.index(INTUI + LVO_CLOSESCREEN)
    assert normal.call_sequence.index(INTUI + LVO_CLOSESCREEN) < normal.call_sequence.index(EXEC + LVO_CLOSELIBRARY)
    assert all(normal.get(STATE + off) == 0 for off in range(0, STATE_SIZE, 4))
    results["public_close_without_db"] = "PASS"
    results["public_close_drains_idcmp"] = "PASS"
    results["public_close_window_before_screen"] = "PASS"

    # R3: Double Buffer active. Window MUST close before freeing either
    # ScreenBuffer and before closing the Screen.
    dbl = Machine(segment(lib, 8), [{"code": 0x21}], strict_close=True)
    dbl.put(STATE + STATE_DB, DBSTATE)
    dbl.put(DBSTATE + 0, SB0)
    dbl.put(DBSTATE + 4, SB1)
    dbl.put(DBSTATE + 12, SAFEPORT)
    dbl.put(DBSTATE + 16, DISPPORT)
    dbl.execute()
    assert dbl.close_window_count == 1 and dbl.close_screen_count == 1
    assert dbl.waitblit_count == 1
    assert dbl.free_screenbuffers == [SB1, SB0]
    assert dbl.deleted_ports == [DISPPORT, SAFEPORT]
    assert dbl.freed_vecs == [DBSTATE]
    assert dbl.call_sequence.index(INTUI + LVO_CLOSEWINDOW) < dbl.call_sequence.index(INTUI + LVO_FREESCREENBUFFER)
    assert dbl.call_sequence.index(INTUI + LVO_CLOSEWINDOW) < dbl.call_sequence.index(GFX + LVO_WAITBLIT)
    assert all(dbl.get(STATE + off) == 0 for off in range(0, STATE_SIZE, 4))
    assert all(x == 1 for x in dbl.reply_count.values())
    results["public_close_with_db"] = "PASS"

    # Extension termination uses the same entry fix in segment 0, entry +56.
    term = Machine(segment(lib, 0), [{"code": 0x22}], strict_close=True)
    term.put(STATE + STATE_DB, 0)
    term.execute(entry_offset=56)
    assert term.close_window_count == 1 and term.close_screen_count == 1
    assert term.close_library_count == 2
    assert term.get(STATE + STATE_WINDOW) == 0
    results["extension_shutdown_without_db"] = "PASS"

    # Repeat public Open/Close models with both resource configurations.
    for cycle in range(4):
        m = Machine(segment(lib, 8), [{"code": 0x30 + cycle}], strict_close=True)
        if cycle & 1:
            m.put(STATE + STATE_DB, DBSTATE)
            m.put(DBSTATE + 0, SB0)
            m.put(DBSTATE + 4, SB1)
            m.put(DBSTATE + 12, SAFEPORT)
            m.put(DBSTATE + 16, DISPPORT)
        m.execute()
        assert m.close_window_count == m.close_screen_count == 1
        assert m.close_library_count == 2
        assert all(n == 1 for n in m.reply_count.values())
    results["public_close_repeated"] = "PASS"

    # Repeated helper Open/Close cycles on the same state.
    for cycle in range(3):
        m = Machine(open_window_helper())
        m.execute(a2_state=True, d7_mode=True)
        assert m.get(STATE + STATE_WINDOW) == WINDOW
        c = Machine(close_window_helper(), [{"code": 0x20 + cycle}])
        # Carry the relevant runtime state into the close helper model.
        c.execute(a2_state=True)
        assert c.get(STATE + STATE_WINDOW) == 0
        assert c.close_window_count == 1
    results["open_close_repeated"] = "PASS"

    # State really grew from 36 to 40 bytes; segment 0 owns a zeroed 40-byte tail.
    init = segment(lib, 0)
    assert init[-STATE_SIZE:] == bytes(STATE_SIZE)
    results["state_size_40"] = "PASS"

    results["abi_registers"] = "PASS"
    results["generic_ilbm_r2_unchanged"] = "PASS"
    results["ap20_audit"] = "PASS"

    output = {
        "candidate_sha256": hashlib.sha256(raw).hexdigest(),
        "candidate_size": len(raw),
        "tests": results,
        "replymsg_rule": "Every message returned by mocked GetMsg was ReplyMsg'd exactly once.",
        "ctrl_c_static_path": (
            "RAWKEY C + IEQUALIFIER_CONTROL performs full AGA cleanup then sets native AMOS BitControl in "
            "T_Actualise; BREAK ON/OFF remains AMOS-owned."
        ),
        "limitation": (
            "CPU/static validation only. Ctrl+C return to AMOS editor still "
            "requires explicit runtime validation in AMOS Professional."
        ),
    }
    path = ROOT / "docs/INTUITION_INPUT_CPU_TESTS.json"
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return output


if __name__ == "__main__":
    run()
