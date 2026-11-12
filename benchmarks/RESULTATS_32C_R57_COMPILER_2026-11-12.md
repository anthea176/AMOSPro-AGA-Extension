# Résultats benchmark V2 compilé — R57 0.13.2 — 12/11/2026

**Source : capture utilisateur WinUAE, programme compilé `benchmarks/graphics_32c_v2.asc`.** PAL 320×256×32 couleurs (5 bitplanes), trois passages, 1 tick = 20 ms. La bibliothèque utilisée est déclarée R57 dans le contexte des tests ; son identité SHA256 en mémoire, le modèle CPU et les réglages détaillés WinUAE ne sont pas fournis par la capture. Le benchmark source et les résultats historiques sont conservés sans modification.

## Valeurs brutes, en ticks

| Opérations | AMOS A | AMCAF M | AGA R57 G |
|---|---|---|---|
| PLOT 120K | 10 / 11 / 10 | 10 / 10 / 10 | 13 / 13 / 13 |
| DRAW 400 | 35 / 35 / 36 | 35 / 35 / 35 | 36 / 36 / 36 |
| BOX 225 | 53 / 53 / 53 | 53 / 53 / 53 | 54 / 54 / 53 |
| CIRCLE 8000 | 16 / 16 / 16 | 14 / 14 / 14 | 10 / 11 / 10 |
| BAR 100 | 40 / 41 / 41 | N/A | **41 / 40 / 41** |
| CLEAR 80 | 87 / 87 / 87 | 58 / 57 / 57 | **58 / 58 / 58** |

**Résultat affiché :** `AGA ERR 0` ; `V2 FINISHED - CLOSE RETURNED` ; aucun Guru visible. `CIRCLE M = 5 BCIRCLE / RING` est l'annotation du benchmark, pas un message d'erreur.

## Comparaison entre exécutables compilés R55 et R57

| Test AGA | R55 médiane (3 passages) | R57 médiane (3 passages) | Réduction du temps | Durée moyenne par opération |
|---|---:|---:|---:|---|
| Fill / BAR ×100 | **54 ticks** (54/54/54) | **41 ticks** (41/40/41) | **24,1 %** | 10,8 → 8,2 ms |
| Clear ×80 | **115 ticks** (115/116/115) | **58 ticks** (58/58/58) | **49,6 %** | 28,75 → 14,5 ms |

Calculs sur les médianes : `(54-41)/54 = 24,07 %`, `(115-58)/115 = 49,57 %`. La durée par opération est la durée de l'ensemble du lot divisée par le nombre d'appels, pas une mesure de latence individuelle.

R57 rejoint **BAR AMOS natif (41 ticks médians)** sur cette charge. Sur **CLEAR**, R57 (58 ticks) se situe à un tick du **Blitter Clear AMCAF** (57 ticks médians). Par rapport à la baseline compilée R46 C1 (Fill 54, Clear 117 ticks), les réductions sont respectivement 24,1 % et 50,4 %.

**Attention aux modes :** R56 avait des mesures Fill/Clear proches de R57 mais en **interprété** ; son exécution compilée plantait avec le Guru `8000000B`. Ne pas mélanger R56 interprétée et R55/R57 compilées pour quantifier le gain.

## Validation et limites

- **R57 Gate A CPU/CI : PASS.** **Gate C AMOS Compiler/WinUAE : PASS** sur le test fonctionnel R57 (capture antérieure : `RESULT 1`, erreurs 0, `CLOSE RETURNED`, aucun Guru) et le benchmark compilé V2 de cette capture (`AGA ERR 0`).
- **Gate B R57 interprétée sur l'ASC courant : non confirmée.** La réussite interprétée R56 ne se transfère pas automatiquement à R57. **Gate D matériel Amiga AGA : non testée.**
- **Conclusion de performance :** accélération Fill et Clear nette et reproductible sur trois passages du programme compilé de référence, sous les conditions WinUAE de l'utilisateur ; pas de garantie universelle de temps ni de comportement sur Amiga physique.
- Le remplacement en place du helper R55 a éliminé le plantage Line-F du scénario compilé R56, mais le mécanisme exact de l'erreur de placement n'a pas été prouvé.
- **R54 reste LAST_GOOD**, inchangée, sans promotion automatique.

**Contrainte de dépôt :** branche `main` uniquement ; un seul binaire de travail `dist/AMOSPro_AGA.Lib`, un seul ASC actif `tests/current/M17_R57_RAST_FILL_01.asc`. Le benchmark historique reste en `benchmarks/`, sans second test actif.

[Benchmark source](graphics_32c_v2.asc) · [R55 compilée](RESULTATS_32C_R55_COMPILER_2026-11-12.md) · [Baseline R44/R46](RESULTATS_32C_BASELINE_R44_2026-11-12.md) · [Rapport M17](../docs/M17_BLITTER_DIAGNOSTIC.md).
