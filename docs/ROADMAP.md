# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 20 novembre 2026.** Ce document décrit l'état actuel et les priorités. Les preuves et jalons historiques sont dans [NEXT_SESSION.md](NEXT_SESSION.md) et [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md).

## 1. Référence de travail

| Élément | État |
| --- | --- |
| **Bibliothèque active** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) — **M19 B8 S1 SafePort**, **116 104 octets**, SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a`, 88 commandes / 184 entrées AP20, cinq groupes MC68020 `[142,153,156,177,181]`, PC16 max 29 962. [Builder S1 byte-exact](../tools/build_m19_b8_safe_retry_in_memory.py). B8 ancienne conservée dans Git. |
| **ASC unique de campagne** | [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **11 092 octets**, provenance SHA S1 ; **aucun VBL artificiel dans la boucle**, [protocole WinUAE](../tests/current/README.md). |
| **Validation S1** | **Gate A MC68020 PASS** (119 contrôles SafePort, [CI 44780312459](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44780312459)). **Gate B WinUAE Runtime PASS sur deux journaux S1 fournis** : 405/405 frames, 9 étapes, 403 Clear, 405 Update, 50 Off, 0 échec et PATH_OK, sans VBL supplémentaire dans la boucle. **Gate C AMOS Compiler reportée** à la demande de l'auteur ; Gate D matériel non testée. |
| **Référence protégée** | [R84 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` — intacte, aucune promotion B8. |

La B7-m2 (102 400 octets ; SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`) est la référence antérieure ; **ses Gates Runtime et Compiler PASS ne s'appliquent pas à B8**. [Preuves B7-m2](M19_B7M2_GATES_BC_2026-11-19.md).

## 2. M19 EN COURS — préparation Chip des banques Bob

**M19 n'est pas terminé.** B8 S1 conserve sa Gate A native et ses deux PASS Runtime ; Gate C Compiler reste reportée. Le chantier Bobs comprend encore `Aga Bob Bank Free N`, lectures X/Y/Image, hotspots, priorités, clipping, édition de banques, collisions et transformations ; la phase Sprites vient ensuite.

**Sous-étape actuelle P0 :** [préparation Chip lors de `Aga Bob Bank N`](M19_P0_BANK_PRESTAGE_2026-11-20.md). Le wrapper MC68020 et le builder AP20 sont **expérimentaux, source-only** ; ils conservent 88 commandes et 184 entrées, et ne modifient pas la Lib S1. **Gate A en cours**. La banque vide ne reçoit aucune allocation ; une banque peuplée doit être préparée avant le premier dessin, avec contrôles de sécurité et rollback.

**Étape suivante :** qualifier le cycle de cache Chip et le futur `Aga Bob Bank Free N` avec les objets actifs, avant tout ajout public ou installation. Aucun nouvel essai Compiler demandé.

**M20 EN ATTENTE :** le prototype Python P0 (13 tests hôtes PASS) existe dans le dépôt, mais n'est pas la prochaine étape. Aucune poursuite de M20 P1 sans clôture et décision explicite sur M19.

## 3. Chantiers ultérieurs (non engagés)

| Sujet | Objectif |
| --- | --- |
| **Bobs et animations** | Stabiliser le cycle `Clear → Update → Swap`, les banques et les erreurs, puis optimiser uniquement sur mesures. |
| **Sprites AGA / AMAL** | Évaluer slots matériels, DMA, collisions et intégration éventuelle avec AMAL. |
| **Tilemaps / scrolling (M20)** | **P0 modèle hôte et 13 tests PASS**, caméra, bandes exposées et deux pages indépendantes ; [spécification et limites](M20_TILEMAP_P0_HOST_MODEL.md). Implémentation native à concevoir, pas de nouveau token. |
| **Dual playfield (M21)** | Plans indépendants, palettes et scrolling. |
| **Entrées (M22)** | Vérifier d'abord les commandes joysticks natives, sans inventer une API AGA. |
| **C2P / Copper (M23/M24)** | Évaluer accélérations et API avec preuve CPU, WinUAE et Compiler. |

Historique non normatif : [Roadmap archivée](ROADMAP_HISTORY_2026-11-17.md) · [reprise technique](NEXT_SESSION.md).
