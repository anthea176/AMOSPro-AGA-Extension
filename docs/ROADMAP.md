# Roadmap — AMOSPro AGA Extension

> **État au 14 novembre 2026 — branche `main`.** Cette roadmap présente les priorités, les décisions validées et les travaux restant à faire. Elle n'est **pas** un journal de builds : consulter l'[historique des bibliothèques](LIBRARY_TEST_HISTORY.md), l'[état de reprise](NEXT_SESSION.md) et l'[archive de la roadmap antérieure](history/ROADMAP_ARCHIVE_2026-11-12.md) pour les essais, anciennes Rxx et incidents.
>
> **Statuts :** *terminé* = implémentation qualifiée sur le périmètre indiqué ; *en cours* = travail autorisé ou candidate à tester ; *prévu* = objectif retenu, non développé ; *à étudier* = idée non approuvée. Une entrée ici n'autorise jamais à elle seule une nouvelle API, un build ou une promotion.

## 1. État actuel

| Élément | Situation établie | Référence |
|---|---|---|
| **Dernière version promue : R82 v0.13.27** | **`LAST_GOOD`**, 64 112 octets, SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`, 74 commandes / 81 entrées AP20, marge 16 bits **4 562 octets**. Gates **A native, B WinUAE Runtime et C Compiler PASS** sur le banc AGAPIC v1/v2 CPU 68030, delta Chip/Fast 0/0 ; **D physique et PRG_STATE 0 non testés**. R81 devient historique. | [Promotion R82](AGAPIC_R82_LAST_GOOD_PROMOTION_2026-11-14.md) |
| **Bibliothèque active : R82 v0.13.27 promue** | `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` **octet pour octet** ; 64 112 octets, 74 commandes / 81 AP20. Gate A/Runtime B/Compiler C PASS sur le banc documenté. Pas d'essai Amiga physique, pas de publication Aminet. | [Journaux B/C](AGAPIC_R82_WINUAE_RUNTIME_COMPILER_2026-11-14.md) |
| **C2P R81 — jalon historique qualifié** | Gates A/B/C **PASS** (périmètre détaillé dans les rapports), constructeur SHA-pinned, API inchangée ; **R81 promue `LAST_GOOD` sur autorisation explicite**. AGAPIC v2 est maintenant un chantier R82 distinct, Gates A native, B Runtime et C Compiler PASS, R82 promue LAST_GOOD avec accord explicite. | [Rapport Gate C](C2P_R81_COMPILER_GATE_C_2026-11-14.md) |
| **Suite de l'ordre retenu** | Finir et qualifier C2P, puis **AGAPIC v2**. Les autres études sont un backlog, sans développement implicite. | Sections suivantes |

**Identité actuelle :** `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/AMOSPro_AGA.Lib` = **R82 v0.13.27 promue** (64 112 octets, SHA256 `b0a69766e1f07978d69498c0408ff349ad457d9284832f254cabd89c7c2b2a36`). **R81 v0.13.26** (59 972 octets, SHA256 `9992d41d16038663a5f8705d0c2d7e07917d6d27977404c94716c211fa04c8f4`) reste reconstructible et accessible dans l'historique Git. R73 v0.13.18 (51 608 octets, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`) demeure dans [l'historique Git](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/e7a11afc284840e61de52d83c2d0de7b368b696e/dist/AMOSPro_AGA_LAST_GOOD.Lib).

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
| **C2P-5 — `Aga C2P Zoom` (R79)** | **Gates A/B PASS** : 62 scénarios CPU natifs, test synthétique WinUAE 5/5 profondeurs et démo IFF 7 Zoom avec 14/14 indices. Gate C Compiler reste non testée. | [Gate A R79](C2P_R79_ZOOM_NATIVE_GATE_A_2026-11-14.md) · [Preuve IFF](C2P_INTEGRATED_IFF_REFERENCE_2026-11-14.md) |
| **C2P-5b — démonstration IFF historique R79** | **WinUAE interprété et compilé PASS** : original IFF 320×256×256, 3 Blit, 7 Zoom, Close/ReOpen, 14/14 indices, ERR 0 et Chip/Fast delta 0. Utilisait une banque chunky `.chk` préparée sur PC ; l'essai R80 élimine cette dépendance. L'ASC R79 est préservé dans l'historique Git et comme exemple public distinct. | [Exemple R79](../examples/c2p_iff_showcase/README.fr.md) · [Preuves](C2P_INTEGRATED_IFF_REFERENCE_2026-11-14.md) |
| **C2P-5c — IFF direct vers chunky (R80)** | **Gate A CPU native PASS (11 images exactes, aucun write sur refus)**. Réutilise le pipeline C2P R79 sans changement. **Gate B WinUAE Runtime R80 PASS (image de référence 8 plans, 14/14, deltas Chip/Fast 0)**, aucun fichier `.chk` ; Compiler R80 volontairement non testé et Gate D physique non testée. | [Contrat R80](C2P_R80_IFF_CHUNKY_CONTRACT_2026-11-14.md) · [ASC](../tests/current/C2P_R80_IFF_CHUNKY_01.asc) |
| **C2P-6 — qualification de l'ensemble** | **R81 OPT020 Gates A/B Runtime/C Compiler PASS** sur image IFF 320×256×8 indexée, CPU 68030 : 14/14 pixels, refus, Close/ReOpen, deltas Chip/Fast 0. R81 **promue `LAST_GOOD`** après autorisation. Gate D physique non testée ; pas de mesure de vitesse chiffrée. | [Promotion R81](C2P_R81_LAST_GOOD_PROMOTION_2026-11-14.md) · [Gate C](C2P_R81_COMPILER_GATE_C_2026-11-14.md) |

**À ne pas réactiver :** l'ancienne piste de relevé de bitmaps via **GDB/PowerShell (C2P/P2)** a été **abandonnée** au profit du bitmap intermédiaire et de `BltBitMap`. Ses [notes d'étude](C2P_P2_WINUAE_GDB_PROBE_2026-11-14.md) restent historiques, **pas une étape bloquante**. Le seul ASC courant est `tests/current/C2P_R80_IFF_CHUNKY_01.asc` (désormais logs R81 OPT020, Gates B Runtime / C Compiler 8 plans PASS) ; R76 Convert Gate B est documentée dans l'historique et R74 reste historique.

