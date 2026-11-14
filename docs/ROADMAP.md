# Roadmap — AMOSPro AGA Extension

> **État au 14 novembre 2026 — branche `main`.** Cette roadmap présente les priorités, les décisions validées et les travaux restant à faire. Elle n'est **pas** un journal de builds : consulter l'[historique des bibliothèques](LIBRARY_TEST_HISTORY.md), l'[état de reprise](NEXT_SESSION.md) et l'[archive de la roadmap antérieure](history/ROADMAP_ARCHIVE_2026-11-12.md) pour les essais, anciennes Rxx et incidents.
>
> **Statuts :** *terminé* = implémentation qualifiée sur le périmètre indiqué ; *en cours* = travail autorisé ou candidate à tester ; *prévu* = objectif retenu, non développé ; *à étudier* = idée non approuvée. Une entrée ici n'autorise jamais à elle seule une nouvelle API, un build ou une promotion.

## 1. État actuel

| Élément | Situation établie | Référence |
|---|---|---|
| **Dernière version promue : R73 v0.13.18** | **`LAST_GOOD`**, 64 commandes / 71 entrées AP20 ; optimisations 68020 AGAPIC et Fast Icons. Gates **A/B/C PASS** sur les scénarios documentés ; Gate **D Amiga physique non testée**. | [Rapport de promotion](OPT020_R73_LAST_GOOD_PROMOTION_2026-11-14.md) |
| **Candidate de développement : R78 v0.13.23** | **55 772 octets**, SHA256 `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`, **68 commandes / 75 AP20**. **Gate A native PASS (46 cas)** et **Gate B WinUAE fonctionnelle PASS** (cinq profondeurs, cinq copies/clippings, cinq rejets et réouvertures). Journal auteur `RESULT 1`, Chip/Fast delta **0/0**. **Gate C Compiler et Gate D physique non testées.** R73 `LAST_GOOD` inchangée. | [Preuve Gate B R78](C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md) |
| **Chantier actif** | **C2P-5 / R79 — `Aga C2P Zoom` nearest-neighbour AVANT clôture**, sur banques chunky 8 bits. Signature 10 paramètres, clipping quatre bords ; première source native et Gate A en cours. **R78 reste la candidate installable Gates A/B PASS tant que R79 n'est pas qualifiée**. Gate C Compiler uniquement après R79 Gate B, pas maintenant. | [Contrat R79](C2P_R79_ZOOM_CONTRACT_2026-11-14.md) |
| **Suite de l'ordre retenu** | Finir et qualifier C2P, puis **AGAPIC v2**. Les autres études sont un backlog, sans développement implicite. | Sections suivantes |

**Identité des binaires au présent état :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` = **R73**, 51 608 octets, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407` ; `dist/AMOSPro_AGA.Lib` = **candidate R78**, 55 772 octets, SHA256 `9f449581b868e0dd1361ed3aa25e27d3c690967a6236ac55ce60ed06b4067e7c`. Aucune promotion automatique.

**BLOCAGE R74/R75 :** régression confirmée sur les entrées clavier/souris RPG après insertion de 138 octets sans recalage de sept accès LEA. [Correctif natif R76](C2P_R76_RPG_REGRESSION_2026-11-14.md). Les deux programmes M0 RPG fonctionnent desormais sous WinUAE avec R76 (retour auteur). Gate B C2P Convert R76 desormais PASS (5/5 profondeurs et journal RAM). Gates C/D restantes ; aucune promotion automatique.

**Règles permanentes depuis R76 :** controle CI des sept LEA clavier/souris sur le binaire natif final (huit cas negatifs) et journal automatique RAM: pour les tests ASC actifs, avec Prg State, CPU signale par Exec, bilan et retour End sans boucle VBL finale. [Regles](../EXTENSION_SOURCE_RULES.md) · [Protocole RAM](AMOS_RAM_TEST_LOGGING.md). **L'ASC C2P instrumenté a produit un journal RAM complet sous WinUAE : Gate B PASS.**

## 2. Priorité immédiate — C2P

**Objectif :** convertir des pixels *chunky* 8 bits d'une banque AMOS vers les bitplanes de l'écran Intuition AGA privé, sans écritures directes non sûres dans ses `ScreenBuffer`.

Chaîne retenue : **banque DATA/WORK chunky → `c2p.library` → bitmap intermédiaire Chip géré par le contexte → `BltBitMap` vers le back buffer `Safe` → `Aga Swap` explicite**. Le bitmap intermédiaire évite de supposer que les plans du bitmap Intuition sont contigus. `c2p.library` est une dépendance externe à installer dans `LIBS:`, pas du code incorporé dans l'extension.

