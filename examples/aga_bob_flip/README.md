# AGA Bob Flip — Démonstration visuelle à formes asymétriques

Ce programme n'est **pas** le test de campagne M19 actuel. Il illustre l'API P2b **`Aga Bob Flip(N,Mode)`** de la **Lib P2d** de travail, sans modifier la Lib ni le code natif.

## Affichage

L'image AGBO unique est **un F asymétrique de 32×32 pixels**, à barre longue vers la droite, barre médiane plus courte et accent de couleur ; index 0 transparent via `Make AGA Bob Mask 1,0`. Quatre Bobs indépendants présentent les modes :

| Position | Mode | Rendu attendu |
| --- | --- | --- |
| Haut gauche | 0 | F normal |
| Haut droite | 1 | F retourné horizontalement |
| Bas gauche | 2 | F retourné verticalement |
| Bas droite | 3 | F retourné sur les deux axes |

Le hotspot 0 de l'image est inversé avec la géométrie par `Aga Bob Flip` : les coordonnées des Bobs retournés sont décalées de **31 pixels** pour garder les quatre silhouettes alignées dans leurs cases.

L'écran AGA est placé automatiquement devant l'écran AMOS par **`Amos To Back`**, après initialisation des deux pages et le premier affichage. Une touche ferme l'écran et restaure **`Amos To Front`**.

## Journaux selon le mode

| Mode | `Prg State` | Fichier RAM |
| --- | ---: | --- |
| Interprété strict | `0` | `RAM:AGA_BOB_FLIP_INTERPRETED.TXT` |
| Runtime | `1` | `RAM:AGA_BOB_FLIP_RUNTIME.TXT` |
| Compiler | `-1` | `RAM:AGA_BOB_FLIP_COMPILED.TXT` |

Autre état : `RAM:AGA_BOB_FLIP_UNKNOWN.TXT`. Le programme affiche le chemin réellement choisi après fermeture et ajoute `RUN_MODE` dans le journal. Le fonctionnement en Compiler **n'est pas encore validé**.

## Exécution

1. Installer l'unique `dist/AMOSPro_AGA.Lib` P2d sous `APSystem`, redémarrer AMOS Pro/WinUAE AGA 68020+.
2. Dans un programme vierge : **Project → Merge ASCII** sur [FLIP_VISUAL.asc](FLIP_VISUAL.asc). La banque 24 doit être libre.
3. Exécuter en Runtime, comparer les quatre orientations visibles et appuyer sur une touche pour revenir sous AMOS.
4. Récupérer `RAM:AGA_BOB_FLIP_RUNTIME.TXT` : les quatre champs `FLIP0..3` doivent valoir 1, `RESULT 1`, `ERR 0`, `SWAPS 2`, `CLOSE_RETURNED 1`, `VERDICT PASS`.

**Statut au dépôt :** structure source contrôlée localement, **Runtime et vrai Compiler NON TESTÉS**. Le journal `VERDICT PASS` du programme vérifie les appels et le nettoyage, **pas la correction visuelle de tous les pixels** : l'utilisateur doit contrôler les quatre orientations à l'écran.
