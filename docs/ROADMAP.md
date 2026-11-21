# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 21 novembre 2026.** Ce document décrit l'état actuel et les priorités. Les preuves et jalons historiques sont dans [NEXT_SESSION.md](NEXT_SESSION.md) et [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md).

## 1. Référence de travail

| Élément | État |
| --- | --- |
| **Bibliothèque active** | [M19 P1e](../dist/AMOSPro_AGA.Lib), promue en LAST_GOOD après 2 Runtime PASS, 124 444 octets, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, 96 commandes, 196 entrées AP20, PC16 maximal 14 130. Gate A native PASS ; Gate B Runtime PASS 2/2 ; Gate C Compiler et D physique NON TESTÉES. |
| **ASC unique de campagne** | [M19_B8_BOB_CLEAR_UPDATE_BC_01.asc](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), 405 frames, quatre phases hotspot, huit sondes de priorité, 24 lectures de clipping trois frames d’édition AGBO et banque 26. Journal `RAM:M19_P1E_BANK_EDIT.TXT`. |
| **Qualification P0** | **Gate A native MC68020 PASS : 104 contrôles préparation Chip + 121 Bank Free** (OS/Blitter simulés, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756)). **Gate B WinUAE Runtime P0 : PASS fonctionnel sur les journaux fournis** ([rapport et limites](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md)) ; **Gate C Compiler reportée**, Gate D matériel non testée. |
| **LAST_GOOD promue P1e** | [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **124 444 octets**, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`, exactement la Lib active. Promotion autorisée après Gate A native et deux Runtime PASS. Gates C/D NON TESTÉES. Ancienne LAST_GOOD P0 SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d` conservée dans Git. [Rapport](M19_P1E_PROMOTION_2026-11-21.md). |

**Historique distinct :** B8 S1 SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a` a passé deux essais Runtime à 405/405 frames. Ce résultat ne qualifie pas la nouvelle P0. La B7-m2 (102 400 octets ; SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`) est la référence antérieure ; **ses Gates Runtime et Compiler PASS ne s'appliquent pas à B8**. [Preuves B7-m2](M19_B7M2_GATES_BC_2026-11-19.md).

## 2. M19 — P1e promue, Gate B Runtime PASS

**P0 fonctionnelle conservée dans la Lib active P1e et dans LAST_GOOD P1e (P0 préservée dans Git) :** `Aga Bob Bank N` prépare en Chip les images AGBO d'une banque peuplée (aucune allocation si vide) ; `Aga Bob Bank Free N` désactive les Bobs dépendants, attend `WaitBlit`, libère le cache privé **sans effacer la banque AMOS**. Opération idempotente, refus pendant `READY`/`DIRTY`, nouvelle sélection pour réactiver. [Rapport et limites](M19_P0_BANK_FREE_GATES_2026-11-20.md).

P1a (getters) et P1b (hotspot) ont passé leur campagne Runtime. P1c expose `Aga Bob Priority(Mode)` et conserve le tri initial par ID au mode 0. [Rapport P1b](M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md#résultats-runtime-winue).

**P1e** — [Del Bob et Ins Bob](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p1e--del-bob-et-ins-bob) sont raccordés à la transaction AMOS et passent le banc natif. La P1e est promue. [Gate B PASS 2/2](M19_P1E_PROMOTION_2026-11-21.md). [Résultats P1d Runtime](M19_P1D_LIMIT_BOB_RUNTIME_2026-11-21.md).

**M20 EN ATTENTE :** prototype Python P0 (13 tests hôtes PASS) conservé ; aucune poursuite avant décision sur M19.

## 3. M19 P2 — chantier engagé ; suites ultérieures

| Sujet | Objectif |
| --- | --- |
| **P2a — collisions Bob–Bob** | **Raccord P1e/AGBO livré : 17 + 23 tests hôtes PASS**, 64 objets, stamps, masques et limites P1d ; signature API seulement proposée, aucun token ni nouvelle Lib. [Modèle hôte P2a](M19_P2A_COLLISIONS_HOST_2026-11-21.md) · [contrat P2](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p2--fonctions-avancées--compatibilité-progressive). |
| **P2b — retournements H/V** | Transformations non destructives par objet, image et hotspot partagés préservés. |
| **P2c — SET BOB / AMAL** | Étudier les modes de rendu avancés, les updates automatiques, puis l’intégration éventuelle à AMAL. |
| **Bobs et animations** | Maintenir la régression `Clear → Update → Swap` et optimiser uniquement sur des mesures. |
| **Sprites AGA / AMAL** | Évaluer slots matériels, DMA, collisions et intégration éventuelle avec AMAL. |
| **Tilemaps / scrolling (M20)** | **P0 modèle hôte et 13 tests PASS**, caméra, bandes exposées et deux pages indépendantes ; [spécification et limites](M20_TILEMAP_P0_HOST_MODEL.md). Implémentation native à concevoir, pas de nouveau token. |
| **Dual playfield (M21)** | Plans indépendants, palettes et scrolling. |
| **Entrées (M22)** | Vérifier d'abord les commandes joysticks natives, sans inventer une API AGA. |
| **C2P / Copper (M23/M24)** | Évaluer accélérations et API avec preuve CPU, WinUAE et Compiler. |

Historique non normatif : [Roadmap archivée](ROADMAP_HISTORY_2026-11-17.md) · [reprise technique](NEXT_SESSION.md).
