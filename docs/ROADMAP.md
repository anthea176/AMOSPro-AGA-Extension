# Roadmap — AMOSPro AGA Extension

**M19 P2.3 (15/11/2026) — R86 v0.13.31 :** développement natif `Aga Bob Batch(DescriptorBank,Count)` dans le quatrième AP20 BOBS. Descripteurs `BOB1` (16 + 20×Count), AGAPIC v1/v2 et FICON8, ordre Z déjà trié par BASIC, back buffer Safe, clipping, opaque/masqué. Ce jalon est une **candidate de travail non promue** ; **Gates B/C du Batch NON TESTÉES**, ne pas confondre avec celles du témoin R85. R84 LAST_GOOD ne doit pas changer. [Contrat](M19_P23_BOBS_BATCH_CONTRACT.md) · [Test actif](../tests/current/M19_P23_BOBS_BATCH_01.asc).


**M19 P2.2 (15/11/2026) : candidat actif R85 v0.13.30 dans [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), Gate A native MC68020 PASS.** Quatrième unité BOBS 40 octets (témoin `Aga Bob Probe`, **pas encore de dessin Batch**). Binaire actif 67 988 octets SHA256 `4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f`. **LAST_GOOD R84** 67 904 octets SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d` préservée. WinUAE **Gate B Runtime et Gate C Compiled du témoin PASS**, [rapport des deux journaux](M19_P22_4UNIT_WINUAE_RUNTIME_COMPILED_2026-11-15.md). **Aga Bob Batch toujours à développer**. [Rapport](M19_P22_FOURTH_BOBS_UNIT_2026-11-15.md).

**M19 P2.2 — développement du quatrième groupe natif BOBS engagé** (accord de l'auteur le 15/11/2026), **d'abord comme témoin AP20 isolé** `Aga Bob Probe` et non encore `Aga Bob Batch`. [Architecture et test Gate A](M19_P22_FOURTH_BOBS_UNIT_2026-11-15.md) ; R84 `LAST_GOOD` inchangée, aucune API native de production publiée. **Gates A native, B Runtime et C Compiled du témoin désormais PASS**. Le candidat R85 est dans `dist/AMOSPro_AGA.Lib`, la R84 `LAST_GOOD` est protégée.


> **État au 14 novembre 2026 — branche `main`.** Ce document indique ce qui est livré et les pistes futures. **Les chantiers R83 (modularisation) et R84 (AGAPIC v1/v2) sont clôturés** ; ils ne constituent plus des tâches à réaliser. Pour la chronologie, les incidents et les preuves détaillées, voir l'[historique](LIBRARY_TEST_HISTORY.md) et le [suivi technique](NEXT_SESSION.md).
>
> **Statuts :** **livré** = intégré dans une version promue ; **à étudier** = piste non engagée. Une entrée au backlog n'approuve ni API, ni implémentation, ni calendrier.

## 1. Version de référence

| Point | État vérifié |
|---|---|
| **Version active** | **Candidat R85 v0.13.30** en développement dans `dist/AMOSPro_AGA.Lib` (67 988 octets, SHA256 `4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f`). **R84 v0.13.29 `LAST_GOOD`** reste la dernière version promue, figée à 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`. Gates B/C du témoin R85 PASS ; rendu groupé non implémenté. |
| **API** | **76 commandes / 85 entrées AP20**, CPU **MC68020 minimum**, chipset AGA. |
| **Architecture native** | **Trois unités** : C2P 5 558 octets, IFF 2 508 octets, AGA/AGAPIC 56 580 octets. Budget Compiler V2 et portée des branchements vérifiés ; **8 954 octets de marge** sur l'unité AGA/AGAPIC. |
| **Qualification R84** | **Gate A native/CI PASS**, **Gate C AMOS Compiler PASS** sur le scénario documenté (68030 WinUAE, programme compilé avec banque incluse, 4 et 8 plans). **Gate B Runtime corrigée non attestée séparément**, mode strictement interprété `PRG_STATE 0` et Gate D Amiga physique non testés. Promotion autorisée avec ces limites. |
| **Test de référence** | `tests/current/AGAPIC_R84_V1_V2_01.asc`, avec copie dans `tests/passed/`. |

[README et API actuels](../README.fr.md) · [Promotion R84](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) · [Preuve Compiler](AGAPIC_R84_COMPILER_GATE_C_2026-11-14.md)

## 2. Chantiers clôturés

