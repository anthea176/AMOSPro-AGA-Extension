# Test actif — M19 P2.2, quatrième bloc natif BOBS (R85)

**Un seul ASC actif : [M19_P22_4UNIT_PROBE_01.asc](M19_P22_4UNIT_PROBE_01.asc)**

Il doit **toujours être cherché ici, dans `tests/current/`**, et non dans `tests/design/`. La bibliothèque de travail correspondante est [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), candidate **R85 v0.13.30**. Le fichier [`dist/AMOSPro_AGA_LAST_GOOD.Lib`](../../dist/AMOSPro_AGA_LAST_GOOD.Lib) est **R84 v0.13.29**, sauvegarde protégée **à ne pas remplacer**.

## Résultats de l'essai

**Deux journaux WinUAE ont été reçus, tous les deux PASS :**

| Mode | Fichier produit | Verdict |
|---|---|---|
| AMOS Runtime (`Prg State = 1`) | `RAM:M19_P22_4UNIT_RUNTIME.TXT` | **PASS, ERR 0, BOB_PROBE 1** |
| Compiled (`Prg State = -1`) | `RAM:M19_P22_4UNIT_COMPILED.TXT` | **PASS, ERR 0, BOB_PROBE 1** |

Les deux affichent aussi `AGA_DETECT -1`, `CLOSE_RETURNED 1`. [Journaux et analyse](../../docs/M19_P22_4UNIT_WINUAE_RUNTIME_COMPILED_2026-11-15.md).

**Ce test vérifie le quatrième groupe AP20**, pas le dessin des Bobs. `Aga Bob Batch` est encore à développer.

Le benchmark antérieur P2.1 sur le cache Z, validé sous WinUAE, est [archivé à l'identique](../passed/M19_P21_ZCACHE_BENCH_01.asc), avec son [rapport final](../../benchmarks/RESULTATS_M19_P21_ZCACHE_68020_NOJIT_2026-11-15.md).

## Pour relancer ce test R85, si nécessaire

Dans AMOS, importer le **seul ASC actif de ce dossier** via **Project → Merge ASCII**, en partant d'un programme vide et avec **R85 installée**. Ne pas lancer le test avec R84 `LAST_GOOD`, qui ne possède pas `Aga Bob Probe`. Le test écrit automatiquement le journal correspondant au mode d'exécution.

**État :** témoin P2.2 Runtime/Compiled PASS ; R85 candidate non promue ; prochain développement = **véritable API native de Bobs**, distincte de ce témoin.
