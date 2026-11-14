#!/usr/bin/env python3
"""R82 exact in-memory Compiler V2 -> native reconstruction and strict CFG audit.

The active installable is NOT changed here. The source is authenticated from
the R82 deterministic builder and its frozen R81 LAST_GOOD ancestor.
This is not AMOS Compiler nor WinUAE runtime validation.
"""
from hashlib import sha256

from build_agapic_v2_r82_full_preview import build
from active_library import R82_SHA,R81_SHA
from compiler_bridge_v2_probe import is_v2_wrapped
import generate_aga_native_source as exp


def main():
    candidate,meta=build()
    assert sha256(candidate).hexdigest()==R82_SHA==meta['sha256']
    assert is_v2_wrapped(candidate)
    native,ctx=exp.source_binary_from_input(candidate)
    assert ctx and ctx['verified_extract_and_rewrap']
    assert ctx['official_entries']==81 and ctx['native_entries']==80
    parsed=exp.parse_lib(native)
    assert parsed['title'].startswith(b'AMOSPro AGA AGAPIC v2 Palette and Region R82')
    issues=exp.unclassified_gaps(parsed)
    assert not issues,('strict native source: unclassified bytes',issues[:12])
    source,report=exp.output(parsed)
    exp.validate_structure(source,parsed)
    assert report and len(source)>1000
    print('R82 IN-MEMORY STRICT NATIVE SOURCE PASS:',len(candidate),
          'bytes / 81 AP20 / 80 native / no unclassified ranges;',
          'pinned SHA256',R82_SHA,'parent R81',R81_SHA)


if __name__=='__main__':
    main()
