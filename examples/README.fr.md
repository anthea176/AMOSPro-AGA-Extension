# AMOSPro AGA — exemples et démonstrations

## Nouveau — Fast Icon Lab R67 : CPU, Blitter, capture et cache Chip

**[Fast Icon Lab — démo interactive](fast_icons_r67/README.fr.md)** · [Source AMOS ASCII](fast_icons_r67/FAST_ICON_LAB.asc) · [English](fast_icons_r67/README.md)

Une interface 320×256×256 couleurs générée **entièrement par AMOS** : cinq icônes 16×16 en quatre colonnes (**CPU transparent/opaque, Blitter transparent/opaque**), re-staging d'un cristal après modification et **capture directe depuis le back buffer à X=31**. Les pixels sont produits par `Poke` ; **aucun IFF, ABK, police ou fichier externe**. Sortie par touche/clic, nettoyage des banques.

**Requiert la bibliothèque candidate R67 v0.13.12** (Gates A/B de la fonction de capture validées, **Gate C Compiler encore en attente**). **Ce nouvel exemple public a été confirmé fonctionnel par l'auteur sous WinUAE en interprété le 13/11/2026, sans capture ni valeurs console fournies** : ne pas confondre avec les régressions R67 archivées. **Banques 11/12/13 libres** obligatoires ; `Reserve As Data 13,256` écrase la banque 13 si elle existait. Programme à importer par **Project → Merge ASCII** et à lancer **en interprété uniquement**.


## R54 v0.12.9 — exemple complémentaire validé

[Exemple R54 des fonctions par numéro de banque](bank_number_r54/) : `Aga Bank Image Draw(Bank,X,Y,Mode)` et `Aga Bank Font Select(Bank)` sont comparées aux anciennes commandes. **Essai utilisateur PASS en interprété et en compilé sous WinUAE (`RESULT 1`, `CLOSE RETURNED`)**. Le programme ASCII validé et les deux ressources ABK sont fournis dans le nouveau dossier versionné ; [original archivé](../tests/passed/M16_R54_BANK_NUMBER_01.asc) inchangé. Les onze exemples simples ci-dessous restent intacts.

[English](README.md) | **Français** · [Installation](../INSTALL.fr.md)

**État de la bibliothèque pour les exemples :** R67 v0.13.12 est l'unique **candidate** (Gates A/B PASS sur son scénario) ; R63 est la dernière **`LAST_GOOD` protégée**. Le programme R54 ci-dessous reste un exemple historique validé avec sa version. Aucune Gate C Compiler R67 n'est revendiquée. L'[exemple compilé R46 C1](compiler_r46_all_in_one/) reste une démonstration historique figée, utile pour la compatibilité.

Ces programmes sont des **démonstrations destinées aux utilisateurs**, et non les anciens tests de régression. La plupart utilisent la [`AMOSPro_AGA.Lib` courante](../dist/AMOSPro_AGA.Lib) en **AMOS Professional interprété** ; l'exemple tout-en-un compilé archivé utilisait la **R46 C1 historique**.

