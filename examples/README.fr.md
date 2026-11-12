# AMOSPro AGA — 9 exemples simples

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
| [`show.asc`](show.asc) | **Démo animée R27 :** texte AGA natif, interface rétro, Blitter Fill/Clear/Copy sécurisés, rectangles animés et copiés, collision AABB et souris | Choisir `demo.iff`, observer les blocs verts/rouges et déplacer le curseur ; **clic gauche ou touche** pour quitter (arrêt automatique après 600 images au maximum) |
| [`fade_to_bank_r33.asc`](fade_to_bank_r33.asc) | **Démo visuelle R33 :** trois bandes colorées, rouge → vert → bleu → rouge, fondus de 150 VBL | Aucun IFF. **Écrase la banque AMOS 12** ; `Aga Swap` et `Amos To Back` sont exécutés **avant** les fondus. Pauses entre changements ; résultats après fermeture. **Démo testée par l'utilisateur sous WinUAE : fondu visible et fonctionnel (11/11/2026), sans mesure de FPS ni de durée réelle.** |
| [`font_bank_r38.asc`](font_bank_r38.asc) | **Démo BankFont AMCAF R38 :** afficher `Hwarf1252S.abk` et `Pix3M-1252L.abk` sur un même écran AGA 320×256 | Nécessite R38 v0.11.0 ; lancer depuis le répertoire `examples/` avec `Amcaf Fonts/` présent ; **remplace la banque AMOS 25** ; une touche pour quitter. |

**Démo de fontes R38 — `font_bank_r38.asc` :** charge successivement `Amcaf Fonts/Hwarf1252S.abk` et `Amcaf Fonts/Pix3M-1252L.abk` avec `Load "...",25`, puis `Aga Font Bank Select(Start(25),Length(25))` et `Aga Text`. Les deux ABK utilisent le numéro de banque 25, **écrasé par la démo**. `Erase 25` est sans danger après sélection réussie : R38 conserve une copie privée en Chip RAM. L’exemple restaure la fonte système avec `Aga Font Select("",0)` et ferme l’écran. Les chemins AmigaDOS utilisent `/` comme séparateur (contrairement aux chemins Windows avec `\\`) ; le répertoire AmigaDOS courant doit être `examples/`, par exemple en copiant ce dossier complet sur un volume Amiga. **L’extension AMCAF n’est pas nécessaire à l’exécution.** **La démo de fontes R38 fonctionne sous AMOS interprété/WinUAE (confirmation utilisateur du 12 novembre 2026).** Un [test distinct de 500 changements de fonte](../tests/passed/M14_R38_CHIP_RAM_STRESS_01.asc) a ensuite été validé sous WinUAE le 12/11/2026 sans baisse mesurée de Chip RAM libre.

**Attribution des fontes :** [Hwarf — licence/crédits](Amcaf%20Fonts/Hwarf-12xxS.licence) et [Pix3M — CC BY 3.0](Amcaf%20Fonts/Pix3M-12xxL.licence). Les graphismes des ABK ne relèvent pas de la licence MIT du code source.

Les `.asc` sont des **sources texte ASCII**, pas des programmes AMOS tokenisés. Dans AMOS, repartir d'un programme vide puis utiliser **Project → Merge ASCII** pour chaque fichier. Le menu `Load` classique ne convient pas. Pour `Fsel$("**")`, sélectionner `examples/demo.iff` depuis un volume visible par AmigaOS.

`demo.iff` est une mire originale 320×256, 8 bitplanes et 256 couleurs, également conservée dans `iff-TEST/`. Les neuf exemples disposent de contrôles statiques. **La démo de fondu R33 est confirmée visible et fonctionnelle sous WinUAE par l'utilisateur ; les autres exemples ne sont pas tous validés de bout en bout.** Les tests de régression R23 (souris/clavier/Ctrl+C) et R25 (collisions) ont, eux, été validés sous AMOS interprété/WinUAE ; cela ne valide pas automatiquement ces versions pédagogiques.

**Pourquoi charger un IFF pour `collide.asc` ?** `demo.iff` fournit le mode PAL et la palette (index 3 = bleu, 28 = vert, 224 = rouge). L'exemple efface tout le back buffer à chaque image : **les pixels de l'IFF ne sont pas affichés et ne participent pas aux collisions**. La fonction `Aga Rect Overlap` fonctionne sans IFF ni écran ; le fichier n'est utilisé ici que pour obtenir les bonnes couleurs.


**Démo R27 — `show.asc` :** l'IFF fournit uniquement le mode PAL et les couleurs indexées (0 = fond, 3 = bleu, 28 = vert, 224 = rouge). L'exemple **redessine tous les pixels avec l'extension AGA** : l'image IFF ne sert pas de décor. Au début de chaque image, `Aga Blit Clear` réessaie au maximum **12 fois**, avec un VBL entre les refus Safe ; `Aga Swap` utilise la même limite. La démo regroupe `Aga Text`, `Aga Blit Copy`, `Aga Rect Overlap` et les entrées souris/clavier. **Cet exemple n'a pas été testé séparément sous WinUAE et ne mesure pas les FPS.** Le [test R27 validé à 40 swaps](../tests/passed/M12_R27_SAFE_BLIT_01.asc) reste indépendant.

Les anciens essais restent classés dans [`tests/current/`](../tests/current/), [`tests/passed/`](../tests/passed/) et [`tests/historical/`](../tests/historical/). **Ils ne font pas partie du jeu d'exemples simplifié.**

**Licences :** sources des exemples sous [MIT](../LICENSE) ; graphismes des fontes sous conditions d’attribution [Hwarf](Amcaf%20Fonts/Hwarf-12xxS.licence) et [Pix3M](Amcaf%20Fonts/Pix3M-12xxL.licence). L'image **n'est pas sous MIT** : [notice graphique](../ASSETS_LICENSE.md), consultation/tests locaux autorisés, redistribution/réutilisation de l'illustration séparément soumise à autorisation.
