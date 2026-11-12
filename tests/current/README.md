# Tests AMOS actifs

**Seul test actif :** [`M15_R40_PLOT_01.asc`](M15_R40_PLOT_01.asc) — **M15/R40 Gate B non testée**. Ne pas archiver ni promouvoir `LAST_GOOD` avant une confirmation de fonctionnement sous AMOS interprété/WinUAE.

**Pour tester R40 :** installer la [candidate `AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib) (v0.11.1, 23 840 octets, SHA256 `0282fbf8eacd0c3e68e710a6ffa89bda2fed689674b2b5ea01aedbc1a3378231`) à la place de l'extension AGA précédente dans **`APSystem`**, sans changer le **slot**, puis redémarrer AMOS. Conserver une sauvegarde de l'ancienne bibliothèque ; la [R38 `LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) reste inchangée et validée. Démarrer un programme vide et importer le test via **Project → Merge ASCII**, jamais via `Load` de programmes tokenisés. **Aucun ABK ni IFF à copier.**

Le programme ouvre un écran 320×256×256 couleurs, affiche **un X composé de deux diagonales** et les quatre pixels extrêmes `(0,0)`, `(319,0)`, `(0,255)`, `(319,255)`. Il appelle 192 fois `Aga Plot` pour les diagonales, vérifie le pen 0, les coordonnées hors écran et les pens invalides, puis présente le back buffer avec `Aga Swap`. Après un swap, il vérifie également que le dessin redevient possible lorsque `Safe` est disponible. À la fermeture il teste le refus sans écran ouvert.

**Résultats attendus :** `CORNERS 1 1 1 1`, `CENTER 1 PEN0 1`, `DIAG 192 ERR 0`, `BADXY 0 0 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. Capturer à la fois l'écran AGA (X coloré visible) et la console finale. `RESULT 1` seul ne démontre ni affichage correct ni stabilité matérielle.

**R40 n'est pas encore `LAST_GOOD`.** Gates C AMOS Compiler et D Amiga AGA réel non testées. Les validations R38 archivées restent dans [`tests/passed/`](../passed/).