| Fichier | Démonstration | Utilisation |
|---|---|---|
| [`fast_icons_r67/FAST_ICON_LAB.asc`](fast_icons_r67/FAST_ICON_LAB.asc) | **Nouveau showcase M18/R67** : banques `FICON8`/`FICHIP8`, pixels chunky, `Bank Put`, re-staging, capture écran X non aligné et rendu CPU/Blitter dans quatre modes | **Sans ressource externe.** Installer R67, libérer 11/12/13, importer ASCII. Touche/clic pour quitter ; attendre `ERROR 0` et `RESULT 1`. **Fonctionnement confirmé par l'auteur sous WinUAE en interprété (sans capture).** |
| [`screen.asc`](screen.asc) | Ouvrir/fermer un écran 320×256×256 couleurs | Affiche un motif environ 3 secondes, sans image |
| [`picture.asc`](picture.asc) | Lire une image IFF, la charger, faire le Swap | Choisir [`demo.iff`](demo.iff), puis appuyer sur une touche |
| [`blitter.asc`](blitter.asc) | `Aga Blit Fill`, `Clear` et `Copy` | Choisir `demo.iff`, regarder les formes, appuyer sur une touche |
| [`copper.asc`](copper.asc) | Raster Copper RGB4 avec `Wait`/`Move` | Bandes horizontales rouge/vert/bleu/noir, puis une touche |
| [`mouse.asc`](mouse.asc) | Position, clics, lecture clavier | Cliquer gauche/droit, puis une touche ou attendre 5 secondes |
| [`collide.asc`](collide.asc) | R25 `Aga Rect Overlap`, souris, Blitter, double buffering et VBL | Choisir `demo.iff`, entrer/sortir du rectangle bleu (vert = libre, rouge = collision) ; clic gauche pour quitter ou 900 images maximum |
| [`show.asc`](show.asc) | **Démo animée R27 :** texte AGA natif, interface rétro, Blitter Fill/Clear/Copy sécurisés, rectangles animés et copiés, collision AABB et souris | Choisir `demo.iff`, observer les blocs verts/rouges et déplacer le curseur ; **clic gauche ou touche** pour quitter (arrêt automatique après 600 images au maximum) |
| [`fade_to_bank_r33.asc`](fade_to_bank_r33.asc) | **Démo visuelle R33 :** trois bandes colorées, rouge → vert → bleu → rouge, fondus de 150 VBL | Aucun IFF. **Écrase la banque AMOS 12** ; `Aga Swap` et `Amos To Back` sont exécutés **avant** les fondus. Pauses entre changements ; résultats après fermeture. **Démo testée par l'utilisateur sous WinUAE : fondu visible et fonctionnel (11/11/2026), sans mesure de FPS ni de durée réelle.** |
| [`font_bank_r38.asc`](font_bank_r38.asc) | **Démo BankFont AMCAF R38 :** afficher `Hwarf1252S.abk` et `Pix3M-1252L.abk` sur un même écran AGA 320×256 | Nécessite R38 v0.11.0 ; lancer depuis le répertoire `examples/` avec `Amcaf Fonts/` présent ; **remplace la banque AMOS 25** ; une touche pour quitter. |
| [`m15_2d_cursor.asc`](m15_2d_cursor.asc) | **Démo complète M15 + M15bis (R44) :** étoiles Plot, axes et réticule mobile Draw, cadres Box, radar et viseur Circle, puis affichage/masquage local du curseur avec `Aga Mouse Cursor` | **Sans IFF ni banque de fontes.** Déplacer la souris, **clic droit** pour afficher/masquer le pointeur, **clic gauche ou touche** pour quitter (600 images au maximum). R44 v0.11.5 nécessaire ; **démo validée par l'utilisateur sous WinUAE (12/11/2026).** |
| [`compiler_r46_all_in_one/COMPILER_R46_ALL_IN_ONE.asc`](compiler_r46_all_in_one/COMPILER_R46_ALL_IN_ONE.asc) | **Test Compiler R46 C1 tout-en-un :** images AGAPIC opaque/masquée, clipping, Plot/Draw/Box/Circle, double buffering, deux polices, 500 bascules du curseur et fermeture complète | **Un seul ASC et deux ABK fournis.** Conserver le dossier complet et compiler avec la R46 C1 officielle. Vérifier `RESULT 1` et `CLOSE RETURNED`. **PASS compilé sous WinUAE (12/11/2026) : `RESULT 1`, 0 erreur curseur, Chip drop 0.** |

**Test Compiler R46 tout-en-un :** [télécharger l'archive ZIP complète](COMPILER_R46_ALL_IN_ONE.zip), ou utiliser le [dossier autonome](compiler_r46_all_in_one/) et son [mode d'emploi](compiler_r46_all_in_one/README.md). Le programme ASC charge ses deux fichiers ABK inclus ; **le dossier doit être le répertoire courant AmigaDOS pendant l'exécution compilée**. Aucune modification de la bibliothèque officielle `LAST_GOOD`.

**Démo interactive M15 + M15bis — `m15_2d_cursor.asc` :** scène AGA autonome 320×256, palette 256 couleurs et double buffering sécurisé. Elle dessine 23 étoiles avec Plot, des axes et un réticule mobile avec Draw, des cadres Box, des anneaux de radar et le viseur avec Circle, et pilote le curseur local R44. Le pointeur système commence masqué : **clic droit** pour l'afficher/le masquer, **clic gauche ou touche** pour quitter, ou arrêt après 600 images. La fermeture restaure automatiquement le curseur. `Aga Blit Clear` et `Aga Swap` ont chacun 12 tentatives bornées en cas de refus Safe. De retour dans AMOS, succès : `ERROR 0`, `RESULT 1`, `CLOSE RETURNED`. **Nécessite R44 ; rendu et interaction confirmés par l'utilisateur sous WinUAE (12/11/2026), sans relevé chiffré joint.** Aucun IFF, ABK ou fichier externe.

