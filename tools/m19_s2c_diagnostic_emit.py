#!/usr/bin/env python3
# AGA_NATIVE_MIN_CPU: MC68020
"""S2c-P1d diagnostic source adapter; default P1c remains reproducible.

Public return: -(stage<<24 | check<<16 | detail16).
Original guards, success paths, receipts and retirement are retained.
No new token, hardware write, or unsafe pointer dereference.
"""
import re

def once(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)

def section(s,start,end,fn):
    a=s.index(start+'\n')
    b=s.index(end+'\n',a+len(start)+1)
    return s[:a]+fn(s[a:b])+s[b:]

def instrument(public,life,frame):
    stubs=[]
    def detail(label,check,value='',size='w',pop=False,tail='s2c_l_no'):
        body=label+':\n'
        if pop:body+='    addq.l #4,sp\n'
        if value:
            body+='    moveq #0,d1\n    move.'+size+' '+value+',d1\n'
            body+='    ori.l #$%08x,d1\n'%(check<<16)
        else:body+='    move.l #$%08x,d1\n'%(check<<16)
        stubs.append(body+'    neg.l d1\n    bra.w '+tail+'\n')
        return label

    def branches(part,pattern,rows,prefix,tail='s2c_l_no'):
        matches=list(re.finditer(pattern,part,re.M))
        assert len(matches)==len(rows),(prefix,len(matches),len(rows))
        for match,row in reversed(list(zip(matches,rows))):
            label=detail(prefix+str(row[0]),*row,tail=tail)
            part=part[:match.start()]+'    '+match[1]+'.w '+label+part[match.end():]
        return part

    # Context predicates in source order. Read details only in validated
    # memory, after the original failed comparison.
    context=[
        (1,'','w',False),(2,'','w',False),(3,'','w',False),
        (4,'','w',False),(5,'','w',False),(6,'32(a0)','w',False),
        (7,'24(a0)','w',False),(8,'26(a0)','w',False),
        (9,'','w',False),(10,'','w',False),(11,'','w',False),
        (12,'','w',False),(13,'1(a0)','b',False),
        (14,'2(a0)','w',False),(15,'18(a0)','b',False)]
    life=section(life,'s2c_l_context:','s2c_l_context_palette:',
        lambda p:branches(p,r'^    (bne|beq)\.w s2c_l_no$',context,'s2cd_ctx_'))
    slots=[(16,'','w',False),(17,'','w',False),
           (18,'(a0)','w',False),(19,'4(a0)','w',False),
           (20,'8(a0)','w',False),(21,'12(a0)','w',False),
           (22,'','w',True),(23,'','w',True)]
    life=section(life,'s2c_l_slots:','s2c_l_slots_bad:',
        lambda p:branches(p,r'^    (bne|beq)\.[sw] s2c_l_(?:no|slots_bad)$',
                          slots,'s2cd_slots_'))
    def palette(p):
        rows=[(24,'d0','w',False),(25,'6(a2)','w',False),
              (26,'14(a2)','w',False),(27,'22(a2)','w',False),
              (28,'30(a2)','w',False)]
        pat=r'^    (bne)\.s s2c_l_pal_no$'
        ms=list(re.finditer(pat,p,re.M))
        assert len(ms)==6
        last=ms[-1]
        p=p[:last.start()]+'    bne.w s2cd_rgb'+p[last.end():]
        return branches(p,pat,rows,'s2cd_pal_',tail='s2c_l_pal_no')
    life=section(life,'s2c_l_context_palette:','s2c_l_slots:',palette)
    stubs.append("""s2cd_rgb:
    ; A1 points one byte after expected RGB; D0.B is actual.
    moveq #0,d1
    move.b -1(a1),d1
    lsl.w #8,d1
    move.b d0,d1
    moveq #0,d4
    move.w 30(a4),d4
    mulu.w #3,d4
    subq.l #1,d4
    sub.l d7,d4
    addi.l #64,d4
    swap d4
    or.l d4,d1
    neg.l d1
    bra.w s2c_l_pal_no
""")

    def stage_stub(label,stage,tail,sticky=False,local=None):
        code=label+':\n    subi.l #$%08x,d1\n'%(stage<<24)
        if sticky:code+='    move.l #15,12(a3)\n'
        code+='    bra.w '+tail+'\n'
        (stubs if local is None else local).append(code)
        return label

    def stage_call(part,callee,old,label,stage,sticky=False):
        seq='    bsr.w '+callee+'\n    tst.l d0\n    beq.w '+old+'\n'
        return once(part,seq,seq.replace(old,stage_stub(label,stage,'s2c_l_refuse',sticky)))

    def acquire(p):
        seq='    bsr.w s2c_l_context_palette\n    tst.l d0\n    beq.w s2c_l_context_bad\n'
        assert p.count(seq)==2
        for label,stage in [('s2cd_acquire_before',1),('s2cd_acquire_after',2)]:
            p=p.replace(seq,seq.replace('s2c_l_context_bad',
                        stage_stub(label,stage,'s2c_l_refuse')),1)
        p=stage_call(p,'s2c_l_slots','s2c_l_owner','s2cd_acquire_slots',1)
        a=p.index('s2c_l_quarantine:\n')
        body,tail=p[:a],p[a:]
        pat=r'^    (beq|bne|bra)\.w (s2c_l_bad|s2c_l_owner|s2c_l_quarantine|s2c_l_get_fail)$'
        ms=list(re.finditer(pat,body,re.M))
        assert len(ms)==19,len(ms)
        for i,m in reversed(list(enumerate(ms))):
            check=32+i
            stage=2 if i>=17 else 1
            label='s2cd_acq_'+str(check)
            reason={'s2c_l_bad':1,'s2c_l_owner':3,'s2c_l_quarantine':5,'s2c_l_get_fail':4}[m[2]]
            code=label+':\n'
            if reason==5:code+='    ori.l #$80000004,12(a3)\n'
            code+='    move.l #%d,d1\n    bra.w s2c_l_refuse\n'%(-((stage<<24)|(check<<16)|reason))
            stubs.append(code)
            body=body[:m.start()]+'    '+m[1]+'.w '+label+body[m.end():]
        return body+tail
    life=section(life,'AGSP_S2C_ACQUIRE:','AGSP_S2C_SHOW:',acquire)

    def show(p):
        p=stage_call(p,'s2c_l_context_palette','s2c_l_context_bad','s2cd_show_before',3)
        p=stage_call(p,'s2c_l_context','s2c_l_publish_bad','s2cd_show_even',4,True)
        return stage_call(p,'s2c_l_context_palette','s2c_l_publish_bad','s2cd_show_odd',4,True)
    life=section(life,'AGSP_S2C_SHOW:','AGSP_S2C_MOVE:',show)
    def move(p):
        p=stage_call(p,'s2c_l_context_palette','s2c_l_context_bad','s2cd_move_before',5)
        return stage_call(p,'s2c_l_context','s2c_l_publish_bad','s2cd_move_after',9,True)
    life=section(life,'AGSP_S2C_MOVE:','AGSP_S2C_PALETTE:',move)

    def change(p):
        seq='    bsr.w s2c_l_context_palette\n    tst.l d0\n    beq.w s2c_f_context_bad\n'
        assert p.count(seq)==2
        local=[]
        for label,stage in [('s2cd_change_before',6),('s2cd_change_fences',7)]:
            p=p.replace(seq,seq.replace('s2c_f_context_bad',
                        stage_stub(label,stage,'s2c_f_fail',local=local)),1)
        for callee,label in [('s2c_l_context_palette','s2cd_change_hidden'),
                             ('s2c_l_context','s2cd_change_move')]:
            seq='    bsr.w '+callee+'\n    tst.l d0\n    beq.w s2c_f_uncertain\n'
            p=once(p,seq,seq.replace('s2c_f_uncertain',
                   stage_stub(label,8,'s2c_f_fail',True,local=local)))
        return p+'\n'+''.join(local)
    frame=section(frame,'AGSP_S2C_CHANGE:','s2c_f_refs:',change)
    anchor='    include "s2c_v5_frame.s"\n'
    life=once(life,anchor,'\n'+''.join(stubs)+'\n'+anchor)

    # Store diagnostic D1 before cleanup calls. Generic positive reason
    # maps to check 60. Existing simple-sprite return codes are unchanged.
    public=once(public,"""    bsr.w AGSP_S2C_ACQUIRE
    tst.l d0
    bne.w s2b_acquired
    move.l #-208,I_PHASE(a2)
    cmpi.l #2,d1
    bne.w p2i_retire_failed
    move.l #-153,I_PHASE(a2)
    bra.w p2i_retire_failed
""","""    bsr.w AGSP_S2C_ACQUIRE
    tst.l d0
    bne.w s2b_acquired
    bsr.w s2cd_public_stage1
    bra.w p2i_retire_failed
""")
    public=once(public,"""    bsr.w AGSP_S2C_SHOW
    tst.l d0
    beq.w p2i_retire_failed
    bra.w p2i_success
""","""    bsr.w AGSP_S2C_SHOW
    tst.l d0
    bne.w p2i_success
    bsr.w s2cd_public_stage3
    bra.w p2i_retire_failed
""")
    public=once(public,"""    bsr.w AGSP_S2C_MOVE
    tst.l d0
    bne.w p2i_success
    bra.w s2c_active_failed
""","""    bsr.w AGSP_S2C_MOVE
    tst.l d0
    bne.w p2i_success
    bsr.w s2cd_public_stage5
    bra.w s2c_active_failed
""")
    public=once(public,"""    movea.l sp,a2
    move.l d0,d7
    bsr.w s2a_free_scratch
""","""    movea.l sp,a2
    move.l d0,d7
    tst.l d7
    bne.s s2cd_change_free
    bsr.w s2cd_public_stage6
s2cd_change_free:
    bsr.w s2a_free_scratch
""")
    for stage in (1,3,5,6):
        public+=("""
s2cd_public_stage%d:
    tst.l d1
    bmi.s s2cd_public_have%d
    andi.l #$0000ffff,d1
    ori.l #$%08x,d1
    neg.l d1
s2cd_public_have%d:
    move.l d1,I_PHASE(a2)
    rts
"""%(stage,stage,(stage<<24)|(60<<16),stage))
    return public,life,frame
