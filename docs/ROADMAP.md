# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 21 novembre 2026.** Ce document décrit l'état actuel et les priorités. Les preuves et jalons historiques sont dans [NEXT_SESSION.md](NEXT_SESSION.md) et [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md).

## 1. Référence de travail

| Élément | État |
| --- | --- |
| **Bibliothèque active** | [M19 P1c](../dist/AMOSPro_AGA.Lib), candidate WinUAE, 119 916 octets, SHA256 `658717f41e73ea0410ddcea682929d357df1a80fefd40d8ae0dece037a37613c`, 93 commandes, 190 entrées AP20, PC16 maximal 32 144. [Gate A PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44886543740). Gates B/C/D à tester. |
| **ASC unique de campagne** | [M19_B8_BOB_CLEAR_UPDATE_BC_01.asc](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), 405 frames, quatre phases hotspot, huit sondes de priorité et banque AGBO 26. Journal `RAM:M19_P1C_PRIORITY.TXT`. |
| **Qualification P0** | **Gate A native MC68020 PASS : 104 contrôles préparation Chip + 121 Bank Free** (OS/Blitter simulés, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756)). **Gate B WinUAE Runtime P0 : PASS fonctionnel sur les journaux fournis** ([rapport et limites](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md)) ; **Gate C Compiler reportée**, Gate D matériel non testée. |
| **LAST_GOOD promue P0** | [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, **distinct de la Lib active P1c et conservé sans modification** ; [promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/71ff3862929b729bb44db20294aec9b048775cbf). Ancienne R84, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, récupérable dans Git et par builder. Gate C P0 non testée. |

**Historique distinct :** B8 S1 SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a` a passé deux essais Runtime à 405/405 frames. Ce résultat ne qualifie pas la nouvelle P0. La B7-m2 (102 400 octets ; SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`) est la référence antérieure ; **ses Gates Runtime et Compiler PASS ne s'appliquent pas à B8**. [Preuves B7-m2](M19_B7M2_GATES_BC_2026-11-19.md).

## 2. M19 — P1c active pour la Gate B

**P0 fonctionnelle conservée dans la Lib active P1c et dans LAST_GOOD P0 :** `Aga Bob Bank N` prépare en Chip les images AGBO d'une banque peuplée (aucune allocation si vide) ; `Aga Bob Bank Free N` désactive les Bobs dépendants, attend `WaitBlit`, libère le cache privé **sans effacer la banque AMOS**. Opération idempotente, refus pendant `READY`/`DIRTY`, nouvelle sélection pour réactiver. [Rapport et limites](M19_P0_BANK_FREE_GATES_2026-11-20.md).

P1a (getters) et P1b (hotspot) ont passé leur campagne Runtime. P1c expose `Aga Bob Priority(Mode)` et conserve le tri initial par ID au mode 0. [Rapport P1b](M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md#résultats-runtime-winue).

**Action suivante** — Exécuter le banc P1c deux fois sous WinUAE Runtime dans la même session et sauvegarder les deux journaux. La CI `Artifact integrity` historique comporte encore des échecs sur d’anciennes empreintes.

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
