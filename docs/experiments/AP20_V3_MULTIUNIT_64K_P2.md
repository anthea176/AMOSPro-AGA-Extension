# AP20 V3 — P2: R82 promoted monolith + independent second native unit

This experiment is on \`experiment/ap20-v3-multiunit-64k\` only.

## Construction

Read the EXACT promoted R82 v0.13.27 current + LAST_GOOD binaries,
requiring SHA256 \`b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36\`.
Build entirely **in memory**; no \`dist/\` write or new release/version.

- Keep the R82 60,972-byte native unit **byte-for-byte unchanged**.
- Rebase the old 80 AP20 RBSR stubs' target indices from group 80 to 81,
  leaving every original offset, marker, native instruction and public
  token unchanged.
- Add experimental token \`aga v3 size probe\` returning integer D3=77,
  at public entry 80, and an independent native MC68020 unit at entry 82.
- Native unit sizes: **60,972 + 12,034 = 73,006 bytes** (greater than 64 KiB).
  Each individual unit remains under the 65,534-byte per-unit Compiler limit.
- Both native dispatchers are the existing *exact* 34-byte V2 bridge.
- The addon starts with \`MOVEQ #77,D3; EXTB.L D3; RTS\`. Padding NOPs
  after RTS only raise the size for this boundary experiment.
- Require existing public token names, signatures and parameter markers
  to survive the transformation; use the repository's independent AP20
  token audit and format parser.

The CPU test simulates a far-link JSR to the new unit on Unicorn
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
