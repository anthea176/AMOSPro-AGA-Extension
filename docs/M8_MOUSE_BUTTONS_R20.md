# M8 / R20 0.8.4 — Lecture des boutons souris

**Statut historique : R20 0.8.4 archivée, Gate A 21 CPU/CI PASS. Un test utilisateur WinUAE le 10/11/2026 a confirmé `PRESSED=RELEASED=SEEN=3`, `DONE=1`, `IOERR=0`, `KEY=64`, fin ligne 100, **mais le bouton droit a ouvert une barre Intuition persistante**. Gate B R20 partielle, pas PASS globale. Correctif candidate [R21](M8_RMBTRAP_R21.md). Compiler/Amiga réel non testés.

## API

```amos
_B=Aga Mouse Buttons
```

Retour : **bitmask entier `0..7`** (somme des bits) : `1` bouton gauche, `2` droit, `4` central si présent. `3` signifie gauche et droit simultanément ; `0` aucun bouton. **`-1`** si l'écran/fenêtre Intuition de l'extension est absent, étranger, ou si `input.device` ne peut pas être ouvert.

Les données proviennent de `input.device/PeekQualifier()` V36 : `IEQUALIFIER_LEFTBUTTON=$4000`, `RBUTTON=$2000`, `MIDBUTTON=$1000`. Cette lecture **ne retire aucun `IntuiMessage`** de `Window.UserPort`, et ne modifie ni `Aga Key` ni `Aga Wait Key`. Le pointeur de fenêtre et son écran sont contrôlés avant l'appel. Pas de nouvel `IDCMP`, d'allocation persistante ou d'état caché : un IOStdReq de **48 octets sur la pile**, initialisé à zéro, sert seulement à `OpenDevice()`, `PeekQualifier()`, `CloseDevice()`; `CloseDevice` n'est appelé que si l'ouverture a réussi.

**Limites explicites :** `PeekQualifier()` renvoie un **instantané global** de l'état d'entrée, pas les événements souris réservés à notre fenêtre. Le test doit garder le focus sur l'écran AGA. Ouvrir/fermer `input.device` à chaque appel est acceptable pour ce premier candidat de compatibilité, **pas une optimisation acquise pour une boucle de jeu**. Un appui/relâchement entre deux lectures peut être manqué ; R20 n'implémente pas de file d'événements ni de transitions mémorisées dans la Lib. La capture événementielle `IDCMP_MOUSEBUTTONS` et la gestion stricte du focus sont à étudier dans un incrément distinct.

## Transitions calculées côté AMOS

```amos
_OLD=Aga Mouse Buttons
_NOW=Aga Mouse Buttons
If _OLD>=0 and _NOW>=0
   _PRESSED=_NOW And (7-_OLD)
   _RELEASED=_OLD And (7-_NOW)
End If
```

La détection `pressed/released` compare **deux instantanés**. Pour une lecture continue, sauvegarder `_OLD=_NOW` à chaque itération. Les masques des transitions sont identiques à ceux des boutons (1/2/4). Ce ne sont **pas** encore des fonctions AP20 `Aga Mouse Pressed/Released`.

## Artefacts / immutabilité

- **Base protégée :** `dist/experimental/AMOSPro_AGA_M8_v0.8.3_MOUSE_POSITION_R19.Lib`, SHA256 `32c99d9d83affda67058fede26731dace6511ebc033b7974330e6f9eef39e295`.
- **Candidat R20 :** `dist/experimental/AMOSPro_AGA_M8_v0.8.4_MOUSE_BUTTONS_R20.Lib` et `dist/AMOSPro_AGA.Lib` **archivée depuis R21**, **12 016 octets**, SHA256 `9d1e9d6fd13478947c016d3f95973efa2ac766f96c364e091f43c69daa8672fe`.
- **Builder :** `tools/build_m8_mouse_buttons_r20.py`, entrée AP20 **30**. Entrées 0..28 R19 inchangées ; entrée 29 uniquement complétée par `GetP` ; nouvelle entrée 30 code 68000 242 octets. ABIs : D3 résultat, D2=0, A3 préservé, SP équilibrée.
- **Test CPU :** `tools/test_m8_mouse_buttons_r20.py` (OpenDevice, PeekQualifier, CloseDevice, rejets, ABI, masques). Attention : simulation CPU = Gate A uniquement.
- **Test utilisateur unique :** [`tests/historical/M8_R20_MOUSE_BUTTONS_01.asc`](../tests/historical/M8_R20_MOUSE_BUTTONS_01.asc), bandeau `M8-R20-MOUSE-BUTTONS-01`.
- **Protections :** R18/R19 archivées et `dist/AMOSPro_AGA_LAST_GOOD.Lib` R10 inchangée.

## Test WinUAE (après PASS Gate A)

1. Historique uniquement : ancienne procédure R20 ; pour la nouvelle validation installer **R21 0.8.5 de main**, lancer l'unique `.asc`, sélectionner `MYGIRL.IFF` **320×256×8**.
2. Dans l'image AGA, **relâcher les boutons**, presser et maintenir ~0,3 seconde **gauche**, relâcher ; puis presser et maintenir **droit**, relâcher. Éviter les clics instantanés.
3. Appuyer sur une **touche du clavier** pour terminer ; capturer le résumé AMOS.

**Attendu :** `OPEN/DB/LOAD/SWAP/REOPEN=1` ; `BEFORE/CLOSED/CLOSED2=-1` ; `PRESSED And 3=3`, `RELEASED And 3=3` ; `DONE=1`, `IOERR=0`, `KEY` non nul et `CLOSE X2 RETURNED` avec retour normal dans AMOS. `SEEN` reflète les états vus pendant le test (1, 2, 3 ou 7 possibles). `_REBTN` après réouverture reflète le bouton réellement tenu au moment de cet appel (normalement 0).

La Gate B R20 ne sera qualifiée **PASS** qu'après capture WinUAE vérifiée. Ne pas confondre ce scénario avec une validation de clics rapides, d'absence de fuite, d'AMOS Compiler ou du matériel réel.

Références AmigaOS : [`PeekQualifier()`](https://developer.amigaos3.net/autodocs/input.device/PeekQualifier.html), [`inputevent.h`](https://d0.se/include/devices/inputevent.h), [`OpenDevice()`](https://developer.amigaos3.net/autodocs/exec.library/OpenDevice.html), [plan interactions](INTERACTIONS_COLLISIONS.md).
