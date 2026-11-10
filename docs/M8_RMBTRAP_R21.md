# M8 — R21 0.8.5 : RMBTRAP sur la fenêtre Intuition

**Statut R21 0.8.5 : Gate A + B PASS.** Gate A : **11 cas CPU 68000 et [CI complète verte](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/42887916480)**. Gate B : **PASS sur le scénario AMOS interprété/WinUAE**, confirmé explicitement par l'utilisateur le **10/11/2026** : les boutons fonctionnent et le clic droit n'affiche plus de barre de menus Intuition. Aucune capture chiffrée supplémentaire R21 n'a été communiquée. Compiler, matériel réel, stress et clics très brefs non testés.

## Incident constaté en R20 (10 novembre 2026)

Capture utilisateur : `M8-R20-MOUSE-BUTTONS-01`, `MYGIRL.IFF` 320×256×8. `OPEN/DB/LOAD/SWAP/REOPEN=1`, `PRESSED=3`, `RELEASED=3`, `SEEN=3`, `DONE=1`, `IOERR=0`, `KEY=64`, `BEFORE/CLOSED/CLOSED2=-1`, `REOPEN BUTTONS=0`, `CLOSE X2 RETURNED` et fin AMOS ligne 100. Les transitions gauche et droit ont été observées sans erreur.

**Défaut bloquant pour l'usage jeu :** pendant le clic droit, Intuition ouvre la barre de menus de l'écran AGA ; la barre ne se retire pas normalement après relâchement. Ce défaut ne contredit pas les valeurs des boutons, mais interdit de classer le scénario R20 comme **Gate B complète PASS**. Le test R20 est conservé **identique** dans `tests/historical/M8_R20_MOUSE_BUTTONS_01.asc` ; ne pas le ranger dans `passed/`.

## Diagnostic technique confirmé

Le manuel AmigaOS recommande `WFLG_RMBTRAP` (valeur `$00010000`) lors de l'ouverture de toute fenêtre qui utilise le clic droit sans menus Intuition. Le système délivre alors les événements `MENUDOWN/MENUUP` à la fenêtre plutôt que de déclencher ses menus. **La fonction `Aga Mouse Buttons` de R20 utilise `input.device/PeekQualifier()`** et ne modifie pas `IDCMP` ; son résultat instantané ne dépend pas d'une lecture de ces messages.

Dans l'entrée AP20 **6 — `Aga Screen Open`**, l'appel `OpenWindow()` reçoit une structure `NewWindow` sur la pile. Le champ `NewWindow.Flags` est à **+14** dans la structure. La routine assembleur R20 initialise ce champ à :

```asm
MOVE.L #$00021900,14(A7)   ; Flags existants (sans RMBTRAP)
```

R21 change **un seul octet de code** (immédiat au décalage `+$01EE` de l'entrée 6) :

```asm
MOVE.L #$00031900,14(A7)   ; Ajout de WFLG_RMBTRAP ($00010000)
```

Aucun autre bit de `NewWindow.Flags` n'est modifié ; aucune instruction n'est insérée. Tous les branchements PC-relatifs et longueurs AP20 restent identiques. Les **30 autres segments**, les tokens et les commandes AMOS R20 demeurent identiques bit pour bit. Le titre interne passe de R20 0.8.4 à R21 0.8.5, sans changement de longueur HUNK.

## Artefacts et invariants

- **Bibliothèque courante validée WinUAE sur ce scénario :** [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) — R21 0.8.5, **12 016 octets**, SHA256 `a72e3046df64e3ff8ebe12a5b4b0db45efebe27e17056919d31d11ca61e9c644`.
- **Archive R21 :** `dist/experimental/AMOSPro_AGA_M8_v0.8.5_RMBTRAP_R21.Lib` (identique à la candidate).
- **Base R20 archivée et non modifiée :** `dist/experimental/AMOSPro_AGA_M8_v0.8.4_MOUSE_BUTTONS_R20.Lib` SHA256 `9d1e9d6fd13478947c016d3f95973efa2ac766f96c364e091f43c69daa8672fe`.
- **R19/R18 et `LAST_GOOD` R10 inchangées.**
- **Builder :** `tools/build_m8_rmbtrap_r21.py`, dérivé exclusivement de l'archive R20, avec vérification de signature et SHA256.
- **Tests CPU :** `tools/test_m8_rmbtrap_r21.py` vérifie le champ réellement transmis à `OpenWindow()` sous CPU 68000 simulé, les modes, la fermeture, les boutons R20 et l'identité des autres segments. Il ne simule pas le rendu des menus Intuition.
- **Test WinUAE validé et archivé (identique octet pour octet) :** [`tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc`](../tests/passed/M8_R21_MOUSE_RMBTRAP_01.asc), bandeau `M8-R21-MOUSE-RMBTRAP-01`.

## Gate B — protocole effectué et validé par l'utilisateur

1. Installer la **R21 de `main`** à la place de R20 ; relancer AMOS si nécessaire pour recharger la bibliothèque.
2. Exécuter le seul test courant. Choisir `MYGIRL.IFF`, 320×256, 8 plans.
3. Dans la fenêtre AGA, presser/maintenir environ 0,3 s **gauche**, relâcher, puis presser/maintenir **droit** et relâcher. **Observer pendant le clic droit : aucune barre de menus Intuition ne doit apparaître.**
4. Presser une touche clavier pour terminer ; vérifier le retour dans l'éditeur, sans menu restant affiché, et faire une capture du résumé.

**Critères attendus** : `OPEN/DB/LOAD/SWAP/REOPEN=1`, `PRESSED And 3=3`, `RELEASED And 3=3`, `DONE=1`, `IOERR=0`, `KEY` reçu, `BEFORE/CLOSED/CLOSED2=-1`, `CLOSE X2 RETURNED`, **aucune barre de menus pendant et après le clic droit**. Le champ `FRAME=1001` peut être normal : le test termine une boucle `For 1 To 1000` même si `DONE=1` est atteint avant.

**Résultat : Gate B R21 PASS sur confirmation explicite de l'utilisateur.** La disparition de la barre Intuition après clic droit est confirmée ; les valeurs individuelles du récapitulatif R21 n'ont pas été fournies et ne sont pas inventées. Aucun clic rapide garanti, aucune preuve d'absence de fuite ou de compatibilité Compiler/Amiga réel.

**Sources AmigaOS :** [Intuition Mouse](https://wiki.amigaos.net/wiki/Intuition_Mouse), [Intuition Classic Menus](https://wiki.amigaos.net/wiki/Intuition_Classic_Menus), [structure et flags de Window](https://amigadev.grimore.org/Includes_and_Autodocs_3._guide/node05e0.html).
