# M13 / R32 0.10.4 — Aga Palette Bank Apply (contrat approuvé)

**État du chantier le 11/11/2026 : source R32 en préparation Gate A ; pas encore de candidate installable.** R31 0.10.3 reste la bibliothèque courante et `LAST_GOOD` validée WinUAE. Ne pas publier ni promouvoir R32 avant les contrôles prévus. Gates B AMOS/WinUAE, C Compiler et D Amiga réel NON TESTÉES.

## Contrat de la fonction unique

`_OK=Aga Palette Bank Apply(Start(bank),index)` — fonction à deux paramètres entiers, retour entier **1** succès, **0** rejet sans changement d'écran.

- `Start(bank)` : pointeur des données d'une **banque DATA AMOS native encore vivante**, préalablement initialisée au format **AGAPAL v1** (R30), et remplie par R31 ou rechargée avec `Load` AMOS. Le numéro de banque brut n'est pas un pointeur. La banque n'est pas modifiée.
- `index` : emplacement à partir de **0**, strictement inférieur à la capacité AGAPAL (1..256).
- Palette : compte du descripteur choisi **1..256**. Une palette vide (compte 0) est refusée. La fonction vérifie les signatures externes/interne, la version, le numéro et la taille exacte de la banque, les flags et l'offset de l'emplacement avant tout accès aux couleurs.
- Écran cible : **écran AGA Intuition privé actif de l'extension**, profondeur 1..8, mode standard indexé (refus HAM/EHB/dual playfield), `ColorMap` valide. Refus si le compte de la palette dépasse le nombre logique de couleurs ou `ColorMap.Count` : **pas de troncature silencieuse**.
- Conversion **RGB24 → RGB32 AmigaOS** : chaque octet de composante est répété quatre fois (exemple : `0x7F` → `0x7F7F7F7F`). Une table temporaire `LoadRGB32` est créée en mémoire publique, **8 + 12 × nombre de couleurs** octets (maximum 3 080), incluant en-tête (count,firstPen=0) et terminateur 32 bits nul. AllocVec puis FreeVec, sans mémoire persistante de l'extension ; Fast RAM possible par le système.
- **Effet immédiat, sans WaitTOF/VBL implicite** : un seul `graphics.library/LoadRGB32` sur le `ViewPort` de l'écran privé. Seules les couleurs **0..count-1** sont remplacées ; les couleurs supérieures restent inchangées. Aucun pixel, bitplane, Copper, fichier ABK ou donnée de banque modifié. Aucun fade ni cycling.
- Les rejets (banque/index/palette/écran/alloc invalides) surviennent **avant `LoadRGB32`**, et ne modifient ni la banque ni l'écran. `LoadRGB32` ne fournit pas de résultat d'erreur à annuler une fois appelé.

**Sécurité :** `TypeOfMem` vérifie les bornes accessibles mais ne prouve pas que l'adresse appartient réellement à une allocation. N'utiliser **que** `Start(bank)` d'une banque DATA AMOS vivante, jamais un pointeur arbitraire, ancien ou libéré.

## Validation prévue

- **Gate A :** builder AP20 reproductible à partir de l'archive R31, uniquement un nouveau token, tests Unicorn M68000 avec Capstone pour l'ABI (D3/D2/A3), conversion RGB32, limites de l'écran, palette partielle, banque Chip/Fast, refus atomiques avant affichage, libération temporaire, absence d'écritures dans banque/bitplanes ; export source 68000 strict, CI complète. Résultat à consigner avant distribution.
- **Gate B :** dans AMOS interprété/WinUAE, importer un seul fichier `.asc` actif après Gate A ; ouvrir un écran AGA indexé, capturer deux palettes différentes en AGAPAL, altérer les couleurs affichées, appliquer successivement les deux, vérifier `Aga Palette Get` sur les pens 28/3/224, l'application partielle et la conservation des couleurs supérieures, les refus (index hors plage, palette vide, écran fermé), les sauvegardes/rechargements ABK natifs, le retour `RESULT 1` et la fermeture propre. La CI ne remplace pas cette preuve utilisateur.
- **Gates C et D :** compilation AMOS et Amiga physique AGA non testés tant que cela n'a pas réellement été réalisé.

La candidate passante Gate A devra être `dist/AMOSPro_AGA.Lib`, avec une archive versionnée R32 ; `dist/AMOSPro_AGA_LAST_GOOD.Lib` reste R31 jusqu'au PASS WinUAE utilisateur, puis devra être promue **octet pour octet**. Actualiser les **deux README à chaque nouvelle instruction et validation** et archiver le test PASS sans retouche. **Aucune fonction de fade/import/cycling n'est incluse.** Pas de nouvelle branche et aucun autre dépôt.
