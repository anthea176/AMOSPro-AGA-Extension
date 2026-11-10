#!/usr/bin/env python3
"""R8 0.5.9: Safe/Disp synchronization on R7, no loader changes.

R7 is the sole validated base. The old nonblocking swap discarded asynchronous
notification messages without tracking which response was still in flight.
R8 tracks pending responses in the existing DBState +20 long:
  bit 0: dbi_SafeMessage reply pending
  bit 1: dbi_DispMessage reply pending
Set both ONLY if ChangeScreenBuffer succeeds. GetMsg replies are never ReplyMsg'd.

Swap remains nonblocking: if the previous swap is in flight, return 0.
Close/init/CTRL+C use cooperative GetMsg + graphics.library WaitTOF polling.
On timeout they FAIL CLOSED: no Window/Screen/DB/port is freed, and Ctrl+C
Break is NOT triggered. The caller can retry after normal system progress.

All code changes are append-only relative to original entry body except for
one old branch at public Close, init shutdown, keyboard Ctrl+C, and a complete
rebuild of the Swap segment with symbolic branches.
"""
import json
from pathlib import Path
from ap20_utils import split,rebuild,Asm,digest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.5.8_DB_POINTER_R7.Lib'
SRC_SHA='e6dd32ceda1181ef3172dfb242a1d4fc93656c6788023d7b1333dc2561ed3dce'
DEST=ROOT/'dist/AMOSPro_AGA.Lib'
ARCHIVE=ROOT/'dist/experimental/AMOSPro_AGA_M5_v0.5.9_DB_SYNC_R8.Lib'
REPORT=ROOT/'docs/DB_SYNC_R8_BUILD.json'
PENDING_SAFE=1;PENDING_DISP=2
MAX_VBL=300  # WaitTOF loop bound. On timeout leave all resources intact.

# All opcodes in the poll code are standard MC68000, no 68020-only features.
def poll_replies(a:Asm):
    """A4 DBState. D6 becomes pending mask; D0 returns pending count/mask.

    GETMSG receives a message which Intuition/graphics ALREADY replied to our
    private Safe/Disp port. Never call ReplyMsg on a ScreenBuffer response.
    A0/A6, D0/D6, CCR modified. A2/A4 and other registers untouched.
    """
    a.label('poll_replies')
    a.emit('2c2c0014')  # MOVE.L 20(A4),D6
    a.emit('028600000003')  # ANDI.L #3,D6
    a.emit('08060000')  # BTST #0,D6
    a.branch(0x6700,'skip_safe')
    a.emit('206c000c20084a80')  # MOVEA.L 12(A4),A0 / MOVE.L A0,D0 / TST.L D0
    a.branch(0x6700,'skip_safe')
    a.emit('2c7800044eaefe8c4a80')  # EXEC GetMsg(-372), TST.L D0
    a.branch(0x6700,'skip_safe')
    a.emit('08860000')  # BCLR #0,D6 (safe reply consumed)
    a.label('skip_safe')
    a.emit('08060001')  # BTST #1,D6
    a.branch(0x6700,'skip_disp')
    a.emit('206c001020084a80')  # MOVEA.L 16(A4),A0
    a.branch(0x6700,'skip_disp')
    a.emit('2c7800044eaefe8c4a80')  # GetMsg(disp), TST.L D0
    a.branch(0x6700,'skip_disp')
    a.emit('08860001')  # BCLR #1,D6
    a.label('skip_disp')
    a.emit('2946001420064e75')  # MOVE.L D6,20(A4); MOVE.L D6,D0; RTS


def wait_for_pending(a:Asm):
    """A2 state*, result D0=1 fully synchronized, 0 timed out.

    No orphan ScreenBuffers: caller MUST abort all freeing when D0==0.
    No WaitPort, no Exec Wait. Time bound is MAX_VBL WaitTOF iterations.
    """
    a.label('wait_for_pending')
    a.emit('286a0020200c4a80')  # MOVEA.L 32(A2),A4, TST.L ptr
    a.branch(0x6700,'synced')
    a.emit('7800')  # MOVEQ #0,D4 (cooperative VBL count)
    a.label('wait_poll')
    a.branch(0x6100,'poll_replies')  # BSR.W, return D0 pending mask
    a.emit('4a80')
    a.branch(0x6700,'synced')
    a.emit('5284')  # ADDQ.L #1,D4
    a.emit('0c840000'+f'{MAX_VBL+1:04x}')  # CMPI.L #MAX_VBL,D4
    a.branch(0x6c00,'timeout')  # BGE: never free after bounded wait expiry
    a.emit('2c6a0008200e4a80')  # MOVEA.L 8(A2),A6 / TST pointer
    a.branch(0x6700,'timeout')
    a.emit('4eaefef2')  # graphics.library/WaitTOF, cooperative
    a.branch(0x6000,'wait_poll')
    a.label('synced');a.emit('70014e75')  # MOVEQ #1,D0, RTS
    a.label('timeout');a.emit('70004e75')  # MOVEQ #0,D0, RTS
    poll_replies(a)


