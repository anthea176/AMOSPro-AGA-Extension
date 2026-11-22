# Roadmap — AMOSPro AGA Extension

> **22/11/2026 — S1-P0 AGSP v1 APPROUVÉ : format multi-images + RGB24 local par image, modèle hôte 27 tests PASS.** [Format](M19_S1_AGSP_V1_FORMAT_2026-11-22.md) / [contrat](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md). S1 simple (3 opaques) ; S2 attaché (15 opaques) ; >15 refus. API AMOS/WinUAE et sécurité DMA NON qualifiées. P2d et LAST_GOOD protégées.

> **22/11/2026 — Sprite S0d : Gates B et C PASS sur WinUAE, rendu confirme** ([Runtime](evidence/M19_S0D_ROB_RUNTIME_2026-11-22.TXT), [Compiler](evidence/M19_S0D_ROB_COMPILED_2026-11-22.TXT)). Trois cycles, 108 mouvements, curseur et Copper fonctionnels ; DMA materiel et Gate D non qualifies. [S1 : IFF indexé CMAP RGB24 capturé sur écran, sans ABK ; commandes non implémentées](AGA_HARDWARE_SPRITES_S1_API_CONTRACT_DRAFT_2026-11-22.md). P2d et `LAST_GOOD` proteges.

> Les jalons anciens et les protocoles detailles restent dans [NEXT_SESSION.md](NEXT_SESSION.md) et [ROADMAP_HISTORY_2026-11-17.md](ROADMAP_HISTORY_2026-11-17.md) ; la roadmap conserve seulement l'etat actif.

## 1. Référence de travail