**Limites du premier jalon :** 320×256 uniquement, chunky 8 bits, profondeur indexée de 4 à 8 plans ; pas de HAM8, conversion partielle, changement automatique de palette ou autre résolution annoncé comme implémenté. Toute extension de périmètre doit être décidée séparément.

## 3. Après C2P — AGAPIC v2 et API Bank palettes

**Statut : R82 v0.13.27 PROMUE LAST_GOOD ; Gates A native / B Runtime / C Compiler PASS sur le périmètre documenté ; interprétation pure et matériel non testés.**
R81 0.13.26 reste `LAST_GOOD`. [Contrat détaillé P0](M16_AGAPIC_V2_CONTRACT_2026-11-14.md) et [AGAPIC v1 historique](M16_AGAPIC_FORMAT_DESIGN.md).

- **AGAPIC v2** : même RLE planaire et masque que v1, ModeID U32 **obligatoire, égalité stricte** avec le mode réellement affiché ; palette RGB24 **obligatoire et complète (2^Depth)**. Dessin sans application automatique de palette, sans Swap.
- **AGAPIC v1 inchangé** : dessin et banques v1 toujours utilisables, sans ModeID ni palette. AGAPAL v1 et son format multi-palettes restent inchangés.
- **Quatre nouvelles API par numéro de banque** : `Aga Bank Palette Init(B,N)`, `Aga Bank Palette Capture(B,I)`, `Aga Bank Palette Apply(B,I)`, `Aga Bank Palette Fade(B,I,VBL)`. Init/Capture = AGAPAL seulement ; Apply/Fade = AGAPAL index I ou AGAPIC v2 index 0 avec ModeID strict ; AGAPIC v1 sans palette refusé. Les anciennes API `Start(B)` sont conservées.
- **Limite 16 bits mesurée dans le vrai binaire R81** : monolithe 57 034/65 534 octets, **8 500 octets de marge**. Les appels proches de l'origine peuvent nécessiter un branchement long 68020, mais cela ne résout pas la limite globale du pont Compiler V2. Garde-fou indépendant `tools/aga_compiler_capacity.py` ; n'ajouter aucun code natif non qualifié pour masquer un dépassement.
- **R82/P1 natif complet PASS** : [rapport des Gate A](AGAPIC_V2_R82_P1_GATE_A_2026-11-14.md), 69 Image Draw + 52 Init/Capture + 63 Apply/Fade + 70 Region, plus 19 cas natifs aux offsets AP20 finaux. Candidat structurel **en mémoire** : 64 124 octets, 74 commandes / 81 entrées, monolithe 60 972 octets, **marge 4 562 octets**. ASC et banques de test sous `tests/design`, Gate B WinUAE/C Compiler **non exécutées**, dist R81 et LAST_GOOD protégées.
- **P0 hôte** : `tools/m16_agapic_v2.py` réutilise le parseur et le RLE v1 ; `tools/test_m16_agapic_v2.py` teste 168 couples v1/v2, palette, ABK, ModeID et corruptions ; aucun nouveau token AP20 ni binaire.
- **Prochaine étape P1** : architecture native économe, source vérifiée du ModeID effectif, ABI 68020, dispatch v1/v2, interfaces palettes et liens PC relatifs ; puis Gates A CPU/CI, B WinUAE interprété, C Compiler une fois en fin de chantier, D matériel réel à part. Aucun PASS anticipé.
- **Autres API possibles non approuvées** : capture directe v2, métadonnées d'image, atlas. Ne pas ajouter de cinquième commande presque homonyme pour la palette.

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
7. **Architecture CPU cible : 68020 minimum.** Décision applicable **dès maintenant** à tous les futurs développements (68020/68EC020, 68030, 68040, 68060). **Aucun support 68000/68010 exigé** pour du code nouveau ; conserver les tests et binaires historiques, sans les réécrire. Les contrôles de rejet sur anciens CPU restent pertinents pour éviter un Guru, mais leur prise en charge fonctionnelle est abandonnée. Voir la [règle prioritaire](../EXTENSION_SOURCE_RULES.md). Aucun build modifié par cette décision.


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
