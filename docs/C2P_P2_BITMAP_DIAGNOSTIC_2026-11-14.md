# C2P P2 — diagnostic des bitmaps Intuition (14/11/2026)

**Préparation en lecture seule, aucune Gate B/C C2P réalisée.** La référence reste R73 v0.13.18 `LAST_GOOD` (51 608 octets, SHA256 `c995ea143a21ea1820c9f0c75455131215a7fc876be81587dc8bf561a7808407`).

## Correction d'offset importante

Les exports natifs R23 et R57 de `Aga Double Buffer` donnent la chaîne :

```text
A5+$1C8            -> State
State+$20          -> DBState
DBState+$00        -> SB0 (ScreenBuffer *)
DBState+$04        -> SB1 (ScreenBuffer *)
DBState+$08        -> index frontal
ScreenBuffer+$04   -> BitMap *
```

**Le pointeur BitMap est à ScreenBuffer+4 et non +0** comme indiqué dans la synthèse C2P préliminaire. C'est vérifié par `MOVEA.L 4(A0),A0` après la récupération de SB0/SB1 dans les deux exports historiques. Vérifier sa conservation lors d'un futur changement natif.

`struct BitMap` : `+$00 BytesPerRow` (WORD), `+$02 Rows` (WORD), `+$04 Flags` (BYTE), `+$05 Depth` (BYTE), `+$08..+$24 Planes[0..7]` (LONG).

## Mesure attendue sous WinUAE

1. Conserver **la R73 binaire inchangée**. L'ASC actif `tests/current/C2P_P2_R73_BITMAP_01.asc` ouvre `Aga Screen Open(320,256,256,$00021000)` et `Aga Double Buffer`, puis attend `Aga Wait Key` pour permettre la capture GDB. Voir [procédure](C2P_P2_WINUAE_GDB_PROBE_2026-11-14.md).
2. Dans le débogueur WinUAE, interrompre l'exécution **à l'intérieur d'une routine AGA après allocation des deux buffers**, relever A5 et suivre la chaîne ci-dessus en lecture seule. A5 n'est pas fiable après retour dans du code AMOS arbitraire.
3. Relever les deux pointeurs `ScreenBuffer`, deux `BitMap`, les huit pointeurs de plans et les champs de structure. Pour la preuve mémoire Chip, soit vérifier réellement `TypeOfMem`/`MEMF_CHIP` sur chaque plan, soit fournir une taille Chip RAM confirmée dans WinUAE **et** la carte physique RAM GDB couvrant cette zone. Ne pas substituer un retour `TypeOfMem` inventé à une plage issue de la configuration.
4. Reporter les valeurs dans un JSON avec `mode={width:320,height:256,depth:8}` et `buffers=[SB0,SB1]`. Chaque buffer comporte `name`, `screen_buffer`, `bitmap`, `bytes_per_row`, `rows`, `depth`, `flags`, `planes` (8 adresses), `type_of_mem_first` (8 valeurs), `type_of_mem_last` (8 valeurs). Les nombres peuvent être des entiers ou chaînes hexadécimales `0x...`.
5. Exécuter `python -B tools/c2p_p2_layout_check.py observation.json`. Retour **0** : deux dispositions non entrelacées compatibles *sur les données fournies* ; **1** : refus / preuve incomplète ; **2** : format mal formé. Cela ne vaut **jamais** un PASS de C2P, Safe/Swap ou WinUAE.

## Critères 320 × 256 × 8

- Un buffer chunky = **81 920 octets**. Un plan = **10 240 octets** (`$2800`).
- Pour une disposition standard non entrelacée : `BytesPerRow=40`, `Rows=256`, `Depth=8` et `Planes[i]=Planes[0]+i*$2800`.
- Les huit plans doivent être en mémoire Chip, correctement alignés ; les zones mémoire SB0 et SB1 ne doivent pas se recouvrir.
- **Un plan non contigu, une mémoire inconnue ou un bitmap entrelacé bloque la conversion directe** pour cette première étude.

## Attention à l'entrelacement dans le SDK

Le README de `c2p.library` v1.9 annonce la prise en charge des bitmaps entrelacés depuis la **v1.4** et l'API expose `C2P_CONTEXT_PARAMETER_INTERLEAVED_BITMAP`. Pourtant l'autodoc `C2P_SetContextParameter(BITMAP)` exige un bitmap custom non entrelacé et la comparaison des drapeaux d'entrelacement est commentée dans `InitializeContext`. Les bitmaps entrelacés ne sont donc **pas validés par ce premier outil** : ils nécessitent un test indépendant.

## Résultat obtenu

**18 tests Python hôte synthétiques PASS** (11 vérificateur + 7 lecteur GDB) : standard, plan décalé, mémoire Chip absente/inconnue, recouvrement SB0/SB1, interleavé refusé, profondeur, largeur, pointeurs et nombre de plans invalides. **Aucune observation réelle WinUAE P2**, aucune conversion, aucune nouvelle commande AMOS, aucun changement à `dist/` ou `tests/passed/` ; l'unique ASC actif est désormais le témoin P2.

**Suite :** collecter le relevé WinUAE ; si les deux bitmaps satisfont aux contraintes, prototype C2P direct avec deux contextes et garde `Safe`. Sinon, évaluer une allocation C2P indépendante, sans changer le moteur AGA classique.