| Élément | État |
| --- | --- |
| **Bibliothèque active** | **[M19 P2d](../dist/AMOSPro_AGA.Lib)**, 136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`, 100 commandes et 203 AP20. **Gate A native PASS**, **scénario intégré P2a–P2e PASS Gate B Runtime et Gate C vrai Compiler** sur WinUAE ; pas de requalification générale des autres API. Lib P2d **promue LAST_GOOD à octets identiques** ; ancienne P1e préservée dans Git. |
| **ASC unique de campagne** | **ASC actif de régression** : [M19_P2_ALL_IN_ONE.asc](../tests/current/M19_P2_ALL_IN_ONE.asc) conservé pour la CI ; P2a–P2e validés et publiés en [exemple ALL IN ONE](../examples/bob_p2_all_in_one/README.fr.md), **source 25 056 octets inchangée**, avec [test figé](../tests/passed/M19_P2_ALL_IN_ONE.asc). **Gates B Runtime et C Compiler PASS** sur les deux journaux WinUAE ([rapport](M19_P2_ALL_IN_ONE_2026-11-21.md)) ; Gate D non testée. Nouvelle campagne non définie ; la source de régression reste en place jusqu'à remplacement autorisé. |
| **Qualification P0** | **Gate A native MC68020 PASS : 104 contrôles préparation Chip + 121 Bank Free** (OS/Blitter simulés, [CI](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/44801203756)). **Gate B WinUAE Runtime P0 : PASS fonctionnel sur les journaux fournis** ([rapport et limites](M19_P0_BANK_FREE_RUNTIME_B_2026-11-20.md)) ; **Gate C Compiler reportée**, Gate D matériel non testée. |
| **LAST_GOOD promue P2d** | [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib) **identique à la Lib active** (136 020 octets, SHA256 `ce5fb614c7acae9b1bb88e1d793d73dbe7ba747edc285acb7d9e72ac3104176f`) ; autorisation auteur du 21/11/2026 après Gates A/B/C et [preuve](M19_P2D_LAST_GOOD_PROMOTION_2026-11-21.md). Ancienne LAST_GOOD P1e (124 444 octets, SHA256 `7922f558af378c07ff0ac339e3baeca11861c3e7feb3114d8f0c6c380158cd42`) préservée dans l'historique Git. |

**Historique distinct :** B8 S1 SHA256 `3d00b745591533a66d76c8c6e28fc8eca86da795e2e5e0cee06a6e22f548292a` a passé deux essais Runtime à 405/405 frames. Ce résultat ne qualifie pas la nouvelle P0. La B7-m2 (102 400 octets ; SHA256 `242e5ed7e8f732bf4e613a462b8dd266269f8d6977911bac867f5db26f8c39c6`) est la référence antérieure ; **ses Gates Runtime et Compiler PASS ne s'appliquent pas à B8**. [Preuves B7-m2](M19_B7M2_GATES_BC_2026-11-19.md).

## 2. M19 — P2d promue ; chantier Bob P0–P2 clos

**P0 fonctionnelle conservée dans la Lib P2d et dans LAST_GOOD P2d (P0 et P1e préservées dans Git) :** `Aga Bob Bank N` prépare en Chip les images AGBO d'une banque peuplée (aucune allocation si vide) ; `Aga Bob Bank Free N` désactive les Bobs dépendants, attend `WaitBlit`, libère le cache privé **sans effacer la banque AMOS**. Opération idempotente, refus pendant `READY`/`DIRTY`, nouvelle sélection pour réactiver. [Rapport et limites](M19_P0_BANK_FREE_GATES_2026-11-20.md).

P1a (getters) et P1b (hotspot) ont passé leur campagne Runtime. P1c expose `Aga Bob Priority(Mode)` et conserve le tri initial par ID au mode 0. [Rapport P1b](M19_P1B_HOTSPOT_CANDIDATE_2026-11-21.md#résultats-runtime-winue).

**P1e** — [Del Bob et Ins Bob](M19_BOBS_MULTI_IMAGE_ABK_API_DESIGN.md#p1e--del-bob-et-ins-bob) sont raccordés à la transaction AMOS et passent le banc natif. La P1e est promue. [Gate B PASS 2/2](M19_P1E_PROMOTION_2026-11-21.md). [Résultats P1d Runtime](M19_P1D_LIMIT_BOB_RUNTIME_2026-11-21.md).

**M20 EN ATTENTE :** prototype Python P0 (13 tests hôtes PASS) conservé ; aucune poursuite avant décision sur M19.

## 3. M19 P2 terminé — prochain chantier : sprites matériels AGA

**Le moteur Bob P0–P2 est clos sur la P2d promue.** Prochain objectif : reprendre l'[audit S0 des Sprites matériels AGA](AGA_HARDWARE_SPRITES_S0_AUDIT_2026-11-21.md), vérifier les contrats NDK/Intuition/Copper puis préparer S1 (un Sprite matériel 16 pixels). **Aucun nouveau code Sprite, token ou binaire n'est inclus dans la release Bob.** [Plan S0–S3](AGA_HARDWARE_SPRITES_S0_S3_ROADMAP.md).

| Sujet | Objectif |
| --- | --- |
| **P2a — collisions Bob–Bob** | `Aga Bob Col(A,B,Mode)` compare les rectangles ou les masques AGBO. Runtime WinUAE PASS 8/8 sur le premier ASC P2a. [Preuves](M19_P2A_PUBLIC_CANDIDATE_2026-11-21.md). |
| **P2b — retournements H/V** | `Aga Bob Flip(N,Mode)` livré. Rendu et collisions utilisent la même variante Chip. Gate A native et banc WinUAE Runtime/Compiler PASS. [Banc WinUAE P2b](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/562f24343a379aa4fd69c28edb63219581f4d7c6/tests/current/M19_P2B_BOB_FLIP.asc). |
| **P2c — Sélection des plans** | `Aga Bob Planes(N,Masque)` livré. [Contrat, Gate A et preuve Runtime](M19_P2C_BOB_PLANES_MODEL.md). |
| **P2d — Update automatique** | `Aga Bob Auto Update(Mode)` livré. Gate A PASS, **Runtime P2d PASS 43/43** ; Compiler regroupé avec le futur exemple complet P2. |
| **P2e.0 — AMAL / Bobs AGA** | Passerelle mémoire 8 octets vers un Bob, **Gate B Runtime PASS** sur 240 cycles et 29 pixels (voir [rapport](M19_P2E0_AMAL_BRIDGE_2026-11-21.md)). Les flags `Deek` restent diagnostics ; aucun nouveau token/Lib. |
| **P2e.1 — Deux canaux AMAL** | [Banc actif corrigé](../tests/current/M19_P2E1_AMAL_TWO_BOBS.asc) : F/L avec transparence et affichage AGA automatique ; **Runtime à tester**, sans nouveau token ni Lib. Démo [Bob Flip F asymétrique](../examples/aga_bob_flip/FLIP_VISUAL.asc) séparée. |
| **Bobs et animations** | Maintenir la régression `Clear → Update → Swap` et optimiser uniquement sur des mesures. |
| **Sprites matériels AGA S0** | **Audit NDK/architecture en cours, modèle HOST 12/12 PASS, [sonde AMOS ViewPort prête](../examples/sprite_s0_viewport/README.md) (WinUAE non testé)** : [document S0 d'intégration](AGA_HARDWARE_SPRITES_S0_INTEGRATION_2026-11-21.md) et [modèle](../tools/aga_sprite_s0_model.py). Méthode S1 retenue sous réserve de preuve : `GetSprite(-1)` / `MoveSprite` / `ChangeSprite` pour un canal 16 pixels non attaché ; vérifier `Screen.ViewPort.Modes`, pointeur Intuition, couleurs Copper, arrêt DMA et fermeture. **Aucun S1 natif, aucune nouvelle Lib/API, Gates B/C/D non testées.** |
| **Tilemaps / scrolling (M20)** | **P0 modèle hôte et 13 tests PASS**, caméra, bandes exposées et deux pages indépendantes ; [spécification et limites](M20_TILEMAP_P0_HOST_MODEL.md). Implémentation native à concevoir, pas de nouveau token. |
| **Dual playfield (M21)** | Plans indépendants, palettes et scrolling. |
| **Entrées (M22)** | Vérifier d'abord les commandes joysticks natives, sans inventer une API AGA. |
| **C2P / Copper (M23/M24)** | Évaluer accélérations et API avec preuve CPU, WinUAE et Compiler. |

Historique non normatif : [Roadmap archivée](ROADMAP_HISTORY_2026-11-17.md) · [reprise technique](NEXT_SESSION.md).
