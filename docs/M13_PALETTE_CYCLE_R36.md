# M13 — R36 0.10.8 : Aga Palette Cycle

## Contrat utilisateur approuvé le 11/11/2026

**Une seule nouvelle fonction :** `_OK=Aga Palette Cycle(First,Last,Direction)`.
Elle effectue **une seule rotation de couleurs RGB32 par appel**, indépendamment des pixels ; elle ne lance aucune animation automatique.

- `First` : premier index inclus, entier `0..255`. `Last` : dernier index inclus, strictement supérieur à `First` et dans les pens logiques de l'écran et de la ColorMap (au maximum 255). La plage doit contenir **au moins deux couleurs**.
- `Direction` : `1` décale vers les indices croissants (couleur de `Last` vers `First`) ; `-1` décale vers les indices décroissants (couleur de `First` vers `Last`). Toute autre valeur est refusée.
- **Retour 1** après une rotation réussie, **0** pour arguments, écran ou ColorMap invalides ou allocation impossible. Rejet **avant** toute modification de palette, sans effet sur pixels, banques ou fichiers.
- Cible : uniquement l'écran AGA Intuition privé actif et **indexé** (1 à 8 bitplanes, jusqu'à 256 pens logiques). Rejet des modes HAM/EHB/dual playfield et des ColorMap inadaptées. Aucun effet hors de la plage [First,Last].
- **Précision complète :** `graphics.library/GetRGB32` capture `N=Last-First+1` couleurs comme triplets 32 bits, les fait tourner sans conversion RGB8, puis **un seul** `LoadRGB32` pour ces mêmes N indices. **Aucun `WaitTOF` implicite**, pas de dégradation de couleur et pas de pixel déplacé.
- **Mémoire temporaire** : `Exec/AllocVec(MEMF_PUBLIC)` avec exactement `8+12*N` octets (au plus **3 080 octets** pour 256 couleurs), libérée en sortie, aucune variable globale ou état permanent.
- Le rythme, la pause et l'arrêt du cycling sont entièrement à la charge du code AMOS appelant (via `Aga Wait Vbl`). Pour revenir à la palette initiale, faire l'inverse ou capturer/restaurer avec AGAPAL. Aucun effet n'est réalisé en tâche de fond.
- ABI AP20 : fonction numérique, trois arguments, `Direction` dans D3, `Last` puis `First` lus à `(A3)+` ; retour dans D3 et D2=0, sauvegarde des autres registres. Base R35 0.10.7 immuable (41 tokens), **R36 ajoute la 42e commande**, segment 47, signature `00,0,0`.

### Exemple AMOS

~~~amos
For _I=1 To 60
   _OK=Aga Palette Cycle(28,31,1)
   Aga Wait Vbl
Next _I
~~~

Le test [`M13_R36_PALETTE_CYCLE_01.asc`](../tests/current/M13_R36_PALETTE_CYCLE_01.asc) présente quatre bandes colorées **avant** le début du cycling, puis 20 rotations espacées de huit VBL chacune. Il vérifie les deux sens, une inversion qui restaure la palette, les couleurs RGB24 attendues, les invalides et le retour propre à AMOS. **Aucune banque AMOS ni aucun fichier ABK/IFF écrasé.**

## État de la version : Gate A CPU/CI PASS, Gate B WinUAE en attente

**Gate A PASS :** **106 scénarios CPU 68000 natifs** (RGB32 exact, rotation +1/-1, 256 pens, couleurs hors plage inchangées, boucles inverses, absence `WaitTOF`, ABI et rejets atomiques), export natif 68000 strict PASS, [CI Gate A](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43064528445). **42 tokens AP20.**

**Candidate R36 publique :** `dist/AMOSPro_AGA.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib`, **21 836 octets**, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`, copies strictement identiques. Générée de manière déterministe à partir de l'archive R35 WinUAE-PASS. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste R35 0.10.7** (21 300 octets, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`), inchangée.

**Gate B WinUAE NON TESTÉE :** [`tests/current/M13_R36_PALETTE_CYCLE_01.asc`](../tests/current/M13_R36_PALETTE_CYCLE_01.asc) affiche 4 bandes avant le cycling (20 rotations, pause 8 VBL), confirme le sens des rotations, les couleurs exactes, rejets et fermeture propre. **Aucune banque AMOS ni fichier écrasé.** Installer la candidate dans `APSystem`, même slot, redémarrer AMOS, importer par **New → Project → Merge ASCII**.

Après confirmation utilisateur, promouvoir **sans recompilation** dans `LAST_GOOD`, archiver l'ASC exact à l'octet et actualiser les deux README, docs et CI dans le même commit. Gates C Compiler/D matériel non testées.

- Gates C Compiler et D Amiga AGA physique restent **NON TESTÉES**. Toute fonction R37 doit faire l'objet d'une discussion et d'une approbation distinctes.
