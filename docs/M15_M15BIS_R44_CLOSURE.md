# M15 + M15bis — Clôture R44 v0.11.5 (12/11/2026)

**Statut : CLÔTURÉ pour les Gates A (CPU/CI) et B (AMOS interprété/WinUAE).** Deux retours utilisateur distincts valident d'abord le test R44 du curseur, puis l'[exemple interactif réunissant M15 et M15bis](../examples/2d_cursor.asc) (« ça marche super »). Le second retour confirme le fonctionnement visible de la démo ; aucun relevé de sortie chiffré de cette démo n'a été fourni. Les **Gates C (AMOS Compiler) et D (Amiga AGA physique) ne sont pas testées** et ne sont pas déduites de WinUAE.

## Fonctionnalités livrées

- **M15** : `_OK=Aga Plot(X,Y,Pen)`, `_OK=Aga Draw(X1,Y1,X2,Y2,Pen)`, `_OK=Aga Box(X1,Y1,X2,Y2,Pen)`, `_OK=Aga Circle(CX,CY,Radius,Pen)`. Dessin 2D sur le back buffer AGA privé, clipping et contrôles `Safe`, sans tracé hors écran.
- **M15bis/R44** : `_OK=Aga Mouse Cursor(Visible)` : `0` masque le pointeur Intuition **de notre seule fenêtre AGA**, `1` restaure le pointeur ; la souris reste active. Image transparente 16×16, 72 octets Chip RAM alloués une fois au premier masque ; fermeture dans l'ordre `ClearPointer` → `CloseWindow` → `FreeMem` avec les quatre sorties de la fenêtre privée protégées. Les autres fenêtres et le Workbench ne sont pas désactivés globalement.
- **R44 v0.11.5** : **49 commandes AP20, 55 segments, 27 460 octets**, SHA256 **`0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`**.

## Gates et preuves

**Gate A CPU/CI PASS :** 516 cas natifs CPU 68000 de R44, incluant 500 changements de visibilité, ABI, mémoire, sécurité des paramètres, appels Intuition, fermeture, HUNK/AP20 et export source strict. [CI de publication candidate PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43209272738), [CI de l'exemple combiné PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43210592337). Ces CI sont des preuves statiques/natives, pas des exécutions AMOS interactives.

**Gate B AMOS/WinUAE PASS — test curseur R44 :** capture utilisateur avec `OPEN 1 DB 1 SWAP 1`, `SHOW 1 1 1`, `HIDE 1 1`, `BAD 0 0 NOSCREEN 0`, `SWITCHES 500 ERR 0`, `CHIP FREE 1631384 1631384 DROP 0`, `BIG FREE 1630656 1630656 DROP 0`, `CHIP WARN 0`, `CHIP BEFORE/END 1801928 1801928`, `CLOSED -1 RESULT 1` et `CLOSE RETURNED`. Aucune perte de Chip RAM **mesurée sur ce test** ; cela ne prouve pas tous les scénarios prolongés ou matériels.

**Gate B WinUAE PASS — démonstration globale :** l'utilisateur confirme ensuite « ça marche super » pour [`examples/2d_cursor.asc`](../examples/2d_cursor.asc), qui rassemble Plot/Draw/Box/Circle et la visibilité du pointeur. Aucune image IFF, banque de fontes ni fichier supplémentaire n'est nécessaire. Test visuel confirmé ; le texte exact `RESULT 1` de cette démo **n'a pas été fourni**.

## Promotion et intégrité

- **`dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M15BIS_v0.11.5_MOUSE_CURSOR_R44.Lib`**, même binaire exact R44, 27 460 octets, SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`.
- **Test WinUAE R44 archivé à l'octet près** : [`tests/passed/M15BIS_R44_MOUSE_CURSOR_01.asc`](../tests/passed/M15BIS_R44_MOUSE_CURSOR_01.asc), **3 053 octets**, Git blob `099f7125260c340dfbb4819f5770d1dbafd6789d`. Aucune correction des commentaires historiques dans le fichier.
- **Exemple combiné conservé** : [`examples/2d_cursor.asc`](../examples/2d_cursor.asc), **6 495 octets**, Git blob `b9db059c7c3554d8f3bb59fca61ff2d54270a23b`.
- `tests/current/` ne contient plus aucun test `.asc` actif après promotion.
- **R43 v0.11.4** reste archivée séparément dans `dist/experimental/AMOSPro_AGA_M15_v0.11.4_CIRCLE_R43.Lib`, 27 092 octets, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf` ; R42 et toutes les archives antérieures restent conservées, non réécrites.

**Travail GitHub :** exclusivement sur la branche `main` du dépôt `anthea176/AMOSPro-AGA-Extension`. Cette clôture ne commence **aucun nouveau chantier M16**. Prochaine étude éventuelle : format d'images compressées en Fast RAM avec dessin CPU, gestion opaque/transparente et décompression rapide, [roadmap](ROADMAP.md).
