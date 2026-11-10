"""Reproduce R1 last-plane loss with a deferred blit; validate R2 on every IFF."""
import json
from build_m5_generic import build as build_r1
from build_m5_generic_r2 import build, ROOT
from test_m5_generic import Machine, run as full_validation
from validate_ilbm import inspect,decode

def run():
    full_validation(builder=build,report_name='GENERIC_R2_VALIDATION.json')
    r1,_=build_r1(); r2,report=build(); results=[]
    paths=sorted((p for p in ROOT.rglob('*') if p.suffix.lower() in ('.iff','.ilbm')),key=lambda p:p.as_posix().lower())
    for path in paths:
        data=path.read_bytes(); meta,body=inspect(data); planes,_=decode(meta,body)
        old=Machine(r1,data,meta,pending_blit=True); assert old.execute(13)==1
        assert all(not any(old.uc.mem_read(old.planes[-1]+row*old.stride,meta['row_bytes']))
                   for row in range(meta['height']))
        # The final bitplane may legitimately be all zero (e.g. an 8-plane
        # indexed image using only colours 0..127). Such an image cannot
        # visually expose the historical R1 last-plane loss, but must still
        # pass R2's full pixel, synchronization and resource checks.
        r1_observable=any(planes[-1])
        current=Machine(r2,data,meta,pending_blit=True); assert current.execute(13)==1
        current.assert_pixels(planes); assert not current.pending_blit
        r1_note='last plane erased' if r1_observable else 'not observable (empty last plane)'
        results.append(dict(file=path.relative_to(ROOT).as_posix(),r1_delayed_blit=r1_note,r2_delayed_blit='PASS'))
        print('R2 synchronized PASS',path.name,flush=True)
    output=dict(sha256=report['sha256'],files=results,
                limitation='Deferred blit model validates ordering; runtime visual validation still required.')
    (ROOT/'docs/GENERIC_R2_CPU_TESTS.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    return output

if __name__=='__main__':run()
