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

Le test [`M13_R36_PALETTE_CYCLE_01.asc`](../tests/passed/M13_R36_PALETTE_CYCLE_01.asc) présente quatre bandes colorées **avant** le début du cycling, puis 20 rotations espacées de huit VBL chacune. Il vérifie les deux sens, une inversion qui restaure la palette, les couleurs RGB24 attendues, les invalides et le retour propre à AMOS. **Aucune banque AMOS ni aucun fichier ABK/IFF écrasé.**

## Statut R36 — Gates A CPU/CI et B AMOS interprété/WinUAE PASS (11/11/2026)

**Gate A PASS :** 106 scénarios réels CPU 68000 (RGB32 exact, sens +/-1, 256 pens, indices hors plage préservés, rotations inverses, ABI, sans WaitTOF), export source 68000 strict et [CI candidate complète 38/38 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43064975345), **42 commandes AP20**.

**Gate B PASS — capture de l'utilisateur sous AMOS interprété/WinUAE :** quatre bandes affichées avant 20 rotations espacées de huit VBL. `OPEN 1 DB 1 DRAW 1 1 1 1`, `CYC20 1 RESTORED 16711680 16776960`, `FWD 1 COLOR 16776960 16711680 65280 255`, `REV 1 RESTORE 16711680 16776960`, `NEG 1 COLOR 65280 16711680 POS 1`, `RESET 16711680 16776960`, `BADFIRST 0 BADEQ 0 BADORDER 0`, `BADLAST 0 DIR0 0 DIR2 0 DIRN 0`, `AFTERBAD 16711680 NOSCREEN 0`, **`RESULT 1`**, **`CLOSE RETURNED`**, fin normale à la ligne **138**. L'utilisateur confirme « fct nickel ! » ; cycling visuellement fonctionnel. Pas de mesure FPS ni de durée réelle.

**Promotion sans recompilation :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.8_PALETTE_CYCLE_R36.Lib`, **21 836 octets**, SHA256 `f30882fc3d3dd86a0f30bf5c897e102a4892f992efa7e5e349184994d749d225`, binaires octet pour octet identiques. Archive R35 0.10.7 préservée intacte, 21 300 octets, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`.

**Test original archivé à l'octet près :** [`tests/passed/M13_R36_PALETTE_CYCLE_01.asc`](../tests/passed/M13_R36_PALETTE_CYCLE_01.asc), blob Git `4644236576033f755ac0dc274f6f22f92a2d9201`, identique au fichier de `tests/current/` exécuté par l'utilisateur ; **aucun ASC actif après archivage**. Aucune banque AMOS ni fichier ABK/IFF remplacé.

- Émetteur : `tools/m13_palette_cycle_r36_emit.py`.
- Builder déterministe : `tools/build_m13_palette_cycle_r36.py` (base archive R35 figée, pas de modification des octets après test).
- Régressions natives : `tools/test_m13_palette_cycle_r36.py`.
- **Gates C Compiler et D Amiga AGA réel NON TESTÉES**. Toute fonction R37 exige discussion et accord explicite ; rester sur `main`.



