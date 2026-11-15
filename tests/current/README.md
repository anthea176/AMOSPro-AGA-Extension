# Test actif — M19 P2.6 : performance du rendu groupé BOBS sur R87

**Un seul ASC actif : [M19_P26_R87_DRAW_BENCH_01.asc](M19_P26_R87_DRAW_BENCH_01.asc)**. Le **smoke R87 P2.5** dont les journaux Runtime/Compiled ont donné `RESULT 1 / ERR 0 / VERDICT PASS` a été [archivé sans aucune modification](../passed/M19_P25_R87_BOBS_SMOKE_01.asc).

**Bibliothèque à installer :** `dist/AMOSPro_AGA.Lib` R87 v0.13.32, **73 184 octets**, SHA256 `02d97cfaea9949f9a5d5a5ae6ce4ac4754cde353667a8c5b0b821f1aeb03c302`. R84 `LAST_GOOD` reste protégée. Ne pas utiliser la R86.

## Objet : mesurer les performances, pas refaire les tests de chargement

Le programme génère seul deux images AGAPIC v1/v2 40×40 et un FICON8 16×16, puis prépare des banques BOB1 strictes de **4, 8 et 16 descripteurs**. BASIC et Batch utilisent exactement les mêmes sources, positions, ordre et mode de transparence.

Pour chaque quantité, exécution de **64 répétitions BASIC puis 64 Batch**, avec une seconde passe **Batch puis BASIC**. **12 chronométrages**, **3 584 dessins de Bobs par méthode** et **384 appels Batch**. Après échauffement, le fond est initialisé *avant* chaque chronométrage. Aucun tri Z, effacement, Swap, Wait VBL, animation, capture ou allocation dans les fenêtres mesurées. Aucun affichage visuel permanent n'est attendu : c'est un benchmark du **back buffer**.

Les ticks `Timer` sont journalisés **séparément pour les deux passes** et cumulés pour 4/8/16. Le programme ne calcule pas de gain supposé. Ces mesures draw-only **ne sont pas directement les anciennes durées de composition P2.1**.

## Exécution

Dans WinUAE, sélectionner **MC68020 à 14 MHz, AGA PAL, JIT OFF**, installer R87 dans son slot APSystem et redémarrer AMOS. Ouvrir un programme vide, puis **Project → Merge ASCII** du seul ASC actif. Lancer une fois en Runtime, puis compiler **le même fichier** avec AMOS Compiler V2 et exécuter le binaire.

Récupérer dans `RAM:` :

- `M19_P26_RUNTIME.TXT`
- `M19_P26_COMPILED.TXT`

Champs attendus : `RESULT 1`, `ERR 0`, `VERDICT PASS`, `REPS 64`, `BENCH_RUNS 12`, `BASIC_CALLS 3584`, `BATCH_CALLS 384`, `BASIC_BOBS 3584`, `BATCH_BOBS 3584`, `CLOSE_RETURNED 1`. Pour chaque 4/8/16, relever `BASIC_TICKS`, `BATCH_TICKS`, `PASS0_N` et `PASS1_N`.

**Statut P2.6 : PREPARE / Gates Runtime et Compiled NON TESTÉES** tant que les deux nouveaux journaux n'ont pas été produits. L'ancien P2.5 reste validé mais ne mesure aucune performance.

[Protocole et limites des mesures](../../docs/M19_P26_R87_DRAW_PERFORMANCE_2026-11-15.md).
