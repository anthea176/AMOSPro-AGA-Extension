# M19 B7-m1 — benchmark A/B/C de l'effacement en Runtime

**Seul ASC actif (chemin conservé pour les workflows) :** [M19_P0J_B7_ANIM_RUNTIME_03.asc](M19_P0J_B7_ANIM_RUNTIME_03.asc) — **7 555 octets**, SHA256 `0f18cb608f75cda0390f86d25169bd4312561efd4d2051435a6803ceff42f689`. L'ancien test de 120 frames reste consultable [dans l'historique Git avant ce banc](https://github.com/anthea176/AMOSPro-AGA-Extension/blob/75caa3c8198aad612e434e1ae3d54ceb2249ca45/tests/current/M19_P0J_B7_ANIM_RUNTIME_03.asc).

**Bibliothèque B7-m1 conservée sans modification :** [`dist/AMOSPro_AGA.Lib`](../../dist/AMOSPro_AGA.Lib), 102 360 octets, SHA256 `838245ce1ad2a4120bb2512df8b2147ae89dc6b3eebe2ba2a9f633f2e9a56403`. Gate A native MC68020 PASS (793 contrôles). R84 `LAST_GOOD` inchangée. **Benchmark Runtime WinUAE NON TESTÉ ; aucun test Compiler.**

## Exécution

1. Dans WinUAE : **AGA PAL, 68030/JIT ON**, Lib B7-m1 dans `APSystem`. AMOS Professional : programme vierge, **Project → Merge ASCII** du seul ASC actif (pas Load).
2. Banques AMOS **24 et 25 libres** ; n'employer `Erase All` que dans une session de test sans autre banque à préserver.
3. Exécuter **en Runtime uniquement**. Le programme prépare les deux pages puis réalise **six séries de 120 frames** (ordre **A, B, C, C, B, A**). Pour A/C, les **quatre Bobs sont mobiles**, rouges masqués et jaunes opaques, avec clipping dynamique. B est volontairement un écran vide.
4. À la fin : `Aga Screen Close`, `Amos To Front`, effacement des deux banques, puis journal **`RAM:M19_B7M1_CLEAR_BENCH.TXT`**. Le conserver avant reset, observer d'éventuelles traînées dans C, puis relancer sans `Erase All`.

## Comparaison

| Cas | Travail mesuré (120 frames par série) | Utilité |
|---|---|---|
| A | `Aga Blit Fill(0,0,320,256,1)` + 4 Bobs + `Aga Swap` | Référence plein écran |
| B | Même Fill plein écran + Swap, **sans** `Aga Bob Draw` | Coût de la boucle Fill/Swap |
| C | Effacement des anciens rectangles sur la **bonne page arrière** + 4 Bobs + Swap | Mesurer le gain des dirty rectangles |

En C, **les deux premières frames de chaque série effacent tout l'écran**, une fois par page. Les 118 suivantes effacent les quatre anciennes emprises de cette même page, avec clipping, puis redessinent les quatre objets. La page logique ne change **qu'après Swap réussi**. Un Fill ou Draw refusé interdit le Swap de cette frame.

Les fenêtres chronométrées vont du premier effacement au dernier Swap de chaque série ; **aucun VBL artificiel par frame**. `Aga Wait Vbl` est utilisé seulement **en cas de refus** de Fill/Swap (retries bornés à 40) ; une pause finale de 40 VBL est **hors mesure**.

## Journal et critères

Pour chaque série, relever les champs `RUN n CASE c`, `RUN_FRAMES`, `RUN_TICKS`, `RUN_FPS_X10`. `Timer` vaut **50 ticks/s** en AMOS : `FPS ≈ RUN_FPS_X10/10` ; conserver les ticks bruts, et comparer en priorité **A contre C** sur les deux passages. Les deux mesures d'un même cas ne constituent pas une médiane robuste ; ne pas annoncer de gain avant observation. `RETRY_VBL` signale les attentes induites par des refus, pouvant biaiser les durées. Le temps d'un `Swap` synchrone reste inclus.

Attendu sur un parcours correct : `RESULT 1`, `ERR 0`, `FRAMES_OK 720`, six séries à `RUN_FRAMES 120`, `CLEAR_FAILS 0`, `DRAW_FAILS 0`, `SWAP_FAILS 0`, `BANKS_ERASED 2`, `VERDICT PATH_OK` ; aucun freeze, résidu, masque incorrect ou scintillement anormal. **PATH_OK n'est pas une preuve pixel ni une mesure de Chip RAM.** Les FPS issus des ticks sont des moyennes incluant le BASIC, la synchronisation matérielle et les échanges OS, pas une vitesse brute du Blitter.

**Statut : PREFLIGHT PASS (source AMOS + 240 vérifications géométriques de double buffer en simulation). Gate B de ce nouveau banc : NON TESTÉE ; Gate C/D : NON TESTÉES.** [Rapport détaillé](../../docs/M19_B7M1_CLEAR_BENCH_RUNTIME_2026-11-18.md).
