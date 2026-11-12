# Roadmap — AMOSPro AGA Extension

> **Feuille de route active, mise à jour le 13 novembre 2026.** Ce fichier suit les **décisions et travaux à venir**, pas les journaux de chaque révision. Les ~90 000 caractères de l'ancienne roadmap ont été conservés dans l'[archive historique intégrale](history/ROADMAP_ARCHIVE_2026-11-12.md), avec les liens relatifs ajustés. Les anciens états de cette archive ne sont pas les états courants.

## 1. Situation vérifiée

| Référence | Statut / preuves | Action |
|---|---|---|
| **R60 v0.13.5 — candidate M18** | `dist/AMOSPro_AGA.Lib`, **35 056 octets**, 54 commandes / 61 AP20, V2 **32 798 octets**. `Aga Image Region` sous-rectangles AGAPIC v1. **Gate A native CPU/CI PASS (86 cas)**, Gates B/C WinUAE/D physique non testées. R59 `LAST_GOOD` inchangée. | [ASC actif unique](../tests/current/M18_R60_IMAGE_REGION_01.asc) ; tester interprété puis nouvel exécutable compilé. [Rapport R60](M18_R60_IMAGE_REGION.md). |
| **R59 v0.13.4** — M17, `LAST_GOOD` PROMUE | `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` (**32 984 octets**, 53 commandes / 60 entrées AP20, bloc V2 30 782 octets, sans remplissage 40 Ko). **Gates A/B/C PASS** interprété/compilé WinUAE ; [régression complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43312486348) sur le HEAD exact `5f29d78`, puis promotion explicitement approuvée le 12/11/2026. D physique non testée. | Pont V2 compact validé et promu ; [test R59 exact archivé](../tests/passed/M17_R59_COMPACT_V2_01.asc). Nouvelles fonctions uniquement sur décision de l'auteur. | |
| **R58 v0.13.3** — témoin V2 historique | 40 000 natifs atteints dans une bibliothèque **42 264 octets**, **Gates A/B/C PASS** sur son scénario ; [ASC archivé](../tests/passed/M17_R58_COMPILER_BRIDGE_01.asc). | Preuve de franchissement 32 Ko conservée ; ne pas publier le padding comme release finale. |
| **R57 v0.13.2** — ancien `LAST_GOOD` | **32 980 octets**, Gates A/B/C PASS historiques, [ancienne référence dans Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/5f29d78e65b666f7260f5a32e28bd4e8bcf59a4a/dist/AMOSPro_AGA_LAST_GOOD.Lib), builder R57 déterministe. | Historique reproductible, sans duplication d'une bibliothèque candidate. |
| **M17 — performances** | R57 : benchmark Fill/Clear compilé PASS et diagnostics Copy sous WinUAE. Petit rectangle aligné : `Screen Copy` 35 ticks contre `Aga Blit Copy` 69 ; cause exacte non identifiée. | Poursuivre le diagnostic / comparer les API AmigaOS avant tout changement ; aucune optimisation nouvelle automatiquement approuvée. |

**Source d'état opérationnel :** [NEXT_SESSION.md](NEXT_SESSION.md). [Rapport compact R59](M17_R59_COMPACT_V2.md) · [Rapport du témoin R58](GATE_C_COMPILER_BRIDGE_V2_PROBE.md) · [Diagnostic Blitter](M17_BLITTER_DIAGNOSTIC.md) · [Historique des validations](LIBRARY_TEST_HISTORY.md). Tout état plus ancien dans les documents conservés est historique, même s'il emploie le mot « courant ».

## 2. Ordre des travaux retenus

