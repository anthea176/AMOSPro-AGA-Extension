# M8 — R22 0.8.6 : transitions souris natives Pressed/Released

**Statut : Gate A CPU/CI PASS 25 cas (CI complète (archive CI privée, run #42893816454)), Gate B AMOS interprété/WinUAE PASS sur le scénario R22 du 10/11/2026.** AMOS Compiler, matériel réel et stress NON TESTÉS.

## API AP20

Deux nouvelles fonctions **entières sans argument**, disponibles dans `dist/AMOSPro_AGA.Lib` R22 :

```amos
_P=Aga Mouse Pressed
_R=Aga Mouse Released
_B=Aga Mouse Buttons
```

Les résultats `Pressed` et `Released` sont des **masques de bits** : `0` aucun front, `1` gauche, `2` droit, `4` central et somme de ces bits pour plusieurs changements simultanés. **`-1`** si l'extension n'a pas de fenêtre/écran valide, si le focus Intuition n'appartient plus à la fenêtre, ou si `input.device` est indisponible.

Une **pression maintenue** génère `Pressed=1` une seule fois, puis `0` jusqu'à une nouvelle transition. Le premier appel alors que la fenêtre est active **initialise l'état** et renvoie `0`, même si un bouton est déjà tenu ; la reprise de focus fait de même.

Les transitions sont mémorisées dans **deux masques indépendants** (un pour Pressed, un pour Released) dans une zone privée de 16 octets liée à l'extension. Lire `Pressed` **ne consomme pas** le masque `Released`, et inversement. Chaque appel interroge `input.device/PeekQualifier()` et fait évoluer les deux files de fronts. La lecture retourne et efface uniquement le masque demandé. En cas de perte de focus, les deux masques sont invalidés ; après une réouverture `Aga Screen Open`, les 16 octets sont remis à zéro.

## Sécurité et limites

- L'implémentation R22 **ne lit aucun `IDCMP_MOUSEBUTTONS`**, ne retire aucun message de `Window.UserPort` et préserve `Aga Key`, `Aga Wait Key`, `Ctrl+C`, le RMBTRAP de R21, le Copper et les blits. Elle n'introduit aucune allocation persistante ni file d'événements Intuition propriétaire.
- **Clics courts :** si un appui ET son relâchement se produisent entièrement entre deux appels, ils **ne sont pas détectés**. Il faudrait un futur dispatcher commun `IDCMP_MOUSEBUTTONS/RAWKEY` avec enregistrement des transitions et non-perte des touches. R22 n'en fait pas une promesse.
- **Focus :** `Window.Flags` doit contenir `WFLG_WINDOWACTIVE` (`$00002000`). Une fenêtre non active donne `-1` et remet l'état à zéro. `Aga Mouse Buttons` R21 conserve son comportement antérieur d'instantané global.
- **Événements réels :** le masque est un échantillonnage des changements observés ; pas un compteur de clics. Deux appuis du même bouton sans appel intermédiaire restent confondus.
- **CPU 68000 :** D3 = résultat entier, D2 = 0 ; A3/SP et registres préservés ; lecture non bloquante, IOStdReq local 48 octets et paire OpenDevice/CloseDevice équilibrée.

## Construction et protections

| Élément | R22 |
|---|---|
| Bibliothèque courante | `dist/AMOSPro_AGA.Lib` |
| Archive candidate | `dist/experimental/AMOSPro_AGA_M8_v0.8.6_MOUSE_EDGES_R22.Lib` |
| Version et taille | `R22 0.8.6`, **12 852 octets** |
| SHA256 | `96e38d478bd97e7a65801e16e96ce08c0bbd4aaacb4a8a6644e4bc1289a0c997` |
| Base figée | R21 SHA256 `a72e3046df64e3ff8ebe12a5b4b0db45efebe27e17056919d31d11ca61e9c644` |
| Builder reproductible | [`tools/build_m8_mouse_edges_r22.py`](../tools/build_m8_mouse_edges_r22.py) |
| Émetteur 68000 | [`tools/m8_mouse_edges_emit.py`](../tools/m8_mouse_edges_emit.py) |
| Gate A CPU | [`tools/test_m8_mouse_edges_r22.py`](../tools/test_m8_mouse_edges_r22.py) |
| Gate B WinUAE PASS | [`tests/passed/M8_R22_MOUSE_EDGES_01.asc`](../tests/passed/M8_R22_MOUSE_EDGES_01.asc) — test exact archivé |

Les 31 entrées AP20 de R21 sont conservées, sauf la routine 6 `Aga Screen Open` (+18 octets, relais de remise à zéro) et l'ajout obligatoire de `GetP` à l'entrée 30. Les entrées 31 et 32 sont nouvelles. `R21`, `R20`, `R19`, `R18`, et `LAST_GOOD` R10 restent **inchangées**.

## Recette AMOS / WinUAE (Gate B exécutée)

1. Installer **R22 0.8.6 depuis `main`**, relancer AMOS pour recharger la bibliothèque. Ouvrir le test exact archivé et choisir `MYGIRL.IFF` (320×256×8).
2. Relâcher tous les boutons au début, puis maintenir **gauche environ 0,3 s**, relâcher ; maintenir **droit environ 0,3 s**, relâcher. Observer **aucune barre de menus Intuition** au clic droit.
3. Une fois les fronts observés, appuyer sur une touche clavier pour afficher le bilan AMOS. Faire une capture.

**Attendu :** `OPEN=DB=LOAD=SWAP=REOPEN=1` ; `BASEP=BASER=0` ; `PRESSED And 3=3` et `RELEASED And 3=3` ; `PL=PR=RL=RR=1` pour un seul cycle par bouton ; `DONE=1`, `ERR=0`, `KEY` enregistré ; `BEFOREP/BEFORER/CLOSEP/CLOSER/CLOSE2=-1` ; `REOPENP=REOPENR=0` ; `CLOSE X2 RETURNED`, retour normal sous AMOS. Les vérifications de focus sont couvertes par les tests CPU ; le focus réel et les clics courts doivent être évalués séparément.

**Résultat obtenu :** 10/11/2026 — capture WinUAE utilisateur : MYGIRL.IFF 320×256×8 ; OPEN=DB=LOAD=SWAP=REOPEN=1 ; BEFORE=-1/-1 ; BASE=0/0 ; PRESSED=3, RELEASED=3, PL=PR=RL=RR=1 ; DONE=1, ERR=0, FRAME=1001 (fin de boucle For) ; KEY=64, MOUSE=(221,185) ; CLOSED=-1/-1, CLOSE2=-1, REOPEN BASE=0/0 ; CLOSE X2 RETURNED ; fin AMOS normale ligne 117. Pas de preuve visuelle de la barre Intuition pendant le clic droit. Clics très courts, perte/reprise de focus réelle, Compiler, Amiga physique et stress non testés.

**Portée du PASS :** transitions gauche/droite échantillonnées et retour clavier/écran dans ce test ; ne garantit pas la capture des clics entre deux lectures ni les autres fonctionnalités M8 (drag, molette, dispatcher événementiel).

[État M8](M8_STATUS.md) · [Roadmap](ROADMAP.md) · [Interactions](INTERACTIONS_COLLISIONS.md).
