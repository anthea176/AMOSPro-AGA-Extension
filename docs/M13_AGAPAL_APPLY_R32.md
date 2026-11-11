# M13 / R32 0.10.4 — Aga Palette Bank Apply (Gates A/B PASS)

## R32 0.10.4 VALIDÉE — Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Fonction ajoutée seule :** `_OK=Aga Palette Bank Apply(Start(bank),index)` applique une palette RGB24 AGAPAL non vide (1..256 couleurs) à l'écran AGA privé par `graphics.library/LoadRGB32`, immédiatement sans VBL implicite. Retour entier 1/0, aucun changement des banques/pixels, seuls les pens 0..compte-1 remplacés. Exiger un vrai `Start(bank)` d'une banque DATA vivante, jamais un numéro brut ou une adresse périmée.

**Gate A :** 136 scénarios CPU 68000 PASS, export source 68000 strict PASS, [CI candidate 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032230040), [CI documentaire 34/34 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43032630960).

**Gate B PASS — capture utilisateur de `M13_R32_AGAPAL_APPLY_01.asc` :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `AP0 1 AP1 1 PART 1`, `GREEN 65280 RED 16711680 BLUE 255`, `PEN224 795192 PART3 660510 PART28 255`, `BADNEG 0 BAD8 0 EMPTY 0`, `BADSIZE 0 BADCOUNT 0`, `AFTERBAD 255 AFTERCOUNT 255`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 16711680 PART 1`, `REST3 660510 REST28 16711680`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**, et fin propre `End of program at line 161`. PASS limité à ce scénario AMOS interprété/WinUAE ; Compiler et vrai Amiga AGA non testés.

**Promotion :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.4_AGAPAL_BANK_APPLY_R32.Lib`, **19 244 octets**, SHA256 `0a20d014303f77732f25959afa7daa4cc92c53479a7770f2abbff26fb1708894` (octet pour octet). R31 0.10.3 est préservée en archive versionnée (18 520 octets, SHA256 `0b36e65fcc6e6e88fa2a4e6520fd831973e751c8af602cfb8501ec22c7492c41`). ASC validé archivé **sans modification** dans [`tests/passed/M13_R32_AGAPAL_APPLY_01.asc`](../tests/passed/M13_R32_AGAPAL_APPLY_01.asc). **Aucun ASC actif** dans `tests/current/`. Gates C Compiler/D matériel réel **NON TESTÉES**.

**Suite :** aucune fonction Import/Fade/Cycling sans échange et accord explicite sur son contrat ; travailler seulement sur `main`, aucun autre dépôt ni branche.

---



**Checkpoint historique :** R32 était candidate Gate A ; la capture WinUAE a depuis validé Gate B et entraîné la promotion dans `LAST_GOOD`.

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

## Validation : Gates A/B PASS ; Gates C/D non testées

- **Gate A :** builder AP20 reproductible à partir de l'archive R31, uniquement un nouveau token, tests Unicorn M68000 avec Capstone pour l'ABI (D3/D2/A3), conversion RGB32, limites de l'écran, palette partielle, banque Chip/Fast, refus atomiques avant affichage, libération temporaire, absence d'écritures dans banque/bitplanes ; export source 68000 strict, CI complète. Résultat à consigner avant distribution.
- **Gate B PASS (capture utilisateur) :** dans AMOS interprété/WinUAE, importer un seul fichier `.asc` actif après Gate A ; ouvrir un écran AGA indexé, capturer deux palettes différentes en AGAPAL, altérer les couleurs affichées, appliquer successivement les deux, vérifier `Aga Palette Get` sur les pens 28/3/224, l'application partielle et la conservation des couleurs supérieures, les refus (index hors plage, palette vide, écran fermé), les sauvegardes/rechargements ABK natifs, le retour `RESULT 1` et la fermeture propre. La CI ne remplace pas cette preuve utilisateur.
- **Gates C et D :** compilation AMOS et Amiga physique AGA non testés tant que cela n'a pas réellement été réalisé.

R32 Gate A/B PASS : `dist/AMOSPro_AGA.Lib`, `dist/AMOSPro_AGA_LAST_GOOD.Lib` et l'archive R32 sont identiques. Le test a été archivé octet pour octet. Aucune fonction de fade/import/cycling ajoutée ; discuter toute prochaine fonction avant codage.

## Test WinUAE R32 (validé et archivé)

Copier [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib) R32 0.10.4 dans `APSystem` sous son **nom exact** sans renommer ni changer de slot ; quitter et relancer AMOS. Ouvrir un projet vide et utiliser **Project → Merge ASCII** sur [`tests/passed/M13_R32_AGAPAL_APPLY_01.asc`](../tests/passed/M13_R32_AGAPAL_APPLY_01.asc). **Attention : le test remplace banques 10/11 et `RAM:R32_AGAPAL_APPLY.ABK`.**

Le test ouvre un écran AGA Intuition indexé 320×256×8, initialise une banque AGAPAL huit palettes, capture deux états RGB24 (pen 28 vert puis rouge), puis change les couleurs affichées (bleu/pen 224). `Apply(...,0)` doit restaurer le vert et le pen 224 ; `Apply(...,1)` doit donner le rouge. Pour la palette partielle (compte 4), seuls les pens 0..3 doivent changer et le pen 28 doit rester bleu. Il refuse index -1/8, palette vide, banque mal dimensionnée, compte 257 et écran fermé, sans altérer les couleurs. Le test sauvegarde et recharge le fichier ABK via AMOS `Save/Erase/Load`, puis applique les palettes depuis la banque rechargée. Aucun VBL implicite : le test déclenche volontairement ses propres VBL.

**Résultat confirmé par capture utilisateur :** `INIT 1 OPEN 1 DB 1`, `CAP0 1 CAP1 1`, `AP0 1 AP1 1 PART 1`, `GREEN 65280 RED 16711680 BLUE 255`, `PEN224 795192 PART3 660510 PART28 255`, `BADNEG 0 BAD8 0 EMPTY 0`, `BADSIZE 0 BADCOUNT 0`, `AFTERBAD 255 AFTERCOUNT 255`, `ABK AGAPAL SIZE 6224`, `COUNT0 4 COUNT1 256`, `RELOAD 1 16711680 PART 1`, `REST3 660510 REST28 16711680`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. **Gate B PASS** : `RESULT 1`, `CLOSE RETURNED`, fin normale ligne 161. R32 est `LAST_GOOD`.
