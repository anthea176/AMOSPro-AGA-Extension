# M8 / R19 0.8.3 — Souris Intuition : coordonnées X et Y

**État au 10/11/2026 : R19 PASS Gate A CPU 68000 (76 cas) et Gate B AMOS interprété/WinUAE** sur le scénario X/Y ; CI générale #42878271256 (archive CI privée) PASS. M8 reste en cours pour boutons et transitions.

## Artefacts

| Élément | Référence |
|---|---|
| Bibliothèque candidate | [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), **R19 0.8.3, 11 744 octets** |
| Archive identique | [`dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib`](../dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib) |
| SHA256 | `32c99d9d83affda67058fede26731dace6511ebc033b7974330e6f9eef39e295` |
| Base R18 PASS WinUAE | `dist/experimental/AMOSPro_AGA_M7_v0.8.2_COPPER_RASTER_R18.Lib` (inchangée) |
| LAST_GOOD | R10 0.6.1 inchangée |
| Builder / CPU | [`build_m8_mouse_position_r19.py`](../tools/build_m8_mouse_position_r19.py) / [`test_m8_mouse_position_r19.py`](../tools/test_m8_mouse_position_r19.py) |
| **Test archivé et validé** | [`M8_R19_MOUSE_POSITION_01.asc`](../tests/passed/M8_R19_MOUSE_POSITION_01.asc) |

## Contrat de l'API

~~~amos
_MX=Aga Mouse X
_MY=Aga Mouse Y
~~~

- Deux **fonctions entières sans argument**, entrées AP20 **28** et **29**, non bloquantes. Ces commandes renvoient la position en **pixels logiques de l'écran AGA** (origine en haut à gauche).
- Plages : `X = 0..largeur-1`, `Y = 0..hauteur-1`. **Retour `-1`** si écran/fenêtre inexistant, fenêtre étrangère, dimension invalide ou composante de position hors écran. X et Y sont évalués indépendamment.
- **Syntaxe obligatoire :** `_MX=Aga Mouse X` et jamais `Aga Mouse X` seul, qui serait une erreur de syntaxe AMOS. Résultat dans D3, D2=0, A3 inchangé, SP équilibrée.
- La routine lit `Window.MouseX(+14)` / `MouseY(+12)` et ajoute `Window.LeftEdge(+4)` / `TopEdge(+6)` après extension signée 16 bits. Elle vérifie `Window.WScreen(+46)` contre l'écran de l'extension. Les dimensions proviennent de l'état historique (largeur +12, hauteur +16), le pointeur de fenêtre de +36.
- **Aucune allocation, aucun nouveau champ d'état, aucun événement IDCMP supplémentaire**, aucun `GetMsg` ni `ReplyMsg`. Le clavier existant (`Aga Key`, `Aga Wait Key`) et le Copper sont inchangés.
- Les **28 entrées AP20 R18** sont préservées : 0..26 identiques, entrée 27 complétée uniquement par le délimiteur `GetP` ; nouvelles fonctions 28 et 29.

## Validation

**Gate A isolée : PASS 76 scénarios CPU 68000** (CI #42877478472 (archive CI privée)). Coordonnées 320, 640, 1280, fenêtres décalées, hors limites, état clos, fenêtre étrangère, maintien des registres et reproductibilité HUNK/AP20. **La CI d'intégrité générale a également PASS** (CI générale #42878271256 (archive CI privée)) avec les anciennes bibliothèques préservées.

**Gate B sous AMOS Professional interprété/WinUAE : PASS** après deux captures utilisateur du 10/11/2026. Test archivé : [`M8_R19_MOUSE_POSITION_01.asc`](../tests/passed/M8_R19_MOUSE_POSITION_01.asc) avec `MYGIRL.IFF` 320×256×8.

1. Installer R19, choisir l'image IFF. Pointer **vers le haut-gauche** de l'image et appuyer une fois sur une touche.
2. Pointer **vers le bas-droit** et appuyer une deuxième fois sur une touche.
3. Capturer la console AMOS : `OPEN/DB/LOAD/SWAP=1`, `P1` et `P2` dans les plages attendues et différentes, `BEFORE/CLOSED/CLOSED2=-1 -1`, `REOPEN=1`, `CLOSE X2 RETURNED`. La position `POS3` après réouverture dépend de l'emplacement réel du pointeur.

**Résultats observés :** Deux captures WinUAE le 10/11/2026 : premier essai `P1=(112,65)`, `P2=(24,238)` ; second essai confirmatoire `P1=(0,0)`, `P2=(319,255)` sur `MYGIRL.IFF` 320×256×8. `OPEN=DB=LOAD=SWAP=REOPEN=1`, `BEFORE/CLOSED/CLOSED2=-1 -1`, `KEY=64` deux fois, `POS3=(319,255)`, `CLOSE X2 RETURNED`, retour AMOS normal ligne 87. La seconde capture lève la réserve de position du premier essai.

**Gate C Compiler et Gate D Amiga réel : NON TESTÉES.** Aucun succès CPU ne remplace la validation du suivi réel de souris ou du focus.

## Suite

Après le **PASS WinUAE**, la révision GitHub exacte du test R19 a été archivée et `tests/current/` est vide. Prochain incrément M8 : boutons gauche/droit et fronts appui/relâchement, sans conflit avec `Aga Key`. M9 hotspots et M10 collisions restent séparés.

Références : [NDK `Window`](https://amigadev.elowar.com/read/ADCD_2.1/Libraries_Manual_guide/node0121.html), [`intuition.i`](https://d0.se/include/intuition/intuition.i), [spécification interactions](INTERACTIONS_COLLISIONS.md).
