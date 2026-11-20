# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 21 novembre 2026.** Ce document décrit l'état actuel et les priorités. Les preuves et jalons historiques sont dans [NEXT_SESSION.md](NEXT_SESSION.md) et [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md).

## 1. Référence de travail

| Élément | État |
| --- | --- |
| **Bibliothèque active** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) — **M19 P1a, candidate WinUAE**, **118 816 octets**, SHA256 `165a24edcd4c00074d6ddce4a98317f720ed3236d61ba006333574743b55063a`, **92 commandes / 188 entrées AP20**, cinq groupes MC68020 `[142,153,156,177,181]`, PC16 max **31 092**. [Builder exact](../tools/build_m19_p1a_getters_in_memory.py), [Gate A P1a PASS (110 contrôles)](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829640179). **Gate B P1a PASS fonctionnel sur deux journaux WinUAE** ([preuves](M19_P1A_RUNTIME_B_2026-11-21.md)); Compiler C et matériel D non testés. |
| **ASC unique de campagne** | [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **14 871 octets**. Neuf étapes / 405 frames P0 préservées, trois phases Free/réactivation, **14 lectures × 3 champs = 42 valeurs** ; journal `RAM:M19_P1A_BOB_GETTERS.TXT`. [Protocole](../tests/current/README.md). |
| **Qualification P0** | **Gate A native MC68020 PASS : 104 contrôles préparation Chip + 121 Bank Free** (OS/Blitter simulés, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756)). **Gate B WinUAE Runtime P0 : PASS fonctionnel sur les journaux fournis** ([rapport et limites](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md)) ; **Gate C Compiler reportée**, Gate D matériel non testée. |
| **LAST_GOOD promue P0** | [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, **distinct de la Lib active P1a et conservé sans modification** ; [promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/71ff3862929b729bb44db20294aec9b048775cbf). Ancienne R84, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, récupérable dans Git et par builder. Gate C P0 non testée. |

**Historique distinct :** B8 S1 SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a` a passé deux essais Runtime à 405/405 frames. Ce résultat ne qualifie pas la nouvelle P0. La B7-m2 (102 400 octets ; SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`) est la référence antérieure ; **ses Gates Runtime et Compiler PASS ne s'appliquent pas à B8**. [Preuves B7-m2](M19_B7M2_GATES_BC_2026-11-19.md).

## 2. M19 — P0 LAST_GOOD ; P1a active pour Gate B WinUAE

**P0 fonctionnelle conservée dans la Lib active P1a et dans LAST_GOOD P0 :** `Aga Bob Bank N` prépare en Chip les images AGBO d'une banque peuplée (aucune allocation si vide) ; `Aga Bob Bank Free N` désactive les Bobs dépendants, attend `WaitBlit`, libère le cache privé **sans effacer la banque AMOS**. Opération idempotente, refus pendant `READY`/`DIRTY`, nouvelle sélection pour réactiver. [Rapport et limites](M19_P0_BANK_FREE_GATES_2026-11-20.md).

**État :** **P0 terminée et promue LAST_GOOD sur décision explicite**, **Gate A 225 contrôles PASS**, **Gate B Runtime PASS fonctionnel sur journaux** (deux fichiers identiques ; visuel non contrôlé), Gates C/D P0 non testées. **M19 global reste ouvert** : P1 lectures X/Y/Image, hotspots, priorités et clipping ; puis édition des banques, collisions, transformations et Sprites selon décisions. **P1 source-only :** préparation `object_read` et `set_hotspot` AGBO [PASS](M19_P1_BOB_READ_HOTSPOT_SOURCE_2026-11-20.md), puis **P1a trois getters X/Y/I** avec shims MC68020 et tokens AP20 dans un **builder en mémoire**, 110 contrôles Gate A [PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44829476430). [Rapport P1a](M19_P1A_BOB_GETTERS_GATE_A_2026-11-20.md). **Bascule P1a explicitement autorisée : trois tokens installés dans la seule Lib active, LAST_GOOD P0 inchangée ; ASC actif prolongé de 42 contrôles. **Gate B P1a PASS fonctionnel (2 × 405 frames, 42/42 lectures, 0 erreur)** ; [rapport](M19_P1A_RUNTIME_B_2026-11-21.md).**

**Régressions CI avant promotion P0 : PASS** ([Artifact integrity](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44823490337) et [politique CPU/chemins](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44823490306), code au commit `05c283a6`). **Action suivante :** **P1b Hot Spot natif**, commencer par l'audit de la chaîne AGBO → cache Chip → Safe Blit et les tests MC68020 source-only. **Ne pas changer la Lib P1a active ni promouvoir `LAST_GOOD` P0.** Puis priorités et clipping après validation. Le dernier contrôle global d'intégrité doit rester affiché séparément des Gates. Gate C Compiler P0 toujours non testée ; M20 reste en attente.

**M20 EN ATTENTE :** prototype Python P0 (13 tests hôtes PASS) conservé ; aucune poursuite avant décision sur M19.

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
