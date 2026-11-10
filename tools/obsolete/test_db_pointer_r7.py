#!/usr/bin/env python3
"""R7 Unicorn 68000 test of full AP20 Aga Double Buffer entry.

The R6 copy of the allocator is byte-verified to contain two malformed
MOVEA.L $4A80(A0),A0 instructions; the R7 one must read sb_DBufInfo at +4,
then write Safe/Disp reply ports only inside that allocated DBufInfo.

The test makes real 68000 execution through the full allocator, not just
a helper or a blob-string check, with mocked Exec/Intuition functions.

DO NOT exercise Swap here. Its outstanding Safe/Disp cleanup is a known
separate unresolved defect.
"""
import hashlib
import json

from audit_ap20 import parse, inspect as audit
from build_db_pointer_r7 import (
    build, double_buffer_fixed, old_double_buffer, BAD0, BAD1,
    GOOD0, GOOD1, ROOT, BASE,
)
from test_intuition_input_r1 import (
    Machine, segment, DR, AR, STATE, STATE_DB, STATE_WINDOW, STATE_SIZE,
    SCREEN, INTUI, EXEC, DBSTATE, SB0, SB1, SAFEPORT, DISPPORT,
    LVO_FREESCREENBUFFER,
)
from unicorn import UC_HOOK_MEM_READ

LVO_ALLOCVEC = -684
LVO_CREATEMSGPORT = -666
LVO_ALLOCSCREENBUFFER = -768
DBI0 = 0x0B0000
DBI1 = 0x0B1000
PUBLIC_CLEAR = 0x00010001


class AllocMachine(Machine):
    def __init__(self, code, failure=None):
        super().__init__(code)
        self.failure = failure
        self.ports_created = 0
        self.buffers_created = 0
        self.alloc_count = 0
        self.free_count = 0
        self.invalid_far_reads = []
        self.alloc_order = []
        self.put(SB0 + 4, DBI0)
        self.put(SB1 + 4, DBI1)
        for base, offsets in (
            (EXEC, (LVO_ALLOCVEC, LVO_CREATEMSGPORT)),
            (INTUI, (LVO_ALLOCSCREENBUFFER,)),
        ):
            for offset in offsets:
                self.uc.mem_write(base + offset, bytes.fromhex("4e75"))
        self.uc.hook_add(UC_HOOK_MEM_READ, self.on_read)

    def on_read(self, uc, access, address, size, value, user):
        if address in (SB0 + 0x4A80, SB1 + 0x4A80):
            self.invalid_far_reads.append(address)
            raise AssertionError("Invalid ScreenBuffer +$4A80 dereference")

    def os_call(self, uc, address, size, user):
        if address == EXEC + LVO_ALLOCVEC:
            assert self.d(0) == 24, self.d(0)
            assert self.d(1) == PUBLIC_CLEAR
            self.alloc_count += 1
            self.alloc_order.append("AllocVec")
            self.return_from_call(0 if self.failure == "vec" else DBSTATE)
        elif address == EXEC + LVO_CREATEMSGPORT:
            self.ports_created += 1
            self.alloc_order.append("CreateMsgPort")
            result = SAFEPORT if self.ports_created == 1 else DISPPORT
            if self.failure == "safeport" and self.ports_created == 1:
                result = 0
            if self.failure == "dispport" and self.ports_created == 2:
                result = 0
            self.return_from_call(result)
        elif address == INTUI + LVO_ALLOCSCREENBUFFER:
            assert self.a(0) == SCREEN
            assert self.a(1) == 0
            self.buffers_created += 1
            self.alloc_order.append("AllocScreenBuffer")
            assert self.d(0) == self.buffers_created
            result = SB0 if self.buffers_created == 1 else SB1
            if self.failure == "sb0" and self.buffers_created == 1:
                result = 0
            if self.failure == "sb1" and self.buffers_created == 2:
                result = 0
            if self.failure == "dbi0" and self.buffers_created == 1:
                self.put(SB0 + 4, 0)
            if self.failure == "dbi1" and self.buffers_created == 2:
                self.put(SB1 + 4, 0)
            self.return_from_call(result)
        elif address == EXEC - 690:  # FreeVec on partial allocation failure
            assert self.a(1) == DBSTATE
            self.free_count += 1
            self.alloc_order.append("FreeVec")
            self.return_from_call()
        else:
            super().os_call(uc, address, size, user)


