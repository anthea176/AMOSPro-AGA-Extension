# P3 — Disposable WinUAE / AMOS Compiler trial (not yet executed)

**Strictly EXPERIMENTAL.** This is not an R83 release, nor a change to the
promoted R82 v0.13.27. The artifact is published by the
branch-only GitHub Actions workflow and expires according to artifact retention.

## Files inside the artifact

- \`AMOSPro_AGA_V3_FIXED.Lib\`: R82's original 60,972-byte native unit
  kept byte-for-byte, existing public API preserved, plus a second independent
  12,034-byte native unit containing \`aga v3 size probe\`.
- \`AP20_V3_R82_MULTIUNIT_01.asc\`: independent AMOS test (no image banks).
- \`P3_INSTRUCTIONS.md\`: this document.

## Isolation requirement

1. Use **a separate COPY** of the known-good WinUAE machine/configuration.
   Backup the test machine's \`APSystem\` extension and any installed AGA library.
   **Never replace the production R82 installation or LAST_GOOD reference.**
2. In that disposable WinUAE environment only, install the experimental
   \`.Lib\` as the AGA extension in its usual slot, exactly as R82 was installed.
   Its file name is deliberately distinct; rename/copy only inside the
   disposable test machine as required by AMOS installation.
3. Configure an actual MC68020 or later, AGA, and unchanged R82 dependencies.
4. Merge \`AP20_V3_R82_MULTIUNIT_01.asc\` into a **blank** AMOS program via
   **Project -> Merge ASCII**; do not merge it into an existing test program.
5. **First test interpreted**. It calls \`Aga Detect\` (old R82 monolith) and
   \`Aga V3 Size Probe\` (new second unit), expecting nonzero and **77**.
   Recover \`RAM:AP20_V3_RUNTIME.TXT\` if \`PRG_STATE=1\`, or
   \`RAM:AP20_V3_INTERPRETED.TXT\` if \`PRG_STATE=0\`.
6. **Only if the first run actually passes**, compile a NEW executable in
   AMOS Compiler, run it within the same disposable configuration and obtain
   \`RAM:AP20_V3_COMPILED.TXT\`. Never reuse an executable built with R82.
7. Provide both RAM logs and any screenshot, Guru, freeze, or build error.
   Copy RAM: logs to disk before resetting WinUAE.

## Pass / fail

Expected if supported: \`R82_OK 1\`, \`V3_PROBE 77\`, \`V3_OK 1\`,
\`RESULT 1\`, \`ERR 0\`, normal \`End\` and no unexpected Chip/Fast growth.

The experiment deliberately does NOT claim those values until actual WinUAE
logs exist. Static parser success, MC68020 Unicorn CPU tests, and a generated
artifact are **not** proof of real Interpreter or Compiler compatibility.

The exporter is \`tools/experiments/ap20_v3_r82_p2_export.py\`, restricted
to a clearly labeled test filename **outside** \`dist/\` and \`tests/current/\`.

The test exists only on \`experiment/ap20-v3-multiunit-64k\`, with no merge
or promotion to main without explicit authorization.

## FIX01 critical boot regression

The earlier `AMOSPro_AGA_V3_TEST_ONLY.Lib` must **NOT** be installed:
it triggered AMOS365 Software Failure 80000004 at interpreter startup.
It placed the extra native unit after R82's 60,972-byte group and caused
an out-of-range 60,978-byte BSR.W relocation. The FIX01 builder instead
places the probe native group before the historical R82 monolith and
checks **every** RBSR displacement against the AMOS365 interpreter source.
Passing host tests is not WinUAE boot proof. Use an isolated WinUAE copy.