| Jalon | Contrat et état | Prochaine décision |
|---|---|---|
| **C2P-1 — `Aga C2P Open(Bank)`** | **Implémenté en R74 ; Gate A native PASS.** Banque AMOS DATA/WORK existante n° 5..65535, au moins **81 920 octets** ; CPU **68020+** ; écran AGA privé **320×256, 16/32/64/128/256 couleurs** (4 à 8 plans), double buffering activé. Ouvre un seul contexte et son bitmap Chip, sans conversion ni Swap. Nettoyage automatique au `Screen Close` ou à la sortie AMOS. | **Gate B réelle WinUAE interprétée R74 Open PASS**, cinq profondeurs, refus doublon, mémoire stable ; [rapport](C2P_R74_WINUAE_GATE_B_2026-11-14.md). R75 Convert a sa Gate A native PASS ; B/C/D restantes. |
| **C2P-2 — `Aga C2P Convert`** | **[Contrat approuvé](C2P_R75_CONVERT_CONTRACT_2026-11-14.md), implémentation native R75 intégrée**. Fonction entière sans paramètre : revalide la banque, contrôle le back et Safe, convertit avec `c2p.library` vers son bitmap Chip puis copie par `BltBitMap($C0,$FF)` et `WaitBlit`, sans Swap ni changement de palette. **Gate A native 24 scénarios PASS**. `ScreenBuffer.sb_BitMap` est à **+0**, pas +4. | **Gate B WinUAE R76 PASS** avec l'unique [ASC R76](../tests/current/C2P_R76_CONVERT_01.asc) : cinq profondeurs, mire visible, journal RAM et retour AMOS. [Preuves](C2P_R76_CONVERT_WINUAE_GATE_B_2026-11-14.md). Gate C Compiler réservée à la fin du chantier ; Close reste à décider séparément. |
| **C2P-3 — `Aga C2P Close` (R77)** | **Gates A et B fonctionnelle PASS**, 5/5 fermetures, deuxiemes fermetures, reouvertures/Swap, `RESULT 1`. Correctif `Amos To Back` dans l'ASC pour eviter les faux blocages clavier. Une execution propre supplementaire verifiera le focus et le delta Fast, sans bloquer R78. Gate C reservee a la fin du chantier. | [Preuve WinUAE](C2P_R77_CLOSE_WINUAE_GATE_B_2026-11-14.md) |
| **C2P-4 — `Aga C2P Blit` (R78)** | **Implémenté et Gate A/B PASS** : CPU chunky 8 bits opaque, SrcPitch, clipping quatre bords, validation et refus des banques invalides, double buffer/Convert/Swap explicites. Journal R78 : 5/5 copies, pixels, rejets et Blit après réouverture ; Chip/Fast delta 0. | [Rapport Gate B R78](C2P_R78_BLIT_WINUAE_GATE_B_2026-11-14.md) · [Contrat](C2P_R78_BLIT_CONTRACT_2026-11-14.md) |
| **C2P-5 — `Aga C2P Zoom` (R79)** | **Fonction prévue et acceptée par l'auteur avant la clôture C2P.** Nearest-neighbour agrandissement/réduction, origine source, SrcPitch, rectangle destination et clipping sans rééchantillonnage du rectangle clippé ; index 0 opaque ; pas de Convert/Swap implicite. **Source native en cours, non installable tant que Gate A CPU et intégrité CI ne sont pas PASS ; Gate B WinUAE à venir.** | [Contrat Zoom](C2P_R79_ZOOM_CONTRACT_2026-11-14.md) |
| **C2P-6 — qualification de l'ensemble** | Gates A/B déjà PASS pour R78 ; **une seule Gate C AMOS Compiler après R79 Zoom et sa Gate B**, sur l'ASC C2P final, sans anticiper compilation/promotion. Gate D physique reste distincte ; R73 `LAST_GOOD` protégée. | [Ancien plan R78, à adapter après R79](C2P_R78_COMPILER_GATE_C_PLAN_2026-11-14.md) |

**À ne pas réactiver :** l'ancienne piste de relevé de bitmaps via **GDB/PowerShell (C2P/P2)** a été **abandonnée** au profit du bitmap intermédiaire et de `BltBitMap`. Ses [notes d'étude](C2P_P2_WINUAE_GDB_PROBE_2026-11-14.md) restent historiques, **pas une étape bloquante**. Le seul ASC courant R78 (réutilisable pour Gate C) est `tests/current/C2P_R78_BLIT_01.asc` ; R76 Convert Gate B est documentée dans l'historique et R74 reste historique.

**Limites du premier jalon :** 320×256 uniquement, chunky 8 bits, profondeur indexée de 4 à 8 plans ; pas de HAM8, conversion partielle, changement automatique de palette ou autre résolution annoncé comme implémenté. Toute extension de périmètre doit être décidée séparément.

## 3. Après C2P — AGAPIC v2

