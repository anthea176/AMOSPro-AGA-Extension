# M15/R42 — Aga Box : contrat de contour 2D AGA

**M15/R42 v0.11.3 — CANDIDATE PUBLIÉE, Gate A CPU/CI PASS (360 scénarios), Gate B WinUAE NON TESTÉE (12/11/2026).** `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, **47 commandes AP20**. Coins inclusifs normalisés, 1 px d'épaisseur, clipping indépendant des quatre côtés d'origine (jamais de bordure inventée), refus sécurisé des rectangles hors écran, validation des coordonnées signed16 et index `Pen`, BitMap physique et signal `Safe` non bloquant. [Test unique WinUAE](../tests/current/M15_R42_BOX_01.asc) à importer via **Project → Merge ASCII**. `dist/AMOSPro_AGA.Lib` et `dist/experimental/AMOSPro_AGA_M15_v0.11.3_BOX_R42.Lib` identiques (**25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`). **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste la R41 v0.11.2 validée** (24 816 octets, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`) ; archives R41 et antérieures inchangées. [CI CPU + source strict PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43198823212). Gates C Compiler/D AGA physique non testées. Aucun test R42 archivé ou `LAST_GOOD` promu sans validation utilisateur. Travail uniquement sur `main` de `anthea176/AMOSPro-AGA-Extension`.

## Historique de l'étude et des vérifications préalables

**M15/R42 Gate A CPU/CI PASS (12/11/2026) :** **360 tests 68000** avec contrôle pixel à pixel du contour, sécurité des bitplanes, huit orientations de coins, rectangles clippés et hors écran, signal `Safe`, ABI, AP20 **47 commandes / 53 segments**, export assembleur strict et [CI globale PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43198823212). Binaire reproductible R42 v0.11.3 généré **en mémoire uniquement** : **25 896 octets**, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`. **Gate B AMOS interprété/WinUAE non testée** ; la R41 v0.11.2 demeure `LAST_GOOD` (24 816 octets), intacte. Le programme de recette R42 est préparé mais non encore publié.

**Décision du 12 novembre 2026 :** après la validation sous WinUAE de R41, l'utilisateur a autorisé le chantier M15/R42, **une seule nouvelle fonction `Aga Box`**. Ce texte est le contrat proposé pour le développement en cours. **Gate A CPU/CI et Gate B WinUAE non exécutées à l'ouverture du chantier.** R41 v0.11.2 est **`LAST_GOOD`**, 46 commandes AP20, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`.

## API prévue

```amos
_OK=Aga Box(X1,Y1,X2,Y2,Pen)
```

- **Contour d'un pixel**, jamais un remplissage (`Aga Blit Fill` existe déjà). **Coins inclusifs**, dans l'esprit du `Box x1,y1 To x2,y2` d'AMOS. Contrairement à `Aga Blit Fill(x,y,width,height,...)`, les deux paires sont des **coordonnées de coins**, pas des dimensions. La bibliothèque **normalise les coins inversés** : `Aga Box(280,220,20,30,Pen)` et `Aga Box(20,30,280,220,Pen)` produisent le même rectangle.
- Coordonnées AMOS reçues en LONG et vérifiées comme **signed16** `-32768..32767`. Tout argument hors de cet intervalle retourne `0` sans troncature vers un `SHORT` AmigaOS.
- `Pen` est un **index de couleur**, `0 <= Pen < (1<<Depth)`, avec profondeur physique/logique 1 à 8. Les pens invalides retournent `0` sans toucher l'écran.
- Les **quatre côtés d'origine** sont testés et clippés séparément aux bornes `0..Width-1` / `0..Height-1`. Un rectangle gigantesque qui englobe tout l'écran **mais dont les quatre côtés restent hors champ** ne doit dessiner **aucune bordure inventée** : `_OK=0`.
- Un rectangle partiellement à l'extérieur dessine **uniquement la portion visible de ses côtés d'origine**. Si `X1=X2` ou `Y1=Y2`, le contour dégénère en une seule ligne ; si les deux coins sont identiques, il dessine un pixel. Une seule couleur, **1 pixel d'épaisseur**, pas de motif de ligne, pas de XOR, pas de coordonnées flottantes.
- **`_OK=1` dès qu'au moins un pixel a été tracé** sur le back buffer AGA et **`_OK=0`** si rectangle invisible, état/arguments invalides, signal `Safe` indisponible ou aucun `WritePixel` réussi. Comme R41, un échec après un début de dessin n'est pas atomique.

## Sécurité des limites et mémoire

- Réutiliser strictement les validations R41 (déjà testée en WinUAE) : `Screen`, `GfxBase`, `DBState`, largeur/hauteur logiques et physiques `BitMap`, profondeur égale et 1..8, tous les pointeurs `Planes[]`, index front buffer 0 ou 1 ; **cible exclusive back buffer privé**.
- Vérifier **avant** tout dessin que le contour est susceptible d'avoir un côté visible. Les rectangles totalement invisibles retournent `0` et **n'utilisent pas `GetMsg` ni `graphics.library`**.
- Conserver la garde `Safe` non bloquante : un seul `Exec/GetMsg(-372)` si nécessaire, ne jamais bloquer avec `WaitPort`, ne pas `ReplyMsg`, ne pas effacer le bit `Disp`.
- `InitRastPort(-198)` temporaire sur la pile, `rp->BitMap` = `ScreenBuffer.sb_BitMap` inactif ; `SetAPen(-342)` et `SetDrMd(-354)` en mode de copie JAM1, `Move(-240)` puis `Draw(-246)` seulement sur **extrémités déjà incluses dans le BitMap**. Si une ligne est réduite à un point, utiliser `WritePixel(-324)` et traduire son succès `0` en résultat AMOS `1`. Terminer par `WaitBlit(-228)` avant de libérer le RastPort temporaire. **Aucune allocation persistante en Chip RAM**, aucun swap ou VBL implicite.
- Ne jamais appeler `graphics.library/Draw` avec coordonnées hors limites sur un `RastPort` non-layered : hors écran cela peut corrompre la mémoire. Le clipping `Aga Box` est réalisé en amont, indépendamment du clipping de `Aga Draw`.
- Les côtés partagent éventuellement leurs pixels aux coins ; avec une seule couleur en mode de copie, les écritures répétées sont idempotentes.

## AP20, build et validation

- Numéro d'entrée AP20 **52**, signature fonction numérique `00,0,0,0,0`, **47 commandes AP20 / 53 segments** visés. ABI : `D3=Pen`, `(A3)+ = Y2,X2,Y1,X1`, retour `D3` entier 0/1, `D2=0`, pile équilibrée, autres registres préservés comme R41.
- Source : [`tools/m15_box_r42_emit.py`](../tools/m15_box_r42_emit.py) ; [builder déterministe](../tools/build_m15_box_r42.py) **depuis l'archive R41 immuable** ; [CPU test natif](../tools/test_m15_box_r42.py).
- **Gate A** : construction 68000, audit des 47 commandes AP20 / 53 segments, validation stricte Capstone et export source natif, rectangles inversés, dégénérés, traversants, invisibles/enveloppants, tous côtés, dernière ligne/pixel, profondeurs 1/2/4/8, bitmap invalidé, pen hors plage, signal `Safe` et bit `Disp`, contrôle pixel à pixel des bitplanes et absence d'écriture extérieure, régressions anciennes et intégrité.
- **Gate B** : seulement après Gate A PASS, publier `dist/AMOSPro_AGA.Lib` et son archive **candidate R42 v0.11.3** + un seul `.asc` actif dans `tests/current/`; importer via **Project → Merge ASCII** et vérifier le rendu sous AMOS interprété/WinUAE. Promouvoir exactement la candidate testée vers `LAST_GOOD` **seulement après confirmation explicite de l'utilisateur**.
- Gates C Compiler et D Amiga AGA physique : non testées et indépendantes. **R41 `LAST_GOOD` et tous les binaires archivés restent intacts avant Gate B.** Aucun code R43 Circle ni R39 Font 8×8.

Travail exclusivement dans `anthea176/AMOSPro-AGA-Extension`, branche **`main`**, sans création de branche.