def run():
    data, report = build()
    again, _ = build()
    assert again == data
    lib = parse(data)
    old = parse(BASE.read_bytes())
    assert audit(lib)["issues"] == []
    assert len(lib.jumps) == len(old.jumps) == 19
    tests = {}

    for index in range(19):
        if index == 10:
            assert segment(lib, index) != segment(old, index)
            assert segment(old, index) == old_double_buffer() + b"GetP"
            assert segment(lib, index) == double_buffer_fixed() + b"GetP"
        else:
            assert segment(lib, index) == segment(old, index)
    tests["only_ap20_entry_10_changed"] = "PASS"
    tests["generic_ilbm_r2_and_picinfo_identical"] = "PASS"
    tests["ctrl_c_key_window_close_identical"] = "PASS"

    old_binary = segment(old, 10)
    fixed_binary = segment(lib, 10)
    assert old_binary.count(BAD0) == old_binary.count(BAD1) == 1
    assert fixed_binary.count(GOOD0) == fixed_binary.count(GOOD1) == 1
    assert BAD0 not in fixed_binary and BAD1 not in fixed_binary
    tests["r6_invalid_pointer_opcodes_reproduced"] = "PASS"
    tests["r7_both_dbufinfo_pointers_plus_4"] = "PASS"
    tests["all_local_branches_reassembled"] = "PASS"

    machine = AllocMachine(fixed_binary)
    machine.put(STATE + STATE_DB, 0)
    machine.execute(preserve_public=True)
    assert machine.d(3) == 1, machine.d(3)
    assert machine.d(2) == 0
    assert machine.get(STATE + STATE_DB) == DBSTATE
    assert machine.get(DBSTATE + 0) == SB0
    assert machine.get(DBSTATE + 4) == SB1
    assert machine.get(DBSTATE + 12) == SAFEPORT
    assert machine.get(DBSTATE + 16) == DISPPORT
    assert machine.get(DBI0 + 22) == SAFEPORT
    assert machine.get(DBI0 + 54) == DISPPORT
    assert machine.get(DBI1 + 22) == SAFEPORT
    assert machine.get(DBI1 + 54) == DISPPORT
    assert machine.ports_created == 2 and machine.buffers_created == 2
    assert not machine.invalid_far_reads
    tests["cpu_alloc_screenbuffers_and_ports"] = "PASS"
    tests["cpu_dbufinfo_replyport_writes"] = "PASS"
    tests["cpu_68000_registers_and_abi"] = "PASS"

    # Repeat the call while DBState exists: must return success without
    # re-allocating any ScreenBuffer or MsgPort.
    repeat = AllocMachine(fixed_binary)
    repeat.put(STATE + STATE_DB, DBSTATE)
    repeat.execute(preserve_public=True)
    assert repeat.d(3) == 1
    assert repeat.alloc_count == 0
    assert repeat.ports_created == 0 and repeat.buffers_created == 0
    tests["cpu_double_buffer_idempotent"] = "PASS"

    # Validate failure cleanup before any DBState pointer is published.
    for fail in ("vec", "safeport", "dispport", "sb0", "sb1",
                 "dbi0", "dbi1"):
        m = AllocMachine(fixed_binary, failure=fail)
        m.execute(preserve_public=True)
        assert m.d(3) == 0, (fail, m.d(3))
        assert m.get(STATE + STATE_DB) == 0, fail
        assert not m.invalid_far_reads
    tests["cpu_partial_allocation_failure_paths"] = "PASS"

    # Close without Swap should work with allocated DBState.
    from test_intuition_input_r3 import Machine as CloseMachine
    closer = CloseMachine(segment(lib, 8))
    closer.put(STATE + STATE_DB, DBSTATE)
    closer.put(DBSTATE + 0, SB0)
    closer.put(DBSTATE + 4, SB1)
    closer.put(DBSTATE + 12, SAFEPORT)
    closer.put(DBSTATE + 16, DISPPORT)
    # Aga Screen Close is a STATEMENT, not an AP20 integer function.
    # D2 must be preserved, not forced to 0. Check every public D/A register.
    before_close = closer.execute()
    for reg, initial in before_close.items():
        assert closer.uc.reg_read(reg) == initial, (reg, initial)
    assert closer.close_window_count == 1 and closer.close_screen_count == 1
    assert closer.free_screenbuffers == [SB1, SB0]
    assert closer.deleted_ports == [DISPPORT, SAFEPORT]
    assert closer.get(STATE + STATE_DB) == 0
    tests["cpu_no_swap_close_after_allocation"] = "PASS"

    output = {
        "candidate_sha256": hashlib.sha256(data).hexdigest(),
        "candidate_size": len(data),
        "tests": tests,
        "limitation": (
            "68000 CPU with mocked system calls only. Real WinUAE/AMOS "
            "Aga Double Buffer + Close needs validation; Aga Swap/Close "
            "remains unsafe pending Safe/Disp notification synchronization."
        ),
    }
    dest = ROOT / "docs/DB_POINTER_R7_CPU_TESTS.json"
    dest.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    return output


if __name__ == "__main__":
    run()
