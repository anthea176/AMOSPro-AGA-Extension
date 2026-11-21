# M19 P2a — Collisions Bob–Bob sous WinUAE

**ASC unique de campagne** — [M19_P2A_BOB_COL.asc](M19_P2A_BOB_COL.asc), 3 358 octets ASCII LF, SHA256 `dfb44261c99979b7000e7ae1b2f0ec364b6538687173f25235a20f007bf5e2f4`. Le banc crée ses propres images AGBO. Il requiert deux banques AMOS libres, **24 et 25**.

**Lib active** — [AMOSPro_AGA.Lib](../../dist/AMOSPro_AGA.Lib), P2a, 129 544 octets, SHA256 `e2d149f67da9eb3a8c7222113338a8e0ad3f08fb512792a54b825987e88d92fe`. La [référence LAST_GOOD](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) reste P1e.

## Exécution

1. Copier la Lib P2a dans l'emplacement habituel sous `APSystem` et redémarrer AMOS Pro. Utiliser WinUAE en AGA avec un MC68020 ou supérieur.
2. Dans un programme vierge, importer [M19_P2A_BOB_COL.asc](M19_P2A_BOB_COL.asc) via **Project → Merge ASCII**.
3. Lancer en **Runtime** et relever `RAM:M19_P2A_BOB_COL.TXT`.

| Contrôle | Valeur attendue |
| --- | --- |
| `PRG_STATE`, `RESULT`, `ERR` | `1`, `1`, `0` |
| `RECT_HOLE`, `MASK_HOLE` | `1`, `0` |
| `RECT_SOLID`, `MASK_SOLID` | `1`, `1` |
| `CLIPPED`, `RESET` | `0`, `1` |
| `BAD_MODE`, `BOB_OFF` | `-1`, `-1` |
| `CHECKS`, `CLOSE_RETURNED`, `VERDICT` | `8`, `1`, `PASS` |

Gate A couvre le préflight et les tests natifs sous émulation MC68020. Gate B Runtime, Gate C AMOS Compiler et Gate D matérielle restent à établir sur P2a. Le [banc P1e précédent](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/6b7b8e213a870996d77684541130d050f2a02b1b/tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc) reste accessible dans Git avec ses [instructions historiques](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/6b7b8e213a870996d77684541130d050f2a02b1b/tests/current/README.md).
