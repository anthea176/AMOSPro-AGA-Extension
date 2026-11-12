# Benchmark graphique 320×256×32 — AMOS / AMCAF / AGA

## Benchmark cible : Copy (M17/R57)

**[Screen Copy AMOS vs Aga Blit Copy](README_COPY_32C.md)** — [source ASCII `copy_32c_r57.asc`](copy_32c_r57.asc), quatre géométries (alignée, décalée, grande zone et recouvrement), trois passages, PAL 320×256×32, interprété et compilé. **En attente des mesures utilisateur.** Aucun changement de la R57, de `LAST_GOOD` ou de `tests/current/`.

**V1 : exécution AMOS interprété / WinUAE confirmée par capture utilisateur (12/11/2026), `AGA ERR 0` et `BENCH FINISHED - CLOSE RETURNED`.** Les durées restent des observations, pas des preuves d'optimisation. Le benchmark ne modifie ni la bibliothèque AGA ni ses archives / tests `LAST_GOOD`.

## Second run

**Résultats mesurés V1/V2 et référence avant M17 :** [rapport de benchmark](RESULTATS_32C_BASELINE_R44_2026-11-12.md). Données brutes, médianes, limites et protocole de nouveau test après M16/M17.

**[Nouveau benchmark V2 : graphique 320x256x32 avec trois temps séparés](README_V2.md)** — source [`graphics_32c_v2.asc`](graphics_32c_v2.asc), sans changer la bibliothèque AGA. La V1 est conservée telle quelle.

**Mesures V1, ticks cumulés sur 3 passages :** PLOT (AMOS/AMCAF/AGA) 5/3/6 ; DRAW 105/105/107 ; BOX 160/159/159 ; CIRCLE 0/1/0 (mesure non exploitable) ; BAR 121/N/A/164 ; CLEAR 261/174/352. Une seule exécution, statistiques non établies.

## Fichier et installation

`graphics_32c.asc` est un **source ASCII** AMOS Pro autonome, sans IFF ni ABK. Il exige **AMOS Professional**, **AMCAF v1.40+** et **AMOSPro_AGA.Lib R43+** (R44 v0.11.5 recommandée). AMCAF occupe normalement le slot 8 et l'extension AGA utilise historiquement le 14 si disponible. **Ne changez pas les slots déjà installés.**

Copier le fichier sur un volume Amiga ou WinUAE ; dans l'éditeur AMOS, créer un programme vide, puis **Project → Merge ASCII**. Exécuter **en mode interprété**. Le programme montre trois dessins de contrôle successifs, ferme l'écran AGA et affiche les chiffres dans AMOS.

## Protocole

- **320 × 256 pixels**, mode PAL, **32 couleurs indexées = 5 bitplanes** ; dessin en **index 31 (blanc)** sur **index 0 (noir)**.
- Chaque famille est répétée **3 fois** avec un petit échauffement préalable. Le chronomètre AMOS `Timer` compte en unités de 1/50 seconde, soit **20 ms**. Les résultats sont le **total de ticks sur les trois répétitions** : plus petit = plus rapide pour la même charge.
- Le temps mesuré inclut la boucle AMOS, la préparation des coordonnées et l'appel. Il **n'inclut pas** ouverture/fermeture d'écran, nettoyage préparatoire, sortie texte, échange de buffers ni attente VBL. Un `Blitter Wait` placé à la fin d'une série native/AMCAF garantit une barrière de fin ; pour AMCAF `CLEAR`, une barrière est également présente après chaque groupe de cinq plans.
- Les deux premières méthodes dessinent dans un **écran AMOS natif**, la troisième dans le **back buffer privé AGA**. Le nombre de bitplanes et la géométrie coïncident, **mais pas le modèle écran/mémoire**. Il s'agit de vitesse observable depuis AMOS, pas d'une isolation des algorithmes assembleur.
- L'ordre du programme est **AMOS → AMCAF → AGA**, le CPU/Chip RAM/Fast RAM/JIT/caches restant identiques durant un lancement.

## Tableau des comparaisons