| Étape | Périmètre | Situation / condition |
|---|---|---|
| **M17** | Pont Compiler V2 compact R59, résultats Blitter/Copy R57 conservés | **R59 A/B/C + régression PASS, `LAST_GOOD` promue** ; diagnostic Copy différé sans modification du moteur |
| **Publication Aminet** | Publication initiale signalée comme déjà réalisée par l'auteur | **Déjà faite** ; aucune nouvelle publication imposée pour commencer l'étude M18. Toute nouvelle version reste sur décision de l'auteur. |
| **M18** | Atlas/animations AGAPIC, CBlock pixel-exact et `F 16 Icon` | P0 hôte PASS, **R60 `Aga Image Region` Gate A M68000 PASS ; B/C WinUAE à confirmer**. CBlock au pixel près et optimisation 16 pixels à mesurer. `F 16 Icon` et choix AUTO en attente d'audit. |
| **M19** | Objets/sprites AGA, étude de la passerelle AMAL | **Planifié, non engagé** ; prototype AMAL distinct, aucun dessin depuis une interruption |
| **M20** | Scrolling AGA, caméra, surfaces plus grandes que l'écran | **Planifié, non engagé** ; dépendances avec tilemaps à examiner |
| **M21** | Dual Playfield AGA | **Planifié, non engagé** |
| **M22** | Copper AGA avancé | **Planifié, non engagé** |

**Chantier actif unique : M18/R60 `Aga Image Region`.** Le support de `c2p.library` n'est pas engagé. Les numéros et l'ordre M18–M22 ne valent pas autorisation de coder. Ne pas démarrer un nouveau chantier sans demande explicite. **Uniquement la branche `main`** ; pas de création/changement de branche sans instruction.

## 3. Études en attente — aucun développement autorisé

### A. AGE v1.01 — Tilemaps et blocs graphiques

**Statut : AUDIT DOCUMENTAIRE UNIQUEMENT.** [Audit détaillé, sources et limites](AUDIT_AGE_V1_01_TILEMAP_C2P.md).

- AGE documente `_AGE_OPEN_BLKDATA_BANK`, `_AGE_REMOVE_BLKDATA_BANK` et `_AGE_DRAW_BLOCK_ARRAY_CPU`. Son archive fournit des données graphiques 320×256×8 et des exemples de blocs. **Le format exact, la transparence, le scrolling et les performances ne sont pas démontrés.**
- Étudier pour notre extension un **tileset 16×16**, une banque de cartes à indices, le dessin CPU Planar vers le back buffer privé AGA, les masques opaques/transparents, le clipping et le rafraîchissement indépendant des deux buffers.
- Comparer les ressources AGAPIC RLE décompressées à la demande avec un cache de tuiles Planar pré-décodées en Fast RAM ; vérifier résidence Fast/Chip réelle et coûts CPU.
- **Articulation proposée :** les atlas/frames peuvent rejoindre les études M18 ; la caméra et les grandes cartes sont pertinentes pour M20. **Pas de nouveau jalon ni de commande créée** avant arbitrage.

### B. AGE v1.01 — Conversion Chunky-to-Planar / Planar-to-Chunky

**Statut : AUDIT DOCUMENTAIRE UNIQUEMENT.** [Audit détaillé](AUDIT_AGE_V1_01_TILEMAP_C2P.md).

- AGE liste `_AGE_C2P_STRIP_FROM_MEMORY`, `_AGE_P2C_STRIP_TO_MEMORY`, `_AGE_C2P_SCRN`, `_AGE_C2P_SCRN_CLS`. Les fonctions exactes et leurs performances restent à qualifier.
- Étudier **un buffer Chunky 8 bits en Fast RAM → conversion CPU → 8 bitplanes du back buffer AGA en Chip RAM**, d'abord plein écran puis rectangulaire ; P2C en piste secondaire.
- À 320×256×8 : **81 920 octets Chunky et 81 920 octets Planar**, hors métadonnées ; le C2P est une représentation de travail, pas une compression.
- **Moteur indépendant du tileset Planar** : ne pas ajouter de conversion inutile à chaque tuile. Benchmarks, `Safe`, double buffering, Compiler, gestion des banques et fermeture requis avant une API.

**Exclusion explicite :** aucune étude ni fonction 3D AGE dans cette roadmap.

### C. Copie alignée sur 16 pixels — étude différée

