# 0.15.0-alpha.1 — M19 S2d, Sprites larges

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
