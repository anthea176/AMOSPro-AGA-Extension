# AP20 V3 — P2: R82 promoted monolith + independent second native unit

This experiment is on \`experiment/ap20-v3-multiunit-64k\` only.

## Construction

Read the EXACT promoted R82 v0.13.27 current + LAST_GOOD binaries,
requiring SHA256 \`b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36\`.
Build entirely **in memory**; no \`dist/\` write or new release/version.

- Keep the R82 60,972-byte native unit **byte-for-byte unchanged**.
- Rebase the old 80 AP20 RBSR stubs' target indices from group 80 to 82,
  leaving every original offset, marker, native instruction and public
  token unchanged.
- Add experimental token \`aga v3 size probe\` returning integer D3=77,
  at public entry 80, and an independent native MC68020 unit at entry 81.
- Native unit sizes: **60,972 + 12,034 = 73,006 bytes** (greater than 64 KiB).
  Each individual unit remains under the 65,534-byte per-unit Compiler limit.
- Both native dispatchers are the existing *exact* 34-byte V2 bridge.
- The addon starts with \`MOVEQ #77,D3; EXTB.L D3; RTS\`. Padding NOPs
  after RTS only raise the size for this boundary experiment.
- Require existing public token names, signatures and parameter markers
  to survive the transformation; use the repository's independent AP20
  token audit and format parser.

The corrected CPU test executes the actual interpreter-style BSR.W to the new unit on Unicorn
**MC68020** and validates D3, A7, return PC, preserved registers and
read-only native code. It **does not execute the original R82 monolith**:
old native behavior is protected by byte identity, not re-qualified by
this isolated CPU test.

## Status

The branch-only workflow runs the P0 structure suite, P1 MC68020 dual
dispatcher suite and P2 R82-extension tests. The resulting library is
not written to disk, installed in AMOS, or promoted.

This remains **host/CPU Gate A only**. The official AMOS interpreter
and AMOS Compiler are not being executed by these tests, and the
exact real-Compiler relocation output has not been verified.

Next milestone: a disposable, independently installable test artefact,
and a WinUAE 68020+ interpreted/compiled test, without replacing the
R82 LAST_GOOD reference. Only then consider production multiunit work.

## P2-FIX01 after the AMOS365 80000004 report

The previous binary had a 60,978-byte interpreter RBSR->BSR.W relocation
(entry 80 to group 82). AMOS365 +B.s / GRouB explicitly executes ILLEGAL
outside ±32,766 bytes, before any test source is executed. This was missing
from previous CPU tests which simulated an absolute JSR.

FIX01 places the **12,034-byte native probe unit at group 81, immediately
after the public stubs**, then the byte-identical R82 monolith at group 82.
Existing R82 RBSR targets are rebased 80->82; the test stub targets 81.
The new Gate A models all AMOS365 RBSR relocations, intentionally rejects
the previous crashing layout, and executes the patched BSR.W on MC68020.
This does not claim an actual WinUAE boot result.
