# Benchmark graphique AMOS / AMCAF / AGA — baseline avant optimisation Blitter

**Date : 12 novembre 2026. Statut : résultats AMOS interprété ET compilé sous WinUAE, issus des captures utilisateur.**

Référence de performance **avant le chantier M17 (après M16)**. Ce document archive les deux exécutions du [benchmark V1](graphics_32c.asc), les trois passages du [benchmark V2 interprété](graphics_32c_v2.asc) (référence R44) et les **trois passages de V2 compilé avec le correctif AMOS Compiler R46 C1**. **Aucune optimisation du Blitter n'est engagée par ce bilan.**

## Configuration et méthode

- PAL **320 × 256, 32 couleurs indexées = 5 bitplanes**, fond index 0 et dessin index 31.
- `A` = AMOS Professional natif ; `M` = AMCAF ; `G` = extension AGA. Les campagnes V1/V2 historiques ont été lancées **en interprété AMOS sous WinUAE** ; la nouvelle campagne V2 utilise un **exécutable AMOS Compiler sous WinUAE**.
- Horloge `Timer` AMOS : **1 tick = 20 ms**. Durées inférieures à quelques ticks insuffisantes pour conclure.
- **V1** : résultats cumulés pour 3 passages par exécution ; **V2 interprété et V2 compilé** : 3 temps individuels par moteur/opération, avec médiane calculée. Les charges et la source [`graphics_32c_v2.asc`](graphics_32c_v2.asc) sont identiques.
- AMOS/AMCAF dessinent sur l'écran AMOS ; l'extension utilise son **écran privé AGA, back buffer et Safe**. Les charges et les 5 bitplanes sont comparables, **pas les architectures graphiques**.
- **Bibliothèque de référence dans le dépôt :** R44 v0.11.5, `dist/AMOSPro_AGA_LAST_GOOD.Lib`, SHA256 documenté `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`. **Empreinte du binaire réellement installé dans WinUAE non relevée** ; ne pas la présenter comme vérifiée.
- **Campagne compilée :** candidate expérimentale de compatibilité **R46 C1 monolithique** ([identité du binaire source et protocole](../docs/GATE_C_R46_MONOLITH_CANDIDATE.md)), d'après les essais de réparation Compiler du 12/11/2026. **Aucun SHA256 du fichier effectivement chargé lors de la compilation, ni de l'exécutable obtenu, n'a été relevé.** Ne pas présenter le binaire chargé comme vérifié cryptographiquement.
- **Configuration WinUAE exacte non relevée :** CPU et fréquence, cycle-exact/JIT, mémoire Chip/Fast, versions précises d'AMOS et d'AMCAF ; on ne peut donc pas garantir l'identité complète de l'environnement entre les deux campagnes. Les relever pour les prochains tests.

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

## Résultats V2 interprété — temps bruts par passage

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

## Résultats V2 compilé — candidate AMOS Compiler R46 C1

**Capture utilisateur du 12/11/2026.** Programme : [`graphics_32c_v2.asc`](graphics_32c_v2.asc) **compilé** avec la bibliothèque corrigée de la campagne R46 C1. Charges PAL 320×256×32, 5 bitplanes, 3 passages, `Timer` à 20 ms/tick. Les trois colonnes de chaque moteur sont les **temps individuels**, pas des sommes.

| Test | Opérations / passage | AMOS (essais 1 / 2 / 3) | AMCAF (essais 1 / 2 / 3) | AGA (essais 1 / 2 / 3) |
|---|---:|---:|---:|---:|
| Plot | 120 000 | 11 / 11 / 11 | 10 / 11 / 10 | 13 / 13 / 13 |
| Draw | 400 | 35 / 36 / 35 | 35 / 35 / 35 | 36 / 35 / 36 |
| Box | 225 | 54 / 53 / 54 | 53 / 53 / 53 | 54 / 53 / 53 |
| Circle | 8 000 | 15 / 16 / 16 | 14 / 14 / 14 | 11 / 10 / 11 |
| Bar / Fill | 100 | 40 / 40 / 41 | N/A | 54 / 55 / 54 |
| Clear | 80 | 86 / 87 / 87 | 57 / 58 / 58 | 117 / 116 / 117 |

La capture confirme **`AGA ERR 0`**, `CIRCLE M = 5 BCIRCLE / RING` et **`V2 FINISHED - CLOSE RETURNED`**, sans Guru visible. C'est un **PASS du benchmark V2 compilé** (dont la fermeture AGA), **pas une validation exhaustive Gate C de toutes les API**. Les autres tests Compiler de [R46 C1](../docs/GATE_C_R46_MONOLITH_CANDIDATE.md) restent distincts.

### Médianes V2 compilé — ticks de 20 ms

| Test | AMOS | AMCAF | AGA |
|---|---:|---:|---:|
| Plot | 11 | 10 | 13 |
| Draw | 35 | 35 | 36 |
| Box | 54 | 53 | 53 |
| Circle | 16 | 14 | 11 |
| Bar / Fill | 40 | — | 54 |
| Clear | 87 | 58 | 117 |

