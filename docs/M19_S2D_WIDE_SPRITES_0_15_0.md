# 0.15.0-alpha.1 — M19 S2d, Sprites larges

**28/11/2026 — S2d-P2a : préparation ExtSprite détachée source-only engagée en parallèle de la qualification P1, autorisation auteur « continu ne tarrete pas ».** [CI P1 46127045983](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46127045983) : shard chain PASS sur les deux modèles AP20, build P1 observé 161096 octets SHA256 `7741b1945206bf2176ccf1dfed4f8ec8d65c5e64eccd09ae50e5804c53d6da76`, blob `3c6faa1ef3b4d833cf357146d05743d3647510c5`, 105 commandes/219 AP20, UNIT213 20498, marge WORD 45036, PC16 max 3658 avec réserve 16384. Autres shards P1 à relever. P2a : validation AGSP v1 complète, InitBitMap, AllocSpriteDataA (A2=bitmap, A1=tags), FreeSpriteData (A2) sur échec seconde allocation. Sprite simple V39+, attaché V40+ seulement pour ce composant : V39 a deux défauts documentés (ATTACH dans les données et GSTAG_ATTACHED), aucun contournement non qualifié ni décision d'abandon de V39. [CI P2a](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-ext-prepare-gate-a.yml) à relever. Aucune acquisition de canal ni publication DMA, aucune écriture ExtSprite/FM0DE, aucune activation. S2c-E1/ASC/ABK/LAST_GOOD inchangés.

**28/11/2026 — S2d-P1 intégration capture source-only engagée, autorisation auteur « ok on continu ».** [P0 CI 46125716891](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46125716891) PASS : six groupes CPU, fixture 24 images 6836 octets SHA256 `f8816b944102c5826f9819b84747acd61fd4468423bf815c25e128a9dcfe4e64`, régressions S1/S2c et contrôle du couple actif PASS. [Requalification intégrale S2c-E1](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/46124380826) PASS. P1 relie le Get AGA Sprite existant aux kernels larges via le pont ScreenBuffer Safe/WaitBlit et la transaction AGSP inchangée : largeur inclusive 16/32/64, workspace 4120+128*W (6168/8216/12312), staging oldlen+96+(W/2)*H, largeur explicite dans les requêtes privées. Builder en mémoire depuis le source exact S2c-E1, vérification du parent SHA et AP20, ancien mode sans option inchangé. [CI P1](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-public-capture-gate-a.yml) à relever : aucune validation intégrée revendiquée avant les résultats. Aucune modification DMA, token, bibliothèque, ASC, ABK, LAST_GOOD ni archive. Prochaine étape après qualification P1 : ExtSprite V39+ (P2).

**28/11/2026 — S2d-P0, sources de capture/repack 16/32/64 engagées pour 0.15.0-alpha.1 (pas de Lib intégrée).** Deux kernels MC68020 isolés, dérivés de S2c sans modification de ses sources : descripteur capture +62.W largeur explicite, repack +36.W largeur et +38.W réservé zéro ; stride=W/8, 4*stride*H maximal 8192 octets. AGSP v1 sur disque inchangé ; aucune modification DMA/OS/AP20. Générateur de 24 images contrastées (3 largeurs × 4 familles × 2 frames, sous-palettes RGB24 cohérentes) et banc CPU avec oracle AGSP indépendant, canaris, conservation des entrées, tous les comptes de couleurs, hauteur 1/256, bords, transparence, 16 opaques et refus, remplacements entre largeurs/profondeurs. [CI P0](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/workflows/m19-s2d-wide-capture-gate-a.yml) à relever ; aucun PASS CPU revendiqué avant résultat. La suite intégrera la capture dans les commandes existantes, puis la voie ExtSprite V39 qualifiée séparément. S2c-E1 reste active, B/C fonctionnelles PASS. Aucun changement du couple actif, archives ni LAST_GOOD.

