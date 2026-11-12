# Test AMOS actif — M17/R55 Blitter groupé

**Unique test actif :** [`M17_R55_BLIT_GROUP_01.asc`](M17_R55_BLIT_GROUP_01.asc). Il exerce `Aga Blit Fill`, `Aga Blit Clear`, `Aga Blit Copy`, `Safe` et les 40 swaps sur `examples/demo.iff` 320×256×256 couleurs, avec couleurs mixtes 3/28/224 ; attendu : `RESULT 1`, `CLOSE RETURNED`, image correcte et aucun blocage.

**Unique bibliothèque de travail :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) **R55 v0.13.0**, SHA256 `97f48ccb946ced9bad0b661cbabff00440a4e5a07aeef49021b215b269fcf9ad`, Gate A CPU/CI PASS ; **Gate B AMOS interprété/WinUAE PASS** (capture `RESULT 1` et `CLOSE RETURNED`), **Gate C nouvel exécutable compilé/WinUAE PASS confirmé par l'auteur, sans capture**, Gate D Amiga physique NON TESTÉE.

`dist/AMOSPro_AGA_LAST_GOOD.Lib` conserve R54 v0.12.9 validée, sans changement. Les ressources ABK déjà présentes restent pour les tests historiques, qui ne sont plus actifs dans ce dossier. À la validation de R55, archiver uniquement l'ASC approuvé selon la procédure du projet.

**Affichage final :** `Wait Key` est placé après `CLOSE RETURNED` pour conserver les résultats à l'écran jusqu'à une touche, notamment dans le programme compilé. Cette seule ligne de confort a été ajoutée après la validation B/C rapportée ; elle ne change aucune primitive de la bibliothèque.
