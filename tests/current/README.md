# M18/R68 — CBlock PERF-02, benchmark AMOS interprété, non-JIT

**UN SEUL ASC actif** : [`M18_R68_CBLOCK_PERF_02.asc`](M18_R68_CBLOCK_PERF_02.asc).

**Bibliothèque NON CHANGÉE** : [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), R68 v0.13.13, 51 064 octets, SHA256 `ffaa41e3a95bc5b761114dd7f5a3fd4506673c904784816177303446f35eb1ed`. **Gates A/B R68 déjà PASS** ([rapport R68](../../docs/M18_R68_CBLOCK_WINUAE_GATE_B_2026-11-13.md)). R63 `LAST_GOOD` reste protégée. **Pas de Compiler AMOS avant la fin M18**.

**But :** mesurer honnêtement le croisement de performances entre les chemins CPU8 / CPU16 / Blitter, sur **68020 à 14 MHz JIT OFF** puis **68030 JIT OFF** ; noter la fréquence, les Chip/Fast RAM et le modèle CPU de chaque essai. Ne pas comparer les anciens `68030 JIT ON 0/0/6` à ces mesures hors JIT.

**Installation/exécution :** laisser la même R68 en `APSystem` avec le slot déjà configuré ; vérifier que les **banques 11 et 13 sont libres**. Dans AMOS : **New → Project → Merge ASCII** sur le seul ASC ci-dessus, **Run interprété**. Aucune recompilation, aucune nouvelle banque/bibliothèque à télécharger.

## Scénarios (2 répétitions, nombre de copies affiché)

| S | Taille en pixels | Appels par méthode, **par opération** | Alignement |
|---:|---:|---:|---|
| 0 | 16×16 | 1 200 | CPU8 / CPU16 / Blitter |
| 1 | 24×16 | 1 000 | **CPU16 non applicable**, affiché `-1` (largeur 24) ; CPU8/Blitter sur X=8 |
| 2 | 32×16 | 800 | Tous, cas de référence R68 |
| 3 | 64×48 | 240 | Tous |
| 4 | 128×96 | 80 | Tous |
| 5 | 320×64 | 70 | Tous ; X=0, pleine largeur |

Pour chaque méthode : **deux passes**, chronométrées séparément pour `Capture` et `Draw`, banque 11 préallouée (coût Reserve exclu), puis **comparaison octet par octet** de la banque 11 contre une recapture Blitter de destination dans la banque 13 (validation hors chronométrage). Le fond est réinitialisé à chaque taille. Le code vérifie réutilisation de banque, `Chip Free` après `Erase`, retour d'appel, fermeture et résultat global.

## Lecture de la console

- Pour chaque scénario `S0..S5` : ligne `S<n> W×H N<nombre total d'appels>`, puis `C cpu8/cpu16/blit D cpu8/cpu16/blit` en **ticks `Timer` AMOS**. **Les valeurs `C` et `D` portent sur N appels chacune**, pas sur N partagé entre les deux.
- `-1` pour CPU16 sur 24×16 est **un saut volontaire** dû à l'alignement exigé, pas une erreur.
- `RUNS/ERR/MIS/MEM 17 0 0 0` et `RESULT 1` / `CLOSE RETURNED` attendus.
- `CHIP START/END` : nombres identiques, `NOS/CLOSE 0 -1`. En cas de `RESULT 0`, ne pas déclarer ce benchmark validé.
- **Ticks bruts à ne comparer qu'à taille et N identiques.** Quelques ticks de différence peuvent être de la quantification `Timer` ; refaire un essai si proche. Ce programme ne choisit pas encore automatiquement CPU ou Blitter.

**ASC R68 Gate B historique, immuable :** [`tests/passed/M18_R68_CBLOCK_CHIP_01.asc`](../passed/M18_R68_CBLOCK_CHIP_01.asc). Ne pas le modifier ni l'utiliser à la place du test actif.
