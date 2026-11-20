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

## 2. M19 stabilisée, début de M20

**B8 S1 est conservée comme candidate validée en Runtime** : deux journaux transmis, chacun 405/405 frames, ERR 0 et PATH_OK. Aucun nouveau cycle de test Compiler n'est demandé. La Gate C S1 reste reportée ; R84 LAST_GOOD n'est pas promue.

**Démarrage M20 P0 :** [modèle hôte de tilemap/scrolling sur deux pages](M20_TILEMAP_P0_HOST_MODEL.md) et [13 tests pixel-exacts PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44789691639). Les tests vérifient le décalage de caméra **par page physique**, le redessin de zones exposées, les éditions dynamiques de carte, l'absence de fantômes Bob et un scénario de 405 frames **simulées en Python**, non WinUAE.

**Verrous avant le moteur M20 natif :** choix du format de tuiles, des masques, des banques, des copies planaires non alignées, de la synchronisation Safe/Disp et du budget Fast/Chip. Aucun nouveau token AP20 n'est créé. La Lib S1 et l'ASC de campagne restent inchangés.

## 3. Travaux après M19

| Sujet | Objectif |
| --- | --- |
| **Bobs et animations** | Stabiliser le cycle `Clear → Update → Swap`, les banques et les erreurs, puis optimiser uniquement sur mesures. |
| **Sprites AGA / AMAL** | Évaluer slots matériels, DMA, collisions et intégration éventuelle avec AMAL. |
| **Tilemaps / scrolling (M20)** | **P0 modèle hôte et 13 tests PASS**, caméra, bandes exposées et deux pages indépendantes ; [spécification et limites](M20_TILEMAP_P0_HOST_MODEL.md). Implémentation native à concevoir, pas de nouveau token. |
| **Dual playfield (M21)** | Plans indépendants, palettes et scrolling. |
| **Entrées (M22)** | Vérifier d'abord les commandes joysticks natives, sans inventer une API AGA. |
| **C2P / Copper (M23/M24)** | Évaluer accélérations et API avec preuve CPU, WinUAE et Compiler. |

Historique non normatif : [Roadmap archivée](ROADMAP_HISTORY_2026-11-17.md) · [reprise technique](NEXT_SESSION.md).
