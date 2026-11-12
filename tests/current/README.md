# Test AMOS actif — M17/R56 RastPort Fill/Clear

**Seul test actif :** [`M17_R56_RAST_FILL_01.asc`](M17_R56_RAST_FILL_01.asc). Avec `examples/demo.iff` 320×256×8 bitplanes, il vérifie `Aga Blit Fill`, `Aga Blit Clear`, `Aga Blit Copy`, la garde non bloquante `Safe`, les couleurs 3/28/224 et **40 swaps** avec alternance des panneaux. Résultats attendus : **`RESULT 1`**, **`CLOSE RETURNED`**, `DRAWERR 0`, `SAFEERR 0`, `SWAPERR 0`, bon rendu et absence de Guru. `Wait Key` termine le test pour conserver les résultats.

**Seul binaire actif :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), **R56 0.13.1**, **33 560 octets**, SHA256 `df0bf2400eb9dc87e69e94f4472c05c8a7d57b496ef792a11125f7419d75ffef`, 53 commandes / 60 entrées AP20. **Gate A CPU/CI PASS** ([run R56](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43282947214)) ; **Gates B WinUAE interprété, C nouvel exécutable compilé et D machine physique NON TESTÉES pour R56**.

**Historique sans revalidation :** R55 0.13.0 a passé les Gates A/B/C sur son propre test utilisateur (Gate C confirmée sans capture) ; le benchmark compilé Fill 54 ticks / Clear 115 ticks a montré l'absence de gain significatif vs R46 C1. R54 0.12.9 reste l'unique `LAST_GOOD` validée dans `dist/AMOSPro_AGA_LAST_GOOD.Lib`, SHA256 `f5c5c40c94eb48ffd1b13aa8e7ca216248f77a2939793939d3e0001242ac82f0`, intacte.