| Jalon | Livrable terminé | Référence |
|---|---|---|
| **C2P — R81** | Chaîne complète **IFF indexé → banque chunky → Blit/Zoom → conversion planaire → back buffer AGA**, fermeture du contexte et optimisations MC68020. `c2p.library` dans `LIBS:` reste nécessaire aux commandes `Aga C2P`, pas au décodeur `Aga Iff To Chunky` utilisé seul. **R81 promue ; Gates A/B/C PASS** sur ses scénarios documentés. | [Promotion R81](C2P_R81_LAST_GOOD_PROMOTION_2026-11-14.md) |
| **Chantier 1 — R83, modularisation** | **Terminé et promu.** Passage d'un monolithe à **trois unités natives AP20** (C2P, IFF, AGA/AGAPIC), en préservant les 74 signatures existantes. Constructeur déterministe et contrôles des liens. **R83 Gates A/B/C PASS** sur son banc. | [Promotion R83](R83_LAST_GOOD_PROMOTION_2026-11-14.md) · [Builder figé](../tools/build_aga_r83_modular.py) |
| **Chantier 2 — R84, AGAPIC v1/v2** | **Terminé et promu `LAST_GOOD`.** Lecture et dessin v1/v2 ; capture explicite **v1 ou v2** par `Aga Bank Image Capture(Bank,X,Y,Width,Height,TransparentIndex,Version)` ; métadonnées par `Aga Bank Image Info(Bank,Champ)`. La commande historique `Aga Image Capture` continue de produire du **v1**. Compatibilité v1 et API de palettes conservées. | [Contrat R84](AGAPIC_R84_V1_V2_CONTRACT_2026-11-14.md) · [Promotion R84](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) |

**Capacités maintenant disponibles :** écran Intuition AGA privé et double buffering, Swap, opérations Blitter/Copper, dessin et captures AGAPIC RLE (masque facultatif), régions, palettes AGAPAL et RGB24/ModeID AGAPIC v2 appliquées **uniquement sur appel explicite**, Fast Icons et CBlock, texte, clavier et souris. Les banques AGAPIC v1/v2 se sauvegardent et se rechargent avec les mécanismes AMOS. [Format AGAPIC v2](M16_AGAPIC_V2_CONTRACT_2026-11-14.md).

**« Livré » ne signifie pas « testé dans toutes les configurations ».** Les résultats R84 sont limités aux Gates et scénarios explicitement indiqués ci-dessus ; la Gate D et l'interprétation pure ne sont pas validées par déduction. Les constructeurs et rapports historiques R81/R82/R83 restent accessibles dans Git, mais `LAST_GOOD` désigne désormais **R84**.

## 3. Backlog — pistes non engagées

Les chantiers R83 et R84 sont clos. **M19 : P0, P1 et P2.0 sont PASS sous AMOS Runtime/WinUAE dans leurs scénarios**, dont P2.0 en 68030 et 8 plans (240 frames). **Aucune API native M19 n'est approuvée** ; la R84 LAST_GOOD reste inchangée. [Rapport P2.0](M19_P2_WINUAE_RUNTIME_2026-11-15.md). **Benchmark 4/8/16 Bobs : 68030/JIT et 68020/14 MHz/JIT OFF tous deux PASS (240 frames, 9 088 dessins chacun). Sur 68020/JIT OFF : composition ~60/96/190 ms/frame et tri Z ~4/15/59 ms/appel ; cache Z **P2.1 Gate B Runtime/68020 PASS** (A/B 4/8/16, gains de composition **5,8/15,6/30,4 %**) ; coût de chaque format à évaluer avant API native**, sans changement R84. [Protocole](../benchmarks/README_M19_P2_BOBS_4_8_16.md) · [Plan M19](M19_SPRITES_BOBS_AMAL_PLAN.md).