**Démo de fontes R38 — `font_bank_r38.asc` :** charge successivement `Amcaf Fonts/Hwarf1252S.abk` et `Amcaf Fonts/Pix3M-1252L.abk` avec `Load "...",25`, puis `Aga Font Bank Select(Start(25),Length(25))` et `Aga Text`. Les deux ABK utilisent le numéro de banque 25, **écrasé par la démo**. `Erase 25` est sans danger après sélection réussie : R38 conserve une copie privée en Chip RAM. L’exemple restaure la fonte système avec `Aga Font Select("",0)` et ferme l’écran. Les chemins AmigaDOS utilisent `/` comme séparateur (contrairement aux chemins Windows avec `\\`) ; le répertoire AmigaDOS courant doit être `examples/`, par exemple en copiant ce dossier complet sur un volume Amiga. **L’extension AMCAF n’est pas nécessaire à l’exécution.** **La démo de fontes R38 fonctionne sous AMOS interprété/WinUAE (confirmation utilisateur du 12 novembre 2026).** Un [test distinct de 500 changements de fonte](../tests/passed/M14_R38_CHIP_RAM_STRESS_01.asc) a ensuite été validé sous WinUAE le 12/11/2026 sans baisse mesurée de Chip RAM libre.

**Attribution des fontes :** [Hwarf — licence/crédits](Amcaf%20Fonts/Hwarf-12xxS.licence) et [Pix3M — CC BY 3.0](Amcaf%20Fonts/Pix3M-12xxL.licence). Les graphismes des ABK ne relèvent pas de la licence MIT du code source.

Les `.asc` sont des **sources texte ASCII**, pas des programmes AMOS tokenisés. Dans AMOS, repartir d'un programme vide puis utiliser **Project → Merge ASCII** pour chaque fichier. Le menu `Load` classique ne convient pas. Pour `Fsel$("**")`, sélectionner `examples/demo.iff` depuis un volume visible par AmigaOS.

`demo.iff` est une mire originale 320×256, 8 bitplanes et 256 couleurs, également conservée dans `iff-TEST/`. Les dix exemples précédents disposent de contrôles statiques ; le nouveau programme intégré doit encore être testé sous WinUAE. **La démo de fondu R33 est confirmée visible et fonctionnelle sous WinUAE par l'utilisateur ; les autres exemples ne sont pas tous validés de bout en bout.** Les tests de régression R23 (souris/clavier/Ctrl+C) et R25 (collisions) ont, eux, été validés sous AMOS interprété/WinUAE ; cela ne valide pas automatiquement ces versions pédagogiques.

**Pourquoi charger un IFF pour `collide.asc` ?** `demo.iff` fournit le mode PAL et la palette (index 3 = bleu, 28 = vert, 224 = rouge). L'exemple efface tout le back buffer à chaque image : **les pixels de l'IFF ne sont pas affichés et ne participent pas aux collisions**. La fonction `Aga Rect Overlap` fonctionne sans IFF ni écran ; le fichier n'est utilisé ici que pour obtenir les bonnes couleurs.


**Démo R27 — `show.asc` :** l'IFF fournit uniquement le mode PAL et les couleurs indexées (0 = fond, 3 = bleu, 28 = vert, 224 = rouge). L'exemple **redessine tous les pixels avec l'extension AGA** : l'image IFF ne sert pas de décor. Au début de chaque image, `Aga Blit Clear` réessaie au maximum **12 fois**, avec un VBL entre les refus Safe ; `Aga Swap` utilise la même limite. La démo regroupe `Aga Text`, `Aga Blit Copy`, `Aga Rect Overlap` et les entrées souris/clavier. **Cet exemple n'a pas été testé séparément sous WinUAE et ne mesure pas les FPS.** Le [test R27 validé à 40 swaps](../tests/passed/M12_R27_SAFE_BLIT_01.asc) reste indépendant.

Les anciens essais restent classés dans [`tests/current/`](../tests/current/), [`tests/passed/`](../tests/passed/) et [`tests/historical/`](../tests/historical/). **Ils ne font pas partie du jeu d'exemples simplifié.**

**Licences :** sources des exemples sous [MIT](../LICENSE) ; graphismes des fontes sous conditions d’attribution [Hwarf](Amcaf%20Fonts/Hwarf-12xxS.licence) et [Pix3M](Amcaf%20Fonts/Pix3M-12xxL.licence). L'image **n'est pas sous MIT** : [notice graphique](../ASSETS_LICENSE.md), consultation/tests locaux autorisés, redistribution/réutilisation de l'illustration séparément soumise à autorisation.
