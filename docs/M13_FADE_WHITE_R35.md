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

## État du développement

**Contrat approuvé, Gate A CPU/CI et Gate B WinUAE encore non testées pour R35.** R35 n'est pas encore une bibliothèque installable ; le builder n'écrit qu'en mémoire.

**R34 0.10.6 est la version validée WinUAE et `LAST_GOOD`**, 20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`, identique à son archive figée.

- Émetteur R35 : `tools/m13_aga_fade_white_r35_emit.py`.
- Builder : `tools/build_m13_aga_fade_white_r35.py` (base figée : archive R34, 40 commandes AP20), ajoute le token 41 `aga fade to white`, signature `00`, segment AP20 46.
- Test CPU 68000 : `tools/test_m13_aga_fade_white_r35.py`, exécution des véritables octets avec Unicorn/Capstone, RGB32 blanc exact, pas DDA, ABI, LVO, durée, mémoire, écrans et invalides.
- Test AMOS pour la Gate B : [`tests/current/M13_R35_FADE_TO_WHITE_01.asc`](../tests/current/M13_R35_FADE_TO_WHITE_01.asc), grandes bandes affichées avec `Aga Swap` et `Amos To Back` **avant le fondu visible de 150 VBL**. Vérifie les pens 28/29/30/224 blancs à 16777215, refus durées invalides 0/256/-1/65536, durée 1/2, appel sur écran déjà blanc, fermeture écran, `RESULT 1` et `CLOSE RETURNED`. **Aucune banque AMOS remplacée**.
- Après PASS de Gate A et export source strict, publication de la candidate en `dist/AMOSPro_AGA.Lib` et archive `dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib`, avec **R34 toujours dans `LAST_GOOD`**.
- La Gate B ne sera déclarée PASS **qu'après ton test AMOS interprété/WinUAE** ; les Gates C Compiler/D Amiga physique resteront non testées en l'absence de preuve.

Aucune autre fonction n'est ajoutée à R35. Le contrat de R36 devra être discuté et approuvé avant tout développement.
