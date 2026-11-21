# M19 P1c — validation WinUAE du banc de priorité

**21 novembre 2026.** P1c active, 119 916 octets, SHA256 `658717f41e73ea0410ddcea682929d357df1a80fefd40d8ae0dece037a37613c`. [Livraison](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/7e550b75d47c183b54799d16e050d92e67bffd89) · [CI Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44887213453) · [Protocole](../tests/current/README.md).

| Journaux transmis | Mode | SHA256 du journal brut |
| --- | --- | --- |
| `M19_P1C_PRIORITY1.TXT`, `M19_P1C_PRIORITY2.TXT` | Runtime, `PRG_STATE 1` | `2253abfddeeb141e690cd369fa971239a72bbbdcd75a54530682605e17357ddc` pour chacun |
| `M19_P1C_PRIORITY.TXT` | Compilé, `PRG_STATE -1` | `e65fb96f00bf81c573c94f6ec0d107d9d0b4998384222b7cd38430f6d3e81ae6` |

Chaque passage rend `RESULT 1`, `ERR 0`, `PATH_OK`. Les 405 frames et les neuf étapes passent, dont celle à 64 Bobs. Les quatre phases hotspot passent avec 12 lectures exactes, en plus des 42 getters de régression. Les huit sondes de chevauchement sur les deux pages relèvent `5,5,4,4,4,4,5,5`. Les 16 appels avec un mode invalide sont refusés. Clear, Update et Swap comptent zéro échec. La fermeture revient à AMOS et les quatre banques sont effacées.

**Gate B Runtime et Gate C Compiler PASS sur les contrôles mesurés.** Les deux fichiers Runtime sont identiques octet pour octet. La continuité de la session AMOS et le rendu visuel des quatre phases hotspot n'ont pas été documentés dans les fichiers fournis. Le champ `LIB_SHA256` reprend la constante du banc. Gate D Amiga physique à tester. P0 reste `LAST_GOOD`.
