# AGA Bob showcase — P2 ALL IN ONE

[Français](README.fr.md) · [All examples](../README.md) · [Installation](../../INSTALL.md)

**Public example validated in WinUAE Runtime and with AMOS Compiler.** This single, self-contained AMOS Professional program covers the **P2a–P2e Bob features** using asymmetric **F and L** graphics: two AMAL animation channels, collision detection, H/V/HV flips, destination bitplane masks, and automatic Bob updates with double buffering. **No external images or bank files** are required.

## Files and requirements

- [**BOB_ALL_IN_ONE.asc**](BOB_ALL_IN_ONE.asc): **byte-identical original ASCII source**, 25,056 bytes; Git blob `c48d334fd4508d402d28399bffdfec08d4cb4acb`, tag `P2_FULL_V1_20261121`.
- Requires [`dist/AMOSPro_AGA.Lib` M19 P2d](../../dist/AMOSPro_AGA.Lib), **136,020 bytes**, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, **100 commands / 203 AP20 entries**, **MC68020/68EC020 minimum**.
- [Frozen test copy](../../tests/passed/M19_P2_ALL_IN_ONE.asc): **exact same bytes** as this example. Protected P1e `LAST_GOOD` is unchanged.

## What appears on screen

| Stage | API / behaviour | Actual test coverage |
| --- | --- | --- |
| 1 — P2e / P2d | Two AMAL channels driving moving 16×16 F/L Bobs | **240 samples**, 29 pixel checks per Bob |
| 2 — P2a | `Aga Bob Col(A,B,Mode)`: rectangle and opacity-mask collisions | **8 checks** including invalid mode |
| 3 — P2b | `Aga Bob Flip(N,Mode)`: normal/H/V/HV | Two asymmetric **32×32** glyphs, **20 pixel checks** |
| 4 — P2c / P2d | `Aga Bob Planes(N,Mask)`, `Aga Bob Auto Update(1/0)` | **10 bitplane pixel checks** across five masks, auto-update disabled on exit |

The AGA display comes forward automatically via `Amos To Back`, then closes and restores AMOS with `Amos To Front`. The demo **exits on its own** and writes a `RAM:` log; there is no key-to-exit step.

## How to run

1. Install the exact **P2d library** into the AGA slot in `APSystem`; restart AMOS Professional, running WinUAE with AGA and a 68020+ CPU.
2. In a **new, empty AMOS program**, make sure banks **24, 27 and 28** are unused.
3. Use **Project → Merge ASCII** to import `BOB_ALL_IN_ONE.asc`. Run in Runtime mode or compile **the same unchanged source** using AMOS Compiler.
4. Preserve the resulting `RAM:` log before resetting WinUAE or running again.

| Mode | Output log |
| --- | --- |
| Strict interpreted (`Prg State 0`) | `RAM:M19_P2_FULL_INTERPRETED.TXT` — not tested |
| Runtime (`Prg State 1`) | `RAM:M19_P2_FULL_RUNTIME.TXT` — **PASS** |
| Compiled (`Prg State -1`) | `RAM:M19_P2_FULL_COMPILED.TXT` — **PASS** |
| Unknown | `RAM:M19_P2_FULL_UNKNOWN.TXT` |

## WinUAE results, 21 November 2026

Both **user-supplied original logs** agree on every diagnostic except `PRG_STATE` and `RUN_MODE`.

| Check | Runtime | Compiled |
| --- | ---: | ---: |
| `RESULT / ERR / VERDICT` | 1 / 0 / PASS | 1 / 0 / PASS |
| `VALID_SAMPLES / SWAPS` | 240 / 252 | 240 / 252 |
| `COL_CHECKS` | 8 | 8 |
| `FLIP_PIX0 / FLIP_PIX1` | 8 / 12 | 8 / 12 |
| `PLANES_PIX0 / PLANES_PIX1` | 5 / 5 | 5 / 5 |
| `AUTO_ENABLE / AUTO_DISABLE` | 1 / 1 | 1 / 1 |
| `SWAP_REFUSALS / SWAP_RECOVERED / RETRY_VBLS` | 121 / 121 / 121 | 121 / 121 / 121 |
| `CLOSE_RETURNED` | 1 | 1 |

**Byte-exact CRLF evidence:** [Runtime, 1,632 bytes](../../docs/evidence/M19_P2_ALL_IN_ONE_RUNTIME_PASS_2026-11-21.TXT), SHA256 `864f6b17652033b99f06ec34df3ce85f3a1579bbb52c033d67d62e178852c627` · [Compiled, 1,633 bytes](../../docs/evidence/M19_P2_ALL_IN_ONE_COMPILED_PASS_2026-11-21.TXT), SHA256 `296f562f73a83d91f419d60a4538e35ef05d55f0c159012949fc5482ce88bf41`.

**Important:** all **121 initial `Aga Swap` refusals** recovered after one extra VBL. Do not silently drop or reinterpret that counter in future versions. The PASS results do not prove zero refusals, performance limits or behaviour on every machine.

**Scope:** Gate B Runtime and Gate C true AMOS Compiler **PASS for this exact test scenario and installed P2d library** under WinUAE, as evidenced by the supplied logs. Strict interpreted Gate B and physical Amiga Gate D were not tested. No `LAST_GOOD` promotion, new native binary, or blanket revalidation of other AGA APIs.
