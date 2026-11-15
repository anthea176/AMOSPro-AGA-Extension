# Test actif — M19 P2.4, validation pixels et benchmark R86

**Un seul ASC actif : [M19_P24_BOBS_PIXELS_BENCH_01.asc](M19_P24_BOBS_PIXELS_BENCH_01.asc).**

Le test M19 P2.3 déjà qualifié a été [archivé octet pour octet](../passed/M19_P23_BOBS_BATCH_01.asc), sans changement du code. Son [rapport Gates B/C](../../docs/M19_P23_R86_WINUAE_RUNTIME_COMPILED_2026-11-15.md) reste valide ; ses anciens journaux ne peuvent pas servir à valider P2.4.

**Candidat à installer :** `dist/AMOSPro_AGA.Lib` **R86 v0.13.31**, inchangée, SHA256 `63ad295d49c807cda1ba7e2482855fe8c00d6f9e71987f3aa9bc3fdbedd5a93f`. `dist/AMOSPro_AGA_LAST_GOOD.Lib` R84 reste protégée.

Le nouveau programme crée lui-même AGAPIC v1/v2 et FICON8. Il compare **19 vrais indices de pixels** issus de captures 1×1, contrôle l'ordre Z, l'opacité du pen 0, la transparence, les clips et l'ancien front après le Swap explicite. Il compare ensuite **le flux image complet** entre commandes individuelles et `Aga Bob Batch` pour 4, 8 et 16 Bobs.

Le benchmark intégré utilise 64 répétitions × 2 passages inversés par méthode et par nombre de Bobs, **sans tri Z, fond, Swap ou Wait VBL dans la zone chronométrée**. Il ne mesure donc pas exactement le même périmètre que le benchmark P2.1.

**Exécution WinUAE :** de préférence 68020, 14 MHz, PAL et JIT désactivé. Exécuter d'abord en Runtime, puis Compiler. Récupérer dans `RAM:` :

- `M19_P24_RUNTIME.TXT`
- `M19_P24_COMPILED.TXT`

**Statut :** [CI statique PASS](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43701540717) ; **Gates WinUAE Runtime/Compiled P2.4 non testées** jusqu'à réception des deux nouveaux journaux. Attendu : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `PIXEL_OK 19`, `PIXEL_BAD 0`, `PARITY_OK 3`, `PARITY_BAD 0`, `BENCH_RUNS 12`, `CLOSE_RETURNED 1`.

[Plan technique et limites](../../docs/M19_P24_PIXEL_ORACLE_BENCH_PLAN_2026-11-15.md).
