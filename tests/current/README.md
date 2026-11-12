# Tests AMOS actifs

**Unique test courant :** [`M15BIS_R44_MOUSE_CURSOR_01.asc`](M15BIS_R44_MOUSE_CURSOR_01.asc), pour **R44 v0.11.5 `Aga Mouse Cursor(Visible)`**. Importer sous AMOS interprété / WinUAE via **Project → Merge ASCII** après installation de la candidate R44 (27 460 octets, SHA256 `0902c9c58f9c0de7d65fc5dbf8782d552b113b85263af1653778b1a706b4e2dc`).

**Gate A CPU 68000/CI PASS (516 scénarios), [CI complète PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43208679398). Gate B WinUAE NON TESTÉE.** Observer le pointeur visible au lancement, masqué après la commande `0`, réaffiché avec `1`, puis masqué jusqu'à la fermeture. Tester le passage Workbench/AGA, les coordonnées et clics, l'absence de fuite pendant les 500 bascules (`SWITCHES 500 ERR 0`), `RESULT 1` et `CLOSE RETURNED`. Les mesures Chip et le plus grand bloc doivent être examinées, sans leur attribuer à elles seules la preuve d'absence de fuite. La recette complète inclut également Ctrl+C et réouverture.

**Dernière bibliothèque validée sous WinUAE : R43 `LAST_GOOD`**, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf` ; [test R43 archivé sans modification](../passed/M15_R43_CIRCLE_01.asc). `LAST_GOOD` ne doit pas être remplacée avant la validation utilisateur de Gate B R44. Gates C (Compiler) et D (Amiga AGA physique) non testées.
