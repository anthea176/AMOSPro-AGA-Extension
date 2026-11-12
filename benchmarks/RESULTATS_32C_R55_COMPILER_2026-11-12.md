# Benchmark V2 compilé — R55, avant remplacement RastPort R56

**Date : 12 novembre 2026. Source : capture utilisateur du benchmark compilé `benchmarks/graphics_32c_v2.asc`**, PAL 320×256×32 couleurs (5 bitplanes). **Ce document conserve l'observation R55 sans toucher à la baseline R44/R46 C1 figée.** Identité cryptographique du binaire réellement chargé et paramètres détaillés WinUAE non relevés ; utilisation déclarée de la R55 active.

## Temps bruts compilés (ticks, 1 tick = 20 ms)

| Test | AMOS A | AMCAF M | AGA R55 G |
|---|---|---|---|
| Plot 120 000 | 10 / 11 / 10 | 10 / 10 / 10 | 13 / 13 / 13 |
| Draw 400 | 36 / 35 / 35 | 35 / 35 / 35 | 36 / 36 / 36 |
| Box 225 | 53 / 54 / 53 | 53 / 53 / 53 | 54 / 53 / 54 |
| Circle 8 000 | 16 / 16 / 16 | 14 / 14 / 14 | 10 / 11 / 10 |
| Bar / Fill 100 | 40 / 41 / 41 | N/A | 54 / 54 / 54 |
| Clear 80 | 87 / 87 / 87 | 58 / 58 / 57 | 115 / 116 / 115 |

**Contrôles visibles :** `AGA ERR 0`, `V2 FINISHED - CLOSE RETURNED`; programme compilé terminé sans Guru visible.

## Comparaison avec la baseline compilée R46 C1

| Opération | Avant M17 : R46 C1 médiane | R55 médiane | Variation du temps |
|---|---:|---:|---:|
| Fill ×100 | 54 ticks | 54 ticks | 0 % |
| Clear ×80 | 117 ticks | 115 ticks | −1,7 % |

La variation du Clear de **2 ticks sur 80 appels** n'établit pas un gain robuste. La R55 avait cependant les Gates A/B/C PASS sur le scénario fonctionnel Fill/Clear/Copy utilisateur (Gate C sans capture). **Conclusion : pas d'accélération notable** malgré le regroupement de plusieurs bitplanes dans un appel `BltBitMap`. La R56 vise les fonctions `RectFill`/`SetRast` avec une nouvelle validation indépendante B/C, et **doit être mesurée avec le même programme inchangé**.

[Baseline figée](RESULTATS_32C_BASELINE_R44_2026-11-12.md) · [Benchmark source](graphics_32c_v2.asc) · [Rapport M17](../docs/M17_BLITTER_DIAGNOSTIC.md).