def patch_brw(buf:bytearray,pos,target,expected):
    """Patch exactly one BRA.W instruction, preserving all other bytes."""
    assert bytes(buf[pos:pos+4]) == expected,(hex(pos),buf[pos:pos+4].hex())
    disp=target-(pos+2)
    assert -32768<=disp<=32767
    buf[pos:pos+4]=b'\x60\x00'+disp.to_bytes(2,'big',signed=True)


def close_entry(base:bytes,index):
    """Unconditional preflight before CloseWindow, no cleanup after timeout."""
    if index==8:
        assert base.endswith(b'GetP')
        old=base[:-4];suffix=b'GetP'
        hook=8;old_call=0xd4;continue_at=12;abort_at=0xce
        assert old[hook:hook+4]==bytes.fromhex('610000ca')
        assert old[old_call:old_call+4]==bytes.fromhex('266a0024')
        assert old[abort_at:abort_at+4]==bytes.fromhex('4cdf7fff')
    else:
        assert index==0
        old=base;suffix=b''
        hook=0x40;old_call=0x14e;continue_at=0x44;abort_at=0x148
        assert old[hook:hook+4]==bytes.fromhex('6100010c')
        assert old[old_call:old_call+4]==bytes.fromhex('266a0024')
        assert old[abort_at:abort_at+4]==bytes.fromhex('4cdf7fff')
    add=Asm()
    add.branch(0x6100,'wait_for_pending')
    add.emit('4a80')  # TST.L D0
    add.branch(0x6700,'abort_orig')
    add.branch(0x6100,'old_window')
    add.branch(0x6000,'resume_orig')
    add.label('abort_orig');add.branch(0x6000,'exit_orig')
    wait_for_pending(add)
    entry_pos=len(old)
    add.labels['old_window']=old_call-entry_pos
    add.labels['resume_orig']=continue_at-entry_pos
    add.labels['exit_orig']=abort_at-entry_pos
    patched=bytearray(old)
    patch_brw(patched,hook,entry_pos,old[hook:hook+4])
    if index==0:
        # R6 still contains dormant R6B-R1 WaitPort code in the extension
        # shutdown path. Our preflight COMPLETELY supersedes this code.
        # Force the legacy branch unconditionally past it and replace both
        # forbidden WaitPort invocations with NOPs. Keep all other offsets.
        legacy_branch=0x62
        assert patched[legacy_branch:legacy_branch+4] == bytes.fromhex('6700003a')
        patched[legacy_branch:legacy_branch+2] = bytes.fromhex('6000')
        legacy_waitport = bytes.fromhex('4eaefe80')
        assert patched.count(legacy_waitport)==2
        patched = patched.replace(legacy_waitport, bytes.fromhex('4e714e71'))
        assert legacy_waitport not in patched
    return bytes(patched)+add.out()+suffix


def ctrl_entry(base:bytes,index):
    """Preflight on Ctrl+C before existing Window/DB cleanup and Break.

    For failed safe/disp synchronization, retain ALL resources; do not set
    native AMOS Break flags. Original D3=-1, D2=0 returned to caller.
    """
    assert index in (17,18)
    old=bytearray(base);hook=0x7e;old_cleanup=0x8c
    # Original BRA.W to cleanup before ORI.W #$8100,T_Actualise.
    assert old[hook:hook+4]==bytes.fromhex('6000000c')
    assert old[0x82:0x88]==bytes.fromhex('006d8100ff58')
    abort_at=0x1da if index==17 else 0x1ee
    assert old[abort_at:abort_at+4]==bytes.fromhex('4cdf5ff3')
    add=Asm()
    add.branch(0x6100,'wait_for_pending')
    add.emit('4a80')
    add.branch(0x6700,'abort_orig')
    add.branch(0x6000,'resume_cleanup')
    add.label('abort_orig');add.branch(0x6000,'orig_restore')
    wait_for_pending(add)
    entry_pos=len(old)
    add.labels['resume_cleanup']=old_cleanup-entry_pos
    add.labels['orig_restore']=abort_at-entry_pos
    patch_brw(old,hook,entry_pos,b'\x60\x00\x00\x0c')
    return bytes(old)+add.out()


