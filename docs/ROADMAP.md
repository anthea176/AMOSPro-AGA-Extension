# Roadmap — AMOSPro AGA Extension

> **Pilotage actif — 17 novembre 2026.** Cette page recense la référence installable, la priorité technique et les travaux suivants. **Ce n'est pas un journal de commits.** L'[ancien contenu intégral](ROADMAP_HISTORY_2026-11-17.md), les [preuves](NEXT_SESSION.md) et les [règles du projet](../EXTENSION_SOURCE_RULES.md) sont consultables séparément.

## 1. Référence actuelle

| Élément | État vérifié |
| --- | --- |
| **Bibliothèque de travail** | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) : **M19 AP20 V2 ISLANDS**, **96 908 octets**, SHA256 `34f4e3c13f9a079e3e586e50b054b83459bb32bd7c5d15211b55437275e6bf56`, **85 commandes / 178 entrées AP20**, quatre unités natives. |
| **Test AMOS actif unique** | [`M19_AP20_ISLANDS_01.asc`](../tests/current/M19_AP20_ISLANDS_01.asc) et [notice WinUAE](../tests/current/README.md). |
| **Validation de cette bibliothèque** | **Gate A MC68020 PASS ; Gate B Runtime WinUAE PASS ; Gate C véritable AMOS Compiler PASS** sur le scénario **Bob Blit / dispatch AP20 V2**, et uniquement ce scénario. Capture visuelle issue de l'exécutable compilé ; Runtime attesté par journal. [Preuves et limites](M19_AP20_V2_GATES_BC_2026-11-17.md). **Gate D physique non testée.** |
| **Référence protégée** | [R84 `LAST_GOOD`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), **67 904 octets**, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`, sans nouvelle promotion. |

**API Bob :** `Aga Bob Blit` dessine immédiatement. `Aga Bob` et `Aga Bob Off` sont exposées, mais **leur cycle de vie persistant et leur utilisation complète ne sont pas qualifiés en Runtime/Compiler**. `Aga Bob Draw` **n'est pas encore intégré** dans la bibliothèque installable.

La **cinquième unité native** a été validée en Gates A/B/C pour son banc de sondes, puis ces sondes ont été retirées : la version installable reste à **quatre unités**. [Rapport de l'expérience](M19_AP20_V2_UNIT5_GATES_BC_2026-11-17.md).

## 2. Priorité — M19 : afficher les Bobs persistants

**Objectif :** un rendu Blitter de **1 à 64 Bobs multi-banques**, dans le back buffer `Safe`, **sans projection temporaire de `bank_active_state`**, sans Swap implicite, sans mémoire Chip périmée et avec refus sûr d'une frame invalide.

**Dernier jalon Gate A validé : M19 P0j-b2.** Préparation Chip explicitement indexée par banque et cache réutilisé sans allocation supplémentaire : **46 vérifications MC68020 PASS** ([preuve](M19_P0J_EXPLICIT_BANK_STAGE_GATE_A_2026-11-17.md)). **Dernier jalon Gate A validé : P0j-b3**, résolution des images/masques Chip par banque source **52 contrôles PASS** ([preuve](M19_P0J_EXPLICIT_IMAGE_RESOLVE_GATE_A_2026-11-17.md)). **Étape en cours : P0j-b4**, implémentation source-only du peintre Safe/Blitter et parcours 64 Bobs **sans projection temporaire**, Gate A à confirmer ; puis stratégie d'atomicité et unique banc AMOS ; source-only, **Gates B/C/D non réalisées**. Le lookup indépendant P0j-b1 reste validé (68 vérifications).

| Ordre | Travail à faire | Critère de réussite |
| --- | --- | --- |
| **1** | **P0j-b2 : préparation Chip explicite — PASS source-only**. | **46 contrôles MC68020 PASS** ; deux banques distinctes, copie Chip contrôlée, cache sans recopie et zéro écriture du shadow. [Preuve](M19_P0J_EXPLICIT_BANK_STAGE_GATE_A_2026-11-17.md). |
| **2** | Adapter la **résolution d'image P0d** et la route Blitter pour chaque banque ; éliminer le shadow temporaire du prototype P0i. | Dessin pixel-exact de 64 Bobs issus au minimum des banques 10/11, sans mutation de `bank_active_state` ni risque de réentrance dû à sa projection. |
| **3** | Achever le **préflight intégral de frame avant DMA** et fixer la stratégie d'échec. | Dimensions, profondeur, répertoire, masques, sources, contexte Chip et port `Safe` validés avant peinture ; pas de Swap implicite ni de frame partielle présentée. |
| **4** | Intégrer le rendu au registre des objets et **sécuriser Close/End**. | Identité de banque conservée après `Aga Bob Off`, allocations libérées une seule fois, pointeurs DMA invalidés, fermeture et réouverture sûres. |
| **5** | Préparer l'**API publique Draw** et son unique banc AMOS, **uniquement après autorisation de bascule**. | Gate A CPU020/ABI/AP20/relocations, puis B Runtime et C Compiler sur la **même candidate canonique** ; Gate D séparée. |

**Acquis sans installation :** [P0i, dessin privé de 64 Bobs](M19_P0I_MULTIBANK_DRAW_GATE_A_2026-11-17.md), Gate A 76 vérifications PASS mais shadow non réentrant ; [P0j-a, prévalidation des 64 images](M19_P0J_IMAGE_PREFLIGHT_GATE_A_2026-11-17.md), Gate A 68 vérifications PASS, sans atomicité complète. **Ces résultats source-only ne prouvent pas les Gates B/C/D et ne changent pas la bibliothèque installée.**

## 3. Après M19 — pistes non engagées

| Sujet | Objectif |
| --- | --- |
| **M19 : animation et Bobs** | Décor reconstruit, ordre des objets, éventuelles API `Clear` / `Update`, double buffering, benchmarks de frames complètes 4/8/16 Bobs. |
| **M19 : sprites matériels AGA / AMAL** | Chantier distinct : slots, DMA, priorités, palettes et intégration éventuelle à AMAL. |
| **M20 : tilemaps / scrolling** | Tilesets, caméra, dirty rectangles et gestion Fast/Chip. |
| **M21 : dual playfield** | Deux plans de jeu, palettes et défilements indépendants. |
| **M22 : joystick** | Tester d'abord `Joy(0)` / `Joy(1)` natifs en Runtime, Compiler et physique ; pas d'API AGA décidée. |
| **M23 : C2P direct** | Étudier la conversion chunky→planar dans le back buffer AGA, sans présumer des gains. |
| **M24 : Copper avancé** | Étudier les commandes au-delà des usages actuels. |
| **Autres études** | P2C, PNG indexé natif et optimisations justifiées par mesures reproductibles. |

**Backlog ≠ engagement.** Aucune signature nouvelle, échéance ni publication n'est approuvée par la seule présence d'une ligne.

## 4. Méthode de suivi et historique

- **`main` uniquement** ; pas de branche, release ou promotion sans demande explicite. Une seule Lib dans `dist/AMOSPro_AGA.Lib` et un seul ASC actif sous `tests/current/` ; préserver `LAST_GOOD`, `tests/passed/` et les archives.
- CPU natif **MC68020/68EC020 minimum**. Gates **A** (CPU/ABI), **B** (WinUAE Runtime), **C** (vrai Compiler) et **D** (matériel) distinctes ; le résultat ne vaut que pour sa version et son scénario. WinUAE fonctionnel : 68030/JIT ON ; benchmarks : 68020/JIT OFF.
- **Ne plus empiler les comptes rendus dans cette page.** Les détails datés, échecs, SHA des candidats privés et anciennes Gates appartiennent aux [rapports techniques](NEXT_SESSION.md), à l'[historique des versions](LIBRARY_TEST_HISTORY.md) ou à l'[archive intégrale de l'ancienne roadmap](ROADMAP_HISTORY_2026-11-17.md).
- Mettre à jour cette roadmap **par remplacement ciblé** lors d'un changement de bibliothèque, de blocage, de décision ou de prochaine étape — **jamais** en ajoutant un nouveau chapitre de checkpoint en tête.
