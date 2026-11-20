# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 20 novembre 2026.** Ce document décrit l'état actuel et les priorités. Les preuves et jalons historiques sont dans [NEXT_SESSION.md](NEXT_SESSION.md) et [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md).

## 1. Référence de travail

| Élément | État |
| --- | --- |
| **Bibliothèque active** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) — **M19 P0 Bank Select/Free**, **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, **89 commandes / 185 entrées AP20**, cinq groupes MC68020 `[142,153,156,177,181]`, PC16 max **31 092**. [Builder source exact](../tools/build_m19_b8_s1_bank_free_in_memory.py). |
| **ASC unique de campagne** | [`M19_B8_BOB_CLEAR_UPDATE_BC_01.asc`](../tests/current/M19_B8_BOB_CLEAR_UPDATE_BC_01.asc), **12 837 octets**, reprend 405 frames B8 + trois phases P0 Free/réactivation ; journal `RAM:M19_P0_BANK_FREE.TXT`, **sans VBL artificiel dans la boucle**. [Protocole](../tests/current/README.md). |
| **Qualification P0** | **Gate A native MC68020 PASS : 104 contrôles préparation Chip + 121 Bank Free** (OS/Blitter simulés, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756)). **Gate B WinUAE Runtime P0 : PASS fonctionnel sur les journaux fournis** ([rapport et limites](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md)) ; **Gate C Compiler reportée**, Gate D matériel non testée. |
| **LAST_GOOD promue P0** | [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **117 896 octets**, SHA256 `f4db949114517f8d3b4d39b70c60b4f63d8d51a6433fecdadbbbfce96bf6689d`, identique à la Lib active ; [promotion](https://github.com/anthea176/AMOSPro-AGA-Extension/commit/71ff3862929b729bb44db20294aec9b048775cbf). Ancienne R84, **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, récupérable dans Git et par builder. Gate C P0 non testée. |

**Historique distinct :** B8 S1 SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a` a passé deux essais Runtime à 405/405 frames. Ce résultat ne qualifie pas la nouvelle P0. La B7-m2 (102 400 octets ; SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`) est la référence antérieure ; **ses Gates Runtime et Compiler PASS ne s'appliquent pas à B8**. [Preuves B7-m2](M19_B7M2_GATES_BC_2026-11-19.md).

## 2. M19 — P0 promue ; P1 source-only engagée

**P0 livrée dans la Lib active :** `Aga Bob Bank N` prépare en Chip les images AGBO d'une banque peuplée (aucune allocation si vide) ; `Aga Bob Bank Free N` désactive les Bobs dépendants, attend `WaitBlit`, libère le cache privé **sans effacer la banque AMOS**. Opération idempotente, refus pendant `READY`/`DIRTY`, nouvelle sélection pour réactiver. [Rapport et limites](M19_P0_BANK_FREE_GATES_2026-11-20.md).

**État :** **P0 terminée et promue LAST_GOOD sur décision explicite**, **Gate A 225 contrôles PASS**, **Gate B Runtime PASS fonctionnel sur journaux** (deux fichiers identiques ; visuel non contrôlé), Gates C/D P0 non testées. **M19 global reste ouvert** : P1 lectures X/Y/Image, hotspots, priorités et clipping ; puis édition des banques, collisions, transformations et Sprites selon décisions. **Premier jalon P1 source-only livré :** tests de `object_read` natif MC68020 (propriétaire/validité/X/Y/image) et `set_hotspot` AGBO avec génération, masque et sauvegarde. [Rapport P1](M19_P1_BOB_READ_HOTSPOT_SOURCE_2026-11-20.md) · [CI P1 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44827972362). **Aucun nouveau token, binaire ou ASC**.

**Régressions CI avant promotion P0 : PASS** ([Artifact integrity](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44823490337) et [politique CPU/chemins](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44823490306), code au commit `05c283a6`). **Action suivante :** valider le nom et la sémantique d'erreur des **trois getters P1a X/Y/I**, puis écrire le shim natif + le builder AP20 **en mémoire**, avec Gate A dédiée ; pas d'installation avant validation/autorisation. Ensuite appliquer le hotspot P1b au rendu, avant priorités/clipping. Gate C Compiler P0 toujours reportée ; M20 reste en attente.

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