### Comparaison interprété → compilé (médianes)

La variation indiquée entre parenthèses est **celle du temps mesuré** : un pourcentage négatif représente un temps inférieur en compilé.

| Test | AMOS interprété → compilé | AMCAF interprété → compilé | AGA interprété → compilé |
|---|---|---|---|
| Plot | 13 → 11 (-15,4 %) | 13 → 10 (-23,1 %) | 16 → 13 (-18,8 %) |
| Draw | 36 → 35 (-2,8 %) | 35 → 35 (0 %) | 36 → 36 (0 %) |
| Box | 53 → 54 (+1,9 %) | 53 → 53 (0 %) | 54 → 53 (-1,9 %) |
| Circle | 16 → 16 (0 %) | 15 → 14 (-6,7 %) | 11 → 11 (0 %) |
| Bar / Fill | 40 → 40 (0 %) | — | 54 → 54 (0 %) |
| Clear | 87 → 87 (0 %) | 58 → 58 (0 %) | 117 → 117 (0 %) |

**Constats sur ce scénario :**

- **Plot** : temps réduit de **15,4 % pour AMOS** (13 → 11 ticks), de **23,1 % pour AMCAF** (13 → 10) et de **18,8 % pour AGA** (16 → 13).
- **Draw, Box, Circle, Bar / Fill et Clear** : la plupart des variations sont nulles ou de **1 tick**, soit à peine la résolution de la mesure ; ne pas interpréter ces différences comme des gains mesurés de façon robuste.
- **Circle en compilé :** AGA reste le plus rapide sur ce cas (11 ticks contre 16 pour AMOS, 14 pour AMCAF), sous réserve de l'équivalence visuelle des algorithmes.
- **Blitter :** `Aga Blit Fill` reste à **54 ticks** contre **40** pour `Bar` AMOS (+35 % de temps). `Aga Blit Clear` reste à **117** contre **58** pour AMCAF (environ **2,02 fois le temps**). Le travail M17 demeure justifié.
- Le benchmark chronomètre la **boucle, la préparation des coordonnées et l'appel**, pas uniquement les instructions 68000 de l'extension. La comparaison R44 interprété / R46 C1 compilé mêle changement de mode d'exécution **et** changement de binaire AGA : elle ne prouve pas à elle seule un gain intrinsèque du compilateur.



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
- `Aga Plot` est plus lent en interprété, mais passe de 16 à 13 ticks en compilé pour la charge V2. Draw et Box restent proches des alternatives. `Aga Circle` donne le meilleur temps de ce scénario dans les deux modes, sans preuve d'identité pixel à pixel avec AMOS/AMCAF.
- `AGA ERR 0` **ne valide pas chaque appel de la boucle** : le benchmark ne contrôle que le dernier retour de chaque série AGA. Contrôler aussi les pixels, les retours et les swaps en validation fonctionnelle.
- Vérifier d'abord `Safe/Disp`, nombre d'appels à `BltBitMap` / `WaitBlit`, temps par bitplane et travail CPU/AP20. Ne pas supprimer de barrière sans preuve de sûreté.

## Contrat de re-test obligatoire après M17 (donc après M16)

1. **Ne pas lancer M17 avant clôture de M16.** Sauvegarder R44 `LAST_GOOD` et ses archives figées ; toute optimisation nécessite une candidate séparée.
2. Tester Fill/Clear sur tous les nombres de plans 1 à 8, couleur 0/non nulle, limites, refus, back buffer, `Safe`, `Disp`, `Swap`, réouverture et libération mémoire. Garder les Gates distinctes : A CPU/CI, B AMOS interprété/WinUAE, C Compiler, D Amiga réel.
3. **Rejouer exactement le même [`graphics_32c_v2.asc`](graphics_32c_v2.asc)** dans les **deux modes interprété ET compilé** : même écran, mêmes charges, même profil WinUAE (CPU/JIT/Chip/Fast) **pour chaque mode**, trois passages par moteur, références `R44 interprété` et `R46 C1 compilé` conservées distinctement. Archiver les temps bruts, médianes et comparaison chiffrée **avant/après** dans un **nouveau MD du dossier `benchmarks/`**, lié à ce fichier.
4. Contrôler le rendu et les non-régressions, sans déclarer un gain sur une simple réduction de ticks non reproductible. Ne promouvoir aucune bibliothèque sans validation utilisateur.

## Références

- [Sources benchmark V1](graphics_32c.asc) · [V2](graphics_32c_v2.asc) · [protocole V2](README_V2.md).
- [Roadmap M16 et M17](../docs/ROADMAP.md) · [Correctif AMOS Compiler R46 C1](../docs/GATE_C_R46_MONOLITH_CANDIDATE.md).
- [M6 — Fill](../docs/M6_BLITTER_R14.md) · [M6 — Clear](../docs/M6_BLITTER_R15.md) · [M12 — Safe Blitter](../docs/M12_SAFE_BLITTER_R27.md).
