# OPT020/P1e — R69 v0.13.14 — WinUAE Gate B interprétée PASS

**Date de validation : 13 novembre 2026.** Deux captures d'écran fournies par l'auteur : console finale et écran AGA du test `OPT020_P1E_R69_INTERPRETED_01.asc`, exécuté en mode **AMOS interprété sous WinUAE**. **Gate B PASS pour le scénario testé**, sans prétendre à une comparaison automatique pixel par pixel.

## Artefacts et preuve

- **Candidate R69** : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), 51 240 octets, SHA256 `9ff104125839fc14b35fabf6fcb436020f9b30cff9c6490868bf3ab7427d6298`. 64 commandes / 71 entrées AP20. Seul `Aga Image Region` est remplacé par le peintre natif 68020 BFINS ; API R60 conservée.
- **R68 `LAST_GOOD` protégée** : [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../dist/AMOSPro_AGA_LAST_GOOD.Lib), 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. R69 **non promue**.
- **ASC exécuté** : [`tests/current/OPT020_P1E_R69_INTERPRETED_01.asc`](../tests/current/OPT020_P1E_R69_INTERPRETED_01.asc). Banque AGAPIC `M16_AGAPIC_SAMPLE_BANK10.abk`.
- **Captures originales dans la conversation** : `image(20261113-203503).png` (console) et `image(20261113-203524).png` (graphique). Les fichiers sont fournis à la conversation et **ne sont pas intégrés à ce commit GitHub**.
- **Gate A / intégrité CI** : [321 cas CPU P1e PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43499755913), [Gate A OPT020 sur candidate R69 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43500643740), [Artifact integrity 47/47 PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43501573321).

## Relevé de la console

```text
OPT020-P1E-R69-INTERPRETED-01
OPT020 P1e CPU020 - INTERPRETED GATE B ONLY
OPEN 1 DB 1 SW0 1 SAFE 1
FRAMES 1 1 1 1 SHIFT 1
CLIP 1 1 1 1 OUT 1
EDGE/PART/MASK OPAQUE 1 1 1
BAD BANK/X/Y/W/M 0 0 0 0 0
LEGACY 1 SWAP 1 NOS 0 CLOSE -1
CHIP BEFORE/END 1800320 1800320
RESULT 1
CLOSE RETURNED
```

La ligne `INTERPRETED GATE B ONLY` s'affiche sur deux lignes à cause de la largeur de la console AMOS ; ce n'est pas une erreur.

**Interprétation :** ouverture AGA, double buffering, premier Swap, Safe, quatre tuiles opaques/masquées, déplacement non aligné, clipping quatre côtés, hors écran valide, deux cas supplémentaires en bord, refus des paramètres invalides, `Aga Bank Image Draw` historique, dernier Swap, refus après fermeture et retour du pointeur AMOS : valeurs conformes. `Chip Free` vaut **1 800 320 octets avant et après**, donc aucune perte de Chip RAM détectée par ce contrôle d'ensemble. `RESULT 1` et `CLOSE RETURNED` visibles.

## Contrôle du rendu graphique

La capture graphique montre bien les quatre sous-images (deux opaques et deux masquées), l'image décalée, le fond uni, le grand motif ancien dessiné au centre/bas et les morceaux partiellement visibles aux bords gauche, droit, supérieur et inférieur. Les très petits fragments isolés aux limites de l'écran sont cohérents avec les cas de clipping inscrits dans l'ASC, pas en eux-mêmes la preuve d'un débordement. Pas de défaut graphique évident ni de Guru dans les captures.

**Limites :** le `RESULT 1` vérifie les retours des appels, pas une comparaison des pixels du framebuffer aux pixels d'une référence calculée. Le rendu est apprécié visuellement. Les captures n'attestent pas indépendamment de la configuration exacte CPU/horloge/RAM ni du réglage **JIT OFF**. Le compteur FPS WinUAE n'est **pas** un benchmark `Aga Image Region`. Les profondeurs 1/2/8 et RLE corrompus ont été couverts côté CPU/CI, pas par cet ASC graphique (16 couleurs / 4 plans).

## État et suite

| Gate | Résultat |
|---|---|
| A — CPU/CI/native + Compiler V2 **structurel** | **PASS** |
| B — WinUAE, AMOS **interprété**, console + rendu | **PASS**, pour ce scénario |
| C — AMOS Compiler **réel** | **NON TESTÉE** |
| D — Amiga physique | **NON TESTÉE** |
| Performance 68020 vs R60, WinUAE JIT OFF | **NON MESURÉE** |

**R69 reste candidate de travail, pas `LAST_GOOD`.** Pas de modification du binaire ni de l'ASC après ces captures. Avant promotion, figer la candidate et réaliser **un seul essai final AMOS Compiler (Gate C)** ; benchmark comparatif R60/R69 en WinUAE **JIT OFF**, relevé CPU/fréquence/RAM, séparément. Aucune affirmation de gain de vitesse avant mesures.
