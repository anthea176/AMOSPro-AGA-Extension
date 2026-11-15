# M19 P2 — benchmark 4 / 8 / 16 Bobs sur écran AGA privé

**Un seul test actif :** [M19_P2_BENCH_BOBS_01.asc](M19_P2_BENCH_BOBS_01.asc). **P2.0 fonctionnel / Gate B Runtime PASS** archivé à l'identique sous [tests/passed/M19_P2_OBJECTS_01.asc](../passed/M19_P2_OBJECTS_01.asc), [rapport P2.0](../../docs/M19_P2_WINUAE_RUNTIME_2026-11-15.md).

**Référence :** bibliothèque R84 v0.13.29 `LAST_GOOD` (67 904 octets, SHA256 `46f274c6051f171132f4dcf6f0e8c3a8ccef16162dfa6a804cab6c3a7bf08e6d`) **inchangée**. Pas de nouvelle API M19, de compilation demandée, de `c2p.library`, ni de travail sur une autre branche.

**État : second journal 68030/JIT activé selon l'auteur, `RESULT 1`, `VERDICT PASS`, `ERR 0`, 240 frames, 9 088 dessins, toutes les charges 4/8/16 complètes, 0 échec Draw/Swap et deltas mémoire nuls.** [Rapport du PASS](../../benchmarks/RESULTATS_M19_P2_BOBS_68030_JIT_2026-11-15.md). Le [premier essai interrompu](../../benchmarks/RESULTATS_M19_P2_BOBS_4_8_16_2026-11-15.md) reste archivé. **Comparatif MC68020/14 MHz/JIT OFF reçu et PASS** (CPU détecté 68020, JIT OFF et 14 MHz déclarés par l'auteur) : 240 frames, 9 088 dessins, aucun échec Draw/Swap ni retry Safe/Swap, mémoire nette stable. [Rapport du 68020](../../benchmarks/RESULTATS_M19_P2_BOBS_68020_14MHZ_NOJIT_2026-11-15.md). **La composition moyenne est 60,08 / 96,25 / 189,50 ms/frame** à 4/8/16 Bobs ; le tri atteint **58,68 ms/appel** à 16 Bobs. Le programme de benchmark reste inchangé. Un PASS P2.0 n'est pas un PASS benchmark. Le nouveau banc n'inclut pas d'AMAL : il mesure le gestionnaire BASIC et le rendu dans un scénario contrôlé.

## Lancement WinUAE

1. Vérifier les banques **11 à 23 libres** ; WinUAE AGA **PAL, JIT OFF**, MC68020 **14 MHz fixe** pour le benchmark de référence (ou démarrer en 68030 pour un premier contrôle).
2. Charger R84 puis **Project → Merge ASCII** dans un programme vide. **`Set Buffer 20` doit être la première instruction exécutée.**
3. Le programme prépare 6 sources AGAPIC et 4 FICON8, puis exécute **deux passages** des charges 4, 8 et 16. Le tri de 800 itérations et les 120 effacements/120 compositions **n'ont pas de Swap** et peuvent montrer un écran fixe ; **40 frames visibles par charge et par passage** sont ensuite affichées avec Swap.
4. **Ne pas appuyer sur Échap** : `Aga Key=69` provoque `ERR 20` et quitte le banc avant le résultat final. Après les **240 frames de présentation** au total, attendre le retour AMOS et relever `RAM:M19_P2_BENCH_BOBS_RUNTIME.TXT` (ou suffixe du mode). Faire une copie du journal avant une nouvelle exécution. Si `ERR 20` revient sans appui Échap, le signaler pour diagnostic.

## Champs essentiels

| Contrôle | Attendu |
|---|---|
| Fonctionnel | `RESULT 1`, `VERDICT PASS`, `ERR 0`, `CLOSE_RETURNED 1` |
| Sources | `CAP_OK 6`, `ICON_OK 4`, `OBJECTS_PREPARED 16` |
| Présentation | `FRAME_OK 240`, `DRAW_FAIL 0`, `SWAP_FAIL 0` |
| Compteurs composés | `N4_Px_COMP_DRAWS 480`, `N8_Px_COMP_DRAWS 960`, `N16_Px_COMP_DRAWS 1920` (x = 0,1) |
| Total dessins | `DRAW_OK 9088`, échauffement 8×16 compris |
| Performance | `N4_P0_SORT_TICKS`, `N8_P0_SORT_TICKS`, `N16_P0_SORT_TICKS` et les colonnes `FILL/COMP/DISP_TICKS` pour P0 et P1 |
| Fiabilité timing | `*_COMP_SAFE_RETRIES` et `*_DISP_SWAP_RETRIES` consignés ; toute attente pendant la composition non synchronisée doit être signalée |

Les durées sont **des temps écoulés**, par `Timer` (PAL nominal ~20 ms/tick), **pas des cycles CPU**. `COMP` = fond + tri + dessins **sans Swap** ; `DISP` = VBL + composition + Swap. On ne déduit pas directement 50 FPS d'un résultat PASS.

[Protocole complet et interprétation](../../benchmarks/README_M19_P2_BOBS_4_8_16.md) · [Plan M19](../../docs/M19_SPRITES_BOBS_AMAL_PLAN.md) · [Règles du projet](../../EXTENSION_SOURCE_RULES.md).
