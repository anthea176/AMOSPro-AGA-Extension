# Tests AMOS actifs

**R43 v0.11.4 — Aga Circle, Gate B AMOS/WinUAE NON TESTÉE.** Un seul test à importer via **Project → Merge ASCII** : [`M15_R43_CIRCLE_01.asc`](M15_R43_CIRCLE_01.asc). Vérifier les cercles concentriques, les quatre coins, le clipping, les paramètres invalides, le double buffering et **`RESULT 1` / `CLOSE RETURNED`**, puis confirmer le rendu.

**Bibliothèque candidate à installer sans renommage :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), 27 092 octets, SHA256 `9c410229e9831c4170194a933451f1d30a2cf69791a88785627b88fad8fcdecf`, 48 commandes AP20 ; Gate A 436 tests CPU 68000 + [CI PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43203755354).

**Dernière version WinUAE validée : R42 `LAST_GOOD`**, [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib), 25 896 octets, SHA256 `6028ff508fb78019e1b53d30a37ec1d0cdcd9012285abd3e09caa44fe3fa98cc`, [test R42 archivé intact](../passed/M15_R42_BOX_01.asc). **Ne pas promouvoir R43 avant Gate B confirmée par l'utilisateur.** Gates C/D R43 non testées.
