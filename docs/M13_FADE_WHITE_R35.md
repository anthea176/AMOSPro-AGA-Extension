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

## Statut R35 : Gate A CPU/CI PASS, Gate B AMOS/WinUAE en attente

**Gate A :** 50 scénarios CPU natifs 68000 PASS (vraies instructions 68000 Unicorn, registre ABI AMOS, interp RGB24, blanc final exact, durées 1..255 et invalides, mémoires conservées), export source 68000 strict PASS, [CI dédiée R35 Gate A réussie](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43057199711). 41 commandes AP20.

**Candidate publique :** `dist/AMOSPro_AGA.Lib` = archive `dist/experimental/AMOSPro_AGA_M13_v0.10.7_AGA_FADE_TO_WHITE_R35.Lib`, **21 300 octets**, SHA256 `ca2a901c30ebd933e41fcaa66c6dc78b5561938caa86901eb09fcc3d81dca539` (copies binaires identiques). Le binaire est le résultat déterministe du builder R35 depuis l'archive immuable R34. **`dist/AMOSPro_AGA_LAST_GOOD.Lib` reste R34 0.10.6 WinUAE-PASS**, 20 752 octets, SHA256 `89124519c391d632bd2dec2c41b4959a965c6dc2d6852d5568b97d23586f4033`, conservée exactement.

**Gate B NON TESTÉE :** [`tests/current/M13_R35_FADE_TO_WHITE_01.asc`](../tests/current/M13_R35_FADE_TO_WHITE_01.asc), scène dessinée et affichée par `Aga Swap` puis `Amos To Back` **avant** le fondu de 150 VBL ; contrôle des pens 28/29/30/224 tous à **16777215**, durées invalides, appel 1/2 VBL, déjà blanc, fermeture et retour AMOS. **Aucune banque AMOS ni fichier remplacé**. Installer candidate R35 dans `APSystem`, même slot, redémarrer AMOS puis **New → Project → Merge ASCII**.

**Une fois Gate B validée par l'utilisateur**, promotion octet pour octet dans `LAST_GOOD`, archivage de l'ASC exact dans `tests/passed/`, mise à jour des deux README et CI complète. Gates C Compiler et D Amiga réel : **NON TESTÉES**.


Aucune autre fonction n'est ajoutée à R35. Le contrat de R36 devra être discuté et approuvé avant tout développement.
