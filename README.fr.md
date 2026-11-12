# AMOSPro AGA Extension

[English](README.md) | **Français**


**AMOSPro AGA Extension** étend les capacités d'**AMOS Professional** sur Commodore Amiga AGA : gestion des écrans et des palettes, chargement IFF/ILBM, double buffering, primitives Blitter et Copper, clavier et souris.

Projet conçu et développé par **HWARF**, avec l'assistance de **ChatGPT (OpenAI)** pour la programmation, les tests et la documentation.

<img src="assets/Hwarf%20Logo.png" alt="Logo HWARF" width="160">

![Illustration de présentation AMOSPro AGA Extension](assets/banniere.png)

*Illustration générée avec ChatGPT : visuel de présentation, pas une capture de l'extension.*

**Licences distinctes :** le code et la documentation technique sont sous [MIT](LICENSE). **Les illustrations, logos, dessins et scans ne sont pas sous MIT** et ne sont pas librement réutilisables : lire la [licence des éléments graphiques](ASSETS_LICENSE.md).

**Pour commencer :** [Notice d'installation](INSTALL.fr.md) · [Exemples AMOS](examples/README.fr.md).

## Bibliothèques et tests

**Dernière version promue `LAST_GOOD` : R46 v0.12.1-C1** — **50 commandes AMOS**, **57 entrées AP20**, **29 964 octets**, SHA256 `d2d26884eca532f4ab78c7e6db665230d8d76ce8939b3a7a7b722e09e0b6037b`. [Bibliothèque à installer](dist/AMOSPro_AGA.Lib) · [Copie `LAST_GOOD` identique](dist/AMOSPro_AGA_LAST_GOOD.Lib) · [Archive C1 exacte](dist/experimental/AMOSPro_AGA_COMPILER_GATE_C_R46_MONOLITH_CANDIDATE.Lib). **Gates A CPU, B WinUAE interprété et C WinUAE compilé (test intégré) PASS** : `RESULT 1`, curseur 500/0, Chip drop 0. Gate C ne couvre pas les 50 commandes individuellement ; Gate D Amiga physique non testée.

**Images AGAPIC en Fast RAM :** les images compressées peuvent être conservées dans une banque DATA AMOS en **Fast RAM**. `Aga Image Draw` les lit et les décompresse au **CPU** directement vers le back buffer AGA en **Chip RAM**, sans décompression intégrale en Chip et sans Blitter pour lire la source. L'emplacement réel de la banque est choisi par AMOS ; celui de l'ABK de test n'a pas été mesuré. [Format AGAPIC](docs/M16_AGAPIC_FORMAT_DESIGN.md).

**Historique et preuves :** [chronologie](docs/LIBRARY_TEST_HISTORY.fr.md) · [rapport Compiler Gate C](docs/GATE_C_R46_MONOLITH_CANDIDATE.md) · [ASC tout-en-un validé](tests/passed/R46_C1_COMPILER_ALL_IN_ONE.asc) · [archive native R46 historique](dist/experimental/AMOSPro_AGA_M16_v0.12.1_IMAGE_DRAW_R46.Lib).

**Installation :** [INSTALL.fr.md](INSTALL.fr.md). Une mise à jour GitHub ne remplace pas automatiquement la bibliothèque installée sous AMOS/WinUAE.

## Commandes AMOS principales

**API de la bibliothèque courante R46 0.12.1** — **50 commandes AP20**. Les paramètres et comportements ci-dessous correspondent à la bibliothèque R46 validée sous AMOS interprété/WinUAE.

| Commande | Syntaxe exacte | Paramètres et comportement |
|---|---|---|
| `Aga Probe` | `Aga Probe` | Instruction historique sans paramètre, réservée au diagnostic ; pas une API de jeu recommandée. |
| `Aga Detect` | `_AGA=Aga Detect` | Sans argument ; résultat non nul si AGA est présent (ne pas supposer que TRUE vaut toujours `1`). |
| `Aga Demo` | `_D=Aga Demo` | Fonction historique sans paramètre, réservée au diagnostic ; pas de contrat de retour pour un jeu. |
| `Aga Screen Open` | `_OK=Aga Screen Open(largeur,hauteur,nbCouleurs,modeID)` | Dimensions en pixels ; **nombre de couleurs**, pas nombre de bitplanes (`2,4,8,16,32,64,128,256` en mode indexé) ; identifiant vidéo AmigaOS, par exemple `$00021000` en PAL LowRes. Retour `1`/`0`. |
| `Aga Screen Close` | `Aga Screen Close` | Sans argument ; ferme l'écran AGA et libère les ressources. |
| `Aga Screen Pattern` | `Aga Screen Pattern` | Sans argument ; dessine le motif de diagnostic. |
| `Aga Double Buffer` | `_DB=Aga Double Buffer` | Sans argument ; active les deux buffers. Retour `1`/`0`. |
| `Aga Swap` | `_SW=Aga Swap` | Sans argument ; présente le back buffer préparé. Retour `1`/`0`. |
| `Aga Back Fill` | `Aga Back Fill couleur` | Instruction à **un argument** : index couleur appliqué à **tout** le back buffer, par exemple `255` sur un écran indexé 8 plans. |
| `Aga Pic Info` | `_V=Aga Pic Info(fichier$,champ)` | Chemin ILBM puis numéro de champ `0..7` (voir tableau suivant) ; renvoie une valeur ou `-1` en cas d'erreur. |
| `Aga Iff Load` | `_OK=Aga Iff Load(fichier$)` | Chemin IFF/ILBM ; charge pixels et palette sur l'écran/buffer compatible. Retour `1`/`0`. |
| `Aga Palette Load` | `_OK=Aga Palette Load(_FILE$)` | Importe uniquement le `CMAP` d'un **IFF standard FORM ILBM**, y compris les palettes PPaint/DPaint sans `BODY` ni `BMHD` ; ne modifie aucun pixel. Retour 1 succès, 0 en cas de refus. |
| `Aga Palette Set` | `_OK=Aga Palette Set(_PEN,_R,_G,_B)` | Définit un index de palette du `ColorMap` Intuition AGA avec R/V/B sur 8 bits (`0..255`) via `LoadRGB32` ; retour 1 ou 0, sans attente VBL. Les modes HAM, EHB et dual playfield ne sont pas pris en charge. |
| `Aga Palette Get` | `_RGB=Aga Palette Get(_PEN)` | Lit le `ColorMap` par `GetRGB32`. Renvoie le RGB24 empaqueté `$00RRGGBB` ou -1 en cas d'erreur ; noir = 0. Aucun pixel modifié. |
| `Aga Palette Save` | `_OK=Aga Palette Save(_FILE$)` | Sauvegarde le `ColorMap` indexé de l'écran AGA Intuition en IFF `FORM ILBM` avec `BMHD` et `CMAP`, **sans BODY**. Chaîne AMOS de 1 à 255 octets (chemin AmigaDOS). **Écrase le fichier existant** via `MODE_NEWFILE`. Résultat entier 1 si écriture/fermeture réussies, 0 si écran/fichier/mémoire/écriture invalides. 1 à 256 couleurs RGB24, sans modifier les pixels ; HAM/EHB/dual playfield refusés. Un échec après ouverture peut détruire l'ancien fichier. |
| `Aga Palette Bank Init` | `_OK=Aga Palette Bank Init(Start(_B),_N)` | Initialise une **banque DATA AMOS existante de taille exacte**, à l'adresse donnée par `Start(_B)` (pas le numéro de banque). `_B` doit être une banque encore réservée 5–65535 ; `_N` vaut 1 à 256 palettes, taille **16+776×_N octets**. Écrit le nom natif `AGAPAL `, un en-tête interne de 16 octets, un index à entrées de 8 octets et 768 octets RGB24 par palette (initialement zéro, compte 0). Retour **1** réussite, **0** si nombre/type/taille ou zone mémoire rejetés ; une nouvelle initialisation efface les palettes existantes. Aucune allocation ni modification d'écran ; banque DATA en Fast RAM prioritaire, repli Chip par AMOS. **Transmettre exclusivement `Start(bank)` d'une banque DATA valide et non libérée : adresse arbitraire ou périmée potentiellement dangereuse.** sur sauvegarde/rechargement ABK 8 palettes. |
| `Aga Palette Bank Capture` | `_OK=Aga Palette Bank Capture(Start(_B),_INDEX)` | Capture la `ColorMap` RGB24 de l'écran AGA Intuition privé actif dans l'emplacement AGAPAL `_INDEX` (indice 0 à N-1). La banque DATA AMOS `_B` doit être vivante et initialisée auparavant par `Aga Palette Bank Init` ; transmettre exclusivement **`Start(_B)`**, jamais le numéro brut ni un pointeur périmé. Lit 1 à 256 couleurs par `GetRGB32`, enregistre trois octets par couleur, le nombre réel de couleurs et remet à zéro les octets inutilisés du **seul** emplacement de 768 octets sélectionné ; une nouvelle capture l'écrase. Aucun autre index, pixel ni couleur écran modifié. Retour entier **1** réussite, **0** rejet sans modification de banque. Rejette en-tête/taille/index invalides, écran absent/incompatible, échec d'allocation temporaire ; tampon libéré. Aucun VBL implicite, fade ou cycling. sur le scénario capture/ABK archivé. |
| `Aga Palette Bank Apply` | `_OK=Aga Palette Bank Apply(Start(_B),_INDEX)` | Applique une palette **non vide (1 à 256 couleurs)** de l'emplacement AGAPAL `_INDEX` (0..N-1) à la `ColorMap` de l'écran AGA Intuition privé actif via `LoadRGB32`, en RGB32, **immédiatement sans attente VBL**. Exige une banque DATA AMOS vivante via **`Start(_B)`**, un descripteur AGAPAL v1 valide et une capacité logique/ColorMap de l'écran suffisante : ne jamais transmettre un numéro brut ou une adresse périmée. Retour entier **1** réussite, **0** rejet sans changement d'écran. Seules les couleurs `0..compte-1` sont appliquées, les suivantes restent inchangées ; jamais de troncature ni d'écriture banque/bitmap. Palette vide, mode incompatible/écran fermé ou allocation temporaire impossible refusés. Tampon mémoire libéré. Aucun fondu ni cycling. |
| `Aga Fade To Bank` | `_OK=Aga Fade To Bank(Start(_B),_INDEX,_VBL)` | Fondu **RGB24 bloquant** de la palette courante de l'écran AGA Intuition privé indexé vers la palette non vide AGAPAL `_INDEX` d'une banque DATA AMOS vivante (**véritable `Start(_B)`**, jamais un numéro brut/pointeur périmé). Durée entière **`_VBL` de 1 à 255**, 0 ou valeur invalide = refus 0 sans changement ; utiliser Aga Palette Bank Apply pour une application immédiate. Pour chaque étape, un `graphics.library/WaitTOF`, interpolation linéaire à pas fixe et un `LoadRGB32` ; **dernière image RGB24 cible exacte**. Seuls les pens `0..compte-1` changent, les suivants et la banque/bitmaps restent intacts. Contrôles et allocation avant tout VBL ; tampon Exec public temporaire (max 10 760 octets) libéré. Retour entier **1** succès, **0** rejet. À 256 couleurs sur 68000 lent, la durée réelle peut excéder `_VBL` périodes de rafraîchissement. |
| `Aga Fade To Black` | `_OK=Aga Fade To Black(_VBL)` | Fondu **RGB24 bloquant vers le noir exact, sans banque AGAPAL**, de tous les pens logiques de l'écran AGA Intuition privé indexé (1–256 couleurs, 1–8 bitplanes ; HAM/EHB/dual playfield refusés). Durée entière `_VBL` **de 1 à 255**, retour entier **0 sans changement** si 0, négative, >255 ou écran invalide. Capture initiale `GetRGB32` si durée >1 ; interpolation signée 8.8 par composante ; à chaque étape, `graphics.library/WaitTOF` puis `LoadRGB32` ; **dernière image RGB32 exactement nulle**. Aucun pixel, fichier, banque ni pen supérieur modifié. Tampon Exec public temporaire `8+42*N` (max 10 760 octets) libéré en sortie. Retour **1** succès. Sur 68000 lent, durée réelle supérieure possible. |
| `Aga Fade To White` | `_OK=Aga Fade To White(_VBL)` | Fondu **RGB24 bloquant vers le blanc exact**, sans banque AGAPAL, sur tous les pens logiques de l'écran AGA Intuition privé indexé (1–256 couleurs, 1–8 bitplanes ; HAM/EHB/dual playfield refusés). Durée entière `_VBL` **1..255**, retour **0 sans changement** si 0, négatif, >255 ou écran invalide. Capture initiale `GetRGB32` si durée >1, interpolation linéaire 8.8 signée positive par composante, chaque étape fait `graphics.library/WaitTOF` puis `LoadRGB32` ; **dernière image exactement `0xFFFFFFFF`** sur toutes les composantes RGB32 (blanc 255,255,255). Aucun argument banque, aucune écriture pixel/fichier, ni modification des pens supérieurs. Scratch Exec public `8+42*N` octets (max 10 760), libéré ; retour **1** succès. Durée réelle susceptible de dépasser les périodes VBL sur 68000 lent. |
| `Aga Palette Cycle` | `_OK=Aga Palette Cycle(First,Last,Direction)` | **Une rotation par appel** des indices inclus `0<=First<Last<256` dans les pens logiques de l'écran AGA privé indexé et de sa ColorMap. `Direction=1` : dernière couleur RGB32 vers First, autres couleurs vers les indices croissants ; `-1` : sens inverse. Un seul `GetRGB32`, permutation de triplets **RGB32 complets** en mémoire temporaire, puis **un seul `LoadRGB32`** sur cette plage ; **aucun WaitTOF implicite**, aucune banque, aucun pixel ni dégradation des couleurs. Scratch Exec public `8+12*N` octets (max 3 080), libéré. Retour **1** succès, **0 sans modification** si indices, sens, écran, ColorMap ou allocation invalides. AMOS pilote la cadence avec `Aga Wait Vbl`. |
| `Aga Key` | `_K=Aga Key` | Sans argument ; lecture non bloquante. Conserve les touches RAWKEY dans une FIFO de 16 éléments avec le dispatcher IDCMP, sans les perdre lors d'une lecture souris. |
| `Aga Wait Key` | `_K=Aga Wait Key` | Sans argument ; attend une touche de la fenêtre Intuition et renvoie un **code clavier**, pas forcément un ASCII. Utilise le même dispatcher/FIFO ; Ctrl+C vérifié sous WinUAE : arrêt à `_WAITK=Aga Wait Key` et fermeture correcte de l'écran Intuition. |
| `Aga Wait Vbl` | `Aga Wait Vbl` | Sans argument ; attend une VBL (`WaitTOF`) ; ne fait rien si aucun écran n'est ouvert. |
| `Aga Blit Copy` | `_OK=Aga Blit Copy(sourceX,sourceY,destX,destY,largeur,hauteur)` | Copie un rectangle dans le **même back buffer**. Contrôle automatiquement `Safe` avant toute écriture DMA ; retour **0 sans copier** si l'ancien buffer affiché n'est pas encore réutilisable (ou paramètres/état invalides), **1** en cas de succès. Un `GetMsg` non bloquant, sans `ReplyMsg`. |
| `Aga Blit Fill` | `_OK=Aga Blit Fill(x,y,largeur,hauteur,indexCouleur)` | Remplit le rectangle dans le back buffer avec l'index couleur en cinquième argument. Même contrôle `Safe` non bloquant avant le premier DMA ; retour **0 sans dessin** si non prêt ou invalide. |
| `Aga Blit Clear` | `_OK=Aga Blit Clear(x,y,largeur,hauteur)` | Remet un rectangle à l'index palette **0** (pas forcément au noir RGB). Hérite du contrôle `Safe` de Fill via son wrapper natif ; retour **0 sans effacement** si buffer non-Safe ou paramètres invalides. |
| **`Aga Copper Clear`** | `_OK=Aga Copper Clear` | Sans argument ; prépare une liste Copper vide, terminée, associée à l'écran AGA privé. Retour `1`/`0`. |
| **`Aga Copper Wait`** | `_OK=Aga Copper Wait(v,h)` | **1 : `v`** = ligne verticale (`0..255`) ; **2 : `h`** = position horizontale (`0..222`). Les WAIT successifs doivent être strictement croissants. Retour `1`/`0`. |
| **`Aga Copper Move`** | `_OK=Aga Copper Move(registre,rgb4)` | **1 : `registre`** = offset matériel couleur pair `$180..$1BE` (`COLOR00..COLOR31`) ; **2 : `rgb4`** = valeur **RGB sur 12 bits**, `$000..$FFF` (ex. `$F00` = rouge). Ce n'est **pas** un index de palette. Retour `1`/`0`. |
| **`Aga Copper End`** | `_OK=Aga Copper End` | Sans argument ; finalise une liste non vide. Un deuxième appel ou un ajout après `End` est refusé. Retour `1`/`0`. |
| **`Aga Copper On`** | `_OK=Aga Copper On` | Sans argument ; applique la liste à l'écran via Intuition. Une liste non vide doit avoir reçu `End`. Retour `1`/`0`. |
| **`Aga Copper Off`** | `_OK=Aga Copper Off` | Sans argument ; retire la liste, restaure l'affichage et libère les ressources appartenant à l'extension. Appel répété accepté. Retour `1`/`0`. |
| **`Aga Mouse X`** | `_MX=Aga Mouse X` | Sans argument ; position **horizontale** en pixels logiques de l'écran de l'extension (`0..largeur-1`), ou **`-1`** si hors écran / fermé. Non bloquant. |
| **`Aga Mouse Y`** | `_MY=Aga Mouse Y` | Sans argument ; position **verticale** en pixels logiques (`0..hauteur-1`), ou **`-1`** si hors écran / fermé. Non bloquant. |
| **`Aga Mouse Buttons`** | `_B=Aga Mouse Buttons` | Sans argument ; **masque entier `0..7`** : `1`=gauche, `2`=droit, `4`=central, bits cumulables (`3`=gauche+droit), `0`=aucun ; **`-1`** si écran/fenêtre invalide ou `input.device` indisponible. Lecture instantanée non bloquante. |
| **`Aga Mouse Pressed`** | `_P=Aga Mouse Pressed` | Fonction entière sans paramètre ; masque `1` gauche, `2` droit, `4` central, cumulable. **Événements IDCMP_MOUSEBUTTONS mémorisés** entre les lectures ; `0` si aucun, `-1` si écran/focus invalide. Chaque appel consomme les appuis observés, même si le bouton a été relâché avant l'appel. |
| **`Aga Mouse Released`** | `_R=Aga Mouse Released` | Fonction entière sans paramètre ; masque `1/2/4`, cumulable. **Relâchements IDCMP mémorisés** jusqu'à lecture, indépendamment de `Pressed`. Même un clic complet entre deux lectures peut fournir `Pressed=Released=1`. |
| **`Aga Hotspot Hit`** | `_HIT=Aga Hotspot Hit(_PX,_PY,_X,_Y,_W,_H)` | **Teste si un point est dans une zone rectangulaire (6 entiers)** : `PX,PY` = point testé (ex. souris) ; `X,Y` = **coin supérieur gauche** ; `W,H` = **largeur et hauteur en pixels, PAS les coordonnées du coin opposé**. Retour **1 dedans**, **0 dehors** ; bords droit/bas exclus. **Ne détecte pas le clic** et ne dessine ni n'enregistre la zone ; utiliser `Aga Mouse Pressed` pour un bouton. [Exemple détaillé](#hotspots--zones-rectangulaires-m9-r24). |
| **`Aga Rect Overlap`** | `_C=Aga Rect Overlap(_AX,_AY,_AW,_AH,_BX,_BY,_BW,_BH)` | **Fonction entière à 8 paramètres** : origine X/Y et largeur/hauteur W/H des rectangles A et B en pixels logiques. Retour **1** si leurs surfaces se recouvrent, même sur un pixel ; **0** si rectangles séparés, contact bord/coin ou dimensions nulles/négatives. Origines négatives autorisées, calcul signé 32 bits protégé. Sans état graphique, souris ou physique. |
| **`Aga Text`** | `_OK=Aga Text(_X,_BASELINE_Y,_PEN,_TEXT$)` | Quatre paramètres : X en pixels, Y de la ligne de base, index couleur, chaîne AMOS (1 à 128 caractères). Rend une ligne sur le back buffer AGA Intuition avec RastPort temporaire, fonte système, fonte AmigaOS ou BankFont AMCAF, et fond `JAM1` transparent. Retour 1 si dessin, 0 si état/géométrie/chaîne invalides ou buffer non-`Safe`. [Contrat R26](docs/M11_TEXT_R26.md) · [contrat R27](docs/M12_SAFE_BLITTER_R27.md). |
| **`Aga Font Select`** | `_OK=Aga Font Select(_FONT$,_YSIZE)` | Charge et sélectionne une fonte AmigaOS `.font` via `diskfont.library` (nom 1..127 caractères, hauteur demandée 1..255). Retour 1 si succès, 0 si refus sans effet. `_OK=Aga Font Select("",0)` restaure la fonte par défaut. Influence `Aga Text` sur l'écran AGA privé ; libération au remplacement/reset/Screen Close. |
| **`Aga Font Bank Select`** | `_OK=Aga Font Bank Select(_START,_LENGTH)` | Sélectionne une fonte monochrome fixe ou proportionnelle provenant d'une banque `BankFont` créée par AMCAF `Make Bank Font`. `_START=Start(n)` et `_LENGTH=Length(n)` désignent la banque AMOS vivante. Retourne 1 en cas de succès, 0 en cas d'échec sans changer la fonte. Copie privée en mémoire Chip (même si la banque source est en Fast) ; fonctionne après `Erase n`, libération au changement/reset/fermeture. |
| **`Aga Plot`** | `_OK=Aga Plot(X,Y,Pen)` | Écrit **un pixel** à `(X,Y)` dans le **back buffer AGA**. X/Y entre zéro et largeur/hauteur moins un, `Pen` indexé 0..2^Depth−1 (1 à 8 plans). `1` si `WritePixel` réussit, `0` sinon (paramètre invalide, écran absent ou buffer non-`Safe`). Pas de clipping hors écran, aucun swap/VBL implicite. |
| **`Aga Draw`** | `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)` | Trace une **ligne d'un pixel** sur le **back buffer AGA**, extrémités incluses. Tracé rapide pour les coordonnées entièrement dans l'écran ; **clipping logiciel sécurisé** par Bresenham en dehors. Coordonnées signées 16 bits, `Pen` indexé selon la profondeur. `1` si au moins un pixel dessiné, `0` sinon. Pas de swap/VBL implicite. |
| **`Aga Box`** | `_OK=Aga Box(X1,Y1,X2,Y2,Pen)` | Dessine **le contour d'un rectangle** de 1 pixel d'épaisseur sur le **back buffer AGA**. Coordonnées des **deux coins inclusives**, dans n'importe quel ordre (pas largeur/hauteur). **Clipping sûr des quatre côtés originaux** sans ajouter de fausse bordure. Coordonnées signées 16 bits, `Pen` couleur indexée ; `1` si au moins un pixel dessiné, sinon `0`. Pas de swap/VBL implicite, pas de remplissage. |
| **`Aga Circle`** | `_OK=Aga Circle(CX,CY,Radius,Pen)` | Trace **un cercle de contour d'un pixel** centré sur `CX,CY` signés 16 bits, avec `Radius` entier 0..32767 et `Pen` indexé (0..2^Depth-1). Un rayon 0 trace un seul pixel ; rayon négatif/hors plage ou paramètres invalides retournent `0`. Symétrie entière à huit octants et `WritePixel` borné, sans bordure artificielle. Seulement sur le back buffer privé `Safe` ; pas de remplissage ni swap/VBL implicite. Retour `1` si au moins un pixel écrit, sinon `0`. |
| **`Aga Mouse Cursor`** | `_OK=Aga Mouse Cursor(Visible)` | Fonction entière : **`Visible=0` masque** le curseur uniquement dans la fenêtre Intuition de l'écran AGA privé ; **`Visible=1` restaure** le curseur normal. `1` si l'action est acceptée, même répétée, `0` si paramètre différent de 0/1, écran absent ou allocation impossible. La souris, les clics et le clavier restent actifs ; Workbench et autres fenêtres ne sont pas modifiés. 72 octets Chip alloués une seule fois au premier masquage ; `ClearPointer` avant `CloseWindow`, puis `FreeMem` et remise à zéro, y compris Ctrl+C. Aucun Swap/VBL implicite. |
| **`Aga Image Draw`** | `_OK=Aga Image Draw(Start(_B),Length(_B),_X,_Y,_MODE)` | Affiche une image compressée **AGAPIC v1 stockée en banque DATA AMOS, y compris en Fast RAM**. Le **CPU** lit et décompresse la banque source directement dans le **back buffer AGA en Chip RAM** : pas de décompression intégrale en Chip et pas de lecture Fast par le Blitter. Profondeur **1 à 8 plans**, `_MODE=0` opaque (index couleur 0 visible), `_MODE=1` avec masque de transparence indépendant ; X non aligné, clipping des quatre côtés, contrôle `Safe` non bloquant et validation RLE avant écriture. Retour **1** pour un appel valide (même si l'image est totalement hors écran), **0** pour paramètre, banque ou données invalides sans modifier le bitmap. Utiliser les valeurs actuelles `Start(_B)` et `Length(_B)` d'une banque vivante ; AMOS décide si elle réside effectivement en Fast ou Chip RAM. |

**Exemple : masquer puis réafficher le curseur sur notre écran AGA** (après ouverture de l'écran privé) :

```amos
_HIDE=Aga Mouse Cursor(0)
If _HIDE=1
   _MX=Aga Mouse X
   _SHOW=Aga Mouse Cursor(1)
End If
```

**Exemple de cercle AGA** (après ouverture de l'écran et activation du double buffering) :

```amos
_OK=Aga Circle(160,128,48,3)
If _OK=1
   _SW=Aga Swap
End If
```

**Exemple AMOS : sauvegarder la palette active** une fois l'écran AGA Intuition ouvert :

```amos
_OK=Aga Palette Save("RAM:MENU_PALETTE.IFF")
If _OK=0
   Print "ERREUR SAUVEGARDE PALETTE"
End If
```

Le [test R29 archivé](tests/passed/M13_R29_PALETTE_SAVE_01.asc) sauvegarde, remplace puis recharge la palette sans pixel. Import de la palette 256 couleurs validé dans Personal Paint ; Deluxe Paint reste non testé ; [contrat R29](docs/M13_PALETTE_R29.md).

**Initialiser une banque AGAPAL native sous R30** (avec une banque DATA AMOS valide) :

```amos
Reserve As Data 10,6224
_OK=Aga Palette Bank Init(Start(10),8)
If _OK=1
   Save "RAM:MENU_PALETTES.ABK",10
End If
```

Le fichier ABK est enregistré avec la commande **`Save` native AMOS**, pas avec `Aga Palette Save` qui génère un IFF. Les huit emplacements RGB24 sont vides jusqu'aux futures fonctions de capture/import, à discuter séparément. [Test WinUAE R30](tests/passed/M13_R30_AGAPAL_BANK_INIT_01.asc). Aucune couleur écran modifiée.

**R31 : capturer la palette de l'écran indexé actif dans l'emplacement AGAPAL 0** (après `Aga Screen Open` et l'initialisation R30 de la banque) :

```amos
_CAPTURE=Aga Palette Bank Capture(Start(10),0)
If _CAPTURE=1
   Save "RAM:MENU_PALETTES.ABK",10
End If
```

Le fichier ABK natif contient la palette RGB24 de l'écran, pas une image IFF ; la capture **n'applique aucune palette à l'écran**. [Test R31 WinUAE validé](tests/passed/M13_R31_AGAPAL_CAPTURE_01.asc).

**R32 : appliquer la palette AGAPAL n°1 à l'écran actif** (après ouverture, initialisation et capture) :

```amos
_OK=Aga Palette Bank Apply(Start(10),1)
If _OK=1
   Print "Palette appliquee"
End If
```

Application immédiate : pour synchroniser une animation, appeler explicitement `Aga Wait Vbl`. [Test WinUAE R32](tests/passed/M13_R32_AGAPAL_APPLY_01.asc).

**R33 : fondu progressif vers une palette AGAPAL sauvegardée** (écran indexé et banque initialisés) :

```amos
_FADE=Aga Fade To Bank(Start(10),1,25)
If _FADE=1
   Print "Fondu termine"
End If
```

La commande attend 25 VBL avec application de couleurs à chaque étape. Une durée nulle est rejetée : utiliser `Aga Palette Bank Apply` pour changer immédiatement de palette. Avec 256 couleurs sur un 68000 lent, le calcul peut dépasser la période d'une image. [Contrat R33](docs/M13_AGAPAL_FADE_R33.md) · [Test fonctionnel R33 archivé](tests/passed/M13_R33_AGAPAL_FADE_01.asc). Pour voir le fondu, utiliser la [démo de trois bandes sur 150 VBL](examples/fade_to_bank_r33.asc) (écrase la banque 12 ; fondu visuel confirmé sous WinUAE).

**Copper RGB4** est disponible depuis R18, **Mouse X/Y** depuis R19, **Mouse Buttons** depuis R20 et RMBTRAP depuis R21. **R22 a ajouté `Aga Mouse Pressed/Released` (PASS WinUAE) ; R23 change leur source vers IDCMP_MOUSEBUTTONS, avec Gate A CPU/CI PASS et Gate B WinUAE PASS sur son scénario.** Capture garantie des clics très courts, sprites et `Aga Set Colour` restent hors de ce périmètre.

### Blitters Safe (M12 R27 — CPU/CI et scénario WinUAE PASS)

Les trois fonctions existantes `Aga Blit Clear`, `Aga Blit Fill` et `Aga Blit Copy` vérifient désormais chacune le signal `Safe`. Le retour `0` peut signifier un buffer non-Safe **ou** une autre erreur ; toute tentative de reprise doit être bornée et entrecoupée de VBL. [Test WinUAE archivé : 40 swaps sans sonde `Aga Text`](tests/passed/M12_R27_SAFE_BLIT_01.asc). L'ancienne instruction `Aga Back Fill` n'est **pas** couverte par cette protection. [Contrat technique](docs/M12_SAFE_BLITTER_R27.md).

### Texte AGA (M11 R26 — validée sous WinUAE sur son scénario graphique)

Après ouverture de l'écran AGA et du double buffering, `Aga Text` dessine dans le **BitMap arrière de l'extension** et non dans un écran AMOS natif. Y=96 est la **ligne de base** de la fonte ; l'index couleur 28 doit avoir été défini (par exemple via `examples/demo.iff`) :

```amos
_TX=Aga Text(40,96,28,"BONJOUR AGA")
If _TX=1
   _SW=Aga Swap
End If
```

Le résultat 0 peut indiquer que l'ancien buffer frontal n'a pas encore été déclaré `Safe`. Ne pas boucler indéfiniment ; la protection R26 ne sécurise pas rétroactivement les anciennes commandes Blitter. [Test WinUAE](tests/passed/M11_R26_AGA_TEXT_01.asc) · [contrat technique](docs/M11_TEXT_R26.md).

### Hotspots : zones rectangulaires (M9 R24)

`Aga Hotspot Hit(PX,PY,X,Y,W,H)` vérifie **si un point est situé dans un rectangle**. Ce n'est pas un test de collision entre deux rectangles. La fonction renvoie un **entier** (à affecter à une variable), pas un identifiant de bouton. Les deux premiers paramètres décrivent le **point**, les quatre suivants le rectangle.

| Paramètre | Signification | Exemple |
|---|---|---|
| `PX`, `PY` | Coordonnées X/Y du point testé (par exemple `Aga Mouse X/Y`) | `60,50` |
| `X`, `Y` | Coordonnées X/Y du **coin supérieur gauche** de la zone | `40,30` |
| `W`, `H` | **Largeur et hauteur** de la zone, pas le coin opposé | `80,40` |
| Résultat (`_HIT`) | `1` = dedans ; `0` = dehors ou paramètres invalides | `1` |

Pour le rectangle `(X=40,Y=30,W=80,H=40)`, les pixels compris dans la zone vont de **X=40 à 119** et de **Y=30 à 69**. À X=120 ou Y=70, le point est **dehors** : les bords droit et bas sont exclus. Les bords gauche et haut sont inclus.

```amos
_DEDANS=Aga Hotspot Hit(60,50,40,30,80,40)
_DEHORS=Aga Hotspot Hit(120,50,40,30,80,40)
' _DEDANS=1, _DEHORS=0
```

**Exemple : activer un bouton de menu seulement si l'on clique gauche à l'intérieur du rectangle** (avec un écran AGA déjà ouvert) :

```amos
_SELECTED=0
_PX=Aga Mouse X
_PY=Aga Mouse Y
_HIT=Aga Hotspot Hit(_PX,_PY,40,30,80,40)
_P=Aga Mouse Pressed
If _P>=0
   _LEFT=_P And 1
   If _LEFT<>0 and _HIT=1
      _SELECTED=10
   End If
End If
```

Ici, `10` est un **identifiant choisi par le programme**, pas une valeur fournie par `Aga Hotspot Hit`. Pour plusieurs zones qui se recouvrent, tester chaque rectangle et attribuer l'ID dans l'ordre de priorité voulu : **la dernière affectation correspondante gagne**, comme dans le [test R24 validé](tests/passed/M9_R24_HOTSPOT_HIT_01.asc).

**Limites :** `PX/PY` négatifs (dont la valeur `-1` renvoyée par `Aga Mouse X/Y`) et `W/H` nuls ou négatifs donnent 0. Les origines `X/Y` des rectangles peuvent être négatives. `Aga Hotspot Hit` ne lit pas la souris, ne consomme aucun événement, ne dessine pas la zone et fonctionne même sans écran AGA ouvert. Le clic se détecte séparément avec `Aga Mouse Pressed` ; les coordonnées de `Aga Mouse X/Y` sont celles **mesurées au moment de la lecture**, pas celles mémorisées à l'instant exact du clic. Voir le [contrat technique](docs/M9_HOTSPOT_R24.md).

### Détail : Souris AGA (R19–R23)

Les cinq fonctions `Aga Mouse X/Y/Buttons/Pressed/Released` sont **des fonctions entières sans argument**, à utiliser dans une affectation ou une expression. Sous AMOS, **ne pas écrire une fonction entière seule sur une ligne**.

```amos
_X=Aga Mouse X
_Y=Aga Mouse Y
_B=Aga Mouse Buttons
_P=Aga Mouse Pressed
_R=Aga Mouse Released

If _X>=0 and _Y>=0 and _B>=0
   _GAUCHE=_B And 1
   _DROIT=_B And 2
End If
```

- **Coordonnées X/Y :** origine `(0,0)` en haut à gauche, X dans `0..largeur-1`, Y dans `0..hauteur-1`. `-1` si fenêtre fermée, invalide ou coordonnée hors limites. Vérifier **les deux** coordonnées.
- **Boutons :** `0`=aucun ; `1`=gauche ; `2`=droit ; `4`=central ; valeurs combinables (par exemple `3`=gauche+droit). `-1` signifie que la lecture n'est pas possible (écran/fenêtre ou périphérique invalide). Vérifier `_B>=0` **avant** les opérations binaires.
- **R21 et clic droit :** `Aga Screen Open` active `WFLG_RMBTRAP`. Le clic droit ne déclenche plus les menus Intuition de la fenêtre AGA ; ce comportement a été validé sous WinUAE.
- **Nature de la lecture :** non bloquante ; `Aga Mouse Buttons` interroge un **instantané global** de `input.device/PeekQualifier()`, sans vider les événements clavier. Ne pas le confondre avec une file de clics propre à la fenêtre ; les appuis trop brefs entre deux lectures peuvent être manqués.
- **Transitions R23 :** `Aga Mouse Pressed` et `Aga Mouse Released` dépilent via un dispatcher central les événements `IDCMP_MOUSEBUTTONS` et mémorisent séparément les appuis/relâchements. Un clic DOWN+UP déjà reçu avant la lecture déclenche les deux masques. Chaque fonction efface uniquement son propre masque. Une FIFO de 16 événements clavier `RAWKEY` préserve `Aga Key` et `Aga Wait Key` ; si elle est pleine, le dispatcher arrête temporairement de dépiler les messages. **Deux clics identiques dans le même intervalle restent fusionnés dans le masque** (ce n'est pas un compteur). Préflight CPU et CI complète PASS (15 cas R23) ; Ctrl+C testé sous WinUAE (interruption propre et écran Intuition fermé) ; tests de focus et de stress encore à réaliser.

**Ancien calcul de fronts R21 côté AMOS**, conservé comme alternative :

```amos
_OLD=Aga Mouse Buttons
_NOW=Aga Mouse Buttons
If _OLD>=0 and _NOW>=0
   _PRESSED=_NOW And (7-_OLD)
   _RELEASED=_OLD And (7-_NOW)
End If
```

**R23 validée sur son scénario WinUAE :** [test exact archivé](tests/passed/M8_R23_IDCMP_QUICK_01.asc) sur la mire originale 320×256×8. Gate A CPU/CI PASS 15 cas (CI (archive CI privée, run #42899343161)), Gate B PASS : `RESULT=1`, `PRESSED=RELEASED=3`, `KEYS=64/64/-1`, `WAIT=16` (touche A AZERTY). **Ctrl+C** interrompt le programme à `_WAITK=Aga Wait Key` et ferme correctement l'écran Intuition (validation utilisateur).

### Détail : Copper AGA (R16–R18)

**Toutes les commandes `Aga Copper` ci-dessus sont des fonctions entières.** Toujours utiliser le résultat dans une affectation ou une expression : `_OK=Aga Copper Off` est valide, mais **`Aga Copper Off` seul provoque une erreur de syntaxe AMOS**, y compris dans une branche `If` jamais exécutée. **Retour `1` = succès, `0` = refus/échec.**

| Fonction | Paramètre 1 | Paramètre 2 | Remarques |
|---|---|---|---|
| `Clear` | — | — | Initialise la liste de l'écran AGA ; à exécuter avant les ajouts. |
| `Wait(v,h)` | `v` : ligne `0..255` | `h` : position `0..222` | Positions croissantes ; les positions invalides ou les retours en arrière donnent `0`. |
| `Move(registre,rgb4)` | `registre` : `$180` à `$1BE`, **pair** | `rgb4` : `$000` à `$FFF` | `$180` = `COLOR00`, `$182` = `COLOR01`… `$1BE` = `COLOR31`. Pas d'accès à DMA, BPLCON ou aux pointeurs bitplanes. |
| `End` | — | — | Scelle la liste non vide ; aucun nouvel ajout après. |
| `On` | — | — | Active la liste terminée ; toute modification après activation est refusée. |
| `Off` | — | — | Détache puis libère la liste de l'extension ; un second `Off` est accepté. |

Les valeurs de `Move` sont du **RGB4** : `$F00` = rouge, `$0F0` = vert, `$00F` = bleu, `$000` = noir. Contrairement à `Aga Blit Fill`, le second argument de `Move` n'est **pas** un numéro d'index couleur. Exemple : `Aga Copper Move($180,$F00)` modifie la valeur de **COLOR00** au moment du balayage défini par le dernier `Wait`.

**Séquence d'exemple**, à placer après un `Aga Screen Open` réussi, `Aga Double Buffer` et éventuellement un `Aga Iff Load` compatible. Elle reprend les appels validés dans le [test R18 complet](tests/passed/M7_R18_COPPER_RASTER_01.asc) :

```amos
_C=Aga Copper Clear
_W1=Aga Copper Wait(20,0)
_M1=Aga Copper Move($180,$F00)
_W2=Aga Copper Wait(80,0)
_M2=Aga Copper Move($180,$0F0)
_W3=Aga Copper Wait(140,0)
_M3=Aga Copper Move($180,$00F)
_W4=Aga Copper Wait(200,0)
_M4=Aga Copper Move($180,$000)
_E=Aga Copper End
_ON=Aga Copper On
_SW=Aga Swap
_K=Aga Wait Key
_OFF=Aga Copper Off
```

**Ordre à respecter :** `Clear` → couples `Wait`/`Move` → `End` → `On` → affichage/attente → `Off` → `Aga Screen Close`. Avec `COLOR00`, les bandes sont surtout visibles là où l'image utilise l'index de couleur 0 ; les pixels utilisant cet index dans l'image peuvent également changer de couleur. Le premier exemple RGB4 est limité à **62 instructions utiles + CEND**, avec capacité réservée, sans reprogrammation libre des registres AGA.

**Validation :** les tests R16, R17 et R18 ont passé AMOS interprété/WinUAE pour leurs scénarios ; le [test R18](tests/passed/M7_R18_COPPER_RASTER_01.asc) montre le raster, les rejets, `Off`, la réouverture et la fermeture. Cela **ne valide pas** le Compiler AMOS, le matériel réel, une exécution prolongée ni la palette AGA 24 bits complète. Détails : [M7 Copper R18](docs/M7_COPPER_R18.md) et [statut M7](docs/M7_STATUS.md).

### Détail : `Aga Blit Fill`, `Aga Blit Copy` et `Aga Blit Clear`

Ces trois fonctions réclament un écran ouvert via `Aga Screen Open`, puis un `Aga Double Buffer` réussi. Elles agissent **uniquement sur le back buffer** ; appeler `Aga Swap` pour rendre le dessin visible.

```amos
_OK=Aga Blit Fill(18,24,86,48,15)
```

| Argument | Nom | Valeur dans l'exemple |
|---:|---|---|
| 1 | `x` | `18` : coordonnée horizontale de départ |
| 2 | `y` | `24` : coordonnée verticale de départ |
| 3 | `largeur` | `86` pixels |
| 4 | `hauteur` | `48` pixels |
| 5 | `indexCouleur` | `15` : **numéro d'entrée dans la palette** |

Ce rectangle couvre `x=18..103` et `y=24..71` inclus : **ce n'est pas `x1,y1,x2,y2,couleur`**. L'index de couleur **n'est pas un RGB** : en mode indexé 4 plans, plage `0..15` ; en mode indexé 8 plans, plage `0..255` ; plus généralement `0..(2^profondeur-1)`. Les modes spéciaux HAM/EHB ne se manipulent pas comme une palette RGB indexée ordinaire.

```amos
_OK=Aga Blit Copy(18,24,150,24,86,48)
_OK=Aga Blit Clear(32,40,36,16)
```

- `Copy` : source `(18,24)`, destination `(150,24)`, dimensions `86 x 48`. `graphics.library/BltBitMap` gère les chevauchements.
- `Clear` : rectangle `(32,40)` de `36 x 16` pixels, mis à l'index `0`. C'est l'équivalent de `Aga Blit Fill(32,40,36,16,0)`.
- **Pas de clipping** : coordonnées négatives, dimensions nulles/négatives, rectangle dépassant les limites de l'écran ou couleur hors plage => retour `0` ; retour `1` en cas de succès.
- Les blits sont synchronisés avec `WaitBlit`. Si un appel système échoue après qu'un plan a été modifié, `0` ne garantit pas une opération atomique.
- `Aga Back Fill couleur` remplit **tout** le back buffer ; `Aga Blit Fill(...)` ne remplit qu'un rectangle.

### Séquence d'utilisation

Après vérification des retours de `Aga Screen Open` et `Aga Double Buffer`, charger éventuellement une IFF compatible avec `Aga Iff Load`, lancer les opérations Blitter, puis `Aga Swap`. Pour un exemple **exécutable complet avec contrôles d'erreur et fermeture**, voir les programmes déjà validés : [`Copy R13`](tests/passed/M6_R13_BLIT_COPY_01.asc), [`Fill R14`](tests/passed/M6_R14_BLIT_FILL_01.asc), [`Clear R15`](tests/passed/M6_R15_BLIT_CLEAR_01.asc).

**Portée de validation :** scénarios passés sous AMOS interprété/WinUAE ; compilation AMOS et vrai Amiga AGA toujours non testés pour M6.

### Lecture des caractéristiques ILBM

`Aga Pic Info(fichier$,champ)` expose les champs suivants :

| Champ | Valeur |
|---:|---|
| 0 | Largeur |
| 1 | Hauteur |
| 2 | Nombre de bitplanes |
| 3 | Nombre de couleurs dans CMAP |
| 4 | Compression : 0 (RAW), 1 (ByteRun1) |
| 5 | CAMG original |
| 6 | ModeID utilisable pour l'ouverture |
| 7 | Nombre de couleurs à demander à l'écran |

L'inventaire des images de référence est dans [`docs/ILBM_INVENTORY.md`](docs/ILBM_INVENTORY.md). Un chargement ILBM ne remplace pas l'obligation de créer un écran compatible avant `Aga Iff Load`.

### Séquence de test recommandée

Les tests M6 R14 Fill et R13 Copy sont [archivés](tests/passed/) après PASS WinUAE. Le test R15 Clear est également [archivé après PASS WinUAE](tests/passed/M6_R15_BLIT_CLEAR_01.asc) ; aucun test M6 actif. Le programme R12 [`R12_JEFF_A0_RETRY.asc`](tests/passed/R12_JEFF_A0_RETRY.asc) reste archivé ; son enchaînement historique était :

```text
Aga Pic Info → Aga Screen Open → Aga Double Buffer
→ Aga Iff Load → Aga Swap → Aga Wait Key
→ Aga Screen Close → Amos To Front
```

Sous AMOS, utiliser la syntaxe `If condition` / `End If` (sans `Then`) et fermer l'écran AGA avant de quitter le programme.

## Documentation et développement

- **Prise en main :** [installation](INSTALL.fr.md), [exemples AMOS](examples/README.fr.md), [tests validés](tests/passed/).
- **Rapports techniques :** [architecture](docs/ARCHITECTURE.md), [BankFont R38](docs/M14_FONT_BANK_R38.md), [historique et validations](docs/NEXT_SESSION.md), [feuille de route](docs/ROADMAP.md).
- **Développement :** [outils](tools/README.md), [intégrité des binaires](tools/verify_artifacts.py), [contrôle API bilingue](tools/test_readme_api_coverage.py), [CI](.github/workflows/artifact-integrity.yml), [règles techniques](EXTENSION_SOURCE_RULES.md).

