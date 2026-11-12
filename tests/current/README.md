# Test AMOS actif — M15/R41 Aga Draw

**Seul test `.asc` actif :** [`M15_R41_DRAW_01.asc`](M15_R41_DRAW_01.asc). **Gate A CPU/CI 68000 PASS (325 cas) ; Gate B AMOS interprété/WinUAE NON TESTÉE**. La R40 reste `LAST_GOOD`. Ne PAS déplacer le test dans `tests/passed/` ni promouvoir de binaire sans confirmation utilisateur.

Installer la [candidate R41](../../dist/AMOSPro_AGA.Lib) (**v0.11.2**, 24 816 octets, SHA256 `0dee80beb83ea6d01f0fa6d74dc41dbb6374cf51bbc89ffc47c6191077c51bdc`) dans `APSystem`, sous le nom exact `AMOSPro_AGA.Lib`, en conservant le même slot d'extension. Sauvegarder la précédente version et **redémarrer AMOS**. La [R40 `LAST_GOOD`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) et son archive sont inchangées.

Dans un programme AMOS **vide**, importer le test avec **Project → Merge ASCII** (pas `Load` des programmes tokenisés). Aucun IFF ni ABK nécessaire. Le test ouvre un écran **320×256×256 couleurs**, dessine un cadre, **huit rayons** dans toutes les directions et **quatre lignes traversant les limites de l'écran**, dont des diagonales. Il vérifie aussi les quatre segments intégralement hors écran, les valeurs 32 bits qui ne rentrent pas dans les coordonnées signées 16 bits, les index de couleur invalides, le point unique, le `Safe` après un swap et le retour à AMOS.

**Affichage attendu :** cadre blanc, étoile colorée à huit branches au centre, deux diagonales, une ligne horizontale et une verticale traversantes (toutes coupées proprement aux bords). Les tracés ne doivent pas déborder sur la mémoire et aucun écran noir / plantage n'est attendu.

**Résultats attendus à la console :** `OPEN 1 DB 1 CLEAR 1`, `BORDER 1 1 1 1`, `CLIPPED 1 1 1 1`, `STAR 8 ERR 0 CENTER 1`, `OUTSIDE 0 0 0 0`, `BADLONG 0 0`, `BADPEN 0 0`, `SWAP 1 BACKSAFE 1`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. Le résultat numérique `RESULT 1` ne remplace pas la vérification du rendu visuel.

**Gates C Compiler et D Amiga AGA physique NON TESTÉES.** Ancien [test R40 exact et validé](../passed/M15_R40_PLOT_01.asc) conservé dans `tests/passed/`.
