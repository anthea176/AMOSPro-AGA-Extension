# M13 / R35 0.10.7 — Aga Fade To White

## Contrat approuvé par l'utilisateur le 11/11/2026

La R35 reprend strictement le modèle de la R34 WinUAE-PASS, à l'exception de la **couleur cible blanche**. Une seule nouvelle fonction :

```amos
_OK=Aga Fade To White(_VBL)
```

- `_VBL` entier **1 à 255 inclus**. Durée 0, négative ou >255 = refus **0 sans changement**.
- **Bloquant** : un `graphics.library/WaitTOF` puis un `LoadRGB32` pour chaque VBL. Pas d'attente cachée. Le calcul 68000 peut dépasser la durée d'une trame ; la durée réelle n'est pas garantie exactement à N/50 seconde.
- **Écran cible** : écran AGA Intuition privé actif, indexé, 1 à 8 bitplanes, 1 à 256 pens logiques. `ColorMap.Count` doit couvrir tous les pens logiques. HAM/EHB/dual playfield et écrans invalides refusés.
- **Source RGB24** : snapshot `GetRGB32` une fois pour `_VBL>=2` ; aucune capture nécessaire si `_VBL=1`.
- **Interpolation** linéaire et indépendante des canaux RGB24, pas fixe signé **8.8** (`(255-source)*256/_VBL`), calculé une fois comme R34. À la **dernière image**, toutes les composantes sont forcées exactement à `0xFFFFFFFF` au format RGB32, sans résidu d'arrondi.
- Aucun changement des pixels/bitplanes, des banques DATA/AGAPAL/ABK ni des fichiers ; aucun argument `Start(bank)`.
- Allocation Exec temporaire `AllocVec(MEMF_PUBLIC)` de `8+42*N` octets (max **10 760**), libérée par `FreeVec`. Les validations et l'allocation précèdent le premier VBL.
- Retour entier **1** si le fondu s'achève ; **0** si paramètres, écran ou allocation invalides, sans altération de palette. Éviter la fermeture concurrente de l'écran durant la fonction.

### Usage AMOS

```amos
_OK=Aga Fade To White(100)
```

## Statut R35 — Gates A CPU/CI et B fonctionnelle AMOS/WinUAE PASS (11/11/2026)

**Gate A PASS :** 50 scénarios natifs CPU 68000, export source 68000 strict et [CI candidate complète 37/37 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43057572164). **41 commandes AP20.**

**Gate B PASS — test visuel utilisateur sous AMOS interprété/WinUAE :** capture fournie après exécution du [test ASC original archivé](../tests/passed/M13_R35_FADE_TO_WHITE_01.asc). Valeurs visibles :
`OPEN 1 DB 1 DRAW 1 1 1`, `FADE150 1 WHITE 16777215 16777215`, `WHITE2 16777215 16777215`, `BAD0 0 BAD256 0 BADNEG 0 BADL 0`, `BEFOREBAD 7915560 AFTERBAD 7915560`, `FADE1 1 ONE 16777215`, `FADE2 1 TWO 16777215`, `SAME 1 SAME28 16777215`, `NOSCREEN 0 CLOSED -1`, **`RESULT 1`**, **`CLOSE RETURNED`**. L'utilisateur confirme « c nickel » : fondu de 150 VBL vers le blanc visuellement réussi, sans mesure instrumentée de cadence/FPS ni de durée réelle.

**Promotion R35 sans recompilation :** `dist/AMOSPro_AGA.Lib` = `dist/AMOSPro_AGA_LAST_GOOD.Lib` = `dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib`, **21 300 octets**, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539`, **strictement identiques**. R34 0.10.6 reste inchangée dans son [archive historique](../dist/experimental/AMOSPro_AGA_M13_v0.10.6_AGA_FADE_TO_BLACK_R34.Lib), 20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`.

**Test WinUAE archivé sans altération :** [`tests/passed/M13_R35_FADE_TO_WHITE_01.asc`](../tests/passed/M13_R35_FADE_TO_WHITE_01.asc), Git blob `21115dfbbcff345e6ae8132c03956152b897a6b2`, identique octet pour octet au fichier de `tests/current/` exécuté par l'utilisateur. **Aucun ASC actif dans `tests/current/`.** Aucune banque AMOS ni fichier ABK/IFF écrasé par ce test.

- Émetteur 68000 R35 : `tools/m13_aga_fade_white_r35_emit.py`.
- Builder déterministe R35 depuis l'archive R34 figée : `tools/build_m13_aga_fade_white_r35.py`, binaire calculé en mémoire.
- Régression CPU native : `tools/test_m13_aga_fade_white_r35.py`.
- **Gates C Compiler et D Amiga physique NON TESTÉES.** Durée réelle et fluidité mesurée non validées.
- Avant toute nouvelle commande R36, discuter son contrat et demander l'accord explicite de l'utilisateur ; rester sur `main`.


Aucune autre fonction n'est ajoutée à R35. Le contrat de R36 devra être discuté et approuvé avant tout développement.
