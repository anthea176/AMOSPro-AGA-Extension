# M19 P2.1 — dernier benchmark Z BASIC vs cache Z (68020/noJIT)

**Un seul ASC actif :** [M19_P21_ZCACHE_BENCH_01.asc](M19_P21_ZCACHE_BENCH_01.asc). Benchmark P2 4/8/16 **déjà PASS** archivé avec blob identique [ici](../passed/M19_P2_BENCH_BOBS_01.asc). [Rapport du précédent essai MC68020/14 MHz/JIT OFF](../../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md).

**Binaire R84 v0.13.29 `LAST_GOOD` inchangé** (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`). Aucun token AP20 nouveau, aucun test Compiler ou Amiga réel demandé.

**État : programme P2.1 contrôlé statiquement et prêt ; aucune exécution WinUAE P2.1 reçue, Gate B P2.1 EN ATTENTE.**

## Démarrage direct sur le profil noJIT

1. Utiliser **68020 à 14 MHz, JIT OFF, AGA PAL**. Banques AMOS **11 à 23 libres**.
2. Dans AMOS, repartir d'un programme vide, puis **Project → Merge ASCII** avec le [nouvel ASC](M19_P21_ZCACHE_BENCH_01.asc).
3. Ne pas appuyer sur **Échap** (`ERR 41`). Les phases sans Swap peuvent donner un écran temporairement immobile. Laisser terminer **240 présentations** au total.
4. Récupérer **`RAM:M19_P21_ZCACHE_RUNTIME.TXT`** et le renvoyer ici.

## Vérifications intégrées

| Champ | Attendu |
|---|---:|
| `RESULT` / `ERR` | `1` / `0` |
| `CACHE_INVALID_TESTS` / `BENCH_CASES` | `5` / `12` |
| `SORT_CALLS_TOTAL` / `CACHE_BUILDS_TOTAL` / `CACHE_HITS_TOTAL` | `1225` / `17` / `1188` |
| `FRAME_OK` / `DRAW_OK` | `240` / `9088` |
| `SORT_FAIL`, `FILL_FAIL`, `DRAW_FAIL`, `SWAP_FAIL` | tous `0` |
| `CLOSE_RETURNED` | `1` |

Pour les **4/8/16 Bobs**, deux passages inversant l'ordre **BASE/CACHE**. Chaque passage mesure **120 demandes de tri, 60 compositions et 20 frames VBL+Swap** par mode. À comparer dans le journal : `N4_P0_BASE_COMP_TICKS` / `N4_P0_CACHE_COMP_TICKS`, idem pour N8, N16, P1, avec leurs **comptages de tris**. Le gain de performance est **inconnu avant le test**.

[Protocole complet](../../benchmarks/README_M19_P21_ZCACHE_68020_NOJIT.md) · [Plan M19](../../docs/M19_SPRITES_BOBS_AMAL_PLAN.md) · [Règles](../../EXTENSION_SOURCE_RULES.md).