| Sujet | Objectif à étudier |
|---|---|
| **M19 — Sprites AGA, Bobs et AMAL** | **P0 Runtime/WinUAE PASS** (211 frames, 2 Bobs, zéro erreur de dessin/Swap) ; clignotement d'alternance d'image corrigé visuellement. **P1 Gate B WinUAE Runtime PASS** : 240 frames, six images AGAPIC v1/v2, 46 frames avec chevauchement, trois inversions d'ordre, pixel témoin validé, clipping 240/240, zéro échec dessin/Swap, delta mémoire Chip/Fast nul. [Rapport P1](M19_P1_WINUAE_RUNTIME_2026-11-15.md). **P2.0 Gate B Runtime/WinUAE PASS** : [gestionnaire BASIC archivé](../tests/passed/M19_P2_OBJECTS_01.asc), 240 frames, cinq objets créés au total, suppression d'un objet, refus de l'ancien ID et des sources invalides, visibilité, ordre Z stable, 4 clips, 2 cullings, zéro échec de dessin/Swap et deltas Chip/Fast nuls. [Rapport](M19_P2_WINUAE_RUNTIME_2026-11-15.md). [Contrat P2](M19_P2_OBJECT_MANAGER_CONTRACT.md). **Benchmark P2 : [4/8/16 Bobs, ASC archivé](../tests/passed/M19_P2_BENCH_BOBS_01.asc), [PASS 68030/JIT complet](../benchmarks/RESULTATS_M19_P2_BOBS_68030_JIT_2026-11-15.md) (240 frames, 9 088 dessins), après [un premier essai interrompu](../benchmarks/RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md). **Comparatif MC68020/14 MHz/JIT OFF PASS** : [résultats et analyse](../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md). **P2.1 : [dernier benchmark cache Z PASS](../benchmarks/RESULTATS_M19_P21_ZCACHE_68020_NOJIT_2026-11-15.md)**, 240 frames, 9 088 dessins, cache valide, aucun retry/échec graphique, gain jusqu'à **30,4 %** à 16 Bobs ; cache BASIC recommandé, **aucun autre benchmark ni API native décidés**. Aucune API native validée. [Plan M19](M19_SPRITES_BOBS_AMAL_PLAN.md). |
| **M20 — Tilemaps et scrolling** | Tilesets, cartes, caméra, transparence, gestion des ressources Fast/Chip et dirty rectangles adaptés au double buffering. |
| **M21 — Dual Playfield AGA** | Étudier les deux playfields, leurs palettes, priorités et défilements indépendants, en cohérence avec l'écran privé et les buffers. |
| **M22 — Joysticks sur écran AGA** | Vérifier que les lectures natives AMOS `Joy(0)` / `Joy(1)` fonctionnent sur l'écran Intuition AGA privé, avec double buffering et animation. Essais des directions/boutons et des deux ports en Runtime WinUAE, Compiler puis Amiga physique ; contrôler la coexistence avec clavier/souris et les changements de premier plan. **Réutiliser l'API AMOS existante si elle fonctionne** : aucune commande AGA joystick décidée. |
| **M23 — Écran C2P direct** | Étudier un mode d'écran AGA dédié à la conversion chunky → planar **directement dans le back buffer d'affichage**, pour supprimer le bitmap Chip intermédiaire et la copie complète `BltBitMap` de l'architecture C2P R81/R84. Vérifier la compatibilité réelle du `CUSTOM_BITMAP` de `c2p.library` v1.9 avec la disposition des bitplanes Intuition, la gestion de deux buffers/contextes, les notifications `Safe/Disp`, les ressources Chip/Fast, les primitives existantes et le retour propre à AMOS. Prototype isolé, comparatif mesuré contre R84 en 16/256 couleurs et validation Runtime/Compiler/Amiga physique **avant toute API ou remplacement du chemin C2P actuel** ; gain non présumé. |
| **M24 — Copper avancé** | Définir les usages et limites d'accès aux registres au-delà des commandes RGB4 existantes (ancien M22, décalé après les études joystick et C2P direct). |
| **P2C et PNG natif AMOS** | Études distinctes de planar → chunky et de chargement/sauvegarde PNG indexé ; aucune API décidée. |
| **Optimisations graphiques** | Mesurer des cas reproductibles avant toute nouvelle optimisation ou commande. |

**Aucune de ces pistes n'est une fonctionnalité promise pour une version donnée.** L'auteur décidera de l'ordre, du périmètre et des signatures éventuelles.

## 4. Règles de développement et de validation

1. **Dépôt : `main` uniquement.** Pas de nouvelle branche, PR, tag, release ou publication Aminet sans demande explicite.
2. **Une seule référence promue : `dist/AMOSPro_AGA_LAST_GOOD.Lib`.** Toute évolution part d'une candidate distincte et ne remplace `LAST_GOOD` qu'après décision expresse, validation et contrôle des octets/SHA.
3. **Un seul test AMOS actif** sous `tests/current/` ; les anciens bancs sont archivés dans `tests/passed/` et les rapports dédiés.
4. **Gates séparées :** A = CPU natif/CI et ABI/AP20 ; B = AMOS Runtime WinUAE ; C = AMOS Compiler ; D = Amiga AGA physique. **Un PASS ne vaut que pour son scénario et ne couvre pas automatiquement les autres.**
5. **Avant toute nouvelle API :** spécifier paramètres, retours, mémoire Fast/Chip, géométrie, erreurs, fermeture, `Safe`/Swap, compatibilité des banques et budget du Compiler V2. Aucun changement de palette ou Swap implicite sans contrat.
6. **Historique dans les rapports, pas dans la roadmap.** Conserver les constats techniques et résultats datés dans [NEXT_SESSION](NEXT_SESSION.md), les [promotions](AGAPIC_R84_LAST_GOOD_PROMOTION_2026-11-14.md) et [LIBRARY_TEST_HISTORY](LIBRARY_TEST_HISTORY.md).