**Chantier suivant : 0.15.0-alpha.1 (M19 S2d)** : capture/repack puis affichage Sprite 16/32/64px ; largeur commune par contexte, API existante, couleur franche et motifs asymétriques. Source-only jusqu'à preuve Gate A et bascule explicitement autorisée. Cible publique 0.15.0 ; objectif final 1.0.0. Ne pas renommer les binaires historiques.

## Contraintes et découpage

1. P0 : capture/repack AGSP v1 16/32/64px, 1..256 lignes, 2/4 plans, RGB24 exact, transparence explicite, refus 16 opaques ; aucun changement du format disque, banque ni DMA.
2. P1 : intégrer le chemin de capture dans les tokens publics existants, gérer les bornes inclusives et la taille des allocations ; reproduire S2c-E1 à l'identique sans option. Préserver les protections, toute ancienne ABK et ASC.
3. P2 : qualifer la voie ExtSprite V39+ (AllocSpriteDataA, GetExtSpriteA, ChangeExtSpriteA, FreeSpriteData, FreeSprite) avec ownership, blank, mode de fetch global, alignement, fences et Close/End. Pas de manipulation brute de FMODE ; aucune écriture directe dans les champs ExtSprite internes. Une largeur par contexte, changements de largeur seulement après retraite complète, compatibilité avec curseur Intuition et autres canaux à démontrer. L'éventuel nouveau token nécessite un contrat distinct approuvé.
4. P3 : intégration AP20 et campagne ASC unique avec 16/32/64, simple/attaché, capture, animation, déplacement, refus et mémoire ; Gate A avant activation ; B/C réelles séparées.

