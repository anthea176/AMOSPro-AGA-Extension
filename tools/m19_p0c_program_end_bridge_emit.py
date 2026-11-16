#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""M19 P0c PRIVATE AMOS End callback bridge, appended SOURCE ONLY.

End register slots A5+460 and A5+464 are set by the SHA-pinned AGA
initializer to the ORIGINAL native callback within the same AGA V2 group
as State. Rather than a broken cross-unit PC-relative BSR, use the pinned
state-relative delta to identify the original end callback after relocation.

Two PRIVATE entrypoints:
  program_end_arm_entry: D2=0,D3=1/0. Called ONLY AFTER registry_prepare
    succeeded and active owner A5 matches. Checks both callbacks are original
    or already armed, then installs one same-unit BOBS callback for both.
  program_end_bridge_entry: AMOS callback; saves/restores all registers,
    first validates original AGA End bytes and calls screen_preclose_entry;
    on success restores both original callbacks BEFORE JSR old End;
    on failure leaves existing resources intact, NEVER calls destructive End.

NO public token/compiled WinUAE claim. All old AGA native code stays untouched.
Actual public future Chip-staging command MUST call arm_entry after a successful
prepare; otherwise direct End is still unsafe. This experiment does not
silently change already-qualified P0b commands.
"""
from __future__ import annotations

from m68k_emit import Code,D,A,M,I
from m19_p0c_screen_close_bridge_emit import emit_screen_close_bridge

AGA_STATE_OFF=0x1c2
AGA_END_OFF=0x5a
END_STATE_DELTA=AGA_END_OFF-AGA_STATE_OFF
assert END_STATE_DELTA==-0x168
STATE_A5=0x1c8
END1_A5=0x1cc
END2_A5=0x1d0
END_SIGNATURE=(0x48e7fffe,0x246d01c8,0x60000978)


def emit_program_end_bridge() -> tuple[bytes,dict[str,int]]:
    previous,old_labels=emit_screen_close_bridge()
    c=Code()
    c.raw(previous.hex())
    c.labels.update(old_labels)
    B,L=c.branch,c.label

    def get_end(failure):
        # A5 is the live AMOS context. Exact provenance is checked by builder.
        c.move(A(5),D(0)); c.tst(D(0)); B(7,failure)
        c.imm('and',1,D(0)); B(6,failure)
        c.move(M(5,STATE_A5),D(0))
        c.imm('cmp',0x168,D(0))
        B(5,failure)            # unsigned lower => underflow
        c.imm('sub',0x168,D(0))
        c.move(D(0),D(1));c.imm('and',1,D(1));B(6,failure)
        c.move(D(0),A(4))      # old End ptr; A4 preserved across all calls
        c.move(A(4),A(1))
        c.raw('2c780004')
        c.call_os(-534)        # TypeOfMem(old original End entry)
        c.tst(D(0));B(7,failure)
        for i,word in enumerate(END_SIGNATURE):
            c.move(M(4,i*4),D(0))
            c.imm('cmp',word,D(0))
            B(6,failure)

    L('program_end_arm_entry')
    c.raw('48e7efee')           # preserve AMOS caller except integer D2/D3
    c.move(I(0),D(3))
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'end_arm_return')

    # A5 owner must match a populated/verified per-bank Chip registry.
    c.lea(0,'registry_state')
    c.move(M(0,0),D(0))
    c.move(A(5),D(1))
    c.alu('cmp',D(1),0);B(6,'end_arm_return')
    c.tst(M(0,4));B(7,'end_arm_return')
    get_end('end_arm_return')

    # Refuse to clobber a third-party hook, including partially patched
    # callback pairs. Both must be the OLD native End or OUR bridge.
    c.move(M(5,END1_A5),D(0))
    c.move(M(5,END2_A5),D(1))
    c.alu('cmp',D(1),0);B(6,'end_arm_return')
    c.move(A(4),D(1))
    c.alu('cmp',D(1),0)
    B(7,'end_arm_install')
    c.lea(1,'program_end_bridge_entry')
    c.move(A(1),D(1))
    c.alu('cmp',D(1),0);B(6,'end_arm_return')
    L('end_arm_install')
    c.lea(0,'program_end_bridge_entry')
    c.move(A(0),M(5,END1_A5))
    c.move(A(0),M(5,END2_A5))
    c.move(I(1),D(3))
    L('end_arm_return')
    c.raw('4cdf77f7')
    c.raw('74004e75')         # MOVEQ #0,D2; RTS

    L('program_end_bridge_entry')
    c.raw('48e7fffe')       # preserve full original AGA callback ABI
    B(1,'registry_cpu_guard')
    c.tst(D(0));B(7,'end_bridge_return')
    get_end('end_bridge_return')

    c.lea(0,'program_end_bridge_entry')
    c.move(A(0),D(1))
    c.move(M(5,END1_A5),D(0))
    c.alu('cmp',D(1),0);B(6,'end_bridge_return')
    c.move(M(5,END2_A5),D(0))
    c.alu('cmp',D(1),0);B(6,'end_bridge_return')

    # Cleanup must complete while AGA graphics.library is still alive.
    B(1,'screen_preclose_entry')
    c.tst(D(3));B(7,'end_bridge_return')

    # Restore original AMOS callback slots BEFORE the original callback,
    # preventing later End from reentering freed BOBS code.
    c.move(A(4),M(5,END1_A5))
    c.move(A(4),M(5,END2_A5))
    c.raw('4e94')            # JSR (A4): actual legacy AGA End callback
    L('end_bridge_return')
    c.raw('4cdf7fff')        # restore all D0-D7/A0-A6
    c.raw('4e75')

    code=c.out()
    assert code[:len(previous)]==previous
    assert c.labels['program_end_arm_entry']==len(previous)
    assert c.labels['program_end_bridge_entry']>c.labels['program_end_arm_entry']
    assert len(code)<32766 and not (len(code)&1)
    return code,c.labels

if __name__=='__main__':
    from hashlib import sha256
    code,lab=emit_program_end_bridge()
    print('M19 P0c PRIVATE AMOS End callback bridge SOURCE ONLY',
          len(code),sha256(code).hexdigest(),lab['program_end_arm_entry'],
          lab['program_end_bridge_entry'],'no installed library or WinUAE/Compiler test')
