# AP20 V3 — P1 MC68020 two-unit dispatcher test

Experimental branch \`experiment/ap20-v3-multiunit-64k\` only.
Promoted R82 v0.13.27 and active AMOS test remain untouched.

## Scope

A **host CPU execution test** has been added:
\`tools/experiments/ap20_v3_multiunit_cpu020.py\`.

It constructs four independent native routines separated into two AP20 V2
dispatcher units with **82,012 native bytes**, and **82,080 unit bytes**
including two separate 34-byte dispatchers:

- Group 4: 40,040 bytes; offsets 0 and 40,000.
- Group 5: 42,040 bytes; offsets 0 and 42,000.

Each entry performs \`MOVEQ #value,D3; EXTB.L D3; RTS\`. \`EXTB.L\`
is specifically MC68020+, so this experiment does not silently revert to a
68000 compatibility target. NOP padding after RTS creates the large layout;
it is not a speed test.

On MC68020 Unicorn the suite executes **four separate entries twice**:
one near-link \`BSR.W\` and one simulated far-link absolute \`JSR\`.
The test checks correct unit/entry dispatch, D3 return value,
A0/A5/D0/D2 preservation, balanced A7, successful return to caller,
and native-code immutability. It also invokes the repository's
\`compiler_relocation.unpack_ap20\` independently of the experiment parser.

## Exact limitation

**This does not reproduce the byte-for-byte native output of the real
AMOS Compiler**, which has its own recursive \`LRouB\` loading and
linkage/relocation. It is a CPU-level *model* of compiler-patched RBSR
stubs plus actual 68k V2 dispatchers.

An actual AP20 with public tokens and AMOS cold start has not been
constructed, installed or run. No WinUAE interpreted Gate B or real
AMOS Compiler Gate C is claimed. No multiunit R82 production builder
exists. Next step is to establish the real compiler's link contract
from native source and qualify a separate minimal, callable test library
without overwriting the R82 slot.

## Execution

Branch-scoped workflow \`.github/workflows/ap20-v3-experiment.yml\`
runs structural tests, MC68020 CPU tests, and confirms that both R82
\`dist\` binaries exactly match the promoted SHA256 before testing.

No changes to \`main\`, \`dist/\`, \`tests/current/\`, or R82 API.

## First P1 CI iteration

The first branch-only run (43633736583) verified both R82 protected files,
passed all six P0 structural tests, and executed **four far JSR** targets on
MC68020 with correct ABI, return and target values. Its four near BSR.W
calls failed because the *test harness* calculated the branch from PC+4
rather than the 68k instruction's PC+2 base (already established by the
repository's earlier V2 bridge tests). This branch iteration fixes that
formula and adds a dedicated branch-opcode assertion. No native units or
production files were changed; the full P1 CPU gate must be rerun.