**Statut : BACKLOG LONG TERME, NON PRIORITAIRE.** Une commande optionnelle de type `Aga Blit16 Copy` a été évoquée, **sans nom ni signature validés**. Étudier uniquement si la comparaison d'API AmigaOS apporte un bénéfice reproductible pour les copies alignées ; pas d'accès direct aux registres Blitter ni de dégradation de `Aga Blit Copy`. [Résultats Copy/Wait R57](../benchmarks/RESULTATS_COPY_WAIT_R57_2026-11-12.md).

### D. Cible native 68020+ — après le chantier actif M18/R60

**Décision de l'auteur (13/11/2026) : à traiter APRÈS la clôture du chantier actif M18/R60 (`Aga Image Region`), actuellement en attente des Gates B/C WinUAE.** L'intégration de `c2p.library` est une piste distincte et **n'a pas commencé**. Aucun changement de binaire, de test actif ou d'ABI n'est autorisé par cette seule inscription.

- **Processeur minimum visé pour le code natif de l'extension : Motorola 68020 / 68EC020**, puis 68030, 68040 et 68060 ; aucune exigence de compatibilité d'exécution avec un 68000 seul.
- **Compilateur/assembleur et nouveaux générateurs natifs : cible `68020` minimale réelle**, et pas seulement un contrôle de présence du CPU au démarrage. Employer les instructions et modes d'adressage du 68020 lorsqu'ils sont utiles, sans réécrire artificiellement les routines 68000 existantes qui fonctionnent déjà sur 68020.
- **Revoir les contrôles de prérequis CPU**, la documentation, l'installation et les tests Gate A pour inclure une exécution effective des instructions 68020 (68020/68EC020), puis vérifier AMOS interprété (B), **nouvel exécutable AMOS Compiler** (C) et Amiga AGA physique (D). Les tests M68000 historiques restent des preuves de leur code d'origine, pas la cible de qualification des futurs ajouts 020.
- Conserver l'ABI AP20, les règles de relocation/compiler, la gestion du back buffer, `Safe`, les tests de non-régression et **`LAST_GOOD` protégée**. Ne proposer des optimisations spécifiques 030/040/060 qu'après mesures et en maintenant la compatibilité 020.

**Ordre :** terminer et valider R60 en cours, puis étudier séparément la cible native 68020+ ; l'intégration de `c2p.library` reste un chantier futur non engagé, sans priorité décidée vis-à-vis des autres études. **Pas de modification du moteur existant dans ce lot de roadmap.**

## 4. Règles de validation et de livraison

- **Gate A :** CPU/CI, structure HUNK/AP20, ABI et tests statiques ; **Gate B :** AMOS interprété + WinUAE ; **Gate C :** nouvel exécutable compilé + WinUAE ; **Gate D :** Amiga AGA physique. Un PASS sur un scénario ne prouve pas tous les scénarios.
- Toute nouvelle commande doit définir ses paramètres, retours, clipping, mémoire, `Safe/Disp`, nettoyage, comportement en cas d'échec, tests et exemples **avant** développement.
- Respecter l'écran **Intuition AGA privé**, son back buffer, les ressources Fast/Chip, les banques AMOS et la compatibilité Compiler.
- `dist/AMOSPro_AGA.Lib` est la **candidate de travail unique** ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` est le **dernier binaire explicitement promu**. Archives et tests passés ne sont jamais modifiés silencieusement.
- Aucun code, binaire, test actif, tag, publication ou promotion n'est autorisé par une **simple entrée de roadmap**.
- AGE est une **référence de fonctionnalités documentées**, non une dépendance : sa licence interdit notamment la modification et le reverse engineering de `AGE.lib`. Développement indépendant uniquement.

## 5. Références et historique

- [État de reprise actuel](NEXT_SESSION.md) · [Règles sources](../EXTENSION_SOURCE_RULES.md) · [Architecture](ARCHITECTURE.md)
- [Audit AGE — tilemaps et C2P](AUDIT_AGE_V1_01_TILEMAP_C2P.md) · [AGAPIC v1](M16_AGAPIC_FORMAT_DESIGN.md)
- [Archive intégrale de l'ancienne roadmap](history/ROADMAP_ARCHIVE_2026-11-12.md) · [Historique des bibliothèques](LIBRARY_TEST_HISTORY.md)
