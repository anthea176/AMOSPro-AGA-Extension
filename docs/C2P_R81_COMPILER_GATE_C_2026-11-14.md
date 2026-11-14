# R81 v0.13.26 OPT020 — Gate C AMOS Compiler PASS (14/11/2026)

## Preuve de l'exécutable compilé sous WinUAE

Journal transmis par l'auteur : **`C2P_R81_COMPILED.TXT`**.

| Contrôle | Valeur dans le journal |
| --- | --- |
| Identification | `TEST C2P-R81-OPT020-01`, `VERSION R81 V0.13.26 OPT020 CANDIDATE` |
| Exécution | **`RUN_MODE COMPILED`, `PRG_STATE -1`** |
| CPU | **68030** ; `CPU_ATTNFLAGS 32823` |
| IFF chargé en deux banques | `DH6:iff-TEST/AGA_DEMO_320x256_256c.iff`, `LOAD12_OK 1`, `LOAD13_OK 1` |
| Image | `IMAGE_WIDTH 320`, `IMAGE_HEIGHT 256`, `IMAGE_DEPTH 8`, `SCREEN_COLORS 256` |
| Pixels de référence | `GOLDEN_REFERENCE 1`, `GOLDEN_PIXEL_COUNT 14`, `PIXEL_CHECK_OK 1`, `PIXEL_CHECK_COUNT 14` |
| Fonctions | `IFF_OK 1`, `PALETTE_OK 1`, `CHUNKY_OK 1`, `C2P_BASE_OK 1`, `BLIT_OK 1`, `ZOOM_OK 1` |
| Refus et cycle de vie | `INVALID_BANK_OK 1`, `INVALID_CALLS_OK 1`, `REOPEN_OK 1`, `ESC_OK 1`, `SCREEN_CLOSE_COUNT 1` |
| Verdict | **`RESULT 1`, `VERDICT PASS`, `ERR 0`, `CLOSE_RETURNED`** |

### Mémoire

| Mémoire libre | Avant | Après | Variation |
| --- | ---: | ---: | ---: |
| Chip RAM | 1 313 104 | 1 313 104 | **0 octet** |
| Fast RAM | 130 096 560 | 130 096 560 | **0 octet** |

**Les variations à zéro ne constituent pas une mesure du pic de mémoire en cours d'exécution.**

## Statut consolidé

- **Gate A native / intégrité : PASS** — [CI R81](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43617105778), [tests des noyaux](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43615716395).
- **Gate B Runtime WinUAE : PASS** — [rapport R81 Runtime](C2P_R81_RUNTIME_GATE_B_2026-11-14.md), `PRG_STATE 1`, CPU 68030, IFF de référence 8 plans, 14/14 pixels.
- **Gate C AMOS Compiler : PASS** — *nouveau journal `C2P_R81_COMPILED.TXT`*, `PRG_STATE -1`, CPU 68030, IFF 320×256×8, 14/14 pixels, toutes fonctions et refus à 1, `ERR 0`, RAM sans perte nette, fermeture correcte.
- **Gate D matériel Amiga : NON TESTÉE**.
- **Limites** : la Gate C attestée vaut pour **ce scénario 8 plans / 256 couleurs sur CPU 68030** ; pas de qualification compilée déduite pour 4–7 plans ni de preuve de gain de vitesse. La Gate C est désormais **réalisée**, contrairement au plan antérieur qui n'en demandait pas une nouvelle.
- **R81 candidate non promue** : `dist/AMOSPro_AGA.Lib` reste R81 v0.13.26, 59 972 octets, SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4` ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` demeure **R73**. Aucune promotion ni modification de binaire autorisée par ce rapport.

**Verdict : R81 OPT020 Gates A, B Runtime et C compilée PASS dans les périmètres documentés.**