| Test | AMOS Pro natif | AMCAF | Extension AGA | Charge/essai |
|---|---|---|---|---|
| PLOT | `Plot x,y` avec `Ink 31` | `Turbo Plot x,y,31` | `Aga Plot(x,y,31)` | 12 000 points |
| DRAW | `Draw x1,y1 To x2,y2` | `Turbo Draw x1,y1 To x2,y2,31` | `Aga Draw(x1,y1,x2,y2,31)` | 400 lignes |
| BOX | `Box x1,y1 To x2,y2` | **4 × `Turbo Draw`** | `Aga Box(x1,y1,x2,y2,31)` | 225 rectangles |
| CIRCLE | `Circle cx,cy,r` | **5 × `Bcircle`** : une fois par bitplane | `Aga Circle(cx,cy,r,31)` | 170 cercles |
| BAR | `Bar x1,y1 To x2,y2` | **N/A** | `Aga Blit Fill(x,y,width,height,31)` | 100 rectangles 200×136 |
| CLEAR | `Cls 0` | **5 × `Blitter Clear 0,plane` + `Blitter Wait`** | `Aga Blit Clear(0,0,320,256)` | 80 effacements |

**Comparaison équivalente mais non strictement 1:1 pour BOX/CIRCLE/CLEAR :** AMCAF n'a pas une unique primitive générique de contour RECTANGLE. `Bcircle` ne dessine que **dans un plan**, donc il faut **5 appels**, sur les bitplanes 0 à 4, pour afficher l'index couleur 31 dans une image 32 couleurs. Les algorithmes de rasterisation de cercle peuvent différer légèrement. AMCAF `Fcircle` réalise un **cercle plein** et n'est pas assimilable à `Circle` ; il n'est pas utilisé ici. Les commandes `F Plot` et `F Circle` de Turbo Extension 1.9 ne sont **pas** des commandes AMCAF.

**BAR AMCAF = N/A** : pas de primitive rectangulaire pleine strictement équivalente retenue. Ne pas interpréter la valeur sentinelle `-1` comme un temps ou une défaite.

## Relever les résultats

Les lignes finales indiquent `A` (AMOS), `M` (AMCAF) et `G` (AGA) en **ticks**, et le nombre réel de formes traitées pendant les 3 essais. Les conditions de bon déroulement sont `AGA ERR 0` et `BENCH FINISHED - CLOSE RETURNED`.

Pour chaque profil WinUAE, conserver : **processeur, fréquence, JIT/cycle-exact, Chip/Fast RAM, PAL, version d'AMOS, version AMCAF, version binaire de l'extension AGA et chronos bruts**. Refaire plusieurs lancements et calculer une médiane si l'écart est faible.

Si un résultat vaut 0 ou moins de 10 ticks cumulés, augmenter en haut du programme les charges `_NP`, `_NL`, `_NB`, `_NC`, `_NF` ou `_NE`, puis relancer les **trois moteurs avec les mêmes comptes**. Les mesures à la granularité 20 ms ne justifient pas des ratios à plusieurs décimales.

Le code **n'a pas été exécuté sous AMOS/WinUAE** dans cette préparation. La compilation AMOS et les mesures sur AGA physique sont également **non testées**. On pourra analyser les écarts après une capture utilisateur.

## Références de syntaxe

- [AMOS Pro : Graphics](https://amospromanual.dev/06-04-graphics.html)
- [AMCAF V1.40 — Chris Hodges](https://www.ultimateamiga.com/HostedProjects/AMOSFactory/AMCAFguide/index.html), dont `Turbo Plot`, `Turbo Draw`, `Bcircle` et `Blitter Clear`.
- Dans ce dépôt : `docs/M15_PLOT_R40.md`, `docs/M15_DRAW_R41.md`, `docs/M15_BOX_R42.md`, `docs/M15_CIRCLE_R43.md`, `docs/M6_BLITTER_R14.md`, `docs/M6_BLITTER_R15.md`.

La commande `Aga Detect` figure dans AMCAF **et** dans l'extension AGA : ce benchmark évite volontairement ce nom homonyme et valide son écran directement par `Aga Screen Open`.