**Statut : prévu, non engagé.** Démarrer uniquement après qualification de la chaîne C2P correspondante et accord de l'auteur. [Format AGAPIC v1](M16_AGAPIC_FORMAT_DESIGN.md).

- **Image autonome en banque AMOS DATA/ABK :** conserver la compression planaire RLE, ajouter des métadonnées versionnées (dimensions, profondeur, **mode vidéo AGA**) et une **palette RGB24 facultative** (jusqu'à 256 couleurs).
- **Compatibilité descendante :** les banques AGAPIC **v1 restent lisibles sans conversion** ; préserver les signatures existantes lorsque possible, notamment `Aga Bank Image Draw`.
- **Palette indépendante :** aucune application automatique des couleurs lors du dessin, pour ne pas modifier la palette des autres objets. Prévoir une application explicite si une palette est embarquée.
- **Avant le code :** figer format binaire, longueurs, offsets, indicateurs, limites, transparence, gestion des données corrompues et stratégie de lecture v1/v2. **Réutiliser** les routines de capture, dessin, palette et banques déjà qualifiées.
- **Noms à l'étude, non approuvés :** `Aga Image Capture V2`, `Aga Bank Image Info`, `Aga Bank Palette Apply`. Aucun token AP20 nouveau tant que les signatures ne sont pas décidées.
- **Validation future :** ABK `Save/Load`, modes/profondeurs, palettes, clipping, Fast/Chip, `Safe`, ABI/Compiler et Gates A/B/C ; Gate D physique à documenter séparément.

## 4. Backlog — non engagé, sans priorité supplémentaire décidée

| Sujet | Intention conservée | Condition avant développement |
|---|---|---|
| **M19 — Sprites / objets AGA, AMAL** | Étudier une passerelle AMAL et l'affichage d'objets/sprites sur l'écran privé AGA. **Pas de dessin depuis une interruption.** | Définir les contrats et un prototype indépendant. |
| **M20 — Tilemaps et scrolling** | Tilesets 16×16, cartes à indices, caméra, surfaces plus grandes que l'écran, masques/transparence, dirty rectangles **par back buffer**. Comparer tuiles planaires pré-décodées en Fast RAM et décodage AGAPIC à la demande. | Étude indépendante de [l'audit documentaire AGE](AUDIT_AGE_V1_01_TILEMAP_C2P.md) ; aucune API `Aga Tile/Map` approuvée. |
| **M21 — Dual Playfield AGA** | Support éventuel du double playfield. | Spécification et arbitrage à venir. |
| **M22 — Copper AGA avancé** | Aller au-delà du Copper RGB4 existant. | Définir précisément les usages, registres et limites ; pas d'accès libre arbitraire. |
| **Performance Fast Icons** | Évaluer le coût **total** création/staging Fast→Chip + dessin CPU/Blitter ; ne pas conclure à partir du dessin seul. | Benchmarks comparables, **seulement si demandés** ; aucune optimisation implicite. |
| **Copy aligné / Blitter** | Investiguer l'écart historique `Screen Copy` / `Aga Blit Copy` sur les petits blocs alignés ; éventuelle copie spécialisée 16 pixels. | Gain reproductible requis ; **aucun nom, signature ni nouvelle commande approuvés**. [Diagnostic M17](M17_BLITTER_DIAGNOSTIC.md). |
| **P2C (planar → chunky)** | Piste secondaire à C2P, évoquée par la documentation AGE. | Aucune API ni priorité validée ; **pas de fonctionnalité 3D AGE prévue**. |

**AGE v1.01** est une **référence documentaire**, pas une dépendance ou du code à reprendre : pas de modification, désassemblage ou reverse engineering d'`AGE.lib`. Les éventuelles fonctionnalités doivent être développées indépendamment. [Périmètre et limites de l'audit](AUDIT_AGE_V1_01_TILEMAP_C2P.md).

## 5. Jalons clôturés et décisions à conserver

| Chantier | Résultat durable |
|---|---|
| **AGAPIC v1 / M16** | Banques DATA/ABK, compression RLE, dessin CPU dans le back buffer AGA ; source Fast ou Chip, pas de DMA Blitter depuis la Fast. |
| **M17** | Pont AMOS Compiler V2 et corrections de dessin/Blitter qualifiés. Le diagnostic de `Copy` reste une **étude**, pas un chantier ouvert. |
| **M18 — Fast Icons / CBlock** | Banques `FICON8`, cache `FICHIP8` en Chip, staging explicite, capture/dessin CPU/Blitter et blocs temporaires RAW Chip livrés. **CBlock garde un `Method` explicite : 0=CPU8, 1=CPU16, 2=Blitter ; aucun mode AUTO.** [Contrat CBlock](M18_CBLOCK_DESIGN.md). |
| **OPT020 — R73** | P1e/P2 AGAPIC et P3 Fast Icons 68020 (capture et dessin), **Gates A/B/C PASS**, **R73 promue `LAST_GOOD`**. Aucun gain non mesuré ni validation physique revendiqué. [Rapport de promotion](OPT020_R73_LAST_GOOD_PROMOTION_2026-11-14.md). |
| **Aminet** | Publication initiale indiquée comme déjà réalisée par l'auteur. **Aucune nouvelle publication** déduite d'une future promotion. |

