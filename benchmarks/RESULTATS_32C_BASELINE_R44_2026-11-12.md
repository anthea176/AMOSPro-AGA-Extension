# Benchmark graphique AMOS / AMCAF / AGA — baseline avant optimisation Blitter

**Date : 12 novembre 2026. Statut : résultats AMOS interprété / WinUAE fournis par captures utilisateur.**

Référence de performance **avant le chantier M17 (après M16)**. Ce document archive les deux exécutions du [benchmark V1](graphics_32c.asc) et les trois passages distincts du [benchmark V2](graphics_32c_v2.asc). **Aucune optimisation du Blitter n'est engagée par ce bilan.**

## Configuration et méthode

- PAL **320 × 256, 32 couleurs indexées = 5 bitplanes**, fond index 0 et dessin index 31.
- `A` = AMOS Professional natif ; `M` = AMCAF ; `G` = extension AGA. Code lancé **dans l'interpréteur AMOS sous WinUAE**.
- Horloge `Timer` AMOS : **1 tick = 20 ms**. Durées inférieures à quelques ticks insuffisantes pour conclure.
- **V1** : résultats cumulés pour 3 passages par exécution ; **V2** : 3 temps individuels, avec médiane calculée par moteur/opération.
- AMOS/AMCAF dessinent sur l'écran AMOS ; l'extension utilise son **écran privé AGA, back buffer et Safe**. Les charges et les 5 bitplanes sont comparables, **pas les architectures graphiques**.
- **Bibliothèque de référence dans le dépôt :** R44 v0.11.5, `dist/AMOSPro_AGA_LAST_GOOD.Lib`, SHA256 documenté `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`. **Empreinte du binaire réellement installé dans WinUAE non relevée** ; ne pas la présenter comme vérifiée.
- **Configuration WinUAE exacte non relevée :** CPU et fréquence, cycle-exact/JIT, mémoire Chip/Fast, versions précises d'AMOS et d'AMCAF. Les relever pour les prochains tests.

Les programmes exécutent un échauffement, excluent du chronométrage l'ouverture d'écran, les effacements préparatoires, les swaps et les attentes VBL intentionnelles ; `Blitter Wait` ferme les séries AMOS/AMCAF. V2 ajoute un `Blitter Wait` après la `Bar` préparatoire de CLEAR (hors mesure).

## Résultats V1 — deux exécutions

Les deux captures V1 indiquent `AGA ERR 0` et `BENCH FINISHED - CLOSE RETURNED`. Durées **cumulées sur trois passages** (ticks).

| Test | Opérations V1 cumulées | AMOS (run 1 / 2) | AMCAF (run 1 / 2) | AGA (run 1 / 2) |
|---|---:|---:|---:|---:|
| Plot | 36 000 | 5 / 4 | 3 / 3 | 6 / 4 |
| Draw | 1 200 | 105 / 106 | 105 / 105 | 107 / 106 |
| Box | 675 | 160 / 160 | 159 / 159 | 159 / 159 |
| Circle | 510 | 0 / 1 | 1 / 2 | 0 / 0 |
| Bar / Fill | 300 | 121 / 121 | N/A | 164 / 162 |
| Clear | 240 | 261 / 261 | 174 / 174 | 352 / 348 |

**Attention :** Circle V1 (0 à 2 ticks) n'est pas une mesure significative. Les charges de Plot et Circle ont été augmentées dans V2.

## Résultats V2 — temps bruts par passage

Source **à conserver inchangée pour la mesure à l'issue de M17** : [`graphics_32c_v2.asc`](graphics_32c_v2.asc). La capture indique `AGA ERR 0` et `V2 FINISHED - CLOSE RETURNED`.

| Test | Opérations / passage | AMOS (essais 1 / 2 / 3) | AMCAF (essais 1 / 2 / 3) | AGA (essais 1 / 2 / 3) |
|---|---:|---:|---:|---:|
| Plot | 120 000 | 13 / 13 / 13 | 13 / 13 / 13 | 16 / 16 / 16 |
| Draw | 400 | 35 / 36 / 36 | 35 / 35 / 35 | 36 / 36 / 35 |
| Box | 225 | 53 / 53 / 53 | 53 / 53 / 53 | 54 / 54 / 53 |
| Circle | 8 000 | 16 / 16 / 16 | 15 / 15 / 15 | 11 / 11 / 10 |
| Bar / Fill | 100 | 40 / 40 / 40 | N/A | 54 / 54 / 55 |
| Clear | 80 | 87 / 87 / 87 | 58 / 58 / 58 | 116 / 117 / 117 |

