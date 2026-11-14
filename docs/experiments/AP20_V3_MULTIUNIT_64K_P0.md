# AP20 V3 multiunit >64 KiB: isolated experiment

Base: promoted R82 v0.13.27, exact branch origin ff950e4d2553d1a36b99ab959153fbbb35201c8a.
Experimental branch only. The main branch, dist/ libraries, LAST_GOOD, and tests/current/ are unchanged.

## Objective and evidence level

Investigate whether one AMOS extension can contain multiple independently
copied AP20 Compiler native units, each under the 65,534-byte size bound,
while total native code is above 65,536 bytes. No modification to AMOS Compiler.

The initial structural probe is tools/experiments/ap20_v3_multiunit_probe.py.
Run: python3 tools/experiments/ap20_v3_multiunit_probe.py

Locally executed on 2026-11-14 with Python 3: six unit tests PASS.
The test constructs 82,008 bytes of deliberately independent synthetic
68000-instruction-compatible code, in TWO AP20 units of 40,038 and 42,038
bytes including the 34-byte V2 dispatcher in each. Their stub destinations
point to group 4 or 5, with offsets 0/40000 and 0/42000. All groups remain
under 65,534 bytes. It verifies AP20 HUNK round trips, deterministic output,
rejection of wrong group or odd offsets, unit overflow, unsafe inputs and
unexpected GetP markers.

CRITICAL: The choice of old-compatible synthetic NOP/MOVEQ/RTS instructions
is deliberate for a structural layout oracle. It DOES NOT change the
official minimum CPU of 68020. This is not a performance implementation.

## Why this is only a hypothesis

The official AMOS Compiler source compiler/+APComp.s has a 16-bit
LB_LibSizes entry width in Lib_Load and resolves RBSR target routine numbers
through LRouB. That supports investigating multiple independent units.
It does not prove the produced code will execute correctly after being copied.

The production R82 monolith contains linked routines, PC-relative data
references and State-based offsets. Splitting it without full relocation and
cross-unit reference auditing risks corruption. This prototype intentionally
does not support or silently modify linked R82 functions.

No WinUAE Gate B, AMOS Compiler Gate C, or physical Gate D result is claimed.
No experimental .Lib is installed and no official version is incremented.

## Follow-up gates

1. Validate generated AP20 multiunit structure against the repository's
   original compiler_relocation.py parser and strict source-format auditing.
2. Generate a minimal independent AP20 extension with real callable tokens
   and two groups; test under AMOS Pro WinUAE MC68020+ interpreted first,
   then with a newly compiled executable. Record actual logs.
3. Only if that passes, analyze R82 native inter-entry call graph, shared
   static data and all PC-relative and State-relative links; define explicit
   independent module boundaries/trampolines.
4. Keep main R82 LAST_GOOD protected; no promotion, merge or release
   without the author's express approval.

Reference docs on main: EXTENSION_SOURCE_RULES.md and
docs/AGAPIC_R82_LAST_GOOD_PROMOTION_2026-11-14.md.
