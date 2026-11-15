# M19 P2.1 — Dernier benchmark, tri Z BASIC vs cache Z (15/11/2026)

**Gate B AMOS Runtime/WinUAE MC68020 : PASS** selon le journal utilisateur `M19_P21_ZCACHE_RUNTIME.TXT` (147 lignes). Profil annoncé par l'auteur : **68020 à 14 MHz, AGA PAL, JIT OFF**. Le journal vérifie `CPU 68020`, pas directement le réglage MHz/JIT. **R84 v0.13.29 `LAST_GOOD` inchangée.**

Test Git inchangé : [M19_P21_ZCACHE_BENCH_01.asc](../tests/current/M19_P21_ZCACHE_BENCH_01.asc), blob `f75af1a84b4c658d5f1cb330d58d248413e72cc7`. Un seul ASC actif. Aucun code natif ni API AP20 supplémentaire.

## 1. Contrôles fonctionnels

| Champ du journal | Valeur |
|---|---:|
| `RUN_MODE / PRG_STATE` | RUNTIME / 1 |
| `CPU / CPU_ATTNFLAGS` | 68020 / 3 |
| `RESULT / VERDICT / ERR` | **1 / PASS / 0** |
| `CACHE_INVALID_TESTS / BENCH_CASES` | **5 / 12** |
| `SORT_CALLS_TOTAL` | **1 225** |
| `CACHE_BUILDS_TOTAL / CACHE_HITS_TOTAL` | **17 / 1 188** |
| `CAP_OK / ICON_OK / OBJECTS_PREPARED` | 6 / 4 / 16 |
| `FRAME_OK / DRAW_OK` | **240 / 9 088** |
| `SORT_FAIL / FILL_FAIL / DRAW_FAIL / SWAP_FAIL` | 0 / 0 / 0 / 0 |
| `SAFE_RETRIES / SWAP_RETRIES` | **0 / 0** |
| `CHIP_BEFORE / CHIP_AFTER / CHIP_DELTA` | 1 840 176 / 1 840 176 / **0** |
| `FAST_BEFORE / FAST_AFTER / FAST_DELTA` | 138 364 864 / 138 364 864 / **0** |
| `CLOSE_RETURNED` | **1** |

Cinq essais de cache ont passé : ordre initial, changement de Z, restauration de Z, masquage, réapparition. Chaque charge et chaque méthode présentent le même nombre de Bobs et suivent les mêmes mouvements. Il n'existe pas de comparaison pixel par pixel de la totalité des buffers dans ce banc.

## 2. Ticks bruts du journal

Deux passages `P0` puis `P1` ; 120 demandes d'ordre, 60 compositions sans Swap et 20 présentations VBL+Swap, **par méthode et charge**. P0 : BASE puis CACHE ; P1 : CACHE puis BASE. `Timer` PAL : **20 ms/tick nominaux**.

| Bobs | Passage | SORT BASE | SORT CACHE | COMP BASE | COMP CACHE | DISP BASE | DISP CACHE |
|---:|:---:|---:|---:|---:|---:|---:|---:|
| 4 | P0 | 25 | 1 | 180 | 170 | 80 | 62 |
| 4 | P1 | 25 | 2 | 181 | 170 | 80 | 60 |
| 8 | P0 | 94 | 2 | 289 | 244 | 101 | 100 |
| 8 | P1 | 91 | 2 | 289 | 244 | 101 | 100 |
| 16 | P0 | 353 | 4 | 569 | 397 | 201 | 140 |
| 16 | P1 | 353 | 5 | 569 | 395 | 200 | 140 |

Tri : 120 vrais tris en BASE contre **1 tri + 119 réutilisations** en CACHE par série. Composition : 60 tris en BASE contre **1 reconstruction** en CACHE ; présentation : 20 tris en BASE contre **0** en CACHE. Toutes les attentes `COMP_SAFE_RETRIES` et `DISP_SWAP_RETRIES` valent 0. Fond seul : **188 ticks / 120 appels**, soit **31,33 ms/fill** nominal.

## 3. Gains réels en composition

Moyenne des deux passages, `COMP_TICKS × 20 / 60`. Valeurs de temps **écoulé**, pas des cycles CPU :

| Bobs | BASE (ms/frame) | CACHE (ms/frame) | Gain CACHE |
|---:|---:|---:|---:|
| **4** | **60,17** | **56,67** | **−3,50 ms / −5,8 %** |
| **8** | **96,33** | **81,33** | **−15,00 ms / −15,6 %** |
| **16** | **189,67** | **132,00** | **−57,67 ms / −30,4 %** |

## 4. Présentation avec VBL et Swap

Moyenne des passages, `DISP_TICKS × 20 / 20`. La cadence dérivée représente des **frames présentées en moyenne** et inclut attente VBL et Swap ; ce n'est pas une mesure de FPS matériels garantis.

| Bobs | BASE (ms/frame) | CACHE (ms/frame) | Débit moyen BASE → CACHE |
|---:|---:|---:|---:|
| 4 | 80,0 | 61,0 | 12,5 → **16,4 FPS** |
| 8 | 101,0 | 100,0 | 9,9 → **10,0 FPS** |
| 16 | 200,5 | 140,0 | 5,0 → **7,1 FPS** |

L'écart de présentation à 8 Bobs (1 ms seulement) ne suit pas le gain de composition (15 ms) ; cela illustre l'influence de la cadence et du VBL/Swap. Le tri de 120 demandes coûte BASE/CACHE : 4 Bobs **25/1–2 ticks**, 8 Bobs **91–94/2 ticks**, 16 Bobs **353/4–5 ticks**. Les quelques ticks côté cache ne mesurent pas le coût d'un tri isolé.

## 5. Conclusion et clôture

- **Cache Z BASIC recommandé :** maintenir un ordre stable `(Z, ID)` et ne le recalculer qu'en cas de création/suppression, changement de Z, visibilité ou liste active. Les cinq contrôles d'invalidation du banc ont passé, mais le gestionnaire de production n'est pas modifié.
- **Gain de composition confirmé dans ce scénario**, culminant à **30,4 % avec 16 Bobs**. Malgré cela, **132 ms/composition** à 16 Bobs reste coûteux ; le dessin et le fond complet demeurent hors du périmètre de cette optimisation.
- **Dernier essai terminé : aucun nouveau benchmark demandé.** Aucune nouvelle API native/AP20, aucune promotion R84, aucun nouveau binaire ni branche.
- **Portée :** AMOS Runtime sur WinUAE 68020 uniquement ; M19 Compiler Gate C, mode interprété strict (`PRG_STATE 0`), Amiga physique Gate D, coût en cycles CPU et identité visuelle pixel par pixel **non testés**. Chip/Fast delta nul = mesure nette entre deux instants, pas le pic mémoire.

[Protocole P2.1](README_M19_P21_ZCACHE_68020_NOJIT.md) · [Baseline P2 sur 68020 sans JIT](RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md) · [Roadmap](../docs/ROADMAP.md)
