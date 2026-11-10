# AMOSPro-AGA — R8 0.5.9, Safe/Disp synchronization

**STATUS: WinUAE PARTIAL PASS 5/5 (single Swap + Close, no IFF). Independent Unicorn CPU, CI and extended runtime still pending. DO NOT PROMOTE TO `main` OR LAST_GOOD.**

Single development branch intended: `codex/intuition-input-r1`, PR #4 only.
Base binary R7 0.5.8 (5/5 successful runtime on `Aga Double Buffer` without `Aga Swap`). Base SHA256: `e6dd32ceda1181ef3172dfb242a1d4fc93656c6788023d7b1333dc2561ed3dce`.

## Changes from R7

- Entry 11 `Aga Swap`: nonblocking `GetMsg` polling for pending Safe/Disp notifications; no second `ChangeScreenBuffer` until both previous notifications are received. On successful switch only, store pending=3 at DBState+20; on failure keep pending 0. A successful call still returns `D3=1,D2=0`. No `WaitPort`, no Exec `Wait`.
- Entry 8 `Aga Screen Close`: preflight synchronization **before** touching Intuition Window, ScreenBuffers, ports or Screen. Cooperative `GetMsg`/`WaitTOF`; if it cannot synchronize in 300 VBL cycles, it aborts closure and keeps **all** resources (and the Window) alive. A subsequent Close can retry. Retains previous ABI and original Close code after preflight.
- Entry 0 extension shutdown: equivalent preflight, plus old unreachable `WaitPort` code explicitly bypassed and replaced by NOPs (without relocating other code).
- Entries 17/18 `Aga Key` / `Aga Wait Key`: only the Ctrl+C cleanup path is guarded by the same synchronization; Ctrl+C Break is suppressed on timeout rather than freeing buffers still referenced by Intuition. Normal keys, Ctrl-alone filtering, and AMOS_WB(1)/native Test_PaSaut on successful cleanup are unchanged.
- **DBState+20:** bit 0=Safe reply pending, bit 1=Disp reply pending. Uses the existing 24-byte DBState allocation. Both bits are set after a successful ChangeScreenBuffer. A corresponding bit is cleared *only* when the relevant port's `GetMsg()` returns a message. These replies have already been `ReplyMsg()`'d by Intuition/graphics, therefore **no `ReplyMsg()` is performed** on them.
- Entry 10 Double Buffer allocation is **bit-for-bit identical** to R7; all Generic ILBM R2 and PicInfo code is unchanged.

## Failure policy

No pending replies → no extra wait; old R7 Close/Break sequence executes normally.
Pending replies → GetMsg both ports, WaitTOF and retry, up to 300 VBLs. If still pending, **leave Window/Screen/DBState/ScreenBuffers/ports allocated**. No forced free, no Guru; no Ctrl+C Break upon timeout. An application that calls `Aga Screen Close` gets no return status (existing statement API): after timeout, the Screen remains open; the application may attempt closure again after a delay. This is intentional memory safety, not a complete user-visible error reporting mechanism.

## Remaining risks (must validate)

1. This R8 is a static/model candidate. The actual 68000 code path has **not** been executed by Unicorn or native AMOS. Do not claim CPU PASS or runtime PASS.
2. `Aga Swap` can return with Safe/Disp messages in flight. The extension blocks subsequent **Swap** until both arrived and delays **Close**, but the caller must not draw/modify an old bitmap before the Safe reply. The unchanged ILBM loader is not instrumented to wait for Safe; do not perform back-to-back loader updates immediately after Swap without further validation of drawing safety.
3. If Intuition never replies, the timeout preserves resources. The calling program can continue and might need to retry closure; this state must be exercised under WinUAE.
4. Real project builder needs GitHub CI execution with Unicorn tests and exact matching `dist/AMOSPro_AGA.Lib` vs the versioned archive before exposing R8 as runtime-testable.
5. Full WinUAE validation needed with simple swap only before image load + Swap, normal keyboard close, Ctrl+C while swap in flight, repeated Open/Swap/Close. Include WinUAE JIT on/off if necessary.

## Reference sources

- https://d0.se/autodocs/graphics.library/AllocDBufInfo — Safe/Disp replies, semantics and wait-before-free requirements.
- https://d0.se/autodocs/intuition.library/ChangeScreenBuffer — V39+ asynchronous screen bitmap switch.
- https://wiki.amigaos.net/wiki/Intuition_Screens — reply messages are NOT to be replied to again by consumer.

## Local artifacts

- `tools/ap20_utils.py` — AP20/HUNK exact parse/rebuild and tiny labelled 68000 emitter.
- `tools/build_r7_reconstruction.py` — verifies exact deterministic R7 base from R6 and its SHA256.
- `tools/build_db_safe_r8.py` — reproducible candidate builder, asserts all unchanged segments.
- `tools/test_db_sync_r8.py` — byte-level tests and 2,000 randomized state-machine model scenarios (**not** CPU execution).
- `tests/current/M5_DB_SYNC_R8.asc` — single Swap/Close test, **do not run before Unicorn/CI**.
- `dist/experimental/AMOSPro_AGA_M5_v0.5.9_DB_SYNC_R8.Lib` and `dist/AMOSPro_AGA.Lib` — same local candidate.

## Validation utilisateur R8 — 10/11/2026

**PASS 5/5 en WinUAE** : 640×512×4, un `Aga Swap` réussi, `Aga Wait Key=68`, puis `Aga Screen Close` et retour AMOS, sans IFF. Les Swaps multiples, Ctrl+C pendant Swap et IFF Fallout ne sont pas couverts. R8 déjà synchronisée sur la branche unique, binaire 8 772 octets, SHA256 `112dce3e7945a235430a0263e309126061639de0d8dcc0d9c319431b0f2f27a2`. CI R8 indépendante encore à confirmer ; PR #4 reste Draft.

