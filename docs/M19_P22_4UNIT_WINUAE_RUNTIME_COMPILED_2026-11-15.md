# M19 P2.2 — Quatrième bloc natif BOBS : WinUAE Runtime et Compiled PASS (15/11/2026)

**Gate B Runtime et Gate C Compiled du témoin `Aga Bob Probe` : PASS** sur les deux journaux fournis par l'auteur. **Ceci valide l'accès au quatrième groupe AP20 avec les deux modes testés, pas encore le dessin des Bobs ni `Aga Bob Batch`.**

**Test exact :** [`tests/current/M19_P22_4UNIT_PROBE_01.asc`](../tests/current/M19_P22_4UNIT_PROBE_01.asc), blob Git **`cd564aa660f8927b1c4d0b63456de58b5535fae0`** : **déplacé sans changer les octets** depuis `tests/design/`. Candidat de travail attendu : [`dist/AMOSPro_AGA.Lib`](../dist/AMOSPro_AGA.Lib), R85 v0.13.30 (67 988 octets, SHA256 `4accb5768503735b38b465a41a7ea712b400dcf92b4becad563ff7a95abdd84f`). R84 `LAST_GOOD` protégée : 67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`.

## Journaux fournis — données brutes

**`M19_P22_4UNIT_RUNTIME.TXT` :**

```text
TEST M19_P22_4UNIT_PROBE_01
LIBRARY EXPERIMENTAL_4UNIT_GATE_A_ONLY
PRG_STATE  1
RESULT  1
VERDICT PASS
ERR  0
AGA_DETECT -1
BOB_PROBE  1
CLOSE_RETURNED 1
```

**`M19_P22_4UNIT_COMPILED.TXT` :**

```text
TEST M19_P22_4UNIT_PROBE_01
LIBRARY EXPERIMENTAL_4UNIT_GATE_A_ONLY
PRG_STATE -1
RESULT  1
VERDICT PASS
ERR  0
AGA_DETECT -1
BOB_PROBE  1
CLOSE_RETURNED 1
```

| Contrôle | Runtime | Compiled |
|---|---:|---:|
| `Prg State` | **1** | **−1** |
| `RESULT`, `ERR` | **1, 0** | **1, 0** |
| `AGA_DETECT` | **−1** | **−1** |
| `BOB_PROBE` | **1** | **1** |
| `CLOSE_RETURNED` | **1** | **1** |
| Verdict | **PASS** | **PASS** |

## Portée des validations

- **Gate A** : CI MC68020 Unicorn **PASS** sur [run 43696972204](https://github.com/anthea176/AMOSPro-AGA-Extension/actions/runs/43696972204), avec les quatre unités natives et la préservation des anciens corps.
- **Gate B du témoin** : **PASS Runtime** sur la base de `PRG_STATE 1` et de `BOB_PROBE 1`, retour normal. Ce test ne mesure ni performance, ni dessin AGA, ni RAM Chip/Fast.
- **Gate C du témoin** : **PASS Compiled** sur la base de `PRG_STATE -1`, `BOB_PROBE 1`, retour normal ; pas une validation du futur moteur de Bobs.
- **Limite de preuve** : les journaux portent la chaîne fixée dans le programme `LIBRARY EXPERIMENTAL_4UNIT_GATE_A_ONLY`, pas une empreinte du binaire réellement installé. Ils attestent la réponse de `Aga Bob Probe` sur les deux chemins d'exécution, pas la SHA256 du fichier chargé dans WinUAE.
- **Gate D** matériel Amiga non testée. **`Aga Bob Batch`** non implémentée, non testée, et aucun gain de performance revendiqué.

## Organisation des fichiers corrigée

Le **seul ASC actif** est désormais [`tests/current/M19_P22_4UNIT_PROBE_01.asc`](../tests/current/M19_P22_4UNIT_PROBE_01.asc). Le benchmark P2.1 PASS est [archivé octet pour octet](../tests/passed/M19_P21_ZCACHE_BENCH_01.asc), blob Git `f75af1a84b4c658d5f1cb330d58d248413e72cc7`. L'ancien emplacement `tests/design/M19_P22_4UNIT_PROBE_01.asc` n'est plus utilisé ; **ne plus y chercher le test actif**.

**Suite native M19 :** après cette preuve d'infrastructure, développer une commande de rendu groupé dans le bloc BOBS, la qualifier distinctement, garder le candidat dans `dist/AMOSPro_AGA.Lib` et ne jamais écraser `LAST_GOOD`.

[Architecture P2.2](M19_P22_FOURTH_BOBS_UNIT_2026-11-15.md) · [Plan M19](M19_SPRITES_BOBS_AMAL_PLAN.md) · [Source active](../tests/current/M19_P22_4UNIT_PROBE_01.asc)