Les validations détaillées, les Rxx intermédiaires, les échecs historiques, les chronos et les anciens ASC se trouvent dans l'[historique de tests](LIBRARY_TEST_HISTORY.md), les [rapports techniques](NEXT_SESSION.md) et la [roadmap archivée](history/ROADMAP_ARCHIVE_2026-11-12.md) ; ils ne doivent plus être copiés comme des tâches actives.

## 6. Règles de réalisation et de livraison

1. **Branche : `main` uniquement.** Ne créer ni branche ni PR sans demande explicite.
2. **Une seule candidate :** `dist/AMOSPro_AGA.Lib`. **Une seule référence promue :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` ; elle n'est remplacée qu'après accord exprès et validation. Ne pas modifier les archives ni les tests figés.
3. **Gates :** A = CPU/CI + ABI/AP20, B = AMOS interprété sur WinUAE, C = nouvel exécutable AMOS Compiler sur WinUAE, D = Amiga AGA physique. Un PASS ne vaut que pour son scénario et **n'autorise pas** à afficher PASS pour les autres.
4. **Contrat avant code :** entrée/sortie, mémoire Fast/Chip, plage des paramètres, `Safe`, écran/buffers, traitement d'erreur, ressources et nettoyage, gestion de la fermeture, scénario de test. Les fonctions C2P futures exigent chacune une validation de contrat.
5. **Affichage :** écran Intuition AGA privé, dessin uniquement sur back buffer autorisé, `Safe` avant écriture/DMA, `WaitBlit` si nécessaire ; **aucun Swap ni changement de palette implicite** sauf contrat explicite.
6. **Traçabilité :** état courant dans [NEXT_SESSION](NEXT_SESSION.md), spécifications dans les rapports dédiés, chronologie dans [LIBRARY_TEST_HISTORY](LIBRARY_TEST_HISTORY.md). Pas de benchmark, nouvelle compilation, tag, release ou publication par simple mise à jour de cette roadmap.


## 7. Dernier jalon potentiel — Chargement / sauvegarde PNG

**Statut : à étudier, en toute fin de roadmap ; aucune priorité ni implémentation approuvée.** Ce chantier ne démarre qu'après les travaux précédents (qualification C2P, puis AGAPIC v2 et priorités intermédiaires décidées), sur demande explicite de l'auteur. Aucun changement aux builds ou APIs actuels.

- **Objectif :** lecture et écriture de PNG **indexés** directement depuis AMOS, sans conversion IFF/ILBM intermédiaire ; conserver exactement les **indices** et la **palette RGB24** (jusqu'à 256 couleurs).
- **Périmètre initial à étudier :** PNG indexé non entrelacé, profondeurs PNG **4 et 8 bits** ; pas de RGB/RGBA, HAM ni quantification automatique dans le premier prototype. Préciser dimensions, palette, transparence et comportement sur écran incompatible.
- **Chargement pressenti :** décodage PNG (PLTE/IDAT, filtres + DEFLATE) → chunky en Fast RAM → C2P → back buffer AGA `Safe`. La chaîne C2P R76 reste actuellement limitée à **320×256 / 4–8 plans** et n'est pas complètement qualifiée ; ne pas supposer d'autres dimensions.
- **Sauvegarde pressentie :** lecture planar→chunky (**P2C à développer ou sélectionner séparément**, non fourni par `c2p.library`) → encodeur PNG indexé, avec palette.
- **Bibliothèques candidates, non sélectionnées :** `z.library` Amiga 68k + codec PNG indexé dédié (z.library ne fournit que la compression), ou **LodePNG** compilé pour 68k (toolchain, ABI, empreinte et licence à vérifier). `c2p.library` convertit les pixels, mais ne lit ni n'écrit de PNG.
- **Commandes possibles, non approuvées :** `Aga Png Load(fichier$)` et `Aga Png Save(fichier$)`. Aucun token AP20 ni dépendance à intégrer sans validation préalable.
- **Tests futurs :** aller-retour PNG avec comparaison bit à bit des indices et palette, cas corrompus, tailles/profondeurs, gestion des erreurs et de la mémoire Fast/Chip, `Safe` et Gates A/B/C/D distinctes.

---
*Document de planification. Les versions, binaires et résultats de test évoluent indépendamment ; les vérifier à la clôture de chaque jalon.*
