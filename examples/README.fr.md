# AMOSPro AGA — 6 exemples simples

[English](README.md) | **Français** · [Installation](../INSTALL.fr.md)

Ces programmes sont des **démonstrations destinées aux utilisateurs**, et non les anciens tests de régression. Ils utilisent la [`AMOSPro_AGA.Lib` courante](../dist/AMOSPro_AGA.Lib) dans **AMOS Professional interprété**.

| Fichier | Démonstration | Utilisation |
|---|---|---|
| [`screen.asc`](screen.asc) | Ouvrir/fermer un écran 320×256×256 couleurs | Affiche un motif environ 3 secondes, sans image |
| [`picture.asc`](picture.asc) | Lire une image IFF, la charger, faire le Swap | Choisir [`demo.iff`](demo.iff), puis appuyer sur une touche |
| [`blitter.asc`](blitter.asc) | `Aga Blit Fill`, `Clear` et `Copy` | Choisir `demo.iff`, regarder les formes, appuyer sur une touche |
| [`copper.asc`](copper.asc) | Raster Copper RGB4 avec `Wait`/`Move` | Bandes horizontales rouge/vert/bleu/noir, puis une touche |
| [`mouse.asc`](mouse.asc) | Position, clics, lecture clavier | Cliquer gauche/droit, puis une touche ou attendre 5 secondes |
| [`collide.asc`](collide.asc) | R25 `Aga Rect Overlap`, souris, Blitter, double buffering et VBL | Choisir `demo.iff`, entrer/sortir du rectangle bleu (vert = libre, rouge = collision) ; clic gauche pour quitter ou 900 images maximum |

Les `.asc` sont des **sources texte ASCII**, pas des programmes AMOS tokenisés. Dans AMOS, repartir d'un programme vide puis utiliser **Project → Merge ASCII** pour chaque fichier. Le menu `Load` classique ne convient pas. Pour `Fsel$("**")`, sélectionner `examples/demo.iff` depuis un volume visible par AmigaOS.

`demo.iff` est une mire originale 320×256, 8 bitplanes et 256 couleurs, également conservée dans `iff-TEST/`. Les six exemples disposent de contrôles statiques, **mais chacun de ces programmes simplifiés reste à valider de bout en bout sous WinUAE**. Les tests de régression R23 (souris/clavier/Ctrl+C) et R25 (collisions) ont, eux, été validés sous AMOS interprété/WinUAE ; cela ne valide pas automatiquement ces versions pédagogiques.

**Pourquoi charger un IFF pour `collide.asc` ?** `demo.iff` fournit le mode PAL et la palette (index 3 = bleu, 28 = vert, 224 = rouge). L'exemple efface tout le back buffer à chaque image : **les pixels de l'IFF ne sont pas affichés et ne participent pas aux collisions**. La fonction `Aga Rect Overlap` fonctionne sans IFF ni écran ; le fichier n'est utilisé ici que pour obtenir les bonnes couleurs.

Les anciens essais restent classés dans [`tests/current/`](../tests/current/), [`tests/passed/`](../tests/passed/) et [`tests/historical/`](../tests/historical/). **Ils ne font pas partie du jeu d'exemples simplifié.**

**Licences :** sources des exemples sous [MIT](../LICENSE). L'image **n'est pas sous MIT** : [notice graphique](../ASSETS_LICENSE.md), consultation/tests locaux autorisés, redistribution/réutilisation de l'illustration séparément soumise à autorisation.
