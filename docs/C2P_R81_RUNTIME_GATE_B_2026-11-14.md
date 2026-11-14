# R81 v0.13.26 OPT020 — Gate B WinUAE Runtime PASS (14/11/2026)

## Journal réel transmis par l'auteur

**Fichier :** `C2P_R81_RUNTIME.TXT` (14 novembre 2026). Le journal identifie `TEST C2P-R81-OPT020-01` et `VERSION R81 V0.13.26 OPT020 CANDIDATE`. L'unique ASC actif du dépôt conserve son nom historique [`tests/current/C2P_R80_IFF_CHUNKY_01.asc`](../tests/current/C2P_R80_IFF_CHUNKY_01.asc), mais écrit les journaux de R81.

| Rubrique | Données exactes du journal |
| --- | --- |
| Mode d'exécution | `RUN_MODE RUNTIME`, `PRG_STATE 1` |
| CPU | `CPU 68030`, `CPU_ATTNFLAGS 32823` |
| Source IFF/chunky | `DH6:iff-TEST/AGA_DEMO_320x256_256c.iff` pour les deux |
| Image | `IMAGE_WIDTH 320`, `IMAGE_HEIGHT 256`, `IMAGE_DEPTH 8`, `SCREEN_COLORS 256` |
| Référence | `GOLDEN_REFERENCE 1`, `GOLDEN_PIXEL_COUNT 14` |
| Chargement et refus banque | `LOAD12_OK 1`, `LOAD13_OK 1`, `INVALID_BANK_OK 1` |
| Décodage et couleurs | `IFF_OK 1`, `PALETTE_OK 1`, `CHUNKY_OK 1` |
| Conversion / optimisation | `C2P_BASE_OK 1`, `BLIT_OK 1`, `ZOOM_OK 1` |
| Contrôles des pixels | `PIXEL_CHECK_OK 1`, `PIXEL_CHECK_COUNT 14` |
| Refus / cycles d'écran | `INVALID_CALLS_OK 1`, `REOPEN_OK 1`, `ESC_OK 1`, `SCREEN_CLOSE_COUNT 1` |
| Résultat | **`RESULT 1` ; `VERDICT PASS` ; `ERR 0` ; `CLOSE_RETURNED`** |

## Mémoire libre

| Zone | Avant | Après | Delta journalisé |
| --- | ---: | ---: | ---: |
| Chip RAM | **1 249 000** | **1 249 000** | **0 octet** |
| Fast RAM | **127 851 704** | **127 851 704** | **0 octet** |

Aucune perte **nette** de mémoire entre les deux relevés. Cela ne mesure pas le pic de consommation pendant l'exécution.

## Portée de la qualification

- **Gate A native/CI R81 : PASS.** [CI générale 65 étapes PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43617105778). [Gate A des 3 noyaux](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43615716395) : 22 cas Blit, 14 Zoom, 15 lignes IFF, refus 68000.
- **Gate B R81 WinUAE Runtime : PASS** pour le scénario avec IFF **320×256×8 plans, 256 couleurs**, CPU **68030**. Cette preuve est **indépendante du PASS Runtime R80**.
- **Gate C AMOS Compiler : NON TESTÉE**, conformément à la demande expresse de l'auteur de passer aux optimisations sans nouvelle compilation. `PRG_STATE 1` ne prouve pas un exécutable compilé.
- **Gate D Amiga réel : NON TESTÉE.** Ce seul journal n'étend pas la Gate B de R81 aux profondeurs 4–7 plans, à d'autres images ou CPU ; aucune mesure comparative de vitesse R80/R81 n'est fournie.
- **Candidate active R81 v0.13.26** : `dist/AMOSPro_AGA.Lib`, **59 972 octets**, SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`, **70 commandes / 77 entrées AP20**. Ce SHA provient de la construction GitHub, et non du journal utilisateur.
- **Aucune promotion** : `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste R73 v0.13.18, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`.

**Verdict au moment de ce journal : Gate B Runtime R81 PASS.** L'auteur a transmis ensuite `C2P_R81_COMPILED.TXT` : [Gate C compilée R81 PASS](C2P_R81_COMPILER_GATE_C_2026-11-14.md). Aucune promotion ni mesure de vitesse revendiquée.
