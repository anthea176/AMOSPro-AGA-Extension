# M4b runtime safety rules

These rules are mandatory before a candidate may replace `dist/AMOSPro_AGA.Lib`.

## Never block the AMOS interpreter

AMOS `Ctrl-C` is serviced by the interpreter. If an extension routine blocks inside Exec/Intuition, AMOS cannot process the break request.

Therefore the following are forbidden in AMOS-facing runtime commands:

- Exec `WaitPort()`;
- Exec `Wait()`;
- unbounded retry loops around `ChangeScreenBuffer()`;
- any loop whose exit depends only on an external message arriving.

Use instead:

- `GetMsg()` for non-blocking polling;
- a small, explicit `WaitTOF()` budget when a frame delay is needed;
- a hard attempt counter;
- return a failure/pending status to AMOS when the budget expires.

## Candidate gates

Every new M4b candidate must pass, in order:

1. AP20/HUNK/SHA/builder integrity.
2. `tools/check_no_blocking_waits.py`.
3. AMOS365 **load-only** test.
4. Open/Close regression.
5. Double Buffer allocation/cleanup regression.
6. One Swap only.
7. Multiple swaps only after the single-swap test passes.

Do not combine gates.

## Change isolation

After a block has runtime validation, keep it byte-for-byte unchanged unless that block itself is the target of the next test.

In particular:

- do not change Cold/hooks while testing Swap;
- do not change Close while testing Swap unless Close is the explicit test target;
- do not change multiple runtime entries in one candidate without a separate justification.

## Dist policy

- `dist/AMOSPro_AGA.Lib` = current file presented for testing.
- `dist/AMOSPro_AGA_LAST_GOOD.Lib` = last runtime-validated candidate.
- rejected candidates stay only in `dist/experimental/`.

When a candidate is rejected, restore `dist/AMOSPro_AGA.Lib` from `dist/AMOSPro_AGA_LAST_GOOD.Lib` before starting the next candidate.