Références OS : [NDK graphics/sprite.h](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node060B.html) ; [graphics.library autodocs](https://developer.amigaos3.net/autodocs/graphics.library/). Les contraintes et retours précis doivent être recoupés avant tout appel natif ExtSprite.

## Visuel demandé

Fond sombre neutre, trois familles de 3 couleurs simples (rouge/orange/jaune, bleu/cyan/blanc, vert/lime/rose), 15 couleurs opaques distinctes pour l'attaché. Sous-palettes partagées 21..23, 25..27, 29..31 compatibles avec 17..31. Deux frames distinctes à palette identique, silhouette asymétrique, bandes alternées et repères des frontières de mots 16px, bords gauche/droit différenciés, transparence réelle. Palette RGB24 exacte ; aucun dégradé ambigu.

## Statut

Parent actif S2c-E1, [Gates B/C fonctionnelles PASS](M19_S2C_P1E_RUNTIME_COMPILER_2026-11-28.md). Aucun nouveau binaire ni changement public à ce stade. Le numéro 0.15.0-alpha.1 est réservé à la future candidate intégrée, pas au composant P0. LAST_GOOD L2b intacte. Aucun autre dépôt ou branche.

## Composants P0 livrés (source only)

- [Capture MC68020](../src/native/m19_s2/M19_S2D_AGSP_CAPTURE_MC68020.s) : descripteur de 64 octets, largeur explicite à +62 ; allocation de stage à charge du futur appelant, image plane-major de (W/8)*H*depth.
- [Repack MC68020](../src/native/m19_s2/M19_S2D_AGSP_REPACK_MC68020.s) : requête de 40 octets, largeur à +36 et réservé à +38 ; dimensions/stride/données canoniques AGSP v1, transactions détachées.
- [Banc CPU](../tools/test_m19_s2d_capture_repack_cpu.py) et [générateur visuel](../tools/m19_s2d_visual_fixture.py) : sortie ABK de préparation exclusivement hors dépôt, pas d'ASC ou d'ABK actif nouveau.

Les deux kernels n'ont pas encore de preuve CPU au moment de l'écriture. Le mode de largeur global et la publication ExtSprite n'ont pas été implémentés. Aucun changement utilisateur installable.

## Composants P1 (source only, qualification en attente)

- `src/native/m19_s2/M19_S2D_GET_PUBLIC_MC68020.s`, `M19_S2D_CAPTURE_PIPELINE_MC68020.s`, `M19_S2D_SCREEN_RGB24_MC68020.s` : variantes source de la voie publique, protections et contrat de retour inchangés.
- `tools/build_m19_s2d_capture_in_memory.py` : réassemblage des sources préparées par le builder exact S2c, substitution dans un répertoire temporaire indépendant ; seuls UNIT213 et les trois offsets Sprite sont candidats au changement. Le binaire P1 interne n'est pas installable ; la version 0.15.0-alpha.1 reste réservée à P3.
- `tools/test_m19_s2d_public_capture_gate_a.py` : modèles AP20 Runtime/Compiler, oracle AGSP indépendant, canaris, 1/256 lignes, limites, palette, refus, erreurs allocation, changement de propriétaire/génération, régression 16px et Display mixte.

## P2a — ABI OS et contrat de préparation détachée

Références NDK / Autodocs consultées le 28/11/2026 :
- [graphics/sprite.h](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node060B.html), [graphics/gfx.h](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_3._guide/node05DC.html), [exec/libraries.h](https://amigadev.elowar.com/read/ADCD_2.1/Includes_and_Autodocs_2._guide/node009C.html).
- [InitBitMap](https://d0.se/autodocs/graphics.library/InitBitMap) : -390, A0/D0/D1/D2.
- [AllocSpriteDataA](https://d0.se/autodocs/graphics.library/AllocSpriteDataA) : -1020, A2/A1, D0 pointeur ou zéro. SPRITEA_Width=$81000000 ; SPRITEA_Attached=$81000008 prend les plans 2/3 du même BitMap. Les plans source peuvent être en Fast.
- [GetExtSpriteA](https://d0.se/autodocs/graphics.library/GetExtSpriteA) : -930, A2/A1, D0 canal ou -1 ; GSTAG_SPRITE_NUM=$82000020, GSTAG_ATTACHED=$82000022.
- [ChangeExtSpriteA](https://d0.se/autodocs/graphics.library/ChangeExtSpriteA) : -1026, A0/A1/A2/A3, succès non nul. Ne jamais traiter l'ancien pointeur comme libérable avant retrait prouvé.
- [FreeSpriteData](https://d0.se/autodocs/graphics.library/FreeSpriteData) : -1032, A2. L'OS possède le format et l'allocation des données ; ne pas utiliser FreeVec sur le pointeur ExtSprite.

Les deux anomalies V39 imposent des chemins séparés : tag de paire non fonctionnel, acquisition séparée requise ; bits ATTACH manquants, correctif documenté des mots de contrôle selon largeur. P2a refuse temporairement les images attachées sur V39 avant allocation. Le support V39 attaché reste un point à résoudre avant de déclarer la qualification V39+. Ne jamais écrire es_wordwidth/es_flags ou FMODE. Sur V40+, aucune retouche ATTACH manuelle.

Le composant [M19_S2D_EXT_PREPARE_MC68020.s](../src/native/m19_s2/M19_S2D_EXT_PREPARE_MC68020.s) utilise un BitMap et tags privés en pile, source AGSP stable et strictement validée, appel synchrone. Retour D0/D1 deux pointeurs détachés (D1=0 pour simple), ou zéro/zéro. Le second échec libère le premier via l'OS. Pas de pointeur source conservé ; pas de GetExtSpriteA. Le banc CPU [test_m19_s2d_ext_prepare_cpu.py](../tools/test_m19_s2d_ext_prepare_cpu.py) vérifie les registres, tags, plans et pixels avec un oracle indépendant, négatifs et rollback, conservation des entrées, aucune écriture hors pile. Le mock ne prouve ni la conversion réelle d'AmigaOS ni l'alignement Chip/DMA réel.

P2b restant : allocation de blank(s), attribution du contexte/largeur globale et ownership; acquisition des paires, publication, changements et retraits, vérification références/attente bornée, Close/End, coexistence curseur et autres Sprite. La documentation ne garantit pas la synchronisation de deux ChangeExtSpriteA ; ne pas libérer de frame possiblement exposée ou publier un demi-attaché.