def swap_entry():
    a=Asm()
    a.emit('48e7effe7600246d01c84a92')  # MOVEM, MOVEQ #0,D3, state*, TST Screen
    a.branch(0x6700,'done')
    a.emit('286a0020200c4a80')  # DBState*, NULL?
    a.branch(0x6700,'done')
    a.emit('202c000c4a80')  # SafePort present?
    a.branch(0x6700,'done')
    a.emit('202c00104a80')  # DispPort present?
    a.branch(0x6700,'done')
    a.branch(0x6100,'poll_replies')  # Only GetMsg on pending messages
    a.emit('4a80')
    a.branch(0x6600,'done')  # BNE: still pending, cannot swap again
    a.emit('202c00084a80')  # current index (0/1)
    a.branch(0x6700,'front0')
    a.emit('7e00')  # target SB0
    a.branch(0x6000,'target_ready')
    a.label('front0');a.emit('7e01')  # target SB1
    a.label('target_ready')
    a.emit('2c6a0008200e4a80')  # gfx base valid?
    a.branch(0x6700,'done')
    a.emit('4eaeff1c')  # WaitBlit
    # Explicit reload of A1 after WaitBlit, no assumed A1 survival.
    a.emit('4a87')  # TST.L D7
    a.branch(0x6700,'target0')
    a.emit('226c0004')  # MOVEA.L 4(A4),A1 (SB1)
    a.branch(0x6000,'target_loaded')
    a.label('target0');a.emit('2254')  # MOVEA.L (A4),A1 (SB0)
    a.label('target_loaded')
    a.emit('20094a80')
    a.branch(0x6700,'done')
    a.emit('20522c6a00044eaefcf44a80')  # Screen A0, Intuition A6; ChangeScreenBuffer
    a.branch(0x6700,'done')
    a.emit('29470008')  # MOVE.L D7,8(A4) current index
    a.emit('297c000000030014')  # MOVE.L #3,20(A4) both notifications in flight
    a.emit('7601')  # D3=1 success
    a.label('done')
    a.emit('4cdf7ff774004e75')  # restore public registers, D2=0, RTS
    poll_replies(a)
    return a.out()+b'GetP'


def build():
    raw=SRC.read_bytes()
    assert digest(raw)==SRC_SHA, 'R7 base hash mismatch'
    tokens,old,title=split(raw)
    assert len(old)==19 and len(old[0])==456 and len(old[8])==298
    new=list(old)
    new[0]=close_entry(old[0],0)
    new[8]=close_entry(old[8],8)
    new[11]=swap_entry()
    new[17]=ctrl_entry(old[17],17)
    new[18]=ctrl_entry(old[18],18)
    for i in range(len(new)):
        if i not in (0,8,11,17,18):
            assert new[i]==old[i],('Unexpected modified segment',i)
    # Critical loader/PicInfo and R7 DB allocation frozen byte-for-byte.
    for i in (6,7,9,10,13,14,15,16):assert new[i]==old[i]
    new_title=(title.replace(b'Intuition Input R7 0.5.8',b'Intuition Input R8 0.5.9')
                    .replace(b'AMOSPro_AGA 0.5.8',b'AMOSPro_AGA 0.5.9'))
    assert len(new_title)==len(title)==64
    output=rebuild(raw,new,new_title)
    assert output!=raw and len(output)%4==0
    manifest={
        'version':'0.5.9','source_sha256':SRC_SHA,'sha256':digest(output),
        'source_size':len(raw),'size':len(output),
        'changed_ap20_segments':[0,8,11,17,18],
        'all_other_segments_byte_identical':True,
        'generic_ilbm_r2_picinfo_byte_identical':True,
        'screenbuffer_allocation_r7_byte_identical':True,
        'safe_disp_replymsg_forbidden':True,
        'pending_mask_at_dbstate_offset':20,
        'pending_safe_bit':0,'pending_disp_bit':1,
        'close_max_cooperative_wait_vbl':MAX_VBL,
        'timeout_policy':'fail closed, leave all resources allocated and cancel native Ctrl+C break',
        'status':'WinUAE single Swap plus Close without IFF 5/5 PASS; repeated Swap, Ctrl+C in-flight, IFF and independent Unicorn CPU still pending',
    }
    return output,manifest

if __name__=='__main__':
    output,manifest=build();assert build()[0]==output
    DEST.write_bytes(output);ARCHIVE.write_bytes(output)
    REPORT.write_text(json.dumps(manifest,indent=2)+'\n')
    print('R8',len(output),digest(output),'changed',[0,8,11,17,18])
