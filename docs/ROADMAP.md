# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 21 novembre 2026.** Ce document décrit l'état actuel et les priorités. Les preuves et jalons historiques sont dans [NEXT_SESSION.md](NEXT_SESSION.md) et [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md).

## 1. Référence de travail

| Élément | État |
| --- | --- |
| **Bibliothèque active** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **M19 P1b, candidate WinUAE**, **119 176 octets**, SHA256 `2bf9a3bb46725c8cd3a65042fec06b35e71b5e4a0876201b1e7e874388fe48d4`, **92 commandes / 188 AP20** et cinq groupes MC68020, PC16 max **31 444**. [Builder](../tools/build_m19_p1b_hotspot_in_memory.py) ; [Gate A intégrée PASS, 98 contrôles](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44836896149). **Gates B/C/D P1b en attente.** |
| **ASC unique de campagne** | [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **17 566 octets** : **405 frames** + **4 phases hotspot**, 14 × 3 getters P1a préservés. [AGBO banque 26](../tests/current/M19_P1B_HOTSPOT_BANK26.abk), 200 octets, hot=(4,3). Journal `RAM:M19_P1B_HOTSPOT.TXT`. [Protocole](../tests/current/README.md). |
| **Qualification P0** | **Gate A native MC68020 PASS : 104 contrôles préparation Chip + 121 Bank Free** (OS/Blitter simulés, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756)). **Gate B WinUAE Runtime P0 : PASS fonctionnel sur les journaux fournis** ([rapport et limites](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md)) ; **Gate C Compiler reportée**, Gate D matériel non testée. |
| **LAST_GOOD promue P0** | [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, **distinct de la Lib active P1b et conservé sans modification** ; [promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/71ff3862929b729bb44db20294aec9b048775cbf). Ancienne R84, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, récupérable dans Git et par builder. Gate C P0 non testée. |

**Historique distinct :** B8 S1 SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a` a passé deux essais Runtime à 405/405 frames. Ce résultat ne qualifie pas la nouvelle P0. La B7-m2 (102 400 octets ; SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`) est la référence antérieure ; **ses Gates Runtime et Compiler PASS ne s'appliquent pas à B8**. [Preuves B7-m2](M19_B7M2_GATES_BC_2026-11-19.md).

## 2. M19 — P0 LAST_GOOD ; P1a Runtime PASS ; P1b installée pour Gate B

**P0 fonctionnelle conservée dans la Lib active P1b et dans LAST_GOOD P0 :** `Aga Bob Bank N` prépare en Chip les images AGBO d'une banque peuplée (aucune allocation si vide) ; `Aga Bob Bank Free N` désactive les Bobs dépendants, attend `WaitBlit`, libère le cache privé **sans effacer la banque AMOS**. Opération idempotente, refus pendant `READY`/`DIRTY`, nouvelle sélection pour réactiver. [Rapport et limites](M19_P0_BANK_FREE_GATES_2026-11-20.md).

**État :** P0 terminée et promue `LAST_GOOD`, Gate A 225 contrôles et Gate B Runtime PASS fonctionnel. P1a getters X/Y/I Gate A 110 contrôles, **Gate B Runtime PASS fonctionnel (2 × 405 frames, 42/42 valeurs)** ([rapport](M19_P1A_RUNTIME_B_2026-11-21.md)). **P1b Hot Spot est maintenant intégrée et installée dans l'unique Lib de test**, avec image AGBO masquée et hotspots par image : [rapport P1b](M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md), Gate A MC68020 intégrée PASS ; **Gates B/C/D P1b NON TESTÉES**. Aucune nouvelle commande publique. M19 global reste ouvert : priorités, `Limit Bob`, édition Del/Ins, collisions et Sprites après tests P1b.

**Action suivante :** lancer deux essais Runtime WinUAE sur **P1b** suivant [le protocole de campagne](../tests/current/README.md), sauvegarder les journaux et observer les quatre décalages/masques. Après résultats, décider de la suite de P1 et de la Gate C vrai Compiler. La CI `Artifact integrity` historique possède encore des contrôles d'anciennes SHA à migrer ; ses échecs ne valent pas une Gate B ni une preuve de bug P1b.

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
