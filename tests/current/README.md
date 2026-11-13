# M18/R67 — Capture directe FICON8 : Gate B WinUAE interprétée À FAIRE

**Candidate active R67 v0.13.12** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **43 180 octets**, SHA256 `ce7742ae605daba5359145b69fe6cbc5bfa1869ba81c0c9e3e8a1ae12f4cd1e5`, 61 commandes / 68 AP20. **Gate A M68000 PASS, 240 cas**, [CI complète](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43456641279). Gate B WinUAE **non exécutée**, Gate C Compiler manuelle une seule fois **à la fin M18**. R63 `LAST_GOOD` protégée.

**ASC unique actif** : [`M18_R67_FICON8_CAPTURE_01.asc`](M18_R67_FICON8_CAPTURE_01.asc). Installer R67, créer un programme AMOS vide, **Project → Merge ASCII**, exécuter **en interprété uniquement, sans Compiler**. Les **banques 11, 12 et 13 doivent être libres** ; `Reserve As Data 13,256` peut écraser des données. Le programme écrit ou écrase `RAM:M18_R67_FICON8.ABK` ; environnement WinUAE jetable recommandé.

Il crée FICON8 et FICHIP8, prépare une icône source indexée 256 couleurs (cadre blanc, diagonales rouges/vertes, intérieur index zéro), la dessine **opaque** dans le back buffer à **X31 Y44 (non aligné)** puis à **X16 Y80 (aligné)**, et la capture vers les slots 2/3 sans banque intermédiaire. Il compare **tous les 288 octets** capturés à l'original, vérifie six appels invalides rejetés, et **Chip/Fast Free identiques avant/après capture**. Il sauvegarde une **banque FICON8 remplie** sur `RAM:`, efface/recharge, puis compare à nouveau les 288 octets. Après appel explicite de `Aga F Chip Stage`, il affiche les deux icônes capturées en CPU et au Blitter.

**Rendu attendu :** fond bleu, **X30** CPU transparent et **X90** Blitter transparent (intérieur bleu), **X150** Blitter opaque (intérieur noir), **X210** sans dessin (cache non prêt). Les trois premières icônes sont 16×16, contour blanc et diagonales rouges/vertes. Console : **`RESULT 1` et `CLOSE RETURNED`** ; transmettre les deux captures graphique + texte.

Le test R66 validé A/B est [archivé à l'identique](../passed/M18_R66_FICHIP_DYNAMIC_01.asc). Le binaire R66 historique et R63 `LAST_GOOD` restent inchangés.