### Médianes V2 — ticks de 20 ms

| Test | AMOS | AMCAF | AGA | Lecture des écarts |
|---|---:|---:|---:|---|
| Plot | 13 | 13 | 16 | AGA : +23,1 % de temps |
| Draw | 36 | 35 | 36 | Presque à égalité |
| Box | 53 | 53 | 54 | Presque à égalité |
| Circle | 16 | 15 | **11** | AGA : **-31,3 % de temps vs AMOS**, -26,7 % vs AMCAF |
| Bar / Fill | **40** | — | 54 | AGA Fill : **+35,0 % de temps vs AMOS Bar** |
| Clear | 87 | **58** | 117 | AGA Clear : **2,02 fois le temps d'AMCAF**, +34,5 % vs AMOS |

Les écarts sont calculés sur les durées mesurées pour ces charges, **pas sur des FPS**. Les moteurs n'utilisent pas nécessairement la même rasterisation, notamment pour les cercles. Un `Box` AMCAF = 4 `Turbo Draw` ; un `Circle` AMCAF = **5 `Bcircle`** (un par bitplane) ; `Bar` AMCAF est **N/A**, pas une mesure à zéro.

### Reproductibilité entre les campagnes

Les charges DRAW/BOX/BAR/CLEAR sont identiques en V1 et V2. Comparaison AGA en ticks **sur 3 passages** :

| Test | V1 run 2 | V2 somme des 3 passages |
|---|---:|---:|
| Draw (1 200) | 106 | 107 |
| Box (675) | 159 | 161 |
| Bar / Fill (300) | 162 | 163 |
| Clear (240) | 348 | 350 |

Les écarts de 1–2 ticks confortent la reproductibilité sur ce profil, sans remplacer des tests sur d'autres configurations.

## Interprétation technique (hypothèses, pas de corrections validées)

- **Priorité M17 :** `Aga Blit Fill` et `Aga Blit Clear`. Le chemin actuel Fill emploie `graphics.library/BltBitMap` avec synchronisation `WaitBlit` par bitplane ; Clear réutilise Fill pour l'index 0. Les synchronisations pourraient expliquer une partie du coût, **à profiler avant tout changement**.
- `Aga Plot` est plus lent sur V2 ; Draw et Box restent proches des alternatives. `Aga Circle` donne le meilleur temps de ce scénario, sans preuve d'identité pixel à pixel avec AMOS/AMCAF.
- `AGA ERR 0` **ne valide pas chaque appel de la boucle** : le benchmark ne contrôle que le dernier retour de chaque série AGA. Contrôler aussi les pixels, les retours et les swaps en validation fonctionnelle.
- Vérifier d'abord `Safe/Disp`, nombre d'appels à `BltBitMap` / `WaitBlit`, temps par bitplane et travail CPU/AP20. Ne pas supprimer de barrière sans preuve de sûreté.

## Contrat de re-test obligatoire après M17 (donc après M16)

1. **Ne pas lancer M17 avant clôture de M16.** Sauvegarder R44 `LAST_GOOD` et ses archives figées ; toute optimisation nécessite une candidate séparée.
2. Tester Fill/Clear sur tous les nombres de plans 1 à 8, couleur 0/non nulle, limites, refus, back buffer, `Safe`, `Disp`, `Swap`, réouverture et libération mémoire. Garder les Gates distinctes : A CPU/CI, B AMOS interprété/WinUAE, C Compiler, D Amiga réel.
3. **Rejouer exactement le même [`graphics_32c_v2.asc`](graphics_32c_v2.asc)** : même écran, mêmes charges, même mode AMOS, même configuration WinUAE (CPU/JIT/Chip/Fast), trois passages par moteur. Archiver les temps bruts, médianes et comparaison chiffrée **avant/après** dans un **nouveau MD du dossier `benchmarks/`**, lié à ce fichier.
4. Contrôler le rendu et les non-régressions, sans déclarer un gain sur une simple réduction de ticks non reproductible. Ne promouvoir aucune bibliothèque sans validation utilisateur.

## Références

- [Sources benchmark V1](graphics_32c.asc) · [V2](graphics_32c_v2.asc) · [protocole V2](README_V2.md).
- [Roadmap M16 et M17](../docs/ROADMAP.md).
- [M6 — Fill](../docs/M6_BLITTER_R14.md) · [M6 — Clear](../docs/M6_BLITTER_R15.md) · [M12 — Safe Blitter](../docs/M12_SAFE_BLITTER_R27.md).
