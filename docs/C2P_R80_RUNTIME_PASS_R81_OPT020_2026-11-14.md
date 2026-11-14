# R80 Runtime PASS et R81 OPT020 Gate A — 14/11/2026

## Validation R80 réelle sous WinUAE

Le journal utilisateur `C2P_R80_RUNTIME.TXT` (transmis le 14 novembre 2026) atteste le scénario **Runtime** sur CPU **68030** (`CPU_ATTNFLAGS 32823`) et image **320×256×8 plans**, 256 couleurs `DH6:iff-TEST/AGA_DEMO_320x256_256c.iff`.

- `PRG_STATE 1`, `RUN_MODE RUNTIME` ; ce n'est **pas** une Gate C AMOS Compiler.
- `RESULT 1`, `VERDICT PASS`, `ERR 0` ; `LOAD12_OK 1`, `LOAD13_OK 1`, `INVALID_BANK_OK 1`.
- `IFF_OK 1`, `PALETTE_OK 1`, `CHUNKY_OK 1`, `C2P_BASE_OK 1`, `BLIT_OK 1`, `ZOOM_OK 1`.
- `PIXEL_CHECK_COUNT 14`, `GOLDEN_PIXEL_COUNT 14`, `INVALID_CALLS_OK 1`, `REOPEN_OK 1`, `ESC_OK 1`, `SCREEN_CLOSE_COUNT 1`, `CLOSE RETURNED`.
- `CHIP_BEFORE 1383224` / `CHIP_AFTER 1383224` ; `FAST_BEFORE 130314944` / `FAST_AFTER 130314944` ; **deltas 0/0**.

**Portée :** Gate B de R80 PASS pour ce cas Runtime 8 plans, sans déduire un PASS 4–7 plans ou une compilation AMOS. La Gate C est volontairement **non réalisée** à la demande de l'auteur.

## Optimisation R81 indépendante

La R81 conserve les **70 commandes et 77 entrées AP20** de R80 ; les entrées natives **73/74/75** sont remplacées par les variantes MC68020 sans toucher aux anciens générateurs épinglés.

| Entrée | Commande | Noyau OPT020 |
| --- | --- | --- |
| 73 | `Aga C2P Blit` | copies `MOVE.L` par 4 pixels, résidu `MOVE.B` |
| 74 | `Aga C2P Zoom` | paramètres DDA horizontaux en registres plutôt que relectures mémoire par pixel |
| 75 | `Aga Iff To Chunky` | LUT de 16 nibbles, adressage indexé 020, deux `OR.L` pour huit pixels/plans |

**Véritable Gate A CPU MC68020 PASS** : [CI 43615716395](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43615716395), 22 cas Blit, 14 Zoom, 15 lignes IFF reconstruites bit à bit, rejet 68000 avant les opcodes exclusifs, intégrité AP20/ABI, et CI complète réussie. Générateur R81 déterministe : `59 972 octets`, SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`.

**Aucun chronométrage revendiqué** ; gains architecturaux implémentés, performances non quantifiées. Aucun nouveau test AMOS Compiler ; la Gate B Runtime R81 est ensuite passée indépendamment sur l'IFF 320×256×8, CPU 68030 : [rapport Gate B R81](C2P_R81_RUNTIME_GATE_B_2026-11-14.md). Aucun benchmark de vitesse ni nouvel essai Compiler n'est revendiqué.
