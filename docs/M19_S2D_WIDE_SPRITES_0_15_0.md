# 0.15.0-alpha.1 — M19 S2d, Sprites larges

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
